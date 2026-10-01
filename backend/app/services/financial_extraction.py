from typing import Dict, Any
from app.models.conversation import CustomerProfile
from app.providers.llm.base import LLMProvider
import logging

logger = logging.getLogger(__name__)


class FinancialExtractor:
    """Extract financial information from natural language using LLM"""
    
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
    
    def extract_profile(
        self,
        user_message: str,
        existing_profile: CustomerProfile
    ) -> CustomerProfile:
        """
        Extract financial information from user message
        
        Updates existing profile with new information without overwriting
        known values with null
        """
        system_prompt = """You are a financial information extraction assistant.
Extract structured financial information from the user's message.
Respond with valid JSON only.

Extract these fields if mentioned:
- age: integer
- employment_type: "salaried", "self-employed", or "business"
- occupation: string
- monthly_income: number (in rupees)
- monthly_expenses: number
- existing_emi: number
- credit_score: integer
- requested_loan_amount: number (in rupees)
- loan_purpose: string
- preferred_tenure_months: integer
- preferred_emi: number
- employment_duration_months: integer
- location: string

IMPORTANT:
- Only extract values that are explicitly mentioned
- Use null for fields not mentioned
- Handle natural language: "6 lakh" = 600000, "55k" = 55000
"""

        messages = [{"role": "user", "content": user_message}]
        
        try:
            extracted = self.llm_provider.generate_structured(
                messages=messages,
                system_prompt=system_prompt,
                output_schema={
                    "age": "integer or null",
                    "employment_type": "string or null",
                    "occupation": "string or null",
                    "monthly_income": "number or null",
                    "monthly_expenses": "number or null",
                    "existing_emi": "number or null",
                    "credit_score": "integer or null",
                    "requested_loan_amount": "number or null",
                    "loan_purpose": "string or null",
                    "preferred_tenure_months": "integer or null",
                    "preferred_emi": "number or null",
                    "employment_duration_months": "integer or null",
                    "location": "string or null"
                }
            )
            
            # Update profile without overwriting known values with null
            profile_dict = existing_profile.model_dump()
            
            for field, value in extracted.items():
                if value is not None:
                    profile_dict[field] = value
            
            return CustomerProfile(**profile_dict)
            
        except Exception as e:
            logger.error(f"Financial extraction error: {e}")
            return existing_profile
