class LiveAvatarService {
  constructor() {
    this.currentSession = null;
    this.sessionToken = null;
    this.liveKitUrl = null;
    this.liveKitToken = null;
    this.isSessionActive = false;
    this.audioContext = null;
    this.mediaStream = null;
    this.apiBaseUrl = process.env.REACT_APP_API_URL || 'http://13.62.188.127:8000/api';
  }

  // Method to create a session token (Full Mode or Custom Mode)
  async createSessionToken(avatarId = null, mode = 'FULL', voiceId = null, contextId = null) {
    try {
      console.log('Creating LiveAvatar session token...');
      
      const payload = {
        mode: mode,
        avatar_id: avatarId || this.getDefaultAvatarId(),
      };

      if (voiceId) {
        payload.voice_id = voiceId;
      }
      if (contextId) {
        payload.context_id = contextId;
      }

      console.log('Session token payload:', payload);

      const response = await fetch(`${this.apiBaseUrl}/liveavatar/session-token/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
        throw new Error(`Session token failed: ${response.status} - ${errorData.error || 'Unknown error'}`);
      }

      const data = await response.json();
      console.log('Session token created:', data);
      
      this.sessionToken = data.session_token;
      this.currentSession = data.session_id;
      
      return data;
    } catch (error) {
      console.error('Error creating session token:', error);
      throw error;
    }
  }

  // Method to start the session
  async startSession() {
    try {
      console.log('Starting LiveAvatar session...');
      
      if (!this.sessionToken) {
        throw new Error('No session token available. Call createSessionToken() first.');
      }

      const response = await fetch(`${this.apiBaseUrl}/liveavatar/sessions/start/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_token: this.sessionToken
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
        throw new Error(`Session start failed: ${response.status} - ${errorData.error || 'Unknown error'}`);
      }

      const data = await response.json();
      console.log('Session started:', data);
      
      this.liveKitUrl = data.livekit_url;
      this.liveKitToken = data.livekit_token;
      this.isSessionActive = true;
      
      return data;
    } catch (error) {
      console.error('Error starting session:', error);
      throw error;
    }
  }

  // Legacy method names for backward compatibility
  async createCustomSessionToken(avatarId, customLiveKitUrl = null) {
    return this.createSessionToken(avatarId, 'CUSTOM');
  }

  async startCustomSession() {
    return this.startSession();
  }

  // Method to send a message to LiveAvatar (Full Mode)
  async sendMessage(message) {
    try {
      if (!this.isSessionActive || !this.currentSession || !this.sessionToken) {
        throw new Error('No active session. Call startSession() first.');
      }

      console.log('Sending message to LiveAvatar:', message);
      
      const response = await fetch(`${this.apiBaseUrl}/liveavatar/sessions/${this.currentSession}/message/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          session_token: this.sessionToken
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
        throw new Error(`Send message failed: ${response.status} - ${errorData.error || 'Unknown error'}`);
      }

      const result = await response.json();
      console.log('Message sent successfully:', result);
      
      return result;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  }

  // Method to feed audio to LiveAvatar (Custom Mode - for backward compatibility)
  async feedAudioToAvatar(audioBlob) {
    try {
      if (!this.isSessionActive) {
        throw new Error('No active session to feed audio to');
      }

      console.log('Feeding audio to LiveAvatar (Custom Mode)...');
      console.warn('feedAudioToAvatar is deprecated. Use sendMessage() for Full Mode or implement Custom Mode audio streaming.');
      
      // For Custom Mode, you would need to implement WebRTC audio streaming
      // This is a placeholder for backward compatibility
      throw new Error('Custom Mode audio feeding requires WebRTC implementation. Use Full Mode with sendMessage() instead.');
    } catch (error) {
      console.error('Error feeding audio to avatar:', error);
      throw error;
    }
  }

  // Method to convert text to audio (using OpenAI TTS)
  async convertTextToAudio(text) {
    try {
      console.log('Converting text to audio...');
      
      const response = await fetch('http://13.62.188.127:8000/api/tts/generate/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: text,
          voice: 'alloy', // OpenAI voice
          model: 'tts-1'
        }),
      });

      if (!response.ok) {
        throw new Error(`TTS failed: ${response.status}`);
      }

      const audioBlob = await response.blob();
      console.log('Text converted to audio successfully');
      
      return audioBlob;
    } catch (error) {
      console.error('Error converting text to audio:', error);
      throw error;
    }
  }

  // Complete pipeline: Text -> LiveAvatar (Full Mode)
  // For Full Mode, we just send the text message directly
  async processTextWithAvatar(text) {
    try {
      console.log('Processing text with LiveAvatar pipeline...');
      
      // For Full Mode, send message directly to LiveAvatar
      // LiveAvatar handles TTS and avatar rendering automatically
      if (this.isSessionActive) {
        return await this.sendMessage(text);
      } else {
        throw new Error('No active session. Call startSession() first.');
      }
    } catch (error) {
      console.error('Error in text-to-avatar pipeline:', error);
      throw error;
    }
  }

  // Method to get the LiveKit room URL
  getLiveKitRoomUrl() {
    if (!this.liveKitUrl || !this.liveKitToken) {
      throw new Error('Session not started. Call startSession() first.');
    }
    
    // Return the LiveKit URL with token for embedding
    // The frontend can use this with LiveKit SDK or iframe
    return {
      url: this.liveKitUrl,
      token: this.liveKitToken
    };
  }

  // Method to get iframe URL for LiveKit (simplified integration)
  getLiveKitIframeUrl() {
    const roomInfo = this.getLiveKitRoomUrl();
    // Use LiveKit's web client or create a custom iframe URL
    // For now, return a URL that can be used with LiveKit Web SDK
    return roomInfo.url;
  }

  // Method to end the session
  async endSession() {
    try {
      if (this.isSessionActive && this.currentSession && this.sessionToken) {
        const response = await fetch(`${this.apiBaseUrl}/liveavatar/sessions/${this.currentSession}/end/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            session_token: this.sessionToken
          }),
        });

        if (response.ok) {
          console.log('Session ended successfully');
        } else {
          console.warn('Session end returned non-OK status:', response.status);
        }
      }
    } catch (error) {
      console.error('Error ending session:', error);
    } finally {
      this.cleanup();
    }
  }

  // Cleanup method
  cleanup() {
    this.currentSession = null;
    this.sessionToken = null;
    this.liveKitUrl = null;
    this.liveKitToken = null;
    this.isSessionActive = false;
    
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
    
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach(track => track.stop());
      this.mediaStream = null;
    }
  }

  // Get default Luna avatar ID
  // Note: This should be replaced with your actual LiveAvatar avatar ID
  // To create a custom avatar from Luna.png, you need to:
  // 1. Record 2+ minutes of video footage
  // 2. Upload to LiveAvatar to create custom avatar
  // 3. Use the returned avatar_id here
  getDefaultAvatarId() {
    // Default avatar ID - replace with your custom Luna avatar ID after creation
    return '33946dd18761452bb192b38011b177a9';
  }
}

export default new LiveAvatarService();
