#!/bin/bash
# Restart frontend on port 3000

echo "🛑 Stopping all Node processes..."
pkill -9 -f "react-scripts"
pkill -9 -f "npm start"
killall -9 node 2>/dev/null
sleep 3

echo "📝 Setting up .env file..."
cd /home/ec2-user/OneDevelopment-Agent/frontend
echo "PORT=3000" > .env
echo "HOST=0.0.0.0" >> .env
cat .env

echo "🚀 Starting frontend on port 3000..."
cd /home/ec2-user/OneDevelopment-Agent/frontend
BROWSER=none PORT=3000 nohup npm start > /tmp/frontend.log 2>&1 &

sleep 8

echo "📊 Checking status..."
if pgrep -f "react-scripts" > /dev/null; then
    echo "✅ Frontend process is running"
    echo ""
    echo "📋 Recent logs:"
    tail -15 /tmp/frontend.log | grep -E "(Local|Network|port|3000|8080|Compiled)" || tail -10 /tmp/frontend.log
else
    echo "❌ Frontend failed to start"
    echo "📋 Error logs:"
    tail -20 /tmp/frontend.log
fi





