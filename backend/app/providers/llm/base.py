from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class LLMProvider(ABC):
    """Base class for LLM providers"""
    
    @abstractmethod
    def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate response from LLM
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        pass
    
    @abstractmethod
    def generate_structured(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        output_schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate structured JSON response from LLM
        
        Args:
            messages: List of message dicts
            system_prompt: Optional system prompt
            output_schema: Expected output schema
            
        Returns:
            Structured response as dict
        """
        pass
