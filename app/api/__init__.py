"""
API endpoints for driaClaude
"""

from fastapi import APIRouter

from app.api.tts import router as tts_router
from app.api.voices import router as voices_router

router = APIRouter()

# Include sub-routers
router.include_router(tts_router, prefix="/tts", tags=["TTS"])
router.include_router(voices_router, prefix="/voices", tags=["Voices"])