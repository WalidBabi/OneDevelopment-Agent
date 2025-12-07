#!/bin/bash
# Quick script to update AVATAR_SERVICE_URL and restart backend

echo "🔗 Avatar Service URL Updater"
echo "================================"
echo ""

# Get current ngrok URL from user
read -p "Enter your ngrok URL (e.g., https://fa8978e3c6ef.ngrok-free.app): " NGROK_URL

if [ -z "$NGROK_URL" ]; then
    echo "❌ Error: No URL provided!"
    exit 1
fi

echo ""
echo "📝 Updating scripts with new URL: $NGROK_URL"
echo ""

# Update start_with_avatar.sh
sed -i "s|export AVATAR_SERVICE_URL=.*|export AVATAR_SERVICE_URL=\"$NGROK_URL\"|" backend/start_with_avatar.sh
echo "✅ Updated backend/start_with_avatar.sh"

# Update restart-backend.sh
sed -i "s|export AVATAR_SERVICE_URL=.*|export AVATAR_SERVICE_URL=\"$NGROK_URL\"|" restart-backend.sh
echo "✅ Updated restart-backend.sh"

# Update manage-servers.sh
sed -i "s|export AVATAR_SERVICE_URL=.*|export AVATAR_SERVICE_URL=\"$NGROK_URL\"|" manage-servers.sh
echo "✅ Updated manage-servers.sh"

echo ""
echo "🧪 Testing avatar service connection..."
if curl -s --max-time 5 "$NGROK_URL/health" > /dev/null 2>&1; then
    echo "✅ Avatar service is reachable!"
    curl -s "$NGROK_URL/health" | python3 -m json.tool 2>/dev/null || echo "   (Response received)"
else
    echo "⚠️  Warning: Could not reach avatar service at $NGROK_URL/health"
    echo "   Make sure:"
    echo "   1. Avatar service is running on your local laptop"
    echo "   2. ngrok is running and forwarding correctly"
    echo "   3. The URL is correct"
fi

echo ""
echo "🔄 To restart backend with new URL, run:"
echo "   ./restart-backend.sh"
echo ""
echo "   Or manually:"
echo "   export AVATAR_SERVICE_URL=\"$NGROK_URL\""
echo "   cd backend && source venv/bin/activate && python manage.py runserver 0.0.0.0:8000"








