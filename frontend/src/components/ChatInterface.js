import React, { useState, useEffect, useRef } from 'react';
import { chatService } from '../services/api';
import { v4 as uuidv4 } from 'uuid';
import ReactMarkdown from 'react-markdown';
import Sidebar from './Sidebar';
import './ChatInterface.css';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [suggestedQuestions, setSuggestedQuestions] = useState([]);
  const [error, setError] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const messagesEndRef = useRef(null);

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

    // Add user message to chat
    const userMessage = {
      id: uuidv4(),
      type: 'user',
      content: text,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Send message to backend
      const response = await chatService.sendMessage(text, sessionId);

      // Add AI response to chat
      const aiMessage = {
        id: uuidv4(),
        type: 'assistant',
        content: response.response,
        intent: response.intent,
        entities: response.entities,
        suggestedActions: response.suggested_actions,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, aiMessage]);
      
      // Reload conversations to update the list
      loadConversations();
    } catch (err) {
      console.error('Error sending message:', err);
      setError('Failed to send message. Please try again.');
      
      // Add error message
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
              {messages.map((message) => (
                <div key={message.id} className={`message ${message.type}`}>
                  {message.type === 'assistant' && (
                    <div className="message-avatar">
                      <img src="/Luna.png" alt="Luna" className="avatar-image" />
                    </div>
                  )}
                  <div className="message-content">
                    {message.type === 'assistant' ? (
                      <ReactMarkdown>{message.content}</ReactMarkdown>
                    ) : (
                      message.content
                    )}
                    
                    {message.suggestedActions && message.suggestedActions.length > 0 && (
                      <div className="suggested-actions">
                        {message.suggestedActions.map((action, idx) => (
                          <button
                            key={idx}
                            className="suggested-action-btn"
                            onClick={() => handleSuggestedAction(action)}
                          >
                            {action}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              
              {isLoading && (
                <div className="message assistant">
                  <div className="message-avatar">
                    <img src="/Luna.png" alt="Luna" className="avatar-image" />
                  </div>
                  <div className="message-content">
                    <div className="typing-indicator">
                      <div className="typing-dot"></div>
                      <div className="typing-dot"></div>
                      <div className="typing-dot"></div>
                    </div>
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

