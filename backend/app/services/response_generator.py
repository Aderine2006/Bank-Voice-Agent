from typing import List, Dict, Any, Optional
from app.models.conversation import ConversationState, ConversationStage, Intent
from app.models.loan import ProductMatch
from app.providers.llm.base import LLMProvider
import logging

logger = logging.getLogger(__name__)


class ResponseGenerator:
    """Generate natural language responses using LLM"""
    
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
    
    def generate_response(
        self,
        state: ConversationState,
        product_matches: List[ProductMatch],
        bank_name: str = "NovaBank"
    ) -> str:
        """
        Generate appropriate response based on conversation state
        
        Returns natural language response
        """
        system_prompt = f"""You are Ava, a professional banking loan assistant for {bank_name}.
Your role is to help customers explore loan options and understand requirements.

IMPORTANT RULES:
- Be professional, warm, patient, and concise
- Do not pretend to be human
- Do not guarantee loan approval
- Do not invent interest rates, fees, or policies
- Use only the information provided in the context
- Clearly distinguish between information, eligibility, and final approval
- If information is unavailable, say you don't have enough verified information
- Never ask for passwords, OTPs, PINs, or CVV
- Keep responses concise and conversational

Current conversation stage: {state.current_stage.value}
Customer intent: {state.intent.value}
"""

        # Build context
        context = self._build_context(state, product_matches, bank_name)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nGenerate a helpful response."}
        ]
        
        try:
            response = self.llm_provider.generate(
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Response generation error: {e}")
            return self._get_fallback_response(state)
    
    def _build_context(
        self,
        state: ConversationState,
        product_matches: List[ProductMatch],
        bank_name: str
    ) -> str:
        """Build context string for LLM"""
        
        context_parts = []
        
        # Customer profile
        profile = state.customer_profile
        profile_info = []
        if profile.requested_loan_amount:
            profile_info.append(f"Requested loan amount: ₹{profile.requested_loan_amount:,.0f}")
        if profile.monthly_income:
            profile_info.append(f"Monthly income: ₹{profile.monthly_income:,.0f}")
        if profile.employment_type:
            profile_info.append(f"Employment type: {profile.employment_type}")
        if profile.loan_purpose:
            profile_info.append(f"Loan purpose: {profile.loan_purpose}")
        if profile.age:
            profile_info.append(f"Age: {profile.age}")
        if profile.existing_emi:
            profile_info.append(f"Existing EMI: ₹{profile.existing_emi:,.0f}")
        
        if profile_info:
            context_parts.append("Customer Profile:")
            context_parts.append("\n".join(f"- {info}" for info in profile_info))
        
        # Missing information
        if state.missing_fields:
            context_parts.append("\nMissing Information:")
            context_parts.append("\n".join(f"- {field}" for field in state.missing_fields))
        
        # Product matches
        if product_matches:
            context_parts.append("\nMatching Products:")
            for match in product_matches[:3]:  # Limit to top 3
                product = match.product
                eligibility = match.eligibility
                
                match_info = f"\n- {product.product_name}"
                match_info += f"\n  Status: {eligibility.status}"
                
                if eligibility.reasons:
                    match_info += f"\n  Reasons: {', '.join(eligibility.reasons[:2])}"
                
                if match.emi_calculation:
                    match_info += f"\n  Estimated EMI: ₹{match.emi_calculation.emi:,.0f}/month"
                
                context_parts.append(match_info)
        
        return "\n".join(context_parts)
    
    def _get_fallback_response(self, state: ConversationState) -> str:
        """Get fallback response when LLM fails"""
        
        if state.current_stage == ConversationStage.GREETING:
            return "Hi, I'm Ava, the bank's virtual assistant. I can help you explore loan options and understand the information required. How can I help you today?"
        
        elif state.current_stage == ConversationStage.PROFILE_COLLECTION:
            if state.missing_fields:
                field_map = {
                    "requested_loan_amount": "How much would you like to borrow?",
                    "loan_purpose": "What would you like to use the loan for?",
                    "monthly_income": "What is your approximate monthly income?",
                    "employment_type": "Are you salaried or self-employed?",
                    "age": "May I know your age?",
                }
                for field in state.missing_fields:
                    if field in field_map:
                        return field_map[field]
            return "Could you please provide more details about your loan requirements?"
        
        elif state.current_stage == ConversationStage.PRODUCT_MATCHING:
            return "Based on your information, I've found some matching loan options. Would you like me to explain the differences between them?"
        
        return "I'm here to help you explore loan options. Could you please tell me more about what you're looking for?"
