import React, { useState, useEffect, useRef, useCallback } from 'react';
import HeyGenAvatar from './HeyGenAvatar';
import { heygenService } from '../services/heygen';
import './LunaHeyGenAvatar.css';

const LunaHeyGenAvatar = ({
  text = '',
  isSpeaking = false,
  isListening = false,
  onSpeakingStateChange = () => {},
  onReady = () => {},
  onError = (error) => console.error('HeyGen Avatar Error:', error),
  className = ''
}) => {
  const [isAvatarReady, setIsAvatarReady] = useState(false);
  const [isAvatarSpeaking, setIsAvatarSpeaking] = useState(false);
  const [currentText, setCurrentText] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [isInitialized, setIsInitialized] = useState(false);
  const [error, setError] = useState(null);
  const animationFrameRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const [audioLevel, setAudioLevel] = useState(0);

  // Initialize HeyGen service
  const initializeHeyGen = useCallback(async () => {
    if (isInitialized) return;
    
    try {
      console.log('Initializing HeyGen service...');
      
      // Check if we already have a session
      if (!heygenService.sessionId) {
        console.log('Creating new HeyGen session...');
        const session = await heygenService.createSession();
        setSessionId(session);
      } else {
        console.log('Using existing HeyGen session:', heygenService.sessionId);
        setSessionId(heygenService.sessionId);
      }
      
      setIsInitialized(true);
      onReady();
      
    } catch (err) {
      console.error('Failed to initialize HeyGen:', err);
      setError('Failed to initialize avatar service');
      onError(err);
    }
  }, [isInitialized, onReady, onError]);

  // Handle text changes
  useEffect(() => {
    if (text && text !== currentText && isInitialized) {
      console.log('New text to speak:', text);
      setCurrentText(text);
      
      // In a real implementation, we would send this text to HeyGen
      // For now, we'll just simulate the speaking state
      if (isSpeaking) {
        setIsAvatarSpeaking(true);
        
        // Simulate speaking duration based on text length
        const wordCount = text.split(/\s+/).length;
        const duration = Math.max(2000, Math.min(wordCount * 300, 10000)); // 0.3s per word, min 2s, max 10s
        
        const timer = setTimeout(() => {
          setIsAvatarSpeaking(false);
          onSpeakingStateChange(false);
        }, duration);
        
        return () => clearTimeout(timer);
      }
    }
  }, [text, currentText, isSpeaking, isInitialized, onSpeakingStateChange]);

  // Initialize on mount
  useEffect(() => {
    initializeHeyGen();
    
    return () => {
      // Cleanup
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      
      // Note: We're not closing the session here to allow for reuse
      // In a production app, you might want to implement session management
    };
  }, [initializeHeyGen]);

  // Handle avatar speaking state changes
  useEffect(() => {
    if (isAvatarSpeaking !== isSpeaking) {
      onSpeakingStateChange(isAvatarSpeaking);
    }
  }, [isAvatarSpeaking, isSpeaking, onSpeakingStateChange]);

  // Audio visualization
  const setupAudioAnalysis = useCallback((stream) => {
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
        
        if (isAvatarSpeaking) {
          animationFrameRef.current = requestAnimationFrame(updateAudioLevel);
        }
      };

      updateAudioLevel();
    } catch (error) {
      console.error('Error setting up audio analysis:', error);
    }
  }, [isAvatarSpeaking]);

  // Visual feedback for speaking
  const getMouthShape = useCallback(() => {
    if (!isAvatarSpeaking) return 'M 40,50 Q 50,30 60,50 Q 50,70 40,50';
    
    // Dynamic mouth shape based on audio level
    const open = 20 + (audioLevel * 15);
    const width = 5 + (audioLevel * 5);
    
    return `M ${40 - width},50 Q 50,${50 - open} ${60 + width},50`;
  }, [isAvatarSpeaking, audioLevel]);

  // Render error state
  if (error) {
    return (
      <div className={`luna-heygen-avatar error ${className}`}>
        <div className="error-message">
          <p>Avatar Unavailable</p>
          <small>{error}</small>
        </div>
      </div>
    );
  }

  // Render loading state
  if (!isInitialized) {
    return (
      <div className={`luna-heygen-avatar loading ${className}`}>
        <div className="loading-spinner"></div>
        <p>Initializing Avatar...</p>
      </div>
    );
  }

  return (
    <div className={`luna-heygen-avatar ${className}`}>
      <div className="avatar-container">
        {/* In a real implementation, we would use the HeyGenAvatar component */}
        {/* <HeyGenAvatar
          text={currentText}
          onAvatarSpeaking={setIsAvatarSpeaking}
          onAvatarReady={() => setIsAvatarReady(true)}
          onError={onError}
          autoStart={isSpeaking}
        /> */}
        
        {/* Fallback UI for now */}
        <div className="avatar-fallback">
          <svg viewBox="0 0 100 100" className="avatar-silhouette">
            <circle cx="50" cy="40" r="30" fill="#f0f0f0" />
            <path d={getMouthShape()} fill="none" stroke="#333" strokeWidth="2" />
            <circle cx="40" cy="35" r="3" fill="#333" />
            <circle cx="60" cy="35" r="3" fill="#333" />
          </svg>
          
          {isListening && (
            <div className="listening-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          )}
        </div>
        
        {/* Audio visualization */}
        {isAvatarSpeaking && (
          <div className="audio-visualizer">
            {Array.from({ length: 10 }).map((_, i) => (
              <div 
                key={i}
                className="audio-bar"
                style={{
                  height: `${10 + (Math.sin(i * 0.5) * 0.5 + 0.5) * audioLevel * 50}px`,
                  opacity: 0.5 + (audioLevel * 0.5)
                }}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default LunaHeyGenAvatar;
