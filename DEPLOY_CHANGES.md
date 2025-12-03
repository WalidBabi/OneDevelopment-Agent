# 🚀 Deploy Changes to AWS

## Files Changed

### Critical Files (Must Deploy):
1. `frontend/src/components/LunaFreeInterface.js`
   - Fixed video player
   - Removed old audio playback
   - Added smooth transitions

2. `frontend/src/services/api.js`
   - Added quality parameter
   - Defaults to 'fast' mode

3. `backend/api/views.py`
   - Increased timeout to 600s
   - Passes quality parameter

4. `avatar_service/avatar_server_final.py`
   - Force fast quality mode
   - Optimized settings

5. `avatar_service/sadtalker_generator.py`
   - Fast mode optimizations
   - GPU batch size = 4

---

## Deployment Steps

### Step 1: Commit Changes
```bash
git add frontend/src/components/LunaFreeInterface.js
git add frontend/src/services/api.js
git add backend/api/views.py
git add avatar_service/avatar_server_final.py
git add avatar_service/sadtalker_generator.py
git commit -m "Optimize avatar generation: fast mode, fix video display, remove old audio"
```

### Step 2: Push to Repository
```bash
git push origin main
```

### Step 3: Deploy on AWS

**SSH into AWS:**
```bash
ssh ec2-user@<YOUR_SERVER_IP>
```

**Pull changes:**
```bash
cd /home/ec2-user/OneDevelopment-Agent
git pull origin main
```

**Restart servers:**
```bash
./manage-servers.sh restart
```

---

## Alternative: Quick Deploy Script

I can create a script that does all of this automatically!

---

## Important Notes

### Avatar Service Setup
The avatar service (video generation) runs on your **laptop** via ngrok:
- Laptop: `localhost:8000`
- ngrok: `https://YOUR_UNIQUE_ID.ngrok-free.app` (get from `ngrok http 8000`)
- AWS Backend connects to ngrok URL via `AVATAR_SERVICE_URL` env var

**⚠️ SECURITY:** Never commit ngrok URLs to version control!

**This means:**
- Video generation happens on your laptop GPU
- AWS just proxies the requests
- You don't need GPU on AWS (saves money!)

### After Deployment
1. Frontend changes will be live on AWS
2. Backend changes will be live on AWS
3. Avatar generation still happens on your laptop
4. Everything works together via ngrok!

---

## Cost Savings

**Current Setup (Recommended):**
- AWS: Frontend + Backend (no GPU needed)
- Laptop: Avatar generation (uses your RTX 4050)
- Cost: ~$10-20/month (just AWS hosting)

**Alternative (Expensive):**
- AWS: Everything including GPU
- Cost: ~$150-300/month (GPU instance)

**Your current setup is perfect!** 💰

---

## Next Steps

1. Commit and push changes
2. SSH into AWS and pull
3. Restart servers on AWS
4. Test from http://<YOUR_SERVER_IP>:3000/
5. Download Wav2Lip for 8-12s generation

Ready to commit and push?

