import React, { useState, useEffect, useRef } from 'react';
import { useDraggable } from '@dnd-kit/core';
import './RecipeListView.css';

const RecipeListView = ({ 
  recipes, 
  selectedCategory, 
  onRecipeClick, 
  onRecipeEdit,
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
      filtered = filtered.filter(recipe =>
        recipe.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        recipe.ingredients?.toLowerCase().includes(searchTerm.toLowerCase())
      );
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

    return sorted;
  }, [recipes, searchTerm, sortBy, sortOrder]);

  const getCategoryDisplayName = (categoryId) => {
    const categoryNames = {
      'all': 'All Recipes',
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
    <div className="recipe-list-view">
      <div className="recipe-list-header">
        <div className="category-title">
          <h2>{getCategoryDisplayName(selectedCategory)}</h2>
          <span className="recipe-count">({filteredAndSortedRecipes.length})</span>
        </div>

        <div className="view-controls">
          <div className="search-bar">
            <input
              type="text"
              placeholder="Search..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>
          
          <div className="sort-controls">
            <select 
              value={sortBy} 
              onChange={(e) => setSortBy(e.target.value)}
              className="sort-select"
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
              <p>No recipes found</p>
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
                          {categoryRecipes.map(recipe => (
                            <RecipeCard
                              key={recipe.id}
                              recipe={recipe}
                              onRecipeClick={onRecipeClick}
                              onRecipeEdit={onRecipeEdit}
                              isChild={true}
                            />
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                // Show flat list for specific category
                <div className="recipe-list">
                  {filteredAndSortedRecipes.map(recipe => (
                    <RecipeCard
                      key={recipe.id}
                      recipe={recipe}
                      onRecipeClick={onRecipeClick}
                      onRecipeEdit={onRecipeEdit}
                      isChild={false}
                    />
                  ))}
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
        console.log('Remove recipe:', recipe.id);
        break;
      case 'move':
        console.log('Move recipe:', recipe.id);
        break;
      default:
        break;
    }
  };

  const complexity = getComplexity(recipe);

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`recipe-card ${isDragging ? 'dragging' : ''} ${isHovered ? 'hovered' : ''} ${isChild ? 'child-item' : ''}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => {
        setIsHovered(false);
        setShowMenu(false);
      }}
      onClick={(e) => onRecipeClick(recipe)}
      {...listeners}
      {...attributes}
    >
      <div className="recipe-card-header">
        <div className="recipe-title-container">
          {isChild && <span className="tree-indent">    </span>}
          <span className="recipe-title">{recipe.title}</span>
        </div>
        <div className="recipe-actions">
          <button 
            className="action-btn edit-btn"
            onClick={(e) => handleMenuAction('edit', e)}
            title="Edit"
          >
            ✎
          </button>
          <div className="menu-container">
            <button 
              className="action-btn menu-btn"
              onClick={(e) => {
                e.stopPropagation();
                setShowMenu(!showMenu);
              }}
              title="More"
            >
              ⋯
            </button>
            {showMenu && (
              <div className="dropdown-menu">
                <button onClick={(e) => handleMenuAction('edit', e)}>
                  Edit
                </button>
                <button onClick={(e) => handleMenuAction('move', e)}>
                  Move
                </button>
                <button onClick={(e) => handleMenuAction('remove', e)}>
                  Remove
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Recipe info expansion below the card */}
      {isHovered && (
        <div 
          style={{
            marginTop: '4px',
            background: '#f8f9fa',
            border: '1px solid #e9ecef',
            borderRadius: '4px',
            padding: '8px 10px',
            fontSize: '9px',
            lineHeight: '1.3',
            color: '#495057'
          }}
        >
          <div style={{display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '3px'}}>
            <span style={{fontWeight: '500', color: '#374151', minWidth: '35px'}}>Time:</span>
            <span style={{color: '#6b7280'}}>{formatPrepTime(recipe.time_min) || 'Not set'}</span>
          </div>
          
          <div style={{display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '3px'}}>
            <span style={{fontWeight: '500', color: '#374151', minWidth: '35px'}}>Rating:</span>
            <span style={{color: '#6b7280'}}>
              {recipe.rating ? `★ ${recipe.rating}/5` : 'No rating'}
            </span>
          </div>
          
          <div style={{display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '3px'}}>
            <span style={{fontWeight: '500', color: '#374151', minWidth: '35px'}}>Level:</span>
            <span style={{ color: complexity.color, fontWeight: '500' }}>
              {complexity.text}
            </span>
          </div>

          <div style={{display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap'}}>
            {recipe.meal_role && (
              <>
                <span style={{fontWeight: '500', color: '#374151', minWidth: '35px'}}>Type:</span>
                <span style={{color: '#6b7280'}}>{recipe.meal_role}</span>
              </>
            )}
            
            {recipe.is_one_pot && (
              <span style={{
                background: '#22c55e', 
                color: 'white', 
                padding: '1px 4px', 
                borderRadius: '2px', 
                fontSize: '7px',
                marginLeft: 'auto'
              }}>
                One-Pot
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default RecipeListView;
