import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import * as householdAPI from '../utils/householdAPI';
import { useToast } from '../components/ToastContainer';
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
  const toast = useToast();
  const [activeFeature, setActiveFeature] = useState('cookbook');
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [isCategoriesExpanded, setIsCategoriesExpanded] = useState(true);
  const [isHouseholdsExpanded, setIsHouseholdsExpanded] = useState(false);
  const [households, setHouseholds] = useState([]);
  const [loadingHouseholds, setLoadingHouseholds] = useState(false);
  const [showCreateHouseholdModal, setShowCreateHouseholdModal] = useState(false);
  const [newHouseholdName, setNewHouseholdName] = useState('');
  const [newHouseholdDescription, setNewHouseholdDescription] = useState('');
  const [creatingHousehold, setCreatingHousehold] = useState(false);
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

  // Load households function
  const loadHouseholds = async () => {
    if (!user?.id) return;
    
    try {
      setLoadingHouseholds(true);
      console.log('📋 Loading households for user:', user.id);
      const response = await householdAPI.getHouseholds();
      console.log('📋 Households API response:', response);
      
      if (response.success) {
        // API returns households in response.households, not response.data
        const householdsList = response.households || response.data || [];
        console.log('✅ Households loaded:', householdsList);
        setHouseholds(householdsList);
      } else {
        console.error('❌ Failed to load households:', response);
      }
    } catch (error) {
      console.error('❌ Error loading households:', error);
    } finally {
      setLoadingHouseholds(false);
    }
  };

  // Load households on mount and when user changes
  useEffect(() => {
    if (user?.id) {
      loadHouseholds();
    }
  }, [user?.id]);

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

  // Default categories without icons
  const defaultCategories = [
    { id: 'all', name: 'All', color: '#6B7280', isDefault: true },
    { id: 'recent-imports', name: 'Recent Imports', color: '#059669', isDefault: true, priority: true },
    { id: 'breakfast', name: 'Breakfast', color: '#F59E0B', isDefault: true },
    { id: 'lunch', name: 'Lunch', color: '#10B981', isDefault: true },
    { id: 'dinner', name: 'Dinner', color: '#3B82F6', isDefault: true },
    { id: 'desserts', name: 'Desserts', color: '#8B5CF6', isDefault: true },
    { id: 'one-pot', name: 'One-Pot', color: '#EF4444', isDefault: true },
    { id: 'quick', name: 'Quick', color: '#F97316', isDefault: true },
    { id: 'favorites', name: 'Favorites', color: '#EC4899', isDefault: true }
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

  const toggleHouseholdsExpansion = () => {
    setIsHouseholdsExpanded(!isHouseholdsExpanded);
  };

  const handleHouseholdClick = (household) => {
    // Open whiteboard gallery for this household (not direct to canvas)
    setActiveFeature('households');
    onFeatureSelect?.('households', { 
      householdId: household.id,
      showGallery: true // Show gallery, not canvas
    });
  };

  const handleCreateHousehold = async (e) => {
    e.preventDefault();

    if (!newHouseholdName.trim()) {
      toast.warning('Please enter a household name');
      return;
    }

    try {
      setCreatingHousehold(true);

      const response = await householdAPI.createHousehold(
        newHouseholdName.trim(),
        newHouseholdDescription.trim() || ''
      );

      if (response.success) {
        // Close modal and reset form
        setShowCreateHouseholdModal(false);
        setNewHouseholdName('');
        setNewHouseholdDescription('');

        // Reload households to show the new one
        await loadHouseholds();
        
        toast.success(`Created: ${newHouseholdName.trim()}`);
      } else {
        toast.error(response.message || 'Failed to create household');
      }
    } catch (err) {
      console.error('Error creating household:', err);
      toast.error('Failed to create household');
    } finally {
      setCreatingHousehold(false);
    }
  };

  const handleCategoryClick = (categoryId) => {
    onCategorySelect?.(categoryId);
  };

  const features = [
    {
      id: 'community',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
          <polyline points="9 22 9 12 15 12 15 22"/>
        </svg>
      ),
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
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
          <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
        </svg>
      ),
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
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="16"/>
          <line x1="8" y1="12" x2="16" y2="12"/>
        </svg>
      ),
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
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
          <line x1="16" y1="2" x2="16" y2="6"/>
          <line x1="8" y1="2" x2="8" y2="6"/>
          <line x1="3" y1="10" x2="21" y2="10"/>
        </svg>
      ),
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
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="9" cy="21" r="1"/>
          <circle cx="20" cy="21" r="1"/>
          <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>
        </svg>
      ),
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
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
          <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
          <line x1="12" y1="22.08" x2="12" y2="12"/>
        </svg>
      ),
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
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
          <circle cx="9" cy="7" r="4"/>
          <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
          <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
        </svg>
      ),
      label: 'Friends',
      description: 'Connect with friends and family',
      available: true,
      onClick: () => {
        setActiveFeature('friends');
        onFeatureSelect?.('friends');
      }
    },
    {
      id: 'households',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
          <polyline points="9 22 9 12 15 12 15 22"/>
        </svg>
      ),
      label: 'Households',
      description: 'Collaborative whiteboards',
      available: true,
      badge: 'NEW',
      onClick: () => {
        setActiveFeature('households');
        onFeatureSelect?.('households');
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

              {/* Households Inline Section */}
              {feature.id === 'households' && (
                <div className="households-section">
                  <button 
                    className="households-toggle"
                    onClick={toggleHouseholdsExpansion}
                  >
                    <span className="toggle-icon">
                      {isHouseholdsExpanded ? '▼' : '▶'}
                    </span>
                    <span className="toggle-label">My Households</span>
                    <button 
                      className="add-household-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        setShowCreateHouseholdModal(true);
                      }}
                      title="Create New Household"
                    >
                      +
                    </button>
                  </button>
                  
                  {isHouseholdsExpanded && (
                    <div className="households-list-inline">
                      {loadingHouseholds ? (
                        <div className="households-loading">Loading...</div>
                      ) : households.length === 0 ? (
                        <div className="households-empty">
                          <p>No households yet</p>
                          <small>Click + to create one</small>
                        </div>
                      ) : (
                        households.map(household => (
                          <button
                            key={household.id}
                            className="household-item-inline"
                            onClick={() => handleHouseholdClick(household)}
                            title={`Open ${household.name} whiteboard`}
                          >
                            <span className="household-icon">🏠</span>
                            <span className="household-name">{household.name}</span>
                            <span className="household-role">{household.role}</span>
                          </button>
                        ))
                      )}
                    </div>
                  )}
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

      {/* Create Household Modal */}
      {showCreateHouseholdModal && (
        <div className="household-modal-overlay" onClick={() => setShowCreateHouseholdModal(false)}>
          <div className="household-modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="household-modal-header">
              <h2>Create New Household</h2>
              <button className="close-button" onClick={() => setShowCreateHouseholdModal(false)}>
                ×
              </button>
            </div>

            <form onSubmit={handleCreateHousehold}>
              <div className="form-group">
                <label htmlFor="household-name">Household Name *</label>
                <input
                  id="household-name"
                  type="text"
                  placeholder="e.g., My Family, Roommates"
                  value={newHouseholdName}
                  onChange={(e) => setNewHouseholdName(e.target.value)}
                  autoFocus
                  disabled={creatingHousehold}
                />
              </div>

              <div className="form-group">
                <label htmlFor="household-description">Description (optional)</label>
                <textarea
                  id="household-description"
                  placeholder="Who's in this household?"
                  value={newHouseholdDescription}
                  onChange={(e) => setNewHouseholdDescription(e.target.value)}
                  rows={3}
                  disabled={creatingHousehold}
                />
              </div>

              <div className="modal-actions">
                <button
                  type="button"
                  className="cancel-button"
                  onClick={() => setShowCreateHouseholdModal(false)}
                  disabled={creatingHousehold}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="create-button"
                  disabled={creatingHousehold || !newHouseholdName.trim()}
                >
                  {creatingHousehold ? 'Creating...' : 'Create Household'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </nav>
  );
};

export default SidebarNavigation;

