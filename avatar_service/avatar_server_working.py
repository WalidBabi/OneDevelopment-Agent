"""
Luna Avatar GPU Service - LivePortrait Working Version
======================================================
"""

import os
import sys
import uuid
import logging
import subprocess
from pathlib import Path
from typing import Optional
import torch
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="Luna Avatar GPU Service", version="2.0.0")

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

AVATAR_IMAGE = Path("./luna_base.png").resolve()  # Convert to absolute path
TEMP_AUDIO_DIR = Path("./temp_audio")
TEMP_AUDIO_DIR.mkdir(exist_ok=True)

LIVEPORTRAIT_PATH = Path(r"C:\Users\Walid\Downloads\LivePortrait-main")
LIVEPORTRAIT_INFERENCE = LIVEPORTRAIT_PATH / "inference.py"

# Device
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
logger.info(f"Using device: {DEVICE}")

# Check if LivePortrait is available
liveportrait_available = LIVEPORTRAIT_INFERENCE.exists()


class AvatarRequest(BaseModel):
    text: str
    audio_url: Optional[str] = None
    voice_id: Optional[str] = "default"


class AvatarResponse(BaseModel):
    video_url: str
    video_id: str
    duration: float
    status: str


def cleanup_old_files():
    """Clean up old files"""
    import time
    current_time = time.time()
    for video_file in OUTPUT_DIR.glob("*.mp4"):
        if current_time - video_file.stat().st_mtime > 3600:
            video_file.unlink()
            logger.info(f"Cleaned up: {video_file.name}")


@app.on_event("startup")
async def startup():
    """Startup checks"""
    logger.info("Luna Avatar Service Starting...")
    logger.info(f"LivePortrait available: {liveportrait_available}")
    logger.info(f"Luna base image: {AVATAR_IMAGE.exists()}")
    logger.info(f"GPU available: {torch.cuda.is_available()}")


@app.get("/")
def root():
    return {
        "service": "Luna Avatar GPU Service",
        "status": "running",
        "device": DEVICE,
        "liveportrait_available": liveportrait_available,
        "gpu_available": torch.cuda.is_available(),
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
        "liveportrait_available": liveportrait_available,
        "device": DEVICE,
        "gpu_info": gpu_info,
    }


@app.post("/generate", response_model=AvatarResponse)
async def generate_avatar(request: AvatarRequest, background_tasks: BackgroundTasks):
    """Generate photorealistic talking avatar using LivePortrait"""
    
    if not AVATAR_IMAGE.exists():
        raise HTTPException(status_code=500, detail="luna_base.png not found")
    
    if not liveportrait_available:
        raise HTTPException(status_code=503, detail="LivePortrait not available")
    
    video_id = str(uuid.uuid4())
    output_path = OUTPUT_DIR / f"{video_id}.mp4"
    
    try:
        logger.info(f"Generating avatar for: {request.text[:50]}...")
        
        # Step 1: Generate audio from text
        from gtts import gTTS
        import tempfile
        
        audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3", dir=str(TEMP_AUDIO_DIR))
        tts = gTTS(text=request.text, lang='en', slow=False)
        tts.save(audio_file.name)
        logger.info(f"Audio generated: {audio_file.name}")
        
        # Step 2: Convert audio to video (LivePortrait needs video input, not just audio)
        # Create a simple video from audio with a static frame
        driving_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4", dir=str(TEMP_AUDIO_DIR))
        
        # Use FFmpeg to create a video from the audio with the avatar image
        # This creates a video where the image is displayed for the duration of the audio
        ffmpeg_cmd = [
            'ffmpeg',
            '-loop', '1',  # Loop the image
            '-i', str(AVATAR_IMAGE),  # Input image
            '-i', audio_file.name,  # Input audio
            '-c:v', 'libx264',  # Video codec
            '-tune', 'stillimage',  # Optimize for still image
            '-c:a', 'aac',  # Audio codec
            '-b:a', '192k',  # Audio bitrate
            '-pix_fmt', 'yuv420p',  # Pixel format for compatibility
            '-shortest',  # End when shortest input ends (audio)
            '-y',  # Overwrite output file
            driving_video.name
        ]
        
        logger.info("Converting audio to video...")
        ffmpeg_result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        
        if ffmpeg_result.returncode != 0:
            logger.error(f"FFmpeg error: {ffmpeg_result.stderr}")
            raise Exception(f"FFmpeg failed: {ffmpeg_result.stderr}")
        
        logger.info(f"Driving video created: {driving_video.name}")
        
        # Step 3: Run LivePortrait via subprocess
        logger.info("Running LivePortrait...")
        
        cmd = [
            sys.executable,  # Python executable
            str(LIVEPORTRAIT_INFERENCE),
            "-s", str(AVATAR_IMAGE),
            "-d", driving_video.name,  # Use video instead of audio
            "-o", str(output_path),
            "--flag-eye-retargeting", 
            "--flag-lip-retargeting",
            "--flag-stitching",
            "--flag-relative-motion",
            "--flag-pasteback",
            "--flag-do-crop",
        ]
        
        result = subprocess.run(
            cmd,
            cwd=str(LIVEPORTRAIT_PATH),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            logger.error(f"LivePortrait error: {result.stderr}")
            raise Exception(f"LivePortrait failed: {result.stderr}")
        
        logger.info("LivePortrait completed successfully")
        
        # Clean up temp files
        os.unlink(audio_file.name)
        os.unlink(driving_video.name)
        
        # Get video duration
        import cv2
        cap = cv2.VideoCapture(str(output_path))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        duration = frame_count / fps if fps > 0 else 5.0
        cap.release()
        
        logger.info(f"✓ Video generated: {video_id} ({duration:.2f}s)")
        
        background_tasks.add_task(cleanup_old_files)
        
        return AvatarResponse(
            video_url=f"http://localhost:8000/videos/{video_id}.mp4",
            video_id=video_id,
            duration=duration,
            status="generated"
        )
        
    except Exception as e:
        logger.error(f"Error generating avatar: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


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

