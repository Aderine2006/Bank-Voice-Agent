from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.conversation import (
    ConversationRequest, ConversationResponse,
    ConversationState, Message
)
from app.services.conversation_manager import ConversationManager
from app.services.response_generator import ResponseGenerator
from app.services.loan_matching import LoanMatchingEngine
from app.providers.llm.base import LLMProvider
from app.core.logging import logger
import time

router = APIRouter(prefix="/api/conversation", tags=["conversation"])


# Dependency injection (simplified for MVP)
def get_conversation_manager() -> ConversationManager:
    from app.main import conversation_manager
    return conversation_manager


def get_response_generator() -> ResponseGenerator:
    from app.main import response_generator
    return response_generator


def get_loan_matching_engine() -> LoanMatchingEngine:
    from app.main import loan_matching_engine
    return loan_matching_engine


def get_products() -> List:
    from app.main import products
    return products


@router.post("/start", response_model=ConversationState)
async def start_conversation(
    manager: ConversationManager = Depends(get_conversation_manager)
):
    """Start a new conversation session"""
    try:
        state = manager.start_conversation()
        logger.info(f"Started new conversation: {state.conversation_id}")
        return state
    except Exception as e:
        logger.error(f"Error starting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/message", response_model=ConversationResponse)
async def send_message(
    request: ConversationRequest,
    manager: ConversationManager = Depends(get_conversation_manager),
    response_generator: ResponseGenerator = Depends(get_response_generator),
    matching_engine: LoanMatchingEngine = Depends(get_loan_matching_engine),
    products: List = Depends(get_products)
):
    """Send a message in the conversation"""
    start_time = time.time()
    
    try:
        # Get or create conversation
        if request.conversation_id:
            state = manager.get_conversation(request.conversation_id)
            if not state:
                state = manager.start_conversation()
        else:
            state = manager.start_conversation()
        
        # Process message
        state = manager.process_message(
            state.conversation_id,
            request.message,
            products
        )
        
        # Get product matches
        matches = matching_engine.match_products(
            products,
            state.customer_profile,
            state.customer_preferences
        )
        
        # Generate response
        assistant_response = response_generator.generate_response(
            state,
            matches
        )
        
        # Build response
        response = ConversationResponse(
            conversation_id=state.conversation_id,
            transcript=request.message,
            intent=state.intent,
            assistant_response=assistant_response,
            profile_updates=state.customer_profile.model_dump(),
            missing_information=state.missing_fields,
            loan_matches=[
                {
                    "product_id": m.product.product_id,
                    "product_name": m.product.product_name,
                    "status": m.eligibility.status,
                    "match_score": m.eligibility.match_score,
                    "emi": m.emi_calculation.emi if m.emi_calculation else None
                }
                for m in matches
            ],
            workflow_stage=state.current_stage,
            audio_url=None,  # Will be set by TTS endpoint
            sources=[]
        )
        
        duration_ms = (time.time() - start_time) * 1000
        logger.log_response(state.conversation_id, 200, duration_ms)
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{conversation_id}", response_model=ConversationState)
async def get_conversation(
    conversation_id: str,
    manager: ConversationManager = Depends(get_conversation_manager)
):
    """Get conversation state"""
    state = manager.get_conversation(conversation_id)
    if not state:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return state


@router.post("/{conversation_id}/reset", response_model=ConversationState)
async def reset_conversation(
    conversation_id: str,
    manager: ConversationManager = Depends(get_conversation_manager)
):
    """Reset conversation to initial state"""
    state = manager.reset_conversation(conversation_id)
    if not state:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return state
