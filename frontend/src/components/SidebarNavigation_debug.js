import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import './SidebarNavigation.css';

const SidebarNavigation = ({ onFeatureSelect, showMealPlanner, onToggleMealPlanner, showPantry, onTogglePantry, onShowGroceryList, showChat, onToggleChat }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [activeFeature, setActiveFeature] = useState('cookbook');
  // const [showUserMenu, setShowUserMenu] = useState(false);

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
      id: 'meal-planner',
      icon: '📅',
      label: 'Meal Planner',
      description: 'Customizable meal planning',
      available: true,
      onClick: () => {
        onToggleMealPlanner?.();
        setActiveFeature('meal-planner');
      }
    }
  ];

  return (
    <nav className="sidebar-navigation">
      <div className="navigation-header">
        <div className="app-logo">
          <span className="logo-icon">🍽️</span>
          <span className="logo-text">Yes Chef!</span>
        </div>
      </div>

      <div className="features-grid">
        {features.map(feature => (
          <button
            key={feature.id}
            className="feature-card"
            onClick={feature.onClick}
            title={feature.description}
          >
            <div className="feature-icon">{feature.icon}</div>
            <div className="feature-label">{feature.label}</div>
          </button>
        ))}
      </div>
    </nav>
  );
};

export default SidebarNavigation;
