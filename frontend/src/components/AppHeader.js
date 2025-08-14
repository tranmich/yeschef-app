import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import './AppHeader.css';

const AppHeader = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="app-header">
      <div className="header-content">
        {/* Left side - User Info */}
        <div className="header-left">
          <div 
            className="user-profile"
            onClick={() => setDropdownOpen(!dropdownOpen)}
          >
            <div className="user-avatar">
              {user?.name?.charAt(0)?.toUpperCase() || 'U'}
            </div>
            <span className="user-name">{user?.name}</span>
            <span className={`dropdown-arrow ${dropdownOpen ? 'open' : ''}`}>
              ▼
            </span>
          </div>

          {dropdownOpen && (
            <div className="header-dropdown">
              <div className="dropdown-header">
                <div className="dropdown-user-info">
                  <div className="dropdown-avatar">
                    {user?.name?.charAt(0)?.toUpperCase() || 'U'}
                  </div>
                  <div>
                    <div className="dropdown-name">{user?.name}</div>
                    <div className="dropdown-email">{user?.email}</div>
                  </div>
                </div>
              </div>
              
              <div className="dropdown-divider"></div>
              
              <button
                className="dropdown-item"
                onClick={() => {/* Preferences coming soon */}}
                disabled
              >
                <span className="dropdown-icon">⚙️</span>
                Account Settings
                <span className="coming-soon">Soon</span>
              </button>
              
              <div className="dropdown-divider"></div>
              
              <button
                className="dropdown-item logout"
                onClick={handleLogout}
              >
                <span className="dropdown-icon">🚪</span>
                Sign Out
              </button>
            </div>
          )}
        </div>

        {/* Center - App Title */}
        <div className="header-center">
          <div className="app-title">
            <span className="app-logo">🍽️</span>
            <span className="app-name">Hungie</span>
          </div>
        </div>

        {/* Right side - Future features (cart, import, etc.) */}
        <div className="header-right">
          <button className="header-button" disabled title="Import Recipes - Coming Soon">
            <span className="button-icon">📥</span>
          </button>
          <button className="header-button" disabled title="Shopping Cart - Coming Soon">
            <span className="button-icon">🛒</span>
          </button>
        </div>
      </div>

      {/* Mobile overlay to close dropdown */}
      {dropdownOpen && (
        <div 
          className="dropdown-overlay"
          onClick={() => setDropdownOpen(false)}
        ></div>
      )}
    </header>
  );
};

export default AppHeader;
