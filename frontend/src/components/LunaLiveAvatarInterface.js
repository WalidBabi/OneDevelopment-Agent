import React, { useState, useEffect, useRef } from 'react';
import { Room, RoomEvent } from 'livekit-client';
import chatService from '../services/api';
import liveAvatarService from '../services/liveavatar';
import './LunaHeyGenInterface.css';

const LunaLiveAvatarInterface = () => {
  const [isInitialized, setIsInitialized] = useState(false);
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [status, setStatus] = useState('Initializing...');
  const [message, setMessage] = useState('');
  const [conversation, setConversation] = useState([]);
  const [liveKitUrl, setLiveKitUrl] = useState(null);
  const [suggestedQuestions, setSuggestedQuestions] = useState([]);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [audioContext, setAudioContext] = useState(null);
  const videoRef = useRef(null);
  const audioRef = useRef(null);
  const messagesEndRef = useRef(null);
  const roomRef = useRef(null);

  // Initialize UI with auto-greeting and proper state management
  useEffect(() => {
    let isMounted = true;

    const init = async () => {
      if (!isMounted) return;

      try {
        setStatus('Initializing LiveAvatar...');
        setIsInitialized(true);
        setIsSessionActive(true);
        await loadSuggestedQuestions();
        setStatus('LiveAvatar ready - Click anywhere to enable audio');
        
        // Auto-start with greeting after a short delay
        setTimeout(async () => {
          if (isMounted) {
            // Check if this is a fresh start (no existing conversation)
            if (conversation.length === 0) {
              await startLiveAvatarSession('Hello! I\'m Luna, your AI assistant from One Development. How can I help you today?');
            }
          }
        }, 1500); // Slightly longer delay for smooth transition
      } catch (error) {
        console.error('Error initializing LiveAvatar:', error);
        setStatus(`Error: ${error.message}`);
        setIsInitialized(true);
        setIsSessionActive(true);
      }
    };

    init();

    return () => {
      if (roomRef.current) {
        roomRef.current.disconnect();
        roomRef.current = null;
      }
      liveAvatarService.endSession();
      isMounted = false;
    };
  }, []);

  // Handle component unmount and cleanup
  useEffect(() => {
    return () => {
      // Clean up any ongoing sessions
      if (roomRef.current) {
        roomRef.current.disconnect();
        roomRef.current = null;
      }
      liveAvatarService.endSession();
    };
  }, []);

  // Handle page refresh and component remount
  useEffect(() => {
    const handleBeforeUnload = () => {
      // Clean up sessions before page unload
      if (roomRef.current) {
        roomRef.current.disconnect();
      }
      liveAvatarService.endSession();
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, []);

  // Load suggested questions
  const loadSuggestedQuestions = async () => {
    try {
      const questions = await chatService.getSuggestedQuestions(4);
      setSuggestedQuestions(questions);
    } catch (error) {
      console.error('Error loading suggested questions:', error);
      // Fallback questions
      setSuggestedQuestions([
        { id: 1, question: "Tell me about One Development" },
        { id: 2, question: "What projects are available?" },
        { id: 3, question: "What are the payment plans?" },
        { id: 4, question: "Where are you located?" }
      ]);
    }
  };

  // Handle suggested question click
  const handleSuggestedQuestionClick = (questionText) => {
    setMessage(questionText);
    // Auto-submit after a brief delay
    setTimeout(() => {
      const form = document.querySelector('.input-area');
      if (form) {
        const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
        form.dispatchEvent(submitEvent);
      }
    }, 100);
  };

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversation]);

  // Initialize audio context on user interaction
  const initializeAudioContext = async () => {
    if (!audioContext) {
      try {
        const context = new (window.AudioContext || window.webkitAudioContext)();
        if (context.state === 'suspended') {
          await context.resume();
        }
        setAudioContext(context);
        console.log('AudioContext initialized and resumed');
        setStatus('LiveAvatar ready - Audio enabled');
      } catch (error) {
        console.error('Error initializing AudioContext:', error);
      }
    }
  };

  // Connect to LiveKit room
  const connectToLiveKit = async (url, token) => {
    try {
      const room = new Room({
        adaptiveStream: true,
        dynacast: true,
      });

      // Set up event listeners for track subscription
      room.on(RoomEvent.TrackSubscribed, (track, publication, participant) => {
        console.log('Track subscribed:', track.kind);
        if (track.kind === 'video') {
          console.log('Attaching video track to element');
          if (videoRef.current) {
            track.attach(videoRef.current);
            videoRef.current.onloadedmetadata = () => {
              console.log('Video element readyState:', videoRef.current.readyState);
              console.log('Video element videoWidth:', videoRef.current.videoWidth);
              console.log('Video element videoHeight:', videoRef.current.videoHeight);
              console.log('Video element paused:', videoRef.current.paused);
            };
          }
        } else if (track.kind === 'audio') {
          console.log('Attaching audio track to element');
          if (audioRef.current) {
            track.attach(audioRef.current);
          }
        }
      });

      room.on(RoomEvent.TrackUnsubscribed, (track, publication, participant) => {
        console.log('Track unsubscribed:', track.kind);
        track.detach();
      });

      room.on(RoomEvent.Disconnected, () => {
        console.log('Disconnected from LiveKit room');
        setLiveKitUrl(null);
        if (videoRef.current) {
          videoRef.current.innerHTML = '';
        }
      });

      // Connect to the room
      await room.connect(url, token);
      roomRef.current = room;
      console.log('Connected to LiveKit room:', room.name);
    } catch (error) {
      console.error('Error connecting to LiveKit:', error);
      setStatus(`LiveKit error: ${error.message}`);
    }
  };

  // Start LiveAvatar session
  const startLiveAvatarSession = async (message) => {
    try {
      // Add user message to conversation if it's not the auto-greeting
      const isAutoGreeting = message.includes("Hello! I'm Luna, your AI assistant from One Development");
      
      if (!isAutoGreeting) {
        const userMessage = { 
          text: message, 
          isUser: true, 
          timestamp: new Date().toISOString() 
        };
        setConversation(prev => [...prev, userMessage]);
      }

      const response = await fetch('http://13.62.188.127:8000/api/liveavatar/chat-custom/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          session_id: 'luna-liveavatar-custom-session',
          voice: 'shimmer',
          avatar_id: '26393b8e-e944-4367-98ef-e2bc75c4b792'  // Use correct Luna avatar ID
        })
      });

      if (!response.ok) {
        throw new Error(`Backend API error: ${response.status}`);
      }

      const result = await response.json();
      
      // Add Luna's response to conversation
      const lunaMessage = {
        text: result.text_response,
        isUser: false,
        timestamp: new Date().toISOString()
      };
      setConversation(prev => [...prev, lunaMessage]);
      
      if (result.livekit_url && result.livekit_token) {
        setLiveKitUrl(result.livekit_url);
        await connectToLiveKit(result.livekit_url, result.livekit_token);
      }
    } catch (error) {
      console.error('Error starting LiveAvatar session:', error);
      throw error;
    }
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Initialize audio context on first user interaction
    if (!audioContext) {
      await initializeAudioContext();
    }
    
    if (!message.trim() || !isSessionActive) return;
    
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
      
      // Scroll to the bottom
      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
      
      // Process the message using LiveAvatar Custom Mode pipeline
      console.log('Processing user message (Custom Mode):', userMessageText);
      setStatus('Thinking...');
      
      try {
        const response = await fetch('http://13.62.188.127:8000/api/liveavatar/chat-custom/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: userMessageText,
            session_id: 'luna-liveavatar-custom-session',
            voice: 'shimmer',
            avatar_id: '26393b8e-e944-4367-98ef-e2bc75c4b792'  // Use correct Luna avatar ID
          })
        });
        
        if (!response.ok) {
          throw new Error(`Backend API error: ${response.status}`);
        }
        
        const result = await response.json();
        const lunaResponse = result.text_response;
        
        console.log('Luna response (Custom Mode):', lunaResponse);
        
        const lunaMessage = {
          text: lunaResponse,
          isUser: false,
          timestamp: new Date().toISOString()
        };
        setConversation(prev => [...prev, lunaMessage]);

        // Store LiveAvatar session and LiveKit info for endSession and streaming
        if (result.session_token && result.session_id) {
          liveAvatarService.sessionToken = result.session_token;
          liveAvatarService.currentSession = result.session_id;
          liveAvatarService.isSessionActive = true;
        }
        if (result.livekit_url && result.livekit_token) {
          liveAvatarService.liveKitUrl = result.livekit_url;
          liveAvatarService.liveKitToken = result.livekit_token;
          await connectToLiveKit(result.livekit_url, result.livekit_token);
          setLiveKitUrl(result.livekit_url);
          setStatus('LiveAvatar streaming...');
        }
        
        // Play OpenAI TTS audio as fallback/backup
        if (result.audio_base64) {
          playAudioResponse(result.audio_base64);
        }
        
        if (!result.livekit_url || !result.livekit_token) {
          setStatus('Ready');
        }
        
      } catch (backendError) {
        console.error('Backend API error:', backendError);
        
        // Fallback response
        const fallbackResponse = "I'm Luna, your AI assistant! I'm using the new LiveAvatar system for better streaming quality.";
        const lunaMessage = {
          text: fallbackResponse,
          isUser: false,
          timestamp: new Date().toISOString()
        };
        setConversation(prev => [...prev, lunaMessage]);
      }
      
      setStatus('Ready');
      
    } catch (error) {
      console.error('Error processing message:', error);
      setStatus(`Error: ${error.message}`);
    }
  };

  // Play audio response
  const playAudioResponse = (audioBase64) => {
    try {
      setIsSpeaking(true);
      const audioData = atob(audioBase64);
      const audioArray = new Uint8Array(audioData.length);
      for (let i = 0; i < audioData.length; i++) {
        audioArray[i] = audioData.charCodeAt(i);
      }
      
      const audioBlob = new Blob([audioArray], { type: 'audio/mpeg' });
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      
      audio.play().catch(error => {
        console.error('Error playing audio:', error);
        setIsSpeaking(false);
      });
      
      // Clean up the URL after playing
      audio.addEventListener('ended', () => {
        URL.revokeObjectURL(audioUrl);
        setIsSpeaking(false);
      });
    } catch (error) {
      console.error('Error processing audio:', error);
      setIsSpeaking(false);
    }
  };

  // End session
  const handleEndSession = async () => {
    try {
      setStatus('Ending session...');
      if (roomRef.current) {
        try {
          roomRef.current.disconnect();
        } catch (e) {
          console.error('Error disconnecting LiveKit room:', e);
        }
        roomRef.current = null;
      }
      await liveAvatarService.endSession();
      setIsSessionActive(false);
      setLiveKitUrl(null);
      setStatus('Session ended');
    } catch (error) {
      console.error('Error ending session:', error);
      setStatus(`Error: ${error.message}`);
    }
  };

  return (
    <div 
      className="luna-heygen-interface"
      onClick={() => {
        if (!audioContext) {
          initializeAudioContext();
        }
      }}
    >
      <div className="interface-header">
        <h2>Luna AI Assistant - LiveAvatar</h2>
        <div className="status-indicator">
          <span className={`status-dot ${isSessionActive ? 'active' : 'inactive'}`}></span>
          <span>{status}</span>
        </div>
      </div>

      <div className="main-content">
        <div className="avatar-section">
          <div className="avatar-container-simple">
            {!liveKitUrl ? (
              <div className="avatar-placeholder">
                <img 
                  src="/Luna.png" 
                  alt="Luna Avatar" 
                  className={`luna-avatar-image static-avatar ${isSpeaking ? 'speaking' : ''}`}
                />
                <div className="avatar-status-indicator">
                  <span className={`status-dot ${isSpeaking ? 'speaking' : 'active'}`}></span>
                  <span>{isSpeaking ? 'Luna is speaking...' : 'Luna is ready'}</span>
                </div>
              </div>
            ) : (
              <video
                ref={videoRef}
                className="luna-avatar-video"
                autoPlay
                playsInline
                muted={false}
              />
            )}
            <audio
              ref={audioRef}
              className="luna-avatar-audio"
              autoPlay
              playsInline
              muted={false}
            />
          </div>
        </div>

        <div className="conversation-container">
          <div className="messages">
            {conversation.length === 0 && suggestedQuestions.length > 0 && (
              <div className="suggested-questions-section">
                <h3 className="suggested-questions-title">Suggested Questions</h3>
                <div className="suggested-questions-grid">
                  {suggestedQuestions.map((q) => (
                    <button
                      key={q.id}
                      className="suggested-question-btn"
                      onClick={() => handleSuggestedQuestionClick(q.question)}
                      disabled={!isSessionActive}
                    >
                      {q.question}
                    </button>
                  ))}
                </div>
              </div>
            )}
            {conversation.map((msg, index) => (
              <div key={index} className={`message ${msg.isUser ? 'user' : 'assistant'}`}>
                <div className="message-content">
                  {msg.text}
                </div>
              </div>
            ))}
            {conversation.length > 0 && suggestedQuestions.length > 0 && (
              <div className="suggested-questions-inline">
                {suggestedQuestions.slice(0, 3).map((q) => (
                  <button
                    key={q.id}
                    className="suggested-question-btn-inline"
                    onClick={() => handleSuggestedQuestionClick(q.question)}
                    disabled={!isSessionActive}
                  >
                    {q.question}
                  </button>
                ))}
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleSubmit} className="input-area-compact">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Type your message..."
              disabled={!isSessionActive}
            />
            <button 
              type="submit" 
              className="send-button-compact"
              disabled={!isSessionActive || !message.trim()}
            >
              <span>Send</span>
            </button>
            {isSessionActive && (
              <button 
                type="button" 
                onClick={handleEndSession}
                className="end-session-btn-compact"
              >
                End Session
              </button>
            )}
          </form>
        </div>
      </div>
    </div>
  );
};

export default LunaLiveAvatarInterface;
