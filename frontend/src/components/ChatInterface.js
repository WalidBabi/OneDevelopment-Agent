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
  
  // Hide immediately if phase is done OR if no current action and not active
  if (phase === 'done' || currentAction?.type === 'done') {
    return null;
  }
  
  // Don't show anything if not active and no action
  if (!isActive && !currentAction) return null;
  
  // Also hide if action is null and phase is empty/done
  if (!currentAction && (!phase || phase === '' || phase === 'done')) {
    return null;
  }
  
  // Get action display info
  const getActionDisplay = (action) => {
    if (!action) return { label: 'PROCESSING', icon: '⚡', color: '#966bfc' }; // OneDevelopment violet
    
    const actionMap = {
      'thinking': { label: 'THINKING', icon: '🧠', color: '#966bfc' }, // OneDevelopment violet
      'searching_kb': { label: 'SEARCHING KNOWLEDGE BASE', icon: '🔍', color: '#60a5fa' },
      'searching_web': { label: 'SEARCHING WEB', icon: '🌐', color: '#34d399' },
      'searching_docs': { label: 'SEARCHING DOCUMENTS', icon: '📄', color: '#fbbf24' },
      'reading_pdf': { label: 'READING PDF', icon: '📑', color: '#f472b6' },
      'fetching_brochure': { label: 'FETCHING BROCHURE', icon: '📋', color: '#fb923c' },
      'analyzing': { label: 'ANALYZING', icon: '🔬', color: '#966bfc' }, // OneDevelopment violet
      'comparing': { label: 'COMPARING', icon: '⚖️', color: '#38bdf8' },
      'market_data': { label: 'GETTING MARKET DATA', icon: '📊', color: '#4ade80' },
      'user_context': { label: 'CHECKING USER CONTEXT', icon: '👤', color: '#966bfc' }, // OneDevelopment violet
      'searching': { label: 'SEARCHING', icon: '🔍', color: '#60a5fa' },
      'responding': { label: 'GENERATING RESPONSE', icon: '✨', color: '#D4AF37' }, // OneDevelopment gold
      'tool_result': { label: 'PROCESSING RESULTS', icon: '✅', color: '#22c55e' },
      'verifying': { label: 'VERIFYING', icon: '🔍', color: '#966bfc' }, // OneDevelopment violet
      'improving': { label: 'IMPROVING RESPONSE', icon: '✨', color: '#D4AF37' }, // OneDevelopment gold
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
      // Subagents - specialized agents
      'deep_research': 'subagent_research',
      'analyze_pricing': 'subagent_pricing',
      'compare_properties': 'subagent_compare',
      'guide_buyer_journey': 'subagent_guide',
    };
    
    // Subagent-specific displays
    const subagentMap = {
      'subagent_research': { label: '🔬 DEEP RESEARCH SUBAGENT', icon: '🤖', color: '#966bfc' },
      'subagent_pricing': { label: '💰 PRICING ANALYSIS SUBAGENT', icon: '🤖', color: '#966bfc' },
      'subagent_compare': { label: '⚖️ COMPARISON SUBAGENT', icon: '🤖', color: '#966bfc' },
      'subagent_guide': { label: '🗺️ BUYER JOURNEY SUBAGENT', icon: '🤖', color: '#966bfc' },
    };
    
    // Check if it's a tool action
    if (action.toolName) {
      const mappedType = toolMap[action.toolName] || 'analyzing';
      
      // Check if it's a subagent
      if (subagentMap[mappedType]) {
        return subagentMap[mappedType];
      }
      
      return actionMap[mappedType] || actionMap['analyzing'];
    }
    
    // Check if action type is a subagent
    if (subagentMap[action.type]) {
      return subagentMap[action.type];
    }
    
    return actionMap[action.type] || { label: action.type?.toUpperCase() || 'PROCESSING', icon: '⚡', color: '#966bfc' }; // OneDevelopment violet
  };
  
  // Determine what to show
  const display = getActionDisplay(currentAction);
  // Show thinking tokens if we have thinking text and we're in thinking phase OR if action is thinking
  const isThinkingPhase = phase === 'thinking' || currentAction?.type === 'thinking';
  const hasTokens = (isThinkingPhase && thinkingText && thinkingText.trim().length > 0);
  const hasQuery = currentAction?.query;
  const hasDetail = currentAction?.detail;
  const isWaiting = !hasTokens && !hasQuery && phase !== 'done';
  
  // Check if this is a subagent action
  const isSubagent = display.label && display.label.includes('SUBAGENT');
  
  // Parse thinking text into lines
  const lines = thinkingText ? thinkingText.split('\n').filter(line => line.trim()) : [];
  const visibleLines = expanded ? lines : lines.slice(-4);
  
  return (
    <div className={`action-display ${isSubagent ? 'subagent-action' : ''}`} style={{ '--action-color': display.color }}>
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

// Cursor-Style Thinking Summary - Shows after completion with Subagent info
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
  
  // Identify subagents vs regular tools
  const subagentTools = ['deep_research', 'analyze_pricing', 'compare_properties', 'guide_buyer_journey'];
  const subagentCalls = toolCalls.filter(step => subagentTools.includes(step.tool));
  const regularToolCalls = toolCalls.filter(step => !subagentTools.includes(step.tool));
  
  // Get friendly tool names with subagent icons
  const getToolDisplay = (toolName, isSubagent = false) => {
    const toolDisplayMap = {
      // Subagents (specialized AI agents)
      'deep_research': { label: '🔬 Deep Research Agent', desc: 'Specialized in comprehensive market research' },
      'analyze_pricing': { label: '💰 Pricing Analysis Agent', desc: 'Expert in property valuation and pricing' },
      'compare_properties': { label: '⚖️ Comparison Agent', desc: 'Specialized in property comparisons' },
      'guide_buyer_journey': { label: '🗺️ Buyer Journey Agent', desc: 'Expert in guiding purchase process' },
      // Regular tools
      'search_knowledge_base': { label: 'Searched knowledge base', desc: '' },
      'search_uploaded_documents': { label: 'Searched documents', desc: '' },
      'search_web': { label: 'Searched web', desc: '' },
      'search_web_for_market_data': { label: 'Searched web (market data)', desc: '' },
      'search_one_development_website': { label: 'Searched One Development website', desc: '' },
      'scrape_webpage': { label: 'Scraped webpage', desc: '' },
      'download_and_read_pdf': { label: 'Read PDF document', desc: '' },
      'fetch_project_brochure': { label: 'Fetched project brochure', desc: '' },
      'get_project_details': { label: 'Got project details', desc: '' },
      'find_and_read_brochure': { label: 'Found and read brochure', desc: '' },
      'get_dubai_market_context': { label: 'Got Dubai market context', desc: '' },
      'get_user_context': { label: 'Checked user context', desc: '' },
      'save_user_information': { label: 'Saved user information', desc: '' },
    };
    return toolDisplayMap[toolName] || { label: toolName.replace(/_/g, ' '), desc: '' };
  };
  
  return (
    <div className="thinking-summary">
      <div 
        className="thinking-summary-header"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <span className="thinking-summary-label">
          💭 Thought for {duration}s
          {subagentCalls.length > 0 && (
            <span className="subagent-badge"> • {subagentCalls.length} Subagent{subagentCalls.length > 1 ? 's' : ''} Summoned</span>
          )}
        </span>
        <button className="thinking-summary-toggle">
          {isExpanded ? '▼' : '▶'}
        </button>
      </div>
      
      {isExpanded && (
        <div className="thinking-summary-content">
          {/* Subagents Section - Show first if present */}
          {subagentCalls.length > 0 && (
            <div className="subagents-section">
              <div className="subagents-header">
                <span className="subagents-icon">🤖</span>
                <span className="subagents-title">Specialized Subagents Deployed ({subagentCalls.length})</span>
              </div>
              {subagentCalls.map((step, idx) => {
                const display = getToolDisplay(step.tool, true);
                return (
                  <div key={`subagent-${idx}`} className="subagent-item">
                    <div className="subagent-name">{display.label}</div>
                    {display.desc && (
                      <div className="subagent-desc">{display.desc}</div>
                    )}
                    {step.query && (
                      <div className="subagent-task">
                        <span className="subagent-task-label">Task:</span> "{step.query}"
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
          
          {/* Regular Tools Section */}
          {regularToolCalls.length > 0 && (
            <div className="regular-tools-section">
              {subagentCalls.length > 0 && (
                <div className="tools-header">
                  <span className="tools-icon">🔧</span>
                  <span className="tools-title">Tools Used ({regularToolCalls.length})</span>
                </div>
              )}
              {regularToolCalls.map((step, idx) => {
                const display = getToolDisplay(step.tool, false);
                return (
                  <div key={`tool-${idx}`} className="thinking-summary-item">
                    <span className="thinking-summary-bullet">•</span>
                    <span className="thinking-summary-text">
                      {display.label}
                      {step.query && (
                        <span className="thinking-summary-query"> "{step.query}"</span>
                      )}
                    </span>
                  </div>
                );
              })}
            </div>
          )}
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

// Context Monitor Component
const ContextMonitor = ({ sessionId }) => {
  const [contextData, setContextData] = useState(null);
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    const fetchContext = async () => {
      try {
        const data = await chatService.getContextStatus(sessionId);
        setContextData(data);
      } catch (error) {
        console.error('Error fetching context:', error);
      }
    };

    fetchContext();
    // Refresh every 5 seconds
    const interval = setInterval(fetchContext, 5000);
    return () => clearInterval(interval);
  }, [sessionId]);

  if (!contextData) return null;

  const percentage = contextData.percentage_used || 0;
  const isNearLimit = percentage > 70;
  const isAtLimit = percentage > 85;

  return (
    <div className={`context-monitor ${showDetails ? 'expanded' : ''}`}>
      <div className="context-header" onClick={() => setShowDetails(!showDetails)}>
        <span className="context-icon">📊</span>
        <span className="context-label">Context</span>
        <span className={`context-percentage ${isAtLimit ? 'critical' : isNearLimit ? 'warning' : ''}`}>
          {percentage.toFixed(1)}%
        </span>
        <span className="context-toggle">{showDetails ? '▼' : '▶'}</span>
      </div>
      
      {/* Progress bar */}
      <div className="context-bar">
        <div 
          className={`context-fill ${isAtLimit ? 'critical' : isNearLimit ? 'warning' : ''}`}
          style={{ width: `${Math.min(percentage, 100)}%` }}
        />
      </div>

      {showDetails && (
        <div className="context-details">
          <div className="context-stat">
            <span className="stat-label">Tokens:</span>
            <span className="stat-value">
              {contextData.tokens_used?.toLocaleString()} / {contextData.max_tokens?.toLocaleString()}
            </span>
          </div>
          <div className="context-stat">
            <span className="stat-label">Model:</span>
            <span className="stat-value">{contextData.model}</span>
          </div>
          {contextData.breakdown && (
            <div className="context-breakdown">
              <div className="breakdown-item">
                <span>💬 Messages:</span>
                <span>{contextData.breakdown.messages?.toLocaleString()}</span>
              </div>
              <div className="breakdown-item">
                <span>📝 System:</span>
                <span>{contextData.breakdown.system_prompt?.toLocaleString()}</span>
              </div>
              <div className="breakdown-item">
                <span>🛠️ Tools:</span>
                <span>{contextData.breakdown.tools?.toLocaleString()}</span>
              </div>
            </div>
          )}
          <div className={`filesystem-status ${contextData.filesystem_active ? 'active' : 'ready'}`}>
            <span className="filesystem-icon">💾</span>
            <span className="filesystem-text">
              {contextData.filesystem_active 
                ? '🟢 FilesystemMiddleware: ACTIVE' 
                : '⚪ FilesystemMiddleware: Ready (activates at 85%)'
              }
            </span>
          </div>
        </div>
      )}
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
  // Start with sidebar collapsed on mobile devices
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(window.innerWidth <= 768);
  const [currentThinking, setCurrentThinking] = useState([]);
  const [showThinking, setShowThinking] = useState(true);
  const [streamEvents, setStreamEvents] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [useStreaming, setUseStreaming] = useState(true); // Toggle streaming mode
  const [currentPhase, setCurrentPhase] = useState('');
  const [toolInfo, setToolInfo] = useState(null);
  const [currentAction, setCurrentAction] = useState(null); // Track CURRENT action only (Cursor-style)
  const [showContextMonitor, setShowContextMonitor] = useState(true);
  
  // Refs to track accumulated text
  const thinkingRef = useRef('');
  const responseRef = useRef('');
  const messagesEndRef = useRef(null);
  const streamingMessageIdRef = useRef(null);

  // Initialize: Load conversations and current session
  useEffect(() => {
    initializeApp();
  }, []);

  // Handle responsive sidebar state on window resize
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth <= 768) {
        setIsSidebarCollapsed(true);
      }
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
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
    
    // Auto-close sidebar on mobile after creating new conversation
    if (window.innerWidth <= 768) {
      setIsSidebarCollapsed(true);
    }
    
    // Reload conversations list
    loadConversations();
  };

  const handleSelectConversation = async (selectedSessionId) => {
    localStorage.setItem('chat_session_id', selectedSessionId);
    setSessionId(selectedSessionId);
    setMessages([]);
    setError(null);
    
    // Auto-close sidebar on mobile after selecting a conversation
    if (window.innerWidth <= 768) {
      setIsSidebarCollapsed(true);
    }
    
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
                // Initialize thinking stream if not already set
                if (!thinkingRef.current) {
                  thinkingRef.current = '';
                }
                flushSync(() => {
                  setMessages(prev =>
                    prev.map(m =>
                      m.id === streamingMessageIdRef.current
                        ? { ...m, thinkingPhase: 'thinking', thinkingStream: m.thinkingStream || '' }
                        : m
                    )
                  );
                });
                console.log('[Phase] Thinking phase started');
              }
              // When searching phase starts
              if (event.phase === 'searching') {
                setCurrentAction({ type: 'searching' });
              }
              // When the model switches to responding, keep thinking text but mark phase as responding
              if (event.phase === 'responding') {
                // Set current action to responding (replaces previous)
                setCurrentAction({ type: 'responding' });
                const endedAt = Date.now();
                // Don't clear thinking text - it should persist for the summary
                flushSync(() => {
                  setMessages(prev =>
                    prev.map(m =>
                      m.id === streamingMessageIdRef.current
                        ? {
                            ...m,
                            // Keep thinkingStream for summary, just update phase
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
              // Ensure we're in thinking phase - set phase and action immediately
              setCurrentPhase('thinking');
              setCurrentAction({ type: 'thinking' });
              thinkingRef.current += event.token;
              // Log first few thinking tokens for debugging
              if (thinkingTokenCount < 3) {
                console.log('[Thinking Token]', event.token?.substring(0, 50));
              }
              flushSync(() => {
                const newThinking = thinkingRef.current;
                setMessages(prev =>
                  prev.map(m =>
                    m.id === streamingMessageIdRef.current
                      ? { ...m, thinkingStream: newThinking, thinkingPhase: 'thinking' }
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
                // Don't clear thinking text immediately - let it persist briefly
                // The thinking phase is complete, but we can show it until tool completes
                // Set current action to the tool (replaces previous action)
                setCurrentAction({ 
                  toolName: event.tool, 
                  query: event.query 
                });
                setToolInfo({ tool: event.tool, query: event.query });
                // Update phase to searching/executing
                setCurrentPhase('searching');
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
              setIsStreaming(false); // Stop streaming immediately
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
                          isStreaming: false, // Mark message as not streaming
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
        onAvatarToggle={onAvatarToggle}
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
          <button 
            className={`context-toggle-btn ${showContextMonitor ? 'active' : ''}`}
            onClick={() => setShowContextMonitor(!showContextMonitor)}
            title="Toggle Context Monitor"
          >
            📊
          </button>
        </div>

        {/* Context Monitor */}
        {showContextMonitor && sessionId && (
          <ContextMonitor sessionId={sessionId} />
        )}

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
                        phase={message.thinkingPhase || currentPhase || 'thinking'}
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

