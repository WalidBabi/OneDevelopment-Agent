import React, { useState, useEffect, useRef } from 'react';
import { flushSync } from 'react-dom';
import { chatService } from '../services/api';
import { v4 as uuidv4 } from 'uuid';
import ReactMarkdown from 'react-markdown';
import Sidebar from './Sidebar';
import './ChatInterface.css';

// Cursor-Style Action Display - Shows ONE action at a time with streaming tokens
// Previous action disappears when new action arrives
// Action word pulses when waiting for tokens
const ActionDisplay = ({ currentAction, thinkingText, phase, isActive }) => {
  const [expanded, setExpanded] = useState(true);
  const contentRef = useRef(null);
  
  // Auto-scroll content
  useEffect(() => {
    if (contentRef.current) {
      contentRef.current.scrollTop = contentRef.current.scrollHeight;
    }
  }, [thinkingText, currentAction]);
  
  // Don't show anything if not active and no action
  if (!isActive && !currentAction) return null;
  
  // Hide immediately if phase is done
  if (phase === 'done' || currentAction?.type === 'done') {
    return null;
  }
  
  // Get action display info
  const getActionDisplay = (action) => {
    if (!action) return { label: 'PROCESSING', icon: '⚡', color: '#94a3b8' };
    
    const actionMap = {
      'thinking': { label: 'THINKING', icon: '🧠', color: '#a78bfa' },
      'searching_kb': { label: 'SEARCHING KNOWLEDGE BASE', icon: '🔍', color: '#60a5fa' },
      'searching_web': { label: 'SEARCHING WEB', icon: '🌐', color: '#34d399' },
      'searching_docs': { label: 'SEARCHING DOCUMENTS', icon: '📄', color: '#fbbf24' },
      'reading_pdf': { label: 'READING PDF', icon: '📑', color: '#f472b6' },
      'fetching_brochure': { label: 'FETCHING BROCHURE', icon: '📋', color: '#fb923c' },
      'analyzing': { label: 'ANALYZING', icon: '🔬', color: '#a78bfa' },
      'comparing': { label: 'COMPARING', icon: '⚖️', color: '#38bdf8' },
      'market_data': { label: 'GETTING MARKET DATA', icon: '📊', color: '#4ade80' },
      'user_context': { label: 'CHECKING USER CONTEXT', icon: '👤', color: '#c084fc' },
      'searching': { label: 'SEARCHING', icon: '🔍', color: '#60a5fa' },
      'responding': { label: 'GENERATING RESPONSE', icon: '✨', color: '#fcd34d' },
      'tool_result': { label: 'PROCESSING RESULTS', icon: '✅', color: '#22c55e' },
      'verifying': { label: 'VERIFYING', icon: '🔍', color: '#8b5cf6' },
      'improving': { label: 'IMPROVING RESPONSE', icon: '✨', color: '#f59e0b' },
      'done': { label: 'COMPLETE', icon: '✓', color: '#22c55e' },
      'error': { label: 'ERROR', icon: '❌', color: '#ef4444' },
    };
    
    // Map tool names to action types
    const toolMap = {
      'search_knowledge_base': 'searching_kb',
      'search_uploaded_documents': 'searching_docs',
      'search_web': 'searching_web',
      'search_web_for_market_data': 'market_data',
      'search_one_development_website': 'searching_web',
      'scrape_webpage': 'searching_web',
      'download_and_read_pdf': 'reading_pdf',
      'fetch_project_brochure': 'fetching_brochure',
      'get_project_details': 'fetching_brochure',
      'find_and_read_brochure': 'fetching_brochure',
      'get_dubai_market_context': 'market_data',
      'get_user_context': 'user_context',
      'save_user_information': 'user_context',
      'deep_research': 'analyzing',
      'analyze_pricing': 'analyzing',
      'compare_properties': 'comparing',
      'guide_buyer_journey': 'analyzing',
    };
    
    // Check if it's a tool action
    if (action.toolName) {
      const mappedType = toolMap[action.toolName] || 'analyzing';
      return actionMap[mappedType] || actionMap['analyzing'];
    }
    
    return actionMap[action.type] || { label: action.type?.toUpperCase() || 'PROCESSING', icon: '⚡', color: '#94a3b8' };
  };
  
  // Determine what to show
  const display = getActionDisplay(currentAction);
  const hasTokens = (phase === 'thinking' && thinkingText && thinkingText.trim().length > 0);
  const hasQuery = currentAction?.query;
  const hasDetail = currentAction?.detail;
  const isWaiting = !hasTokens && !hasQuery && phase !== 'done';
  
  // Parse thinking text into lines
  const lines = thinkingText ? thinkingText.split('\n').filter(line => line.trim()) : [];
  const visibleLines = expanded ? lines : lines.slice(-4);
  
  return (
    <div className="action-display" style={{ '--action-color': display.color }}>
      {/* Action Header */}
      <div className="action-header" onClick={() => setExpanded(!expanded)}>
        <div className="action-header-left">
          <span className="action-icon">{display.icon}</span>
          <span className={`action-label ${isWaiting ? 'pulsing' : ''}`}>
            {display.label}
          </span>
          {isActive && <span className="action-cursor">▌</span>}
        </div>
        {lines.length > 4 && (
          <button className="action-expand-btn" onClick={(e) => { e.stopPropagation(); setExpanded(!expanded); }}>
            {expanded ? '▼' : '▶'} {lines.length} lines
          </button>
        )}
      </div>
      
      {/* Query if present */}
      {hasQuery && (
        <div className="action-query">"{currentAction.query}"</div>
      )}
      
      {/* Detail if present and no tokens */}
      {hasDetail && !hasTokens && (
        <div className="action-detail">{currentAction.detail}</div>
      )}
      
      {/* Streaming tokens */}
      {hasTokens && (
        <div className="action-content" ref={contentRef}>
          {visibleLines.map((line, idx) => (
            <div key={idx} className="action-line">{line}</div>
          ))}
        </div>
      )}
    </div>
  );
};

// Cursor-Style Thinking Summary - Shows after completion
const ThinkingSummary = ({ message }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  if (!message.thinking || message.thinking.length === 0) return null;
  
  // Calculate thinking duration
  const duration = message.thinkingEndedAt && message.thinkingStartedAt
    ? ((message.thinkingEndedAt - message.thinkingStartedAt) / 1000).toFixed(1)
    : null;
  
  // Extract tool calls
  const toolCalls = message.thinking.filter(step => step.type === 'tool_call');
  
  if (toolCalls.length === 0) return null;
  
  // Get friendly tool names
  const getToolDisplay = (toolName) => {
    const toolDisplayMap = {
      'search_knowledge_base': 'Searched knowledge base',
      'search_uploaded_documents': 'Searched documents',
      'search_web': 'Searched web',
      'search_web_for_market_data': 'Searched web (market data)',
      'search_one_development_website': 'Searched One Development website',
      'scrape_webpage': 'Scraped webpage',
      'download_and_read_pdf': 'Read PDF document',
      'fetch_project_brochure': 'Fetched project brochure',
      'get_project_details': 'Got project details',
      'find_and_read_brochure': 'Found and read brochure',
      'get_dubai_market_context': 'Got Dubai market context',
      'get_user_context': 'Checked user context',
      'save_user_information': 'Saved user information',
      'deep_research': 'Deep research',
      'analyze_pricing': 'Analyzed pricing',
      'compare_properties': 'Compared properties',
    };
    return toolDisplayMap[toolName] || toolName.replace(/_/g, ' ');
  };
  
  return (
    <div className="thinking-summary">
      <div 
        className="thinking-summary-header"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <span className="thinking-summary-label">
          Thought for {duration}s
        </span>
        <button className="thinking-summary-toggle">
          {isExpanded ? '▼' : '▶'}
        </button>
      </div>
      
      {isExpanded && (
        <div className="thinking-summary-content">
          {toolCalls.map((step, idx) => (
            <div key={idx} className="thinking-summary-item">
              <span className="thinking-summary-bullet">•</span>
              <span className="thinking-summary-text">
                {getToolDisplay(step.tool)}
                {step.query && (
                  <span className="thinking-summary-query"> "{step.query}"</span>
                )}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Legacy Thinking Steps Component (for non-streaming fallback)
const ThinkingSteps = ({ steps, isVisible }) => {
  if (!isVisible || !steps || steps.length === 0) return null;

  return (
    <div className="thinking-container">
      <div className="thinking-header">
        <span className="thinking-brain">🧠</span>
        <span className="thinking-title">Luna's Thinking Process</span>
      </div>
      <div className="thinking-steps">
        {steps.map((step, index) => (
          <div 
            key={index} 
            className={`thinking-step ${step.type}`}
            style={{ animationDelay: `${index * 0.15}s` }}
          >
            {step.type === 'thinking' && (
              <>
                <span className="step-icon">💭</span>
                <span className="step-text">{step.description}</span>
              </>
            )}
            {step.type === 'tool_call' && (
              <>
                <span className="step-icon">{step.description.split(' ')[0]}</span>
                <span className="step-text">
                  {step.description.split(' ').slice(1).join(' ')}
                  {step.query && <span className="step-query">"{step.query}"</span>}
                </span>
              </>
            )}
            {step.type === 'tool_result' && (
              <>
                <span className="step-icon">✅</span>
                <span className="step-text step-result">Found relevant information</span>
              </>
            )}
            {step.type === 'responding' && (
              <>
                <span className="step-icon">✨</span>
                <span className="step-text">{step.description}</span>
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [suggestedQuestions, setSuggestedQuestions] = useState([]);
  const [error, setError] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [currentThinking, setCurrentThinking] = useState([]);
  const [showThinking, setShowThinking] = useState(true);
  const [streamEvents, setStreamEvents] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [useStreaming, setUseStreaming] = useState(true); // Toggle streaming mode
  const [currentPhase, setCurrentPhase] = useState('');
  const [toolInfo, setToolInfo] = useState(null);
  const [currentAction, setCurrentAction] = useState(null); // Track CURRENT action only (Cursor-style)
  
  // Refs to track accumulated text
  const thinkingRef = useRef('');
  const responseRef = useRef('');
  const messagesEndRef = useRef(null);
  const streamingMessageIdRef = useRef(null);

  // Initialize: Load conversations and current session
  useEffect(() => {
    initializeApp();
  }, []);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const initializeApp = async () => {
    // Generate or retrieve session ID
    let storedSessionId = localStorage.getItem('chat_session_id');
    if (!storedSessionId) {
      storedSessionId = uuidv4();
      localStorage.setItem('chat_session_id', storedSessionId);
    }
    setSessionId(storedSessionId);

    // Load all conversations
    await loadConversations();

    // Load current conversation history
    await loadConversationHistory(storedSessionId);

    // Fetch suggested questions
    fetchSuggestedQuestions();

    // Set up rotating suggested questions
    const intervalId = setInterval(() => {
      if (messages.length === 0) {
        fetchSuggestedQuestions();
      }
    }, 15000);

    return () => clearInterval(intervalId);
  };

  const loadConversations = async () => {
    try {
      const data = await chatService.getAllConversations();
      const list = data.results || data || [];
      setConversations(list);
      return list;
    } catch (err) {
      console.error('Failed to load conversations:', err);
      return [];
    }
  };

  const loadConversationHistory = async (sessionIdToLoad) => {
    try {
      const conversation = await chatService.getConversationHistory(sessionIdToLoad);
      
      if (conversation && conversation.messages) {
        const formattedMessages = conversation.messages.map(msg => ({
          id: msg.id || uuidv4(),
          type: msg.message_type === 'human' ? 'user' : 'assistant',
          content: msg.content,
          timestamp: new Date(msg.created_at),
        }));
        
        setMessages(formattedMessages);
      }
    } catch (err) {
      // If conversation doesn't exist yet, that's okay
      console.log('No previous conversation found, starting fresh');
      setMessages([]);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchSuggestedQuestions = async () => {
    try {
      const questions = await chatService.getSuggestedQuestions(6);
      setSuggestedQuestions(questions);
    } catch (err) {
      console.error('Failed to fetch suggested questions:', err);
    }
  };

  const handleNewConversation = () => {
    const newSessionId = uuidv4();
    localStorage.setItem('chat_session_id', newSessionId);
    setSessionId(newSessionId);
    setMessages([]);
    setError(null);
    
    // Reload conversations list
    loadConversations();
  };

  const handleSelectConversation = async (selectedSessionId) => {
    localStorage.setItem('chat_session_id', selectedSessionId);
    setSessionId(selectedSessionId);
    setMessages([]);
    setError(null);
    
    // Load the selected conversation
    await loadConversationHistory(selectedSessionId);
  };

  const handleDeleteConversation = async (sessionIdToDelete) => {
    if (!sessionIdToDelete) return;

    const confirmDelete = window.confirm(
      'Delete this conversation? This action cannot be undone.'
    );

    if (!confirmDelete) return;

    try {
      await chatService.deleteConversation(sessionIdToDelete);

      const updatedConversations = await loadConversations();

      if (sessionIdToDelete === sessionId) {
        if (updatedConversations.length > 0) {
          const nextConversation = updatedConversations[0];
          await handleSelectConversation(nextConversation.session_id);
        } else {
          handleNewConversation();
        }
      }
    } catch (err) {
      console.error('Failed to delete conversation:', err);
      setError('Failed to delete conversation. Please try again.');
    }
  };

  const handleDeleteAllConversations = async () => {
    const confirmDelete = window.confirm(
      'Delete all conversations? This action cannot be undone.'
    );

    if (!confirmDelete) return;

    try {
      await chatService.deleteAllConversations();
      setMessages([]);
      setConversations([]);
      setError(null);

      // Start a fresh session
      handleNewConversation();
    } catch (err) {
      console.error('Failed to delete all conversations:', err);
      setError('Failed to delete all conversations. Please try again.');
    }
  };

  const sendMessage = async (messageText = null) => {
    const text = messageText || inputMessage.trim();
    
    if (!text) return;

    // Clear input immediately
    setInputMessage('');
    setError(null);
    setCurrentThinking([]);
    setStreamEvents([]);

    // Add user message to chat
    const userMessage = {
      id: uuidv4(),
      type: 'user',
      content: text,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    if (useStreaming) {
      // Use TRUE streaming mode - show actual LLM thinking tokens
      setIsStreaming(true);
      setCurrentPhase('');
      setToolInfo(null);
      
      // Clear accumulators
      thinkingRef.current = '';
      responseRef.current = '';
      setCurrentAction(null);
      
      // Create placeholder assistant message we will stream into
      const streamingId = uuidv4();
      const thinkingStartedAt = Date.now();
      streamingMessageIdRef.current = streamingId;
      
      // Set initial action
      setCurrentAction({ type: 'thinking' });
      
      setMessages(prev => [
        ...prev,
        {
          id: streamingId,
          type: 'assistant',
          content: '',
          thinkingStream: '',
          responseStream: '',
          isStreaming: true,
          thinkingStartedAt,
          thinkingEndedAt: null,
          thinkingPhase: 'thinking',
          timestamp: new Date(),
        },
      ]);
      let suggestedActions = [];
      let thinkingTokenCount = 0;
      let responseTokenCount = 0;

      try {
        await chatService.sendMessageStream(text, sessionId, (event) => {
          switch (event.type) {
            case 'phase':
              setCurrentPhase(event.phase);
              if (event.phase === 'thinking') {
                // Set current action to thinking (replaces previous)
                setCurrentAction({ type: 'thinking' });
                flushSync(() => {
                  setMessages(prev =>
                    prev.map(m =>
                      m.id === streamingMessageIdRef.current
                        ? { ...m, thinkingPhase: 'thinking' }
                        : m
                    )
                  );
                });
              }
              // When searching phase starts
              if (event.phase === 'searching') {
                setCurrentAction({ type: 'searching' });
              }
              // When the model switches to responding, clear the transient thinking text
              if (event.phase === 'responding') {
                // Set current action to responding (replaces previous)
                setCurrentAction({ type: 'responding' });
                const endedAt = Date.now();
                thinkingRef.current = '';
                flushSync(() => {
                  setMessages(prev =>
                    prev.map(m =>
                      m.id === streamingMessageIdRef.current
                        ? {
                            ...m,
                            thinkingStream: '',
                            thinkingPhase: 'responding',
                            thinkingEndedAt: m.thinkingEndedAt || endedAt,
                          }
                        : m
                    )
                  );
                });
              }
              break;
            
            case 'thinking':
              thinkingRef.current += event.token;
              flushSync(() => {
                const newThinking = thinkingRef.current;
                setMessages(prev =>
                  prev.map(m =>
                    m.id === streamingMessageIdRef.current
                      ? { ...m, thinkingStream: newThinking }
                      : m
                  )
                );
              });
              thinkingTokenCount++;
              break;
            
            case 'thinking_done':
              // Capture the exact moment thinking completed (before tool execution)
              flushSync(() => {
                const thinkingDoneAt = Date.now();
                setMessages(prev =>
                  prev.map(m =>
                    m.id === streamingMessageIdRef.current
                      ? { ...m, thinkingEndedAt: m.thinkingEndedAt || thinkingDoneAt }
                      : m
                  )
                );
              });
              break;
            
            case 'tool':
              if (event.action === 'start') {
                // Clear thinking text when tool starts
                thinkingRef.current = '';
                flushSync(() => {
                  setMessages(prev =>
                    prev.map(m =>
                      m.id === streamingMessageIdRef.current
                        ? { ...m, thinkingStream: '' }
                        : m
                    )
                  );
                });
                // Set current action to the tool (replaces previous action)
                setCurrentAction({ 
                  toolName: event.tool, 
                  query: event.query 
                });
                setToolInfo({ tool: event.tool, query: event.query });
              } else if (event.action === 'result') {
                // Show processing results briefly, then it will be replaced by next action
                setCurrentAction({ type: 'tool_result', detail: 'Processing results...' });
                setToolInfo(prev => ({ ...prev, result: event.content }));
              }
              break;
            
            case 'verification':
              // Handle verification results
              setCurrentAction({ type: 'verifying', detail: `Confidence: ${(event.confidence * 100).toFixed(0)}%` });
              flushSync(() => {
                setMessages(prev =>
                  prev.map(m =>
                    m.id === streamingMessageIdRef.current
                      ? {
                          ...m,
                          verification: {
                            confidence: event.confidence,
                            level: event.level,
                            sources: event.sources || [],
                            issues: event.issues || []
                          }
                        }
                      : m
                  )
                );
              });
              break;
            
            case 'response_improved':
              // Response was improved after verification
              responseRef.current = event.content;
              flushSync(() => {
                setMessages(prev =>
                  prev.map(m =>
                    m.id === streamingMessageIdRef.current
                      ? {
                          ...m,
                          content: event.content,
                          responseStream: event.content
                        }
                      : m
                  )
                );
              });
              break;
            
            case 'response':
              responseRef.current += event.token;
              flushSync(() => {
                const newResponse = responseRef.current;
                setMessages(prev =>
                  prev.map(m =>
                    m.id === streamingMessageIdRef.current
                      ? {
                          ...m,
                          responseStream: newResponse,
                          content: newResponse,
                        }
                      : m
                  )
                );
              });
              responseTokenCount++;
              break;
            
            case 'done':
              // Clear the action display when done
              setCurrentPhase('done');
              setCurrentAction(null); // Clear action completely
              setToolInfo(null); // Clear tool info
              suggestedActions = event.suggested_actions || [];
              flushSync(() => {
                const endedAt = Date.now();
                setMessages(prev =>
                  prev.map(m =>
                    m.id === streamingMessageIdRef.current
                      ? {
                          ...m,
                          thinkingPhase: 'done',
                          thinkingEndedAt: m.thinkingEndedAt || endedAt,
                        }
                      : m
                  )
                );
              });
              break;
            
            case 'error':
              setCurrentAction({ type: 'error', detail: event.content });
              setError(event.content);
              break;
            
            default:
              break;
          }
        });

        // Finalize the streaming assistant message
        setMessages(prev =>
          prev.map(m =>
            m.id === streamingMessageIdRef.current
              ? {
                  ...m,
                  content: responseRef.current,
                  suggestedActions: suggestedActions,
                  thinking: thinkingRef.current,
                  isStreaming: false,
                }
              : m
          )
        );
        streamingMessageIdRef.current = null;
        loadConversations();

      } catch (err) {
        console.error('Streaming error:', err);
        setError('Streaming failed. Trying regular mode...');
        setUseStreaming(false);
      } finally {
        setIsStreaming(false);
        setCurrentPhase('');
        setToolInfo(null);
        setCurrentAction(null);
        setIsLoading(false);
      }
    } else {
      // Non-streaming mode (fallback)
      setCurrentThinking([{ type: 'thinking', description: '🤔 Analyzing your question...' }]);

      try {
        const response = await chatService.sendMessage(text, sessionId);

        if (response.metadata && response.metadata.thinking) {
          setCurrentThinking(response.metadata.thinking);
        }

        await new Promise(resolve => setTimeout(resolve, 500));

        const aiMessage = {
          id: uuidv4(),
          type: 'assistant',
          content: response.response,
          suggestedActions: response.suggested_actions,
          thinking: response.metadata?.thinking || [],
          toolsUsed: response.metadata?.tools_used || 0,
          reasoningSteps: response.metadata?.reasoning_steps || 0,
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, aiMessage]);
        setTimeout(() => setCurrentThinking([]), 1000);
        loadConversations();
      } catch (err) {
        console.error('Error sending message:', err);
        setError('Failed to send message. Please try again.');
        
        const errorMessage = {
          id: uuidv4(),
          type: 'assistant',
          content: "I'm sorry, I'm having trouble connecting right now. Please try again in a moment.",
          timestamp: new Date(),
        };
        
        setMessages((prev) => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage();
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleSuggestedQuestion = (question) => {
    sendMessage(question);
  };

  const handleSuggestedAction = (action) => {
    sendMessage(action);
  };

  // Track the most recent assistant message so we only show
  // follow-up suggested actions under the latest AI reply.
  const lastAssistantId =
    messages.filter((m) => m.type === 'assistant').slice(-1)[0]?.id;

  return (
    <div className="app-container">
      <Sidebar
        conversations={conversations}
        currentSessionId={sessionId}
        onSelectConversation={handleSelectConversation}
        onNewConversation={handleNewConversation}
        onDeleteConversation={handleDeleteConversation}
        onDeleteAllConversations={handleDeleteAllConversations}
        isCollapsed={isSidebarCollapsed}
        onToggle={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
      />

      <div className="chat-container">
        <div className="chat-header">
          <div className="header-logo">
            <img src="/onedev-logo.svg" alt="One Development" className="logo-image" />
          </div>
          <h1>Luna - AI Agent</h1>
          <p>Ask me anything about One Development</p>
        </div>

        <div className="chat-messages">
          {messages.length === 0 ? (
            <div className="welcome-section">
              <div className="welcome-avatar">
                <img src="/Luna.png" alt="Luna" className="welcome-avatar-image" />
              </div>
              <h2>Welcome! I'm Luna 🌙</h2>
              <p>
                Your intelligent AI agent for One Development. I'm here to answer your questions about our company, 
                projects, services, and everything related to One Development. How can I assist you today?
              </p>
              
              <div className="suggested-questions">
                {suggestedQuestions.map((question, index) => (
                  <div
                    key={question.id || index}
                    className="suggested-question"
                    onClick={() => handleSuggestedQuestion(question.question)}
                  >
                    {question.question}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <>
              {messages.map((message) => {
                return (
                <div key={message.id} className={`message ${message.type}`}>
                  {message.type === 'assistant' && (
                    <div className="message-avatar">
                      <img src="/Luna.png" alt="Luna" className="avatar-image" />
                    </div>
                  )}
                  <div className="message-content">
                    {/* Cursor-Style Thinking Summary */}
                    {message.type === 'assistant' && !message.isStreaming && showThinking && (
                      <ThinkingSummary message={message} />
                    )}
                    
                    {/* Cursor-Style Action Display - Shows ONE action at a time */}
                    {message.type === 'assistant' && message.isStreaming && (
                      <ActionDisplay
                        currentAction={currentAction}
                        thinkingText={message.thinkingStream}
                        phase={currentPhase || 'thinking'}
                        isActive={message.isStreaming}
                      />
                    )}

                    {/* Verification Badge (if verified) */}
                    {message.type === 'assistant' && message.verification && !message.isStreaming && (
                      <div className="verification-badge">
                        <span className="verification-icon">
                          {message.verification.level === 'high' ? '✅' : 
                           message.verification.level === 'medium' ? '✓' : '⚠️'}
                        </span>
                        <span className="verification-text">
                          {message.verification.level === 'high' ? 'Verified' : 
                           message.verification.level === 'medium' ? 'Verified' : 'General Info'}
                          {' '}
                          ({(message.verification.confidence * 100).toFixed(0)}% confidence)
                        </span>
                        {message.verification.sources && message.verification.sources.length > 0 && (
                          <span className="verification-sources">
                            Sources: {message.verification.sources.map(s => 
                              s.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
                            ).join(', ')}
                          </span>
                        )}
                      </div>
                    )}

                    {/* Final assistant content (streams in as responseStream updates) */}
                    {message.type === 'assistant'
                      ? <ReactMarkdown>{message.content}</ReactMarkdown>
                      : message.content}

                    {message.type === 'assistant' && message.id === lastAssistantId && !message.isStreaming && (() => {
                      const fallbackActions = suggestedQuestions.map(q => q.question);
                      const actions = (message.suggestedActions && message.suggestedActions.length > 0)
                        ? message.suggestedActions
                        : fallbackActions;

                      if (!actions || actions.length === 0) return null;

                      return (
                        <div className="suggested-actions">
                          <div className="suggested-actions-title">
                            ✨ You could also ask:
                          </div>
                          <div className="suggested-actions-grid">
                            {actions.map((action, idx) => (
                              <button
                                key={idx}
                                className="suggested-action-btn"
                                onClick={() => handleSuggestedAction(action)}
                              >
                                <span className="suggested-action-icon">↳</span>
                                <span className="suggested-action-text">{action}</span>
                              </button>
                            ))}
                          </div>
                        </div>
                      );
                    })()}
                  </div>
                </div>
              )})}
              
              {/* Legacy loading indicator */}
              {isLoading && !isStreaming && (
                <div className="message assistant">
                  <div className="message-avatar">
                    <img src="/Luna.png" alt="Luna" className="avatar-image" />
                  </div>
                  <div className="message-content loading-content">
                    {useStreaming ? null : (
                      <>
                        <ThinkingSteps steps={currentThinking} isVisible={showThinking} />
                        <div className="typing-indicator">
                          <div className="typing-dot"></div>
                          <div className="typing-dot"></div>
                          <div className="typing-dot"></div>
                        </div>
                      </>
                    )}
                  </div>
                </div>
              )}
            </>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <div className="chat-input-area">
          <form onSubmit={handleSubmit} className="chat-input-wrapper">
            <input
              type="text"
              className="chat-input"
              placeholder="Type your question here..."
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
            />
            <button
              type="submit"
              className="send-button"
              disabled={isLoading || !inputMessage.trim()}
            >
              {isLoading ? 'Sending...' : 'Send'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;

