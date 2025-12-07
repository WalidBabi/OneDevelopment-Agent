# 🎭 LiveAvatar Custom Mode Integration

This document explains how to use LiveAvatar in **Custom Mode** with your existing OpenAI/deepagents conversation pipeline.

## Overview

**Custom Mode** enables you to:
- Use your existing LLM (OpenAI via deepagents) for conversation
- Convert text to audio using your preferred TTS (OpenAI TTS, Fish Audio, etc.)
- Send audio to LiveAvatar for video generation
- Control the entire conversation flow yourself

## Architecture

```
User Message
    ↓
OpenAI/DeepAgents (Text Response)
    ↓
TTS (Text-to-Speech) → Audio
    ↓
LiveAvatar Custom Mode → Avatar Video
```

## Backend Endpoints

### 1. Complete Pipeline Endpoint

**POST** `/api/liveavatar/chat-custom/`

This endpoint handles the complete pipeline:
1. Processes user message through LLM (deepagents)
2. Converts text response to audio using TTS
3. Creates LiveAvatar Custom Mode session
4. Returns audio + session info

**Request:**
```json
{
  "message": "Hello, I'm Luna!",
  "session_id": "optional-session-id",
  "avatar_id": "33946dd18761452bb192b38011b177a9",
  "voice": "nova",
  "livekit_room_url": "optional-custom-livekit-room",
  "livekit_room_token": "optional-custom-livekit-token"
}
```

**Response:**
```json
{
  "text_response": "Luna's text response",
  "audio_url": "/api/avatar/audio/liveavatar_xxx.mp3",
  "audio_base64": "base64-encoded-audio",
  "audio_size": 12345,
  "session_id": "liveavatar-session-id",
  "livekit_url": "wss://livekit-room-url",
  "livekit_token": "livekit-token",
  "session_token": "liveavatar-session-token",
  "avatar_id": "33946dd18761452bb192b38011b177a9",
  "conversation_session_id": "conversation-session-id"
}
```

### 2. Send Audio to Custom Mode

**POST** `/api/liveavatar/sessions/<session_id>/audio/`

Send audio data to an active LiveAvatar Custom Mode session.

**Request:**
```json
{
  "audio_data": "base64-encoded-audio",
  "session_token": "session-token",
  "format": "mp3"
}
```

## Frontend Usage

### Using the LiveAvatar Service

```javascript
import liveAvatarService from './services/liveavatar';

// Complete pipeline: Chat → Text → TTS → Audio → LiveAvatar
async function chatWithLuna(message) {
  try {
    const result = await liveAvatarService.chatWithCustomMode(
      message,
      'conversation-session-id', // Optional
      null, // avatarId (uses default)
      'nova' // TTS voice
    );

    console.log('Text response:', result.text_response);
    console.log('Audio URL:', result.audio_url);
    console.log('LiveKit URL:', result.livekit_url);
    
    // Get LiveKit connection info
    const livekitInfo = liveAvatarService.getCustomModeLiveKitInfo();
    
    // Connect to LiveKit room and stream audio/video
    // Use LiveKit SDK to connect and send audio track
    
    return result;
  } catch (error) {
    console.error('Error:', error);
  }
}
```

### Complete Pipeline with Auto-Streaming

```javascript
// Process message with automatic audio streaming
const result = await liveAvatarService.processMessageWithCustomMode(
  "Hello, I'm Luna!",
  'session-id',
  {
    avatarId: '33946dd18761452bb192b38011b177a9',
    voice: 'nova',
    autoStreamAudio: true // Automatically stream audio to LiveKit
  }
);
```

### Manual Audio Streaming

```javascript
// Step 1: Get text + audio + session
const chatResult = await liveAvatarService.chatWithCustomMode(message);

// Step 2: Convert base64 audio to blob
const audioBytes = Uint8Array.from(
  atob(chatResult.audio_base64), 
  c => c.charCodeAt(0)
);
const audioBlob = new Blob([audioBytes], { type: 'audio/mpeg' });

// Step 3: Send audio to LiveAvatar
await liveAvatarService.sendAudioToCustomMode(
  audioBlob,
  chatResult.session_id,
  chatResult.session_token
);
```

## LiveKit Integration

To display the avatar video, you need to connect to the LiveKit room using the LiveKit Web SDK:

```javascript
import { Room, RoomEvent, RemoteParticipant } from 'livekit-client';

async function connectToLiveKit(livekitUrl, livekitToken) {
  const room = new Room();
  
  await room.connect(livekitUrl, livekitToken);
  
  room.on(RoomEvent.TrackSubscribed, (track, publication, participant) => {
    if (track.kind === 'video') {
      // Display video track
      const videoElement = document.getElementById('avatar-video');
      track.attach(videoElement);
    }
  });
  
  return room;
}

// Usage
const livekitInfo = liveAvatarService.getCustomModeLiveKitInfo();
const room = await connectToLiveKit(livekitInfo.url, livekitInfo.token);
```

## Configuration Options

### Avatar Selection

You can select from LiveAvatar's catalog of avatars. Each avatar has a unique `avatar_id`.

- Preview avatars: https://liveavatar.com/avatars
- Default Luna avatar: `33946dd18761452bb192b38011b177a9`

### LiveKit Room Configuration

**Option 1: Use LiveAvatar's Default Room** (Recommended)
- Don't provide `livekit_room_url` or `livekit_room_token`
- LiveAvatar creates and manages the room automatically

**Option 2: Use Your Own LiveKit Room**
- Provide `livekit_room_url` and `livekit_room_token`
- LiveAvatar will send the avatar to your existing room

### TTS Voice Options

Available OpenAI TTS voices:
- `nova` - Default, natural female voice (Luna's voice)
- `alloy` - Professional, neutral voice
- `shimmer` - Friendly, warm voice
- `echo` - Male voice
- `fable` - British accent
- `onyx` - Deep male voice

## Environment Variables

Make sure these are set in your backend `.env`:

```bash
# LiveAvatar API Key (required)
LIVEAVATAR_API_KEY=your_api_key_here

# Optional: Custom LiveAvatar API URL
LIVEAVATAR_API_URL=https://api.liveavatar.com

# OpenAI API Key (for TTS)
OPENAI_API_KEY=your_openai_key_here
```

## Example: React Component

```javascript
import React, { useState } from 'react';
import liveAvatarService from '../services/liveavatar';

function LunaCustomModeChat() {
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    setLoading(true);
    try {
      const result = await liveAvatarService.chatWithCustomMode(
        message,
        null, // sessionId
        null, // avatarId (default)
        'nova' // voice
      );
      
      setResponse(result);
      
      // Connect to LiveKit to display avatar
      // (See LiveKit integration above)
      
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Ask Luna..."
      />
      <button onClick={handleSend} disabled={loading}>
        Send
      </button>
      
      {response && (
        <div>
          <p>{response.text_response}</p>
          <audio src={response.audio_url} controls />
        </div>
      )}
    </div>
  );
}
```

## Differences: Full Mode vs Custom Mode

| Feature | Full Mode | Custom Mode |
|---------|-----------|-------------|
| Conversation | LiveAvatar handles | You handle (LLM) |
| TTS | LiveAvatar handles | You handle |
| Audio Generation | LiveAvatar | Your TTS service |
| Video Generation | LiveAvatar | LiveAvatar |
| Control | Less control | Full control |
| Use Case | Quick setup | Custom LLM/TTS |

## Troubleshooting

### "LIVEAVATAR_API_KEY not configured"
- Add `LIVEAVATAR_API_KEY` to your backend `.env` file
- Restart the backend server

### "Failed to connect to LiveAvatar API"
- Check your internet connection
- Verify the API key is correct
- Check if LiveAvatar service is accessible

### Audio not playing
- Verify TTS is working: Check `/api/tts/generate/` endpoint
- Check audio format (should be MP3)
- Verify LiveKit connection is established

### Avatar not appearing
- Connect to LiveKit room using the provided URL and token
- Use LiveKit Web SDK to display video tracks
- Check browser console for WebRTC connection errors

## Next Steps

1. **Install LiveKit SDK** (if not already installed):
   ```bash
   npm install livekit-client
   ```

2. **Create a React component** that uses Custom Mode

3. **Connect to LiveKit room** to display the avatar video

4. **Test the complete pipeline** with a sample message

## Support

- LiveAvatar Documentation: https://docs.liveavatar.com
- LiveKit Documentation: https://docs.livekit.io
- OpenAI TTS Documentation: https://platform.openai.com/docs/guides/text-to-speech


