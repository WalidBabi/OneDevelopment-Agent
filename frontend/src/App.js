import React, { useState, useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import LunaFreeInterface, { LunaAvatarInterface } from './components/LunaFreeInterface';
import './App.css';

function App() {
  // Default to the new Luna Avatar experience
  const [interfaceMode, setInterfaceMode] = useState(() => {
    return localStorage.getItem('luna_interface_mode') || 'luna';
  });
  const [showModeSelector, setShowModeSelector] = useState(false);

  // Save preference
  useEffect(() => {
    localStorage.setItem('luna_interface_mode', interfaceMode);
  }, [interfaceMode]);

  const handleModeChange = (mode) => {
    setInterfaceMode(mode);
    setShowModeSelector(false);
  };

  return (
    <div className="App">
      {/* Mode Toggle */}
      <button 
        className="mode-toggle"
        onClick={() => setShowModeSelector(!showModeSelector)}
        title="Switch Interface"
      >
        ⚙️
      </button>

      {/* Mode Selector */}
      {showModeSelector && (
        <div className="mode-overlay" onClick={() => setShowModeSelector(false)}>
          <div className="mode-dialog" onClick={(e) => e.stopPropagation()}>
            <h3>Choose Interface</h3>
            <p className="mode-subtitle">Select your preferred experience</p>
            
            <div className="mode-choices">
              <button 
                className={`mode-choice ${interfaceMode === 'luna' ? 'selected' : ''}`}
                onClick={() => handleModeChange('luna')}
              >
                <span className="choice-icon">🌙</span>
                <div className="choice-info">
                  <span className="choice-name">Luna Avatar</span>
                  <span className="choice-desc">Voice-first AI with stunning visuals</span>
                </div>
                {interfaceMode === 'luna' && <span className="choice-check">✓</span>}
              </button>

              <button 
                className={`mode-choice ${interfaceMode === 'avatar' ? 'selected' : ''}`}
                onClick={() => handleModeChange('avatar')}
              >
                <span className="choice-icon">🖼️</span>
                <div className="choice-info">
                  <span className="choice-name">Avatar Only</span>
                  <span className="choice-desc">Fullscreen Luna with simple prompts</span>
                </div>
                {interfaceMode === 'avatar' && <span className="choice-check">✓</span>}
              </button>
              
              <button 
                className={`mode-choice ${interfaceMode === 'chat' ? 'selected' : ''}`}
                onClick={() => handleModeChange('chat')}
              >
                <span className="choice-icon">💬</span>
                <div className="choice-info">
                  <span className="choice-name">Text Chat</span>
                  <span className="choice-desc">Classic text conversation</span>
                </div>
                {interfaceMode === 'chat' && <span className="choice-check">✓</span>}
              </button>
            </div>

            <button 
              className="mode-close"
              onClick={() => setShowModeSelector(false)}
            >
              Close
            </button>
          </div>
        </div>
      )}

      {/* Render Interface */}
      {interfaceMode === 'luna' && <LunaFreeInterface />}
      {interfaceMode === 'avatar' && <LunaAvatarInterface />}
      {interfaceMode === 'chat' && <ChatInterface />}
    </div>
  );
}

export default App;
