import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import './SidebarNavigation.css';

const SidebarNavigation = ({ 
  onFeatureSelect, 
  showMealPlanner, 
  onToggleMealPlanner, 
  showPantry, 
  onTogglePantry, 
  onShowGroceryList, 
  showChat, 
  onToggleChat,
  // New props for recipe categories
  selectedCategory,
  onCategorySelect,
  recipeCounts,
  customCategories,
  onAddCategory,
  onRefreshRecipes,
  // Admin props
  isAdmin,
  onShowAdminDashboard
}) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [activeFeature, setActiveFeature] = useState('cookbook');
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [isCategoriesExpanded, setIsCategoriesExpanded] = useState(true);
  const [dropdownPosition, setDropdownPosition] = useState({ top: 0, left: 0 });
  const userMenuRef = useRef(null);
  const userButtonRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target)) {
        setShowUserMenu(false);
      }
    };

    if (showUserMenu) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }
  }, [showUserMenu]);

    const handleLogout = () => {
      logout();
      navigate('/login');
      setShowUserMenu(false);
    };

    const toggleUserMenu = () => {
      if (!showUserMenu && userButtonRef.current) {
        const rect = userButtonRef.current.getBoundingClientRect();
        setDropdownPosition({
          top: rect.bottom + 8,
          left: rect.left - 20
        });
      }
      setShowUserMenu(!showUserMenu);
    };

  const getUserInitials = (name) => {
    if (!name) return 'U';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  // Default categories with icons and colors (from CookbookSidebar)
  const defaultCategories = [
    { id: 'all', name: 'All', icon: '📚', color: '#6B7280', isDefault: true },
    { id: 'recent-imports', name: 'Recent Imports', icon: '📥', color: '#059669', isDefault: true, priority: true },
    { id: 'breakfast', name: 'Breakfast', icon: '🍳', color: '#F59E0B', isDefault: true },
    { id: 'lunch', name: 'Lunch', icon: '🥗', color: '#10B981', isDefault: true },
    { id: 'dinner', name: 'Dinner', icon: '🍽️', color: '#3B82F6', isDefault: true },
    { id: 'desserts', name: 'Desserts', icon: '🍰', color: '#8B5CF6', isDefault: true },
    { id: 'one-pot', name: 'One-Pot', icon: '🥘', color: '#EF4444', isDefault: true },
    { id: 'quick', name: 'Quick', icon: '⚡', color: '#F97316', isDefault: true },
    { id: 'favorites', name: 'Favorites', icon: '⭐', color: '#EC4899', isDefault: true }
  ];

  // Merge default categories with user custom categories
  const allCategories = [
    ...defaultCategories,
    ...(customCategories || []).filter(cat => !defaultCategories.find(def => def.id === cat.id))
  ];

  const getRecipeCount = (categoryId) => {
    return recipeCounts?.[categoryId] || 0;
  };

  const toggleCategoriesExpansion = () => {
    setIsCategoriesExpanded(!isCategoriesExpanded);
  };

  const handleCategoryClick = (categoryId) => {
    onCategorySelect?.(categoryId);
  };

  const features = [
    {
      id: 'community',
      icon: '🌟',
      label: 'Home',
      description: 'Discover amazing recipes',
      available: true,
      onClick: () => {
        setActiveFeature('community');
        onFeatureSelect?.('community');
      }
    },
    {
      id: 'cookbook',
      icon: '📖',
      label: 'My Recipes',
      description: 'Browse and organize recipes',
      available: true,
      onClick: () => {
        setActiveFeature('cookbook');
        onFeatureSelect?.('cookbook');
      }
    },
    {
      id: 'add-recipe',
      icon: '➕',
      label: 'Add Recipe',
      description: 'Import or create recipe',
      available: true,
      onClick: () => {
        setActiveFeature('add-recipe');
        onFeatureSelect?.('import');
      }
    },
    {
      id: 'meal-planner',
      icon: '📅',
      label: 'Meal Plan',
      description: 'Weekly meal planning',
      available: true,
      onClick: () => {
        onToggleMealPlanner?.();
        setActiveFeature('meal-planner');
      }
    },
    {
      id: 'grocery-lists',
      icon: '🛒',
      label: 'Grocery List',
      description: 'Shopping lists',
      available: true,
      onClick: () => {
        onShowGroceryList?.();
        setActiveFeature('grocery-lists');
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
      id: 'friends',
      icon: '👥',
      label: 'Friends',
      description: 'Connect with friends and family',
      available: true,
      onClick: () => {
        setActiveFeature('friends');
        onFeatureSelect?.('friends');
      }
    }
  ];

  return (
    <nav className="sidebar-navigation">
      <div className="navigation-header">
        <div className="header-left">
          <div className="app-logo">
            <img 
              src="/images/yeschef-logo.png" 
              alt="YesChef Logo" 
              className="logo-icon"
            />
          </div>
          
          <div className="user-menu-container" ref={userMenuRef}>
            <button
              ref={userButtonRef}
              className="user-avatar"
              onClick={toggleUserMenu}
              title="User Menu"
            >
              <span className="avatar-initials">{getUserInitials(user?.name)}</span>
            </button>

            {showUserMenu && (
              <div 
                className="user-dropdown"
                style={{
                  top: `${dropdownPosition.top}px`,
                  left: `${dropdownPosition.left}px`
                }}
              >
                <div className="user-info">
                  <div className="user-name">{user?.name}</div>
                  <div className="user-email">{user?.email}</div>
                </div>
                <div className="dropdown-divider"></div>
                <div className="dropdown-actions">
                  <button className="dropdown-item" disabled>
                    ?? Account Settings
                  </button>
                  <button className="dropdown-item" disabled>
                    ?? Preferences
                  </button>
                  <div className="dropdown-divider"></div>
                  <button 
                    className="dropdown-item logout-btn"
                    onClick={handleLogout}
                  >
                    ?? Logout
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
            <div key={feature.id} className="feature-container">
              <button
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

              {/* Recipe Categories Inline Section */}
              {feature.id === 'cookbook' && (
                <div className="recipe-categories-section">
                  <button 
                    className="categories-toggle"
                    onClick={toggleCategoriesExpansion}
                  >
                    <span className="toggle-icon">
                      {isCategoriesExpanded ? '▼' : '▶'}
                    </span>
                    <span className="toggle-label">Categories</span>
                    <span className="categories-count">({allCategories.length})</span>
                  </button>
                  
                  {isCategoriesExpanded && (
                    <div className="categories-list-inline">
                      {allCategories.map(category => (
                        <button
                          key={category.id}
                          className={`category-item-inline ${selectedCategory === category.id ? 'active' : ''}`}
                          onClick={() => handleCategoryClick(category.id)}
                          data-category={category.id}
                          style={{ '--category-color': category.color }}
                        >
                          <span className="category-icon">{category.icon}</span>
                          <span className="category-name">{category.name}</span>
                          <span className="category-count">({getRecipeCount(category.id)})</span>
                        </button>
                      ))}
                    </div>
                  )}
                  
                  <div className="categories-footer-inline">
                    <button 
                      className="refresh-recipes-btn"
                      onClick={() => onRefreshRecipes?.()}
                      title="Refresh Recipes"
                    >
                      🔄 Refresh
                    </button>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Admin Dashboard Button - Bottom of Sidebar */}
      {isAdmin && (
        <div className="admin-section">
          <button
            className="admin-dashboard-btn"
            onClick={() => onShowAdminDashboard?.()}
            title="Admin Dashboard"
          >
            <span className="admin-icon">🔧</span>
            <span className="admin-label">Admin Dashboard</span>
          </button>
        </div>
      )}
    </nav>
  );
};

export default SidebarNavigation;

