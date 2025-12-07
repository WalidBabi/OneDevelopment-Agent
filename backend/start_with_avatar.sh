#!/bin/bash

# Django Backend Startup Script with Avatar Service Configuration
# This script starts the Django backend with the ngrok tunnel URL

# Set your ngrok URL here (update this when ngrok restarts)
# Current ngrok URL: https://fa8978e3c6ef.ngrok-free.app -> http://localhost:8001
export AVATAR_SERVICE_URL="https://fa8978e3c6ef.ngrok-free.app"

echo "================================================"
echo "Starting Django Backend with Avatar Service"
echo "================================================"
echo "AVATAR_SERVICE_URL: $AVATAR_SERVICE_URL"
echo "================================================"

# Activate virtual environment
source venv/bin/activate

# Start Django server
python manage.py runserver 0.0.0.0:8000

