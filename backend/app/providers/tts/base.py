from abc import ABC, abstractmethod


class TTSProvider(ABC):
    """Base class for Text-to-Speech providers"""
    
    @abstractmethod
    def synthesize(self, text: str, voice: str = "default", language: str = "en") -> bytes:
        """
        Synthesize speech from text
        
        Args:
            text: Text to synthesize
            voice: Voice identifier
            language: Language code
            
        Returns:
            Audio bytes
        """
        pass
    
    @abstractmethod
    def load_model(self):
        """Load the TTS model"""
        pass
