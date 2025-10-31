import React, { useState, useMemo } from 'react';
import { useDraggable } from '@dnd-kit/core';
import './RecipeTableView.css';

const RecipeTableView = ({ recipes, onRecipeClick, onRecipeDelete, sortBy: initialSortBy = 'title', sortOrder: initialSortOrder = 'asc' }) => {
  const [sortConfig, setSortConfig] = useState({ key: initialSortBy, direction: initialSortOrder });
  const [selectedRecipes, setSelectedRecipes] = useState(new Set());

  // Draggable Row Component
  const DraggableRow = ({ recipe, isSelected }) => {
    const {
      attributes,
      listeners,
      setNodeRef,
      isDragging,
    } = useDraggable({
      id: `recipe-${recipe.id}`,
      data: {
        type: 'recipe',
        recipe: recipe
      }
    });

    // Don't apply transform - let DragOverlay handle it
    const style = isDragging ? {
      opacity: 0.4,
      filter: 'grayscale(50%)',
    } : undefined;

    return (
      <tr
        ref={setNodeRef}
        style={style}
        className={`${isSelected ? 'selected' : ''} ${isDragging ? 'dragging' : ''}`}
      >
        <td className="checkbox-col" onClick={(e) => e.stopPropagation()}>
          <input
            type="checkbox"
            checked={isSelected}
            onChange={() => toggleSelectRecipe(recipe.id)}
          />
        </td>
        <td 
          className="recipe-title-col" 
          title="Drag to meal plan"
        >
          <div className="title-cell draggable-handle" {...listeners} {...attributes}>
            <svg className="drag-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="3" y1="12" x2="21" y2="12"/>
              <line x1="3" y1="6" x2="21" y2="6"/>
              <line x1="3" y1="18" x2="21" y2="18"/>
            </svg>
            <span className="title-text">{recipe.title}</span>
          </div>
        </td>
        <td>
          <span className="category-badge">{recipe.category || recipe.meal_role || '-'}</span>
        </td>
        <td>{formatTime(recipe.time_min || recipe.cooking_time || recipe.prep_time)}</td>
        <td>{recipe.servings || '-'}</td>
        <td>{formatDifficulty(recipe.difficulty)}</td>
        <td>
          <div className="tags-cell">
            {recipe.tags && recipe.tags.length > 0 ? (
              recipe.tags.slice(0, 2).map((tag, i) => (
                <span key={i} className="tag-pill">{tag}</span>
              ))
            ) : (
              <span className="no-tags">-</span>
            )}
          </div>
        </td>
        <td className="actions-col">
          <button
            className="action-btn view-btn"
            onClick={(e) => {
              e.stopPropagation();
              onRecipeClick(recipe);
            }}
            title="View Recipe"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
              <circle cx="12" cy="12" r="3"/>
            </svg>
            View
          </button>
          {onRecipeDelete && (
            <button
              className="action-btn delete-btn"
              onClick={(e) => {
                e.stopPropagation();
                if (window.confirm(`Delete "${recipe.title}"?`)) {
                  onRecipeDelete(recipe.id);
                }
              }}
              title="Delete Recipe"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="3 6 5 6 21 6"/>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
              </svg>
              Delete
            </button>
          )}
        </td>
      </tr>
    );
  };

  // Sort recipes
  const sortedRecipes = React.useMemo(() => {
    const sorted = [...recipes];
    sorted.sort((a, b) => {
      let aVal = a[sortConfig.key];
      let bVal = b[sortConfig.key];

      // Handle different data types
      if (sortConfig.key === 'time_min' || sortConfig.key === 'servings') {
        aVal = parseInt(aVal) || 0;
        bVal = parseInt(bVal) || 0;
      } else if (typeof aVal === 'string') {
        aVal = aVal.toLowerCase();
        bVal = (bVal || '').toLowerCase();
      }

      if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });
    return sorted;
  }, [recipes, sortConfig]);

  const handleSort = (key) => {
    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  const toggleSelectRecipe = (recipeId) => {
    setSelectedRecipes(prev => {
      const newSet = new Set(prev);
      if (newSet.has(recipeId)) {
        newSet.delete(recipeId);
      } else {
        newSet.add(recipeId);
      }
      return newSet;
    });
  };

  const toggleSelectAll = () => {
    if (selectedRecipes.size === recipes.length) {
      setSelectedRecipes(new Set());
    } else {
      setSelectedRecipes(new Set(recipes.map(r => r.id)));
    }
  };

  const formatTime = (time) => {
    if (!time) return '-';
    return `${time} min`;
  };

  const formatDifficulty = (difficulty) => {
    if (!difficulty) return '-';
    return (
      <span className={`difficulty-badge difficulty-${difficulty.toLowerCase()}`}>
        {difficulty}
      </span>
    );
  };

  const SortIcon = ({ column }) => {
    if (sortConfig.key !== column) return <span className="sort-icon">⇅</span>;
    return <span className="sort-icon active">{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>;
  };

  return (
    <div className="recipe-table-view">
      <div className={`bulk-actions-bar ${selectedRecipes.size > 0 ? 'visible' : 'hidden'}`}>
        {selectedRecipes.size > 0 && (
          <>
            <span className="selected-count">{selectedRecipes.size} selected</span>
            <button 
              className="bulk-action-btn bulk-delete-btn" 
              onClick={() => {
                if (window.confirm(`Delete ${selectedRecipes.size} selected recipe(s)?`)) {
                  const recipeIds = Array.from(selectedRecipes);
                  recipeIds.forEach(id => onRecipeDelete?.(id));
                  setSelectedRecipes(new Set());
                }
              }}
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M10 11v6M14 11v6"/>
              </svg>
              Delete
            </button>
            <button 
              className="bulk-action-btn bulk-clear-btn" 
              onClick={() => setSelectedRecipes(new Set())}
            >
              Clear Selection
            </button>
          </>
        )}
      </div>

      <div className="table-container">
        <table className="recipe-table">
          <thead>
            <tr>
              <th className="checkbox-col">
                <input
                  type="checkbox"
                  checked={selectedRecipes.size === recipes.length && recipes.length > 0}
                  onChange={toggleSelectAll}
                />
              </th>
              <th className="sortable" onClick={() => handleSort('title')}>
                Recipe <SortIcon column="title" />
              </th>
              <th className="sortable" onClick={() => handleSort('category')}>
                Category <SortIcon column="category" />
              </th>
              <th className="sortable" onClick={() => handleSort('time_min')}>
                Time <SortIcon column="time_min" />
              </th>
              <th className="sortable" onClick={() => handleSort('servings')}>
                Servings <SortIcon column="servings" />
              </th>
              <th className="sortable" onClick={() => handleSort('difficulty')}>
                Difficulty <SortIcon column="difficulty" />
              </th>
              <th>Tags</th>
              <th className="actions-col">Actions</th>
            </tr>
          </thead>
          <tbody>
            {sortedRecipes.map(recipe => (
              <DraggableRow
                key={recipe.id}
                recipe={recipe}
                isSelected={selectedRecipes.has(recipe.id)}
              />
            ))}
          </tbody>
        </table>

        {recipes.length === 0 && (
          <div className="empty-table">
            <p>No recipes found</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default RecipeTableView;
