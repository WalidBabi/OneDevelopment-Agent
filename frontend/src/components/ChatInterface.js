import React, { useState, useEffect, useRef } from 'react';
import { flushSync } from 'react-dom';
import { chatService } from '../services/api';
import { v4 as uuidv4 } from 'uuid';
import ReactMarkdown from 'react-markdown';
import Sidebar from './Sidebar';
import './ChatInterface.css';

// Cursor-like thinking display for streaming mode
const MAX_COLLAPSED_THINKING_LINES = 4;

const ThinkingDisplay = ({ thinkingText, phase, startedAt, endedAt }) => {
  const [expanded, setExpanded] = useState(false);

  // If we have transitioned to responding/done, show a compact summary line
  if (phase === 'responding' || phase === 'done') {
    if (!startedAt) return null;
    const end = endedAt || Date.now();
    const durationSec = Math.max(1, Math.round((end - startedAt) / 1000));
    return (
      <div className="thinking-summary-line">
        🧠 Thought for {durationSec}s — Generating response...
      </div>
    );
  }

  if (!thinkingText) return null;

  const lines = thinkingText.split('\n').filter(line => line.trim() !== '');
  if (lines.length === 0) return null;

  const visibleLines = expanded
    ? lines
    : lines.slice(-MAX_COLLAPSED_THINKING_LINES);

  return (
    <div className={`thinking-shell ${expanded ? 'expanded' : 'collapsed'}`}>
      <div className="thinking-header-inline">
        <button
          type="button"
          className="thinking-toggle"
          onClick={() => setExpanded(prev => !prev)}
          aria-expanded={expanded}
        >
          {expanded ? '▼' : '▶'}
        </button>
        <span className="thinking-title-inline">Thinking</span>
      </div>
      <div className="thinking-body-inline">
        {visibleLines.map((line, idx) => (
          <div key={idx} className="thinking-line-inline">
            {line}
          </div>
        ))}
        {phase === 'thinking' && (
          <span className="thinking-cursor-inline">▌</span>
        )}
      </div>
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
      // Create placeholder assistant message we will stream into
      const streamingId = uuidv4();
      const thinkingStartedAt = Date.now();
      streamingMessageIdRef.current = streamingId;
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
              // When the model switches to responding, clear the transient thinking text
              if (event.phase === 'responding') {
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
              break;
            
            case 'tool':
              if (event.action === 'start') {
                setToolInfo({ tool: event.tool, query: event.query });
              } else if (event.action === 'result') {
                setToolInfo(prev => ({ ...prev, result: event.content }));
              }
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
                    {/* Show thinking summary for assistant messages */}
                    {message.type === 'assistant' && message.toolsUsed > 0 && showThinking && (
                      <div className="message-thinking-badge">
                        <span className="thinking-badge-icon">🧠</span>
                        <span className="thinking-badge-text">
                          {message.reasoningSteps} steps • {message.toolsUsed} tool{message.toolsUsed > 1 ? 's' : ''} used
                        </span>
                        {message.thinking && message.thinking.length > 0 && (
                          <details className="thinking-details">
                            <summary>View thinking</summary>
                            <div className="thinking-details-content">
                              {message.thinking.map((step, idx) => (
                                <div key={idx} className="thinking-detail-step">
                                  {step.description || step.type}
                                  {step.query && <span className="detail-query">: "{step.query}"</span>}
                                </div>
                              ))}
                            </div>
                          </details>
                        )}
                      </div>
                    )}
                    
                    {/* Live streaming thinking display (Cursor-like) */}
                    {message.type === 'assistant' && (
                      <ThinkingDisplay
                        thinkingText={message.thinkingStream}
                        phase={
                          message.thinkingPhase ||
                          (message.isStreaming
                            ? (currentPhase || 'thinking')
                            : (message.thinkingStream ? 'thinking' : 'done'))
                        }
                        startedAt={message.thinkingStartedAt}
                        endedAt={message.thinkingEndedAt}
                      />
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

