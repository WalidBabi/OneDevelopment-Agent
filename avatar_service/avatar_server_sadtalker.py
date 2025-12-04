"""
Luna Avatar Service with SadTalker Integration
===============================================
This version actually generates videos using SadTalker!
"""
import os
import sys
from pathlib import Path
import uuid
import logging
from typing import Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
import torch

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Directories
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "generated_videos"
AUDIO_DIR = BASE_DIR / "generated_audio"
TEMP_DIR = BASE_DIR / "temp_sadtalker"
AVATAR_IMAGE = BASE_DIR / "luna_base.png"

# Create directories
OUTPUT_DIR.mkdir(exist_ok=True)
AUDIO_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# Device
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
logger.info(f"Using device: {DEVICE}")

# Try to import SadTalker generator
SadTalkerGenerator = None
try:
    from sadtalker_generator import SadTalkerGenerator
    logger.info("SadTalkerGenerator imported successfully")
except Exception as e:
    logger.warning(f"Could not import SadTalkerGenerator: {e}")
    SadTalkerGenerator = None

sadtalker_generator = None

app = FastAPI(title="Luna Avatar Service with SadTalker")


class AvatarRequest(BaseModel):
    text: str
    audio_url: Optional[str] = None
    voice_id: Optional[str] = "default"
    quality: Optional[str] = "fast"  # fast, standard, high
    duration: Optional[float] = None


class AvatarResponse(BaseModel):
    video_url: str
    video_id: str
    duration: float
    status: str
    audio_url: Optional[str] = None


def cleanup_old_files():
    """Clean up files older than 1 hour"""
    import time
    current_time = time.time()
    for video_file in OUTPUT_DIR.glob("*.mp4"):
        if current_time - video_file.stat().st_mtime > 3600:
            video_file.unlink()
            logger.info(f"Cleaned up: {video_file.name}")


@app.on_event("startup")
async def startup_event():
    """Initialize SadTalker on startup"""
    global sadtalker_generator
    
    logger.info("=== Luna Avatar Service Starting ===")
    logger.info(f"Device: {DEVICE}")
    logger.info(f"Avatar image exists: {AVATAR_IMAGE.exists()}")
    logger.info(f"Output directory: {OUTPUT_DIR}")
    
    if DEVICE == "cuda":
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
        logger.info(f"CUDA Version: {torch.version.cuda}")
    
    # Initialize SadTalker if available
    if SadTalkerGenerator:
        try:
            logger.info("Initializing SadTalker...")
            sadtalker_generator = SadTalkerGenerator()
            logger.info("✓ SadTalker initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SadTalker: {e}")
            sadtalker_generator = None
    
    logger.info("=== Service Ready ===")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    gpu_info = {}
    if DEVICE == "cuda":
        gpu_info = {
            "name": torch.cuda.get_device_name(0),
            "memory_allocated": f"{torch.cuda.memory_allocated(0) / 1024**3:.2f} GB",
            "memory_reserved": f"{torch.cuda.memory_reserved(0) / 1024**3:.2f} GB",
        }
    
    return {
        "status": "healthy",
        "model_loaded": sadtalker_generator is not None,
        "device": DEVICE,
        "gpu_info": gpu_info,
    }


@app.post("/generate", response_model=AvatarResponse)
async def generate_avatar(request: AvatarRequest, background_tasks: BackgroundTasks):
    """Generate avatar video using SadTalker with OpenAI TTS support"""
    
    if not AVATAR_IMAGE.exists():
        raise HTTPException(status_code=500, detail="luna_base.png not found")
    
    if not sadtalker_generator:
        raise HTTPException(status_code=503, detail="SadTalker not initialized")
    
    video_id = str(uuid.uuid4())
    audio_path = AUDIO_DIR / f"{video_id}.mp3"
    
    try:
        logger.info(f"📨 New request: {request.text[:50]}...")
        logger.info(f"   Quality: {request.quality}")
        logger.info(f"   Voice: {request.voice_id}")
        logger.info(f"   Audio URL: {request.audio_url}")
        
        # Step 1: Get audio (download OpenAI TTS if provided, otherwise generate)
        if request.audio_url:
            # Download high-quality OpenAI TTS audio from backend
            logger.info(f"📥 Downloading OpenAI TTS audio from: {request.audio_url}")
            import requests
            try:
                response = requests.get(request.audio_url, timeout=30)
                response.raise_for_status()
                audio_path.write_bytes(response.content)
                logger.info(f"✅ Downloaded OpenAI TTS audio: {audio_path}")
            except Exception as e:
                logger.warning(f"⚠️  Failed to download audio_url, falling back to local TTS: {e}")
                # Clear audio_url to trigger local TTS generation
                request.audio_url = None
        
        # Step 2: Generate video using SadTalker
        if request.audio_url and audio_path.exists():
            # Use downloaded OpenAI audio
            logger.info(f"🎬 Generating video with OpenAI TTS audio...")
            result = sadtalker_generator.generate(
                audio_path=str(audio_path),  # Use pre-generated audio
                text=request.text,  # Keep text as reference
                source_image=str(AVATAR_IMAGE),
                video_id=video_id,
                quality=request.quality,
                output_dir=str(OUTPUT_DIR),
                audio_dir=str(AUDIO_DIR),
                temp_dir=str(TEMP_DIR)
            )
        else:
            # Generate audio with local TTS (fallback)
            logger.info(f"🎤 Generating audio with local TTS (no OpenAI audio provided)")
            result = sadtalker_generator.generate(
                text=request.text,
                source_image=str(AVATAR_IMAGE),
                video_id=video_id,
                quality=request.quality,
                output_dir=str(OUTPUT_DIR),
                audio_dir=str(AUDIO_DIR),
                temp_dir=str(TEMP_DIR)
            )
        
        logger.info(f"✓ Video ready: {video_id}.mp4")
        
        # Schedule cleanup
        background_tasks.add_task(cleanup_old_files)
        
        return AvatarResponse(
            video_url=f"http://localhost:8000/videos/{video_id}.mp4",
            audio_url=f"http://localhost:8000/audio/{video_id}.mp3" if result.get('audio_path') else None,
            video_id=video_id,
            duration=result.get('duration', 5.0),
            status="generated"
        )
        
    except Exception as e:
        logger.error(f"Error generating avatar: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/last-video")
async def get_last_video():
    """Get the last generated video"""
    try:
        # Find the most recently modified video file
        mp4_files = list(OUTPUT_DIR.glob("*.mp4"))
        if not mp4_files:
            return {"exists": False, "error": "No videos found"}
        
        # Sort by modification time, get the latest
        latest_video = max(mp4_files, key=lambda p: p.stat().st_mtime)
        video_id = latest_video.stem  # filename without extension
        
        return {
            "exists": True,
            "video_id": video_id,
            "video_url": f"http://localhost:8000/videos/{video_id}.mp4",
            "filename": latest_video.name
        }
    except Exception as e:
        logger.error(f"Error getting last video: {e}")
        return {"exists": False, "error": str(e)}


@app.get("/videos/{filename}")
async def get_video(filename: str):
    """Serve generated video"""
    video_path = OUTPUT_DIR / filename
    
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")
    
    return FileResponse(
        video_path,
        media_type="video/mp4",
        headers={"Content-Disposition": f"inline; filename={filename}"}
    )


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


@app.delete("/videos/{video_id}")
async def delete_video(video_id: str):
    """Delete a video and its audio"""
    video_path = OUTPUT_DIR / f"{video_id}.mp4"
    audio_path = AUDIO_DIR / f"{video_id}.mp3"
    
    deleted = []
    if video_path.exists():
        video_path.unlink()
        deleted.append("video")
    if audio_path.exists():
        audio_path.unlink()
        deleted.append("audio")
    
    if deleted:
        return {"status": "deleted", "items": deleted, "video_id": video_id}
    
    raise HTTPException(status_code=404, detail="Video not found")


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

