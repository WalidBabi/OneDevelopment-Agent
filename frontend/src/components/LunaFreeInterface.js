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

// Enhanced Web Speech Hook with better voice selection and realistic (but gentle) lip sync
const useEnhancedSpeech = () => {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [currentWord, setCurrentWord] = useState('');
  const [speechProgress, setSpeechProgress] = useState(0);
  const [amplitude, setAmplitude] = useState(0);
  const [viseme, setViseme] = useState(VISEME_MAP.silence);
  const [mouthOpen, setMouthOpen] = useState(0);
  const [mouthWidth, setMouthWidth] = useState(0.5);
  const utteranceRef = useRef(null);
  const animationFrameRef = useRef(null);
  const visemeIndexRef = useRef(0);
  const textForVisemeRef = useRef('');
  const startTimeRef = useRef(0);

  const getVoices = () => {
    return new Promise((resolve) => {
      let voices = window.speechSynthesis?.getVoices();
      if (voices?.length) {
        resolve(voices);
      } else {
        window.speechSynthesis?.addEventListener('voiceschanged', () => {
          voices = window.speechSynthesis.getVoices();
          resolve(voices);
        }, { once: true });
        setTimeout(() => resolve(window.speechSynthesis?.getVoices() || []), 100);
      }
    });
  };

  const findBestVoice = async () => {
    const voices = await getVoices();
    
    // Priority: Neural/Natural voices first (more realistic)
    const preferredVoices = [
      // Microsoft Neural voices (best quality)
      'Microsoft Aria Online (Natural)',
      'Microsoft Jenny Online (Natural)',
      'Microsoft Aria Online',
      'Microsoft Jenny',
      'Microsoft Zira',
      // Google voices (good quality)
      'Google UK English Female',
      'Google US English',
      // Apple voices
      'Samantha',
      'Karen',
      'Moira',
      'Tessa',
      'Fiona',
      // Other quality voices
      'Zira',
      'Helena',
      'Victoria',
    ];

    for (const preferred of preferredVoices) {
      const voice = voices.find(v => 
        v.name.toLowerCase().includes(preferred.toLowerCase())
      );
      if (voice) return voice;
    }

    // Fallback: prioritize voices with "natural" or "neural" in name
    const neuralVoice = voices.find(v => 
      v.lang.startsWith('en') && 
      (v.name.toLowerCase().includes('natural') || 
       v.name.toLowerCase().includes('neural'))
    );
    if (neuralVoice) return neuralVoice;

    const englishFemale = voices.find(v => 
      v.lang.startsWith('en') && 
      (v.name.toLowerCase().includes('female') || 
       v.name.toLowerCase().includes('woman') ||
       /samantha|karen|zira|victoria|helena|moira/i.test(v.name))
    );
    if (englishFemale) return englishFemale;

    return voices.find(v => v.lang.startsWith('en')) || voices[0];
  };

  // Animate lip sync based on text timing
  const animateLipSync = useCallback((text, duration) => {
    const chars = text.replace(/[^a-zA-Z\s]/g, '').split('');
    const charDuration = duration / Math.max(chars.length, 1);
    let charIndex = 0;
    let lastViseme = VISEME_MAP.silence;
    
    const animate = () => {
      const elapsed = Date.now() - startTimeRef.current;
      charIndex = Math.min(Math.floor(elapsed / charDuration), chars.length - 1);
      
      const char = chars[charIndex] || ' ';
      const targetViseme = charToViseme(char);
      
      // Smooth interpolation between visemes for natural movement
      const smoothing = 0.25;
      const newMouthOpen = lastViseme.mouthOpen + (targetViseme.mouthOpen - lastViseme.mouthOpen) * smoothing;
      const newMouthWidth = lastViseme.mouthWidth + (targetViseme.mouthWidth - lastViseme.mouthWidth) * smoothing;
      
      // Add subtle natural variation
      const variation = Math.sin(elapsed * 0.01) * 0.05;
      
      setMouthOpen(Math.max(0, Math.min(1, newMouthOpen + variation)));
      setMouthWidth(Math.max(0.2, Math.min(1, newMouthWidth)));
      setAmplitude(newMouthOpen * 0.8 + 0.2);
      
      lastViseme = { mouthOpen: newMouthOpen, mouthWidth: newMouthWidth };
      
      if (elapsed < duration) {
        animationFrameRef.current = requestAnimationFrame(animate);
      }
    };
    
    startTimeRef.current = Date.now();
    animate();
  }, []);

  const speak = useCallback(async (rawText, onEnd) => {
    if (!window.speechSynthesis) {
      console.warn('Speech synthesis not supported');
      onEnd?.();
      return;
    }

    // Cancel any ongoing speech
    window.speechSynthesis.cancel();
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }

    // Sanitize text for natural speech
    const text = sanitizeTextForSpeech(rawText);
    if (!text) {
      onEnd?.();
      return;
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utteranceRef.current = utterance;
    textForVisemeRef.current = text;

    // Get the best available voice
    const voice = await findBestVoice();
    if (voice) {
      utterance.voice = voice;
      console.log('Using voice:', voice.name);
    }

    // Natural but calm speech settings - keep fairly consistent (light monotony)
    utterance.rate = 0.95;   // slightly slower than default for clarity
    utterance.pitch = 1.0;   // neutral pitch to avoid robotic swings
    utterance.volume = 1.0;

    const words = text.split(' ');
    let wordIndex = 0;
    let estimatedDuration = text.length * 65; // ~65ms per character estimate

    utterance.onboundary = (event) => {
      if (event.name === 'word') {
        const word = words[wordIndex] || '';
        setCurrentWord(word);
        wordIndex++;
        setSpeechProgress((wordIndex / words.length) * 100);
      }
    };

    utterance.onstart = () => {
      setIsSpeaking(true);
      // Start lip sync animation
      animateLipSync(text, estimatedDuration);
    };

    utterance.onend = () => {
      setIsSpeaking(false);
      setCurrentWord('');
      setSpeechProgress(0);
      setAmplitude(0);
      setMouthOpen(0);
      setMouthWidth(0.5);
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      onEnd?.();
    };

    utterance.onerror = (event) => {
      console.error('Speech error:', event);
      setIsSpeaking(false);
      setAmplitude(0);
      setMouthOpen(0);
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      onEnd?.();
    };

    window.speechSynthesis.speak(utterance);
  }, [animateLipSync]);

  const stop = useCallback(() => {
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
    isSupported: !!window.speechSynthesis 
  };
};

// Speech Recognition Hook
const useSpeechRecognition = () => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [error, setError] = useState(null);
  const recognitionRef = useRef(null);
  const isInitializedRef = useRef(false);

  const isSupported = typeof window !== 'undefined' && 
    (window.SpeechRecognition || window.webkitSpeechRecognition);

  // Initialize recognition on mount
  useEffect(() => {
    if (!isSupported || isInitializedRef.current) return;

    try {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
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
        
        if (final) {
          setTranscript(final);
          setInterimTranscript('');
        } else {
          setInterimTranscript(interim);
        }
      };

      recognitionRef.current.onend = () => {
        console.log('Speech recognition ended');
        setIsListening(false);
      };
      
      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setError(event.error);
        setIsListening(false);
        
        // Handle specific errors
        if (event.error === 'not-allowed') {
          alert('Microphone access denied. Please allow microphone access and reload the page.');
        } else if (event.error === 'no-speech') {
          // No speech detected, just reset silently
          console.log('No speech detected');
        }
      };

      recognitionRef.current.onaudiostart = () => {
        console.log('Audio capture started');
      };

      isInitializedRef.current = true;
      console.log('Speech recognition initialized successfully');
    } catch (e) {
      console.error('Failed to initialize speech recognition:', e);
      setError('initialization_failed');
    }

    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch (e) {
          // Ignore abort errors
        }
      }
    };
  }, [isSupported]);

  const startListening = useCallback(() => {
    if (!recognitionRef.current) {
      console.error('Speech recognition not initialized');
      setError('not_initialized');
      return false;
    }
    
    // Reset state
    setTranscript('');
    setInterimTranscript('');
    setError(null);
    setIsListening(true); // Set immediately for UI feedback
    
    try {
      // Stop any existing session first
      try {
        recognitionRef.current.abort();
      } catch (e) {
        // Ignore abort errors
      }
      
      // Start fresh after a tiny delay to ensure clean state
      requestAnimationFrame(() => {
        try {
          recognitionRef.current.start();
          console.log('Speech recognition started successfully');
        } catch (e) {
          console.error('Failed to start recognition:', e);
          setIsListening(false);
          setError('start_failed');
          
          // If it's an "already started" error, try again
          if (e.message?.includes('already started')) {
            try {
              recognitionRef.current.stop();
              setTimeout(() => {
                try {
                  recognitionRef.current.start();
                  setIsListening(true);
                } catch (e2) {
                  console.error('Retry failed:', e2);
                }
              }, 200);
            } catch (e2) {
              console.error('Stop failed:', e2);
            }
          }
        }
      });
      
      return true;
    } catch (e) {
      console.error('Recognition start error:', e);
      setIsListening(false);
      setError('start_failed');
      return false;
    }
  }, []);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (e) {
        // Ignore stop errors
      }
    }
    setIsListening(false);
  }, []);

  const clearTranscript = useCallback(() => {
    setTranscript('');
    setInterimTranscript('');
  }, []);

  return { 
    isListening, 
    transcript, 
    interimTranscript,
    startListening, 
    stopListening, 
    clearTranscript,
    isSupported,
    error
  };
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

      // Speak the response
      speech.speak(responseText);

    } catch (err) {
      console.error('Error:', err);
      const errorMsg = "I'm having trouble connecting. Please try again.";
      setMessages(prev => [...prev, {
        id: uuidv4(),
        type: 'assistant',
        content: errorMsg,
        timestamp: new Date(),
      }]);
      speech.speak(errorMsg);
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
  const [avatarServiceAvailable, setAvatarServiceAvailable] = useState(false);
  const [videoProgress, setVideoProgress] = useState(0);
  const [isGeneratingVideo, setIsGeneratingVideo] = useState(false);
  const videoRef = useRef(null);
  const progressIntervalRef = useRef(null);

  const speech = useEnhancedSpeech();
  const recognition = useSpeechRecognition();

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

    // Check if avatar service is available
    const checkAvatarService = async () => {
      try {
        const health = await chatService.avatarHealth();
        setAvatarServiceAvailable(health.status === 'healthy');
        console.log('Avatar service status:', health.status);
      } catch {
        setAvatarServiceAvailable(false);
        console.log('Avatar service unavailable, using fallback TTS');
      }
    };

    loadSuggestions();
    checkAvatarService();
  }, []);

  // Track Luna's high-level state
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

  const sendMessage = useCallback(
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
              speech.speak(responseText);
            } else {
              // Got video! Play it - DO NOT SPEAK, video has audio!
              console.log('Avatar video generated:', avatarResult.video_url);
              setVideoProgress(100);
              
              // Set new video URL - this will play the video with its audio
              setTimeout(() => {
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
            speech.speak(responseText);
          }
        } else {
          // Avatar service not available, use TTS
          speech.speak(responseText);
        }
      } catch (err) {
        console.error('Avatar interface error:', err);
        speech.speak("I'm having trouble connecting right now. Please try again in a moment.");
      } finally {
        setIsProcessing(false);
      }
    },
    [isProcessing, sessionId, speech, avatarServiceAvailable]
  );

  const handleAvatarClick = () => {
    if (!recognition.isSupported) {
      alert('Speech recognition is not supported in this browser. Please use Chrome or Edge for the full Luna experience.');
      return;
    }

    // If currently listening, stop and send what we heard
    if (recognition.isListening) {
      recognition.stopListening();
      const textToSend = recognition.transcript || recognition.interimTranscript;
      if (textToSend?.trim()) {
        setTimeout(() => sendMessage(textToSend), 300);
      }
      return;
    }

    // If speaking, stop speech
    if (speech.isSpeaking) {
      speech.stop();
      return;
    }

    // Otherwise, start listening
    recognition.startListening();
  };

  const handleSuggestionClick = (q) => {
    if (!q) return;
    if (speech.isSpeaking) speech.stop();
    if (recognition.isListening) recognition.stopListening();
    sendMessage(q);
  };

  const statusLabel = (() => {
    if (!recognition.isSupported) return 'Voice not supported in this browser';
    if (lunaState === 'listening') return 'Listening...';
    if (lunaState === 'speaking') return 'Answering...';
    if (lunaState === 'thinking') return 'Thinking...';
    return 'Tap on Luna and speak';
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
                  onEnded={() => setCurrentVideoUrl(null)}
                  onError={(e) => {
                    console.error('Video playback error:', e);
                    setCurrentVideoUrl(null);
                  }}
                />
              ) : (
                <img src="/Luna.png" alt="Luna" className="avatar-image" />
              )}

              {/* Lip sync overlay - only show when using TTS fallback */}
              {!currentVideoUrl && (
                <div
                  className="avatar-mouth"
                  style={{
                    transform: `translate(-50%, -50%) scaleX(${0.8 + speech.mouthWidth * 0.4}) scaleY(${0.3 + speech.mouthOpen * 0.7})`,
                    opacity: speech.isSpeaking ? 1 : 0,
                  }}
                ></div>
              )}

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
        </section>
      </main>
    </div>
  );
};

export { LunaAvatarInterface };
export default LunaFreeInterface;

