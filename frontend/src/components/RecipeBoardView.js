import React, { useState } from 'react';
import './RecipeBoardView.css';

const RecipeBoardView = ({ recipes, onRecipeClick, groupBy = 'difficulty' }) => {
  const [draggedRecipe, setDraggedRecipe] = useState(null);

  // Group recipes by selected property
  const groupRecipes = () => {
    const groups = {};

    if (groupBy === 'difficulty') {
      groups['easy'] = { title: 'Easy', icon: '🟢', recipes: [] };
      groups['medium'] = { title: 'Medium', icon: '🟡', recipes: [] };
      groups['hard'] = { title: 'Hard', icon: '🔴', recipes: [] };
      groups['unknown'] = { title: 'Unknown', icon: '⚪', recipes: [] };

      recipes.forEach(recipe => {
        const difficulty = (recipe.difficulty || 'unknown').toLowerCase();
        if (groups[difficulty]) {
          groups[difficulty].recipes.push(recipe);
        } else {
          groups['unknown'].recipes.push(recipe);
        }
      });
    } else if (groupBy === 'meal_role' || groupBy === 'category') {
      groups['breakfast'] = { title: 'Breakfast', icon: '🌅', recipes: [] };
      groups['lunch'] = { title: 'Lunch', icon: '🌤️', recipes: [] };
      groups['dinner'] = { title: 'Dinner', icon: '🌙', recipes: [] };
      groups['snack'] = { title: 'Snack', icon: '🍿', recipes: [] };
      groups['dessert'] = { title: 'Dessert', icon: '🍰', recipes: [] };
      groups['other'] = { title: 'Other', icon: '🍽️', recipes: [] };

      recipes.forEach(recipe => {
        const category = (recipe.meal_role || recipe.category || 'other').toLowerCase();
        if (groups[category]) {
          groups[category].recipes.push(recipe);
        } else {
          groups['other'].recipes.push(recipe);
        }
      });
    } else if (groupBy === 'time') {
      groups['quick'] = { title: 'Quick (<30min)', icon: '⚡', recipes: [] };
      groups['medium'] = { title: 'Medium (30-60min)', icon: '⏱️', recipes: [] };
      groups['long'] = { title: 'Long (>60min)', icon: '🕐', recipes: [] };
      groups['unknown'] = { title: 'Unknown', icon: '❓', recipes: [] };

      recipes.forEach(recipe => {
        const time = parseInt(recipe.time_min || recipe.cooking_time || recipe.prep_time || 0);
        if (time === 0) {
          groups['unknown'].recipes.push(recipe);
        } else if (time < 30) {
          groups['quick'].recipes.push(recipe);
        } else if (time <= 60) {
          groups['medium'].recipes.push(recipe);
        } else {
          groups['long'].recipes.push(recipe);
        }
      });
    }

    return groups;
  };

  const groupedRecipes = groupRecipes();

  const handleDragStart = (e, recipe) => {
    setDraggedRecipe(recipe);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = (e, targetGroup) => {
    e.preventDefault();
    if (draggedRecipe) {
      console.log(`Moving ${draggedRecipe.title} to ${targetGroup}`);
      // TODO: Implement recipe property update
      setDraggedRecipe(null);
    }
  };

  const formatTime = (recipe) => {
    const time = recipe.time_min || recipe.cooking_time || recipe.prep_time;
    return time ? `${time} min` : 'No time';
  };

  return (
    <div className="recipe-board-view">
      <div className="board-columns">
        {Object.entries(groupedRecipes).map(([groupKey, group]) => (
          <div
            key={groupKey}
            className="board-column"
            onDragOver={handleDragOver}
            onDrop={(e) => handleDrop(e, groupKey)}
          >
            <div className="column-header">
              <span className="column-icon">{group.icon}</span>
              <span className="column-title">{group.title}</span>
              <span className="column-count">{group.recipes.length}</span>
            </div>

            <div className="column-cards">
              {group.recipes.length === 0 ? (
                <div className="empty-column">
                  <p>No recipes</p>
                </div>
              ) : (
                group.recipes.map(recipe => (
                  <div
                    key={recipe.id}
                    className="recipe-board-card"
                    draggable
                    onDragStart={(e) => handleDragStart(e, recipe)}
                    onClick={() => onRecipeClick(recipe)}
                  >
                    <div className="card-header">
                      <h4 className="card-title">{recipe.title}</h4>
                    </div>

                    <div className="card-meta">
                      {recipe.servings && (
                        <span className="meta-item">
                          👥 {recipe.servings}
                        </span>
                      )}
                      <span className="meta-item">
                        ⏱️ {formatTime(recipe)}
                      </span>
                    </div>

                    {recipe.description && (
                      <p className="card-description">
                        {recipe.description.length > 80
                          ? `${recipe.description.substring(0, 80)}...`
                          : recipe.description
                        }
                      </p>
                    )}

                    {recipe.tags && recipe.tags.length > 0 && (
                      <div className="card-tags">
                        {recipe.tags.slice(0, 2).map((tag, i) => (
                          <span key={i} className="card-tag">#{tag}</span>
                        ))}
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>

            <button className="add-recipe-btn">
              + Add Recipe
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RecipeBoardView;
