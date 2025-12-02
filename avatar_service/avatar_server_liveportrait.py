"""
Luna Avatar GPU Service - WITH LIVEPORTRAIT INTEGRATION
========================================================
Photorealistic talking-head generation using LivePortrait.
"""

import os
import uuid
import logging
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
app = FastAPI(title="Luna Avatar Service", version="1.0.0")

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

AVATAR_IMAGE = Path("./luna_base.png")
LIVEPORTRAIT_PATH = Path("../LivePortrait")  # Adjust this path

# Device
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
logger.info(f"Using device: {DEVICE}")

# Global model
avatar_model = None


class AvatarRequest(BaseModel):
    text: str
    audio_url: Optional[str] = None
    voice_id: Optional[str] = "default"
    duration: Optional[float] = None


class AvatarResponse(BaseModel):
    video_url: str
    video_id: str
    duration: float
    status: str


def cleanup_old_files():
    """Clean up videos older than 1 hour"""
    import time
    current_time = time.time()
    for video_file in OUTPUT_DIR.glob("*.mp4"):
        if current_time - video_file.stat().st_mtime > 3600:
            video_file.unlink()
            logger.info(f"Cleaned up old video: {video_file.name}")


@app.on_event("startup")
async def load_model():
    """Load LivePortrait model"""
    global avatar_model
    
    logger.info("Loading LivePortrait model...")
    
    try:
        # Add LivePortrait to path
        import sys
        sys.path.insert(0, str(LIVEPORTRAIT_PATH / "src"))
        
        # Import LivePortrait
        from live_portrait_wrapper import LivePortraitWrapper
        
        # Initialize model
        avatar_model = LivePortraitWrapper(
            cfg_path=str(LIVEPORTRAIT_PATH / "configs" / "inference.yaml"),
            device=DEVICE
        )
        
        logger.info("✓ LivePortrait model loaded successfully")
        
    except Exception as e:
        logger.error(f"Failed to load LivePortrait: {e}")
        logger.info("Falling back to placeholder mode")
        avatar_model = {"status": "placeholder", "device": DEVICE}


@app.get("/")
def root():
    return {
        "service": "Luna Avatar GPU Service",
        "status": "running",
        "device": DEVICE,
        "model_loaded": avatar_model is not None,
        "model_type": "LivePortrait" if isinstance(avatar_model, dict) == False else "Placeholder",
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
        "model_loaded": avatar_model is not None,
        "model_type": "LivePortrait" if not isinstance(avatar_model, dict) else "Placeholder",
        "device": DEVICE,
        "gpu_info": gpu_info,
    }


@app.post("/generate", response_model=AvatarResponse)
async def generate_avatar(request: AvatarRequest, background_tasks: BackgroundTasks):
    """Generate photorealistic talking avatar"""
    
    if not avatar_model:
        raise HTTPException(status_code=503, detail="Avatar model not loaded")
    
    if not AVATAR_IMAGE.exists():
        raise HTTPException(status_code=500, detail="Luna base image not found. Please add luna_base.png")
    
    video_id = str(uuid.uuid4())
    output_path = OUTPUT_DIR / f"{video_id}.mp4"
    
    try:
        logger.info(f"Generating avatar for: {request.text[:50]}...")
        
        # If using placeholder (LivePortrait not loaded)
        if isinstance(avatar_model, dict):
            logger.warning("Using placeholder mode - LivePortrait not loaded")
            import time
            time.sleep(1)
            duration = 5.0
            
            background_tasks.add_task(cleanup_old_files)
            
            return AvatarResponse(
                video_url=f"http://localhost:8000/videos/{video_id}.mp4",
                video_id=video_id,
                duration=duration,
                status="placeholder"
            )
        
        # REAL LIVEPORTRAIT GENERATION
        logger.info("Generating with LivePortrait...")
        
        # Step 1: Generate audio from text (you can use TTS here)
        # For now, we'll use a simple approach
        from gtts import gTTS
        import tempfile
        
        audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts = gTTS(text=request.text, lang='en', slow=False)
        tts.save(audio_file.name)
        logger.info(f"Audio generated: {audio_file.name}")
        
        # Step 2: Generate video with LivePortrait
        result = avatar_model.run(
            source_image_path=str(AVATAR_IMAGE),
            driving_audio_path=audio_file.name,
            output_path=str(output_path)
        )
        
        # Clean up temp audio
        os.unlink(audio_file.name)
        
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

