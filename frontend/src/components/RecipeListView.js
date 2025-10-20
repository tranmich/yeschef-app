import React, { useState, useEffect, useRef } from 'react';
import { useDraggable } from '@dnd-kit/core';
import { formatRecipeText } from '../utils/recipeFormatting';
import './RecipeListView.css';

const RecipeListView = ({ 
  recipes, 
  selectedCategory, 
  onRecipeClick, 
  onRecipeEdit,
  onRefreshRecipes,
  loading = false 
}) => {
  const [sortBy, setSortBy] = useState('alphabetical');
  const [sortOrder, setSortOrder] = useState('asc');
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState('table'); // 'table' or 'columns'

  // Filter and sort recipes
  const filteredAndSortedRecipes = React.useMemo(() => {
    let filtered = recipes || [];

    // Filter by search term
    if (searchTerm) {
      console.log('🔍 Searching with term:', searchTerm);
      console.log('🔍 Total recipes before filter:', filtered.length);
      
      filtered = filtered.filter(recipe => {
        const titleMatch = recipe.title?.toLowerCase().includes(searchTerm.toLowerCase());
        
        // Handle ingredients as both string and array
        let ingredientsMatch = false;
        if (recipe.ingredients) {
          if (typeof recipe.ingredients === 'string') {
            // Handle ingredients as string
            ingredientsMatch = recipe.ingredients.toLowerCase().includes(searchTerm.toLowerCase());
          } else if (Array.isArray(recipe.ingredients)) {
            // Handle ingredients as array - search through all ingredients
            ingredientsMatch = recipe.ingredients.some(ingredient => {
              const ingredientText = typeof ingredient === 'string' 
                ? ingredient 
                : ingredient.name || ingredient.ingredient || String(ingredient);
              return ingredientText.toLowerCase().includes(searchTerm.toLowerCase());
            });
          }
        }
        
        const matches = titleMatch || ingredientsMatch;
        
        // Debug logging for imported recipes
        if (recipe.confidence !== undefined || recipe.imported_at) {
          console.log('🔍 Checking imported recipe:', {
            title: recipe.title,
            ingredients: recipe.ingredients,
            titleMatch,
            ingredientsMatch,
            matches,
            searchTerm
          });
        }
        
        return matches;
      });
      
      console.log('🔍 Total recipes after filter:', filtered.length);
    }

    // Sort recipes
    const sorted = [...filtered].sort((a, b) => {
      let aValue, bValue;

      switch (sortBy) {
        case 'alphabetical':
          aValue = a.title?.toLowerCase() || '';
          bValue = b.title?.toLowerCase() || '';
          break;
        case 'date':
          aValue = new Date(a.created_at || a.date_added || 0);
          bValue = new Date(b.created_at || b.date_added || 0);
          break;
        case 'rating':
          aValue = a.rating || 0;
          bValue = b.rating || 0;
          break;
        case 'prep_time':
          aValue = a.time_min || a.prep_time || 999;
          bValue = b.time_min || b.prep_time || 999;
          break;
        default:
          return 0;
      }

      if (sortBy === 'date') {
        return sortOrder === 'asc' ? aValue - bValue : bValue - aValue;
      }

      if (typeof aValue === 'string') {
        return sortOrder === 'asc' 
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      }

      return sortOrder === 'asc' ? aValue - bValue : bValue - aValue;
    });

    // Debug final sorted results
    if (searchTerm) {
      console.log('🔍 Final sorted results:', sorted.length, 'recipes');
      const importedInResults = sorted.filter(r => r.confidence !== undefined);
      console.log('🔍 Imported recipes in final results:', importedInResults.map(r => r.title));
      console.log('🔍 First 5 results:', sorted.slice(0, 5).map(r => r.title));
    }

    return sorted;
  }, [recipes, searchTerm, sortBy, sortOrder]);

  const getCategoryDisplayName = (categoryId) => {
    const categoryNames = {
      'all': 'All Recipes',
      'recent-imports': 'Recent Imports',
      'breakfast': 'Breakfast',
      'lunch': 'Lunch', 
      'dinner': 'Dinner',
      'desserts': 'Desserts',
      'one-pot': 'One-Pot Meals',
      'quick': 'Quick & Easy',
      'favorites': 'My Favorites'
    };
    return categoryNames[categoryId] || categoryId.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const formatPrepTime = (timeMin) => {
    if (!timeMin) return '';
    if (timeMin < 60) return `${timeMin}min`;
    const hours = Math.floor(timeMin / 60);
    const mins = timeMin % 60;
    return mins > 0 ? `${hours}h ${mins}min` : `${hours}h`;
  };

  const getPantryMatchDisplay = (recipe) => {
    if (recipe.pantryOverlap && recipe.pantryOverlap > 0) {
      return `🥫${Math.round(recipe.pantryOverlap * 100)}%`;
    }
    return '';
  };

  const handleSortChange = (newSortBy) => {
    if (sortBy === newSortBy) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(newSortBy);
      setSortOrder('asc');
    }
  };

  return (
    <div className="recipe-list-view hungie-bg-paper hungie-readable-text">
      <div className="recipe-list-header hungie-bg-paper-dark hungie-border hungie-rounded-md hungie-p-4 hungie-mb-4">
        <div className="category-title">
          <h2 className="hungie-text-charcoal hungie-font-semibold">{getCategoryDisplayName(selectedCategory)}</h2>
          <span className="recipe-count hungie-text-sage">
            {searchTerm ? (
              <>({filteredAndSortedRecipes.length} of {recipes?.length || 0})</>
            ) : (
              <>({filteredAndSortedRecipes.length} {filteredAndSortedRecipes.length === 1 ? 'recipe' : 'recipes'})</>
            )}
          </span>
        </div>

        <div className="view-controls">
          <div className="search-bar">
            <input
              type="text"
              placeholder="Search recipes..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input hungie-form-input"
            />
          </div>
          
          <div className="sort-controls">
            <select 
              value={sortBy} 
              onChange={(e) => setSortBy(e.target.value)}
              className="sort-select hungie-form-input"
            >
              <option value="alphabetical">Name</option>
              <option value="prep_time">Time</option>
              <option value="rating">Rating</option>
              <option value="date">Date</option>
            </select>
          </div>
        </div>
      </div>

      <div className="recipes-container" style={{overflow: 'visible', position: 'relative'}}>
        <div className="recipes-scrollable" style={{
          maxHeight: 'calc(100vh - 200px)', 
          overflowY: 'auto', 
          overflowX: 'visible',
          paddingRight: '8px' // Account for scrollbar
        }}>
          {loading ? (
            <div className="loading-state">
              <div className="loading-spinner"></div>
              <p>Loading...</p>
            </div>
          ) : filteredAndSortedRecipes.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-content">
                <div className="empty-state-icon">📚</div>
                <h3>Your cookbook is empty</h3>
                <p>Start building your recipe collection! Import recipes from any website in seconds.</p>
                <div className="empty-state-actions">
                  <button 
                    className="import-recipe-btn hungie-btn hungie-btn-primary"
                    onClick={() => {
                      // Trigger the import feature
                      const sidebar = document.querySelector('[data-feature="import"]');
                      if (sidebar) {
                        sidebar.click();
                      } else {
                        alert('💡 Click on "📥 Import Recipe" in the sidebar to get started!');
                      }
                    }}
                  >
                    📥 Import Recipe
                  </button>
                  <div className="quick-tips">
                    <p><strong>💡 Pro tip:</strong> Just paste any recipe URL and we'll extract it automatically!</p>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="recipe-explorer" style={{overflow: 'visible', position: 'relative', zIndex: 1}}>
              {selectedCategory === 'all' ? (
                // Show categorized tree view for "All" 
                <div className="category-tree">
                  {['breakfast', 'lunch', 'dinner', 'desserts'].map(categoryType => {
                    const categoryRecipes = filteredAndSortedRecipes.filter(recipe => 
                      recipe.meal_role === categoryType || 
                      (categoryType === 'desserts' && (recipe.meal_role === 'dessert' || recipe.meal_role === 'snack'))
                    );
                    
                    if (categoryRecipes.length === 0) return null;
                    
                    return (
                      <div key={categoryType} className="category-section">
                        <div className="category-header">
                          <span className="category-icon">▶</span>
                          <span className="category-name">
                            {categoryType.charAt(0).toUpperCase() + categoryType.slice(1)}
                          </span>
                          <span className="category-count">({categoryRecipes.length})</span>
                        </div>
                        <div className="recipe-list">
                          {categoryRecipes.map(recipe => {
                            try {
                              return (
                                <RecipeCard
                                  key={recipe.id}
                                  recipe={recipe}
                                  onRecipeClick={onRecipeClick}
                                  onRecipeEdit={onRecipeEdit}
                                  onRefreshRecipes={onRefreshRecipes}
                                  isChild={true}
                                />
                              );
                            } catch (error) {
                              console.error('🔍 Error rendering recipe:', recipe.title, error);
                              return null;
                            }
                          })}
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                // Show flat list for specific category
                <div className="recipe-list">
                  {filteredAndSortedRecipes.map(recipe => {
                    try {
                      return (
                        <RecipeCard
                          key={recipe.id}
                          recipe={recipe}
                          onRecipeClick={onRecipeClick}
                          onRecipeEdit={onRecipeEdit}
                          onRefreshRecipes={onRefreshRecipes}
                          isChild={false}
                        />
                      );
                    } catch (error) {
                      console.error('🔍 Error rendering recipe in flat view:', recipe.title, error);
                      return null;
                    }
                  })}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// VS Code Explorer Style Recipe Card
const RecipeCard = ({ 
  recipe, 
  onRecipeClick, 
  onRecipeEdit,
  onRefreshRecipes,
  isChild = false
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [showMenu, setShowMenu] = useState(false);

  // @dnd-kit draggable hook
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    isDragging,
  } = useDraggable({
    id: `recipe-${recipe.id}`,
    data: {
      recipe: recipe,
    },
  });

  const style = transform ? {
    transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`,
    opacity: isDragging ? 0.5 : 1,
    zIndex: isDragging ? 1000 : 1,
  } : undefined;

  const formatPrepTime = (timeMin) => {
    if (!timeMin) return '';
    if (timeMin < 60) return `${timeMin}min`;
    const hours = Math.floor(timeMin / 60);
    const mins = timeMin % 60;
    return mins > 0 ? `${hours}h ${mins}min` : `${hours}h`;
  };

  const getComplexity = (recipe) => {
    if (recipe.is_easy) return { text: 'Easy', color: '#22c55e' };
    if (recipe.time_min > 60) return { text: 'Complex', color: '#ef4444' };
    return { text: 'Medium', color: '#f59e0b' };
  };

  const handleMenuAction = (action, e) => {
    e.stopPropagation();
    setShowMenu(false);
    
    switch (action) {
      case 'edit':
        onRecipeEdit(recipe);
        break;
      case 'remove':
        handleDeleteRecipe();
        break;
      case 'move':
        console.log('Move recipe:', recipe.id);
        break;
      default:
        break;
    }
  };

  const handleDeleteRecipe = async () => {
    // Show confirmation dialog
    const confirmDelete = window.confirm(
      `Are you sure you want to delete "${recipe.title}"?\n\nThis action cannot be undone.`
    );
    
    if (!confirmDelete) {
      return;
    }
    
    console.log('🗑️ Attempting to delete recipe:', {
      id: recipe.id,
      title: recipe.title,
      user_id: recipe.user_id,
      is_template: recipe.is_template
    });
    
    try {
      const token = localStorage.getItem('authToken');
      if (!token) {
        alert('Please log in to delete recipes');
        return;
      }
      
      console.log(`🌐 Making DELETE request to: /api/recipes/${recipe.id}`);
      
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/recipes/${recipe.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      console.log('📡 Delete response status:', response.status);
      
      const result = await response.json();
      console.log('📄 Delete response data:', result);
      
      if (result.success) {
        alert(`✅ ${result.message}`);
        // Refresh the recipe list using the parent's refresh function
        if (onRefreshRecipes) {
          onRefreshRecipes();
        } else {
          // Fallback to page reload if no refresh function provided
          window.location.reload();
        }
      } else {
        // Check if this is an orphaned recipe that can be claimed
        if (result.can_claim) {
          const claimConfirm = window.confirm(
            `${result.error}\n\nWould you like to claim ownership of this recipe so you can delete it?`
          );
          
          if (claimConfirm) {
            await handleClaimRecipe();
          }
        } else {
          alert(`❌ Error: ${result.error}`);
        }
      }
      
    } catch (error) {
      console.error('Delete recipe error:', error);
      alert(`❌ Failed to delete recipe: ${error.message}`);
    }
  };

  const handleClaimRecipe = async () => {
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/recipes/${recipe.id}/claim`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      const result = await response.json();
      
      if (result.success) {
        alert(`✅ ${result.message}\n\nYou can now delete this recipe if needed.`);
        // Refresh the recipe list
        if (onRefreshRecipes) {
          onRefreshRecipes();
        }
      } else {
        alert(`❌ Failed to claim recipe: ${result.error}`);
      }
      
    } catch (error) {
      console.error('Claim recipe error:', error);
      alert(`❌ Failed to claim recipe: ${error.message}`);
    }
  };

  // Helper function to get theme color based on recipe category or random assignment
  const getRecipeTheme = (recipe) => {
    if (recipe.category) {
      const category = recipe.category.toLowerCase();
      if (category.includes('breakfast') || category.includes('brunch')) return 'yellow';
      if (category.includes('dessert') || category.includes('sweet')) return 'red';
      if (category.includes('salad') || category.includes('vegetable')) return 'sage';
      if (category.includes('main') || category.includes('dinner')) return 'blue';
    }
    // Default theme rotation based on recipe ID for consistent colors
    const themes = ['sage', 'yellow', 'blue', 'red'];
    return themes[recipe.id % 4] || 'sage';
  };

  const complexity = getComplexity(recipe);
  const recipeTheme = getRecipeTheme(recipe);

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`recipe-card hungie-recipe-card ${recipeTheme}-theme ${isDragging ? 'dragging' : ''} ${isChild ? 'child-item' : ''}`}
      onClick={(e) => onRecipeClick(recipe)}
      {...listeners}
      {...attributes}
    >
      <div className="recipe-card-content">
        {/* Left side - Title and tags */}
        <div className="recipe-info-left">
          {isChild && <span className="tree-indent">    </span>}
          <div className="recipe-title-section">
            <span className="recipe-title hungie-recipe-title">{recipe.title}</span>
            <div className="recipe-tags">
              {recipe.meal_role && (
                <span className="recipe-tag meal-tag">{recipe.meal_role}</span>
              )}
              {recipe.is_one_pot && (
                <span className="recipe-tag one-pot-tag">One-Pot</span>
              )}
              {complexity && (
                <span className="recipe-tag complexity-tag" style={{ color: complexity.color }}>
                  {complexity.text}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Right side - Quick info and actions */}
        <div className="recipe-info-right">
          <div className="recipe-quick-info">
            {(recipe.cooking_time || recipe.time_min) && (
              <span className="info-item" title="Prep time">
                ⏱️ {formatPrepTime(recipe.time_min || recipe.cooking_time)}
              </span>
            )}
            {recipe.servings && (
              <span className="info-item" title="Servings">
                👥 {recipe.servings}
              </span>
            )}
            {recipe.rating && (
              <span className="info-item" title="Rating">
                ⭐ {recipe.rating}/5
              </span>
            )}
          </div>
          <div className="recipe-actions">
            <button 
              className="action-btn edit-btn"
              onClick={(e) => handleMenuAction('edit', e)}
              title="Edit recipe"
            >
              ✎
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RecipeListView;
