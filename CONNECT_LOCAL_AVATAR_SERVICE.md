# Connecting Your Local Avatar Service to AWS Frontend

## Current Setup Problem

Your avatar service is running on your **local Windows PC**, but your frontend/backend are running on **AWS server (13.62.188.127)**. 

The AWS frontend cannot directly access your local Windows avatar service because:
1. Your local PC is behind a router/firewall
2. The AWS server can't reach `localhost` on your Windows machine

## Solution Options

### Option 1: Run Everything Locally (RECOMMENDED FOR TESTING)

This is the easiest solution for testing with avatar videos.

**Steps:**

1. **On your Windows PC**, open PowerShell in the project directory:

```powershell
# Start the avatar service (already running)
# Keep it running in one terminal

# Start the Django backend
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver 0.0.0.0:8000

# In another terminal, start the React frontend
cd frontend
npm install
npm start
```

2. **Access the app** at: `http://localhost:3000`

3. The frontend will automatically connect to:
   - Backend API: `http://localhost:8000/api`
   - Avatar Service: `http://localhost:8000/api/avatar/` (proxied through Django backend)

### Option 2: Expose Local Avatar Service to AWS (Advanced)

Use a tunnel service to expose your local avatar service to the internet.

**Using ngrok:**

1. **Download ngrok**: https://ngrok.com/download

2. **Start your avatar service** (already running on port 8000)

3. **Create tunnel**:
```powershell
ngrok http 8000
```

4. **Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`)

5. **Update AWS Django settings**:

SSH into AWS:
```bash
ssh ec2-user@13.62.188.127
cd /home/ec2-user/OneDevelopment-Agent/backend
```

Edit `avatar_service/views.py` to use your ngrok URL:
```python
AVATAR_SERVICE_URL = "https://your-ngrok-url.ngrok.io"
```

6. **Restart Django backend** on AWS

### Option 3: Deploy Avatar Service to AWS (Production)

For production, deploy the avatar service to AWS with GPU support.

**Requirements:**
- AWS GPU instance (g4dn.xlarge or similar)
- CUDA/GPU drivers
- SadTalker models

**Note:** This is expensive (~$0.50-1.00/hour for GPU instances)

## Current Status & Fixes Applied

### ✅ Fixed Issues:

1. **Speech recognition restart** - Now properly restarts after TTS finishes
2. **TTS audio blob errors** - Fixed early URL revocation causing playback errors  
3. **Better error handling** - More robust error messages and recovery

### 🔧 What's Working Now:

- Speech recognition continuously listens
- Auto-transcription after 2 seconds of silence
- TTS voice responses (shimmer/nova/alloy/etc.)
- Automatic restart of listening after response

### ⚠️ Current Limitation:

- Avatar videos can only be generated when:
  - Backend can reach avatar service
  - Currently: Your Windows avatar service needs to be accessible from AWS

## Testing Your Current Setup

Your avatar service IS generating videos successfully! I can see in your terminal:

```
✓ Video ready: 34c6ed16-cb6e-4d6b-97b1-6019b5a8bb7d.mp4
```

**Problem:** The AWS backend can't fetch this video because it can't reach your local Windows PC.

**Quick Test:**

1. Access your app from YOUR Windows PC browser:
   - If on AWS: `http://13.62.188.127:3000`
   - If local: `http://localhost:3000` (after starting frontend locally)

2. Try speaking - you should see:
   - ✅ Voice detected and transcribed
   - ✅ TTS response plays (shimmer voice)
   - ⚠️ Video generation shows progress but may not display (if using AWS frontend)

## Recommended Next Steps

**For immediate testing with videos:**

```powershell
# On your Windows PC:

# Terminal 1: Avatar Service (already running)
cd avatar_service
python avatar_server.py

# Terminal 2: Django Backend  
cd backend
.\venv\Scripts\activate
python manage.py runserver 0.0.0.0:8000

# Terminal 3: React Frontend
cd frontend
npm start
```

Then access: `http://localhost:3000` from your Windows PC browser.

All services will communicate over localhost, and you'll see the generated avatar videos!

## Verification Commands

**Check if services are running:**

```bash
# On AWS:
netstat -tulpn | grep :8000  # Django backend
netstat -tulpn | grep :3000  # React frontend

# On Windows:
netstat -ano | findstr :8000  # Avatar service
```

## Need Help?

If you want me to:
1. Set up ngrok tunnel
2. Configure for local development
3. Deploy to AWS with GPU

Just let me know which option you prefer!

