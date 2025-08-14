import React from 'react';
import { useNavigate } from 'react-router-dom';
import './RecipeCard.css';

const RecipeCard = ({ recipe }) => {
  const navigate = useNavigate();

  const parseTime = (timeStr) => {
    if (!timeStr) return 'Quick';
    if (timeStr.includes('PT')) {
      const minutes = timeStr.replace('PT', '').replace('M', '').replace('H', 'h ');
      return minutes.includes('h') ? minutes + 'm' : minutes + ' min';
    }
    return timeStr;
  };

  const handleClick = () => {
    navigate(`/recipe/${recipe.id}`);
  };

  return (
    <div className="recipe-card" onClick={handleClick}>
      <div className="recipe-card-content">
        <h3 className="recipe-title">{recipe.name}</h3>
        
        {recipe.description && (
          <p className="recipe-description">
            {recipe.description.length > 100 
              ? `${recipe.description.substring(0, 100)}...` 
              : recipe.description
            }
          </p>
        )}

        <div className="recipe-meta">
          <span className="time">
            ⏱️ {parseTime(recipe.total_time)}
          </span>
          {recipe.servings && (
            <span className="servings">
              👥 {recipe.servings} servings
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
