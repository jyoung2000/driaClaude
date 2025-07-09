#!/usr/bin/env python3
"""
driaClaude - CPU-based TTS Web Service
Based on dia TTS model with web interface and API
"""

import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger

from app.config import settings
from app.api import router as api_router
from app.web import router as web_router
from app.models.tts_engine import TTSEngine

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    level=settings.LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# Global TTS engine instance
tts_engine = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global tts_engine
    
    logger.info("Starting driaClaude TTS Service...")
    
    # Create necessary directories
    for dir_path in [settings.DATA_DIR, settings.VOICES_DIR, settings.OUTPUTS_DIR]:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # Initialize TTS engine
    logger.info("Initializing TTS engine...")
    tts_engine = TTSEngine()
    await tts_engine.initialize()
    
    # Store engine in app state
    app.state.tts_engine = tts_engine
    
    logger.info(f"driaClaude started on port {settings.PORT}")
    
    yield
    
    # Cleanup
    logger.info("Shutting down driaClaude...")
    if tts_engine:
        await tts_engine.cleanup()

# Create FastAPI app
app = FastAPI(
    title="driaClaude",
    description="CPU-based TTS Web Service with voice cloning and granular control",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/outputs", StaticFiles(directory=settings.OUTPUTS_DIR), name="outputs")

# Include routers
app.include_router(api_router, prefix="/api/v1")
app.include_router(web_router)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "driaClaude",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        workers=settings.WORKERS,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )