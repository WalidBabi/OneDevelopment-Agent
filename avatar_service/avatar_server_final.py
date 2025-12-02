"""
Luna Avatar GPU Service - FINAL VERSION with SadTalker
=======================================================
High-Quality Voice + Professional Talking Head Videos

Features:
- ✅ High-quality TTS (edge-tts with Microsoft Neural Voices)
- ✅ Professional talking head videos (SadTalker 512px)
- ✅ GPU-accelerated (RTX 4050)
- ✅ Multiple quality modes
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
# Try to import torch (optional - only for GPU detection)
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import our managers
from tts_manager import get_tts_manager

# Try to import video generators - prefer Wav2Lip (faster), fallback to SadTalker
try:
    from wav2lip_generator import Wav2LipGenerator
    WAV2LIP_AVAILABLE = True
except ImportError:
    WAV2LIP_AVAILABLE = False
    Wav2LipGenerator = None

try:
    from sadtalker_generator import SadTalkerGenerator
    SADTALKER_AVAILABLE = True
except ImportError:
    SADTALKER_AVAILABLE = False
    SadTalkerGenerator = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="Luna Avatar GPU Service - FINAL", version="4.0.0")

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

TEMP_DIR = Path("./temp_sadtalker")
TEMP_DIR.mkdir(exist_ok=True)

AVATAR_IMAGE = Path("./luna_base.png").resolve()

# Device
if TORCH_AVAILABLE:
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Using device: {DEVICE}")
else:
    DEVICE = "cpu"
    logger.info("PyTorch not available, using CPU")

# Initialize managers
tts_manager = get_tts_manager()
wav2lip_generator = None  # Lazy load - prefer this (faster)
sadtalker_generator = None  # Lazy load - fallback

# Configuration
# Default to 'fast' (256px, no enhancement) for ~10 second generation
# You can override with env var VIDEO_QUALITY=fast|standard|high|ultra
QUALITY_MODE = os.getenv('VIDEO_QUALITY', 'fast')  # fast, standard, high, ultra


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


def get_wav2lip():
    """Lazy load Wav2Lip generator (faster - 8-12 seconds)"""
    global wav2lip_generator
    if wav2lip_generator is None:
        if not WAV2LIP_AVAILABLE:
            logger.warning("Wav2Lip not available")
            wav2lip_generator = False
            return wav2lip_generator
        try:
            wav2lip_generator = Wav2LipGenerator()
            logger.info("✓ Wav2Lip loaded (fast mode: 8-12s)")
        except Exception as e:
            logger.warning(f"Wav2Lip not available: {e}")
            wav2lip_generator = False
    return wav2lip_generator

def get_sadtalker():
    """Lazy load SadTalker generator (fallback - slower but higher quality)"""
    global sadtalker_generator
    if sadtalker_generator is None:
        if not SADTALKER_AVAILABLE:
            logger.warning("SadTalker not available")
            sadtalker_generator = False
            return sadtalker_generator
        try:
            # Force NVIDIA GPU
            import os
            os.environ['CUDA_VISIBLE_DEVICES'] = '0'
            os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'
            
            sadtalker_generator = SadTalkerGenerator(quality=QUALITY_MODE)
            logger.info(f"✓ SadTalker loaded with '{QUALITY_MODE}' quality")
        except Exception as e:
            logger.error(f"Failed to load SadTalker: {e}")
            logger.exception(e)
            sadtalker_generator = False  # Mark as failed
    return sadtalker_generator


def cleanup_old_files():
    """Clean up old files"""
    import time
    current_time = time.time()
    
    for directory in [OUTPUT_DIR, AUDIO_DIR, TEMP_DIR]:
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
    logger.info("Luna Avatar Service - FINAL VERSION Starting...")
    logger.info("=" * 70)
    logger.info(f"Luna base image: {AVATAR_IMAGE.exists()}")
    if TORCH_AVAILABLE:
        logger.info(f"GPU available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
    else:
        logger.info("GPU detection: PyTorch not available")
    logger.info(f"TTS engines: {len(tts_manager.engines)}")
    logger.info(f"Video quality mode: {QUALITY_MODE}")
    logger.info("=" * 70)


@app.get("/")
def root():
    sadtalker = get_sadtalker()
    
    return {
        "service": "Luna Avatar GPU Service - FINAL",
        "version": "4.0.0",
        "status": "running",
        "device": DEVICE,
        "gpu_available": torch.cuda.is_available() if TORCH_AVAILABLE else False,
        "tts_engines": [engine[0] for engine in tts_manager.engines],
        "video_generation": "SadTalker" if sadtalker else "unavailable",
        "quality_mode": QUALITY_MODE,
        "features": {
            "high_quality_tts": True,
            "talking_head_video": bool(sadtalker),
            "multiple_voices": True,
            "quality_modes": ["fast", "standard", "high", "ultra"]
        }
    }


@app.get("/health")
def health_check():
    gpu_info = {}
    if TORCH_AVAILABLE and torch.cuda.is_available():
        gpu_info = {
            "name": torch.cuda.get_device_name(0),
            "memory_allocated": f"{torch.cuda.memory_allocated(0) / 1024**3:.2f} GB",
            "memory_reserved": f"{torch.cuda.memory_reserved(0) / 1024**3:.2f} GB",
        }
    
    sadtalker = get_sadtalker()
    
    return {
        "status": "healthy",
        "device": DEVICE,
        "gpu_info": gpu_info,
        "tts_available": len(tts_manager.engines) > 0,
        "tts_primary": tts_manager.engines[0][0] if tts_manager.engines else "none",
        "video_available": bool(sadtalker),
        "quality_mode": QUALITY_MODE
    }


@app.post("/generate", response_model=AvatarResponse)
async def generate_avatar(request: AvatarRequest, background_tasks: BackgroundTasks):
    """
    Generate high-quality talking avatar video
    
    Process:
    1. Generate high-quality audio with edge-tts
    2. Generate talking head video with SadTalker (512px + GFPGAN)
    3. Return video URL (or audio if video fails)
    """
    
    if not AVATAR_IMAGE.exists():
        raise HTTPException(status_code=500, detail="luna_base.png not found")
    
    video_id = str(uuid.uuid4())
    audio_path = AUDIO_DIR / f"{video_id}.mp3"
    temp_output = TEMP_DIR / video_id
    final_video_path = OUTPUT_DIR / f"{video_id}.mp4"
    
    # Force 'fast' mode for speed (10 seconds target)
    quality = 'fast'  # Always use fast mode for speed
    
    try:
        logger.info(f"📨 New request: {request.text[:50]}...")
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
        
        # Step 3: Generate video - Try Wav2Lip first (faster), fallback to SadTalker
        wav2lip = get_wav2lip()
        sadtalker = None
        
        # Prefer Wav2Lip for speed (8-12 seconds) - but check if model exists
        if wav2lip and wav2lip is not False:
            try:
                # Check if model file exists and is valid
                model_path = Path(wav2lip.checkpoint)
                if model_path.exists() and model_path.stat().st_size > 100 * 1024 * 1024:  # > 100MB
                    logger.info("⚡ Using Wav2Lip for fast generation (8-12s)...")
                    video_success, video_path, gen_time = wav2lip.generate_video(
                        audio_path=str(audio_path),
                        image_path=str(AVATAR_IMAGE),
                        output_path=str(final_video_path),
                        quality='fast'  # Fast mode for speed
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
                            quality="fast",
                            generation_time=gen_time,
                            message=f"Fast video generated with Wav2Lip ({gen_time:.1f}s)"
                        )
                    else:
                        logger.warning("Wav2Lip failed, trying SadTalker fallback...")
                else:
                    logger.info("Wav2Lip model not found, using SadTalker...")
            except Exception as e:
                logger.warning(f"Wav2Lip error: {e}, using SadTalker fallback...")
        
        # Fallback to SadTalker
        logger.info("Attempting to load SadTalker...")
        sadtalker = get_sadtalker()
        logger.info(f"SadTalker loaded: {sadtalker is not False and sadtalker is not None}")
        
        if sadtalker and sadtalker is not False:
            logger.info(f"🎬 Generating {quality} quality video...")
            
            # Update quality if specified in request
            if quality != sadtalker.quality:
                sadtalker = SadTalkerGenerator(quality=quality)
            
            video_success, video_path, gen_time = sadtalker.generate_video(
                audio_path=str(audio_path),
                image_path=str(AVATAR_IMAGE),
                output_dir=str(temp_output)
            )
            
            if video_success:
                # Always merge audio to ensure video has sound
                logger.info("Merging audio with video...")
                try:
                    import subprocess
                    ffmpeg_bin = r"C:\Users\Walid\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin"
                    ffmpeg_exe = Path(ffmpeg_bin) / "ffmpeg.exe"
                    
                    if ffmpeg_exe.exists():
                        temp_video = final_video_path.parent / f"temp_{final_video_path.name}"
                        
                        # Merge video and audio
                        merge_cmd = [
                            str(ffmpeg_exe),
                            "-i", str(video_path),  # Video from SadTalker
                            "-i", str(audio_path),  # Audio from TTS
                            "-c:v", "copy",         # Copy video codec (no re-encode)
                            "-c:a", "aac",          # Encode audio as AAC
                            "-b:a", "192k",         # Audio bitrate
                            "-map", "0:v:0",        # Use video from first input
                            "-map", "1:a:0",        # Use audio from second input
                            "-shortest",            # Match shortest stream duration
                            "-y",                   # Overwrite output
                            str(temp_video)
                        ]
                        
                        logger.info(f"Running FFmpeg: {' '.join(merge_cmd)}")
                        merge_result = subprocess.run(
                            merge_cmd,
                            capture_output=True,
                            text=True,
                            timeout=60
                        )
                        
                        if merge_result.returncode == 0 and temp_video.exists():
                            shutil.move(str(temp_video), str(final_video_path))
                            logger.info("✓ Audio merged successfully!")
                        else:
                            logger.error(f"Audio merge failed: {merge_result.stderr[:500]}")
                            # Fallback: use video without audio
                            logger.warning("Using video without audio as fallback")
                            shutil.move(video_path, final_video_path)
                    else:
                        logger.warning(f"FFmpeg not found at {ffmpeg_exe}, using video as-is")
                        shutil.move(video_path, final_video_path)
                except Exception as e:
                    logger.error(f"Audio merge error: {e}")
                    import traceback
                    logger.debug(traceback.format_exc())
                    # Fallback: use video without audio
                    logger.warning("Using video without audio as fallback")
                    shutil.move(video_path, final_video_path)
                
                logger.info(f"✓ Video ready: {final_video_path.name}")
                
                background_tasks.add_task(cleanup_old_files)
                
                return AvatarResponse(
                    video_url=f"http://localhost:8000/videos/{video_id}.mp4",
                    audio_url=f"http://localhost:8000/audio/{video_id}.mp3",
                    video_id=video_id,
                    duration=duration,
                    status="video_ready",
                    quality=quality,
                    generation_time=gen_time,
                    message=f"High-quality video generated ({quality} mode)"
                )
            else:
                logger.warning("Video generation failed, returning audio only")
        else:
            logger.warning("SadTalker not available")
        
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
    print("🚀 Starting Luna Avatar Service - FINAL VERSION")
    print("=" * 70)
    print()
    print("Features:")
    print("  ✅ High-quality TTS (Microsoft Neural Voices)")
    print("  ✅ Professional talking head videos (SadTalker)")
    print("  ✅ Multiple quality modes (fast/standard/high/ultra)")
    print("  ✅ GPU acceleration")
    print("  ✅ Automatic fallback")
    print()
    print(f"Quality mode: {QUALITY_MODE}")
    print(f"Set VIDEO_QUALITY env var to change (fast/standard/high/ultra)")
    print()
    print("=" * 70)
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
