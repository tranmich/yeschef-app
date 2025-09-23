import React from 'react';
import { formatRecipeText } from '../utils/recipeFormatting';
import './RecipeDetailModal.css';

const RecipeDetailModal = ({ recipe, isOpen, onClose, onEdit }) => {
  if (!isOpen || !recipe) return null;

  // 🔧 Enhanced OCR text repair (from mobile app)
  const repairOCRText = (text) => {
    if (!text || typeof text !== 'string') return text;
    
    return text
      .replace(/extr a-virgin/g, 'extra-virgin')
      .replace(/ol ive oil/g, 'olive oil') 
      .replace(/unsal ted but ter/g, 'unsalted butter')
      .replace(/gr ated/g, 'grated')
      .replace(/sea son/g, 'season')
      .replace(/tem perature/g, 'temperature')
      .replace(/refrig erate/g, 'refrigerate');
  };

  // 📋 Enhanced Recipe Field Parsing (from mobile app)
  const formatRecipeField = (field) => {
    if (!field) return [];
    
    let text = field;
    if (typeof field === 'object') {
      try {
        text = typeof field === 'string' ? field : JSON.stringify(field);
      } catch (e) {
        console.warn('Failed to parse recipe field:', e);
        return ['Unable to parse recipe data'];
      }
    }

    // Clean up the text
    text = repairOCRText(text.toString());
    
    // Convert various formats to array
    if (text.includes('\n')) {
      return text.split('\n')
        .map(item => item.trim())
        .filter(item => item && item !== '\\n' && item !== 'null');
    } else if (text.includes('•')) {
      return text.split('•')
        .map(item => item.trim())
        .filter(item => item && item !== '\\n' && item !== 'null');
    } else if (text.includes('. ')) {
      return text.split('. ')
        .map(item => item.trim())
        .filter(item => item && item !== '\\n' && item !== 'null');
    } else {
      return [text];
    }
  };

  // Helper function to parse recipe fields that might be JSON strings
  function parseRecipeField(field) {
    if (!field) return field;
    
    // If it's already an array, return as is
    if (Array.isArray(field)) {
      return field;
    }
    
    // If it's a string that looks like JSON array, try to parse it
    if (typeof field === 'string') {
      // Check if it starts and ends with brackets (JSON array)
      if (field.trim().startsWith('[') && field.trim().endsWith(']')) {
        try {
          return JSON.parse(field);
        } catch (e) {
          console.warn('Failed to parse JSON field:', field);
          return field;
        }
      }
      // Regular string, return as is
      return field;
    }
    
    return field;
  }

  // Debug logging to see what we're receiving
  console.log('Recipe data:', recipe);
  console.log('Ingredients type:', typeof recipe.ingredients, recipe.ingredients);
  console.log('Instructions type:', typeof recipe.instructions, recipe.instructions);
  
  // Check if ingredients is an array of objects
  if (Array.isArray(recipe.ingredients) && recipe.ingredients.length > 0) {
    console.log('First ingredient:', recipe.ingredients[0]);
    console.log('Ingredient keys:', Object.keys(recipe.ingredients[0] || {}));
  }

  // Pre-process recipe data to handle JSON strings and format properly
  const processedRecipe = {
    ...recipe,
    ingredients: parseRecipeField(recipe.ingredients),
    instructions: parseRecipeField(recipe.instructions)
  };

  // 📋 Enhanced formatting using mobile app logic
  const ingredients = formatRecipeField(processedRecipe.ingredients);
  const instructions = formatRecipeField(processedRecipe.instructions);

  // Enhanced metadata formatting
  const formattedServings = recipe.servings ? `Serves ${recipe.servings}` : null;
  const formattedTime = [recipe.prep_time, recipe.cook_time].filter(Boolean).join(' + ') || null;
  const formattedDifficulty = recipe.difficulty;

  console.log('🍳 Processed ingredients:', ingredients);
  console.log('📝 Processed instructions:', instructions);

  return (
    <div className="recipe-detail-overlay" onClick={onClose}>
      <div className="recipe-detail-modal" onClick={(e) => e.stopPropagation()}>
        
        {/* Header Section - Left-aligned title */}
        <div className="recipe-header">
          <div className="recipe-title-section">
            <h1 className="recipe-title-large">{recipe.title || 'Untitled Recipe'}</h1>
          </div>
          <div className="header-buttons">
            {onEdit && (
              <button className="edit-button-header" onClick={() => onEdit(recipe)}>
                ✎ Edit
              </button>
            )}
            <button className="close-button" onClick={onClose}>✕</button>
          </div>
        </div>

        {/* Recipe Metadata Bar */}
        <div className="recipe-metadata-bar">
          {formattedServings && (
            <div className="metadata-item">
              <span className="metadata-icon">🍽️</span>
              <span className="metadata-value">{formattedServings}</span>
            </div>
          )}
          
          {formattedTime && (
            <div className="metadata-item">
              <span className="metadata-icon">⏱️</span>
              <span className="metadata-value">{formattedTime}</span>
            </div>
          )}
          
          {formattedDifficulty && (
            <div className="metadata-item">
              <span className="metadata-icon">📊</span>
              <span className="metadata-label">Level:</span>
              <span className="metadata-value">{formattedDifficulty}</span>
            </div>
          )}
          
          {recipe.rating && (
            <div className="metadata-item">
              <span className="metadata-icon">⭐</span>
              <span className="metadata-label">Rating:</span>
              <span className="metadata-value">{recipe.rating}/5</span>
            </div>
          )}
        </div>

        {/* Recipe Content - Single Column Layout */}
        <div className="recipe-content-flow">
          
          {/* Description */}
          {recipe.description && (
            <div className="recipe-section">
              <p className="recipe-description">{recipe.description}</p>
            </div>
          )}
          
          {/* Ingredients Section */}
          {ingredients && ingredients.length > 0 && (
            <div className="recipe-section">
              <h2 className="section-title">🛒 Ingredients ({ingredients.length})</h2>
              <div className="section-content">
                <ul className="ingredients-list">
                  {ingredients.map((ingredient, index) => (
                    <li key={index} className="ingredient-item">
                      {ingredient.startsWith('•') ? ingredient.substring(1).trim() : ingredient}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {/* Instructions Section */}
          {instructions && instructions.length > 0 && (
            <div className="recipe-section">
              <h2 className="section-title">👨‍🍳 Instructions ({instructions.length} steps)</h2>
              <div className="section-content">
                <ol className="instructions-list">
                  {instructions.map((instruction, index) => (
                    <li key={index} className="instruction-step">
                      <div className="step-content">
                        <span className="step-text">{instruction}</span>
                      </div>
                    </li>
                  ))}
                </ol>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="recipe-actions">
            {onEdit && (
              <button className="action-button edit-button" onClick={() => onEdit(recipe)}>
                ✎ Edit Recipe
              </button>
            )}
            <button className="action-button close-button-secondary" onClick={onClose}>
              Close
            </button>
          </div>
        </div>

      </div>
    </div>
  );
};

export default RecipeDetailModal;
