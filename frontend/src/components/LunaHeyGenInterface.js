import React, { useState, useEffect, useRef } from 'react';
import heygenService from '../services/heygen';
import './LunaHeyGenInterface.css';

const LunaHeyGenInterface = () => {
  const [isInitialized, setIsInitialized] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [status, setStatus] = useState('Initializing...');
  const [message, setMessage] = useState('');
  const [conversation, setConversation] = useState([]);
  const [lunaImageKey, setLunaImageKey] = useState(null);
  const videoRef = useRef(null);
  const messagesEndRef = useRef(null);
  const [retryCount, setRetryCount] = useState(0);
  const maxRetries = 3;
  const [currentSession, setCurrentSession] = useState(null);
  const [webSocket, setWebSocket] = useState(null);

  // Setup WebSocket streaming for HeyGen
  const setupWebSocketStreaming = async (sessionData) => {
    try {
      console.log('Setting up WebSocket connection for HeyGen streaming...');
      
      // Create WebSocket connection with token if available
      let wsUrl = sessionData.socket_url;
      if (sessionData.token) {
        wsUrl += `?token=${sessionData.token}`;
      }
      
      const ws = new WebSocket(wsUrl);
      
      ws.onopen = () => {
        console.log('HeyGen WebSocket connected for streaming');
        setStatus('WebSocket connected');
        setWebSocket(ws);
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('HeyGen WebSocket message:', data);
          
          // Handle different message types from HeyGen
          if (data.type === 'video' || data.type === 'media') {
            handleVideoData(data);
          } else if (data.type === 'audio') {
            handleAudioData(data);
          } else if (data.type === 'status') {
            console.log('Status update:', data);
            if (data.status === 'ready') {
              setStatus('Avatar ready');
            }
          } else if (data.type === 'error') {
            console.error('HeyGen error:', data);
            setStatus(`Error: ${data.message}`);
          }
        } catch (error) {
          console.error('Error processing HeyGen WebSocket message:', error);
        }
      };
      
      ws.onerror = (error) => {
        console.error('HeyGen WebSocket error:', error);
        setStatus('Error: WebSocket connection failed');
        setWebSocket(null);
      };
      
      ws.onclose = () => {
        console.log('HeyGen WebSocket connection closed');
        setStatus('Connection closed');
        setWebSocket(null);
      };
      
    } catch (error) {
      console.error('Error setting up HeyGen WebSocket streaming:', error);
      setStatus('Error: Failed to setup streaming');
      throw error;
    }
  };
  
  // Handle video data from HeyGen WebSocket
  const handleVideoData = (data) => {
    console.log('Received video data from HeyGen');
    
    // For HeyGen streaming, we might get video chunks or stream URLs
    if (data.data && data.data.url) {
      // If we get a video URL, set it as the video source
      if (videoRef.current) {
        console.log('Setting video source from HeyGen:', data.data.url);
        videoRef.current.src = data.data.url;
        videoRef.current.play().catch(err => {
          console.error('Error playing HeyGen video:', err);
        });
      }
    } else if (data.data && data.data.chunk) {
      // Handle video chunks (more complex, would require MediaSource API)
      console.log('Received video chunk - requires MediaSource API handling');
    }
  };
  
  // Handle audio data from HeyGen WebSocket
  const handleAudioData = (data) => {
    console.log('Received audio data from HeyGen');
    
    // Similar to video, we might get audio URLs or chunks
    if (data.data && data.data.url) {
      // Create audio element and play
      const audio = new Audio(data.data.url);
      audio.play().catch(err => {
        console.error('Error playing HeyGen audio:', err);
      });
    }
  };

  // Send text to HeyGen avatar via WebSocket
  const sendTextToAvatar = (text) => {
    if (webSocket && webSocket.readyState === WebSocket.OPEN) {
      const message = {
        type: 'text',
        text: text,
        session_id: currentSession?.session_id
      };
      console.log('Sending text to HeyGen avatar:', text);
      webSocket.send(JSON.stringify(message));
    } else {
      console.error('HeyGen WebSocket not available for sending text');
    }
  };

  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      if (webSocket) {
        console.log('Cleaning up HeyGen WebSocket connection...');
        webSocket.close();
        setWebSocket(null);
      }
    };
  }, [webSocket]);

  // Initialize HeyGen streaming session once and reuse
  const initializeStreamingSession = async () => {
    if (currentSession && webSocket && webSocket.readyState === WebSocket.OPEN) {
      console.log('Reusing existing HeyGen streaming session');
      return currentSession;
    }

    try {
      setStatus('Creating streaming session...');
      
      // Clean up existing session if any
      if (webSocket) {
        webSocket.close();
        setWebSocket(null);
      }
      
      const sessionData = await heygenService.createStreamingSession(lunaImageKey);
      console.log('New streaming session created with avatar ID:', lunaImageKey);
      console.log('New streaming session created:', sessionData);
      
      setCurrentSession(sessionData);
      
      // Setup WebSocket connection
      await setupWebSocketStreaming({
        session_id: sessionData.session_id,
        socket_url: sessionData.web_url,
        token: sessionData.token
      });
      
      return sessionData;
    } catch (error) {
      console.error('Failed to initialize streaming session:', error);
      throw error;
    }
  };

  // Handle text-to-speech with HeyGen Streaming
  const speak = async (text) => {
    if (!isInitialized || !lunaImageKey) {
      console.error('HeyGen not initialized or no avatar key');
      setStatus('Error: HeyGen service not ready');
      return;
    }

    try {
      setIsSpeaking(true);
      setStatus('Initializing avatar...');
      
      // Initialize or reuse streaming session
      const sessionData = await initializeStreamingSession();
      
      // Send the text to the avatar
      if (webSocket && webSocket.readyState === WebSocket.OPEN) {
        console.log('Sending text to avatar:', text);
        sendTextToAvatar(text);
        setStatus('Avatar speaking...');
      } else {
        // Wait for connection and then send
        setTimeout(() => {
          if (webSocket && webSocket.readyState === WebSocket.OPEN) {
            sendTextToAvatar(text);
            setStatus('Avatar speaking...');
          }
        }, 2000);
      }
      
      // Add Luna's response to conversation
      const lunaMessage = {
        text: text,
        isUser: false,
        timestamp: new Date().toISOString(),
        sessionId: sessionData.session_id
      };
      setConversation(prev => [...prev, lunaMessage]);
      
      // Scroll to the bottom of the conversation
      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
      
    } catch (error) {
      console.error('Error in speak:', error);
      setStatus(`Error: ${error.message}`);
      
      // Add error message to conversation
      const errorMessage = {
        text: `Sorry, I encountered an error: ${error.message}`,
        isUser: false,
        timestamp: new Date().toISOString(),
        isError: true
      };
      setConversation(prev => [...prev, errorMessage]);
    } finally {
      // Reset speaking status after a delay
      setTimeout(() => {
        setIsSpeaking(false);
        setStatus('Ready');
      }, 3000);
    }
  };

  // Initialize HeyGen service
  useEffect(() => {
    let isMounted = true;
    
    const initHeyGen = async () => {
      if (!isMounted) return;
      
      try {
        setStatus('Initializing Luna Avatar IV...');
        
        // For Avatar IV, we need to:
        // 1. Get default avatar (no upload needed)
        // 2. Fetch available voices (with fallback)
        // 3. Generate videos on demand
        
        // Get default avatar (no upload needed)
        try {
          setStatus('Setting up default avatar...');
          const imageKey = await heygenService.getDefaultAvatar();
          setLunaImageKey(imageKey);
          console.log('Using default avatar key:', imageKey);
        } catch (avatarError) {
          console.error('Failed to get default avatar:', avatarError);
          setStatus('Error: Failed to setup avatar');
          return;
        }
        
        // Fetch available voices with timeout and fallback
        try {
          setStatus('Fetching available voices...');
          const voices = await heygenService.fetchAvailableVoices();
          console.log('Available voices:', voices);
        } catch (voiceError) {
          console.warn('Could not fetch voices, using default voice:', voiceError);
          // Continue with default voice - don't fail initialization
        }
        
        setIsInitialized(true);
        setStatus('Ready');
        
        // Initialize streaming session once at startup
        if (isMounted) {
          setTimeout(async () => {
            try {
              await initializeStreamingSession();
              // Send welcome message after session is ready
              setTimeout(() => {
                if (isInitialized) {
                  speak("Hello! I'm Luna, your AI assistant. How can I help you today?");
                }
              }, 1000);
            } catch (error) {
              console.error('Failed to initialize streaming session:', error);
              setStatus('Ready (streaming unavailable)');
            }
          }, 1000);
        }
        
      } catch (error) {
        console.error('Error initializing HeyGen:', error);
        if (isMounted) {
          setStatus(`Error: ${error.message}`);
        }
      }
    };
    
    initHeyGen();
    
    return () => {
      isMounted = false;
    };
  }, []);

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversation]);

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!message.trim() || isSpeaking) return;
    
    try {
      // Add user message to conversation
      const userMessage = { 
        text: message, 
        isUser: true, 
        timestamp: new Date().toISOString() 
      };
      setConversation(prev => [...prev, userMessage]);
      
      // Clear the input
      const userMessageText = message;
      setMessage('');
      
      // Scroll to the bottom of the conversation
      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
      
      // Process the message using DeepAgent API
      console.log('Processing user message:', userMessageText);
      setStatus('Thinking...');
      
      try {
        // Call the backend chat API to get Luna's response
        const response = await fetch('http://13.62.188.127:8000/api/chat/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: userMessageText,
            session_id: 'luna-avatar-session' // You can make this dynamic
          })
        });
        
        if (!response.ok) {
          throw new Error(`Backend API error: ${response.status}`);
        }
        
        const result = await response.json();
        const lunaResponse = result.response;
        
        console.log('Luna response:', lunaResponse);
        
        // Now use HeyGen only for avatar video generation of the response
        await speak(lunaResponse);
        
      } catch (backendError) {
        console.error('Backend API error:', backendError);
        
        // Fallback to predefined responses if backend is unavailable
        const fallbackResponses = [
          "I'm Luna, your AI assistant. How can I help you today?",
          "That's an interesting question. Let me think about that...",
          "I'm still learning, but I'll do my best to help with that.",
          "Thanks for sharing that with me. Is there anything else you'd like to know?",
          "I'm here to help! Could you tell me more about what you're looking for?"
        ];
        
        const randomResponse = fallbackResponses[Math.floor(Math.random() * fallbackResponses.length)];
        await speak(randomResponse);
      }
      
    } catch (error) {
      console.error('Error processing message:', error);
      setStatus(`Error: ${error.message}`);
    }
  };

  // Handle manual retry
  const handleRetry = () => {
    setRetryCount(0);
    setIsInitialized(false);
    setStatus('Retrying...');
  };

  // Handle voice input
  const toggleListening = () => {
    if (isListening) {
      // Stop listening
      setIsListening(false);
      // Here you would stop the speech recognition
    } else {
      // Start listening
      setIsListening(true);
      // Here you would start the speech recognition
      // For now, we'll simulate voice input after 1 second
      setTimeout(() => {
        const simulatedText = "This is a simulated voice input";
        setMessage(simulatedText);
        setIsListening(false);
        // Auto-submit after voice input
        const event = { preventDefault: () => {} };
        handleSubmit(event);
      }, 1000);
    }
  };

  return (
    <div className="luna-heygen-interface">
      <div className="avatar-container">
        {/* HeyGen Video Feed */}
        <div className="video-feed">
          {isInitialized ? (
            <video
              ref={videoRef}
              className="avatar-video"
              autoPlay
              playsInline
              muted
            />
          ) : (
            <div className="loading-avatar">
              <div className="spinner"></div>
              <p>{status}</p>
              {status.includes('Error') && (
                <button 
                  onClick={handleRetry}
                  className="retry-button"
                  title="Retry connection"
                >
                  Retry
                </button>
              )}
            </div>
          )}
        </div>

        {/* Status Indicator */}
        <div className="status-indicator">
          <span className={`status-dot ${isSpeaking ? 'speaking' : isListening ? 'listening' : 'idle'}`}></span>
          <span className="status-text">
            {isSpeaking ? 'Speaking...' : isListening ? 'Listening...' : status}
          </span>
        </div>
      </div>

      {/* Conversation */}
      <div className="conversation-container">
        <div className="messages">
          {conversation.map((msg, index) => (
            <div key={index} className={`message ${msg.isUser ? 'user' : 'assistant'}`}>
              <div className="message-content">
                {msg.text}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <form onSubmit={handleSubmit} className="input-area">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Type your message..."
            disabled={!isInitialized || isSpeaking}
          />
          <button 
            type="submit" 
            disabled={!isInitialized || isSpeaking || !message.trim()}
            className="send-button"
            title="Send message"
          >
            Send
          </button>
          <button
            type="button"
            onClick={toggleListening}
            className={`voice-button ${isListening ? 'active' : ''}`}
            disabled={!isInitialized || isSpeaking}
            title={isListening ? 'Stop listening' : 'Start voice input'}
          >
            🎤
          </button>
        </form>
      </div>
    </div>
  );
};

export default LunaHeyGenInterface;
