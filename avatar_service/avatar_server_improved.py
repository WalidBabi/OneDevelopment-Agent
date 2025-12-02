"""
Luna Avatar GPU Service - Improved Version with High-Quality TTS
================================================================

Current Status:
- ✅ High-quality TTS (edge-tts with Microsoft Neural Voices)
- ⚠️  Video generation: Placeholder (LivePortrait requires video input, not audio)

To enable full video generation, you need to install SadTalker:
    See: INSTALL_SADTALKER.md

For now, this generates high-quality audio that the frontend can use.
"""

import os
import sys
import uuid
import logging
import asyncio
from pathlib import Path
from typing import Optional
import torch
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import our TTS manager
from tts_manager import get_tts_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="Luna Avatar GPU Service", version="3.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
OUTPUT_DIR = Path("./generated_videos")
OUTPUT_DIR.mkdir(exist_ok=True)

AUDIO_DIR = Path("./generated_audio")
AUDIO_DIR.mkdir(exist_ok=True)

AVATAR_IMAGE = Path("./luna_base.png").resolve()

# Device
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
logger.info(f"Using device: {DEVICE}")

# Initialize TTS Manager
tts_manager = get_tts_manager()


class AvatarRequest(BaseModel):
    text: str
    audio_url: Optional[str] = None
    voice_id: Optional[str] = "default"  # default, professional, british, casual


class AvatarResponse(BaseModel):
    video_url: str
    audio_url: str  # High-quality audio URL
    video_id: str
    duration: float
    status: str
    message: Optional[str] = None


def cleanup_old_files():
    """Clean up old files"""
    import time
    current_time = time.time()
    
    for directory in [OUTPUT_DIR, AUDIO_DIR]:
        for file in directory.glob("*.*"):
            if current_time - file.stat().st_mtime > 3600:  # 1 hour
                file.unlink()
                logger.info(f"Cleaned up: {file.name}")


@app.on_event("startup")
async def startup():
    """Startup checks"""
    logger.info("Luna Avatar Service Starting...")
    logger.info(f"Luna base image: {AVATAR_IMAGE.exists()}")
    logger.info(f"GPU available: {torch.cuda.is_available()}")
    logger.info(f"TTS engines: {len(tts_manager.engines)}")


@app.get("/")
def root():
    return {
        "service": "Luna Avatar GPU Service",
        "version": "3.0.0",
        "status": "running",
        "device": DEVICE,
        "gpu_available": torch.cuda.is_available(),
        "tts_engines": [engine[0] for engine in tts_manager.engines],
        "video_generation": "placeholder (install SadTalker for full support)"
    }


@app.get("/health")
def health_check():
    gpu_info = {}
    if torch.cuda.is_available():
        gpu_info = {
            "name": torch.cuda.get_device_name(0),
            "memory_allocated": f"{torch.cuda.memory_allocated(0) / 1024**3:.2f} GB",
            "memory_reserved": f"{torch.cuda.memory_reserved(0) / 1024**3:.2f} GB",
        }
    
    return {
        "status": "healthy",
        "device": DEVICE,
        "gpu_info": gpu_info,
        "tts_available": len(tts_manager.engines) > 0,
        "tts_primary": tts_manager.engines[0][0] if tts_manager.engines else "none"
    }


@app.post("/generate", response_model=AvatarResponse)
async def generate_avatar(request: AvatarRequest, background_tasks: BackgroundTasks):
    """
    Generate avatar with high-quality audio
    
    Currently generates audio only. For full video generation, install SadTalker.
    """
    
    if not AVATAR_IMAGE.exists():
        raise HTTPException(status_code=500, detail="luna_base.png not found")
    
    video_id = str(uuid.uuid4())
    audio_path = AUDIO_DIR / f"{video_id}.mp3"
    video_path = OUTPUT_DIR / f"{video_id}.mp4"
    
    try:
        logger.info(f"Generating avatar for: {request.text[:50]}...")
        
        # Step 1: Generate high-quality audio
        success = await tts_manager.generate_speech(
            text=request.text,
            output_path=str(audio_path),
            voice=request.voice_id
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="TTS generation failed")
        
        logger.info(f"✓ High-quality audio generated: {audio_path}")
        
        # Step 2: Estimate duration from audio file
        try:
            from mutagen.mp3 import MP3
            audio = MP3(str(audio_path))
            duration = audio.info.length
        except:
            # Rough estimate: 150 words per minute, 5 chars per word
            words = len(request.text.split())
            duration = (words / 150) * 60
        
        logger.info(f"✓ Audio duration: {duration:.2f}s")
        
        # Step 3: Video generation (placeholder for now)
        # TODO: Integrate SadTalker here
        # For now, we'll indicate video generation is pending
        
        background_tasks.add_task(cleanup_old_files)
        
        # Return audio URL (frontend can play this immediately)
        return AvatarResponse(
            video_url=f"http://localhost:8000/videos/{video_id}.mp4",
            audio_url=f"http://localhost:8000/audio/{video_id}.mp3",
            video_id=video_id,
            duration=duration,
            status="audio_ready",  # "video_ready" when full video generation works
            message="High-quality audio generated. Video generation requires SadTalker installation."
        )
        
    except Exception as e:
        logger.error(f"Error generating avatar: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/audio/{filename}")
async def get_audio(filename: str):
    """Serve generated audio"""
    audio_path = AUDIO_DIR / filename
    
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio not found")
    
    return FileResponse(
        audio_path,
        media_type="audio/mpeg",
        headers={"Content-Disposition": f"inline; filename={filename}"}
    )


@app.get("/videos/{video_id}")
async def get_video(video_id: str):
    """Serve generated video"""
    video_path = OUTPUT_DIR / video_id
    
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")
    
    return FileResponse(
        video_path,
        media_type="video/mp4",
        headers={"Content-Disposition": f"inline; filename={video_id}"}
    )


@app.delete("/videos/{video_id}")
async def delete_video(video_id: str):
    """Delete a video"""
    video_path = OUTPUT_DIR / video_id
    
    if video_path.exists():
        video_path.unlink()
        return {"status": "deleted", "video_id": video_id}
    
    raise HTTPException(status_code=404, detail="Video not found")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

