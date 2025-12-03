# 🚀 Deploy Avatar Video Generation to AWS

## Current Setup ✅

- **Avatar Service**: Running locally on port 8000
- **ngrok Tunnel**: `https://YOUR_UNIQUE_ID.ngrok-free.app`
- **GPU**: NVIDIA RTX 4050 (local)
- **Status**: Ready to connect to AWS!

---

## Step 1: Push Latest Changes to GitHub

Your laptop already has the latest code. Make sure it's pushed:

```bash
cd %USERPROFILE%\Downloads\OneDevelopment-Agent-main\OneDevelopment-Agent-main
git add .
git commit -m "Add video player and optimize avatar generation"
git push origin main
```

✅ **Done!** Changes are already pushed.

---

## Step 2: SSH into AWS and Deploy

### Connect to AWS:

```bash
ssh ec2-user@13.62.188.127
```

Or with key:
```bash
ssh -i your-key.pem ec2-user@13.62.188.127
```

### Pull Latest Code:

```bash
cd /home/ec2-user/OneDevelopment-Agent
git pull origin main
```

### Set Avatar Service URL:

```bash
# Set environment variable
export AVATAR_SERVICE_URL=https://YOUR_UNIQUE_ID.ngrok-free.app

# Add to .env file for persistence
echo "AVATAR_SERVICE_URL=https://YOUR_UNIQUE_ID.ngrok-free.app" >> backend/.env
```

### Install Frontend Dependencies (if needed):

```bash
cd frontend
npm install
cd ..
```

### Restart Servers:

**Option A - If you have a restart script:**
```bash
./manage-servers.sh restart
```

**Option B - Manual restart:**

Kill existing processes:
```bash
# Kill frontend
pkill -f "npm start"
pkill -f "react-scripts"

# Kill backend
pkill -f "manage.py runserver"
```

Start backend:
```bash
cd backend
nohup python manage.py runserver 0.0.0.0:8000 > backend.log 2>&1 &
cd ..
```

Start frontend:
```bash
cd frontend
nohup npm start > frontend.log 2>&1 &
cd ..
```

### Verify Servers:

```bash
# Check processes
ps aux | grep "npm start"
ps aux | grep "manage.py"

# Check backend logs
tail -f backend/backend.log

# Check frontend logs
tail -f frontend/frontend.log
```

---

## Step 3: Test the Setup

### From AWS Server:

```bash
# Test backend can reach your laptop
curl https://YOUR_UNIQUE_ID.ngrok-free.app/health

# Should return:
# {"status": "healthy", "device": "cuda", "gpu_info": {...}}
```

### From Browser:

1. Open: **http://13.62.188.127:3000/**
2. Ask Luna: "Tell me about One Development's projects"
3. Watch for:
   - ✅ Progress bar showing video generation
   - ✅ Video appears and plays with audio
   - ✅ Smooth fade-in transition
   - ✅ No old mouth animation

---

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────┐
│                  AWS (13.62.188.127)                     │
│                                                          │
│  ┌────────────────┐         ┌─────────────────┐        │
│  │   Frontend     │◄────────┤    Backend      │        │
│  │  (React:3000)  │         │  (Django:8000)  │        │
│  └────────────────┘         └────────┬────────┘        │
│                                      │                   │
│                                      │ Proxy Avatar      │
│                                      │ Requests          │
└──────────────────────────────────────┼──────────────────┘
                                       │
                                       │ ngrok Tunnel
                                       │ (YOUR_NGROK_ID)
                                       │
┌──────────────────────────────────────▼──────────────────┐
│              Your Laptop (Windows)                       │
│                                                          │
│  ┌──────────────────────────────────────────┐          │
│  │   Avatar Service (FastAPI:8000)          │          │
│  │   • GPU: NVIDIA RTX 4050                 │          │
│  │   • SadTalker: Video Generation          │          │
│  │   • TTS: Audio Generation                │          │
│  │   • 70s per video (with GPU)             │          │
│  └──────────────────────────────────────────┘          │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## How It Works

1. **User asks question** on AWS frontend
2. **Frontend calls** `/api/avatar/generate/` on AWS backend
3. **Backend proxies request** to your laptop via ngrok
4. **Your laptop generates video** using GPU (SadTalker)
5. **Video URL rewritten** to use AWS proxy `/api/avatar/videos/{id}`
6. **Frontend plays video** streamed from your laptop through AWS

---

## OpenAI Shimmer Voice

Your production uses OpenAI's Shimmer voice. To use it:

### On Your Laptop (Avatar Service):

Add OpenAI API key to environment:

```bash
# In avatar_service directory
echo "OPENAI_API_KEY=your-key-here" >> .env
```

Then update `tts_manager.py` to support OpenAI TTS (if not already done).

### On AWS (Backend):

The backend passes `voice_id` to your laptop:

```python
# Already configured in backend/api/views.py
response = requests.post(
    f"{avatar_service_url}/generate",
    json={
        'text': text,
        'voice_id': 'shimmer',  # OpenAI voice
        'quality': 'fast'
    }
)
```

---

## Troubleshooting

### Avatar service not responding:

Check if it's running on your laptop:
```powershell
Get-Process python | Where-Object {$_.Path -like "*avatar_service*"}
```

Restart if needed:
```powershell
cd %USERPROFILE%\Downloads\OneDevelopment-Agent-main\OneDevelopment-Agent-main\avatar_service
python avatar_server_final.py
```

### ngrok tunnel closed:

Check ngrok status:
```powershell
curl http://localhost:4040/api/tunnels
```

Restart ngrok:
```powershell
cd %USERPROFILE%\Downloads\ngrok-v3-stable-windows-amd64
.\ngrok http 8000
```

### AWS can't reach laptop:

Test from AWS:
```bash
curl https://YOUR_UNIQUE_ID.ngrok-free.app/health
```

If fails, check:
1. Laptop avatar service is running
2. ngrok tunnel is active
3. Firewall allows connections

### Video not playing on AWS:

Check browser console for errors. Verify:
1. Video URL points to `/api/avatar/videos/{id}`
2. Backend proxy is working
3. CORS headers allow video streaming

---

## Cost Savings 💰

**Current Setup:**
- AWS: Frontend + Backend (~$10-20/month)
- Laptop: GPU generation (Free - uses your RTX 4050)
- **Total: ~$10-20/month**

**If using AWS GPU:**
- AWS: Everything including GPU (~$150-300/month)
- **Total: ~$150-300/month**

**Your setup saves $130-280/month!** 🎉

---

## Next Steps

1. ✅ Avatar service running on laptop
2. ✅ ngrok tunnel active
3. ⏳ Deploy to AWS (follow Step 2 above)
4. ⏳ Test from AWS UI
5. ⏳ Add OpenAI Shimmer voice (optional)

---

## Quick Commands

### On Laptop:

```powershell
# Check avatar service
curl http://localhost:8000/health

# Get ngrok URL
curl http://localhost:4040/api/tunnels
```

### On AWS:

```bash
# Set avatar URL
export AVATAR_SERVICE_URL=https://YOUR_UNIQUE_ID.ngrok-free.app

# Restart backend
pkill -f "manage.py runserver"
cd backend && nohup python manage.py runserver 0.0.0.0:8000 > backend.log 2>&1 &

# Check backend can reach laptop
curl $AVATAR_SERVICE_URL/health
```

---

Ready to deploy? Follow **Step 2** above! 🚀

