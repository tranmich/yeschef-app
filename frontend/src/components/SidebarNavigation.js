import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import './SidebarNavigation.css';

const SidebarNavigation = ({ onFeatureSelect, showMealPlanner, onToggleMealPlanner, showPantry, onTogglePantry, onShowGroceryList }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [activeFeature, setActiveFeature] = useState('chat');
  const [showUserMenu, setShowUserMenu] = useState(false);

  // Header functionality
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
      id: 'chat',
      icon: '💬',
      label: 'AI Chef Chat',
      description: 'Chat with Hungie AI',
      available: true,
      onClick: () => {
        setActiveFeature('chat');
        onFeatureSelect?.('chat');
      }
    },
    {
      id: 'meal-planner',
      icon: '📅',
      label: 'Meal Planner',
      description: 'Plan your weekly meals',
      available: true,
      onClick: () => {
        onToggleMealPlanner?.();
        setActiveFeature('meal-planner');
      }
    },
    {
      id: 'saved-recipes',
      icon: '💾',
      label: 'Saved Recipes',
      description: 'Your recipe collection',
      available: false,
      onClick: () => {
        setActiveFeature('saved-recipes');
        onFeatureSelect?.('saved-recipes');
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
      id: 'analytics',
      icon: '📊',
      label: 'Analytics',
      description: 'Cooking insights',
      available: false,
      onClick: () => {
        setActiveFeature('analytics');
        onFeatureSelect?.('analytics');
      }
    }
  ];

  return (
    <nav className="sidebar-navigation">
      {/* Navigation Header with Hungie logo and user account */}
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
      </div>

      <div className="sidebar-content">
        <div className="nav-section">
          <div className="nav-section-title">Features</div>
          <div className="nav-items">
            {features.map((feature) => (
              <button
                key={feature.id}
                className={`nav-item ${activeFeature === feature.id ? 'active' : ''} ${!feature.available ? 'disabled' : ''} ${feature.id === 'meal-planner' && showMealPlanner ? 'active' : ''} ${feature.id === 'pantry' && showPantry ? 'active' : ''}`}
                onClick={feature.onClick}
                disabled={!feature.available}
                title={feature.available ? feature.description : `${feature.description} (Coming Soon)`}
              >
                <div className="nav-item-icon">{feature.icon}</div>
                <div className="nav-item-content">
                  <div className="nav-item-label">{feature.label}</div>
                  {!feature.available && (
                    <div className="nav-item-badge">Soon</div>
                  )}
                </div>
              </button>
            ))}
          </div>
        </div>

        <div className="sidebar-footer">
          <div className="feature-hint">
            <div className="hint-icon">💡</div>
            <div className="hint-text">
              More features coming soon! Focus on AI chat and meal planning for now.
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default SidebarNavigation;
