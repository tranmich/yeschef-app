import React, { useState, useEffect } from 'react';
import './RecipeSharing.css';

const RecipeSharing = () => {
  const [activeTab, setActiveTab] = useState('shared-with-me');
  const [sharedRecipes, setSharedRecipes] = useState([]);
  const [mySharedRecipes, setMySharedRecipes] = useState([]);
  const [friends, setFriends] = useState([]);
  const [households, setHouseholds] = useState([]);
  const [showShareModal, setShowShareModal] = useState(false);
  const [selectedRecipe, setSelectedRecipe] = useState(null);
  const [shareTargets, setShareTargets] = useState([]);
  const [shareMessage, setShareMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    loadSharedContent();
  }, []);

  const loadSharedContent = async () => {
    setLoading(true);
    setError('');
    
    try {
      // For demo purposes, we'll use mock data
      // In real implementation, these would be API calls
      await Promise.all([
        loadSharedWithMe(),
        loadMySharedRecipes(),
        loadShareTargets()
      ]);
    } catch (error) {
      setError('Failed to load shared recipes');
      console.error('Error loading shared content:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadSharedWithMe = async () => {
    // Mock data for recipes shared with the user
    const mockSharedRecipes = [
      {
        id: 1,
        title: 'Grandma\'s Chocolate Chip Cookies',
        description: 'The family recipe that\'s been passed down for generations',
        sharedBy: 'Mom',
        sharedAt: '2 days ago',
        category: 'Desserts',
        difficulty: 'Easy',
        prep_time: '15 min',
        cook_time: '12 min',
        servings: '24 cookies',
        sharedFrom: 'Family Kitchen',
        type: 'household'
      },
      {
        id: 2,
        title: 'Spicy Thai Basil Chicken',
        description: 'Authentic Thai recipe with amazing flavor',
        sharedBy: 'Sarah Chen',
        sharedAt: '1 week ago',
        category: 'Asian',
        difficulty: 'Medium',
        prep_time: '20 min',
        cook_time: '15 min',
        servings: '4',
        sharedFrom: 'Sarah\'s Kitchen',
        type: 'friend'
      },
      {
        id: 3,
        title: 'Sunday Roast Dinner',
        description: 'Perfect family roast with all the trimmings',
        sharedBy: 'Dad',
        sharedAt: '3 days ago',
        category: 'Main Course',
        difficulty: 'Hard',
        prep_time: '30 min',
        cook_time: '2 hours',
        servings: '6-8',
        sharedFrom: 'Family Kitchen',
        type: 'household'
      }
    ];
    setSharedRecipes(mockSharedRecipes);
  };

  const loadMySharedRecipes = async () => {
    // Mock data for recipes the user has shared
    const mockMySharedRecipes = [
      {
        id: 101,
        title: 'Mediterranean Quinoa Salad',
        description: 'Healthy and delicious salad perfect for meal prep',
        sharedWith: ['Family Kitchen', 'Sarah Chen', 'Mike Johnson'],
        sharedAt: '5 days ago',
        category: 'Salads',
        difficulty: 'Easy',
        prep_time: '15 min',
        views: 12,
        saves: 3
      },
      {
        id: 102,
        title: 'Homemade Pizza Dough',
        description: 'Easy recipe for perfect pizza night',
        sharedWith: ['Family Kitchen'],
        sharedAt: '1 week ago',
        category: 'Bread',
        difficulty: 'Medium',
        prep_time: '2 hours',
        views: 8,
        saves: 2
      }
    ];
    setMySharedRecipes(mockMySharedRecipes);
  };

  const loadShareTargets = async () => {
    // Mock data for friends and households to share with
    const mockFriends = [
      { id: 1, name: 'Sarah Chen', type: 'friend' },
      { id: 2, name: 'Mike Johnson', type: 'friend' },
      { id: 3, name: 'Emma Wilson', type: 'friend' }
    ];
    
    const mockHouseholds = [
      { id: 1, name: 'Family Kitchen', type: 'household', members: 4 },
      { id: 2, name: 'Roommates', type: 'household', members: 3 }
    ];
    
    setFriends(mockFriends);
    setHouseholds(mockHouseholds);
  };

  const handleShareRecipe = (recipe) => {
    setSelectedRecipe(recipe);
    setShareTargets([]);
    setShareMessage('');
    setShowShareModal(true);
  };

  const handleToggleShareTarget = (target) => {
    setShareTargets(prev => {
      const isSelected = prev.some(t => t.id === target.id && t.type === target.type);
      if (isSelected) {
        return prev.filter(t => !(t.id === target.id && t.type === target.type));
      } else {
        return [...prev, target];
      }
    });
  };

  const handleConfirmShare = async () => {
    if (shareTargets.length === 0) {
      setError('Please select at least one friend or household to share with');
      return;
    }
    
    setError('');
    
    try {
      // In real implementation, this would be an API call
      const shareData = {
        recipeId: selectedRecipe.id,
        targets: shareTargets,
        message: shareMessage.trim()
      };
      
      console.log('Sharing recipe:', shareData);
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSuccess(`Recipe "${selectedRecipe.title}" shared with ${shareTargets.length} recipient(s)!`);
      setShowShareModal(false);
      
      // Refresh shared recipes
      loadMySharedRecipes();
      
      // Clear success message after 5 seconds
      setTimeout(() => setSuccess(''), 5000);
    } catch (error) {
      setError('Failed to share recipe. Please try again.');
    }
  };

  const handleSaveSharedRecipe = async (recipe) => {
    try {
      // In real implementation, this would save the recipe to user's collection
      console.log('Saving shared recipe:', recipe.id);
      
      setSuccess(`"${recipe.title}" saved to your recipe collection!`);
      setTimeout(() => setSuccess(''), 3000);
    } catch (error) {
      setError('Failed to save recipe. Please try again.');
    }
  };

  const getTypeIcon = (type) => {
    return type === 'household' ? '🏠' : '👤';
  };

  const renderTabContent = () => {
    if (loading) {
      return (
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading shared recipes...</p>
        </div>
      );
    }

    switch (activeTab) {
      case 'shared-with-me':
        return (
          <div className="shared-recipes-list">
            {sharedRecipes.length === 0 ? (
              <div className="empty-state">
                <span className="empty-icon">📤</span>
                <h3>No Shared Recipes</h3>
                <p>When friends and family share recipes with you, they'll appear here!</p>
              </div>
            ) : (
              sharedRecipes.map(recipe => (
                <div key={recipe.id} className="shared-recipe-card">
                  <div className="recipe-header">
                    <div className="recipe-info">
                      <h3 className="recipe-title">{recipe.title}</h3>
                      <p className="recipe-description">{recipe.description}</p>
                      <div className="sharing-info">
                        <span className="shared-by">
                          {getTypeIcon(recipe.type)} Shared by <strong>{recipe.sharedBy}</strong> from {recipe.sharedFrom}
                        </span>
                        <span className="shared-time">{recipe.sharedAt}</span>
                      </div>
                    </div>
                    <div className="recipe-actions">
                      <button
                        className="action-button primary"
                        onClick={() => handleSaveSharedRecipe(recipe)}
                      >
                        💾 Save
                      </button>
                      <button className="action-button secondary">👁️ View</button>
                    </div>
                  </div>
                  <div className="recipe-meta">
                    <div className="meta-item">
                      <span className="meta-label">Category:</span>
                      <span className="meta-value">{recipe.category}</span>
                    </div>
                    <div className="meta-item">
                      <span className="meta-label">Difficulty:</span>
                      <span className="meta-value">{recipe.difficulty}</span>
                    </div>
                    <div className="meta-item">
                      <span className="meta-label">Prep Time:</span>
                      <span className="meta-value">{recipe.prep_time}</span>
                    </div>
                    <div className="meta-item">
                      <span className="meta-label">Servings:</span>
                      <span className="meta-value">{recipe.servings}</span>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        );

      case 'my-shared':
        return (
          <div className="my-shared-recipes-list">
            {mySharedRecipes.length === 0 ? (
              <div className="empty-state">
                <span className="empty-icon">📮</span>
                <h3>No Shared Recipes</h3>
                <p>Start sharing your favorite recipes with friends and family!</p>
                <button
                  className="primary-button"
                  onClick={() => {
                    // In real implementation, this would open recipe selection
                    setSelectedRecipe({ id: 'demo', title: 'Demo Recipe' });
                    setShowShareModal(true);
                  }}
                >
                  Share a Recipe
                </button>
              </div>
            ) : (
              mySharedRecipes.map(recipe => (
                <div key={recipe.id} className="my-shared-recipe-card">
                  <div className="recipe-header">
                    <div className="recipe-info">
                      <h3 className="recipe-title">{recipe.title}</h3>
                      <p className="recipe-description">{recipe.description}</p>
                      <div className="sharing-stats">
                        <span className="stat">👁️ {recipe.views} views</span>
                        <span className="stat">💾 {recipe.saves} saves</span>
                        <span className="shared-time">Shared {recipe.sharedAt}</span>
                      </div>
                    </div>
                    <div className="recipe-actions">
                      <button
                        className="action-button secondary"
                        onClick={() => handleShareRecipe(recipe)}
                      >
                        📤 Share Again
                      </button>
                    </div>
                  </div>
                  <div className="shared-with-info">
                    <h4>Shared with:</h4>
                    <div className="shared-targets">
                      {recipe.sharedWith.map((target, index) => (
                        <span key={index} className="shared-target">
                          {target}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="recipe-sharing">
      {/* Header */}
      <div className="sharing-header">
        <h2>Recipe Sharing</h2>
        <p className="header-subtitle">Share recipes with friends and family</p>
      </div>

      {/* Tab Navigation */}
      <div className="tab-navigation">
        <button
          className={`tab-button ${activeTab === 'shared-with-me' ? 'active' : ''}`}
          onClick={() => setActiveTab('shared-with-me')}
        >
          📥 Shared with Me ({sharedRecipes.length})
        </button>
        <button
          className={`tab-button ${activeTab === 'my-shared' ? 'active' : ''}`}
          onClick={() => setActiveTab('my-shared')}
        >
          📤 My Shared Recipes ({mySharedRecipes.length})
        </button>
      </div>

      {/* Messages */}
      {error && (
        <div className="message error-message">
          ❌ {error}
          <button onClick={() => setError('')} className="close-message">×</button>
        </div>
      )}
      {success && (
        <div className="message success-message">
          ✅ {success}
          <button onClick={() => setSuccess('')} className="close-message">×</button>
        </div>
      )}

      {/* Tab Content */}
      <div className="tab-content">
        {renderTabContent()}
      </div>

      {/* Share Recipe Modal */}
      {showShareModal && selectedRecipe && (
        <div className="modal-overlay" onClick={() => setShowShareModal(false)}>
          <div className="modal-content large-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>📤 Share "{selectedRecipe.title}"</h3>
              <button
                className="close-button"
                onClick={() => setShowShareModal(false)}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <p className="modal-instruction">
                Choose friends and households to share this recipe with:
              </p>
              
              {/* Friends Section */}
              <div className="share-section">
                <h4>👥 Friends</h4>
                <div className="share-targets-grid">
                  {friends.map(friend => (
                    <label key={`friend-${friend.id}`} className="share-target-item">
                      <input
                        type="checkbox"
                        checked={shareTargets.some(t => t.id === friend.id && t.type === 'friend')}
                        onChange={() => handleToggleShareTarget({ ...friend, type: 'friend' })}
                      />
                      <span className="target-name">👤 {friend.name}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Households Section */}
              <div className="share-section">
                <h4>🏠 Households</h4>
                <div className="share-targets-grid">
                  {households.map(household => (
                    <label key={`household-${household.id}`} className="share-target-item">
                      <input
                        type="checkbox"
                        checked={shareTargets.some(t => t.id === household.id && t.type === 'household')}
                        onChange={() => handleToggleShareTarget({ ...household, type: 'household' })}
                      />
                      <span className="target-name">
                        🏠 {household.name} ({household.members} members)
                      </span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Message */}
              <div className="share-section">
                <h4>💬 Message (Optional)</h4>
                <textarea
                  value={shareMessage}
                  onChange={(e) => setShareMessage(e.target.value)}
                  placeholder="Add a personal message with your recipe..."
                  className="share-message-input"
                  rows={3}
                />
              </div>

              {/* Share Summary */}
              {shareTargets.length > 0 && (
                <div className="share-summary">
                  <h4>📋 Sharing Summary</h4>
                  <p>
                    This recipe will be shared with{' '}
                    <strong>{shareTargets.length}</strong> recipient(s):
                  </p>
                  <ul className="selected-targets">
                    {shareTargets.map((target, index) => (
                      <li key={index}>
                        {getTypeIcon(target.type)} {target.name}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="modal-actions">
                <button
                  className="secondary-button"
                  onClick={() => setShowShareModal(false)}
                >
                  Cancel
                </button>
                <button
                  className="primary-button"
                  onClick={handleConfirmShare}
                  disabled={shareTargets.length === 0}
                >
                  📤 Share Recipe
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RecipeSharing;