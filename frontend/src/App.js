import React, { useState, useEffect } from 'react';
import LunaLiveAvatarInterface from './components/LunaLiveAvatarInterface';
import ChatInterfaceWithSidebar from './components/ChatInterfaceWithSidebar';
import './App.css';

function App() {
  // Set default to true to always show the LiveAvatar interface
  const [isInitialized, setIsInitialized] = useState(false);
  const [showLiveAvatar, setShowLiveAvatar] = useState(true); // Toggle state
  const [interfaceKey, setInterfaceKey] = useState(0); // Force remount on toggle

  useEffect(() => {
    // Add any global initialization here if needed
    setIsInitialized(true);
    
    // Cleanup function
    return () => {
      // Add any cleanup code here if needed
    };
  }, []);

  // Handle interface toggle with cleanup
  const handleToggle = () => {
    setInterfaceKey(prev => prev + 1); // Force remount
    setShowLiveAvatar(!showLiveAvatar);
  };

  if (!isInitialized) {
    return (
      <div className="app-loading">
        <div className="spinner"></div>
        <p>Initializing Luna...</p>
      </div>
    );
  }

  return (
    <div className="App">
      {/* Single Toggle Button */}
      <div className="interface-toggle">
        <button
          className="toggle-btn"
          onClick={handleToggle}
        >
          {showLiveAvatar ? '💬' : '🎭'}
        </button>
      </div>

      {/* Render the selected interface */}
      {showLiveAvatar ? (
        <LunaLiveAvatarInterface key={`avatar-${interfaceKey}`} />
      ) : (
        <ChatInterfaceWithSidebar key={`chat-${interfaceKey}`} />
      )}
    </div>
  );
}

export default App;
