import React, { useState, useEffect, useRef, useCallback } from 'react';
import { chatService } from '../services/api';
import { v4 as uuidv4 } from 'uuid';
import ReactMarkdown from 'react-markdown';
import './LunaFreeInterface.css';

/**
 * LUNA FREE INTERFACE
 * 
 * 100% FREE - No paid APIs required!
 * 
 * Features:
 * - Web Speech API for voice (built into browsers)
 * - Canvas-based audio visualization
 * - CSS-powered lip-sync simulation
 * - Stunning visual effects
 */

// Audio Analyzer Hook - Creates visual waveform from speech
const useAudioAnalyzer = () => {
  const [audioData, setAudioData] = useState(new Uint8Array(32));
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const analyserRef = useRef(null);
  const animationRef = useRef(null);
  const audioContextRef = useRef(null);

  const startAnalyzing = useCallback((audioElement) => {
    if (!audioElement) return;

    try {
      // Create audio context if needed
      if (!audioContextRef.current) {
        audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      }

      const audioContext = audioContextRef.current;
      
      // Create analyzer
      analyserRef.current = audioContext.createAnalyser();
      analyserRef.current.fftSize = 64;
      analyserRef.current.smoothingTimeConstant = 0.8;

      // Connect audio element to analyzer
      const source = audioContext.createMediaElementSource(audioElement);
      source.connect(analyserRef.current);
      analyserRef.current.connect(audioContext.destination);

      setIsAnalyzing(true);

      // Animation loop for visualization
      const updateData = () => {
        if (!analyserRef.current) return;
        
        const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
        analyserRef.current.getByteFrequencyData(dataArray);
        setAudioData(dataArray);
        
        animationRef.current = requestAnimationFrame(updateData);
      };
      
      updateData();
    } catch (err) {
      console.warn('Audio analyzer not supported:', err);
    }
  }, []);

  const stopAnalyzing = useCallback(() => {
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
    setIsAnalyzing(false);
    setAudioData(new Uint8Array(32));
  }, []);

  useEffect(() => {
    return () => {
      stopAnalyzing();
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, [stopAnalyzing]);

  return { audioData, isAnalyzing, startAnalyzing, stopAnalyzing };
};

// Text sanitizer - Clean text before speaking to avoid reading symbols literally
const sanitizeTextForSpeech = (text) => {
  if (!text) return '';
  
  let cleaned = text
    // Remove markdown code blocks
    .replace(/```[\s\S]*?```/g, ' code block ')
    .replace(/`[^`]+`/g, ' ')
    // Remove markdown headers
    .replace(/^#{1,6}\s+/gm, '')
    // Remove bold/italic markers but keep text
    .replace(/\*\*([^*]+)\*\*/g, '$1')
    .replace(/\*([^*]+)\*/g, '$1')
    .replace(/__([^_]+)__/g, '$1')
    .replace(/_([^_]+)_/g, '$1')
    // Remove bullet points and list markers
    .replace(/^[\s]*[-*+•]\s+/gm, '')
    .replace(/^[\s]*\d+\.\s+/gm, '')
    // Remove links - keep text, remove URL
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/https?:\/\/[^\s]+/g, '')
    // Remove image syntax
    .replace(/!\[([^\]]*)\]\([^)]+\)/g, '')
    // Remove HTML tags
    .replace(/<[^>]+>/g, '')
    // Remove special characters that get read literally
    .replace(/[#@&|\\/<>{}[\]^~`]/g, '')
    // Clean up currency to speak naturally
    .replace(/\$(\d+)/g, '$1 dollars')
    .replace(/AED\s*(\d+)/gi, '$1 dirhams')
    // Clean percentages
    .replace(/(\d+)%/g, '$1 percent')
    // Remove excessive punctuation
    .replace(/\.{3,}/g, '... ')
    .replace(/!{2,}/g, '!')
    .replace(/\?{2,}/g, '?')
    // Add natural pauses with punctuation
    .replace(/([.!?])\s+/g, '$1 ... ')
    .replace(/,\s+/g, ', ')
    .replace(/:\s+/g, ': ')
    // Clean up extra whitespace
    .replace(/\s+/g, ' ')
    .trim();
  
  return cleaned;
};

// Viseme mapping for lip sync - maps phonemes to mouth shapes
const VISEME_MAP = {
  // Closed mouth
  'silence': { mouthOpen: 0, mouthWidth: 0.5 },
  // Open vowels  
  'aa': { mouthOpen: 0.9, mouthWidth: 0.6 },  // "father"
  'ae': { mouthOpen: 0.7, mouthWidth: 0.7 },  // "cat"
  'ah': { mouthOpen: 0.6, mouthWidth: 0.5 },  // "but"
  'ao': { mouthOpen: 0.8, mouthWidth: 0.4 },  // "bought"
  'eh': { mouthOpen: 0.5, mouthWidth: 0.7 },  // "bed"
  'ih': { mouthOpen: 0.3, mouthWidth: 0.6 },  // "bit"
  'iy': { mouthOpen: 0.2, mouthWidth: 0.8 },  // "beat" - wide smile
  'ow': { mouthOpen: 0.7, mouthWidth: 0.3 },  // "boat" - rounded
  'uh': { mouthOpen: 0.4, mouthWidth: 0.4 },  // "book"
  'uw': { mouthOpen: 0.3, mouthWidth: 0.2 },  // "boot" - small rounded
  // Consonants
  'b': { mouthOpen: 0.1, mouthWidth: 0.5 },   // lips together
  'm': { mouthOpen: 0.05, mouthWidth: 0.5 },  // lips together
  'p': { mouthOpen: 0.1, mouthWidth: 0.5 },   // lips together
  'f': { mouthOpen: 0.15, mouthWidth: 0.6 },  // bottom lip tucked
  'v': { mouthOpen: 0.15, mouthWidth: 0.6 },
  'th': { mouthOpen: 0.2, mouthWidth: 0.6 },  // tongue visible
  'w': { mouthOpen: 0.3, mouthWidth: 0.2 },   // rounded
  'r': { mouthOpen: 0.35, mouthWidth: 0.4 },
  's': { mouthOpen: 0.15, mouthWidth: 0.65 }, // slightly open
  'sh': { mouthOpen: 0.25, mouthWidth: 0.35 },
  'ch': { mouthOpen: 0.3, mouthWidth: 0.35 },
  'default': { mouthOpen: 0.4, mouthWidth: 0.5 },
};

// Map characters to approximate visemes
const charToViseme = (char) => {
  const lowerChar = char.toLowerCase();
  const vowelMap = {
    'a': 'aa', 'e': 'eh', 'i': 'ih', 'o': 'ow', 'u': 'uh',
  };
  const consonantMap = {
    'b': 'b', 'm': 'm', 'p': 'p', 'f': 'f', 'v': 'v',
    'w': 'w', 'r': 'r', 's': 's', 'z': 's',
    'c': 'ch', 'j': 'ch', 'k': 'ch', 'g': 'ch',
    'l': 'r', 'n': 'm', 'd': 'th', 't': 'th',
  };
  
  if (vowelMap[lowerChar]) return VISEME_MAP[vowelMap[lowerChar]];
  if (consonantMap[lowerChar]) return VISEME_MAP[consonantMap[lowerChar]];
  if (/[a-z]/i.test(char)) return VISEME_MAP.default;
  return VISEME_MAP.silence;
};

// Enhanced Speech Hook using OpenAI TTS - Super realistic voices!
const useEnhancedSpeech = () => {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [currentWord, setCurrentWord] = useState('');
  const [speechProgress, setSpeechProgress] = useState(0);
  const [amplitude, setAmplitude] = useState(0);
  const [viseme, setViseme] = useState(VISEME_MAP.silence);
  const [mouthOpen, setMouthOpen] = useState(0);
  const [mouthWidth, setMouthWidth] = useState(0.5);
  const audioRef = useRef(null);
  const animationFrameRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const startTimeRef = useRef(0);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  // Animate lip sync based on audio analysis
  const animateLipSync = useCallback((text, audioElement) => {
    if (!audioElement) return;
    
    const chars = text.replace(/[^a-zA-Z\s]/g, '').split('');
    const words = text.split(' ');
    let lastViseme = VISEME_MAP.silence;
    let analyserNode = null;
    let dataArray = null;
    
    // Try to set up audio analysis for more accurate lip sync
    try {
      if (!audioContextRef.current) {
        audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      }
      
      if (!analyserRef.current) {
        analyserRef.current = audioContextRef.current.createAnalyser();
        analyserRef.current.fftSize = 256;
        analyserRef.current.smoothingTimeConstant = 0.8;
        
        const source = audioContextRef.current.createMediaElementSource(audioElement);
        source.connect(analyserRef.current);
        analyserRef.current.connect(audioContextRef.current.destination);
      }
      
      analyserNode = analyserRef.current;
      dataArray = new Uint8Array(analyserNode.frequencyBinCount);
    } catch (e) {
      console.warn('Audio analysis not available, using fallback animation:', e.message);
    }
    
    const animate = () => {
      if (!audioElement || audioElement.paused || audioElement.ended) {
        setMouthOpen(0);
        setMouthWidth(0.5);
        setAmplitude(0);
        return;
      }
      
      let normalizedAmplitude = 0;
      
      // Try to get actual audio data if analyser is available
      if (analyserNode && dataArray) {
        try {
          analyserNode.getByteFrequencyData(dataArray);
          const avg = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
          normalizedAmplitude = Math.min(avg / 128, 1);
        } catch (e) {
          // Fall back to text-based estimation
          normalizedAmplitude = 0.5;
        }
      } else {
        // Fallback: estimate amplitude based on text position
        normalizedAmplitude = 0.5 + Math.sin(Date.now() * 0.01) * 0.2;
      }
      
      // Calculate progress
      const progress = (audioElement.currentTime / audioElement.duration) * 100;
      setSpeechProgress(progress);
      
      // Estimate current word
      const wordIndex = Math.floor((progress / 100) * words.length);
      setCurrentWord(words[Math.min(wordIndex, words.length - 1)] || '');
      
      // Estimate current character for viseme
      const charIndex = Math.floor((progress / 100) * chars.length);
      const char = chars[Math.min(charIndex, chars.length - 1)] || ' ';
      const targetViseme = charToViseme(char);
      
      // Smooth interpolation between visemes
      const newMouthOpen = lastViseme.mouthOpen + (targetViseme.mouthOpen - lastViseme.mouthOpen) * 0.3;
      const newMouthWidth = lastViseme.mouthWidth + (targetViseme.mouthWidth - lastViseme.mouthWidth) * 0.3;
      
      // Blend with actual audio amplitude for more natural movement
      const audioMouthOpen = normalizedAmplitude * 0.8;
      const blendedMouthOpen = (newMouthOpen * 0.4) + (audioMouthOpen * 0.6);
      
      // Add subtle natural variation
      const variation = Math.sin(Date.now() * 0.01) * 0.05;
      
      setMouthOpen(Math.max(0, Math.min(1, blendedMouthOpen + variation)));
      setMouthWidth(Math.max(0.2, Math.min(1, newMouthWidth)));
      setAmplitude(normalizedAmplitude);
      
      lastViseme = { mouthOpen: blendedMouthOpen, mouthWidth: newMouthWidth };
      
      animationFrameRef.current = requestAnimationFrame(animate);
    };
    
    animate();
  }, []);

  const speak = useCallback(async (rawText, onEnd, voice = 'nova') => {
    // Stop any current audio
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }

    // Reset audio context for new audio
    analyserRef.current = null;

    // Sanitize text for natural speech
    const text = sanitizeTextForSpeech(rawText);
    if (!text) {
      onEnd?.();
      return;
    }

    console.log(`🎤 Generating OpenAI TTS (${voice}) for:`, text.substring(0, 50) + '...');
    setIsSpeaking(true);

    try {
      // Call OpenAI TTS via backend with selected voice
      const { audioUrl } = await chatService.generateTTS(text, voice);
      
      console.log('✅ TTS audio received, playing...');
      
      // Create and play audio
      const audio = new Audio(audioUrl);
      audioRef.current = audio;
      
      audio.onplay = () => {
        console.log('🔊 Audio playing');
        // Start lip sync animation with audio element
        animateLipSync(text, audio);
      };
      
      audio.onended = () => {
        console.log('🔇 Audio ended');
        setIsSpeaking(false);
        setCurrentWord('');
        setSpeechProgress(0);
        setAmplitude(0);
        setMouthOpen(0);
        setMouthWidth(0.5);
        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current);
        }
        // Revoke the blob URL to free memory
        URL.revokeObjectURL(audioUrl);
        onEnd?.();
      };
      
      audio.onerror = (event) => {
        console.error('Audio playback error:', event);
        setIsSpeaking(false);
        setAmplitude(0);
        setMouthOpen(0);
        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current);
        }
        URL.revokeObjectURL(audioUrl);
        onEnd?.();
      };
      
      // Resume audio context if suspended (browser autoplay policy)
      if (audioContextRef.current?.state === 'suspended') {
        await audioContextRef.current.resume();
      }
      
      await audio.play();
      
    } catch (error) {
      console.error('TTS error:', error);
      setIsSpeaking(false);
      setAmplitude(0);
      setMouthOpen(0);
      
      // Fallback to browser speech synthesis if OpenAI fails
      console.log('⚠️ Falling back to browser speech synthesis');
      if (window.speechSynthesis) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.95;
        utterance.pitch = 1.0;
        utterance.onend = () => {
          setIsSpeaking(false);
          onEnd?.();
        };
        utterance.onerror = () => {
          setIsSpeaking(false);
          onEnd?.();
        };
        utterance.onstart = () => setIsSpeaking(true);
        window.speechSynthesis.speak(utterance);
      } else {
        onEnd?.();
      }
    }
  }, [animateLipSync]);

  const stop = useCallback(() => {
    // Stop OpenAI TTS audio
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current = null;
    }
    // Also stop any browser speech synthesis (fallback)
    window.speechSynthesis?.cancel();
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
    setIsSpeaking(false);
    setCurrentWord('');
    setSpeechProgress(0);
    setAmplitude(0);
    setMouthOpen(0);
    setMouthWidth(0.5);
  }, []);

  return { 
    speak, 
    stop, 
    isSpeaking, 
    currentWord, 
    speechProgress, 
    amplitude,
    mouthOpen,
    mouthWidth,
    isSupported: true  // OpenAI TTS is always available via backend
  };
};

// Speech Recognition Hook with Audio Waveform and Auto-Send
const useSpeechRecognition = (onAutoSend) => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [error, setError] = useState(null);
  const [audioLevel, setAudioLevel] = useState(0);
  const [waveformData, setWaveformData] = useState(new Array(32).fill(0));
  const recognitionRef = useRef(null);
  const isInitializedRef = useRef(false);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const mediaStreamRef = useRef(null);
  const animationFrameRef = useRef(null);
  const silenceTimeoutRef = useRef(null);
  const lastSpeechTimeRef = useRef(Date.now());
  const hasSpokenRef = useRef(false);
  const fullTranscriptRef = useRef('');

  const SILENCE_TIMEOUT = 2000; // 2 seconds of silence to auto-send

  const isSupported = typeof window !== 'undefined' && 
    (window.SpeechRecognition || window.webkitSpeechRecognition);

  // Start audio analyzer for waveform visualization
  const startAudioAnalyzer = useCallback(async () => {
    try {
      // Stop any existing analyzer first
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach(track => track.stop());
      }
      if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
        await audioContextRef.current.close().catch(() => {});
      }

      console.log('🎤 Requesting microphone for waveform...');
      
      // Get the default audio input device
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: false, // Disable to get raw audio
          noiseSuppression: false,
          autoGainControl: false,
          channelCount: 1
        } 
      });
      mediaStreamRef.current = stream;
      
      // Log which device we're using
      const audioTrack = stream.getAudioTracks()[0];
      console.log('✅ Got microphone:', audioTrack.label);

      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      
      // Resume audio context if suspended (browser policy)
      if (audioContextRef.current.state === 'suspended') {
        await audioContextRef.current.resume();
        console.log('✅ Audio context resumed');
      }

      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 256;
      analyserRef.current.smoothingTimeConstant = 0.5;

      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyserRef.current);

      // Use TIME DOMAIN data for more responsive waveform (actual sound wave)
      const bufferLength = analyserRef.current.fftSize;
      const timeDataArray = new Uint8Array(bufferLength);
      const freqDataArray = new Uint8Array(analyserRef.current.frequencyBinCount);

      const updateWaveform = () => {
        if (!analyserRef.current || !audioContextRef.current) return;
        
        // Get time domain data (actual waveform)
        analyserRef.current.getByteTimeDomainData(timeDataArray);
        // Also get frequency data for level
        analyserRef.current.getByteFrequencyData(freqDataArray);
        
        // Calculate RMS level from time domain (more accurate for speech)
        let sum = 0;
        for (let i = 0; i < bufferLength; i++) {
          const value = (timeDataArray[i] - 128) / 128; // Normalize to -1 to 1
          sum += value * value;
        }
        const rms = Math.sqrt(sum / bufferLength);
        const normalizedLevel = Math.min(rms * 3, 1); // Amplify RMS
        setAudioLevel(normalizedLevel);
        
        // Create waveform from time domain data - sample 32 points
        const waveform = [];
        const step = Math.floor(bufferLength / 32);
        for (let i = 0; i < 32; i++) {
          // Convert from 0-255 to 0-1 range, centered at 0.5
          const raw = timeDataArray[i * step];
          const value = Math.abs(raw - 128) / 128; // Distance from center
          waveform.push(value);
        }
        setWaveformData(waveform);

        // Check for speech activity
        if (normalizedLevel > 0.02) {
          lastSpeechTimeRef.current = Date.now();
          hasSpokenRef.current = true;
        }

        animationFrameRef.current = requestAnimationFrame(updateWaveform);
      };

      updateWaveform();
      console.log('🎤 Audio analyzer started successfully!');
    } catch (e) {
      console.error('❌ Failed to start audio analyzer:', e);
    }
  }, []);

  // Stop audio analyzer
  const stopAudioAnalyzer = useCallback(() => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(track => track.stop());
    }
    if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
      audioContextRef.current.close().catch(() => {});
    }
    analyserRef.current = null;
    audioContextRef.current = null;
    mediaStreamRef.current = null;
    setAudioLevel(0);
    setWaveformData(new Array(32).fill(0));
  }, []);

  // Check for silence and auto-send
  useEffect(() => {
    if (!isListening) return;

    const checkSilence = () => {
      const timeSinceLastSpeech = Date.now() - lastSpeechTimeRef.current;
      const currentTranscript = fullTranscriptRef.current || interimTranscript;
      
      // Auto-send if: has spoken, has transcript, and silence for SILENCE_TIMEOUT
      if (hasSpokenRef.current && currentTranscript.trim() && timeSinceLastSpeech > SILENCE_TIMEOUT) {
        console.log('🔇 Auto-sending after silence:', currentTranscript);
        const textToSend = currentTranscript.trim();
        
        // Reset before sending
        hasSpokenRef.current = false;
        fullTranscriptRef.current = '';
        setTranscript('');
        setInterimTranscript('');
        
        if (onAutoSend) {
          onAutoSend(textToSend);
        }
      }
    };

    silenceTimeoutRef.current = setInterval(checkSilence, 300);

    return () => {
      if (silenceTimeoutRef.current) {
        clearInterval(silenceTimeoutRef.current);
      }
    };
  }, [isListening, interimTranscript, onAutoSend]);

  // Initialize recognition on mount
  useEffect(() => {
    if (!isSupported || isInitializedRef.current) return;

    try {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true; // Keep listening
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';
      recognitionRef.current.maxAlternatives = 1;

      recognitionRef.current.onresult = (event) => {
        let interim = '';
        let final = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcriptText = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            final += transcriptText;
          } else {
            interim += transcriptText;
          }
        }
        
        // Update last speech time when we get results
        lastSpeechTimeRef.current = Date.now();
        hasSpokenRef.current = true;
        
        if (final) {
          fullTranscriptRef.current += ' ' + final;
          setTranscript(fullTranscriptRef.current.trim());
          setInterimTranscript('');
        } else {
          setInterimTranscript(interim);
        }
      };

      recognitionRef.current.onend = () => {
        console.log('Speech recognition ended, restarting...');
        // Auto-restart if still supposed to be listening
        if (recognitionRef.current && isListening) {
          setTimeout(() => {
            try {
              recognitionRef.current.start();
            } catch (e) {
              console.log('Restart failed:', e);
            }
          }, 100);
        }
      };
      
      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setError(event.error);
        
        if (event.error === 'not-allowed') {
          setIsListening(false);
          stopAudioAnalyzer();
        } else if (event.error === 'no-speech') {
          // No speech detected, keep listening
          console.log('No speech detected, continuing...');
        }
      };

      isInitializedRef.current = true;
      console.log('Speech recognition initialized');
    } catch (e) {
      console.error('Failed to initialize speech recognition:', e);
      setError('initialization_failed');
    }

    return () => {
      stopAudioAnalyzer();
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch (e) {}
      }
    };
  }, [isSupported, stopAudioAnalyzer, isListening]);

  const startListening = useCallback(async () => {
    if (!recognitionRef.current) {
      console.error('Speech recognition not initialized');
      setError('not_initialized');
      return false;
    }
    
    // Reset state
    fullTranscriptRef.current = '';
    setTranscript('');
    setInterimTranscript('');
    setError(null);
    hasSpokenRef.current = false;
    lastSpeechTimeRef.current = Date.now();
    setIsListening(true);
    
    // Start audio analyzer for waveform
    await startAudioAnalyzer();
    
    try {
      try { recognitionRef.current.abort(); } catch (e) {}
      
      setTimeout(() => {
        try {
          recognitionRef.current.start();
          console.log('🎤 Speech recognition started');
        } catch (e) {
          console.error('Failed to start recognition:', e);
          setIsListening(false);
          setError('start_failed');
        }
      }, 100);
      
      return true;
    } catch (e) {
      console.error('Recognition start error:', e);
      setIsListening(false);
      setError('start_failed');
      return false;
    }
  }, [startAudioAnalyzer]);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      try { recognitionRef.current.stop(); } catch (e) {}
    }
    stopAudioAnalyzer();
    setIsListening(false);
    if (silenceTimeoutRef.current) {
      clearInterval(silenceTimeoutRef.current);
    }
  }, [stopAudioAnalyzer]);

  const clearTranscript = useCallback(() => {
    fullTranscriptRef.current = '';
    setTranscript('');
    setInterimTranscript('');
    hasSpokenRef.current = false;
  }, []);

  return { 
    isListening, 
    transcript, 
    interimTranscript,
    startListening, 
    stopListening, 
    clearTranscript,
    isSupported,
    error,
    audioLevel,
    waveformData
  };
};

// Microphone Waveform Visualizer - Shows voice input in real-time
const MicrophoneWaveform = ({ waveformData, isListening, audioLevel }) => {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const smoothedDataRef = useRef(new Array(32).fill(0));

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    const barCount = 32;
    const barWidth = (width / barCount) - 2;
    const barGap = 2;

    const draw = () => {
      // Clear canvas with slight fade for trail effect
      ctx.fillStyle = 'rgba(10, 5, 16, 0.3)';
      ctx.fillRect(0, 0, width, height);

      if (isListening && waveformData) {
        // Smooth the waveform data for nicer animation
        for (let i = 0; i < barCount; i++) {
          const target = (waveformData[i] || 0) * 1.5; // Amplify
          smoothedDataRef.current[i] += (target - smoothedDataRef.current[i]) * 0.3;
        }

        // Draw waveform bars from center
        for (let i = 0; i < barCount; i++) {
          const value = Math.min(1, smoothedDataRef.current[i]);
          const barHeight = Math.max(4, value * height * 0.9);
          
          const x = i * (barWidth + barGap);
          const y = (height - barHeight) / 2;

          // Create gradient for each bar
          const gradient = ctx.createLinearGradient(x, y, x, y + barHeight);
          
          if (value > 0.1) {
            // Active bars - purple to gold gradient
            gradient.addColorStop(0, `rgba(150, 107, 252, ${0.6 + value * 0.4})`);
            gradient.addColorStop(0.5, `rgba(212, 175, 55, ${0.5 + value * 0.5})`);
            gradient.addColorStop(1, `rgba(150, 107, 252, ${0.6 + value * 0.4})`);
          } else {
            // Quiet bars - dim purple
            gradient.addColorStop(0, 'rgba(150, 107, 252, 0.3)');
            gradient.addColorStop(1, 'rgba(150, 107, 252, 0.3)');
          }
          
          ctx.fillStyle = gradient;
          ctx.fillRect(x, y, barWidth, barHeight);
          
          // Glow effect for loud bars
          if (value > 0.4) {
            ctx.shadowColor = 'rgba(212, 175, 55, 0.8)';
            ctx.shadowBlur = 15;
            ctx.fillRect(x, y, barWidth, barHeight);
            ctx.shadowBlur = 0;
          }
        }

        // Audio level indicator circle
        const levelRadius = 5 + audioLevel * 10;
        ctx.beginPath();
        ctx.arc(width - 15, height / 2, levelRadius, 0, Math.PI * 2);
        ctx.fillStyle = audioLevel > 0.1 
          ? `rgba(0, 212, 170, ${0.5 + audioLevel * 0.5})` 
          : 'rgba(150, 107, 252, 0.3)';
        ctx.fill();

      } else {
        // Idle state - subtle pulse line
        const time = Date.now() * 0.002;
        ctx.strokeStyle = 'rgba(150, 107, 252, 0.3)';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(0, height / 2);
        for (let x = 0; x < width; x++) {
          const y = height / 2 + Math.sin(x * 0.05 + time) * 3;
          ctx.lineTo(x, y);
        }
        ctx.stroke();
        
        // Reset smoothed data when not listening
        smoothedDataRef.current = new Array(32).fill(0);
      }

      animationRef.current = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [waveformData, isListening, audioLevel]);

  return (
    <canvas 
      ref={canvasRef} 
      width={320} 
      height={60} 
      className="microphone-waveform"
    />
  );
};

// Epic Audio Visualizer Canvas Component - One Development Colors
const AudioVisualizer = ({ amplitude, isSpeaking }) => {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const phaseRef = useRef(0);
  const barsRef = useRef(Array(32).fill(0));

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    const centerY = height / 2;
    const barCount = 32;
    const barWidth = width / barCount - 2;

    const draw = () => {
      // Clear with fade effect for trail
      ctx.fillStyle = 'rgba(10, 5, 16, 0.3)';
      ctx.fillRect(0, 0, width, height);
      
      if (isSpeaking) {
        // Epic bar visualizer
        for (let i = 0; i < barCount; i++) {
          // Smooth bar animation
          const targetHeight = (amplitude * 40) * (0.5 + Math.sin(phaseRef.current + i * 0.3) * 0.5);
          barsRef.current[i] += (targetHeight - barsRef.current[i]) * 0.3;
          
          const barHeight = Math.max(4, barsRef.current[i]);
          const x = i * (barWidth + 2);
          
          // Create gradient for each bar - One Development colors
          const gradient = ctx.createLinearGradient(x, centerY - barHeight, x, centerY + barHeight);
          gradient.addColorStop(0, '#D4AF37'); // Gold
          gradient.addColorStop(0.3, '#966bfc'); // Violet
          gradient.addColorStop(0.7, '#966bfc'); // Violet
          gradient.addColorStop(1, '#D4AF37'); // Gold
          
          ctx.fillStyle = gradient;
          
          // Draw mirrored bars
          ctx.beginPath();
          ctx.roundRect(x, centerY - barHeight, barWidth, barHeight, 2);
          ctx.roundRect(x, centerY, barWidth, barHeight, 2);
          ctx.fill();
          
          // Glow effect
          ctx.shadowColor = '#966bfc';
          ctx.shadowBlur = 15;
          ctx.fill();
          ctx.shadowBlur = 0;
        }
        
        // Center line glow
        const lineGradient = ctx.createLinearGradient(0, 0, width, 0);
        lineGradient.addColorStop(0, 'transparent');
        lineGradient.addColorStop(0.2, 'rgba(212, 175, 55, 0.8)');
        lineGradient.addColorStop(0.5, 'rgba(150, 107, 252, 1)');
        lineGradient.addColorStop(0.8, 'rgba(212, 175, 55, 0.8)');
        lineGradient.addColorStop(1, 'transparent');
        
        ctx.strokeStyle = lineGradient;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(0, centerY);
        ctx.lineTo(width, centerY);
        ctx.stroke();
        
        phaseRef.current += 0.15;
      } else {
        // Idle state - elegant wave
        ctx.beginPath();
        ctx.moveTo(0, centerY);
        
        for (let x = 0; x < width; x++) {
          const y = centerY + 
            Math.sin(x * 0.02 + phaseRef.current) * 4 +
            Math.sin(x * 0.01 + phaseRef.current * 0.5) * 2;
          ctx.lineTo(x, y);
        }
        
        const idleGradient = ctx.createLinearGradient(0, 0, width, 0);
        idleGradient.addColorStop(0, 'transparent');
        idleGradient.addColorStop(0.3, 'rgba(150, 107, 252, 0.4)');
        idleGradient.addColorStop(0.5, 'rgba(150, 107, 252, 0.6)');
        idleGradient.addColorStop(0.7, 'rgba(150, 107, 252, 0.4)');
        idleGradient.addColorStop(1, 'transparent');
        
        ctx.strokeStyle = idleGradient;
        ctx.lineWidth = 2;
        ctx.shadowColor = 'rgba(150, 107, 252, 0.5)';
        ctx.shadowBlur = 10;
        ctx.stroke();
        ctx.shadowBlur = 0;
        
        // Decay bars smoothly
        barsRef.current = barsRef.current.map(b => b * 0.9);
        
        phaseRef.current += 0.03;
      }
      
      animationRef.current = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [amplitude, isSpeaking]);

  return (
    <canvas 
      ref={canvasRef} 
      width={320} 
      height={70} 
      className="audio-visualizer"
    />
  );
};

// Suggestion Card with hover effects
const SuggestionCard = ({ icon, text, onClick, delay }) => (
  <button 
    className="luna-suggestion"
    onClick={onClick}
    style={{ animationDelay: `${delay * 150}ms` }}
  >
    <span className="suggestion-emoji">{icon}</span>
    <span className="suggestion-label">{text}</span>
  </button>
);

// Greeting messages that rotate (reserved for potential future onboarding UI)
const GREETINGS = [
  "Welcome to One Development",
  "How may I assist you today?",
  "Your luxury real estate awaits",
  "Let's find your dream property",
];

// Luna's voice - Shimmer (expressive female)
const LUNA_VOICE = 'shimmer';

// Main Component - Full Voice + Avatar Experience
const LunaFreeInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [lunaState, setLunaState] = useState('idle');
  const [showTextMode, setShowTextMode] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [suggestedQuestions, setSuggestedQuestions] = useState([]);
  const [latestResponse, setLatestResponse] = useState('');
  
  const speech = useEnhancedSpeech();
  const recognition = useSpeechRecognition();
  
  const messagesEndRef = useRef(null);

  // Initialize
  useEffect(() => {
    let sid = localStorage.getItem('luna_free_session');
    if (!sid) {
      sid = uuidv4();
      localStorage.setItem('luna_free_session', sid);
    }
    setSessionId(sid);
    loadSuggestions();
  }, []);

  // Update Luna's state
  useEffect(() => {
    if (speech.isSpeaking) {
      setLunaState('speaking');
    } else if (recognition.isListening) {
      setLunaState('listening');
    } else if (isProcessing) {
      setLunaState('thinking');
    } else {
      setLunaState('idle');
    }
  }, [speech.isSpeaking, recognition.isListening, isProcessing]);

  // Sync transcript to input
  useEffect(() => {
    const text = recognition.transcript || recognition.interimTranscript;
    if (text) setInputText(text);
  }, [recognition.transcript, recognition.interimTranscript]);

  const loadSuggestions = async () => {
    try {
      const questions = await chatService.getSuggestedQuestions(4);
      setSuggestedQuestions(questions);
    } catch {
      setSuggestedQuestions([
        { id: 1, question: "Tell me about One Development" },
        { id: 2, question: "What projects are available?" },
        { id: 3, question: "What are the payment plans?" },
        { id: 4, question: "Where are you located?" }
      ]);
    }
  };

  const sendMessage = async (text) => {
    if (!text?.trim() || isProcessing) return;

    const messageText = text.trim();
    setInputText('');
    recognition.clearTranscript();
    setIsProcessing(true);

    // Add user message
    const userMsg = {
      id: uuidv4(),
      type: 'user',
      content: messageText,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMsg]);

    try {
      const response = await chatService.sendMessage(messageText, sessionId);
      const responseText = response.response;

      // Add Luna's response
      const lunaMsg = {
        id: uuidv4(),
        type: 'assistant',
        content: responseText,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, lunaMsg]);
      setLatestResponse(responseText);

      // Speak the response with Luna's voice
      speech.speak(responseText, null, LUNA_VOICE);

    } catch (err) {
      console.error('Error:', err);
      const errorMsg = "I'm having trouble connecting. Please try again.";
      setMessages(prev => [...prev, {
        id: uuidv4(),
        type: 'assistant',
        content: errorMsg,
        timestamp: new Date(),
      }]);
      speech.speak(errorMsg, null, LUNA_VOICE);
    } finally {
      setIsProcessing(false);
    }

    setTimeout(() => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }), 100);
  };

  const handleMicClick = () => {
    console.log('Mic clicked - state:', { 
      isListening: recognition.isListening, 
      isSpeaking: speech.isSpeaking,
      isProcessing,
      isSupported: recognition.isSupported 
    });
    
    if (recognition.isListening) {
      recognition.stopListening();
      // Send if we have text
      const textToSend = recognition.transcript || recognition.interimTranscript;
      if (textToSend?.trim()) {
        setTimeout(() => sendMessage(textToSend), 300);
      }
    } else if (speech.isSpeaking) {
      speech.stop();
    } else {
      // Start listening
      if (!recognition.isSupported) {
        alert('Speech recognition is not supported in your browser. Please use Chrome or Edge.');
        return;
      }
      const started = recognition.startListening();
      console.log('Started listening:', started);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputText.trim()) {
      sendMessage(inputText);
    }
  };

  const icons = ['✨', '🏛️', '💎', '🌟'];

  return (
    <div className="luna-free-container">
      {/* Background Effects */}
      <div className="luna-background">
        <div className="bg-gradient bg-1"></div>
        <div className="bg-gradient bg-2"></div>
        <div className="bg-gradient bg-3"></div>
        <div className="bg-particles"></div>
        <div className="bg-grid"></div>
      </div>

      {/* Header */}
      <header className="luna-top-bar">
        <img src="/onedev-logo.svg" alt="One Development" className="company-logo" />
        <div className="top-bar-actions">
          <button 
            className={`action-btn ${showHistory ? 'on' : ''}`}
            onClick={() => setShowHistory(!showHistory)}
          >
            💬
          </button>
          <button 
            className={`action-btn ${showTextMode ? 'on' : ''}`}
            onClick={() => setShowTextMode(!showTextMode)}
          >
            {showTextMode ? '🎤' : '⌨️'}
          </button>
        </div>
      </header>

      {/* Main Area */}
      <main className="luna-content">
        {/* Avatar Section */}
        <section className="avatar-section">
          {/* Animated Avatar */}
          <div className={`luna-avatar ${lunaState}`}>
            {/* Outer rings */}
            <div className="avatar-ring ring-1"></div>
            <div className="avatar-ring ring-2"></div>
            <div className="avatar-ring ring-3"></div>
            
            {/* Main avatar container */}
            <div className="avatar-core">
              <img src="/Luna.png" alt="Luna" className="avatar-image" />

              {/* Simple mouth overlay driven by viseme data for a subtle lip-sync effect */}
              <div
                className="avatar-mouth"
                style={{
                  transform: `translate(-50%, -50%) scaleX(${0.8 + speech.mouthWidth * 0.4}) scaleY(${0.3 + speech.mouthOpen * 0.7})`,
                  opacity: speech.isSpeaking ? 1 : 0,
                }}
              ></div>
              
              {/* Speech intensity glow - pulses with speech amplitude */}
              <div 
                className="speech-glow" 
                style={{ 
                  opacity: speech.isSpeaking ? 0.4 + speech.mouthOpen * 0.5 : 0,
                  transform: `scale(${speech.isSpeaking ? 1 + speech.mouthOpen * 0.15 : 1})`
                }}
              ></div>
              
              {/* Glow effect */}
              <div className="avatar-glow"></div>
            </div>

            {/* Floating particles - Epic count */}
            <div className="avatar-particles">
              {[...Array(16)].map((_, i) => (
                <span key={i} className="particle" style={{ '--i': i }}></span>
              ))}
            </div>
          </div>

          {/* Audio Visualizer */}
          <AudioVisualizer 
            amplitude={speech.amplitude} 
            isSpeaking={speech.isSpeaking} 
          />

          {/* Status */}
          <div className="luna-status-bar">
            <span className={`status-indicator ${lunaState}`}></span>
            <span className="status-label">
              {lunaState === 'idle' && '✨ Ready'}
              {lunaState === 'listening' && '🎤 Listening...'}
              {lunaState === 'thinking' && '🧠 Thinking...'}
              {lunaState === 'speaking' && '💬 Speaking...'}
            </span>
          </div>

          {/* Identity */}
          <div className="luna-identity">
            <h1 className="luna-title">
              Luna <span className="moon">🌙</span>
            </h1>
            <p className="luna-tagline">AI Assistant • One Development</p>
          </div>

          {/* Current word being spoken */}
          {speech.isSpeaking && speech.currentWord && (
            <div className="speaking-word">{speech.currentWord}</div>
          )}
        </section>

        {/* Interaction Section */}
        <section className="interaction-section">
          {/* Voice Button - Always show, with fallback for unsupported browsers */}
          {!showTextMode && (
            <button 
              className={`mic-button ${lunaState}`}
              onClick={handleMicClick}
              disabled={isProcessing && !speech.isSpeaking && !recognition.isListening}
            >
              <div className="mic-inner">
                {recognition.isListening && <div className="mic-pulse"></div>}
                <span className="mic-icon">
                  {recognition.isListening ? '🎤' : speech.isSpeaking ? '⏹' : '🎤'}
                </span>
                <span className="mic-label">
                  {!recognition.isSupported 
                    ? 'Not supported' 
                    : recognition.isListening 
                      ? 'Tap to send' 
                      : speech.isSpeaking 
                        ? 'Stop' 
                        : 'Tap to speak'}
                </span>
              </div>
            </button>
          )}

          {/* Live transcript */}
          {recognition.isListening && (inputText || recognition.interimTranscript) && (
            <div className="live-transcript">
              {inputText || recognition.interimTranscript}
              <span className="transcript-cursor">|</span>
            </div>
          )}

          {/* Text input - always available */}
          <form className="text-form" onSubmit={handleSubmit}>
            <input
              type="text"
              className="text-input"
              placeholder={showTextMode || !recognition.isSupported ? "Type your message..." : "Or type here..."}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              disabled={isProcessing}
            />
            <button 
              type="submit" 
              className="send-btn"
              disabled={isProcessing || !inputText.trim()}
            >
              Send →
            </button>
          </form>

          {/* Suggestions */}
          {!recognition.isListening && !isProcessing && messages.length === 0 && (
            <div className="suggestions-area">
              <p className="suggestions-title">Try asking:</p>
              <div className="suggestions-grid">
                {suggestedQuestions.map((q, i) => (
                  <SuggestionCard
                    key={q.id || i}
                    icon={icons[i % icons.length]}
                    text={q.question}
                    onClick={() => sendMessage(q.question)}
                    delay={i * 80}
                  />
                ))}
              </div>
            </div>
          )}
        </section>
      </main>

      {/* Chat History Sidebar */}
      {showHistory && (
        <aside className="history-sidebar">
          <div className="sidebar-head">
            <h3>Chat History</h3>
            <button className="close-sidebar" onClick={() => setShowHistory(false)}>✕</button>
          </div>
          <div className="sidebar-body">
            {messages.length === 0 ? (
              <p className="empty-history">Start a conversation with Luna!</p>
            ) : (
              messages.map(msg => (
                <div key={msg.id} className={`history-msg ${msg.type}`}>
                  <span className="msg-icon">{msg.type === 'user' ? '👤' : '🌙'}</span>
                  <div className="msg-text">
                    {msg.type === 'assistant' ? (
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    ) : (
                      msg.content
                    )}
                  </div>
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>
        </aside>
      )}

      {/* Footer */}
      <footer className="luna-bottom-bar">
        <span className="free-badge">🆓 100% Free • No API Keys Required</span>
        <span className="powered-by">Powered by One Development AI</span>
      </footer>
    </div>
  );
};

// Minimal "Avatar Only" Interface - photorealistic Luna, listening indicator, and suggested questions
const LunaAvatarInterface = () => {
  const [sessionId, setSessionId] = useState(null);
  const [lunaState, setLunaState] = useState('idle');
  const [suggestedQuestions, setSuggestedQuestions] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentVideoUrl, setCurrentVideoUrl] = useState(null);
  const [lastVideoUrl, setLastVideoUrl] = useState(null); // Store last video for replay
  const [lastResponseText, setLastResponseText] = useState(null); // Store last response for audio replay
  const [isVideoPlaying, setIsVideoPlaying] = useState(false);
  // Avatar service - enabled for SadTalker video generation
  const [avatarServiceAvailable, setAvatarServiceAvailable] = useState(false);
  const [videoProgress, setVideoProgress] = useState(0);
  const [isGeneratingVideo, setIsGeneratingVideo] = useState(false);
  const [inputText, setInputText] = useState(''); // Text input state
  const [micPermission, setMicPermission] = useState('pending'); // 'pending', 'granted', 'denied'
  const [debugTranscript, setDebugTranscript] = useState(''); // For debugging
  const videoRef = useRef(null);
  const progressIntervalRef = useRef(null);
  const autoRestartTimeoutRef = useRef(null);
  const sendMessageRef = useRef(null);

  const speech = useEnhancedSpeech();
  
  // Auto-send callback for speech recognition
  const handleAutoSend = useCallback((text) => {
    console.log('📤 Auto-sending:', text);
    setDebugTranscript(text); // Show what was heard
    // Clear debug after 3 seconds
    setTimeout(() => setDebugTranscript(''), 3000);
    
    if (sendMessageRef.current && !isProcessing) {
      sendMessageRef.current(text);
    }
  }, [isProcessing]);

  const recognition = useSpeechRecognition(handleAutoSend);

  // Request microphone permission on mount
  useEffect(() => {
    const requestMicPermission = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        // Permission granted - keep the stream active for continuous listening
        stream.getTracks().forEach(track => track.stop());
        setMicPermission('granted');
        console.log('Microphone permission granted');
      } catch (err) {
        console.error('Microphone permission error:', err);
        setMicPermission('denied');
      }
    };

    requestMicPermission();
  }, []);

  // Auto-start listening when permission is granted and not busy
  useEffect(() => {
    if (micPermission === 'granted' && 
        recognition.isSupported && 
        !recognition.isListening && 
        !isProcessing && 
        !speech.isSpeaking && 
        !isVideoPlaying &&
        !isGeneratingVideo) {
      // Small delay to avoid rapid restarts
      autoRestartTimeoutRef.current = setTimeout(() => {
        recognition.startListening();
      }, 500);
    }

    return () => {
      if (autoRestartTimeoutRef.current) {
        clearTimeout(autoRestartTimeoutRef.current);
      }
    };
  }, [micPermission, recognition.isSupported, recognition.isListening, isProcessing, speech.isSpeaking, isVideoPlaying, isGeneratingVideo, recognition]);

  // Init session & suggestions
  useEffect(() => {
    let sid = localStorage.getItem('luna_avatar_session');
    if (!sid) {
      sid = uuidv4();
      localStorage.setItem('luna_avatar_session', sid);
    }
    setSessionId(sid);

    const loadSuggestions = async () => {
      try {
        const questions = await chatService.getSuggestedQuestions(4);
        setSuggestedQuestions(questions);
      } catch {
        setSuggestedQuestions([
          { id: 1, question: "Tell me about One Development" },
          { id: 2, question: "What projects are available right now?" },
          { id: 3, question: "What are the payment plans?" },
          { id: 4, question: "Where are your flagship developments located?" },
        ]);
      }
    };

    // Check if avatar service (SadTalker) is available
    const checkAvatarService = async () => {
      try {
        const health = await chatService.avatarHealth();
        if (health.status === 'healthy') {
          console.log('✅ Avatar service available:', health);
          setAvatarServiceAvailable(true);
        } else {
          console.log('⚠️ Avatar service not available, using TTS fallback');
          setAvatarServiceAvailable(false);
        }
      } catch (error) {
        console.log('⚠️ Avatar service check failed, using TTS fallback:', error);
        setAvatarServiceAvailable(false);
      }
    };

    loadSuggestions();
    checkAvatarService(); // Check on startup
  }, []);

  // Track Luna's high-level state
  useEffect(() => {
    if (isVideoPlaying || speech.isSpeaking) {
      setLunaState('speaking');
    } else if (recognition.isListening) {
      setLunaState('listening');
    } else if (isProcessing || isGeneratingVideo) {
      setLunaState('thinking');
    } else {
      setLunaState('idle');
    }
  }, [speech.isSpeaking, recognition.isListening, isProcessing, isVideoPlaying, isGeneratingVideo]);

  // Keep sendMessage ref updated for auto-send callback
  useEffect(() => {
    sendMessageRef.current = (text) => {
      if (!text?.trim() || !sessionId || isProcessing) return;
      recognition.stopListening();
      recognition.clearTranscript();
      // Use setTimeout to avoid state issues
      setTimeout(() => {
        sendMessageInternal(text);
      }, 100);
    };
  });

  const sendMessageInternal = useCallback(
    async (messageText) => {
      if (!messageText?.trim() || !sessionId) return;
      if (isProcessing) return;

      const text = messageText.trim();
      setIsProcessing(true);

      try {
        const response = await chatService.sendMessage(text, sessionId);
        const responseText = response.response;

        // Try to generate photorealistic avatar video if service is available
        if (avatarServiceAvailable) {
          try {
            // IMPORTANT: Clear old video and audio FIRST
            setCurrentVideoUrl(null);
            // Stop any currently playing speech
            if (speech.isSpeaking) {
              window.speechSynthesis?.cancel();
            }
            
            // Start progress simulation
            setIsGeneratingVideo(true);
            setVideoProgress(0);
            
            // Simulate progress (since we don't have real progress from backend)
            progressIntervalRef.current = setInterval(() => {
              setVideoProgress(prev => {
                if (prev >= 95) return 95; // Stop at 95% until video arrives
                return prev + 1;
              });
            }, 600); // Update every 600ms (60 seconds total to reach 95%)
            
            const avatarResult = await chatService.generateAvatar(responseText, null, 'default', 'fast');
            
            // Clear progress interval
            if (progressIntervalRef.current) {
              clearInterval(progressIntervalRef.current);
            }
            
            if (avatarResult.fallback) {
              // Avatar service failed, use TTS fallback
              console.log('Avatar generation failed, using TTS:', avatarResult.error);
              setIsGeneratingVideo(false);
              setVideoProgress(0);
              // Only speak if video generation completely failed
              speech.speak(responseText, null, LUNA_VOICE);
            } else {
              // Got video! Play it - DO NOT SPEAK, video has audio!
              console.log('Avatar video generated:', avatarResult.video_url);
              setVideoProgress(100);
              
              // Store video URL for replay and set as current
              setTimeout(() => {
                setLastVideoUrl(avatarResult.video_url); // Save for replay
                setCurrentVideoUrl(avatarResult.video_url);
                setIsGeneratingVideo(false);
                setVideoProgress(0);
              }, 100);
              
              // DO NOT CALL speech.speak() - video has audio!
            }
          } catch (avatarError) {
            console.error('Avatar generation error:', avatarError);
            // Clear progress and fallback to TTS only if error
            if (progressIntervalRef.current) {
              clearInterval(progressIntervalRef.current);
            }
            setIsGeneratingVideo(false);
            setVideoProgress(0);
            // Only speak if there was an error
            speech.speak(responseText, null, LUNA_VOICE);
          }
        } else {
          // Avatar service not available, use TTS
          setLastResponseText(responseText); // Save for replay
          speech.speak(responseText, null, LUNA_VOICE);
        }
      } catch (err) {
        console.error('Avatar interface error:', err);
        speech.speak("I'm having trouble connecting right now. Please try again in a moment.", null, LUNA_VOICE);
      } finally {
        setIsProcessing(false);
      }
    },
    [isProcessing, sessionId, speech, avatarServiceAvailable, LUNA_VOICE]
  );

  // Alias for compatibility
  const sendMessage = sendMessageInternal;

  const handleAvatarClick = () => {
    // If speaking, stop speech (will auto-resume listening)
    if (speech.isSpeaking) {
      speech.stop();
      return;
    }

    // If we have a transcript, send it
    const textToSend = recognition.transcript || recognition.interimTranscript;
    if (textToSend?.trim()) {
      recognition.stopListening();
      setInputText('');
      setTimeout(() => sendMessage(textToSend), 100);
    }
  };

  const handleSuggestionClick = (q) => {
    if (!q) return;
    if (speech.isSpeaking) speech.stop();
    if (recognition.isListening) recognition.stopListening();
    sendMessage(q);
  };

  // Handle text form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputText.trim()) {
      if (speech.isSpeaking) speech.stop();
      if (recognition.isListening) recognition.stopListening();
      sendMessage(inputText);
      setInputText('');
    }
  };

  // Sync voice transcript to text input
  useEffect(() => {
    const text = recognition.transcript || recognition.interimTranscript;
    if (text) setInputText(text);
  }, [recognition.transcript, recognition.interimTranscript]);

  // Auto-send when a final transcript is received
  useEffect(() => {
    if (recognition.transcript && recognition.transcript.trim() && !isProcessing) {
      // Small delay to allow for any additional words
      const sendTimeout = setTimeout(() => {
        const textToSend = recognition.transcript.trim();
        if (textToSend) {
          setInputText('');
          recognition.clearTranscript();
          sendMessage(textToSend);
        }
      }, 1000); // Wait 1 second after final transcript before sending

      return () => clearTimeout(sendTimeout);
    }
  }, [recognition.transcript, recognition, isProcessing, sendMessage]);

  // Replay the last answer (video or audio)
  const handleReplay = () => {
    // Stop any ongoing processes
    if (speech.isSpeaking) speech.stop();
    if (recognition.isListening) recognition.stopListening();
    
    // If we have a video, replay it
    if (lastVideoUrl) {
      setCurrentVideoUrl(lastVideoUrl);
      setIsVideoPlaying(true);
      
      // Force video to play from start
      setTimeout(() => {
        if (videoRef.current) {
          videoRef.current.currentTime = 0;
          videoRef.current.play().catch(err => {
            console.error('Replay error:', err);
            setIsVideoPlaying(false);
          });
        }
      }, 50);
    } 
    // Otherwise replay the audio response
    else if (lastResponseText) {
      speech.speak(lastResponseText, null, LUNA_VOICE);
    }
  };
  
  // Check if replay is available
  const canReplay = (lastVideoUrl || lastResponseText) && !currentVideoUrl && !isGeneratingVideo && !isProcessing && !speech.isSpeaking;

  const statusLabel = (() => {
    if (!recognition.isSupported) return 'Voice not supported in this browser';
    if (micPermission === 'pending') return 'Requesting microphone access...';
    if (micPermission === 'denied') return '🎤 Microphone access denied - please allow in browser settings';
    if (lunaState === 'listening') return '🎤 Listening... (tap Luna to send)';
    if (isVideoPlaying || currentVideoUrl) return '🎬 Luna is speaking...';
    if (lunaState === 'speaking') return '💬 Answering...';
    if (isGeneratingVideo) return `🎬 Generating video... ${videoProgress}%`;
    if (lunaState === 'thinking') return '🧠 Thinking...';
    return '🎤 Ready to listen...';
  })();

  return (
    <div className="luna-free-container avatar-only">
      {/* Soft cosmic background */}
      <div className="luna-background">
        <div className="bg-gradient bg-1"></div>
        <div className="bg-gradient bg-2"></div>
        <div className="bg-gradient bg-3"></div>
        <div className="bg-particles"></div>
        <div className="bg-grid"></div>
      </div>

      <main className="luna-content avatar-only-content">
        <section className="avatar-section avatar-only-section">
          <div
            className={`luna-avatar ${lunaState}`}
            onClick={handleAvatarClick}
          >
            <div className="avatar-ring ring-1"></div>
            <div className="avatar-ring ring-2"></div>
            <div className="avatar-ring ring-3"></div>

            <div className="avatar-core">
              {/* Show video if available, otherwise static image */}
              {currentVideoUrl ? (
                <video
                  ref={videoRef}
                  src={currentVideoUrl}
                  className="avatar-video"
                  autoPlay
                  loop={false}
                  muted={false}
                  playsInline
                  onPlay={() => {
                    console.log('Video started playing');
                    setIsVideoPlaying(true);
                  }}
                  onEnded={() => {
                    console.log('Video ended');
                    setIsVideoPlaying(false);
                    setCurrentVideoUrl(null);
                  }}
                  onPause={() => setIsVideoPlaying(false)}
                  onError={(e) => {
                    console.error('Video playback error:', e);
                    setIsVideoPlaying(false);
                    setCurrentVideoUrl(null);
                  }}
                />
              ) : (
                <img src="/Luna.png" alt="Luna" className="avatar-image" />
              )}

              {/* Mouth overlay disabled - looks unnatural with static image */}

              <div
                className="speech-glow"
                style={{
                  opacity: speech.isSpeaking ? 0.4 + speech.mouthOpen * 0.5 : 0,
                  transform: `scale(${speech.isSpeaking ? 1 + speech.mouthOpen * 0.15 : 1})`,
                }}
              ></div>

              <div className="avatar-glow"></div>
            </div>

            <div className="avatar-particles">
              {[...Array(16)].map((_, i) => (
                <span key={i} className="particle" style={{ '--i': i }}></span>
              ))}
            </div>
          </div>

          {/* Listening / speaking indicator */}
          <div className="luna-status-bar avatar-only-status">
            <span className={`status-indicator ${lunaState}`}></span>
            <span className="status-label">{statusLabel}</span>
          </div>

          {/* Voice Waveform Visualization */}
          {recognition.isListening && (
            <div className="voice-waveform-container">
              <MicrophoneWaveform 
                waveformData={recognition.waveformData} 
                isListening={recognition.isListening}
                audioLevel={recognition.audioLevel}
              />
            </div>
          )}

          {/* Live Transcript Display (Debug) */}
          {(recognition.transcript || recognition.interimTranscript || debugTranscript) && (
            <div className="live-transcript-debug">
              <span className="transcript-label">🎤 Heard:</span>
              <span className="transcript-text">
                {debugTranscript || recognition.transcript || recognition.interimTranscript}
              </span>
              {!debugTranscript && recognition.interimTranscript && (
                <span className="transcript-interim">...</span>
              )}
            </div>
          )}

          {/* Replay Button - shows when there's a previous answer and not currently playing */}
          {canReplay && (
            <button 
              className="replay-button"
              onClick={handleReplay}
              title="Replay last answer"
            >
              <svg 
                viewBox="0 0 24 24" 
                fill="none" 
                stroke="currentColor" 
                strokeWidth="2" 
                strokeLinecap="round" 
                strokeLinejoin="round"
                className="replay-icon"
              >
                <polygon points="5 3 19 12 5 21 5 3" />
              </svg>
              <span>Replay Answer</span>
            </button>
          )}

          {/* Video Generation Progress */}
          {isGeneratingVideo && (
            <div className="video-progress-container">
              <div className="video-progress-label">
                Generating photorealistic video... {Math.round(videoProgress)}%
              </div>
              <div className="video-progress-bar">
                <div 
                  className="video-progress-fill" 
                  style={{ width: `${videoProgress}%` }}
                ></div>
              </div>
            </div>
          )}

          {/* Suggested questions under the avatar */}
          {suggestedQuestions && suggestedQuestions.length > 0 && (
            <div className="avatar-only-suggestions">
              {suggestedQuestions.map((q, index) => (
                <button
                  key={q.id || index}
                  className="avatar-only-suggestion"
                  onClick={() => handleSuggestionClick(q.question)}
                  disabled={isProcessing}
                >
                  {q.question}
                </button>
              ))}
            </div>
          )}

          {/* Text input form */}
          <form className="text-form avatar-text-form" onSubmit={handleSubmit}>
            <input
              type="text"
              className="text-input"
              placeholder="Or type your message here..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              disabled={isProcessing}
            />
            <button 
              type="submit" 
              className="send-btn"
              disabled={isProcessing || !inputText.trim()}
            >
              Send →
            </button>
          </form>
        </section>
      </main>
    </div>
  );
};

export { LunaAvatarInterface };
export default LunaFreeInterface;

