#!/bin/bash

echo "=========================================="
echo "Starting OneDevelopment Server on Port 3000"
echo "=========================================="

# Kill any existing processes
echo "Stopping any existing processes..."
pkill -9 -f "react-scripts" 2>/dev/null || true
pkill -9 -f "npm start" 2>/dev/null || true
killall -9 node 2>/dev/null || true
sleep 2

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed!"
    echo "Please install Node.js first."
    exit 1
fi

echo "✓ Node.js version: $(node --version)"
echo "✓ npm version: $(npm --version)"

# Navigate to frontend directory
cd /home/ec2-user/OneDevelopment-Agent/frontend || exit 1

# Create .env file to ensure port 3000
echo "Creating .env file for port 3000..."
cat > .env << 'EOF'
PORT=3000
HOST=0.0.0.0
BROWSER=none
EOF

echo "✓ .env file created:"
cat .env

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies (this may take a few minutes)..."
    npm install
fi

# Start the server
echo ""
echo "Starting frontend server on port 3000..."
echo "This will take 15-20 seconds to compile..."
echo ""

PORT=3000 HOST=0.0.0.0 BROWSER=none npm start > /tmp/frontend.log 2>&1 &
SERVER_PID=$!

echo "✓ Server started with PID: $SERVER_PID"
echo ""

# Wait for server to start
echo "Waiting for server to compile..."
for i in {1..30}; do
    sleep 1
    if grep -q "Compiled successfully" /tmp/frontend.log 2>/dev/null; then
        echo ""
        echo "✓ Server compiled successfully!"
        break
    fi
    if grep -q "Failed to compile" /tmp/frontend.log 2>/dev/null; then
        echo ""
        echo "❌ Server failed to compile. Check logs:"
        tail -30 /tmp/frontend.log
        exit 1
    fi
    echo -n "."
done

echo ""
echo ""

# Check if process is still running
if ! ps -p $SERVER_PID > /dev/null 2>&1; then
    echo "❌ Server process died. Check logs:"
    tail -30 /tmp/frontend.log
    exit 1
fi

# Show server information
echo "=========================================="
echo "✓ Server is running!"
echo "=========================================="
echo ""
echo "Server details:"
grep -E "(Local|Network|localhost)" /tmp/frontend.log 2>/dev/null | head -3 || echo "  Check logs for details"
echo ""
echo "Access your application at:"
echo "  External: http://13.62.188.127:3000"
echo "  Internal: http://localhost:3000"
echo ""
echo "To view logs:"
echo "  tail -f /tmp/frontend.log"
echo ""
echo "To stop the server:"
echo "  pkill -f react-scripts"
echo ""
echo "Server PID: $SERVER_PID"
echo "=========================================="



