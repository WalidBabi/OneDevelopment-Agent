# Testing LiveAvatar Custom Mode

## Quick Test Instructions

### 1. Start the Backend Server

Make sure the backend server is running:

```bash
cd /home/ec2-user/OneDevelopment-Agent/backend
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

### 2. Test the Endpoint

In another terminal, test the endpoint:

```bash
curl -X POST http://localhost:8000/api/liveavatar/chat-custom/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, I am testing LiveAvatar Custom Mode!",
    "voice": "nova"
  }'
```

### 3. Expected Response

You should get a JSON response like:

```json
{
  "text_response": "Luna's text response from LLM...",
  "audio_url": "/api/avatar/audio/liveavatar_xxx.mp3",
  "audio_base64": "base64-encoded-audio-data...",
  "audio_size": 12345,
  "session_id": "liveavatar-session-id",
  "livekit_url": "wss://livekit-room-url",
  "livekit_token": "livekit-token",
  "session_token": "liveavatar-session-token",
  "avatar_id": "33946dd18761452bb192b38011b177a9",
  "conversation_session_id": "conversation-session-id"
}
```

### 4. Test with Python

```python
import requests
import json

url = "http://localhost:8000/api/liveavatar/chat-custom/"
payload = {
    "message": "Hello, this is a test!",
    "voice": "nova"
}

response = requests.post(url, json=payload)
print(json.dumps(response.json(), indent=2))
```

### 5. Check Server Logs

Watch the server logs to see the processing:
- LLM processing
- TTS generation
- LiveAvatar session creation

## Troubleshooting

### "LIVEAVATAR_API_KEY not configured"
- Check that `LIVEAVATAR_API_KEY` is set in `backend/.env`
- Restart the server after adding it

### "Failed to connect to LiveAvatar API"
- Verify your API key is correct
- Check internet connectivity
- Verify LiveAvatar service is accessible

### "No response from LLM"
- Check that OpenAI API key is configured
- Verify the deepagents system is working
- Check server logs for errors

## Next Steps

Once the endpoint works:
1. Use the `livekit_url` and `livekit_token` to connect via LiveKit SDK
2. Display the avatar video stream
3. Stream the audio to the LiveKit room

See `LIVEAVATAR_CUSTOM_MODE.md` for complete integration examples.



