"""
Configuration settings for driaClaude
"""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Server settings
    PORT: int = 4144
    WORKERS: int = 2
    LOG_LEVEL: str = "INFO"
    
    # Security
    API_KEY: str = "default_key_change_in_production"
    ENABLE_AUTH: bool = False
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # Paths
    DATA_DIR: str = "/app/data"
    VOICES_DIR: str = "/app/voices"
    OUTPUTS_DIR: str = "/app/outputs"
    
    # Model settings
    MODEL_NAME: str = "nari-labs/Dia-1.6B-0626"
    MAX_NEW_TOKENS: int = 3072
    GUIDANCE_SCALE: float = 3.0
    TEMPERATURE: float = 1.8
    TOP_P: float = 0.90
    TOP_K: int = 45
    
    # Audio settings
    MAX_AUDIO_LENGTH: int = 300  # seconds
    SAMPLE_RATE: int = 22050
    
    # Voice cloning
    MAX_CLONE_DURATION: int = 10  # seconds
    MIN_CLONE_DURATION: int = 5   # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()