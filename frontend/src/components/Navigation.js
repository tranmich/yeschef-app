import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';
import './Navigation.css';

const Navigation = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navigateTo = (path) => {
    navigate(path);
    setDropdownOpen(false);
  };

  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <nav className="navigation">
      <div className="nav-container">
        
        {/* Logo/Brand */}
        <div className="nav-brand" onClick={() => navigateTo('/')}>
          <span className="nav-logo">🍽️</span>
          <span className="nav-title">Hungie</span>
        </div>

        {/* Navigation Links */}
        <div className="nav-links">
          <button
            className={`nav-link ${isActive('/') ? 'active' : ''}`}
            onClick={() => navigateTo('/')}
          >
            <span className="nav-icon">🤖</span>
            Chat & Plan
          </button>
          
          <button
            className={`nav-link ${isActive('/dashboard') ? 'active' : ''}`}
            onClick={() => navigateTo('/dashboard')}
          >
            <span className="nav-icon">📊</span>
            Dashboard
          </button>
        </div>

        {/* User Menu */}
        <div className="nav-user">
          <div 
            className="user-dropdown"
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
            <div className="dropdown-menu">
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
                onClick={() => navigateTo('/dashboard')}
              >
                <span className="dropdown-icon">📊</span>
                Dashboard
              </button>
              
              <button
                className="dropdown-item"
                onClick={() => navigateTo('/preferences')}
                disabled
              >
                <span className="dropdown-icon">⚙️</span>
                Preferences
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
      </div>

      {/* Mobile overlay to close dropdown */}
      {dropdownOpen && (
        <div 
          className="dropdown-overlay"
          onClick={() => setDropdownOpen(false)}
        ></div>
      )}
    </nav>
  );
};

export default Navigation;
