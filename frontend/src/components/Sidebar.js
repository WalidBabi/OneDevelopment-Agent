import React from 'react';
import './Sidebar.css';

const Sidebar = ({ 
  conversations, 
  currentSessionId, 
  onSelectConversation, 
  onNewConversation,
  onDeleteConversation,
  onDeleteAllConversations,
  isCollapsed,
  onToggle 
}) => {
  
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) {
      return 'Today';
    } else if (diffDays === 1) {
      return 'Yesterday';
    } else if (diffDays < 7) {
      return `${diffDays} days ago`;
    } else {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }
  };

  const getConversationTitle = (conversation) => {
    if (conversation.title) {
      return conversation.title;
    }
    
    // Generate title from first message
    if (conversation.messages && conversation.messages.length > 0) {
      const firstMessage = conversation.messages.find(m => m.message_type === 'human');
      if (firstMessage) {
        return firstMessage.content.slice(0, 30) + (firstMessage.content.length > 30 ? '...' : '');
      }
    }
    
    return 'New Conversation';
  };

  const getConversationPreview = (conversation) => {
    if (conversation.messages && conversation.messages.length > 0) {
      const lastMessage = conversation.messages[conversation.messages.length - 1];
      const content = lastMessage.content;
      return content.slice(0, 50) + (content.length > 50 ? '...' : '');
    }
    return 'No messages yet';
  };

  return (
    <>
      {/* Mobile overlay backdrop */}
      <div 
        className={`sidebar-overlay ${!isCollapsed ? 'visible' : ''}`}
        onClick={onToggle}
        aria-hidden="true"
      />
      
      <div className={`sidebar-container ${isCollapsed ? 'collapsed' : ''}`}>
        <div className="sidebar-header">
          <button className="new-chat-btn" onClick={onNewConversation}>
            <span>➕</span>
            <span>New Conversation</span>
          </button>
          {conversations.length > 0 && (
            <button
              className="delete-all-btn"
              onClick={onDeleteAllConversations}
              type="button"
            >
              <span>🗑️</span>
              <span>Delete All</span>
            </button>
          )}
        </div>

        <div className="conversations-list">
          {conversations.length === 0 ? (
            <div className="empty-conversations">
              <div className="empty-conversations-icon">💬</div>
              <p>No conversations yet.<br/>Start chatting with Luna!</p>
            </div>
          ) : (
            conversations.map((conversation) => {
              const isActive = conversation.session_id === currentSessionId;

              return (
                <div
                  key={conversation.session_id}
                  className={`conversation-item ${isActive ? 'active' : ''}`}
                  onClick={() => onSelectConversation(conversation.session_id)}
                >
                  <div className="conversation-top">
                    <div className="conversation-title">
                      {getConversationTitle(conversation)}
                    </div>
                    {typeof onDeleteConversation === 'function' && (
                      <div className="conversation-actions">
                        <button
                          type="button"
                          className="action-btn delete"
                          aria-label="Delete conversation"
                          title="Delete conversation"
                          onClick={(event) => {
                            event.stopPropagation();
                            onDeleteConversation(conversation.session_id);
                          }}
                        >
                          Delete
                        </button>
                      </div>
                    )}
                  </div>
                  <div className="conversation-preview">
                    {getConversationPreview(conversation)}
                  </div>
                  <div className="conversation-date">
                    {formatDate(conversation.updated_at || conversation.created_at)}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      <button className="sidebar-toggle" onClick={onToggle}>
        {isCollapsed ? '☰' : '‹'}
      </button>
    </>
  );
};

export default Sidebar;

