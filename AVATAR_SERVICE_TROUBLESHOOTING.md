# 🔧 Avatar Service Connection Troubleshooting

## Current Status
- **Backend URL**: `http://13.62.188.127:8000`
- **ngrok URL**: `https://fa8978e3c6ef.ngrok-free.app`
- **ngrok Forwarding**: `https://fa8978e3c6ef.ngrok-free.app -> http://localhost:8001`
- **Issue**: Avatar service health check returns 404

## ✅ What I Fixed

1. **Updated startup scripts** with your current ngrok URL:
   - `backend/start_with_avatar.sh`
   - `restart-backend.sh`
   - `manage-servers.sh`

2. **Created helper script**: `update-avatar-url.sh` to easily update the URL when ngrok restarts

## 🔍 Troubleshooting Steps

### Step 1: Verify Avatar Service is Running on Your Laptop

On your **local laptop**, check if the avatar service is running:

```bash
# Check if avatar service is running on port 8001
curl http://localhost:8001/health

# Or check what's running on port 8001
netstat -an | grep 8001
# On Windows: netstat -an | findstr 8001
```

**Expected response**:
```json
{
  "status": "healthy",
  "device": "cuda",
  "gpu_info": {...}
}
```

### Step 2: Verify ngrok is Forwarding Correctly

On your **local laptop**, test the ngrok URL:

```bash
# Test health endpoint via ngrok
curl https://fa8978e3c6ef.ngrok-free.app/health

# If you get ngrok browser warning, add header:
curl -H "ngrok-skip-browser-warning: true" https://fa8978e3c6ef.ngrok-free.app/health
```

**If you get 404**, the avatar service might not be running or ngrok is forwarding to the wrong port.

### Step 3: Check Avatar Service Port

The avatar service might be running on a different port. Common ports:
- `8000` (default)
- `8001` (what ngrok is forwarding to)
- `8080`

**To find the correct port**, check:
1. What port your avatar service script uses
2. What ngrok is actually forwarding to

### Step 4: Restart Backend with Correct URL

On the **EC2 server**, restart the backend:

```bash
cd /home/ec2-user/OneDevelopment-Agent
./restart-backend.sh
```

Or manually:
```bash
cd /home/ec2-user/OneDevelopment-Agent/backend
source venv/bin/activate
export AVATAR_SERVICE_URL="https://fa8978e3c6ef.ngrok-free.app"
python manage.py runserver 0.0.0.0:8000
```

### Step 5: Test Backend Connection

On the **EC2 server**, test if backend can reach avatar service:

```bash
# Test backend's avatar health endpoint
curl http://localhost:8000/api/avatar/health/

# Should return:
# {"status": "healthy", ...} if avatar service is accessible
# {"status": "unavailable", ...} if not configured or unreachable
```

## 🚨 Common Issues

### Issue 1: Avatar Service Not Running
**Symptom**: ngrok returns 404
**Solution**: Start avatar service on your laptop:
```bash
cd avatar_service
python avatar_server_sadtalker.py
# Or whichever avatar server script you're using
```

### Issue 2: Wrong Port
**Symptom**: ngrok forwards to port 8001 but service runs on 8000
**Solution**: Either:
- Change ngrok: `ngrok http 8000` (if service runs on 8000)
- Or change avatar service to run on 8001

### Issue 3: ngrok URL Changed
**Symptom**: Backend can't connect (old URL)
**Solution**: Update URL using helper script:
```bash
./update-avatar-url.sh
# Enter new ngrok URL when prompted
```

### Issue 4: ngrok Browser Warning
**Symptom**: Requests blocked by ngrok browser warning page
**Solution**: Add header to requests (already handled in backend code) or upgrade ngrok plan

## 📝 Quick Reference

### Update ngrok URL
```bash
./update-avatar-url.sh
```

### Restart Backend
```bash
./restart-backend.sh
```

### Check Backend Logs
```bash
tail -f /home/ec2-user/OneDevelopment-Agent/server.log
```

### Test Avatar Service (from laptop)
```bash
curl http://localhost:8001/health
curl https://fa8978e3c6ef.ngrok-free.app/health
```

### Test Backend (from EC2)
```bash
curl http://localhost:8000/api/avatar/health/
```

## 🎯 Next Steps

1. **On your laptop**: Verify avatar service is running and accessible at `http://localhost:8001/health`
2. **On your laptop**: Test ngrok URL: `curl https://fa8978e3c6ef.ngrok-free.app/health`
3. **On EC2 server**: Restart backend with: `./restart-backend.sh`
4. **On EC2 server**: Test connection: `curl http://localhost:8000/api/avatar/health/`
5. **In browser**: Check frontend - avatar service should now be available!








