import React, { useState, useEffect, useRef } from 'react';
import { Room, RoomEvent, Track } from 'livekit-client';
import liveAvatarService from '../services/liveavatar';
import { chatService } from '../services/api';
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
  const videoRef = useRef(null);
  const messagesEndRef = useRef(null);
  const roomRef = useRef(null);

  // Initialize UI (Custom Mode will start sessions per message)
  useEffect(() => {
    let isMounted = true;

    const init = async () => {
      if (!isMounted) return;

      try {
        setStatus('Initializing LiveAvatar...');
        setIsInitialized(true);
        setIsSessionActive(true);
        await loadSuggestedQuestions();
        setStatus('LiveAvatar ready - Luna is here!');
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
        if (track.kind === Track.Kind.Video) {
          // Attach video track to the video element
          const element = track.attach();
          if (videoRef.current) {
            // Clear any existing tracks
            videoRef.current.innerHTML = '';
            videoRef.current.appendChild(element);
          }
        } else if (track.kind === Track.Kind.Audio) {
          // Attach audio track for playback
          const element = track.attach();
          document.body.appendChild(element);
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

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
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
            session_id: 'luna-liveavatar-custom-session'
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
        } else {
          // Play audio response if available
          if (result.audio_base64) {
            playAudioResponse(result.audio_base64);
          }
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
    <div className="luna-heygen-interface">
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

          <form onSubmit={handleSubmit} className="input-area">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Type your message..."
              disabled={!isSessionActive}
            />
            <button 
              type="submit" 
              className="send-button"
              disabled={!isSessionActive || !message.trim()}
            >
              <span>Send</span>
            </button>
            {isSessionActive && (
              <button 
                type="button" 
                onClick={handleEndSession}
                className="end-session-btn"
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
