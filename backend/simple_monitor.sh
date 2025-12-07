#!/bin/bash

while true; do
    if ! curl -s http://localhost:8000/api/health/ > /dev/null; then
        echo "$(date): Server down, restarting..." >> /home/ec2-user/OneDevelopment-Agent/backend/restart.log
        cd /home/ec2-user/OneDevelopment-Agent/backend
        pkill -f "manage.py runserver" 2>/dev/null
        source venv/bin/activate
        nohup python manage.py runserver 0.0.0.0:8000 >> /home/ec2-user/OneDevelopment-Agent/backend/server.log 2>&1 &
        sleep 5
    fi
    sleep 60
done
