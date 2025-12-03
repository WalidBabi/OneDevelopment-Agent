# 🔗 Setup Backend Connection to Avatar Service

## ✅ Found ngrok Tunnel!

**ngrok URL:** `https://YOUR_UNIQUE_ID.ngrok-free.app`  
**Tunnels to:** `http://localhost:8000` (avatar service)

---

## 🎯 Setup Steps

### Step 1: Set Environment Variable

The backend needs `AVATAR_SERVICE_URL` environment variable set to the ngrok URL.

**Option A: Set in Backend Environment (Recommended)**

Add to your backend `.env` file or environment:
```bash
AVATAR_SERVICE_URL=https://YOUR_UNIQUE_ID.ngrok-free.app
```

**Option B: Set Before Starting Backend**

In PowerShell:
```powershell
$env:AVATAR_SERVICE_URL="https://YOUR_UNIQUE_ID.ngrok-free.app"
# Then start backend
```

**Option C: Set in Django Settings**

Add to `backend/settings.py`:
```python
AVATAR_SERVICE_URL = os.getenv('AVATAR_SERVICE_URL', 'https://YOUR_UNIQUE_ID.ngrok-free.app')
```

---

### Step 2: Verify Connection

Test if backend can reach avatar service:

```powershell
# Test avatar service directly via ngrok
curl https://YOUR_UNIQUE_ID.ngrok-free.app/health

# Test backend endpoint
curl http://localhost:8000/api/avatar/health/
```

---

### Step 3: Test Full Flow

1. **Frontend** (http://13.62.188.127:3000/) calls:
   - `POST /api/avatar/generate/`

2. **Backend** proxies to:
   - `POST https://YOUR_UNIQUE_ID.ngrok-free.app/generate`

3. **Avatar Service** generates video and returns:
   - Video URL (via ngrok)
   - Audio URL (via ngrok)

---

## 🔍 Current Status

- ✅ Avatar service running: `http://localhost:8000`
- ✅ ngrok tunnel active: `https://YOUR_UNIQUE_ID.ngrok-free.app`
- ⏳ Backend needs: `AVATAR_SERVICE_URL` environment variable

---

## 🚀 After Setup

1. Set `AVATAR_SERVICE_URL`
2. Restart backend server
3. Test from frontend UI
4. Avatar should respond with video! 🎬

