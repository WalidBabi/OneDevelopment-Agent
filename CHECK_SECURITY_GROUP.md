# AWS Security Group Configuration

## Issue: Connection Refused on Port 3000

If you're getting `ERR_CONNECTION_REFUSED` when accessing `http://13.62.188.127:3000`, check the AWS Security Group settings.

## Steps to Fix:

1. **Go to AWS Console** → EC2 → Security Groups
2. **Find the security group** attached to instance `13.62.188.127`
3. **Add Inbound Rule**:
   - Type: Custom TCP
   - Port: 3000
   - Source: 0.0.0.0/0 (or your IP for security)
   - Description: Frontend React App

4. **Also ensure port 8000 is open** (for backend):
   - Type: Custom TCP
   - Port: 8000
   - Source: 0.0.0.0/0

## Verify Server is Running:

```bash
# Check if server is running
ps aux | grep node

# Check what ports are listening
sudo netstat -tulpn | grep -E ":(3000|8080)"

# Check server logs
tail -f /tmp/frontend.log
```

## Start Server Manually:

```bash
cd /home/ec2-user/OneDevelopment-Agent/frontend
PORT=3000 HOST=0.0.0.0 BROWSER=none npm start
```





