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
    
    def transcribe(self, audio_data: bytes, language: str = "en", filename: str = None) -> str:
        """
        Transcribe audio data to text
        
        Args:
            audio_data: Raw audio bytes (any format - will be converted to WAV)
            language: Language code
            filename: Optional filename to help detect format
            
        Returns:
            Transcribed text
        """
        if self.model is None:
            self.load_model()
        
        try:
            import io
            import soundfile as sf
            import librosa
            import tempfile
            import os
            
            logger.info(f"Transcribing audio data: {len(audio_data)} bytes, filename: {filename}")
            
            # Determine file extension from filename or default to wav
            if filename:
                ext = os.path.splitext(filename)[1].lower()
                if not ext:
                    ext = '.wav'
            else:
                ext = '.wav'
            
            audio_array = None
            sample_rate = 16000
            
            # Method 1: Try librosa from BytesIO
            try:
                audio_file = io.BytesIO(audio_data)
                audio_array, sample_rate = librosa.load(audio_file, sr=16000)
                logger.info("Successfully loaded audio with librosa from BytesIO")
            except Exception as e:
                logger.warning(f"Librosa BytesIO load failed: {e}")
                
                # Method 2: Try scipy.io.wavfile for WAV files
                if ext == '.wav':
                    try:
                        from scipy.io import wavfile
                        audio_file = io.BytesIO(audio_data)
                        sample_rate, audio_array = wavfile.read(audio_file)
                        # Convert to float32 if needed
                        if audio_array.dtype.kind == 'i':
                            audio_array = audio_array.astype('float32') / 32768.0
                        # Convert stereo to mono if needed
                        if len(audio_array.shape) > 1:
                            audio_array = audio_array.mean(axis=1)
                        # Resample to 16kHz if needed
                        if sample_rate != 16000:
                            import librosa
                            audio_array = librosa.resample(audio_array, orig_sr=sample_rate, target_sr=16000)
                            sample_rate = 16000
                        logger.info("Successfully loaded audio with scipy.io.wavfile")
                    except Exception as e2:
                        logger.warning(f"Scipy wavfile load failed: {e2}")
                
                # Method 3: Try librosa with temp file
                if audio_array is None:
                    logger.warning(f"Trying temp file with extension {ext}")
                    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
                        temp_file.write(audio_data)
                        temp_path = temp_file.name
                    
                    try:
                        audio_array, sample_rate = librosa.load(temp_path, sr=16000)
                        logger.info(f"Successfully loaded audio with librosa from temp file: {temp_path}")
                    finally:
                        os.unlink(temp_path)
            
            if audio_array is None:
                raise ValueError("Failed to load audio with any method")
            
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
