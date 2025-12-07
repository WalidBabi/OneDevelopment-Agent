import React, { useState, useEffect, useRef } from 'react';
import { Room, RoomEvent } from 'livekit-client';
import { chatService } from '../services/api';
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
  const [showAudioPrompt, setShowAudioPrompt] = useState(false);
  const videoRef = useRef(null);
  const audioRef = useRef(null);
  const roomRef = useRef(null);
  const hasGreetedRef = useRef(false); // Track if greeting has been sent
  const pendingAudioRef = useRef(null); // Store audio to play when avatar is ready

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
        // Send a natural greeting prompt that will be processed by DeepAgents/OpenAI
        setTimeout(async () => {
          if (isMounted && !hasGreetedRef.current) {
            hasGreetedRef.current = true; // Mark as greeted to prevent duplicate
            console.log('🎭 Triggering auto-greeting from Luna...');
            try {
              // Send a greeting that will trigger DeepAgents/OpenAI to generate Luna's natural introduction
              // This will use Luna's system prompt to create an authentic greeting
              await startLiveAvatarSession('Hello');
              console.log('✅ Auto-greeting sent successfully');
            } catch (error) {
              console.error('❌ Error sending auto-greeting:', error);
              // Show a fallback greeting in the conversation
              setConversation([{
                text: "Hello! I'm Luna, your AI research agent for One Development. How can I help you today?",
                isUser: false,
                timestamp: new Date().toISOString()
              }]);
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

  // No longer need scroll functionality with full-screen avatar
  useEffect(() => {
    // Conversation updates - no action needed for full-screen mode
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
        console.log('✅ AudioContext initialized and resumed');
        setStatus('LiveAvatar ready - Audio enabled');
        
        // If there's a pending audio response, try to play it now
        // This helps when audio was blocked due to autoplay policy
      } catch (error) {
        console.error('❌ Error initializing AudioContext:', error);
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
        console.log('Track subscribed:', track.kind, track.id);
        if (track.kind === 'video') {
          console.log('Attaching video track to element');
          if (videoRef.current) {
            track.attach(videoRef.current);
            
            // Ensure video plays when track is attached
            videoRef.current.onloadedmetadata = () => {
              console.log('Video element readyState:', videoRef.current.readyState);
              console.log('Video element videoWidth:', videoRef.current.videoWidth);
              console.log('Video element videoHeight:', videoRef.current.videoHeight);
              console.log('Video element paused:', videoRef.current.paused);
              
              // Explicitly play the video
              if (videoRef.current.paused) {
                videoRef.current.play().catch(err => {
                  console.error('Error playing video:', err);
                });
              }
            };
            
            // Try to play immediately if already loaded
            if (videoRef.current.readyState >= 2) {
              videoRef.current.play().catch(err => {
                console.error('Error playing video (immediate):', err);
              });
            }
            
            // Also handle when video starts playing
            videoRef.current.onplay = () => {
              console.log('✅ Video is now playing');
              setIsSpeaking(true);
            };
            
            videoRef.current.onended = () => {
              console.log('Video playback ended');
              setIsSpeaking(false);
            };
            
            videoRef.current.onerror = (e) => {
              console.error('Video element error:', e);
            };
          }
        } else if (track.kind === 'audio') {
          console.log('Attaching audio track to element');
          if (audioRef.current) {
            track.attach(audioRef.current);
            
            // Ensure audio is not muted and volume is full
            audioRef.current.muted = false;
            audioRef.current.volume = 1.0;
            console.log('🔊 Audio track attached - Volume: 100%, Muted: false');
            
            // Ensure audio plays
            if (audioRef.current.paused) {
              audioRef.current.play().catch(err => {
                console.log('⚠️ Audio autoplay blocked (expected on initial load)');
                console.log('   Audio will play after user interaction');
              });
            }
            
            audioRef.current.onplay = () => {
              console.log('✅ LiveKit audio is now playing!');
              console.log('   🎤 You should hear Luna speaking from the avatar stream');
            };
            
            audioRef.current.onended = () => {
              console.log('Audio playback ended');
            };
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
      console.log('🔑 LiveKit Room Details:');
      console.log('   Room Name (THIS IS THE SESSION):', room.name);
      console.log('   Room SID:', room.sid);
      console.log('   ⚠️ THIS ROOM NAME MUST MATCH THE SESSION ID USED IN WEBSOCKET!');
    } catch (error) {
      console.error('Error connecting to LiveKit:', error);
      setStatus(`LiveKit error: ${error.message}`);
    }
  };

  // Helper to convert AudioBuffer to PCM 16-bit
  const audioBufferToPCM = (audioBuffer) => {
    const channelData = audioBuffer.getChannelData(0); // Mono
    const pcmData = new Int16Array(channelData.length);
    for (let i = 0; i < channelData.length; i++) {
      const s = Math.max(-1, Math.min(1, channelData[i]));
      pcmData[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }
    return pcmData.buffer;
  };

  // Helper to push audio to LiveAvatar via WebSocket for LipSync
  const pushAudioToLiveAvatar = async (audioBase64, wsUrl, sessionId, sessionToken) => {
    if (!sessionToken) {
      console.error('❌ Missing sessionToken for WebSocket connection');
      return;
    }

    // Use LiveKit room name as the actual session for WebSocket
    let actualSessionId = sessionId;
    if (roomRef.current) {
      actualSessionId = roomRef.current.name; // This is the REAL session ID!
      console.log('📡 LiveKit room state:', roomRef.current.state);
      console.log('   Room is connected:', roomRef.current.state === 'connected');
      console.log('   🔑 Using LiveKit Room Name as Session ID:', actualSessionId);
      console.log('   ✅ This ensures video stream matches audio session!');
    } else {
      console.warn('⚠️ No LiveKit room - using backend session ID:', actualSessionId);
    }
    
    // Check video element status
    if (videoRef.current) {
      console.log('📹 Video element before audio push:');
      console.log('   Ready:', videoRef.current.readyState);
      console.log('   Size:', videoRef.current.videoWidth, 'x', videoRef.current.videoHeight);
      console.log('   Playing:', !videoRef.current.paused);
    }

    // Build WebSocket URL using the ACTUAL LiveKit room name
    let targetUrl;
    if (wsUrl) {
      // Use provided URL but replace session ID with actual room name
      targetUrl = wsUrl.replace(/session\/[^\/\?]+/, `session/${actualSessionId}`);
      console.log('📡 Using modified WebSocket URL with correct session:', targetUrl.replace(sessionToken, '***'));
    } else {
      // Fallback: construct URL manually
      targetUrl = `wss://webrtc-signaling.heygen.io/v2-alpha/interactive-avatar/session/${actualSessionId}`;
      console.log('📡 Constructed WebSocket URL:', targetUrl);
    }

    try {
      console.log('🔌 [1/5] Connecting to LiveAvatar WebSocket...');
      console.log('   Using Session ID:', actualSessionId);
      console.log('   (This is the LiveKit room name)');
      console.log('   Has Token:', !!sessionToken);
      
      // Convert Base64 audio to ArrayBuffer
      console.log('🔌 [2/5] Decoding audio data...');
      const audioData = atob(audioBase64);
      const audioArray = new Uint8Array(audioData.length);
      for (let i = 0; i < audioData.length; i++) {
        audioArray[i] = audioData.charCodeAt(i);
      }
      console.log('   Audio data size:', audioArray.length, 'bytes');
      
      // Decode audio (WAV or MP3) to AudioBuffer
      console.log('🔌 [3/5] Converting audio to PCM 24kHz...');
      const targetSampleRate = 24000;
      const tempContext = new (window.AudioContext || window.webkitAudioContext)();
      const decodedBuffer = await tempContext.decodeAudioData(audioArray.buffer);
      console.log('   Original sample rate:', decodedBuffer.sampleRate);
      console.log('   Original duration:', decodedBuffer.duration.toFixed(2), 'seconds');
      
      // Resample to 24kHz using OfflineAudioContext
      const offlineCtx = new OfflineAudioContext(1, decodedBuffer.duration * targetSampleRate, targetSampleRate);
      const source = offlineCtx.createBufferSource();
      source.buffer = decodedBuffer;
      source.connect(offlineCtx.destination);
      source.start();
      const resampledBuffer = await offlineCtx.startRendering();
      console.log('   Resampled to 24kHz, duration:', resampledBuffer.duration.toFixed(2), 'seconds');
      
      // Convert to PCM 16-bit
      const pcmBuffer = audioBufferToPCM(resampledBuffer);
      console.log('   PCM buffer size:', pcmBuffer.byteLength, 'bytes');
      
      // Encode PCM to Base64
      let binary = '';
      const bytes = new Uint8Array(pcmBuffer);
      for (let i = 0; i < bytes.byteLength; i++) {
        binary += String.fromCharCode(bytes[i]);
      }
      const pcmBase64 = btoa(binary);
      console.log('   Base64 PCM size:', pcmBase64.length, 'characters');
      
      // Connect WebSocket
      console.log('🔌 [4/5] Opening WebSocket connection...');
      const ws = new WebSocket(targetUrl);
      
      ws.onopen = () => {
        console.log('✅ [5/5] LiveAvatar WebSocket CONNECTED!');
        console.log('   WebSocket readyState:', ws.readyState);
        console.log('   Session ID:', actualSessionId);
        console.log('   🎥 LiveKit video stream should show avatar speaking after sending audio');
        
        // Send agent.speak event with PCM audio (Custom Mode format)
        const eventId = `speak_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        const speakEvent = {
          type: 'agent.speak',
          event_id: eventId, // Required by LiveAvatar API
          audio: pcmBase64
          // DO NOT include 'text' field - it causes "unknown field" error
        };
        
        console.log('🗣️ Sending agent.speak event...');
        console.log('   Event ID:', eventId);
        console.log('   Audio size:', pcmBase64.length, 'characters');
        console.log('   Payload size:', JSON.stringify(speakEvent).length, 'bytes');
        console.log('   First 50 chars of audio:', pcmBase64.substring(0, 50));
        console.log('   Timestamp:', new Date().toISOString());
        
        ws.send(JSON.stringify(speakEvent));
        console.log('✅ Audio sent to LiveAvatar for lip-sync!');
        console.log('   Waiting for agent.speak_started event...');
        console.log('   🎥 The avatar lips should start moving within 1-2 seconds');
        console.log('   👀 Watch the video carefully for any subtle lip movements');
        
        // Keep connection open for response
        setTimeout(() => {
          console.log('🔌 Closing WebSocket connection');
          ws.close();
        }, 10000);
      };
      
      ws.onerror = (e) => {
        console.error('❌ LiveAvatar WebSocket ERROR:', e);
        console.error('   Connection failed - check URL and authentication');
      };
      
      ws.onmessage = (event) => {
        console.log('📨 LiveAvatar message:', event.data);
        
        try {
          const message = JSON.parse(event.data);
          console.log('   Message type:', message.type);
          console.log('   Event ID:', message.event_id);
          
          // Track audio processing
          if (message.type === 'agent.audio_buffer_appended') {
            console.log('✅ Avatar received and appended audio buffer');
            console.log('   Task ID:', message.task?.id);
            console.log('   🎥 Check video element - avatar should start animating soon');
          }
          
          if (message.type === 'agent.audio_buffer_committed') {
            console.log('✅ Avatar committed audio buffer (ready to speak)');
            console.log('   Task ID:', message.task?.id);
            console.log('   🎥 Avatar should be preparing to animate lips NOW');
          }
          
          // When avatar starts speaking
          if (message.type === 'agent.speak_started') {
            console.log('🎬 Avatar started speaking!');
            console.log('   Task ID:', message.task?.id);
            console.log('   👀 WATCH THE VIDEO - Lips should be moving NOW!');
            console.log('   🔊 Audio should be coming from LiveKit stream');
            console.log('   ⏰ Speak started at:', new Date().toISOString());
            
            // Visual indicator that avatar is speaking
            setStatus('🗣️ Luna is speaking...');
            setIsSpeaking(true);
          }
          
          // Log important state changes
          if (message.type === 'agent.idle_ended') {
            console.log('👁️ Avatar is no longer idle - animation should start');
            setStatus('Luna is speaking...');
          }
          
          if (message.type === 'agent.speak_ended') {
            console.log('✅ Avatar finished speaking');
            console.log('   Task ID:', message.task?.id);
            console.log('   ⏰ Speak ended at:', new Date().toISOString());
            setStatus('Ready');
            setIsSpeaking(false);
          }
          
          if (message.type === 'warning') {
            console.warn('⚠️ LiveAvatar warning:', message.warning);
          }
          
          if (message.type === 'error') {
            console.error('❌ LiveAvatar error:', message.error);
          }
        } catch (e) {
          console.log('   (Non-JSON message, skipping)');
        }
      };
      
      ws.onclose = (e) => {
        console.log('🔌 LiveAvatar WebSocket closed');
        console.log('   Code:', e.code);
        console.log('   Reason:', e.reason || 'No reason provided');
        console.log('   Clean close:', e.wasClean);
      };
      
    } catch (e) {
      console.error('❌ Fatal error in pushAudioToLiveAvatar:', e);
      console.error('   Error details:', e.message);
      console.error('   Stack:', e.stack);
    }
  };

  // Start LiveAvatar session
  const startLiveAvatarSession = async (message) => {
    try {
      // Check if this is an auto-greeting (Luna introducing herself)
      // For auto-greeting, don't show the user's prompt, just Luna's natural response
      // This makes Luna's greeting feel natural, like she's initiating the conversation
      const trimmedMessage = message.toLowerCase().trim();
      const isAutoGreeting = trimmedMessage === 'hello' || 
                             trimmedMessage === 'hi' ||
                             message.includes("Please introduce yourself");
      
      // Only add user message if it's not an auto-greeting
      if (!isAutoGreeting) {
        const userMessage = { 
          text: message, 
          isUser: true, 
          timestamp: new Date().toISOString() 
        };
        setConversation(prev => [...prev, userMessage]);
      }

      console.log('📤 Sending message to LiveAvatar backend:', message);
      setStatus('Processing...');

      // Don't hardcode avatar_id - let backend use the one from .env
      const response = await fetch('http://13.62.188.127:8000/api/liveavatar/chat-custom/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          session_id: 'luna-liveavatar-custom-session',
          voice: 'shimmer'
          // avatar_id will be taken from .env by backend
        })
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Backend API error:', response.status, errorText);
        throw new Error(`Backend API error: ${response.status} - ${errorText}`);
      }

      const result = await response.json();
      
      console.log('📥 Full LiveAvatar response:', result);
      console.log('LiveAvatar response received:', {
        hasText: !!result.text_response,
        textLength: result.text_response?.length || 0,
        hasLiveKitUrl: !!result.livekit_url,
        hasLiveKitToken: !!result.livekit_token,
        hasAudio: !!result.audio_base64,
        audioSize: result.audio_base64?.length || 0,
        textPreview: result.text_response?.substring(0, 100),
        url: result.url,
        realtime_endpoint: result.realtime_endpoint,
        session_id: result.session_id,
        session_token: result.session_token ? '***' : null
      });
      
      // Ensure we have text response - this is critical for the greeting
      const greetingText = result.text_response || 
                          result.response || 
                          "Hello! I'm Luna, your AI research agent for One Development. How can I help you today?";
      
      // Only add text message to conversation if it's NOT an auto-greeting
      // The user wants the avatar to speak the greeting but not show the bubble
      if (!isAutoGreeting) {
        // Add Luna's response to conversation (this is what the user sees)
        const lunaMessage = {
          text: greetingText,
          isUser: false,
          timestamp: new Date().toISOString()
        };
        
        console.log('✅ Adding Luna message to conversation:', greetingText.substring(0, 50) + '...');
        setConversation(prev => [...prev, lunaMessage]);
      } else {
        console.log('🤐 Skipping text bubble for auto-greeting (Audio/Video only)');
      }
      
      // Connect to LiveKit for video streaming
      if (result.livekit_url && result.livekit_token) {
        // Disconnect from previous session first to avoid session mismatch
        if (roomRef.current && roomRef.current.state === 'connected') {
          console.log('⚠️ Disconnecting from OLD LiveKit session:', roomRef.current.name);
          await roomRef.current.disconnect();
          roomRef.current = null;
        }
        
        console.log('Connecting to LiveKit for avatar video...');
        console.log('   NEW Session ID:', result.session_id);
        setLiveKitUrl(result.livekit_url);
        setStatus('Connecting to avatar...');
        await connectToLiveKit(result.livekit_url, result.livekit_token);
        setStatus('Avatar ready - Streaming...');
        
        // Push audio to LiveAvatar - it will handle speaking and streaming back via LiveKit
        console.log('✅ LiveKit connected - Sending audio to LiveAvatar');
        if (result.audio_base64) {
          console.log('🔌 Pushing audio to LiveAvatar for lip-sync...');
          setTimeout(() => {
            // LiveAvatar will animate the avatar and stream audio back via LiveKit
            pushAudioToLiveAvatar(result.audio_base64, result.url || result.realtime_endpoint, result.session_id, result.session_token);
          }, 500); // Wait for LiveKit to fully connect
        }
        
      } else {
        console.warn('No LiveKit URL/token in response, will use static avatar');
        setStatus('Avatar ready');
        
        // Fallback: Play audio locally if no LiveKit stream (no lip-sync available)
        if (result.audio_base64) {
          console.log('🎵 Playing audio without video stream...');
          setTimeout(() => {
            playAudioResponse(result.audio_base64);
          }, 300);
        }
      }
    } catch (error) {
      console.error('❌ Error starting LiveAvatar session:', error);
      
      // Even if there's an error, show a greeting to the user
      const fallbackGreeting = {
        text: "Hello! I'm Luna, your AI research agent for One Development. I'm here to help you with information about our company, projects, and services. How can I assist you today?",
        isUser: false,
        timestamp: new Date().toISOString()
      };
      setConversation(prev => [...prev, fallbackGreeting]);
      setStatus(`Error: ${error.message}. Please try again.`);
      
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
            voice: 'shimmer'
            // avatar_id will be taken from .env by backend
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
          // Disconnect from previous session first to avoid session mismatch
          if (roomRef.current && roomRef.current.state === 'connected') {
            console.log('⚠️ Disconnecting from OLD LiveKit session:', roomRef.current.name);
            await roomRef.current.disconnect();
            roomRef.current = null;
          }
          
          console.log('Connecting to NEW LiveKit session...');
          console.log('   NEW Session ID:', result.session_id);
          liveAvatarService.liveKitUrl = result.livekit_url;
          liveAvatarService.liveKitToken = result.livekit_token;
          await connectToLiveKit(result.livekit_url, result.livekit_token);
          setLiveKitUrl(result.livekit_url);
          setStatus('LiveAvatar streaming...');
          
          // Push audio to LiveAvatar - it will handle speaking and streaming back
          console.log('✅ LiveKit connected - Sending audio to LiveAvatar');
          if (result.audio_base64) {
            console.log('🔌 Pushing audio to LiveAvatar via WebSocket...');
            setTimeout(() => {
              // Let LiveAvatar handle EVERYTHING - audio + video + lip-sync
              pushAudioToLiveAvatar(result.audio_base64, result.url || result.realtime_endpoint, result.session_id, result.session_token);
            }, 500); // Wait for LiveKit to fully connect
          }
          
        } else {
          // Fallback if no LiveKit
          if (result.audio_base64) {
            console.log('🎵 Playing OpenAI TTS audio (local fallback)...');
            playAudioResponse(result.audio_base64);
          }
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
    // Prevent duplicate playback
    if (!audioBase64) {
      console.warn('⚠️ playAudioResponse called with no audio data');
      return;
    }
    
    try {
      console.log('🔊 Playing audio, base64 length:', audioBase64.length);
      setIsSpeaking(true);
      const audioData = atob(audioBase64);
      const audioArray = new Uint8Array(audioData.length);
      for (let i = 0; i < audioData.length; i++) {
        audioArray[i] = audioData.charCodeAt(i);
      }
      
      // Auto-detect audio format (WAV or MP3) from data
      const audioType = audioArray[0] === 0x52 && audioArray[1] === 0x49 ? 'audio/wav' : 'audio/mpeg';
      console.log(`🎵 Audio format detected: ${audioType}`);
      const audioBlob = new Blob([audioArray], { type: audioType });
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      
      // Set volume to maximum
      audio.volume = 1.0;
      
      // Try to play - browsers may block autoplay, so we'll handle the error gracefully
      const playPromise = audio.play();
      
      if (playPromise !== undefined) {
        playPromise
          .then(() => {
            console.log('✅ Audio is playing successfully');
            setStatus('Luna is speaking...');
          })
          .catch(error => {
            console.error('❌ Browser blocked audio autoplay:', error);
            console.log('💡 User interaction required to play audio. Click anywhere on the page.');
            setIsSpeaking(false);
            setShowAudioPrompt(true); // Show visual prompt to user
            setStatus('Click to hear Luna speak');
          });
      }
      
      // Clean up the URL after playing
      audio.addEventListener('ended', () => {
        console.log('✅ Audio playback finished');
        URL.revokeObjectURL(audioUrl);
        setIsSpeaking(false);
        if (!isSpeaking) {
          setStatus('Ready');
        }
      });
      
      audio.addEventListener('error', (e) => {
        console.error('❌ Audio element error:', e);
        setIsSpeaking(false);
      });
    } catch (error) {
      console.error('❌ Error processing audio:', error);
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
        if (showAudioPrompt) {
          setShowAudioPrompt(false);
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
        {/* Audio prompt overlay */}
        {showAudioPrompt && (
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0,0,0,0.7)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            cursor: 'pointer'
          }}>
            <div style={{
              background: '#fff',
              padding: '2rem',
              borderRadius: '10px',
              textAlign: 'center',
              maxWidth: '400px'
            }}>
              <h3 style={{ margin: '0 0 1rem 0', color: '#333' }}>🔊 Click to hear Luna</h3>
              <p style={{ margin: 0, color: '#666' }}>Your browser requires interaction to play audio</p>
            </div>
          </div>
        )}

        {/* Full-screen avatar video */}
        {!liveKitUrl ? (
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
          }}>
            <div style={{ textAlign: 'center', color: 'white' }}>
              <div className="spinner" style={{
                width: '50px',
                height: '50px',
                border: '4px solid rgba(255,255,255,0.3)',
                borderTop: '4px solid white',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite',
                margin: '0 auto 20px'
              }}></div>
              <p style={{ fontSize: '18px', fontWeight: '500' }}>
                {status === 'Initializing LiveAvatar...' ? 'Starting secure session...' : status}
              </p>
            </div>
          </div>
        ) : (
          <>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted={false}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                objectFit: 'cover'
              }}
            />
            {isSpeaking && (
              <div style={{
                position: 'absolute',
                top: '20px',
                right: '20px',
                background: 'rgba(255, 0, 0, 0.9)',
                color: 'white',
                padding: '10px 20px',
                borderRadius: '25px',
                fontSize: '16px',
                fontWeight: 'bold',
                zIndex: 100,
                boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
                backdropFilter: 'blur(10px)'
              }}>
                🎤 SPEAKING
              </div>
            )}
          </>
        )}
        
        <audio
          ref={audioRef}
          autoPlay
          playsInline
          muted={false}
          style={{ display: 'none' }}
        />

        {/* Bottom controls overlay */}
        <div style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          zIndex: 200,
          pointerEvents: 'none'
        }}>
          {/* Suggested questions at bottom */}
          {suggestedQuestions.length > 0 && (
            <div style={{
              display: 'flex',
              gap: '10px',
              padding: '0 20px 10px',
              flexWrap: 'wrap',
              justifyContent: 'center',
              pointerEvents: 'auto'
            }}>
              {suggestedQuestions.slice(0, 4).map((q) => (
                <button
                  key={q.id}
                  onClick={() => handleSuggestedQuestionClick(q.question)}
                  disabled={!isSessionActive}
                  style={{
                    background: 'rgba(255, 255, 255, 0.95)',
                    border: 'none',
                    padding: '10px 20px',
                    borderRadius: '20px',
                    fontSize: '14px',
                    color: '#333',
                    cursor: 'pointer',
                    backdropFilter: 'blur(10px)',
                    boxShadow: '0 2px 10px rgba(0,0,0,0.2)',
                    transition: 'all 0.2s',
                    fontWeight: '500'
                  }}
                  onMouseOver={(e) => {
                    e.target.style.background = 'rgba(255, 255, 255, 1)';
                    e.target.style.transform = 'translateY(-2px)';
                    e.target.style.boxShadow = '0 4px 15px rgba(0,0,0,0.3)';
                  }}
                  onMouseOut={(e) => {
                    e.target.style.background = 'rgba(255, 255, 255, 0.95)';
                    e.target.style.transform = 'translateY(0)';
                    e.target.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
                  }}
                >
                  {q.question}
                </button>
              ))}
            </div>
          )}

          {/* Input form at bottom */}
          <form 
            onSubmit={handleSubmit}
            style={{
              display: 'flex',
              gap: '10px',
              padding: '20px',
              background: 'linear-gradient(180deg, rgba(52, 26, 96, 0.85) 0%, rgba(74, 35, 128, 0.95) 100%)',
              backdropFilter: 'blur(20px)',
              borderTop: '1px solid rgba(150, 107, 252, 0.3)',
              pointerEvents: 'auto'
            }}
          >
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Ask Luna anything..."
              disabled={!isSessionActive}
              style={{
                flex: 1,
                padding: '15px 20px',
                borderRadius: '25px',
                border: 'none',
                fontSize: '16px',
                background: 'rgba(255, 255, 255, 0.95)',
                color: '#333',
                outline: 'none'
              }}
            />
            <button 
              type="submit" 
              disabled={!isSessionActive || !message.trim()}
              style={{
                padding: '15px 30px',
                borderRadius: '25px',
                border: 'none',
                background: 'linear-gradient(135deg, #341a60 0%, #966bfc 100%)',
                color: 'white',
                fontSize: '16px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.2s',
                opacity: (!isSessionActive || !message.trim()) ? 0.5 : 1
              }}
            >
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default LunaLiveAvatarInterface;
