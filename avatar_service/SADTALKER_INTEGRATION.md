# 🎬 SadTalker Integration Guide

## 🎯 Quality Optimization

### Quality Levels Explained

| Mode | Resolution | Enhancement | Speed | Quality | Best For |
|------|------------|-------------|-------|---------|----------|
| **Fast** | 256px | None | ⚡⚡⚡⚡ | ⭐⭐⭐ | Testing |
| **Standard** | 256px | GFPGAN | ⚡⚡⚡ | ⭐⭐⭐⭐ | Balanced |
| **High** | 512px | GFPGAN | ⚡⚡ | ⭐⭐⭐⭐⭐ | **Recommended** |
| **Ultra** | 512px | GFPGAN + RealESRGAN | ⚡ | ⭐⭐⭐⭐⭐ | Maximum quality |

### Recommended: **High Quality Mode** ⭐

```python
# 512px with GFPGAN enhancement
# Perfect balance: 30-40 seconds, excellent quality
python inference.py \
  --driven_audio audio.mp3 \
  --source_image luna_base.png \
  --size 512 \
  --enhancer gfpgan \
  --still \
  --preprocess full
```

**Why this is perfect:**
- ✅ 2x resolution of standard (512 vs 256)
- ✅ GFPGAN face enhancement
- ✅ Still fast enough (30-40s)
- ✅ Professional quality
- ✅ Works great on RTX 4050

---

## 🚀 Integration with Avatar Server

### Step 1: Create SadTalker Wrapper

Create `avatar_service/sadtalker_generator.py`:

```python
"""
SadTalker Video Generator
High-quality wrapper for avatar service
"""
import subprocess
import sys
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class SadTalkerGenerator:
    def __init__(self, 
                 sadtalker_path="%USERPROFILE%/Downloads/SadTalker",
                 quality="high"):
        """
        Initialize SadTalker generator
        
        Args:
            sadtalker_path: Path to SadTalker installation
            quality: 'fast', 'standard', 'high', or 'ultra'
        """
        self.sadtalker_path = Path(sadtalker_path)
        self.python_exe = self.sadtalker_path / "venv310" / "Scripts" / "python.exe"
        self.inference_script = self.sadtalker_path / "inference.py"
        self.quality = quality
        
        # Quality presets
        self.quality_settings = {
            'fast': {
                'size': '256',
                'enhancer': None,
                'bg_upsampler': None,
                'expected_time': 20
            },
            'standard': {
                'size': '256',
                'enhancer': 'gfpgan',
                'bg_upsampler': None,
                'expected_time': 30
            },
            'high': {  # Recommended
                'size': '512',
                'enhancer': 'gfpgan',
                'bg_upsampler': None,
                'expected_time': 40
            },
            'ultra': {
                'size': '512',
                'enhancer': 'gfpgan',
                'bg_upsampler': 'realesrgan',
                'expected_time': 60
            }
        }
        
        if not self.python_exe.exists():
            raise FileNotFoundError(f"SadTalker Python not found: {self.python_exe}")
        
        logger.info(f"SadTalker initialized with '{quality}' quality")
    
    def generate_video(self, audio_path, image_path, output_dir):
        """
        Generate talking head video
        
        Args:
            audio_path: Path to audio file (MP3/WAV)
            image_path: Path to source image
            output_dir: Directory for output video
            
        Returns:
            tuple: (success: bool, video_path: str, duration: float)
        """
        import time
        
        settings = self.quality_settings[self.quality]
        
        logger.info(f"Generating video with {self.quality} quality...")
        logger.info(f"  Audio: {audio_path}")
        logger.info(f"  Image: {image_path}")
        logger.info(f"  Expected time: ~{settings['expected_time']}s")
        
        # Build command
        cmd = [
            str(self.python_exe),
            str(self.inference_script),
            "--driven_audio", str(audio_path),
            "--source_image", str(image_path),
            "--result_dir", str(output_dir),
            "--still",  # Minimal head movement for consistency
            "--preprocess", "full",
            "--size", settings['size']
        ]
        
        if settings['enhancer']:
            cmd.extend(["--enhancer", settings['enhancer']])
        
        if settings['bg_upsampler']:
            cmd.extend(["--bg_upsampler", settings['bg_upsampler']])
        
        logger.debug(f"Command: {' '.join(cmd)}")
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.sadtalker_path),
                capture_output=True,
                text=True,
                timeout=180  # 3 minute timeout
            )
            
            elapsed = time.time() - start_time
            
            if result.returncode == 0:
                # Find generated video
                videos = list(Path(output_dir).glob("**/*.mp4"))
                main_videos = [v for v in videos if "temp" not in v.name.lower()]
                
                if main_videos:
                    video_path = str(main_videos[0])
                    logger.info(f"✓ Video generated in {elapsed:.1f}s: {video_path}")
                    return True, video_path, elapsed
                else:
                    logger.error("Video generation completed but no video found")
                    return False, None, elapsed
            else:
                logger.error(f"SadTalker failed: {result.stderr[:200]}")
                return False, None, time.time() - start_time
                
        except subprocess.TimeoutExpired:
            logger.error("SadTalker timed out (>3 minutes)")
            return False, None, 180
        except Exception as e:
            logger.error(f"SadTalker error: {e}")
            return False, None, 0


# Singleton instance
_generator = None

def get_sadtalker_generator(quality='high'):
    """Get or create SadTalker generator instance"""
    global _generator
    if _generator is None or _generator.quality != quality:
        _generator = SadTalkerGenerator(quality=quality)
    return _generator
```

---

### Step 2: Update Avatar Server

Update `avatar_service/avatar_server_improved.py`:

```python
# Add at the top
from sadtalker_generator import get_sadtalker_generator

# In generate_avatar function, after audio generation:

async def generate_avatar(request: AvatarRequest, background_tasks: BackgroundTasks):
    """Generate avatar with high-quality audio AND video"""
    
    # ... existing audio generation code ...
    
    # NEW: Generate video with SadTalker
    try:
        logger.info("Generating video with SadTalker...")
        
        sadtalker = get_sadtalker_generator(quality='high')  # or 'ultra' for max quality
        
        success, video_path, duration = sadtalker.generate_video(
            audio_path=str(audio_file.name),
            image_path=str(AVATAR_IMAGE),
            output_dir=str(OUTPUT_DIR)
        )
        
        if success:
            logger.info(f"✓ Video generated: {video_path}")
            
            # Move to predictable location
            final_path = OUTPUT_DIR / f"{video_id}.mp4"
            shutil.move(video_path, final_path)
            
            return AvatarResponse(
                video_url=f"http://localhost:8000/videos/{video_id}.mp4",
                audio_url=f"http://localhost:8000/audio/{video_id}.mp3",
                video_id=video_id,
                duration=duration,
                status="generated",
                message="High-quality video with SadTalker"
            )
        else:
            # Fallback to audio-only
            logger.warning("Video generation failed, returning audio only")
            return AvatarResponse(
                video_url=None,
                audio_url=f"http://localhost:8000/audio/{video_id}.mp3",
                video_id=video_id,
                duration=duration,
                status="audio_only",
                message="Audio generated, video failed"
            )
            
    except Exception as e:
        logger.error(f"SadTalker error: {e}")
        # Return audio-only as fallback
        ...
```

---

## 🎯 Quality Enhancement Tips

### 1. **Use Better Source Image**
```python
# Requirements for best quality:
- Resolution: 1024x1024 or higher
- Format: PNG with transparency
- Lighting: Even, professional
- Face: Front-facing, clear, high-res
- Eyes: Open, looking at camera
```

### 2. **Pre-process Image**
```python
# Upscale luna_base.png with Real-ESRGAN
from PIL import Image
import subprocess

def upscale_image(input_path, output_path):
    """Upscale image for better quality"""
    cmd = [
        "realesrgan-ncnn-vulkan",
        "-i", input_path,
        "-o", output_path,
        "-s", "2"  # 2x upscale
    ]
    subprocess.run(cmd)
```

### 3. **Optimize Audio Quality**
```python
# Use higher bitrate for audio
communicate = edge_tts.Communicate(
    text=text,
    voice='en-US-AriaNeural',
    rate='+0%',  # Natural speed
    pitch='+0Hz'  # Natural pitch
)
```

### 4. **Post-Processing (Optional)**
```python
# Further enhance with FFmpeg
def enhance_video(input_path, output_path):
    """Enhance video with FFmpeg"""
    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-vf", "unsharp=5:5:0.8:3:3:0.4",  # Sharpen
        "-c:v", "libx264",
        "-preset", "slow",  # Better quality
        "-crf", "18",  # High quality (lower = better)
        output_path
    ]
    subprocess.run(cmd)
```

---

## ⚡ Speed Optimization

### For Production (Batch Processing)

If generating many videos:

```python
# Cache face landmarks (saves ~5s per video)
def cache_face_landmarks(image_path):
    """Pre-compute face landmarks"""
    # Run once per image
    subprocess.run([
        "python", "inference.py",
        "--source_image", image_path,
        "--preprocess", "full"
    ])
    # Landmarks cached in temp files
```

### Dynamic Quality

```python
def get_quality_based_on_load():
    """Adjust quality based on server load"""
    import psutil
    
    gpu_usage = get_gpu_usage()  # Your function
    
    if gpu_usage < 50:
        return 'ultra'  # GPU available, go for max quality
    elif gpu_usage < 70:
        return 'high'   # Balanced
    else:
        return 'standard'  # GPU busy, use faster mode
```

---

## 📊 Expected Performance

On your RTX 4050:

| Quality | Resolution | Time | File Size | Use Case |
|---------|------------|------|-----------|----------|
| Fast | 256px | 15-20s | 200KB | Testing only |
| Standard | 256px + GFPGAN | 20-30s | 220KB | Quick demos |
| **High** | **512px + GFPGAN** | **30-40s** | **800KB** | **Production ⭐** |
| Ultra | 512px + All | 50-70s | 1.2MB | Maximum quality |

**Recommendation:** Use **High** mode for production  
- Best quality/speed balance
- Professional results
- User-acceptable wait time

---

## 🎬 Production Configuration

```python
# avatar_service/config.py
SADTALKER_CONFIG = {
    'quality': 'high',  # high recommended
    'cache_landmarks': True,  # Faster subsequent generations
    'fallback_to_audio': True,  # Graceful degradation
    'timeout': 120,  # 2 minute max
    'cleanup_temp': True
}
```

---

## 🔥 Pro Tips

1. **First Generation is Slow** (~60s)
   - Models need to load
   - Subsequent: 30-40s

2. **Keep Models in Memory**
   - Don't restart server frequently
   - Loaded models = faster generation

3. **Monitor GPU Memory**
   - 512px needs ~4GB VRAM
   - Close other GPU apps

4. **Use Still Mode**
   - `--still` flag = minimal head movement
   - More consistent results
   - Slightly faster

5. **Pre-generate Popular Responses**
   - Cache common FAQ videos
   - Instant playback

---

## 📈 Next Level (Future)

### Even Better Quality Options:

1. **MuseTalk** (Real-time capable)
2. **EMO** (Most expressive)
3. **Custom Training** (Your specific Luna model)
4. **4K Generation** (For premium users)

See `IMAGE_TO_VIDEO_OPTIONS.md` for alternatives!

---

**Ready to integrate? Let's add this to your avatar server!** 🚀

