#!/bin/bash
# OneDevelopment Agent - Server Management Script

case "$1" in
  start)
    echo "🚀 Starting servers..."
    
    # Start Backend
    cd /home/ec2-user/OneDevelopment-Agent/backend
    source venv/bin/activate
    
    # Set avatar service URL (update this when ngrok restarts)
    export AVATAR_SERVICE_URL="https://fa8978e3c6ef.ngrok-free.app"
    
    nohup python manage.py runserver 0.0.0.0:8000 > /tmp/backend.log 2>&1 &
    echo "✅ Backend started on port 8000"
    echo "   Avatar Service URL: $AVATAR_SERVICE_URL"
    
    # Start Frontend
    cd /home/ec2-user/OneDevelopment-Agent/frontend
    nohup npm start > /tmp/frontend.log 2>&1 &
    echo "✅ Frontend started on port 3000"
    
    sleep 3
    echo ""
    echo "🌐 Access your app at:"
    echo "   Frontend: http://$(curl -s ifconfig.me 2>/dev/null || echo 'YOUR_IP'):3000"
    echo "   Backend:  http://$(curl -s ifconfig.me 2>/dev/null || echo 'YOUR_IP'):8000"
    ;;
    
  stop)
    echo "🛑 Stopping servers..."
    pkill -f "manage.py runserver"
    pkill -f "npm start"
    echo "✅ Servers stopped"
    ;;
    
  restart)
    echo "🔄 Restarting servers..."
    $0 stop
    sleep 2
    $0 start
    ;;
    
  status)
    echo "📊 Server Status:"
    echo ""
    
    if pgrep -f "manage.py runserver" > /dev/null; then
        echo "✅ Backend: Running (port 8000)"
    else
        echo "❌ Backend: Stopped"
    fi
    
    if pgrep -f "npm start" > /dev/null; then
        echo "✅ Frontend: Running (port 3000)"
    else
        echo "❌ Frontend: Stopped"
    fi
    
    echo ""
    echo "PostgreSQL:"
    systemctl is-active --quiet postgresql && echo "✅ Running" || echo "❌ Stopped"
    ;;
    
  logs)
    case "$2" in
      backend)
        tail -f /tmp/backend.log
        ;;
      frontend)
        tail -f /tmp/frontend.log
        ;;
      *)
        echo "Usage: $0 logs [backend|frontend]"
        ;;
    esac
    ;;
    
  *)
    echo "OneDevelopment Agent - Server Management"
    echo ""
    echo "Usage: $0 {start|stop|restart|status|logs}"
    echo ""
    echo "Commands:"
    echo "  start    - Start both servers"
    echo "  stop     - Stop both servers"
    echo "  restart  - Restart both servers"
    echo "  status   - Check server status"
    echo "  logs     - View logs (backend|frontend)"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 status"
    echo "  $0 logs backend"
    exit 1
    ;;
esac

