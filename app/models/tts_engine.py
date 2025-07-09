"""
TTS Engine wrapper for dia model
"""

import os
import asyncio
import torch
import torchaudio
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from datetime import datetime
import hashlib
import json

from transformers import AutoProcessor, DiaForConditionalGeneration
from loguru import logger

from app.config import settings

class TTSEngine:
    """TTS Engine for CPU-based text-to-speech generation"""
    
    def __init__(self):
        self.model = None
        self.processor = None
        self.device = "cpu"  # Force CPU usage
        self.voices_db = {}
        self.voices_db_path = Path(settings.VOICES_DIR) / "voices_db.json"
        
    async def initialize(self):
        """Initialize the TTS model and processor"""
        try:
            logger.info(f"Loading model from {settings.MODEL_NAME}...")
            
            # Load processor and model
            self.processor = AutoProcessor.from_pretrained(settings.MODEL_NAME)
            self.model = DiaForConditionalGeneration.from_pretrained(
                settings.MODEL_NAME,
                torch_dtype=torch.float32  # Use float32 for CPU
            ).to(self.device)
            
            # Set model to evaluation mode
            self.model.eval()
            
            # Load voices database
            await self._load_voices_db()
            
            logger.info("TTS Engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            raise
    
    async def generate_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        temperature: float = settings.TEMPERATURE,
        guidance_scale: float = settings.GUIDANCE_SCALE,
        top_p: float = settings.TOP_P,
        top_k: int = settings.TOP_K,
        seed: Optional[int] = None
    ) -> Tuple[str, Dict]:
        """Generate speech from text"""
        try:
            # Prepare input text
            if not text.startswith("[S1]") and not text.startswith("[S2]"):
                text = f"[S1] {text}"
            
            # Handle voice cloning if voice_id provided
            if voice_id and voice_id in self.voices_db:
                voice_data = self.voices_db[voice_id]
                # Prepend voice transcript for cloning
                text = f"{voice_data['transcript']} {text}"
            
            # Set seed for reproducibility
            if seed is not None:
                torch.manual_seed(seed)
            
            # Process input
            inputs = self.processor(
                text=[text],
                padding=True,
                return_tensors="pt"
            ).to(self.device)
            
            # Generate audio
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=settings.MAX_NEW_TOKENS,
                    guidance_scale=guidance_scale,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k
                )
            
            # Decode outputs
            audio_outputs = self.processor.batch_decode(outputs)
            
            # Save audio file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tts_{timestamp}_{hashlib.md5(text.encode()).hexdigest()[:8]}.mp3"
            output_path = Path(settings.OUTPUTS_DIR) / filename
            
            self.processor.save_audio(audio_outputs, str(output_path))
            
            # Prepare metadata
            metadata = {
                "text": text,
                "voice_id": voice_id,
                "parameters": {
                    "temperature": temperature,
                    "guidance_scale": guidance_scale,
                    "top_p": top_p,
                    "top_k": top_k,
                    "seed": seed
                },
                "timestamp": timestamp,
                "filename": filename
            }
            
            return filename, metadata
            
        except Exception as e:
            logger.error(f"Speech generation failed: {e}")
            raise
    
    async def clone_voice(
        self,
        audio_path: str,
        transcript: str,
        voice_name: str,
        voice_description: Optional[str] = None
    ) -> str:
        """Clone a voice from audio sample"""
        try:
            # Load and validate audio
            waveform, sample_rate = torchaudio.load(audio_path)
            duration = waveform.shape[1] / sample_rate
            
            if duration < settings.MIN_CLONE_DURATION:
                raise ValueError(f"Audio too short. Minimum {settings.MIN_CLONE_DURATION}s required")
            if duration > settings.MAX_CLONE_DURATION:
                raise ValueError(f"Audio too long. Maximum {settings.MAX_CLONE_DURATION}s allowed")
            
            # Generate voice ID
            voice_id = hashlib.md5(f"{voice_name}_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
            
            # Store voice data
            voice_data = {
                "id": voice_id,
                "name": voice_name,
                "description": voice_description or "",
                "transcript": transcript,
                "audio_path": audio_path,
                "duration": duration,
                "created_at": datetime.now().isoformat()
            }
            
            self.voices_db[voice_id] = voice_data
            await self._save_voices_db()
            
            logger.info(f"Voice cloned successfully: {voice_name} (ID: {voice_id})")
            return voice_id
            
        except Exception as e:
            logger.error(f"Voice cloning failed: {e}")
            raise
    
    async def list_voices(self) -> List[Dict]:
        """List all available voices"""
        return list(self.voices_db.values())
    
    async def delete_voice(self, voice_id: str) -> bool:
        """Delete a voice"""
        if voice_id in self.voices_db:
            del self.voices_db[voice_id]
            await self._save_voices_db()
            return True
        return False
    
    async def _load_voices_db(self):
        """Load voices database from file"""
        if self.voices_db_path.exists():
            try:
                with open(self.voices_db_path, 'r') as f:
                    self.voices_db = json.load(f)
                logger.info(f"Loaded {len(self.voices_db)} voices")
            except Exception as e:
                logger.error(f"Failed to load voices database: {e}")
                self.voices_db = {}
    
    async def _save_voices_db(self):
        """Save voices database to file"""
        try:
            with open(self.voices_db_path, 'w') as f:
                json.dump(self.voices_db, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save voices database: {e}")
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.model:
            del self.model
        if self.processor:
            del self.processor
        torch.cuda.empty_cache()