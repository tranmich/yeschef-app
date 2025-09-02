import React from 'react';
import { useNavigate } from 'react-router-dom';
import { formatRecipeText } from '../utils/recipeFormatting';
import './RecipeCard.css';

const RecipeCard = ({ recipe }) => {
  const navigate = useNavigate();

  // Use consistent formatting across all recipe displays
  const formattedIngredients = formatRecipeText.formatIngredients(recipe.ingredients);
  const formattedInstructions = formatRecipeText.formatInstructions(recipe.instructions);
  const formattedTime = formatRecipeText.formatTime(recipe.cooking_time || recipe.time_min || recipe.prep_time);
  const formattedServings = formatRecipeText.formatServings(recipe.servings);
  const formattedDifficulty = formatRecipeText.formatDifficulty(recipe.difficulty);
  const formattedCuisine = formatRecipeText.formatCuisineType(recipe.cuisine_type);

  const handleClick = () => {
    navigate(`/recipe/${recipe.id}`);
  };

  return (
    <div className="recipe-card" onClick={handleClick}>
      <div className="recipe-card-content">
        <h3 className="recipe-title">{recipe.title || recipe.name}</h3>
        
        {recipe.description && (
          <p className="recipe-description">
            {recipe.description.length > 100 
              ? `${recipe.description.substring(0, 100)}...` 
              : recipe.description
            }
          </p>
        )}

        <div className="recipe-meta">
          {formattedTime && (
            <span className="time">
              ⏱️ {formattedTime}
            </span>
          )}
          {formattedServings && (
            <span className="servings">
              👥 {formattedServings}
            </span>
          )}
          {formattedDifficulty && (
            <span className="difficulty">
              📊 {formattedDifficulty}
            </span>
          )}
          {formattedCuisine && (
            <span className="cuisine">
              🍽️ {formattedCuisine}
            </span>
          )}
        </div>

        {recipe.categories && recipe.categories.length > 0 && (
          <div className="recipe-categories">
            {recipe.categories.slice(0, 2).map((category, index) => (
              <span key={index} className="category-tag">
                {category.replace('-', ' ')}
              </span>
            ))}
          </div>
        )}

        <div className="recipe-card-footer">
          <button className="view-recipe-btn">
            View Recipe 👨‍🍳
          </button>
        </div>
      </div>
    </div>
  );
};

export default RecipeCard;
