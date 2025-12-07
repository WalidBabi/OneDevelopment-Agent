import React, { useState, useEffect } from 'react';
import LunaLiveAvatarInterface from './components/LunaLiveAvatarInterface';
import ChatInterfaceWithSidebar from './components/ChatInterfaceWithSidebar';
import './App.css';

function App() {
  // Set default to true to always show the LiveAvatar interface
  const [isInitialized, setIsInitialized] = useState(false);
  const [showLiveAvatar, setShowLiveAvatar] = useState(true); // Toggle state

  useEffect(() => {
    // Add any global initialization here if needed
    setIsInitialized(true);
    
    // Cleanup function
    return () => {
      // Add any cleanup code here if needed
    };
  }, []);

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
      {/* Toggle Button */}
      <div className="interface-toggle">
        <button
          className={`toggle-btn ${showLiveAvatar ? 'active' : ''}`}
          onClick={() => setShowLiveAvatar(true)}
        >
          🎭 LiveAvatar
        </button>
        <button
          className={`toggle-btn ${!showLiveAvatar ? 'active' : ''}`}
          onClick={() => setShowLiveAvatar(false)}
        >
          💬 Chat Only
        </button>
      </div>

      {/* Render the selected interface */}
      {showLiveAvatar ? (
        <LunaLiveAvatarInterface />
      ) : (
        <ChatInterfaceWithSidebar />
      )}
    </div>
  );
}

export default App;
