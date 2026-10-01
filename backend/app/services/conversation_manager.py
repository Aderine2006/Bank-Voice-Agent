from typing import Dict, Any, List, Optional
from app.models.conversation import (
    ConversationState, ConversationStage, Intent,
    CustomerProfile, CustomerPreferences
)
from app.models.loan import LoanProduct
from app.services.financial_extraction import FinancialExtractor
from app.services.intent_detector import IntentDetector
from app.services.loan_matching import LoanMatchingEngine
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


class ConversationManager:
    """Manages conversation state and workflow"""
    
    def __init__(
        self,
        financial_extractor: FinancialExtractor,
        intent_detector: IntentDetector,
        loan_matching_engine: LoanMatchingEngine
    ):
        self.financial_extractor = financial_extractor
        self.intent_detector = intent_detector
        self.loan_matching_engine = loan_matching_engine
        
        # In-memory session storage (for MVP)
        self.sessions: Dict[str, ConversationState] = {}
    
    def start_conversation(self) -> ConversationState:
        """Start a new conversation session"""
        conversation_id = str(uuid.uuid4())
        
        state = ConversationState(
            conversation_id=conversation_id,
            current_stage=ConversationStage.GREETING,
            intent=Intent.UNKNOWN
        )
        
        self.sessions[conversation_id] = state
        logger.info(f"Started conversation: {conversation_id}")
        
        return state
    
    def get_conversation(self, conversation_id: str) -> Optional[ConversationState]:
        """Get existing conversation state"""
        return self.sessions.get(conversation_id)
    
    def process_message(
        self,
        conversation_id: str,
        user_message: str,
        products: List[LoanProduct]
    ) -> ConversationState:
        """
        Process a user message and update conversation state
        
        Returns updated conversation state
        """
        state = self.get_conversation(conversation_id)
        if not state:
            state = self.start_conversation()
        
        # Detect intent
        state.intent = self.intent_detector.detect_intent(user_message)
        
        # Extract financial information
        state.customer_profile = self.financial_extractor.extract_profile(
            user_message,
            state.customer_profile
        )
        
        # Update stage based on intent
        state = self._update_stage(state)
        
        # Match products if we have enough information
        if state.current_stage in [
            ConversationStage.PROFILE_COLLECTION,
            ConversationStage.PRODUCT_MATCHING
        ]:
            matches = self.loan_matching_engine.match_products(
                products,
                state.customer_profile,
                state.customer_preferences
            )
            
            state.candidate_products = [m.product.product_id for m in matches]
            state.eligible_products = [
                m.product.product_id for m in matches
                if m.eligibility.status == "ELIGIBLE_BASED_ON_PROVIDED_INFORMATION"
            ]
            state.ineligible_products = [
                m.product.product_id for m in matches
                if m.eligibility.status == "DOES_NOT_MEET_CONFIGURED_CRITERIA"
            ]
            
            # Get missing information
            state.missing_fields = self.loan_matching_engine.get_missing_information(
                matches,
                state.customer_profile
            )
            
            # Update stage based on results
            if state.missing_fields:
                state.current_stage = ConversationStage.PROFILE_COLLECTION
            elif state.eligible_products:
                state.current_stage = ConversationStage.PRODUCT_MATCHING
            else:
                state.current_stage = ConversationStage.ELIGIBILITY_CHECK
        
        state.updated_at = datetime.utcnow()
        
        logger.info(
            f"Processed message for {conversation_id}: "
            f"stage={state.current_stage}, intent={state.intent}"
        )
        
        return state
    
    def _update_stage(self, state: ConversationState) -> ConversationState:
        """Update conversation stage based on intent and profile"""
        
        if state.current_stage == ConversationStage.GREETING:
            if state.intent == Intent.LOAN_DISCOVERY:
                state.current_stage = ConversationStage.LOAN_DISCOVERY
            elif state.intent == Intent.HUMAN_AGENT_REQUEST:
                state.current_stage = ConversationStage.HANDOFF
        
        elif state.current_stage == ConversationStage.LOAN_DISCOVERY:
            if state.customer_profile.requested_loan_amount:
                state.current_stage = ConversationStage.PROFILE_COLLECTION
        
        elif state.current_stage == ConversationStage.PROFILE_COLLECTION:
            if state.intent == Intent.PRODUCT_COMPARISON:
                state.current_stage = ConversationStage.PRODUCT_COMPARISON
            elif state.intent == Intent.HUMAN_AGENT_REQUEST:
                state.current_stage = ConversationStage.HANDOFF
        
        return state
    
    def reset_conversation(self, conversation_id: str) -> ConversationState:
        """Reset conversation to initial state"""
        state = self.get_conversation(conversation_id)
        if state:
            state.current_stage = ConversationStage.GREETING
            state.intent = Intent.UNKNOWN
            state.customer_profile = CustomerProfile()
            state.customer_preferences = CustomerPreferences()
            state.missing_fields = []
            state.candidate_products = []
            state.eligible_products = []
            state.ineligible_products = []
            state.last_question = None
            state.updated_at = datetime.utcnow()
        
        return state
