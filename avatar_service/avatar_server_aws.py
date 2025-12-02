"""
Luna Avatar GPU Service - AWS Optimized
========================================
Optimized for AWS g4dn/g5 instances with NVIDIA T4/A10G GPUs
Fast video generation using SadTalker + Edge-TTS
"""

import os
import uuid
import logging
import asyncio
import subprocess
from pathlib import Path
from typing import Optional
from datetime import datetime
import torch
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Luna Avatar Service (AWS GPU)",
    version="2.0.0",
    description="Fast avatar video generation using AWS GPU"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
WORK_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = WORK_DIR / "generated_videos"
TEMP_AUDIO_DIR = WORK_DIR / "temp_audio"
AVATAR_IMAGE = WORK_DIR / "luna_base.png"
SADTALKER_DIR = WORK_DIR / "SadTalker"

OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_AUDIO_DIR.mkdir(exist_ok=True)

# Check GPU
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
GPU_NAME = torch.cuda.get_device_name(0) if DEVICE == "cuda" else "CPU"
GPU_MEMORY = torch.cuda.get_device_properties(0).total_memory / 1e9 if DEVICE == "cuda" else 0

logger.info(f"🚀 Device: {DEVICE}")
logger.info(f"🎮 GPU: {GPU_NAME}")
logger.info(f"💾 VRAM: {GPU_MEMORY:.1f}GB")


class AvatarRequest(BaseModel):
    text: str
    audio_url: Optional[str] = None
    voice_id: Optional[str] = "default"
    quality: Optional[str] = "fast"  # fast, standard, high


class AvatarResponse(BaseModel):
    video_url: str
    video_id: str
    duration: float
    status: str
    generation_time: float


# Voice configurations for Edge-TTS
VOICE_MAP = {
    "default": "en-US-AriaNeural",
    "professional": "en-US-GuyNeural",
    "british": "en-GB-SoniaNeural",
    "casual": "en-US-JennyNeural",
    "friendly": "en-US-SaraNeural",
}


async def generate_audio_edge_tts(text: str, voice_id: str, output_path: Path) -> float:
    """Generate audio using Edge-TTS (Microsoft Neural Voices)"""
    import edge_tts
    
    voice = VOICE_MAP.get(voice_id, VOICE_MAP["default"])
    
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output_path))
    
    # Get duration
    import wave
    import contextlib
    
    # Convert to WAV for duration check
    wav_path = output_path.with_suffix('.wav')
    subprocess.run([
        'ffmpeg', '-y', '-i', str(output_path),
        '-ar', '16000', '-ac', '1',
        str(wav_path)
    ], capture_output=True)
    
    with contextlib.closing(wave.open(str(wav_path), 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
    
    return duration


def generate_video_sadtalker(
    audio_path: Path,
    image_path: Path,
    output_path: Path,
    quality: str = "fast"
) -> bool:
    """Generate video using SadTalker"""
    
    # Quality settings
    settings = {
        "fast": {"size": 256, "preprocess": "crop", "still": True},
        "standard": {"size": 256, "preprocess": "full", "still": False},
        "high": {"size": 512, "preprocess": "full", "still": False},
    }
    
    cfg = settings.get(quality, settings["fast"])
    
    # Build SadTalker command
    cmd = [
        "python", str(SADTALKER_DIR / "inference.py"),
        "--driven_audio", str(audio_path),
        "--source_image", str(image_path),
        "--result_dir", str(output_path.parent),
        "--size", str(cfg["size"]),
        "--preprocess", cfg["preprocess"],
        "--enhancer", "gfpgan",  # Face enhancement
    ]
    
    if cfg["still"]:
        cmd.append("--still")
    
    logger.info(f"Running SadTalker: {' '.join(cmd)}")
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(SADTALKER_DIR)
    )
    
    if result.returncode != 0:
        logger.error(f"SadTalker error: {result.stderr}")
        return False
    
    return True


@app.get("/")
def root():
    return {
        "service": "Luna Avatar GPU Service (AWS)",
        "version": "2.0.0",
        "device": DEVICE,
        "gpu": GPU_NAME,
        "vram_gb": round(GPU_MEMORY, 1)
    }


@app.get("/health")
def health_check():
    gpu_memory_used = 0
    gpu_memory_total = 0
    
    if DEVICE == "cuda":
        gpu_memory_used = torch.cuda.memory_allocated(0) / 1e9
        gpu_memory_total = torch.cuda.get_device_properties(0).total_memory / 1e9
    
    return {
        "status": "healthy",
        "device": DEVICE,
        "gpu": GPU_NAME,
        "gpu_memory": {
            "used_gb": round(gpu_memory_used, 2),
            "total_gb": round(gpu_memory_total, 2),
            "available_gb": round(gpu_memory_total - gpu_memory_used, 2)
        },
        "avatar_image": AVATAR_IMAGE.exists(),
        "sadtalker_ready": SADTALKER_DIR.exists(),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/generate", response_model=AvatarResponse)
async def generate_avatar(request: AvatarRequest, background_tasks: BackgroundTasks):
    """Generate talking avatar video"""
    
    start_time = datetime.now()
    video_id = str(uuid.uuid4())
    
    logger.info(f"📥 Generate request: {video_id}")
    logger.info(f"   Text: {request.text[:50]}...")
    logger.info(f"   Quality: {request.quality}")
    
    # Validate avatar image
    if not AVATAR_IMAGE.exists():
        raise HTTPException(status_code=500, detail="Avatar image not found")
    
    try:
        # Step 1: Generate audio
        logger.info("🎤 Generating audio...")
        audio_path = TEMP_AUDIO_DIR / f"{video_id}.mp3"
        
        if request.audio_url:
            # Download provided audio
            import requests
            response = requests.get(request.audio_url)
            audio_path.write_bytes(response.content)
            duration = 5.0  # Estimate
        else:
            # Generate with Edge-TTS
            duration = await generate_audio_edge_tts(
                request.text,
                request.voice_id,
                audio_path
            )
        
        logger.info(f"   Audio duration: {duration:.1f}s")
        
        # Step 2: Generate video
        logger.info("🎬 Generating video...")
        output_path = OUTPUT_DIR / f"{video_id}.mp4"
        
        success = generate_video_sadtalker(
            audio_path=audio_path,
            image_path=AVATAR_IMAGE,
            output_path=output_path,
            quality=request.quality
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Video generation failed")
        
        # Find the actual output file (SadTalker names it differently)
        actual_output = None
        for f in OUTPUT_DIR.glob(f"*{video_id}*.mp4"):
            actual_output = f
            break
        
        if not actual_output:
            # Try to find the latest mp4
            mp4_files = sorted(OUTPUT_DIR.glob("*.mp4"), key=os.path.getmtime)
            if mp4_files:
                actual_output = mp4_files[-1]
                actual_output.rename(output_path)
                actual_output = output_path
        
        if not actual_output or not actual_output.exists():
            raise HTTPException(status_code=500, detail="Output video not found")
        
        # Calculate generation time
        gen_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"✅ Video generated in {gen_time:.1f}s")
        
        # Schedule cleanup
        background_tasks.add_task(cleanup_old_files)
        
        # Return video URL
        video_url = f"/videos/{actual_output.name}"
        
        return AvatarResponse(
            video_url=video_url,
            video_id=video_id,
            duration=duration,
            status="generated",
            generation_time=round(gen_time, 1)
        )
        
    except Exception as e:
        logger.error(f"❌ Generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/videos/{filename}")
async def serve_video(filename: str):
    """Serve generated video files"""
    video_path = OUTPUT_DIR / filename
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")
    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=filename
    )


def cleanup_old_files():
    """Remove files older than 1 hour"""
    import time
    cutoff = time.time() - 3600  # 1 hour
    
    for folder in [OUTPUT_DIR, TEMP_AUDIO_DIR]:
        for f in folder.iterdir():
            if f.is_file() and f.stat().st_mtime < cutoff:
                try:
                    f.unlink()
                    logger.info(f"🗑️ Cleaned up: {f.name}")
                except:
                    pass


if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║          Luna Avatar Service - AWS GPU                    ║
    ║                                                           ║
    ║  GPU: {:<48} ║
    ║  VRAM: {:<47} ║
    ║                                                           ║
    ║  Endpoint: http://0.0.0.0:8001                           ║
    ║  Health:   http://0.0.0.0:8001/health                    ║
    ╚═══════════════════════════════════════════════════════════╝
    """.format(GPU_NAME[:48], f"{GPU_MEMORY:.1f}GB"))
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )

