/**
 * Mini Recipe Card Component
 * ===========================
 * Compact recipe card for display inside meal plan boxes
 * 
 * Features:
 * - Thumbnail image with fallback
 * - Recipe title
 * - Remove button (X)
 * - Hover effects
 * - Click to view full recipe
 * 
 * Author: GitHub Copilot
 * Date: November 5, 2025
 */

import React from 'react';
import './MiniRecipeCard.css';

const MiniRecipeCard = ({ recipe, onRemove, onClick }) => {
  const recipeName = recipe.name || recipe.title || 'Unnamed Recipe';
  const recipeImage = recipe.image_url || recipe.image || recipe.thumbnail;
  const recipeId = recipe.id || recipe.recipe_id;

  const handleRemoveClick = (e) => {
    e.stopPropagation(); // Prevent card click event
    onRemove?.(recipe);
  };

  const handleCardClick = (e) => {
    e.stopPropagation(); // Prevent parent drag
    onClick?.(recipe);
  };

  return (
    <div className="mini-recipe-card" onClick={handleCardClick} title={recipeName}>
      {/* Remove button */}
      <button 
        className="mini-recipe-remove no-drag" 
        onClick={handleRemoveClick}
        title="Remove from group"
      >
        ×
      </button>

      {/* Recipe thumbnail */}
      <div className="mini-recipe-thumbnail">
        {recipeImage ? (
          <img 
            src={recipeImage} 
            alt={recipeName}
            onError={(e) => {
              // Fallback to placeholder on image error
              e.target.style.display = 'none';
              e.target.nextElementSibling.style.display = 'flex';
            }}
          />
        ) : null}
        <div className="mini-recipe-placeholder" style={{ display: recipeImage ? 'none' : 'flex' }}>
          🍳
        </div>
      </div>

      {/* Recipe title */}
      <div className="mini-recipe-title">
        {recipeName}
      </div>
    </div>
  );
};

export default MiniRecipeCard;
