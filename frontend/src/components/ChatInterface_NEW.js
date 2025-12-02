import React, { useState, useEffect, useRef } from 'react';
import { chatService } from '../services/api';
import { v4 as uuidv4 } from 'uuid';
import ReactMarkdown from 'react-markdown';
import Sidebar from './Sidebar';
import './ChatInterface.css';

// DEAD SIMPLE streaming component - polls ref and updates display
const ThinkingStream = ({ thinkingRef, responseRef, isStreaming, currentPhase }) => {
  const [thinkingText, setThinkingText] = useState('');
  const [responseText, setResponseText] = useState('');
  
  // Poll refs every 100ms and update state
  useEffect(() => {
    if (!isStreaming) {
      setThinkingText('');
      setResponseText('');
      return;
    }
    
    const interval = setInterval(() => {
      setThinkingText(thinkingRef.current || '');
      setResponseText(responseRef.current || '');
    }, 100);
    
    return () => clearInterval(interval);
  }, [isStreaming, thinkingRef, responseRef]);
  
  if (!isStreaming && !thinkingText && !responseText) return null;

  return (
    <div style={{ margin: '20px 0' }}>
      {/* Thinking Section */}
      {(thinkingText || currentPhase === 'thinking') && (
        <div style={{ marginBottom: '15px' }}>
          <div style={{ 
            color: '#c084fc', 
            fontSize: '13px', 
            fontWeight: 'bold', 
            marginBottom: '8px',
            textTransform: 'uppercase'
          }}>
            💭 Thinking {isStreaming && '...'}
          </div>
          <div style={{
            background: '#1a0033',
            padding: '15px',
            borderRadius: '6px',
            color: '#c084fc',
            fontSize: '14px',
            fontFamily: 'monospace',
            whiteSpace: 'pre-wrap',
            lineHeight: '1.7',
            minHeight: '60px',
            border: '1px solid #c084fc'
          }}>
            {thinkingText || 'Processing...'}
          </div>
        </div>
      )}
      
      {/* Response Section */}
      {(responseText || currentPhase === 'responding') && (
        <div>
          <div style={{ 
            color: '#4ade80', 
            fontSize: '13px', 
            fontWeight: 'bold', 
            marginBottom: '8px',
            textTransform: 'uppercase'
          }}>
            ✍️ Response {isStreaming && currentPhase === 'responding' && '...'}
          </div>
          <div style={{
            background: '#001a00',
            padding: '15px',
            borderRadius: '6px',
            color: '#ffffff',
            fontSize: '14px',
            fontFamily: 'monospace',
            whiteSpace: 'pre-wrap',
            lineHeight: '1.7',
            minHeight: '60px',
            border: '1px solid #4ade80'
          }}>
            {responseText || 'Generating...'}
          </div>
        </div>
      )}
    </div>
  );
};

export default ThinkingStream;








