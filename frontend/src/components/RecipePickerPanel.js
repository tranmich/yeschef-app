/**
 * Recipe Picker Panel
 * ===================
 * Sliding panel (like Inkscape widgets) that shows user's recipe library
 * Click a recipe to add it to the whiteboard canvas
 * 
 * Features:
 * - Search/filter recipes
 * - Category filtering
 * - Compact recipe cards
 * - Click to add to canvas
 */

import React, { useState, useEffect } from 'react';
import { apiCall } from '../utils/api';
import './RecipePickerPanel.css';

const RecipePickerPanel = ({ isOpen, onClose, onAddRecipe }) => {
  const [recipes, setRecipes] = useState([]);
  const [filteredRecipes, setFilteredRecipes] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [loading, setLoading] = useState(false);

  // Load recipes when panel opens
  useEffect(() => {
    if (isOpen && recipes.length === 0) {
      loadRecipes();
    }
  }, [isOpen]);

  // Filter recipes when search or category changes
  useEffect(() => {
    filterRecipes();
  }, [searchQuery, selectedCategory, recipes]);

  const loadRecipes = async () => {
    try {
      setLoading(true);
      const data = await apiCall('/api/user/recipes?category=all');
      const recipeList = data.data || data.recipes || [];
      
      // Sort alphabetically
      const sorted = [...recipeList].sort((a, b) => {
        const nameA = (a.title || a.name || '').toLowerCase();
        const nameB = (b.title || b.name || '').toLowerCase();
        return nameA.localeCompare(nameB);
      });
      
      setRecipes(sorted);
      console.log('📚 Loaded', sorted.length, 'recipes for picker');
    } catch (err) {
      console.error('Error loading recipes:', err);
    } finally {
      setLoading(false);
    }
  };

  const filterRecipes = () => {
    let filtered = [...recipes];

    // Filter by category
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(r => r.category === selectedCategory);
    }

    // Filter by search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(r => {
        const name = (r.title || r.name || '').toLowerCase();
        const ingredients = (r.ingredients || '').toLowerCase();
        return name.includes(query) || ingredients.includes(query);
      });
    }

    setFilteredRecipes(filtered);
  };

  const handleRecipeClick = (recipe) => {
    console.log('➕ Adding recipe to canvas:', recipe.title || recipe.name);
    onAddRecipe(recipe);
  };

  // Get unique categories
  const categories = ['all', ...new Set(recipes.map(r => r.category).filter(Boolean))];

  if (!isOpen) return null;

  return (
    <div className={`recipe-picker-panel ${isOpen ? 'open' : ''}`}>
      {/* Header */}
      <div className="recipe-picker-header">
        <h3>Add Recipes</h3>
        <button className="close-button" onClick={onClose}>✕</button>
      </div>

        {/* Search */}
        <div className="recipe-picker-search">
          <input
            type="text"
            placeholder="Search recipes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        {/* Category Filter */}
        <div className="recipe-picker-categories">
          {categories.map(cat => (
            <button
              key={cat}
              className={`category-chip ${selectedCategory === cat ? 'active' : ''}`}
              onClick={() => setSelectedCategory(cat)}
            >
              {cat === 'all' ? 'All' : cat.charAt(0).toUpperCase() + cat.slice(1)}
            </button>
          ))}
        </div>

        {/* Recipe List */}
        <div className="recipe-picker-list">
          {loading ? (
            <div className="picker-loading">
              <div className="spinner"></div>
              <p>Loading recipes...</p>
            </div>
          ) : filteredRecipes.length === 0 ? (
            <div className="picker-empty">
              <p>No recipes found</p>
              <small>Try adjusting your filters</small>
            </div>
          ) : (
            filteredRecipes.map(recipe => (
              <div
                key={recipe.id}
                className="picker-recipe-item"
                onClick={() => handleRecipeClick(recipe)}
              >
                {/* Mini thumbnail */}
                <div className="picker-recipe-thumb">
                  {recipe.image_url ? (
                    <img
                      src={recipe.image_url.startsWith('/api')
                        ? `${process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000'}${recipe.image_url}`
                        : recipe.image_url
                      }
                      alt={recipe.title || recipe.name}
                      onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.nextSibling.style.display = 'flex';
                      }}
                    />
                  ) : null}
                  <div 
                    className="picker-recipe-placeholder"
                    style={{ display: recipe.image_url ? 'none' : 'flex' }}
                  >
                    ◈
                  </div>
                </div>

                {/* Recipe info */}
                <div className="picker-recipe-info">
                  <h4>{recipe.title || recipe.name || 'Untitled Recipe'}</h4>
                  <div className="picker-recipe-meta">
                    {recipe.category && (
                      <span className="picker-category-badge">{recipe.category}</span>
                    )}
                    {recipe.prep_time && (
                      <span className="picker-time">⏱ {recipe.prep_time}m</span>
                    )}
                  </div>
                </div>

                {/* Add icon */}
                <div className="picker-add-icon">+</div>
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="recipe-picker-footer">
          <small>{filteredRecipes.length} recipe{filteredRecipes.length !== 1 ? 's' : ''}</small>
        </div>
      </div>
  );
};

export default RecipePickerPanel;
