"""
Luna Avatar GPU Service - PRODUCTION VERSION with Wav2Lip
==========================================================
Ultra-Fast High-Quality Talking Head Videos (15-20 seconds)

Features:
- ✅ High-quality TTS (edge-tts with Microsoft Neural Voices)
- ✅ Ultra-fast talking head videos (Wav2Lip - 15-20s)
- ✅ GPU-accelerated (NVIDIA RTX 4050)
- ✅ Multiple quality modes (fast/standard)
- ✅ Automatic fallback to audio-only if video fails
"""

import os
import sys
import uuid
import logging
import asyncio
import shutil
from pathlib import Path
from typing import Optional
import torch
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Force NVIDIA GPU before any heavy imports
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'

# Import our managers
from tts_manager import get_tts_manager
from wav2lip_generator import get_wav2lip_generator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="Luna Avatar GPU Service - Wav2Lip", version="5.0.0")

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

# Initialize managers
tts_manager = get_tts_manager()
video_generator = None  # Lazy load

# Configuration
VIDEO_QUALITY = os.getenv('VIDEO_QUALITY', 'high')  # 'fast' or 'high'


class AvatarRequest(BaseModel):
    text: str
    audio_url: Optional[str] = None
    voice_id: Optional[str] = "default"
    quality: Optional[str] = None  # Override default quality


class AvatarResponse(BaseModel):
    video_url: Optional[str]
    audio_url: str
    video_id: str
    duration: float
    status: str  # 'video_ready', 'audio_only', 'generating'
    quality: str
    generation_time: Optional[float] = None
    message: Optional[str] = None


def get_video_generator():
    """Lazy load Wav2Lip generator"""
    global video_generator
    if video_generator is None:
        try:
            video_generator = get_wav2lip_generator()
            logger.info(f"✓ Wav2Lip loaded (15-20s per video)")
        except Exception as e:
            logger.error(f"Failed to load Wav2Lip: {e}")
            video_generator = False  # Mark as failed
    return video_generator


def cleanup_old_files():
    """Clean up files older than 1 hour"""
    import time
    current_time = time.time()
    
    for directory in [OUTPUT_DIR, AUDIO_DIR]:
        for file in directory.glob("*.*"):
            try:
                if current_time - file.stat().st_mtime > 3600:  # 1 hour
                    file.unlink()
                    logger.debug(f"Cleaned up: {file.name}")
            except:
                pass


@app.on_event("startup")
async def startup():
    """Startup checks"""
    logger.info("=" * 70)
    logger.info("Luna Avatar Service - WAV2LIP VERSION Starting...")
    logger.info("=" * 70)
    logger.info(f"Luna base image: {AVATAR_IMAGE.exists()}")
    logger.info(f"GPU available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        logger.info(f"GPU: {gpu_name}")
        
        # Warn if not using NVIDIA
        if "NVIDIA" not in gpu_name:
            logger.warning(f"⚠️  WARNING: Not using NVIDIA GPU!")
            logger.warning(f"   Currently using: {gpu_name}")
            logger.warning(f"   Set Windows Graphics Settings to High Performance")
        else:
            logger.info(f"✅ Using NVIDIA GPU (optimal)")
    
    logger.info(f"TTS engines: {len(tts_manager.engines)}")
    logger.info(f"Video generator: Wav2Lip (ultra-fast)")
    logger.info(f"Video quality mode: {VIDEO_QUALITY}")
    logger.info("=" * 70)


@app.get("/")
def root():
    generator = get_video_generator()
    
    gpu_info = "N/A"
    if torch.cuda.is_available():
        gpu_info = torch.cuda.get_device_name(0)
    
    return {
        "service": "Luna Avatar GPU Service - Wav2Lip",
        "version": "5.0.0",
        "status": "running",
        "device": DEVICE,
        "gpu": gpu_info,
        "gpu_available": torch.cuda.is_available(),
        "tts_engines": [engine[0] for engine in tts_manager.engines],
        "video_generation": "Wav2Lip" if generator else "unavailable",
        "video_speed": "15-20 seconds",
        "quality_mode": VIDEO_QUALITY,
        "features": {
            "high_quality_tts": True,
            "ultra_fast_video": True,
            "multiple_voices": True,
            "quality_modes": ["fast", "high"]
        }
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
    
    generator = get_video_generator()
    
    return {
        "status": "healthy",
        "device": DEVICE,
        "gpu_info": gpu_info,
        "tts_available": len(tts_manager.engines) > 0,
        "tts_primary": tts_manager.engines[0][0] if tts_manager.engines else "none",
        "video_available": bool(generator),
        "video_generator": "Wav2Lip",
        "expected_speed": "15-20 seconds",
        "quality_mode": VIDEO_QUALITY
    }


@app.post("/generate", response_model=AvatarResponse)
async def generate_avatar(request: AvatarRequest, background_tasks: BackgroundTasks):
    """
    Generate high-quality talking avatar video with Wav2Lip
    
    Process:
    1. Generate high-quality audio with edge-tts (2-3s)
    2. Generate ultra-fast talking head video with Wav2Lip (15-20s)
    3. Return video URL
    
    Total time: 17-23 seconds
    """
    
    if not AVATAR_IMAGE.exists():
        raise HTTPException(status_code=500, detail="luna_base.png not found")
    
    video_id = str(uuid.uuid4())
    audio_path = AUDIO_DIR / f"{video_id}.mp3"
    final_video_path = OUTPUT_DIR / f"{video_id}.mp4"
    
    quality = request.quality or VIDEO_QUALITY
    
    try:
        logger.info(f"📨 New request: {request.text[:100]}...")
        logger.info(f"   Quality: {quality}")
        logger.info(f"   Voice: {request.voice_id}")
        
        # Step 1: Generate high-quality audio
        logger.info("🎤 Generating audio...")
        success = await tts_manager.generate_speech(
            text=request.text,
            output_path=str(audio_path),
            voice=request.voice_id
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="TTS generation failed")
        
        logger.info(f"✓ Audio generated: {audio_path.name}")
        
        # Step 2: Estimate duration
        try:
            from mutagen.mp3 import MP3
            audio = MP3(str(audio_path))
            duration = audio.info.length
        except:
            words = len(request.text.split())
            duration = (words / 150) * 60
        
        logger.info(f"✓ Audio duration: {duration:.2f}s")
        
        # Step 3: Generate video with Wav2Lip (15-20s!)
        generator = get_video_generator()
        
        if generator and generator is not False:
            logger.info(f"⚡ Generating video with Wav2Lip ({quality})...")
            logger.info(f"   Expected time: 15-20 seconds")
            
            video_success, video_path, gen_time = generator.generate_video(
                audio_path=str(audio_path),
                image_path=str(AVATAR_IMAGE),
                output_path=str(final_video_path),
                quality=quality
            )
            
            if video_success:
                logger.info(f"✓ Video ready: {final_video_path.name} ({gen_time:.1f}s)")
                
                background_tasks.add_task(cleanup_old_files)
                
                return AvatarResponse(
                    video_url=f"http://localhost:8000/videos/{video_id}.mp4",
                    audio_url=f"http://localhost:8000/audio/{video_id}.mp3",
                    video_id=video_id,
                    duration=duration,
                    status="video_ready",
                    quality=quality,
                    generation_time=gen_time,
                    message=f"Ultra-fast video generated in {gen_time:.1f}s ({quality} mode)"
                )
            else:
                logger.warning("Video generation failed, returning audio only")
        else:
            logger.warning("Wav2Lip not available")
        
        # Fallback: Return audio only
        background_tasks.add_task(cleanup_old_files)
        
        return AvatarResponse(
            video_url=None,
            audio_url=f"http://localhost:8000/audio/{video_id}.mp3",
            video_id=video_id,
            duration=duration,
            status="audio_only",
            quality="audio_only",
            message="High-quality audio generated (video unavailable)"
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
        return {"status": "deleted", "video_id": video_id, "deleted": deleted}
    
    raise HTTPException(status_code=404, detail="Video not found")


if __name__ == "__main__":
    print("=" * 70)
    print("🚀 Starting Luna Avatar Service - WAV2LIP VERSION")
    print("=" * 70)
    print()
    print("Features:")
    print("  ✅ High-quality TTS (Microsoft Neural Voices)")
    print("  ✅ Ultra-fast talking head videos (Wav2Lip)")
    print("  ✅ 15-20 second generation time")
    print("  ✅ GPU acceleration")
    print("  ✅ Automatic fallback")
    print()
    print(f"Quality mode: {VIDEO_QUALITY}")
    print(f"Set VIDEO_QUALITY env var to change (fast/high)")
    print()
    print("=" * 70)
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

