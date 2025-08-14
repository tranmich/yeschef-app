import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import './CompactHeader.css';

const CompactHeader = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [showUserMenu, setShowUserMenu] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
    setShowUserMenu(false);
  };

  const toggleUserMenu = () => {
    setShowUserMenu(!showUserMenu);
  };

  const getUserInitials = (name) => {
    if (!name) return 'U';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  return (
    <header className="compact-header">
      <div className="header-left">
        <div className="app-logo">
          <span className="logo-icon">🍽️</span>
          <span className="logo-text">Hungie</span>
        </div>
      </div>

      <div className="header-right">
        <div className="user-menu-container">
          <button 
            className="user-avatar" 
            onClick={toggleUserMenu}
            title={`${user?.name} - Click for account menu`}
          >
            <span className="avatar-initials">{getUserInitials(user?.name)}</span>
          </button>
          
          {showUserMenu && (
            <div className="user-dropdown">
              <div className="user-info">
                <div className="user-name">{user?.name}</div>
                <div className="user-email">{user?.email}</div>
              </div>
              <div className="dropdown-divider"></div>
              <div className="dropdown-actions">
                <button className="dropdown-item" disabled>
                  ⚙️ Account Settings
                </button>
                <button className="dropdown-item" disabled>
                  🎨 Preferences
                </button>
                <div className="dropdown-divider"></div>
                <button className="dropdown-item logout" onClick={handleLogout}>
                  🚪 Sign Out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default CompactHeader;
