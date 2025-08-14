import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './SidebarNavigation.css';

const SidebarNavigation = ({ onFeatureSelect, showMealPlanner, onToggleMealPlanner }) => {
  const navigate = useNavigate();
  const [activeFeature, setActiveFeature] = useState('chat');

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
      available: false,
      onClick: () => {
        setActiveFeature('pantry');
        onFeatureSelect?.('pantry');
      }
    },
    {
      id: 'grocery-lists',
      icon: '🛒',
      label: 'Grocery Lists',
      description: 'Smart shopping lists',
      available: false,
      onClick: () => {
        setActiveFeature('grocery-lists');
        onFeatureSelect?.('grocery-lists');
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
      <div className="sidebar-content">
        <div className="nav-section">
          <div className="nav-section-title">Features</div>
          <div className="nav-items">
            {features.map((feature) => (
              <button
                key={feature.id}
                className={`nav-item ${activeFeature === feature.id ? 'active' : ''} ${!feature.available ? 'disabled' : ''} ${feature.id === 'meal-planner' && showMealPlanner ? 'active' : ''}`}
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
