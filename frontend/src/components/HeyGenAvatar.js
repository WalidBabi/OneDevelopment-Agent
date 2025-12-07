import React, { useState, useEffect, useRef, useCallback } from 'react';
import { heygenService } from '../services/heygen';
import './HeyGenAvatar.css';

const HeyGenAvatar = ({ 
  text = '',
  onAvatarSpeaking = () => {},
  onAvatarReady = () => {},
  onError = (error) => console.error(error),
  autoStart = true,
  className = ''
}) => {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isReady, setIsReady] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const videoRef = useRef(null);
  const mediaSourceRef = useRef(null);
  const sourceBufferRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const animationFrameRef = useRef(null);
  const [audioLevel, setAudioLevel] = useState(0);

  // Initialize HeyGen service and set up WebSocket connection
  const initHeyGen = useCallback(async () => {
    try {
      if (!heygenService.sessionId) {
        await heygenService.createSession();
        setSessionId(heygenService.sessionId);
        setIsReady(true);
        onAvatarReady();
      }
    } catch (error) {
      console.error('Failed to initialize HeyGen:', error);
      onError(error);
    }
  }, [onAvatarReady, onError]);

  // Clean up resources
  const cleanup = useCallback(() => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }

    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }

    if (sourceBufferRef.current) {
      sourceBufferRef.current = null;
    }

    if (mediaSourceRef.current) {
      if (mediaSourceRef.current.readyState === 'open') {
        mediaSourceRef.current.endOfStream();
      }
      mediaSourceRef.current = null;
    }

    if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
  }, []);

  // Initialize audio analysis
  const initAudioAnalysis = useCallback((stream) => {
    try {
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }

      const AudioContext = window.AudioContext || window.webkitAudioContext;
      audioContextRef.current = new AudioContext();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 32;
      source.connect(analyserRef.current);

      const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);

      const updateAudioLevel = () => {
        if (!analyserRef.current) return;
        
        analyserRef.current.getByteFrequencyData(dataArray);
        const sum = dataArray.reduce((a, b) => a + b, 0);
        const avg = sum / dataArray.length;
        setAudioLevel(avg / 255); // Normalize to 0-1
        
        if (isSpeaking) {
          animationFrameRef.current = requestAnimationFrame(updateAudioLevel);
        }
      };

      updateAudioLevel();
    } catch (error) {
      console.error('Error initializing audio analysis:', error);
    }
  }, [isSpeaking]);

  // Handle text-to-speech with HeyGen
  const speak = useCallback(async (textToSpeak) => {
    if (!heygenService || !heygenService.sessionId) {
      console.error('HeyGen service not initialized');
      return;
    }

    try {
      setIsSpeaking(true);
      onAvatarSpeaking(true);

      // Set up MediaSource and MediaRecorder to capture the stream
      const mediaSource = new MediaSource();
      mediaSourceRef.current = mediaSource;
      
      if (videoRef.current) {
        videoRef.current.src = URL.createObjectURL(mediaSource);
      }

      mediaSource.onsourceopen = async () => {
        const sourceBuffer = mediaSource.addSourceBuffer('video/mp4');
        sourceBufferRef.current = sourceBuffer;

        try {
          // Start the HeyGen TTS
          await heygenService.sendText(textToSpeak);
          
          // Set up MediaRecorder to capture the stream
          const stream = await navigator.mediaDevices.getUserMedia({ 
            audio: true, 
            video: false 
          });
          
          initAudioAnalysis(stream);
          
          mediaRecorderRef.current = new MediaRecorder(stream, {
            mimeType: 'video/webm;codecs=vp9',
          });

          const chunks = [];
          
          mediaRecorderRef.current.ondataavailable = (event) => {
            if (event.data.size > 0) {
              chunks.push(event.data);
              
              if (sourceBuffer && !sourceBuffer.updating && mediaSource.readyState === 'open') {
                const blob = new Blob(chunks, { type: 'video/webm' });
                const fileReader = new FileReader();
                
                fileReader.onload = () => {
                  const arrayBuffer = fileReader.result;
                  try {
                    sourceBuffer.appendBuffer(arrayBuffer);
                  } catch (e) {
                    console.error('Error appending buffer:', e);
                  }
                };
                
                fileReader.readAsArrayBuffer(blob);
              }
            }
          };

          mediaRecorderRef.current.start(100); // Collect data every 100ms
          
        } catch (error) {
          console.error('Error during HeyGen TTS:', error);
          onError(error);
          setIsSpeaking(false);
          onAvatarSpeaking(false);
        }
      };

      // Set up event listeners for video playback
      if (videoRef.current) {
        videoRef.current.onended = () => {
          setIsSpeaking(false);
          onAvatarSpeaking(false);
          cleanup();
        };

        videoRef.current.onplay = () => {
          console.log('Video playback started');
        };

        videoRef.current.onerror = (error) => {
          console.error('Video playback error:', error);
          setIsSpeaking(false);
          onAvatarSpeaking(false);
          cleanup();
        };
      }

    } catch (error) {
      console.error('Error in speak function:', error);
      onError(error);
      setIsSpeaking(false);
      onAvatarSpeaking(false);
      cleanup();
    }
  }, [cleanup, initAudioAnalysis, onAvatarSpeaking, onError]);

  // Effect to handle auto-start
  useEffect(() => {
    if (autoStart && text) {
      speak(text);
    }
  }, [autoStart, speak, text]);

  // Initialize HeyGen on mount
  useEffect(() => {
    initHeyGen();
    
    return () => {
      cleanup();
      if (heygenService) {
        heygenService.close();
      }
    };
  }, [initHeyGen, cleanup]);

  // Visual feedback for speech
  const getMouthShape = useCallback(() => {
    if (!isSpeaking) return 'M 40,50 Q 50,30 60,50 Q 50,70 40,50';
    
    // Dynamic mouth shape based on audio level
    const open = 20 + (audioLevel * 15);
    const width = 5 + (audioLevel * 5);
    
    return `M ${40 - width},50 Q 50,${50 - open} ${60 + width},50`;
  }, [isSpeaking, audioLevel]);

  return (
    <div className={`heygen-avatar-container ${className}`}>
      <div className="avatar-video-container">
        <video
          ref={videoRef}
          className="avatar-video"
          autoPlay
          playsInline
          muted
        />
        
        {/* Fallback avatar when video is not available */}
        {!isSpeaking && (
          <div className="avatar-fallback">
            <svg viewBox="0 0 100 100" className="avatar-silhouette">
              <circle cx="50" cy="40" r="30" fill="#f0f0f0" />
              <path d={getMouthShape()} fill="none" stroke="#333" strokeWidth="2" />
              <circle cx="40" cy="35" r="3" fill="#333" />
              <circle cx="60" cy="35" r="3" fill="#333" />
            </svg>
          </div>
        )}
        
        {/* Loading indicator */}
        {!isReady && (
          <div className="avatar-loading">
            <div className="loading-spinner"></div>
            <p>Initializing avatar...</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default HeyGenAvatar;
