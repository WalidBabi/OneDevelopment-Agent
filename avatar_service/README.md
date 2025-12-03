# Luna Avatar GPU Service

Photorealistic talking-head generation service running on your RTX 4050 laptop.

## Overview

This service generates realistic talking avatar videos by:
1. Taking text or audio input
2. Animating a base photorealistic Luna portrait
3. Returning a video URL that can be played in the browser

## Setup on Your Laptop (Windows with RTX 4050)

### 1. Install Prerequisites

```bash
# Install Python 3.10+ from python.org
# Install CUDA Toolkit 11.8 or 12.1 from NVIDIA website
# Install Git
```

### 2. Clone and Setup

```bash
cd /path/to/OneDevelopment-Agent/avatar_service

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Install PyTorch with CUDA

Visit https://pytorch.org/get-started/locally/ and get the command for your CUDA version.

Example for CUDA 11.8:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 4. Choose and Install Avatar Model

Pick ONE of these (LivePortrait recommended for quality):

#### Option A: LivePortrait (Recommended)
```bash
git clone https://github.com/KwaiVGI/LivePortrait.git
cd LivePortrait
pip install -r requirements.txt
# Download model weights (follow their README)
```

#### Option B: SadTalker
```bash
git clone https://github.com/OpenTalker/SadTalker.git
cd SadTalker
pip install -r requirements.txt
# Download checkpoints
```

#### Option C: Wav2Lip
```bash
git clone https://github.com/Rudrabha/Wav2Lip.git
cd Wav2Lip
pip install -r requirements.txt
# Download pretrained models
```

### 5. Prepare Luna Base Image

Place your photorealistic Luna portrait at:
```
avatar_service/luna_base.png
```

Requirements:
- Square image (512x512 or 1024x1024)
- Front-facing portrait
- Good lighting
- PNG format

### 6. Run the Server

```bash
# Make sure you're in the venv
python avatar_server.py
```

Server will start on `http://localhost:8000`

### 7. Expose via Tunnel

#### Using ngrok:
```bash
# Install ngrok from ngrok.com
ngrok config add-authtoken YOUR_TOKEN
ngrok http 8000
```

Copy the HTTPS URL (e.g., `https://abcd-1234.ngrok-free.app`)

#### Using Cloudflare Tunnel:
```bash
# Install cloudflared
cloudflared tunnel --url http://localhost:8000
```

### 8. Configure AWS Backend

On your AWS instance, set the environment variable:

```bash
# In your backend .env file
AVATAR_SERVICE_URL=https://abcd-1234.ngrok-free.app
```

## API Endpoints

### POST /generate
Generate a talking avatar video.

**Request:**
```json
{
  "text": "Hello, I'm Luna, your AI assistant for One Development.",
  "voice_id": "default",
  "audio_url": null
}
```

**Response:**
```json
{
  "video_url": "http://localhost:8000/videos/uuid.mp4",
  "video_id": "uuid",
  "duration": 5.2,
  "status": "generated"
}
```

### GET /videos/{video_id}
Download/stream the generated video.

### GET /health
Check service health and GPU status.

## Integration Steps

### Step 1: Update Backend API

Add to your Luna backend (Node.js):

```javascript
// backend/routes/avatar.js
const axios = require('axios');

router.post('/generate-avatar', async (req, res) => {
  const { text } = req.body;
  
  try {
    const response = await axios.post(
      `${process.env.AVATAR_SERVICE_URL}/generate`,
      { text },
      { timeout: 30000 }
    );
    
    res.json(response.data);
  } catch (error) {
    console.error('Avatar generation failed:', error);
    res.status(500).json({ error: 'Avatar generation failed' });
  }
});
```

### Step 2: Update Frontend

The frontend changes are already prepared in `LunaAvatarInterface.js`.

## Troubleshooting

### GPU Not Detected
```bash
python -c "import torch; print(torch.cuda.is_available())"
```
Should print `True`. If not, reinstall PyTorch with CUDA.

### Out of Memory
Reduce batch size or image resolution in the model config.

### Slow Generation
- Check GPU utilization: `nvidia-smi`
- Ensure CUDA is being used (check logs)
- Consider using a lighter model

### Tunnel Connection Issues
- Make sure ngrok/cloudflared is running
- Check firewall settings
- Verify the tunnel URL is accessible from AWS

## Performance Notes

With RTX 4050:
- Expected generation time: 2-5 seconds per video
- Video length: 3-10 seconds typical
- Memory usage: 4-6 GB VRAM

## Production Considerations

This setup is for **prototyping only**. For production:

1. **Move to cloud GPU**: AWS g4dn.xlarge, g5.xlarge, or similar
2. **Add authentication**: Secure the API with tokens
3. **Implement caching**: Cache frequently used responses
4. **Add queue system**: Use Celery/RQ for async processing
5. **CDN for videos**: Upload generated videos to S3/CloudFront
6. **Monitoring**: Add logging, metrics, error tracking

## Next Steps

1. Run the server and verify GPU is working
2. Test with curl: `curl http://localhost:8000/health`
3. Start ngrok tunnel
4. Update AWS backend with tunnel URL
5. Test end-to-end from Luna web interface
6. Integrate actual avatar model (LivePortrait/SadTalker)
7. Replace placeholder video generation with real implementation

## Model Integration Guide

Once you've chosen a model, update `avatar_server.py`:

1. Import the model library
2. Load model in `load_model()` function
3. Implement video generation in `generate_avatar()` function
4. Test with sample inputs

See inline TODOs in `avatar_server.py` for exact locations.







