"""
TTS API endpoints
"""

import os
import asyncio
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from loguru import logger

from app.models.schemas import (
    TTSRequest, TTSResponse, BatchTTSRequest, BatchTTSResponse
)
from app.auth import get_current_user
from app.config import settings

router = APIRouter()

@router.post("/generate", response_model=TTSResponse)
async def generate_speech(
    request: TTSRequest,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user)
) -> TTSResponse:
    """Generate speech from text"""
    try:
        from main import tts_engine
        
        if not tts_engine:
            raise HTTPException(status_code=503, detail="TTS engine not initialized")
        
        # Generate speech
        filename, metadata = await tts_engine.generate_speech(
            text=request.text,
            voice_id=request.voice_id,
            temperature=request.temperature,
            guidance_scale=request.guidance_scale,
            top_p=request.top_p,
            top_k=request.top_k,
            seed=request.seed
        )
        
        # Build response
        audio_url = f"/outputs/{filename}"
        
        return TTSResponse(
            success=True,
            filename=filename,
            audio_url=audio_url,
            metadata=metadata
        )
        
    except Exception as e:
        logger.error(f"TTS generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch", response_model=BatchTTSResponse)
async def batch_generate(
    request: BatchTTSRequest,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user)
) -> BatchTTSResponse:
    """Generate speech for multiple texts"""
    try:
        from main import tts_engine
        
        if not tts_engine:
            raise HTTPException(status_code=503, detail="TTS engine not initialized")
        
        results = []
        failed = []
        
        # Process each item
        for idx, item in enumerate(request.items):
            try:
                filename, metadata = await tts_engine.generate_speech(
                    text=item.text,
                    voice_id=item.voice_id,
                    temperature=item.temperature,
                    guidance_scale=item.guidance_scale,
                    top_p=item.top_p,
                    top_k=item.top_k,
                    seed=item.seed
                )
                
                audio_url = f"/outputs/{filename}"
                
                results.append(TTSResponse(
                    success=True,
                    filename=filename,
                    audio_url=audio_url,
                    metadata=metadata
                ))
                
            except Exception as e:
                logger.error(f"Failed to process item {idx}: {e}")
                failed.append({
                    "index": idx,
                    "text": item.text[:50] + "...",
                    "error": str(e)
                })
        
        return BatchTTSResponse(
            success=len(failed) == 0,
            results=results,
            failed=failed,
            total=len(request.items)
        )
        
    except Exception as e:
        logger.error(f"Batch generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{filename}")
async def download_audio(
    filename: str,
    current_user: str = Depends(get_current_user)
) -> FileResponse:
    """Download generated audio file"""
    file_path = Path(settings.OUTPUTS_DIR) / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=str(file_path),
        media_type="audio/mpeg",
        filename=filename
    )

@router.delete("/audio/{filename}")
async def delete_audio(
    filename: str,
    current_user: str = Depends(get_current_user)
) -> dict:
    """Delete generated audio file"""
    file_path = Path(settings.OUTPUTS_DIR) / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        os.remove(file_path)
        return {"success": True, "message": "File deleted successfully"}
    except Exception as e:
        logger.error(f"Failed to delete file: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete file")

@router.get("/list")
async def list_audio_files(
    limit: int = 50,
    offset: int = 0,
    current_user: str = Depends(get_current_user)
) -> dict:
    """List generated audio files"""
    try:
        output_dir = Path(settings.OUTPUTS_DIR)
        files = []
        
        # Get all audio files
        audio_files = list(output_dir.glob("*.mp3")) + list(output_dir.glob("*.wav"))
        audio_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Apply pagination
        paginated_files = audio_files[offset:offset + limit]
        
        for file_path in paginated_files:
            stat = file_path.stat()
            files.append({
                "filename": file_path.name,
                "size": stat.st_size,
                "created_at": stat.st_mtime,
                "url": f"/outputs/{file_path.name}"
            })
        
        return {
            "files": files,
            "total": len(audio_files),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Failed to list audio files: {e}")
        raise HTTPException(status_code=500, detail="Failed to list files")