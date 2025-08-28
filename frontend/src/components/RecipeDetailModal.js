import React, { useState } from 'react';
import './RecipeDetailModal.css';

const RecipeDetailModal = ({ recipe, isOpen, onClose, onEdit }) => {
  const [activeTab, setActiveTab] = useState('overview');

  if (!isOpen || !recipe) return null;

  // Helper function to format ingredients
  const formatIngredients = (ingredients) => {
    if (!ingredients) return [];
    
    if (typeof ingredients === 'string') {
      return ingredients.split('\n').filter(ingredient => ingredient.trim());
    }
    
    if (Array.isArray(ingredients)) {
      return ingredients.map(ingredient => 
        typeof ingredient === 'string' ? ingredient : ingredient.name || ingredient.ingredient || String(ingredient)
      );
    }
    
    return [];
  };

  // Helper function to format instructions
  const formatInstructions = (instructions) => {
    if (!instructions) return [];
    
    if (typeof instructions === 'string') {
      return instructions.split('\n').filter(instruction => instruction.trim());
    }
    
    return Array.isArray(instructions) ? instructions : [];
  };

  // Helper function to format time
  const formatTime = (time) => {
    if (!time) return null;
    return typeof time === 'number' ? `${time} min` : time;
  };

  const ingredientList = formatIngredients(recipe.ingredients);
  const instructionList = formatInstructions(recipe.instructions);

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="recipe-detail-modal" onClick={(e) => e.stopPropagation()}>
        
        {/* Header */}
        <div className="recipe-header">
          <div className="recipe-title-section">
            <h1 className="recipe-title">{recipe.title || 'Untitled Recipe'}</h1>
            {recipe.description && (
              <p className="recipe-description">{recipe.description}</p>
            )}
          </div>
          
          <div className="recipe-header-actions">
            {onEdit && (
              <button className="edit-button" onClick={() => onEdit(recipe)}>
                ✏️ Edit
              </button>
            )}
            <button className="close-button" onClick={onClose}>
              ✕
            </button>
          </div>
        </div>

        {/* Recipe Info Bar */}
        <div className="recipe-info-bar">
          {recipe.servings && (
            <div className="info-item">
              <span className="info-icon">🍽️</span>
              <span className="info-label">Serves:</span>
              <span className="info-value">{recipe.servings}</span>
            </div>
          )}
          
          {(recipe.prep_time || recipe.hands_on_time) && (
            <div className="info-item">
              <span className="info-icon">⏱️</span>
              <span className="info-label">Prep:</span>
              <span className="info-value">{formatTime(recipe.prep_time || recipe.hands_on_time)}</span>
            </div>
          )}
          
          {(recipe.cook_time || recipe.total_time || recipe.time_min) && (
            <div className="info-item">
              <span className="info-icon">🔥</span>
              <span className="info-label">Cook:</span>
              <span className="info-value">{formatTime(recipe.cook_time || recipe.total_time || recipe.time_min)}</span>
            </div>
          )}
          
          {recipe.category && (
            <div className="info-item">
              <span className="info-icon">📂</span>
              <span className="info-label">Category:</span>
              <span className="info-value">{recipe.category}</span>
            </div>
          )}

          {recipe.confidence && (
            <div className="info-item">
              <span className="info-icon">🎯</span>
              <span className="info-label">Quality:</span>
              <span className="info-value">{Math.round(recipe.confidence * 100)}%</span>
            </div>
          )}
        </div>

        {/* Tab Navigation */}
        <div className="recipe-tabs">
          <button 
            className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            📖 Overview
          </button>
          <button 
            className={`tab-button ${activeTab === 'ingredients' ? 'active' : ''}`}
            onClick={() => setActiveTab('ingredients')}
          >
            🛒 Ingredients
          </button>
          <button 
            className={`tab-button ${activeTab === 'instructions' ? 'active' : ''}`}
            onClick={() => setActiveTab('instructions')}
          >
            👨‍🍳 Instructions
          </button>
          {recipe.source_url && (
            <button 
              className={`tab-button ${activeTab === 'source' ? 'active' : ''}`}
              onClick={() => setActiveTab('source')}
            >
              🔗 Source
            </button>
          )}
        </div>

        {/* Tab Content */}
        <div className="recipe-content">
          
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="tab-content overview-tab">
              <div className="overview-grid">
                
                {/* Ingredients Preview */}
                <div className="overview-section">
                  <h3>🛒 Ingredients ({ingredientList.length})</h3>
                  <div className="ingredients-preview">
                    {ingredientList.slice(0, 6).map((ingredient, index) => (
                      <div key={index} className="ingredient-preview">
                        • {ingredient}
                      </div>
                    ))}
                    {ingredientList.length > 6 && (
                      <div className="ingredient-preview more">
                        ... and {ingredientList.length - 6} more ingredients
                      </div>
                    )}
                  </div>
                </div>

                {/* Instructions Preview */}
                <div className="overview-section">
                  <h3>👨‍🍳 Instructions ({instructionList.length} steps)</h3>
                  <div className="instructions-preview">
                    {instructionList.slice(0, 3).map((instruction, index) => (
                      <div key={index} className="instruction-preview">
                        <span className="step-number">{index + 1}.</span>
                        <span className="step-text">
                          {instruction.length > 100 ? `${instruction.substring(0, 100)}...` : instruction}
                        </span>
                      </div>
                    ))}
                    {instructionList.length > 3 && (
                      <div className="instruction-preview more">
                        ... and {instructionList.length - 3} more steps
                      </div>
                    )}
                  </div>
                </div>

              </div>
            </div>
          )}

          {/* Ingredients Tab */}
          {activeTab === 'ingredients' && (
            <div className="tab-content ingredients-tab">
              <h3>🛒 Ingredients</h3>
              <div className="ingredients-list">
                {ingredientList.map((ingredient, index) => (
                  <div key={index} className="ingredient-item">
                    <span className="ingredient-bullet">•</span>
                    <span className="ingredient-text">{ingredient}</span>
                  </div>
                ))}
              </div>
              {ingredientList.length === 0 && (
                <p className="no-content">No ingredients listed for this recipe.</p>
              )}
            </div>
          )}

          {/* Instructions Tab */}
          {activeTab === 'instructions' && (
            <div className="tab-content instructions-tab">
              <h3>👨‍🍳 Instructions</h3>
              <div className="instructions-list">
                {instructionList.map((instruction, index) => (
                  <div key={index} className="instruction-item">
                    <div className="instruction-number">{index + 1}</div>
                    <div className="instruction-text">{instruction}</div>
                  </div>
                ))}
              </div>
              {instructionList.length === 0 && (
                <p className="no-content">No instructions provided for this recipe.</p>
              )}
            </div>
          )}

          {/* Source Tab */}
          {activeTab === 'source' && recipe.source_url && (
            <div className="tab-content source-tab">
              <h3>🔗 Recipe Source</h3>
              <div className="source-info">
                <div className="source-url">
                  <strong>Original URL:</strong>
                  <a href={recipe.source_url} target="_blank" rel="noopener noreferrer" className="source-link">
                    {recipe.source_url}
                  </a>
                </div>
                
                {recipe.author && (
                  <div className="source-author">
                    <strong>Author:</strong> {recipe.author}
                  </div>
                )}
                
                {recipe.extraction_method && (
                  <div className="source-method">
                    <strong>Extraction Method:</strong> {recipe.extraction_method}
                  </div>
                )}
                
                {recipe.imported_at && (
                  <div className="source-imported">
                    <strong>Imported:</strong> {new Date(recipe.imported_at).toLocaleDateString()}
                  </div>
                )}
              </div>
            </div>
          )}

        </div>

      </div>
    </div>
  );
};

export default RecipeDetailModal;
