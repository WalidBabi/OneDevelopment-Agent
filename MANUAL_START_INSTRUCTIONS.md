# Manual Server Start Instructions

## The Issue
The server is not starting on port 3000, causing `ERR_CONNECTION_REFUSED`.

## Solution

### Step 1: Stop All Processes
```bash
pkill -9 -f "react-scripts"
pkill -9 -f "npm start"
killall -9 node
```

### Step 2: Verify Ports Are Free
```bash
sudo ss -tulpn | grep -E ":(3000|8080)"
```
Should return nothing. If something is using port 3000, kill it:
```bash
sudo lsof -ti:3000 | xargs sudo kill -9
```

### Step 3: Start Frontend on Port 3000
```bash
cd /home/ec2-user/OneDevelopment-Agent/frontend
PORT=3000 HOST=0.0.0.0 BROWSER=none npm start > /tmp/frontend.log 2>&1 &
```

### Step 4: Monitor Startup (wait 15-20 seconds)
```bash
tail -f /tmp/frontend.log
```

You should see:
```
Compiled successfully!
Local:            http://localhost:3000
On Your Network:  http://172.31.28.22:3000
```

Press Ctrl+C to exit tail.

### Step 5: Test Locally
```bash
curl http://localhost:3000
```
Should return HTML content.

### Step 6: Test Externally
In your browser, visit: `http://13.62.188.127:3000`

## If It Still Shows Port 8080

If the log shows the server started on port 8080 instead of 3000, it means port 3000 is blocked or in use.

**Solution A: Add Security Group Rule for Port 8080**
1. Go to AWS Console → EC2 → Security Groups
2. Find security group `sgr-05e9cac6b953422c2`
3. Add inbound rule:
   - Type: Custom TCP
   - Port: 8080
   - Source: 0.0.0.0/0
4. Try accessing: `http://13.62.188.127:8080`

**Solution B: Force Port 3000**
The package.json has been updated to force port 3000. If it still uses 8080, there's a system-level conflict.

## Quick Start Script
```bash
cd /home/ec2-user/OneDevelopment-Agent
bash manage-servers.sh restart
```

Wait 20 seconds, then check:
```bash
tail -30 /tmp/frontend.log | grep -E "Local|Network|3000|8080"
```

## Troubleshooting

### Check if server is running:
```bash
ps aux | grep node
```

### Check what ports are in use:
```bash
sudo netstat -tulpn | grep -E ":(3000|8080)"
```

### View full logs:
```bash
tail -50 /tmp/frontend.log
```

### Start backend (if needed):
```bash
cd /home/ec2-user/OneDevelopment-Agent/backend
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000 > /tmp/backend.log 2>&1 &
```




