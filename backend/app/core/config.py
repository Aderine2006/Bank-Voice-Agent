from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "BankVoice AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/bankvoice.db"
    
    # LLM Provider
    LLM_PROVIDER: str = "gemini"
    LLM_MODEL: str = "gemini-1.5-flash"
    GEMINI_API_KEY: Optional[str] = None
    
    # STT Provider
    STT_PROVIDER: str = "faster_whisper"
    STT_MODEL: str = "tiny"
    STT_DEVICE: str = "cpu"
    STT_COMPUTE_TYPE: str = "int8"
    
    # TTS Provider
    TTS_PROVIDER: str = "kokoro"
    TTS_VOICE: str = "af_heart"
    TTS_LANGUAGE: str = "en"
    
    # RAG
    FAISS_INDEX_PATH: str = "./data/faiss"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50
    
    # Bank Data
    BANK_DATA_PATH: str = "./data/banks"
    DEFAULT_BANK_ID: str = "demo-bank"
    
    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"
    CORS_ORIGINS: list = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
