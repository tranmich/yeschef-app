import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import './SidebarNavigation.css';

const SidebarNavigation = ({ onFeatureSelect, showMealPlanner, onToggleMealPlanner, showPantry, onTogglePantry, onShowGroceryList, showChat, onToggleChat }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [activeFeature, setActiveFeature] = useState('cookbook');
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

  const features = [
    {
      id: 'cookbook',
      icon: '📚',
      label: 'My Cookbook',
      description: 'Browse and organize recipes',
      available: true,
      onClick: () => {
        setActiveFeature('cookbook');
        onFeatureSelect?.('cookbook');
      }
    },
    {
      id: 'chat',
      icon: '🤖',
      label: 'AI Chat',
      description: 'Chat with cooking assistant',
      available: true,
      onClick: () => {
        onToggleChat?.();
        setActiveFeature('chat');
      }
    },
    {
      id: 'meal-planner',
      icon: '📅',
      label: 'Meal Planner',
      description: 'Customizable meal planning',
      available: true,
      onClick: () => {
        onToggleMealPlanner?.();
        setActiveFeature('meal-planner');
      }
    },
    {
      id: 'pantry',
      icon: '🥕',
      label: 'Pantry',
      description: 'Track ingredients',
      available: true,
      onClick: () => {
        onTogglePantry?.();
        setActiveFeature('pantry');
      }
    },
    {
      id: 'grocery-lists',
      icon: '🛒',
      label: 'Grocery Lists',
      description: 'Smart shopping lists',
      available: true,
      onClick: () => {
        setActiveFeature('grocery-lists');
        onShowGroceryList?.();
      }
    },
    {
      id: 'import',
      icon: '📥',
      label: 'Import Recipe',
      description: 'Add recipes from anywhere',
      available: true,
      onClick: () => {
        setActiveFeature('import');
        onFeatureSelect?.('import');
      }
    }
  ];

  return (
    <nav className="sidebar-navigation">
      <div className="navigation-header">
        <div className="header-left">
          <div className="app-logo">
            <span className="logo-icon">🍽️</span>
            <span className="logo-text">Yes Chef!</span>
          </div>
        </div>

        <div className="header-right">
          <div className="user-menu-container">
            <button
              className="user-avatar"
              onClick={toggleUserMenu}
              title="User Menu"
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
                  <button 
                    className="dropdown-item logout-btn"
                    onClick={handleLogout}
                  >
                    🚪 Logout
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="features-grid">
        {features.map(feature => {
          const featureClasses = `feature-card ${!feature.available ? 'disabled' : ''} ${activeFeature === feature.id ? 'active' : ''}`;
          return (
            <button
              key={feature.id}
              className={featureClasses}
              onClick={feature.available ? feature.onClick : undefined}
              disabled={!feature.available}
              title={feature.description}
            >
              <div className="feature-icon">{feature.icon}</div>
              <div className="feature-label">{feature.label}</div>
              {!feature.available && (
                <div className="coming-soon-badge">Coming Soon</div>
              )}
            </button>
          );
        })}
      </div>
    </nav>
  );
};

export default SidebarNavigation;
