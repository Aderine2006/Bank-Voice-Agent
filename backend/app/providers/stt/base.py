from abc import ABC, abstractmethod
from typing import Optional


class STTProvider(ABC):
    """Base class for Speech-to-Text providers"""
    
    @abstractmethod
    def transcribe(self, audio_data: bytes, language: str = "en") -> str:
        """
        Transcribe audio data to text
        
        Args:
            audio_data: Raw audio bytes
            language: Language code (e.g., 'en', 'hi', 'ta')
            
        Returns:
            Transcribed text
        """
        pass
    
    @abstractmethod
    def load_model(self):
        """Load the STT model"""
        pass
