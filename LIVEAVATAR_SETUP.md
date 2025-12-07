# 🎭 LiveAvatar Integration Setup

This guide will help you set up LiveAvatar with Luna using the official LiveAvatar API.

## 📋 Prerequisites

1. **LiveAvatar Account**: Sign up at [LiveAvatar](https://liveavatar.com)
2. **API Key**: Get your API key from your LiveAvatar dashboard
3. **Luna.png**: The avatar image should be in `frontend/public/Luna.png`

## 🚀 Quick Setup

### Step 1: Get Your LiveAvatar API Key

1. Go to [LiveAvatar Dashboard](https://liveavatar.com)
2. Navigate to API Settings
3. Copy your API key

### Step 2: Configure Environment Variables

Add to your backend `.env` file:

```bash
# LiveAvatar API Configuration
LIVEAVATAR_API_KEY=your_api_key_here
# Optional: Custom API URL (defaults to https://api.liveavatar.com)
# LIVEAVATAR_API_URL=https://api.liveavatar.com
```

### Step 3: Restart Backend

```bash
cd /home/ec2-user/OneDevelopment-Agent/backend
source venv/bin/activate
pkill -f "manage.py runserver"
python manage.py runserver 0.0.0.0:8000 &
```

### Step 4: Test the Integration

1. Open your frontend: `http://13.62.188.127:3000`
2. Navigate to the LiveAvatar interface
3. You should see Luna.png displayed as the avatar
4. Try sending a message to test the conversation flow

## 🎨 Using Luna.png as Custom Avatar

**Important**: LiveAvatar requires **video footage** to create custom avatars, not just images.

To create a custom avatar from Luna:

1. **Record Video Footage**:
   - Minimum 2 minutes of continuous video
   - Resolution: At least 1920x1080 (HD)
   - Framing: Subject from chest up
   - Lighting: Soft, even lighting
   - Performance: Steady eye contact, minimal movement
   - See [LiveAvatar Filming Tips](https://help.heygen.com/en/articles/9612935-live-avatar-filming-tips)

2. **Get Consent Recording**:
   - Record a consent statement from the person in the footage

3. **Upload to LiveAvatar**:
   - Submit video and consent to LiveAvatar
   - Wait for avatar creation (processing time varies)

4. **Update Avatar ID**:
   - Once created, you'll receive an `avatar_id`
   - Update `getDefaultAvatarId()` in `frontend/src/services/liveavatar.js`:
   ```javascript
   getDefaultAvatarId() {
     return 'your-custom-avatar-id-here';
   }
   ```

## 📡 API Endpoints

The backend provides these LiveAvatar endpoints:

### Create Session Token
```
POST /api/liveavatar/session-token/
{
  "avatar_id": "optional-avatar-id",
  "mode": "FULL",  // or "CUSTOM"
  "voice_id": "optional-voice-id",
  "context_id": "optional-context-id"
}
```

### Start Session
```
POST /api/liveavatar/sessions/start/
{
  "session_token": "token-from-create-session-token"
}
```

### Send Message (Full Mode)
```
POST /api/liveavatar/sessions/<session_id>/message/
{
  "message": "Hello, I'm Luna!",
  "session_token": "token"
}
```

### End Session
```
POST /api/liveavatar/sessions/<session_id>/end/
{
  "session_token": "token"
}
```

## 🔧 Configuration

### Frontend Configuration

The frontend service (`frontend/src/services/liveavatar.js`) uses:
- `REACT_APP_API_URL` environment variable (defaults to `http://13.62.188.127:8000/api`)
- Default avatar ID: `33946dd18761452bb192b38011b177a9` (update with your custom avatar ID)

### Backend Configuration

The backend requires:
- `LIVEAVATAR_API_KEY` in environment variables
- Optional: `LIVEAVATAR_API_URL` (defaults to `https://api.liveavatar.com`)

## 🎯 Current Implementation

### Full Mode (Recommended)
- Uses LiveAvatar's Full Mode for easier integration
- Handles LLM, TTS, and avatar rendering automatically
- Send text messages and get avatar responses

### Custom Mode (Advanced)
- Requires WebRTC implementation for audio streaming
- More control but more complex setup
- Currently not fully implemented

## 🐛 Troubleshooting

### "LIVEAVATAR_API_KEY not configured"
- Make sure you've added `LIVEAVATAR_API_KEY` to your backend `.env` file
- Restart the backend server after adding the key

### "Failed to connect to LiveAvatar API"
- Check your internet connection
- Verify the API key is correct
- Check if LiveAvatar API is accessible from your server

### Avatar not showing
- Currently, Luna.png is shown as a placeholder
- To show the actual LiveAvatar stream, integrate LiveKit Web SDK
- See [LiveAvatar Documentation](https://docs.liveavatar.com/docs/getting-started) for LiveKit integration

### Session creation fails
- Verify your API key has proper permissions
- Check that the avatar_id exists in your LiveAvatar account
- Review backend logs for detailed error messages

## 📚 Resources

- [LiveAvatar Documentation](https://docs.liveavatar.com/docs/getting-started)
- [LiveAvatar Quickstart Guide](https://docs.liveavatar.com/docs/quick-start-guide)
- [LiveAvatar API Reference](https://docs.liveavatar.com/docs/api-reference)
- [Custom Avatar Questions](https://docs.liveavatar.com/docs/custom-avatar-questions)

## ✅ Status

- ✅ Backend API endpoints created
- ✅ Frontend service updated
- ✅ Luna.png placeholder displayed
- ✅ Message sending to LiveAvatar
- ⏳ LiveKit Web SDK integration (for actual video stream)
- ⏳ Custom avatar creation from Luna.png video

## 🎉 Next Steps

1. Get your LiveAvatar API key
2. Add it to your `.env` file
3. Test the integration
4. (Optional) Create custom avatar from Luna video footage
5. (Optional) Integrate LiveKit Web SDK for real-time video streaming

