#!/bin/bash
set -e

echo "=========================================="
echo "Starting Frontend Server on Port 3000"
echo "=========================================="

# Kill any existing processes
echo "1. Stopping existing processes..."
pkill -9 -f "react-scripts" 2>/dev/null || true
pkill -9 -f "npm start" 2>/dev/null || true
killall -9 node 2>/dev/null || true
sleep 2

# Navigate to frontend directory
cd /home/ec2-user/OneDevelopment-Agent/frontend

# Create .env file with correct port
echo "2. Creating .env file..."
cat > .env << EOF
PORT=3000
HOST=0.0.0.0
BROWSER=none
EOF

echo "   .env contents:"
cat .env
echo ""

# Remove any existing log
rm -f /tmp/frontend_start.log

# Start the server
echo "3. Starting npm server..."
export PORT=3000
export HOST=0.0.0.0
export BROWSER=none

nohup npm start > /tmp/frontend_start.log 2>&1 &
SERVER_PID=$!

echo "   Started with PID: $SERVER_PID"
echo ""

# Wait for server to start
echo "4. Waiting for server to start (this may take 15-20 seconds)..."
for i in {1..20}; do
    sleep 1
    if grep -q "Compiled successfully" /tmp/frontend_start.log 2>/dev/null; then
        echo "   ✓ Server compiled successfully!"
        break
    fi
    echo -n "."
done
echo ""

# Check if process is still running
if ps -p $SERVER_PID > /dev/null 2>&1; then
    echo "5. ✓ Server process is running (PID: $SERVER_PID)"
else
    echo "5. ✗ Server process died. Check logs:"
    tail -30 /tmp/frontend_start.log
    exit 1
fi

# Show port information from logs
echo ""
echo "6. Server information:"
grep -E "(Local|Network|localhost|3000|8080)" /tmp/frontend_start.log | head -3 || tail -5 /tmp/frontend_start.log

echo ""
echo "=========================================="
echo "Server should be accessible at:"
echo "  http://13.62.188.127:3000"
echo ""
echo "To view logs: tail -f /tmp/frontend_start.log"
echo "To check status: ps -p $SERVER_PID"
echo "=========================================="





