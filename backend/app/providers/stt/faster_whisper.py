from .base import STTProvider
from typing import Optional
import numpy as np
from faster_whisper import WhisperModel
import logging

logger = logging.getLogger(__name__)


class FasterWhisperSTT(STTProvider):
    """Faster-Whisper STT provider"""
    
    def __init__(self, model_size: str = "tiny", device: str = "cpu", compute_type: str = "int8"):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model: Optional[WhisperModel] = None
    
    def load_model(self):
        """Load the Faster-Whisper model"""
        if self.model is None:
            logger.info(f"Loading Faster-Whisper model: {self.model_size}")
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type
            )
            logger.info("Faster-Whisper model loaded successfully")
    
    def transcribe(self, audio_data: bytes, language: str = "en") -> str:
        """
        Transcribe audio data to text
        
        Args:
            audio_data: Raw audio bytes (WAV format)
            language: Language code
            
        Returns:
            Transcribed text
        """
        if self.model is None:
            self.load_model()
        
        try:
            # Convert audio bytes to numpy array
            # Note: This assumes WAV format. For production, proper audio processing needed
            import io
            import soundfile as sf
            
            audio_file = io.BytesIO(audio_data)
            audio_array, sample_rate = sf.read(audio_file)
            
            # Transcribe
            segments, info = self.model.transcribe(
                audio_array,
                language=language,
                beam_size=5,
                vad_filter=True,
                vad_parameters={"min_silence_duration_ms": 500}
            )
            
            # Combine segments
            transcript = " ".join([segment.text for segment in segments])
            
            logger.info(f"Transcription complete: {len(transcript)} chars")
            return transcript.strip()
            
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            raise
