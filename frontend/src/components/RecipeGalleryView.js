import React from 'react';
import RecipeCard from './RecipeCard';
import './RecipeGalleryView.css';

const RecipeGalleryView = ({ recipes, onRecipeClick }) => {
  return (
    <div className="recipe-gallery-view">
      {recipes.length === 0 ? (
        <div className="empty-gallery">
          <h3>No recipes found</h3>
          <p>Try adjusting your filters or add a new recipe</p>
        </div>
      ) : (
        <div className="recipe-grid">
          {recipes.map(recipe => (
            <RecipeCard 
              key={recipe.id} 
              recipe={recipe} 
              onClick={() => onRecipeClick(recipe)}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default RecipeGalleryView;
