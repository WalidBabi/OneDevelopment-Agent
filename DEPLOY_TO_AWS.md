# 🚀 Deploy to AWS - STEP BY STEP

## ✅ Changes Pushed to GitHub!

The following changes are now in the repository:
- Frontend: Video player + audio fixes
- Backend: Timeout + quality parameter  
- Avatar Service: Speed optimizations

---

## 📋 Next Steps - Deploy on AWS

### Step 1: SSH into AWS
```bash
ssh ec2-user@<YOUR_SERVER_IP>
```
Or if you use a key:
```bash
ssh -i your-key.pem ec2-user@<YOUR_SERVER_IP>
```

### Step 2: Navigate to Project
```bash
cd /home/ec2-user/OneDevelopment-Agent
# or wherever your project is located
```

### Step 3: Pull Latest Changes
```bash
git pull origin main
```

### Step 4: Install Frontend Dependencies (if needed)
```bash
cd frontend
npm install
cd ..
```

### Step 5: Restart Servers

**Option A - If you have a restart script:**
```bash
./manage-servers.sh restart
```

**Option B - Manual restart:**

Kill existing processes:
```bash
# Find and kill frontend
pkill -f "npm start"
pkill -f "react-scripts"

# Find and kill backend
pkill -f "python manage.py runserver"
```

Start frontend:
```bash
cd frontend
nohup npm start > frontend.log 2>&1 &
cd ..
```

Start backend:
```bash
cd backend
nohup python manage.py runserver 0.0.0.0:8000 > backend.log 2>&1 &
cd ..
```

### Step 6: Verify Deployment
```bash
# Check if processes are running
ps aux | grep "npm start"
ps aux | grep "manage.py"

# Check logs
tail -f frontend/frontend.log
tail -f backend/backend.log
```

---

## 🧪 Test the Deployment

1. Open browser: http://<YOUR_SERVER_IP>:3000/
2. Ask Luna: "Hello, tell me about yourself"
3. Watch for:
   - ✅ No old audio/mouth animation
   - ✅ Progress bar shows during generation
   - ✅ Video appears and plays smoothly
   - ✅ Video has audio

---

## 🔧 Troubleshooting

### Frontend not updating?
```bash
cd frontend
rm -rf node_modules/.cache
npm start
```

### Backend not responding?
```bash
cd backend
python manage.py check
python manage.py runserver 0.0.0.0:8000
```

### Check ngrok connection:
Make sure your laptop avatar service is still running with ngrok!

---

## 📊 Current Architecture

```
┌─────────────────────────────────────────────┐
│           AWS (<YOUR_SERVER_IP>)               │
│                                             │
│  ┌─────────────┐      ┌─────────────┐     │
│  │  Frontend   │      │   Backend   │     │
│  │  (port 3000)│◄────►│  (port 8000)│     │
│  └─────────────┘      └──────┬──────┘     │
│                               │             │
└───────────────────────────────┼─────────────┘
                                │
                                │ ngrok
                                │
┌───────────────────────────────▼─────────────┐
│         Your Laptop                         │
│                                             │
│  ┌─────────────────────────────────┐       │
│  │   Avatar Service (port 8000)    │       │
│  │   GPU: NVIDIA RTX 4050          │       │
│  │   Video Generation              │       │
│  └─────────────────────────────────┘       │
└─────────────────────────────────────────────┘
```

**Important:** 
- Avatar service stays on your laptop (uses your GPU)
- Only frontend/backend need to be deployed to AWS
- Make sure ngrok is running!

---

## ✅ After Deployment Checklist

- [ ] SSH into AWS
- [ ] Pull latest changes
- [ ] Restart frontend
- [ ] Restart backend
- [ ] Test from browser
- [ ] Verify video plays correctly
- [ ] Check ngrok is still running on laptop

---

## 🎯 Expected Results

**Before:**
- Old audio plays immediately
- Old mouth animation shows
- Video takes 282 seconds
- Video doesn't display

**After:**
- No old audio/animation
- Progress bar shows real progress
- Video generates in ~30-40s (with GPU)
- Video displays and plays smoothly

---

## 💡 Pro Tip

Keep your laptop avatar service running while testing!
The ngrok tunnel connects AWS to your laptop's GPU.

Ready to deploy? Follow the steps above! 🚀

