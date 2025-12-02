# Quick Start: Photorealistic Luna Avatar

## What's Been Set Up

Your Luna now has a complete pipeline for **NVIDIA-powered photorealistic talking avatars**:

- ✅ **Avatar GPU Service** (Python/FastAPI) - runs on your RTX 4050 laptop
- ✅ **Backend Integration** - AWS backend proxies requests to your laptop
- ✅ **Frontend Video Display** - Avatar-only UI shows generated videos
- ✅ **Automatic Fallback** - Uses TTS if GPU service unavailable

## 5-Minute Setup

### 1. On Your Laptop (Windows)

```powershell
# Navigate to avatar service
cd C:\path\to\OneDevelopment-Agent\avatar_service

# Create environment
python -m venv venv
venv\Scripts\activate

# Install basics
pip install -r requirements.txt

# Install PyTorch with CUDA (visit pytorch.org for your version)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Start the service
python avatar_server.py
```

Server runs on `http://localhost:8000`

### 2. Expose via Tunnel

```powershell
# Install ngrok from ngrok.com
ngrok http 8000
```

Copy the HTTPS URL (e.g., `https://abcd-1234.ngrok-free.app`)

### 3. Configure AWS Backend

```bash
# SSH to AWS
ssh -i your-key.pem ec2-user@your-aws-ip

# Set environment variable
export AVATAR_SERVICE_URL=https://abcd-1234.ngrok-free.app

# Restart backend
cd /home/ec2-user/OneDevelopment-Agent
docker-compose restart backend
```

### 4. Test It

1. Open Luna in browser
2. Click gear icon (⚙️) → Select **"Avatar Only"**
3. Click Luna's avatar and speak
4. She responds with voice (and video when you add the model)

## Current Status

Right now, the avatar service is a **working stub**:
- ✅ API endpoints functional
- ✅ GPU detection working
- ✅ Tunnel integration ready
- ✅ Frontend displays videos
- ⏳ **Actual model not yet installed** (placeholder returns mock response)

## Next: Add Real Model

Choose ONE:

### Option A: LivePortrait (Best Quality)
```powershell
cd ..
git clone https://github.com/KwaiVGI/LivePortrait.git
cd LivePortrait
pip install -r requirements.txt
# Download weights from their repo
```

### Option B: SadTalker (Good Alternative)
```powershell
cd ..
git clone https://github.com/OpenTalker/SadTalker.git
cd SadTalker
pip install -r requirements.txt
# Download checkpoints
```

Then edit `avatar_server.py` to integrate the model (see TODOs in code).

## Add Your Photorealistic Luna

1. Get a photorealistic female portrait (512x512 or 1024x1024)
2. Save as `avatar_service/luna_base.png`
3. Restart the service

## Testing

```bash
# Check GPU
python -c "import torch; print(torch.cuda.is_available())"

# Check service
curl http://localhost:8000/health

# Check from AWS
curl http://localhost:8000/api/avatar/health/
```

## What Happens When You Speak

```
You speak → Luna hears → Backend generates text response
    ↓
Backend calls your laptop GPU service
    ↓
GPU generates photorealistic talking video (~2-5 sec)
    ↓
Video URL returned to browser
    ↓
Video plays in avatar circle + TTS audio
```

## Fallback Behavior

If your laptop is offline or the service fails:
- Luna automatically uses the existing TTS + lip-sync simulation
- No errors, seamless degradation
- Users still get a great experience

## Files Created

```
avatar_service/
├── avatar_server.py          # Main GPU service
├── requirements.txt          # Python dependencies
├── README.md                 # Full documentation
├── QUICK_START.md           # This file
└── luna_base.png            # Your photorealistic image (add this)

backend/api/
├── views.py                 # Added avatar endpoints
└── urls.py                  # Added avatar routes

frontend/src/
├── services/api.js          # Added generateAvatar()
└── components/
    ├── LunaFreeInterface.js # Updated with video support
    └── LunaFreeInterface.css # Added video styles
```

## Important Notes

1. **Keep laptop online**: Service only works when your laptop is running
2. **Tunnel URL changes**: ngrok URL resets on restart (use paid plan for fixed URL)
3. **This is for prototyping**: For production, move to cloud GPU
4. **Model not included**: You need to install LivePortrait/SadTalker separately

## Production Roadmap

When ready for real deployment:

1. **Cloud GPU**: AWS g4dn.xlarge (~$360/month) or similar
2. **Fixed endpoint**: No tunnel needed
3. **Add authentication**: Secure the API
4. **Video caching**: Store in S3/CloudFront
5. **Queue system**: Handle multiple requests
6. **Monitoring**: Track GPU usage and costs

## Need Help?

See `PHOTOREALISTIC-AVATAR-SETUP.md` for detailed instructions.

---

**You're ready to go!** Start the avatar service, expose it via ngrok, configure AWS, and test. Then install the actual model for real photorealistic videos.





