import React, { useState, useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import { LunaAvatarInterface } from './components/LunaFreeInterface';
import './App.css';

function App() {
  const [isAvatarMode, setIsAvatarMode] = useState(() => {
    return localStorage.getItem('luna_avatar_mode') === 'true';
  });

  useEffect(() => {
    localStorage.setItem('luna_avatar_mode', isAvatarMode);
  }, [isAvatarMode]);

  return (
    <div className="App">
      {/* Mode Toggle Button */}
      <button 
        className="mode-toggle"
        onClick={() => setIsAvatarMode(!isAvatarMode)}
        title={isAvatarMode ? "Switch to Chat Mode" : "Switch to Avatar Mode"}
      >
        {isAvatarMode ? '💬' : '🌙'}
      </button>

      {isAvatarMode ? <LunaAvatarInterface /> : <ChatInterface />}
    </div>
  );
}

export default App;
