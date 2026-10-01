from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Optional
from app.providers.stt.base import STTProvider
from app.providers.tts.base import TTSProvider
from app.core.logging import logger
import time

router = APIRouter(prefix="/api/voice", tags=["voice"])


def get_stt_provider() -> STTProvider:
    from app.main import stt_provider
    return stt_provider


def get_tts_provider() -> TTSProvider:
    from app.main import tts_provider
    return tts_provider


@router.post("/transcribe")
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    stt: STTProvider = Depends(get_stt_provider)
):
    """Transcribe audio to text"""
    start_time = time.time()
    
    try:
        # Read audio data
        audio_data = await audio_file.read()
        
        if not audio_data:
            raise HTTPException(status_code=400, detail="No audio data provided")
        
        # Transcribe
        transcript = stt.transcribe(audio_data)
        
        duration_ms = (time.time() - start_time) * 1000
        logger.log_provider_call("STT", "transcribe", duration_ms)
        
        return {"transcript": transcript}
        
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/synthesize")
async def synthesize_speech(
    text: str,
    voice: Optional[str] = "default",
    language: Optional[str] = "en",
    tts: TTSProvider = Depends(get_tts_provider)
):
    """Synthesize speech from text"""
    start_time = time.time()
    
    try:
        if not text:
            raise HTTPException(status_code=400, detail="No text provided")
        
        # Synthesize
        audio_data = tts.synthesize(text, voice, language)
        
        duration_ms = (time.time() - start_time) * 1000
        logger.log_provider_call("TTS", "synthesize", duration_ms)
        
        from fastapi.responses import Response
        return Response(
            content=audio_data,
            media_type="audio/wav"
        )
        
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
