"""
Luna Avatar GPU Service - LivePortrait Integration
===================================================
Photorealistic talking-head generation using LivePortrait
"""

import os
import sys
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

# Add LivePortrait to path
LIVEPORTRAIT_PATH = Path(r"C:\Users\Walid\Downloads\LivePortrait-main")
sys.path.insert(0, str(LIVEPORTRAIT_PATH / "src"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="Luna Avatar Service", version="2.0.0")

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
TEMP_AUDIO_DIR = Path("./temp_audio")
TEMP_AUDIO_DIR.mkdir(exist_ok=True)

# Device
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
logger.info(f"Using device: {DEVICE}")

# Global model
live_portrait_pipeline = None


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
async def load_model():
    """Load LivePortrait model"""
    global live_portrait_pipeline
    
    logger.info("Loading LivePortrait...")
    
    try:
        from live_portrait_pipeline import LivePortraitPipeline
        
        live_portrait_pipeline = LivePortraitPipeline(
            inference_cfg_path=str(LIVEPORTRAIT_PATH / "configs" / "inference.yaml"),
            crop_cfg_path=str(LIVEPORTRAIT_PATH / "configs" / "crop.yaml"),
            device=DEVICE
        )
        
        logger.info("✓ LivePortrait loaded successfully!")
        
    except Exception as e:
        logger.error(f"Failed to load LivePortrait: {e}")
        logger.info("Running in placeholder mode")
        live_portrait_pipeline = None


@app.get("/")
def root():
    return {
        "service": "Luna Avatar GPU Service",
        "status": "running",
        "device": DEVICE,
        "model_loaded": live_portrait_pipeline is not None,
        "model_type": "LivePortrait" if live_portrait_pipeline else "Placeholder",
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
        "model_loaded": live_portrait_pipeline is not None,
        "model_type": "LivePortrait" if live_portrait_pipeline else "Placeholder",
        "device": DEVICE,
        "gpu_info": gpu_info,
    }


@app.post("/generate", response_model=AvatarResponse)
async def generate_avatar(request: AvatarRequest, background_tasks: BackgroundTasks):
    """Generate photorealistic talking avatar"""
    
    if not AVATAR_IMAGE.exists():
        raise HTTPException(status_code=500, detail="luna_base.png not found")
    
    video_id = str(uuid.uuid4())
    output_path = OUTPUT_DIR / f"{video_id}.mp4"
    
    try:
        logger.info(f"Generating avatar for: {request.text[:50]}...")
        
        # Generate audio from text
        from gtts import gTTS
        import tempfile
        
        audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3", dir=str(TEMP_AUDIO_DIR))
        tts = gTTS(text=request.text, lang='en', slow=False)
        tts.save(audio_file.name)
        logger.info(f"Audio generated: {audio_file.name}")
        
        # If LivePortrait is loaded, use it
        if live_portrait_pipeline:
            logger.info("Generating with LivePortrait...")
            
            # Run LivePortrait
            live_portrait_pipeline.execute(
                source_image_path=str(AVATAR_IMAGE),
                driving_audio_path=audio_file.name,
                output_path=str(output_path),
                flag_lip_zero=False,
                flag_eye_retargeting=False,
                flag_lip_retargeting=True,
                flag_stitching=True,
                flag_relative=True,
                flag_pasteback=True,
                flag_do_crop=True,
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
        
        else:
            # Placeholder mode
            logger.warning("LivePortrait not loaded - placeholder mode")
            os.unlink(audio_file.name)
            
            import time
            time.sleep(1)
            
            return AvatarResponse(
                video_url=f"http://localhost:8000/videos/{video_id}.mp4",
                video_id=video_id,
                duration=5.0,
                status="placeholder"
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

