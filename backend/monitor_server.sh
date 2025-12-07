#!/bin/bash

# Backend server monitoring script
# Checks if server is running and restarts if needed

BACKEND_DIR="/home/ec2-user/OneDevelopment-Agent/backend"
LOG_FILE="$BACKEND_DIR/server_monitor.log"
PID_FILE="$BACKEND_DIR/server.pid"

# Function to check if server is running
check_server() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            # Check if server is responding
            if curl -s http://localhost:8000/api/health/ > /dev/null 2>&1; then
                echo "$(date): Server is running (PID: $PID)" >> "$LOG_FILE"
                return 0
            else
                echo "$(date): Server not responding, killing process" >> "$LOG_FILE"
                kill $PID 2>/dev/null
                rm -f "$PID_FILE"
                return 1
            fi
        else
            echo "$(date): PID file exists but process not running" >> "$LOG_FILE"
            rm -f "$PID_FILE"
            return 1
        fi
    else
        echo "$(date): No PID file found" >> "$LOG_FILE"
        return 1
    fi
}

# Function to start server
start_server() {
    echo "$(date): Starting backend server..." >> "$LOG_FILE"
    cd "$BACKEND_DIR"
    
    # Kill any existing Django processes
    pkill -f "manage.py runserver" 2>/dev/null
    
    # Start server in background
    source venv/bin/activate
    nohup python manage.py runserver 0.0.0.0:8000 > server.log 2>&1 &
    echo $! > "$PID_FILE"
    
    # Wait a moment and check if it started successfully
    sleep 3
    if check_server; then
        echo "$(date): Server started successfully" >> "$LOG_FILE"
    else
        echo "$(date): Failed to start server" >> "$LOG_FILE"
    fi
}

# Main monitoring loop
while true; do
    if ! check_server; then
        start_server
    fi
    sleep 30  # Check every 30 seconds
done
