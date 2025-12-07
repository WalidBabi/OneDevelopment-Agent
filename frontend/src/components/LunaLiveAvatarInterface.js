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
  const [isProcessing, setIsProcessing] = useState(false);
  const [estimatedTime, setEstimatedTime] = useState(0);
  const videoRef = useRef(null);
  const audioRef = useRef(null);
  const roomRef = useRef(null);
  const hasGreetedRef = useRef(false); // Track if greeting has been sent
  const pendingAudioRef = useRef(null); // Store audio to play when avatar is ready
  const sessionTokenRef = useRef(null); // Store session token to reuse
  const sessionIdRef = useRef(null); // Store session ID to reuse
  const wsUrlRef = useRef(null); // Store WebSocket URL to reuse
  const currentAvatarIdRef = useRef(null); // Track current avatar ID
  const wsRef = useRef(null); // Store active WebSocket connection
  const wsTimeoutRef = useRef(null); // Store WebSocket timeout reference
  const isSpeakingRef = useRef(false); // Track if avatar has started speaking
  const audioSentRef = useRef(false); // Track if audio was successfully sent
  const expectedDurationRef = useRef(0); // Store expected audio duration
  const audioWorkerRef = useRef(null); // Web Worker for audio processing
  const streamingResponseRef = useRef(''); // Accumulate streaming response

  // Initialize Web Worker for audio processing
  useEffect(() => {
    // Create Web Worker for audio processing
    if (typeof Worker !== 'undefined') {
      try {
        audioWorkerRef.current = new Worker('/audioWorker.js');
        audioWorkerRef.current.onmessage = (e) => {
          const { type, pcmBase64, duration, error, message } = e.data;
          if (type === 'audioProcessed') {
            console.log('✅ Audio processed in Web Worker:', { duration, size: e.data.size });
            // Use processed PCM audio if pending
            if (pendingAudioRef.current && pcmBase64) {
              pendingAudioRef.current.pcmBase64 = pcmBase64;
              pendingAudioRef.current.duration = duration;
              // Push audio with processed PCM
              pushAudioToLiveAvatar(
                pendingAudioRef.current.audioBase64,
                pendingAudioRef.current.wsUrl,
                pendingAudioRef.current.sessionId,
                pendingAudioRef.current.sessionToken,
                pcmBase64,
                duration
              );
            }
          } else if (type === 'error') {
            console.warn('⚠️ Web Worker error:', message);
          }
        };
        console.log('✅ Web Worker initialized for audio processing');
      } catch (error) {
        console.warn('⚠️ Web Worker not available:', error);
      }
    }

    return () => {
      if (audioWorkerRef.current) {
        audioWorkerRef.current.terminate();
        audioWorkerRef.current = null;
      }
    };
  }, []);

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
            
            // Start muted to comply with autoplay policy
            audioRef.current.muted = false;
            audioRef.current.volume = 1.0;
            console.log('🔊 Audio track attached - Volume: 100%, Muted: false');
            
            // Try to play audio - if blocked, show prompt
            if (audioRef.current.paused) {
              audioRef.current.play().catch(err => {
                console.log('⚠️ Audio autoplay blocked - showing user prompt');
                setShowAudioPrompt(true);
                // Audio will be enabled after user interaction
              });
            }
            
            audioRef.current.onplay = () => {
              console.log('✅ LiveKit audio is now playing!');
              console.log('   🎤 You should hear Luna speaking from the avatar stream');
              setShowAudioPrompt(false);
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
  const pushAudioToLiveAvatar = async (audioBase64, wsUrl, sessionId, sessionToken, audioPcmBase64 = null, audioDuration = null) => {
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
      
      let pcmBase64;
      let finalAudioDuration = audioDuration; // Use provided duration if available
      
      // OPTIMIZATION: Use pre-processed PCM if available (saves 0.5-1.5s)
      if (audioPcmBase64) {
        console.log('⚡ Using pre-processed PCM from backend (skipping frontend processing)');
        console.log('   This saves ~0.5-1.5s of processing time!');
        pcmBase64 = audioPcmBase64;
        console.log('   Base64 PCM size:', pcmBase64.length, 'characters');
        if (finalAudioDuration) {
          console.log(`   Audio duration: ${finalAudioDuration.toFixed(2)}s`);
        }
      } else {
        // Fallback: Process audio on frontend (original method)
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
        const processedAudioDuration = decodedBuffer.duration; // Capture duration for WebSocket timeout
        console.log('   Original sample rate:', decodedBuffer.sampleRate);
        console.log('   Original duration:', processedAudioDuration.toFixed(2), 'seconds');
        
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
        
        // Encode PCM to Base64 for WebSocket transmission
        const pcmBytes = new Uint8Array(pcmBuffer);
        
        // Use FileReader API for reliable base64 encoding of large arrays
        pcmBase64 = await new Promise((resolve, reject) => {
          const blob = new Blob([pcmBytes], { type: 'application/octet-stream' });
          const reader = new FileReader();
          
          reader.onload = () => {
            const dataUrl = reader.result;
            const base64 = dataUrl.split(',')[1];
            resolve(base64);
          };
          
          reader.onerror = () => {
            reject(new Error('Failed to encode PCM to base64'));
          };
          
          reader.readAsDataURL(blob);
        });
        
        console.log('   Base64 PCM size:', pcmBase64.length, 'characters');
        finalAudioDuration = processedAudioDuration; // Store duration from processing
      }
      
      // OPTIMIZATION: Open WebSocket connection early (parallel with audio processing if needed)
      console.log('🔌 [4/5] Opening WebSocket connection...');
      
      // Close any existing WebSocket connection
      if (wsRef.current && wsRef.current.readyState !== WebSocket.CLOSED) {
        console.log('   Closing previous WebSocket connection');
        wsRef.current.close();
      }
      if (wsTimeoutRef.current) {
        clearTimeout(wsTimeoutRef.current);
        wsTimeoutRef.current = null;
      }
      
      isSpeakingRef.current = false; // Reset speaking flag for new connection
      audioSentRef.current = false; // Reset audio sent flag
      expectedDurationRef.current = 0; // Reset expected duration
      
      // Open WebSocket connection immediately (don't wait for audio processing)
      // This allows connection to establish in parallel with any remaining processing
      const ws = new WebSocket(targetUrl);
      
      // Store WebSocket reference immediately for potential early use
      wsRef.current = ws;
      
      ws.onopen = () => {
        console.log('✅ [5/5] LiveAvatar WebSocket CONNECTED!');
        console.log('   WebSocket readyState:', ws.readyState);
        console.log('   Session ID:', actualSessionId);
        console.log('   🎥 LiveKit video stream should show avatar speaking after sending audio');
        
        const eventId = `speak_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        // According to LiveAvatar docs: Send audio in chunks under 1MB to avoid connection closure
        const MAX_CHUNK_SIZE = 800000; // ~800KB base64 chars (safe margin under 1MB)
        const audioLength = pcmBase64.length;
        
        if (audioLength > MAX_CHUNK_SIZE) {
          // Split audio into chunks
          const numChunks = Math.ceil(audioLength / MAX_CHUNK_SIZE);
          console.log(`📦 Audio is large (${audioLength} chars) - splitting into ${numChunks} chunks`);
          console.log(`   Each chunk: ~${MAX_CHUNK_SIZE} characters (under 1MB limit)`);
          
          // Send first chunk with initial speak event
          let chunkIndex = 0;
          const firstChunk = pcmBase64.substring(0, MAX_CHUNK_SIZE);
          const firstEvent = {
            type: 'agent.speak',
            event_id: eventId,
            audio: firstChunk
          };
          
          try {
            ws.send(JSON.stringify(firstEvent));
            console.log(`✅ Sent chunk ${chunkIndex + 1}/${numChunks} (${firstChunk.length} chars)`);
            chunkIndex++;
            
            // Send remaining chunks as sequential agent.speak events
            // Each chunk is a continuation of the previous one (same event_id)
            const sendNextChunk = () => {
              if (chunkIndex < numChunks && ws.readyState === WebSocket.OPEN) {
                const start = chunkIndex * MAX_CHUNK_SIZE;
                const end = Math.min(start + MAX_CHUNK_SIZE, audioLength);
                const chunk = pcmBase64.substring(start, end);
                
                // Use agent.speak for all chunks (not a custom event type)
                // Same event_id groups them together
                const chunkEvent = {
                  type: 'agent.speak',
                  event_id: eventId,
                  audio: chunk
                };
                
                try {
                  ws.send(JSON.stringify(chunkEvent));
                  console.log(`✅ Sent chunk ${chunkIndex + 1}/${numChunks} (${chunk.length} chars)`);
                  chunkIndex++;
                  
                  // Small delay between chunks to prevent overwhelming the server
                  setTimeout(sendNextChunk, 50); // 50ms delay
                } catch (chunkError) {
                  console.error(`❌ Failed to send chunk ${chunkIndex + 1}:`, chunkError);
                  // Continue with next chunk anyway
                  chunkIndex++;
                  setTimeout(sendNextChunk, 100);
                }
              } else if (chunkIndex >= numChunks) {
                console.log('✅ All audio chunks sent to LiveAvatar for lip-sync!');
                // Send speak_end event to signal completion
                try {
                  const speakEndEvent = {
                    type: 'agent.speak_end',
                    event_id: eventId
                  };
                  ws.send(JSON.stringify(speakEndEvent));
                  console.log('✅ Sent agent.speak_end event');
                } catch (endError) {
                  console.warn('⚠️ Failed to send speak_end event:', endError);
                }
                audioSentRef.current = true;
              }
            };
            
            // Start sending remaining chunks after a short delay
            setTimeout(sendNextChunk, 100);
          } catch (firstChunkError) {
            console.error('❌ Failed to send first chunk:', firstChunkError);
            audioSentRef.current = false;
          }
        } else {
          // Small audio - send in one message
          const speakEvent = {
            type: 'agent.speak',
            event_id: eventId,
            audio: pcmBase64
          };
          
          console.log('🗣️ Sending agent.speak event...');
          console.log('   Event ID:', eventId);
          console.log('   Audio size:', pcmBase64.length, 'characters');
          console.log('   Payload size:', JSON.stringify(speakEvent).length, 'bytes');
          
          try {
            ws.send(JSON.stringify(speakEvent));
            console.log('✅ Audio sent to LiveAvatar for lip-sync!');
            audioSentRef.current = true;
          } catch (sendError) {
            console.error('❌ Failed to send audio via WebSocket:', sendError);
            audioSentRef.current = false;
          }
        }
        
        console.log('   Waiting for agent.speak_started event...');
        console.log('   🎥 The avatar lips should start moving within 1-2 seconds');
        console.log('   👀 Watch the video carefully for any subtle lip movements');
        
        // Store WebSocket reference for cleanup
        wsRef.current = ws;
        
        // Track expected duration
        const expectedDuration = Math.max(10, (finalAudioDuration || 10) + 5);
        expectedDurationRef.current = expectedDuration * 1000; // Store in milliseconds
        console.log(`   ⏱️ Expected response duration: ${expectedDuration.toFixed(1)}s`);
        console.log('   🔄 WebSocket will stay open until avatar finishes speaking');
        
        // Set a very long fallback timeout (5 minutes) as a safety net
        // This should never trigger if everything works correctly
        if (wsTimeoutRef.current) {
          clearTimeout(wsTimeoutRef.current);
        }
        wsTimeoutRef.current = setTimeout(() => {
          console.warn('⚠️ Fallback timeout reached - closing WebSocket after 5 minutes');
          if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.close();
          }
          wsRef.current = null;
          wsTimeoutRef.current = null;
          setIsProcessing(false);
          setEstimatedTime(0);
        }, 5 * 60 * 1000); // 5 minutes fallback
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
            isSpeakingRef.current = true; // Track that speaking has started
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
            setIsProcessing(false);
            setEstimatedTime(0);
            isSpeakingRef.current = false; // Clear speaking flag
            audioSentRef.current = false; // Reset audio sent flag
            expectedDurationRef.current = 0; // Reset expected duration
            
            // Close WebSocket now that avatar has finished speaking
            if (wsTimeoutRef.current) {
              clearTimeout(wsTimeoutRef.current);
              wsTimeoutRef.current = null;
            }
            if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
              console.log('🔌 Closing WebSocket connection (avatar finished speaking)');
              wsRef.current.close();
            }
            wsRef.current = null;
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
        
        // Clear WebSocket reference
        const wasSpeaking = isSpeakingRef.current;
        const audioWasSent = audioSentRef.current;
        const expectedDuration = expectedDurationRef.current;
        wsRef.current = null;
        
        // If WebSocket closed prematurely (code 1006) and avatar was speaking,
        // the avatar might still be speaking via LiveKit. Don't clear processing state immediately.
        // The speak_ended handler will clear it when the avatar actually finishes.
        if (e.code === 1006 && wasSpeaking) {
          console.warn('⚠️ WebSocket closed abnormally while avatar was speaking');
          console.log('   Avatar may still be speaking via LiveKit stream');
          console.log('   Processing state will clear when avatar finishes (via speak_ended event)');
          // Don't clear processing state here - let speak_ended handler do it
        } else if (e.code === 1006 && audioWasSent) {
          // WebSocket closed before speaking started BUT audio was already sent
          // The avatar might still process and speak via LiveKit, so wait for full duration
          console.warn('⚠️ WebSocket closed before avatar started speaking, but audio was sent');
          console.log(`   ⏱️ Waiting ${(expectedDuration / 1000).toFixed(1)}s for avatar to process and speak via LiveKit`);
          console.log('   🔊 Avatar may still start speaking even without WebSocket events');
          console.log('   👀 Watch the video - avatar should start speaking soon');
          console.log('   📊 Processing indicator will remain visible during this time');
          
          // Wait for the full expected duration + buffer before clearing processing state
          // This gives the avatar time to process the audio and speak via LiveKit
          setTimeout(() => {
            if (isProcessing && !isSpeakingRef.current) {
              console.log('⏱️ Processing timeout reached - avatar did not start speaking');
              console.log('   Clearing processing state');
              setIsProcessing(false);
              setEstimatedTime(0);
            } else if (isSpeakingRef.current) {
              console.log('✅ Avatar started speaking via LiveKit (detected after WebSocket closed)');
              // Don't clear processing state - let speak_ended handler do it
            }
          }, expectedDuration + 10000); // Expected duration + 10s buffer
        } else if (e.code === 1006) {
          // WebSocket closed before audio was sent - connection issue
          console.warn('⚠️ WebSocket closed before audio could be sent');
          // Clear processing state after a short delay
          setTimeout(() => {
            setIsProcessing(false);
            setEstimatedTime(0);
          }, 5000); // 5 second delay
        }
        
        // Reset audio sent flag
        audioSentRef.current = false;
        expectedDurationRef.current = 0;
        
        // Clear timeout if WebSocket closed
        if (wsTimeoutRef.current) {
          clearTimeout(wsTimeoutRef.current);
          wsTimeoutRef.current = null;
        }
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
      setIsProcessing(true);

      // Use the correct avatar_id with custom background
      const response = await fetch('http://13.62.188.127:8000/api/liveavatar/chat-custom/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          session_id: 'luna-liveavatar-custom-session',
          voice: 'shimmer',
          avatar_id: '073b60a9-89a8-45aa-8902-c358f64d2852'  // Luna avatar with custom background
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
      
      // Store session info for reuse
      if (result.session_token && result.session_id) {
        sessionTokenRef.current = result.session_token;
        sessionIdRef.current = result.session_id;
        wsUrlRef.current = result.url || result.realtime_endpoint;
      }
      
      // Connect to LiveKit for video streaming
      if (result.livekit_url && result.livekit_token) {
        const avatarId = '073b60a9-89a8-45aa-8902-c358f64d2852';
        console.log('🎬 Connecting to LiveKit for avatar video (initial setup)...');
        console.log('   Session ID:', result.session_id);
        console.log('   Avatar ID:', avatarId);
        currentAvatarIdRef.current = avatarId;
        setLiveKitUrl(result.livekit_url);
        setStatus('Connecting to avatar...');
        await connectToLiveKit(result.livekit_url, result.livekit_token);
        setStatus('Avatar ready');
        
        // Push audio to LiveAvatar for initial greeting
        if (result.audio_base64) {
          console.log('🔌 Pushing greeting audio to LiveAvatar...');
          setTimeout(() => {
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
      setIsProcessing(false);
      setEstimatedTime(0);
      
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
      
      // Process the message using LiveAvatar Custom Mode pipeline with streaming
      console.log('Processing user message (Custom Mode with streaming):', userMessageText);
      setStatus('Thinking...');
      setIsProcessing(true);
      streamingResponseRef.current = ''; // Reset streaming response
      
      // Create a placeholder message that will be updated as tokens arrive
      const lunaMessageId = Date.now();
      const initialLunaMessage = {
        id: lunaMessageId,
        text: '',
        isUser: false,
        timestamp: new Date().toISOString(),
        isStreaming: true
      };
      setConversation(prev => [...prev, initialLunaMessage]);
      
      try {
        // Use streaming endpoint
        const response = await fetch('http://13.62.188.127:8000/api/liveavatar/chat-custom/stream/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: userMessageText,
            session_id: 'luna-liveavatar-custom-session',
            voice: 'shimmer',
            avatar_id: '073b60a9-89a8-45aa-8902-c358f64d2852'  // Luna avatar with custom background
          })
        });
        
        if (!response.ok) {
          throw new Error(`Backend API error: ${response.status}`);
        }
        
        // Handle streaming response
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let result = null;
        
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || ''; // Keep incomplete line in buffer
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                
                if (data.type === 'token') {
                  // Update streaming response
                  streamingResponseRef.current += data.content;
                  setConversation(prev => prev.map(msg => 
                    msg.id === lunaMessageId 
                      ? { ...msg, text: streamingResponseRef.current }
                      : msg
                  ));
                } else if (data.type === 'done') {
                  // Final response received
                  result = data;
                  streamingResponseRef.current = data.text_response || streamingResponseRef.current;
                  setConversation(prev => prev.map(msg => 
                    msg.id === lunaMessageId 
                      ? { ...msg, text: streamingResponseRef.current, isStreaming: false }
                      : msg
                  ));
                } else if (data.type === 'error') {
                  throw new Error(data.content || 'Streaming error');
                }
              } catch (e) {
                console.warn('Error parsing SSE data:', e, line);
              }
            }
          }
        }
        
        if (!result) {
          throw new Error('No response received from stream');
        }
        
        const lunaResponse = result.text_response || streamingResponseRef.current;
        console.log('Luna response (Streaming):', lunaResponse);
        
        // Estimate response time based on text length (rough: ~150 words per minute speaking)
        const wordCount = lunaResponse.split(/\s+/).length;
        const estimatedSeconds = Math.ceil((wordCount / 150) * 60);
        setEstimatedTime(estimatedSeconds);
        console.log(`⏱️ Estimated response time: ${estimatedSeconds}s for ${wordCount} words`);

        // Store session info for reuse
        if (result.session_token && result.session_id) {
          sessionTokenRef.current = result.session_token;
          sessionIdRef.current = result.session_id;
          wsUrlRef.current = result.url || result.realtime_endpoint;
          liveAvatarService.sessionToken = result.session_token;
          liveAvatarService.currentSession = result.session_id;
          liveAvatarService.isSessionActive = true;
        }
        
        // Check if we already have an active LiveKit connection
        const isAlreadyConnected = roomRef.current && roomRef.current.state === 'connected' && liveKitUrl;
        
        // Check if the LiveKit URL or avatar has changed
        const hasUrlChanged = result.livekit_url && result.livekit_url !== liveKitUrl;
        const avatarId = '073b60a9-89a8-45aa-8902-c358f64d2852';
        const hasAvatarChanged = currentAvatarIdRef.current && currentAvatarIdRef.current !== avatarId;
        
        if (result.livekit_url && result.livekit_token) {
          if (!isAlreadyConnected || hasUrlChanged || hasAvatarChanged) {
            // Connect or reconnect to LiveKit if needed
            if (isAlreadyConnected && (hasUrlChanged || hasAvatarChanged)) {
              console.log('🔄 Avatar or session changed - reconnecting to LiveKit...');
              await roomRef.current.disconnect();
              roomRef.current = null;
            } else {
              console.log('🎬 Connecting to LiveKit for the first time...');
            }
            
            console.log('   Session ID:', result.session_id);
            console.log('   Avatar ID:', avatarId);
            currentAvatarIdRef.current = avatarId;
            liveAvatarService.liveKitUrl = result.livekit_url;
            liveAvatarService.liveKitToken = result.livekit_token;
            await connectToLiveKit(result.livekit_url, result.livekit_token);
            setLiveKitUrl(result.livekit_url);
            setStatus('LiveAvatar ready');
          } else {
            console.log('✅ Already connected to LiveKit - reusing existing session');
          }
        }
        
        // Push audio to LiveAvatar for lip-sync (works whether newly connected or reusing)
        if (result.audio_base64 || result.audio_pcm_base64) {
          console.log('🔌 Pushing audio to existing LiveAvatar session...');
          
          // Use Web Worker for audio processing if PCM not available
          let pcmBase64 = result.audio_pcm_base64;
          if (!pcmBase64 && result.audio_base64 && audioWorkerRef.current) {
            console.log('⚙️ Processing audio in Web Worker...');
            audioWorkerRef.current.postMessage({
              type: 'processAudio',
              data: {
                audioBase64: result.audio_base64,
                targetSampleRate: 24000
              }
            });
            // Store audio for Web Worker callback
            pendingAudioRef.current = {
              audioBase64: result.audio_base64,
              wsUrl: wsUrlRef.current || result.url || result.realtime_endpoint,
              sessionId: sessionIdRef.current || result.session_id,
              sessionToken: sessionTokenRef.current || result.session_token
            };
            // Use processed PCM when available (handled in Web Worker callback)
            pcmBase64 = pendingAudioRef.current.pcmBase64;
          }
          
          setTimeout(() => {
            pushAudioToLiveAvatar(
              result.audio_base64, 
              wsUrlRef.current || result.url || result.realtime_endpoint, 
              sessionIdRef.current || result.session_id, 
              sessionTokenRef.current || result.session_token,
              pcmBase64,  // Pre-processed PCM (from backend or Web Worker)
              result.audio_duration     // Duration if provided
            );
          }, isAlreadyConnected ? 50 : 200); // OPTIMIZATION: Reduced delays (was 100/500ms)
        } else if (!result.livekit_url) {
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
      onClick={async () => {
        if (!audioContext) {
          await initializeAudioContext();
        }
        if (showAudioPrompt) {
          setShowAudioPrompt(false);
          // Enable LiveKit audio playback after user interaction
          if (audioRef.current && audioRef.current.paused) {
            try {
              await audioRef.current.play();
              console.log('✅ Audio enabled after user interaction');
            } catch (err) {
              console.error('Failed to enable audio:', err);
            }
          }
          // Retry playing pending audio if available
          if (pendingAudioRef.current) {
            const audioToPlay = pendingAudioRef.current;
            pendingAudioRef.current = null;
            playAudioResponse(audioToPlay);
          }
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
            background: 'rgba(52, 26, 96, 0.95)',
            backdropFilter: 'blur(10px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            cursor: 'pointer',
            animation: 'fadeIn 0.3s ease-in-out'
          }}>
            <div style={{
              background: 'linear-gradient(135deg, rgba(52, 26, 96, 0.95) 0%, rgba(74, 35, 128, 0.95) 100%)',
              padding: '3rem',
              borderRadius: '20px',
              textAlign: 'center',
              maxWidth: '450px',
              border: '2px solid rgba(150, 107, 252, 0.5)',
              boxShadow: '0 20px 60px rgba(0, 0, 0, 0.5), 0 0 40px rgba(150, 107, 252, 0.3)'
            }}>
              <div style={{
                fontSize: '64px',
                marginBottom: '20px',
                animation: 'pulse-glow 2s ease-in-out infinite'
              }}>🔊</div>
              <h3 style={{ 
                margin: '0 0 1rem 0', 
                color: '#ffffff',
                fontSize: '24px',
                fontWeight: '700',
                letterSpacing: '0.5px'
              }}>
                Click to Enable Audio
              </h3>
              <p style={{ 
                margin: 0, 
                color: 'rgba(255, 255, 255, 0.8)',
                fontSize: '16px',
                lineHeight: '1.5'
              }}>
                Tap anywhere to hear Luna speak
              </p>
            </div>
          </div>
        )}

        {/* Processing Indicator - Top Left */}
        {isProcessing && (
          <div className="processing-indicator" style={{
            position: 'fixed',
            top: '20px',
            left: '20px',
            zIndex: 500,
            background: 'linear-gradient(135deg, rgba(52, 26, 96, 0.95) 0%, rgba(74, 35, 128, 0.95) 100%)',
            backdropFilter: 'blur(20px)',
            padding: '16px 24px',
            borderRadius: '16px',
            border: '2px solid rgba(150, 107, 252, 0.5)',
            boxShadow: '0 8px 32px rgba(52, 26, 96, 0.5), 0 0 40px rgba(150, 107, 252, 0.3)',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            animation: 'slideInLeft 0.4s ease-out'
          }}>
            {/* Animated Spinner */}
            <div style={{
              width: '24px',
              height: '24px',
              border: '3px solid rgba(150, 107, 252, 0.3)',
              borderTop: '3px solid #D4AF37',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite'
            }} />
            
            {/* Text */}
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '4px'
            }}>
              <div style={{
                color: '#ffffff',
                fontSize: '14px',
                fontWeight: '600',
                letterSpacing: '0.5px'
              }}>
                Luna is responding...
              </div>
              {estimatedTime > 0 && (
                <div style={{
                  color: 'rgba(212, 175, 55, 0.9)',
                  fontSize: '12px',
                  fontWeight: '500'
                }}>
                  ~{estimatedTime}s
                </div>
              )}
            </div>
          </div>
        )}
        
        <style>{`
          @keyframes slideInLeft {
            from {
              opacity: 0;
              transform: translateX(-20px);
            }
            to {
              opacity: 1;
              transform: translateX(0);
            }
          }
          
          @media (max-width: 768px) {
            .processing-indicator {
              top: 10px !important;
              left: 10px !important;
              padding: 12px 16px !important;
              font-size: 12px !important;
            }
          }
        `}</style>

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
            background: 'linear-gradient(135deg, #341a60 0%, #4a2380 50%, #966bfc 100%)',
            overflow: 'hidden'
          }}>
            {/* Animated background particles */}
            <div style={{
              position: 'absolute',
              width: '100%',
              height: '100%',
              opacity: 0.3
            }}>
              {[...Array(6)].map((_, i) => (
                <div
                  key={i}
                  style={{
                    position: 'absolute',
                    width: `${100 + i * 30}px`,
                    height: `${100 + i * 30}px`,
                    border: '2px solid rgba(150, 107, 252, 0.4)',
                    borderRadius: '50%',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    animation: `ripple ${2 + i * 0.5}s ease-out infinite`,
                    animationDelay: `${i * 0.3}s`
                  }}
                />
              ))}
            </div>
            
            {/* Luna logo/avatar with glow */}
            <div style={{ 
              textAlign: 'center', 
              color: 'white',
              position: 'relative',
              zIndex: 10
            }}>
              <div style={{
                position: 'relative',
                width: '120px',
                height: '120px',
                margin: '0 auto 30px',
                borderRadius: '50%',
                overflow: 'hidden',
                boxShadow: '0 0 60px rgba(150, 107, 252, 0.8), 0 0 120px rgba(212, 175, 55, 0.4)',
                animation: 'pulse-glow 2s ease-in-out infinite',
                border: '3px solid rgba(212, 175, 55, 0.6)'
              }}>
                <img 
                  src="/Luna.png" 
                  alt="Luna" 
                  style={{
                    width: '100%',
                    height: '100%',
                    objectFit: 'cover',
                    animation: 'gentle-zoom 3s ease-in-out infinite'
                  }}
                />
                <div style={{
                  position: 'absolute',
                  inset: 0,
                  background: 'radial-gradient(circle, transparent 40%, rgba(150, 107, 252, 0.3) 100%)',
                  animation: 'rotate 8s linear infinite'
                }}/>
              </div>
              
              <h2 style={{ 
                fontSize: '28px', 
                fontWeight: '700',
                marginBottom: '12px',
                background: 'linear-gradient(135deg, #ffffff 0%, #D4AF37 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
                letterSpacing: '1px'
              }}>
                Luna
              </h2>
              
              <p style={{ 
                fontSize: '16px', 
                fontWeight: '400',
                color: 'rgba(255, 255, 255, 0.8)',
                marginBottom: '30px',
                letterSpacing: '0.5px'
              }}>
                Initializing AI Avatar...
              </p>
              
              {/* Modern loading bar */}
              <div style={{
                width: '200px',
                height: '4px',
                background: 'rgba(255, 255, 255, 0.2)',
                borderRadius: '2px',
                margin: '0 auto',
                overflow: 'hidden',
                position: 'relative'
              }}>
                <div style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  height: '100%',
                  width: '50%',
                  background: 'linear-gradient(90deg, #D4AF37 0%, #966bfc 100%)',
                  borderRadius: '2px',
                  animation: 'loading-slide 1.5s ease-in-out infinite'
                }}/>
              </div>
            </div>
            
            <style>{`
              @keyframes ripple {
                0% {
                  transform: translate(-50%, -50%) scale(0.8);
                  opacity: 1;
                }
                100% {
                  transform: translate(-50%, -50%) scale(1.5);
                  opacity: 0;
                }
              }
              
              @keyframes pulse-glow {
                0%, 100% {
                  box-shadow: 0 0 60px rgba(150, 107, 252, 0.8), 0 0 120px rgba(212, 175, 55, 0.4);
                  transform: scale(1);
                }
                50% {
                  box-shadow: 0 0 80px rgba(150, 107, 252, 1), 0 0 160px rgba(212, 175, 55, 0.6);
                  transform: scale(1.05);
                }
              }
              
              @keyframes gentle-zoom {
                0%, 100% {
                  transform: scale(1);
                }
                50% {
                  transform: scale(1.1);
                }
              }
              
              @keyframes rotate {
                from {
                  transform: rotate(0deg);
                }
                to {
                  transform: rotate(360deg);
                }
              }
              
              @keyframes loading-slide {
                0% {
                  left: -50%;
                }
                100% {
                  left: 100%;
                }
              }
            `}</style>
          </div>
        ) : (
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted={false}
            style={{
              position: 'absolute',
              top: '0',
              left: '50%',
              transform: 'translateX(-50%)',
              width: '100%',
              height: '110%',
              objectFit: 'cover',
              objectPosition: 'center top',
              animation: 'fadeIn 1s ease-in-out'
            }}
          />
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
                    background: 'linear-gradient(135deg, rgba(52, 26, 96, 0.8) 0%, rgba(74, 35, 128, 0.8) 100%)',
                    border: '2px solid rgba(150, 107, 252, 0.5)',
                    padding: '10px 20px',
                    borderRadius: '20px',
                    fontSize: '14px',
                    color: '#ffffff',
                    cursor: 'pointer',
                    backdropFilter: 'blur(10px)',
                    boxShadow: '0 2px 10px rgba(150, 107, 252, 0.3)',
                    transition: 'all 0.2s',
                    fontWeight: '500'
                  }}
                  onMouseOver={(e) => {
                    e.target.style.background = 'linear-gradient(135deg, #341a60 0%, #966bfc 100%)';
                    e.target.style.transform = 'translateY(-2px)';
                    e.target.style.boxShadow = '0 4px 15px rgba(150, 107, 252, 0.5)';
                    e.target.style.borderColor = '#966bfc';
                  }}
                  onMouseOut={(e) => {
                    e.target.style.background = 'linear-gradient(135deg, rgba(52, 26, 96, 0.8) 0%, rgba(74, 35, 128, 0.8) 100%)';
                    e.target.style.transform = 'translateY(0)';
                    e.target.style.boxShadow = '0 2px 10px rgba(150, 107, 252, 0.3)';
                    e.target.style.borderColor = 'rgba(150, 107, 252, 0.5)';
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
              background: 'transparent',
              backdropFilter: 'none',
              border: 'none',
              pointerEvents: 'auto',
              maxWidth: '70%',
              margin: '0 auto',
              width: '100%'
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
                border: '2px solid rgba(150, 107, 252, 0.5)',
                fontSize: '16px',
                background: 'rgba(255, 255, 255, 0.15)',
                color: '#ffffff',
                outline: 'none',
                transition: 'all 0.3s',
                backdropFilter: 'blur(10px)'
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
