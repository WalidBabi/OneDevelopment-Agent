#!/bin/bash
# Script to restart the backend server with new changes

echo "🔄 Restarting Luna backend..."

# Kill existing server
pkill -f "manage.py runserver" 2>/dev/null
echo "✅ Stopped old server"

# Wait a moment
sleep 2

# Start new server
cd /home/ec2-user/OneDevelopment-Agent/backend
source venv/bin/activate

# Set avatar service URL (update this when ngrok restarts)
export AVATAR_SERVICE_URL="https://fa8978e3c6ef.ngrok-free.app"

# Set LiveAvatar avatar ID
export LIVEAVATAR_AVATAR_ID="073b60a9-89a8-45aa-8902-c358f64d2852"

nohup python manage.py runserver 0.0.0.0:8000 > ../server.log 2>&1 &

# Wait for startup
sleep 3

# Check if running
if ps aux | grep -v grep | grep "manage.py runserver" > /dev/null; then
    echo "✅ Backend server restarted successfully!"
    echo "📝 Logs: tail -f /home/ec2-user/OneDevelopment-Agent/server.log"
else
    echo "❌ Failed to start server. Check logs:"
    tail -20 /home/ec2-user/OneDevelopment-Agent/server.log
    exit 1
fi

# Test health
sleep 2
echo ""
echo "🔍 Testing health endpoint..."
curl -s http://localhost:8000/api/health/ | python3 -m json.tool 2>/dev/null || echo "Health check pending..."

echo ""
echo "🎉 Backend is ready!"





