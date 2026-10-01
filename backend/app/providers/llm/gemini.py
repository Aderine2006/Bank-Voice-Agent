from .base import LLMProvider
from typing import List, Dict, Any, Optional
import google.generativeai as genai
import json
import logging

logger = logging.getLogger(__name__)


class GeminiLLM(LLMProvider):
    """Google Gemini LLM provider"""
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model_name = model
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
    
    def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate response from Gemini
        
        Args:
            messages: List of message dicts
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            
        Returns:
            Generated text
        """
        try:
            # Build conversation
            if system_prompt:
                full_messages = [{"role": "system", "parts": [system_prompt]}]
            else:
                full_messages = []
            
            for msg in messages:
                role = "user" if msg["role"] == "user" else "model"
                full_messages.append({"role": role, "parts": [msg["content"]]})
            
            # Generate
            generation_config = {
                "temperature": temperature,
            }
            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens
            
            response = self.model.generate_content(
                full_messages,
                generation_config=generation_config
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            raise
    
    def generate_structured(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        output_schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate structured JSON response from Gemini
        
        Args:
            messages: List of message dicts
            system_prompt: Optional system prompt
            output_schema: Expected output schema
            
        Returns:
            Structured response as dict
        """
        try:
            # Add JSON instruction to system prompt
            json_instruction = "\n\nIMPORTANT: Respond with valid JSON only, no other text."
            if system_prompt:
                system_prompt += json_instruction
            else:
                system_prompt = json_instruction
            
            if output_schema:
                system_prompt += f"\n\nExpected JSON structure:\n{json.dumps(output_schema, indent=2)}"
            
            # Generate
            response_text = self.generate(messages, system_prompt, temperature=0.3)
            
            # Parse JSON
            # Remove markdown code blocks if present
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            return json.loads(response_text.strip())
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}, Response: {response_text}")
            raise
        except Exception as e:
            logger.error(f"Structured generation error: {e}")
            raise
