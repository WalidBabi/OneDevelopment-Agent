# 🎬 Test Avatar from UI - Quick Guide

## ✅ Setup Complete!

**Connection Status:**
- ⏳ Avatar service: Should be running on `localhost:8000`
- ⏳ ngrok tunnel: Run `ngrok http 8000` to get your URL
- ⏳ AVATAR_SERVICE_URL: Must be set (see instructions below)
- ✅ Backend API: `/api/avatar/generate/`

**⚠️ SECURITY WARNING:** Never commit ngrok URLs to version control!

---

## 🚀 Test Steps

### Step 1: Restart Backend (If Running)

**Important:** Backend needs to be restarted to pick up the new `AVATAR_SERVICE_URL` environment variable.

If backend is running:
1. Stop it (Ctrl+C)
2. Restart it (it will now use the ngrok URL)

---

### Step 2: Open UI

Go to: **http://<YOUR_SERVER_IP>:3000/**

You should see the Luna Avatar interface.

---

### Step 3: Ask Luna a Question

**Example questions:**
- "Hello, tell me about yourself"
- "What is One Development?"
- "What projects are available?"

---

### Step 4: Watch Luna Respond!

**What happens:**
1. You type/speak a question
2. Backend processes the question
3. Backend calls avatar service via ngrok
4. Avatar service generates video (30-40s with GPU)
5. Video appears in UI! 🎬

---

## 🔍 Troubleshooting

### Avatar Not Responding?

1. **Check backend logs:**
   - Look for errors about `AVATAR_SERVICE_URL`
   - Check if it's trying to connect to ngrok URL

2. **Check avatar service:**
   ```powershell
   # Replace with your actual ngrok URL
   curl $env:AVATAR_SERVICE_URL/health
   ```
   Should return: `{"status":"healthy",...}`

3. **Check backend endpoint:**
   ```powershell
   curl http://localhost:8000/api/avatar/health/
   ```
   Should return avatar service status

4. **Check browser console:**
   - Open DevTools (F12)
   - Look for errors in Console tab
   - Check Network tab for failed requests

---

## 📊 Expected Flow

```
User → Frontend (port 3000)
     → Backend API (/api/avatar/generate/)
     → ngrok Tunnel ($AVATAR_SERVICE_URL)
     → Avatar Service (localhost:8000)
     → Generate Video (30-40s)
     → Return Video URL
     → Frontend displays video
```

---

## 🎉 Success!

When it works, you'll see:
- ✅ Luna's avatar video playing
- ✅ Audio synchronized
- ✅ Professional talking head animation
- ✅ Response in ~30-40 seconds (with GPU)

**Enjoy talking to Luna!** 🎭

