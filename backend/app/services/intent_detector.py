from typing import Dict, Any
from app.models.conversation import Intent
from app.providers.llm.base import LLMProvider
import logging

logger = logging.getLogger(__name__)


class IntentDetector:
    """Detect conversation intent using LLM"""
    
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
    
    def detect_intent(self, user_message: str) -> Intent:
        """
        Detect the intent of the user's message
        
        Returns one of the predefined Intent values
        """
        system_prompt = """You are a banking conversation intent detector.
Classify the user's message into one of these intents:

- loan_discovery: User wants to explore or apply for a loan
- loan_eligibility: User asks about eligibility for a loan
- product_comparison: User wants to compare different loan products
- interest_rate_question: User asks about interest rates
- emi_question: User asks about EMI calculations
- document_question: User asks about required documents
- repayment_question: User asks about repayment terms
- application_process: User asks about how to apply
- existing_loan: User asks about an existing loan
- general_banking_question: General banking FAQ
- complaint: User has a complaint
- human_agent_request: User wants to speak to a human
- unknown: Cannot determine intent

Respond with valid JSON only:
{"intent": "intent_name"}
"""

        messages = [{"role": "user", "content": user_message}]
        
        try:
            result = self.llm_provider.generate_structured(
                messages=messages,
                system_prompt=system_prompt,
                output_schema={"intent": "string"}
            )
            
            intent_str = result.get("intent", "unknown").lower()
            
            # Map to enum
            for intent in Intent:
                if intent.value == intent_str:
                    return intent
            
            logger.warning(f"Unknown intent detected: {intent_str}")
            return Intent.UNKNOWN
            
        except Exception as e:
            logger.error(f"Intent detection error: {e}")
            return Intent.UNKNOWN
