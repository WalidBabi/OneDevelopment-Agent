import { v4 as uuidv4 } from 'uuid';

// Debug environment variables
console.log('Environment variables:', {
  REACT_APP_HEYGEN_API_KEY: process.env.REACT_APP_HEYGEN_API_KEY ? '***' : 'Not set',
  REACT_APP_HEYGEN_AVATAR_ID: process.env.REACT_APP_HEYGEN_AVATAR_ID ? '***' : 'Not set'
});

// Hardcoded values from your .env.local file
const HEYGEN_API_KEY = 'sk_V2_hgu_kJF0dzYXUXD_KkIYxjBhIQKfPa2yE7ScO4vCNIrAuQCT';
const HEYGEN_AVATAR_ID = 'luna'; // Try using 'luna' as the avatar name

console.log('Using HeyGen API Key:', HEYGEN_API_KEY ? '***' : 'Not set');
console.log('Using HeyGen Avatar ID:', HEYGEN_AVATAR_ID || 'Not set');

if (!HEYGEN_API_KEY || !HEYGEN_AVATAR_ID) {
  console.error('HeyGen API key or Avatar ID not found. Please set REACT_APP_HEYGEN_API_KEY and REACT_APP_HEYGEN_AVATAR_ID environment variables.');
  throw new Error('Missing HeyGen API credentials');
}

const HEYGEN_API_URL = 'https://api.heygen.com/v1';

class HeyGenService {
  constructor() {
    this.currentSession = null;
    this.isCreatingSession = false;
    this.sessionId = null;
    this.socket = null;
    this.messageCallbacks = new Map();
    this.availableVoices = [];
    this.connectionStatus = 'disconnected';
  }

  // Method to upload Luna's image to HeyGen
  async uploadImage(imageFile) {
    try {
      console.log('Uploading Luna image...');
      const formData = new FormData();
      formData.append('file', imageFile);
      formData.append('file_purpose', 'avatar');

      const response = await fetch(`${HEYGEN_API_URL}/asset/upload`, {
        method: 'POST',
        headers: {
          'X-Api-Key': HEYGEN_API_KEY,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Upload error:', errorText);
        throw new Error(`Upload failed: ${response.status}`);
      }

      const data = await response.json();
      console.log('Image uploaded successfully:', data);
      return data.data.file_id; // This will be the image_key
    } catch (error) {
      console.error('Error uploading image:', error);
      throw error;
    }
  }

  // Method to create streaming session (works with free/basic plans)
  async createStreamingSession(avatarId, voiceId) {
    try {
      console.log('Creating HeyGen streaming session...');
      console.log('Received avatarId:', avatarId);
      
      // Ensure we have a valid avatar ID
      if (!avatarId) {
        console.log('No avatarId provided, using default Luna avatar');
        avatarId = '33946dd18761452bb192b38011b177a9'; // Luna avatar ID
      }
      
      // Prevent rapid session creation
      if (this.sessionCreationInProgress) {
        console.log('Session creation already in progress, waiting...');
        return null;
      }
      
      this.sessionCreationInProgress = true;
      
      // Clean up existing session if any
      if (this.currentSession) {
        console.log('Cleaning up existing session...');
        this.currentSession = null;
      }
      
      // Use the real voice ID from your available voices
      const defaultVoiceId = voiceId || '0c418eab508d4030879c0c3381433806'; // Juniper voice
      
      const payload = {
        quality: 'high',
        avatar_id: avatarId,  // Use avatar_id as per the API documentation
        voice: {
          voice_id: defaultVoiceId,
          speed: 1.0,
          pitch: 0,
          style: 'conversational',
          stability: 0.5,
          emotion: 'happy',
          emphasis: 0.5
        },
        background: {
          type: 'color',
          value: '#f0f2f5'
        },
        camera: {
          position: 'front',
          field_of_view: 45
        }
      };

      console.log('Sending payload to HeyGen:', payload);

      const response = await fetch('http://13.62.188.127:8000/api/heygen-streaming/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      this.isCreatingSession = false;

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Streaming session error:', errorText);
        
        // Handle concurrent limit error
        if (errorText.includes('Concurrent limit reached')) {
          console.log('Concurrent limit reached, waiting...');
          await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2 seconds
          // Retry once
          return this.createStreamingSession(avatarId, voiceId);
        }
        
        throw new Error(`Streaming session failed: ${response.status}`);
      }

      const data = await response.json();
      console.log('Streaming session created:', data);
      this.currentSession = data.data;
      return data.data;
    } catch (error) {
      this.isCreatingSession = false;
      this.sessionCreationInProgress = false;
      console.error('Error creating streaming session:', error);
      throw error;
    }
  }

  // Method to check video generation status
  async getVideoStatus(videoId) {
    try {
      const response = await fetch(`${HEYGEN_API_URL}/v2/video/${videoId}/status`, {
        method: 'GET',
        headers: {
          'X-Api-Key': HEYGEN_API_KEY,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to get video status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Video status:', data);
      return data;
    } catch (error) {
      console.error('Error getting video status:', error);
      throw error;
    }
  }

  // Method to get a default HeyGen avatar (no upload needed)
  async getDefaultAvatar() {
    try {
      console.log('Using default HeyGen avatar...');
      
      // Use the real Luna avatar ID provided
      const defaultAvatarId = '33946dd18761452bb192b38011b177a9'; // Luna avatar ID
      
      console.log('Using default avatar ID:', defaultAvatarId);
      return defaultAvatarId;
    } catch (error) {
      console.error('Error getting default avatar:', error);
      // Fallback to a simple name that might work
      return 'luna';
    }
  }

  // Method to fetch available voices (V2 API via backend proxy)
  async fetchAvailableVoices() {
    try {
      console.log('Fetching available voices from HeyGen V2 API via backend...');
      
      // Add timeout to prevent hanging
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
      
      const response = await fetch('http://13.62.188.127:8000/api/heygen-voices/', {
        method: 'GET',
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Error response:', errorText);
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Voices V2 API response:', data);
      
      // Handle V2 response format
      if (data.data && Array.isArray(data.data.voices)) {
        this.availableVoices = data.data.voices;
      } else if (Array.isArray(data.voices)) {
        this.availableVoices = data.voices;
      } else if (Array.isArray(data)) {
        this.availableVoices = data;
      } else {
        console.warn('Unexpected voices V2 response format, using default voice');
        return [{ voice_id: '1bd00e16e4f646c89433d927c865a5b3', name: 'Default Voice' }];
      }

      console.log('Available voices:', this.availableVoices);
      return this.availableVoices;
    } catch (error) {
      console.error('Error fetching voices:', error);
      return [{ voice_id: '1bd00e16e4f646c89433d927c865a5b3', name: 'Default Voice' }];
    }
  }

  // Method to get avatar info (to help find Luna)
  async getAvatarInfo() {
    try {
      console.log('Getting avatar info for:', HEYGEN_AVATAR_ID);
      const response = await fetch(`${HEYGEN_API_URL}/avatar/${HEYGEN_AVATAR_ID}/info`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-Api-Key': HEYGEN_API_KEY,
        },
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Avatar info error:', errorText);
        return null;
      }

      const data = await response.json();
      console.log('Avatar info:', data);
      return data;
    } catch (error) {
      console.error('Error getting avatar info:', error);
      return null;
    }
  }

  // Method to list all avatars to help find Luna
  async listAvatars() {
    try {
      console.log('Listing all avatars...');
      const response = await fetch(`${HEYGEN_API_URL}/avatar.v2.list`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-Api-Key': HEYGEN_API_KEY,
        },
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Error listing avatars:', errorText);
        return null;
      }

      const data = await response.json();
      console.log('All avatars:', data);
      
      // Look for Luna in the list
      if (data.data && data.data.avatars) {
        const lunaAvatar = data.data.avatars.find(a => 
          a.name.toLowerCase().includes('luna') || 
          a.avatar_id.toLowerCase().includes('luna')
        );
        if (lunaAvatar) {
          console.log('Found Luna avatar:', lunaAvatar);
          return lunaAvatar;
        }
      }
      
      return data;
    } catch (error) {
      console.error('Error listing avatars:', error);
      return null;
    }
  }

  async createSession() {
    try {
      console.log('Creating HeyGen session with API Key:', HEYGEN_API_KEY ? '***' : 'Not set');
      console.log('Using Avatar ID:', HEYGEN_AVATAR_ID);
      
      // Try to fetch available voices first
      if (this.availableVoices.length === 0) {
        try {
          await this.fetchAvailableVoices();
        } catch (voiceError) {
          console.warn('Could not fetch voices, using default voice:', voiceError);
        }
      }
      
      // Use the first available voice or fallback to default
      const voiceId = this.availableVoices[0]?.voice_id || '1bd00e16e4f646c89433d927c865a5b3';
      
      // Simple request body with minimal required fields
      const requestBody = {
        quality: 'high',
        avatar_id: HEYGEN_AVATAR_ID,
        voice: {
          voice_id: voiceId,
          emotion: 'Friendly',
          rate: 1.0
        },
        video_encoding: 'VP8',
        disable_idle_timeout: false,
        activity_idle_timeout: 300 // 5 minutes
      };

      console.log('Sending request to HeyGen API:', JSON.stringify(requestBody, null, 2));
      
      const response = await fetch(`${HEYGEN_API_URL}/streaming.new`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Api-Key': HEYGEN_API_KEY,
        },
        body: JSON.stringify(requestBody),
      });

      const responseData = await response.json();
      console.log('Session creation response:', responseData);

      if (!response.ok) {
        // Provide more detailed error information
        const errorDetail = responseData.error || responseData.message || 'Unknown error';
        throw new Error(`${response.status}: ${errorDetail}`);
      }

      if (responseData.code !== 0) {
        throw new Error(responseData.message || 'Failed to create session');
      }

      this.sessionId = responseData.data.session_id;
      console.log('Session created successfully:', this.sessionId);
      
      // Connect to WebSocket
      await this.connectWebSocket(responseData.data.socket_url);
      return this.sessionId;
    } catch (error) {
      console.error('Error creating HeyGen session:', error);
      throw error;
    }
  }

  async connectWebSocket(socketUrl) {
    return new Promise((resolve, reject) => {
      try {
        console.log('Connecting to WebSocket:', socketUrl);
        this.connectionStatus = 'connecting';
        this.socket = new WebSocket(socketUrl);

        this.socket.onopen = () => {
          console.log('WebSocket connected');
          this.connectionStatus = 'connected';
          resolve();
        };

        this.socket.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.connectionStatus = 'error';
          reject(new Error('Failed to connect to WebSocket'));
        };

        this.socket.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            console.log('WebSocket message:', message);
            
            // Handle different message types
            if (message.type === 'response') {
              const callback = this.messageCallbacks.get(message.id);
              if (callback) {
                callback(message);
                this.messageCallbacks.delete(message.id);
              }
            } else if (message.type === 'status') {
              console.log('Status update:', message.data);
              // Handle status updates if needed
            } else if (message.type === 'error') {
              console.error('WebSocket error message:', message.data);
              const callback = this.messageCallbacks.get(message.id);
              if (callback) {
                callback.reject(new Error(message.data));
                this.messageCallbacks.delete(message.id);
              }
            }
          } catch (error) {
            console.error('Error processing WebSocket message:', error);
          }
        };

        this.socket.onclose = (event) => {
          console.log('WebSocket disconnected:', event.code, event.reason);
          this.connectionStatus = 'disconnected';
          if (event.code !== 1000) { // 1000 is normal closure
            console.warn('WebSocket connection closed unexpectedly');
          }
        };
      } catch (error) {
        console.error('Error creating WebSocket:', error);
        this.connectionStatus = 'error';
        reject(error);
      }
    });
  }

  close() {
    if (this.socket) {
      console.log('Closing WebSocket connection...');
      this.socket.close(1000, 'Connection closed by client');
      this.socket = null;
    }
    this.sessionId = null;
    this.messageCallbacks.clear();
    this.connectionStatus = 'disconnected';
  }

  getConnectionStatus() {
    return this.connectionStatus;
  }

  async sendTextToSpeech(text) {
    if (!this.sessionId || !this.socket || this.socket.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket connection not ready');
    }

    try {
      const messageId = uuidv4();
      const message = {
        type: 'text',
        text: text,
        id: messageId
      };

      console.log('Sending text to speech:', text);
      this.socket.send(JSON.stringify(message));

      // Wait for response
      return new Promise((resolve, reject) => {
        const timeout = setTimeout(() => {
          this.messageCallbacks.delete(messageId);
          reject(new Error('Speech generation timeout'));
        }, 30000); // 30 second timeout

        this.messageCallbacks.set(messageId, {
          resolve: (response) => {
            clearTimeout(timeout);
            resolve(response);
          },
          reject: (error) => {
            clearTimeout(timeout);
            reject(error);
          }
        });
      });
    } catch (error) {
      console.error('Error sending text to speech:', error);
      throw error;
    }
  }

  handleIncomingMessage(message) {
    const { message_id, type, data } = message;
    
    if (message_id && this.messageCallbacks.has(message_id)) {
      const { resolve, reject } = this.messageCallbacks.get(message_id);
      this.messageCallbacks.delete(message_id);
      
      if (type === 'error') {
        reject(new Error(data || 'Unknown error'));
      } else {
        resolve(data);
      }
    }

    // Handle other message types (e.g., avatar events, status updates)
    switch (type) {
      case 'avatar_ready':
        console.log('Avatar is ready to speak');
        break;
      case 'speech_start':
        console.log('Avatar started speaking');
        break;
      case 'speech_end':
        console.log('Avatar finished speaking');
        break;
      default:
        console.log('Unhandled message type:', type, message);
    }
  }

  async sendText(text) {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket is not connected');
    }

    const messageId = uuidv4();
    const message = {
      message_id: messageId,
      type: 'text',
      data: {
        text,
        session_id: this.sessionId,
      },
    };

    return new Promise((resolve, reject) => {
      this.messageCallbacks.set(messageId, { resolve, reject });
      this.socket.send(JSON.stringify(message));
      
      // Set a timeout to clean up if no response is received
      setTimeout(() => {
        if (this.messageCallbacks.has(messageId)) {
          this.messageCallbacks.delete(messageId);
          reject(new Error('Request timed out'));
        }
      }, 30000); // 30 seconds timeout
    });
  }

  async close() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
      this.sessionId = null;
    }
  }
}

export const heygenService = new HeyGenService();
export default heygenService;
