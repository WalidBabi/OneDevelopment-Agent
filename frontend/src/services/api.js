import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatService = {
  sendMessage: async (message, sessionId = null, signal = null) => {
    try {
      const response = await api.post('/chat/', {
        message,
        session_id: sessionId,
      }, {
        signal, // Pass AbortSignal to axios
      });
      return response.data;
    } catch (error) {
      // Don't log as error if it was intentionally cancelled
      if (error.name === 'CanceledError' || error.name === 'AbortError') {
        console.log('Request cancelled by user');
      } else {
        console.error('Error sending message:', error);
      }
      throw error;
    }
  },

  // Streaming chat - shows Luna's thinking in real-time
  sendMessageStream: (message, sessionId, onEvent) => {
    const baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
    
    console.log('[Stream] Starting stream to:', `${baseUrl}/chat/stream/`);
    
    return new Promise((resolve, reject) => {
      fetch(`${baseUrl}/chat/stream/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          session_id: sessionId,
        }),
      }).then(response => {
        console.log('[Stream] Response received, status:', response.status);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let eventCount = 0;
        
        function processStream() {
          reader.read().then(({ done, value }) => {
            if (done) {
              console.log('[Stream] Complete, total events:', eventCount);
              resolve();
              return;
            }
            
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop(); // Keep incomplete line in buffer
            
            for (const line of lines) {
              if (line.startsWith('data: ')) {
                try {
                  const data = JSON.parse(line.slice(6));
                  eventCount++;
                  
                  // Log first few events and phase changes
                  if (eventCount <= 5 || data.type === 'phase' || data.type === 'done') {
                    console.log(`[Stream] Event ${eventCount}:`, data.type, data.phase || data.token?.substring(0, 20) || '');
                  }
                  
                  onEvent(data);
                  
                  if (data.type === 'done') {
                    console.log('[Stream] Done event received');
                    resolve(data);
                  }
                } catch (e) {
                  console.error('[Stream] Error parsing SSE:', e, line);
                }
              }
            }
            
            processStream();
          }).catch(err => {
            console.error('[Stream] Read error:', err);
            reject(err);
          });
        }
        
        processStream();
      }).catch(err => {
        console.error('[Stream] Fetch error:', err);
        reject(err);
      });
    });
  },

  getSuggestedQuestions: async (count = 3) => {
    try {
      const response = await api.get(`/suggested-questions/?count=${count}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching suggested questions:', error);
      throw error;
    }
  },

  getConversationHistory: async (sessionId) => {
    try {
      const response = await api.get(`/conversations/${sessionId}/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching conversation history:', error);
      throw error;
    }
  },

  getAllConversations: async () => {
    try {
      const response = await api.get('/conversations/');
      return response.data;
    } catch (error) {
      console.error('Error fetching conversations:', error);
      throw error;
    }
  },

  deleteConversation: async (sessionId) => {
    try {
      const response = await api.delete(`/conversations/${sessionId}/`);
      return response.data;
    } catch (error) {
      console.error('Error deleting conversation:', error);
      throw error;
    }
  },

  deleteAllConversations: async () => {
    try {
      const response = await api.delete('/conversations/delete-all/');
      return response.data;
    } catch (error) {
      console.error('Error deleting all conversations:', error);
      throw error;
    }
  },

  ingestData: async (source = 'initial') => {
    try {
      const response = await api.post('/ingest-data/', { source });
      return response.data;
    } catch (error) {
      console.error('Error ingesting data:', error);
      throw error;
    }
  },

  healthCheck: async () => {
    try {
      const response = await api.get('/health/');
      return response.data;
    } catch (error) {
      console.error('Error checking health:', error);
      throw error;
    }
  },

  // Avatar service
  generateAvatar: async (text, audioUrl = null, voiceId = 'default', quality = 'fast', signal = null) => {
    try {
      const response = await api.post('/avatar/generate/', {
        text,
        audio_url: audioUrl,
        voice_id: voiceId,
        quality: quality, // 'fast' mode: optimized for speed (10-20s with SadTalker)
      }, {
        signal, // Pass AbortSignal to axios
        timeout: 180000, // 3 minute timeout for video generation
      });
      return response.data;
    } catch (error) {
      // Don't log as error if it was intentionally cancelled
      if (error.name === 'CanceledError' || error.name === 'AbortError') {
        console.log('Avatar generation cancelled by user');
        throw error;
      }
      
      console.error('Error generating avatar:', error);
      // Return fallback info if avatar service is unavailable
      if (error.response?.data?.fallback) {
        return {
          fallback: true,
          error: error.response.data.error,
        };
      }
      throw error;
    }
  },

  avatarHealth: async () => {
    try {
      const response = await api.get('/avatar/health/');
      return response.data;
    } catch (error) {
      console.error('Error checking avatar health:', error);
      return { status: 'unavailable' };
    }
  },

  // Text-to-Speech (OpenAI realistic voices)
  generateTTS: async (text, voice = 'nova') => {
    try {
      console.log(`🎙️ Requesting TTS with voice: ${voice}`);
      const response = await api.post('/tts/generate/', {
        text,
        voice,
      }, {
        responseType: 'blob',  // Important: receive as binary blob
      });
      
      // Log which voice was actually used (from response headers)
      const headers = response.headers;
      const actualVoice = headers['x-tts-voice'] || headers['X-TTS-Voice'] || voice;
      const requestedVoiceId = headers['x-tts-voice-id'] || headers['X-TTS-Voice-ID'] || voice;
      console.log(`✅ TTS Response - Requested: ${requestedVoiceId}, Used: ${actualVoice}`);
      
      // Create a URL for the audio blob
      const audioBlob = new Blob([response.data], { type: 'audio/mpeg' });
      const audioUrl = URL.createObjectURL(audioBlob);
      return { audioUrl, blob: audioBlob };
    } catch (error) {
      console.error('Error generating TTS:', error);
      throw error;
    }
  },

  getTTSVoices: async () => {
    try {
      const response = await api.get('/tts/voices/');
      return response.data;
    } catch (error) {
      console.error('Error fetching TTS voices:', error);
      return { voices: [] };
    }
  },
};

export default api;

