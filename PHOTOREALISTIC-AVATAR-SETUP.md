# Photorealistic Luna Avatar Setup Guide

## Overview

You now have a complete pipeline to use your **RTX 4050 laptop as a GPU service** for generating photorealistic talking-head videos of Luna, integrated with your AWS-hosted Luna backend.

## Architecture

```
Browser (User)
    ↓
AWS t3.medium (Luna Backend)
    ↓ HTTP Request
ngrok/Cloudflare Tunnel
    ↓
Your Laptop (RTX 4050)
    ↓ GPU Processing
Avatar Service (FastAPI + LivePortrait/SadTalker)
    ↓ Video URL
Back to Browser → Video plays in avatar circle
```

## Step-by-Step Setup

### Part 1: Setup Avatar Service on Your Laptop (Windows)

#### 1. Install Prerequisites

```powershell
# Install Python 3.10+ from python.org
# Install CUDA Toolkit 11.8 or 12.1 from NVIDIA
# Install Git
```

#### 2. Setup Avatar Service

```powershell
# Navigate to the project
cd C:\path\to\OneDevelopment-Agent\avatar_service

# Create virtual environment
python -m venv venv

# Activate
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install PyTorch with CUDA (visit pytorch.org for your CUDA version)
# Example for CUDA 11.8:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### 3. Choose and Install Avatar Model

**Option A: LivePortrait (Recommended - Best Quality)**

```powershell
cd ..
git clone https://github.com/KwaiVGI/LivePortrait.git
cd LivePortrait
pip install -r requirements.txt
# Follow their README to download model weights
```

**Option B: SadTalker (Good Alternative)**

```powershell
cd ..
git clone https://github.com/OpenTalker/SadTalker.git
cd SadTalker
pip install -r requirements.txt
# Download checkpoints as per their instructions
```

#### 4. Prepare Luna's Base Image

- Get or create a **photorealistic female portrait** (512x512 or 1024x1024 PNG)
- Front-facing, well-lit, neutral expression
- Save it as: `avatar_service/luna_base.png`

#### 5. Test the Service Locally

```powershell
cd avatar_service
python avatar_server.py
```

Visit `http://localhost:8000/health` - should show GPU info.

### Part 2: Expose Your Laptop via Tunnel

#### Option A: Using ngrok (Easiest)

```powershell
# Install ngrok from ngrok.com
# Sign up and get auth token

ngrok config add-authtoken YOUR_TOKEN
ngrok http 8000
```

Copy the HTTPS URL (e.g., `https://abcd-1234.ngrok-free.app`)

#### Option B: Using Cloudflare Tunnel

```powershell
# Install cloudflared
cloudflared tunnel --url http://localhost:8000
```

Copy the tunnel URL.

### Part 3: Configure AWS Backend

#### 1. SSH into your AWS instance

```bash
ssh -i your-key.pem ec2-user@your-aws-ip
```

#### 2. Set environment variable

```bash
cd /home/ec2-user/OneDevelopment-Agent/backend

# Edit .env or set environment variable
echo "AVATAR_SERVICE_URL=https://abcd-1234.ngrok-free.app" >> .env

# Or export temporarily
export AVATAR_SERVICE_URL=https://abcd-1234.ngrok-free.app
```

#### 3. Restart backend

```bash
# If using Docker
docker-compose restart backend

# Or if running directly
python manage.py runserver
```

### Part 4: Test End-to-End

#### 1. Check Avatar Service Health

```bash
curl http://localhost:8000/api/avatar/health/
```

Should return:
```json
{
  "status": "healthy",
  "service_info": {...},
  "url": "https://..."
}
```

#### 2. Test from Browser

1. Open Luna in your browser
2. Click the gear icon (⚙️) in top-right
3. Select **"Avatar Only"** mode
4. Click on Luna's avatar to speak
5. Say something like "Tell me about One Development"
6. Luna should respond with a **photorealistic video** (if service is working) or fallback to TTS

## How It Works

### When Avatar Service is Available:

1. User asks a question
2. Luna backend generates text response
3. Backend calls your laptop: `POST /generate` with text
4. Your laptop's GPU generates talking-head video (~2-5 seconds)
5. Returns video URL
6. Frontend plays video in the avatar circle
7. TTS also plays for audio (until you add audio to the video)

### When Avatar Service is Unavailable:

- Automatically falls back to the existing TTS + lip-sync simulation
- User experience is still good, just not photorealistic

## Integrating the Actual Model

Currently, the avatar server is a **stub**. To integrate a real model:

### For LivePortrait:

Edit `avatar_service/avatar_server.py`:

```python
# In load_model():
from liveportrait import LivePortrait
avatar_model = LivePortrait(device=DEVICE)
avatar_model.load_checkpoint("path/to/checkpoint")

# In generate_avatar():
audio_path = generate_or_download_audio(request.text)
video_path = avatar_model.generate(
    source_image=str(AVATAR_IMAGE),
    driving_audio=str(audio_path),
    output_path=str(output_path)
)
```

### For SadTalker:

```python
# Similar pattern - follow SadTalker's API
from sadtalker import SadTalker
avatar_model = SadTalker(device=DEVICE)
# ... generate video
```

## Troubleshooting

### GPU Not Detected

```powershell
python -c "import torch; print(torch.cuda.is_available())"
```

Should print `True`. If not:
- Reinstall PyTorch with correct CUDA version
- Update NVIDIA drivers
- Check CUDA installation

### Tunnel Connection Failed

- Make sure ngrok/cloudflared is running
- Check firewall settings
- Verify the URL is accessible from AWS: `curl https://your-tunnel-url/health`

### Video Generation Too Slow

- Check GPU utilization: `nvidia-smi`
- Reduce image resolution
- Use a lighter model
- Consider cloud GPU for production

### Video Won't Play in Browser

- Check video codec (H.264 is most compatible)
- Ensure CORS headers are set (already done in the code)
- Check browser console for errors

## Production Considerations

This setup is **for prototyping only**. For production:

### 1. Move to Cloud GPU

- **AWS**: g4dn.xlarge, g5.xlarge
- **Google Cloud**: n1-standard-4 with T4 GPU
- **Azure**: NC-series VMs

### 2. Add Proper Authentication

```python
# In avatar_server.py
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/generate")
async def generate_avatar(request: AvatarRequest, credentials: HTTPBearer = Depends(security)):
    # Verify token
    pass
```

### 3. Implement Video Caching

- Cache frequently requested responses
- Store videos in S3/CloudFront
- Add Redis for quick lookups

### 4. Add Queue System

```python
# Use Celery or RQ for async processing
from celery import Celery

@celery.task
def generate_avatar_async(text):
    # Generate video in background
    pass
```

### 5. Monitoring & Logging

- Add Prometheus metrics
- Set up error tracking (Sentry)
- Monitor GPU usage and costs

## Cost Estimates

### Current Setup (Laptop):
- **Cost**: $0 (using your hardware)
- **Limitation**: Must be online, single user

### Cloud GPU (Production):
- **AWS g4dn.xlarge**: ~$0.50/hour = ~$360/month
- **Google Cloud T4**: ~$0.35/hour = ~$250/month
- **On-demand**: Pay only when generating videos

## Next Steps

1. ✅ Avatar service created
2. ✅ Backend integration complete
3. ✅ Frontend video display ready
4. ⏳ **Install actual model** (LivePortrait/SadTalker)
5. ⏳ **Test with real photorealistic image**
6. ⏳ **Optimize generation speed**
7. ⏳ **Add audio to generated videos** (currently using separate TTS)
8. ⏳ **Deploy to cloud GPU** (when ready for production)

## Quick Reference Commands

### Start Avatar Service (Laptop)
```powershell
cd avatar_service
venv\Scripts\activate
python avatar_server.py
```

### Start Tunnel
```powershell
ngrok http 8000
```

### Check Status
```bash
# From AWS
curl http://localhost:8000/api/avatar/health/
```

### Update Tunnel URL
```bash
# On AWS
export AVATAR_SERVICE_URL=https://new-url.ngrok-free.app
docker-compose restart backend
```

## Support & Resources

- **LivePortrait**: https://github.com/KwaiVGI/LivePortrait
- **SadTalker**: https://github.com/OpenTalker/SadTalker
- **Wav2Lip**: https://github.com/Rudrabha/Wav2Lip
- **ngrok Docs**: https://ngrok.com/docs
- **CUDA Setup**: https://docs.nvidia.com/cuda/

---

**You're all set!** The infrastructure is ready. Now you just need to:
1. Install the actual model (LivePortrait recommended)
2. Add your photorealistic Luna image
3. Start the services and test

The system will automatically use the GPU service when available and gracefully fall back to TTS when it's not.



