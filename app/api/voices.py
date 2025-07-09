"""
Voice management API endpoints
"""

import os
import shutil
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from loguru import logger

from app.models.schemas import (
    VoiceCloneRequest, VoiceCloneResponse, Voice, VoiceListResponse
)
from app.auth import get_current_user
from app.config import settings

router = APIRouter()

@router.post("/clone", response_model=VoiceCloneResponse)
async def clone_voice(
    audio_file: UploadFile = File(...),
    name: str = Form(...),
    transcript: str = Form(...),
    description: str = Form(None),
    current_user: str = Depends(get_current_user)
) -> VoiceCloneResponse:
    """Clone a voice from an audio sample"""
    try:
        from main import tts_engine
        
        if not tts_engine:
            raise HTTPException(status_code=503, detail="TTS engine not initialized")
        
        # Validate file type
        allowed_types = [".mp3", ".wav", ".flac", ".ogg"]
        file_ext = Path(audio_file.filename).suffix.lower()
        if file_ext not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
            )
        
        # Save uploaded file
        temp_path = Path(settings.VOICES_DIR) / f"temp_{audio_file.filename}"
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(audio_file.file, f)
        
        try:
            # Clone voice
            voice_id = await tts_engine.clone_voice(
                audio_path=str(temp_path),
                transcript=transcript,
                voice_name=name,
                voice_description=description
            )
            
            # Move file to permanent location
            perm_path = Path(settings.VOICES_DIR) / f"{voice_id}{file_ext}"
            shutil.move(str(temp_path), str(perm_path))
            
            return VoiceCloneResponse(
                success=True,
                voice_id=voice_id,
                message=f"Voice '{name}' cloned successfully"
            )
            
        finally:
            # Clean up temp file if it exists
            if temp_path.exists():
                os.remove(temp_path)
        
    except Exception as e:
        logger.error(f"Voice cloning failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list", response_model=VoiceListResponse)
async def list_voices(
    current_user: str = Depends(get_current_user)
) -> VoiceListResponse:
    """List all available voices"""
    try:
        from main import tts_engine
        
        if not tts_engine:
            raise HTTPException(status_code=503, detail="TTS engine not initialized")
        
        voices_data = await tts_engine.list_voices()
        
        # Convert to Voice objects
        voices = [
            Voice(
                id=v["id"],
                name=v["name"],
                description=v.get("description", ""),
                created_at=v["created_at"],
                duration=v.get("duration", 0)
            )
            for v in voices_data
        ]
        
        return VoiceListResponse(
            voices=voices,
            total=len(voices)
        )
        
    except Exception as e:
        logger.error(f"Failed to list voices: {e}")
        raise HTTPException(status_code=500, detail="Failed to list voices")

@router.delete("/{voice_id}")
async def delete_voice(
    voice_id: str,
    current_user: str = Depends(get_current_user)
) -> dict:
    """Delete a cloned voice"""
    try:
        from main import tts_engine
        
        if not tts_engine:
            raise HTTPException(status_code=503, detail="TTS engine not initialized")
        
        success = await tts_engine.delete_voice(voice_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Voice not found")
        
        # Delete associated audio file
        voices_dir = Path(settings.VOICES_DIR)
        for audio_file in voices_dir.glob(f"{voice_id}.*"):
            try:
                os.remove(audio_file)
            except Exception as e:
                logger.warning(f"Failed to delete voice file: {e}")
        
        return {"success": True, "message": "Voice deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete voice: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete voice")

@router.get("/{voice_id}")
async def get_voice(
    voice_id: str,
    current_user: str = Depends(get_current_user)
) -> dict:
    """Get voice details"""
    try:
        from main import tts_engine
        
        if not tts_engine:
            raise HTTPException(status_code=503, detail="TTS engine not initialized")
        
        voices = await tts_engine.list_voices()
        
        for voice in voices:
            if voice["id"] == voice_id:
                return voice
        
        raise HTTPException(status_code=404, detail="Voice not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get voice: {e}")
        raise HTTPException(status_code=500, detail="Failed to get voice")