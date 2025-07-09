"""
Pydantic schemas for API requests and responses
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from datetime import datetime

class TTSRequest(BaseModel):
    """Text-to-speech generation request"""
    text: str = Field(..., description="Text to convert to speech. Use [S1] and [S2] for dialogue")
    voice_id: Optional[str] = Field(None, description="Voice ID for cloned voice")
    temperature: float = Field(1.8, description="Sampling temperature", ge=0.1, le=2.0)
    guidance_scale: float = Field(3.0, description="Guidance scale for generation", ge=1.0, le=10.0)
    top_p: float = Field(0.90, description="Top-p sampling parameter", ge=0.1, le=1.0)
    top_k: int = Field(45, description="Top-k sampling parameter", ge=1, le=100)
    seed: Optional[int] = Field(None, description="Random seed for reproducibility")
    
    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError("Text cannot be empty")
        return v

class TTSResponse(BaseModel):
    """Text-to-speech generation response"""
    success: bool
    filename: str
    audio_url: str
    metadata: Dict
    duration: Optional[float] = None

class VoiceCloneRequest(BaseModel):
    """Voice cloning request"""
    name: str = Field(..., description="Name for the cloned voice")
    description: Optional[str] = Field(None, description="Description of the voice")
    transcript: str = Field(..., description="Transcript of the audio sample")
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Voice name cannot be empty")
        return v
    
    @validator('transcript')
    def validate_transcript(cls, v):
        if not v.strip():
            raise ValueError("Transcript cannot be empty")
        return v

class VoiceCloneResponse(BaseModel):
    """Voice cloning response"""
    success: bool
    voice_id: str
    message: str

class Voice(BaseModel):
    """Voice information"""
    id: str
    name: str
    description: str
    created_at: datetime
    duration: float

class VoiceListResponse(BaseModel):
    """Voice list response"""
    voices: List[Voice]
    total: int

class BatchTTSRequest(BaseModel):
    """Batch TTS generation request"""
    items: List[TTSRequest] = Field(..., description="List of TTS requests")
    
    @validator('items')
    def validate_items(cls, v):
        if not v:
            raise ValueError("Batch must contain at least one item")
        if len(v) > 10:
            raise ValueError("Batch size cannot exceed 10 items")
        return v

class BatchTTSResponse(BaseModel):
    """Batch TTS generation response"""
    success: bool
    results: List[TTSResponse]
    failed: List[Dict]
    total: int