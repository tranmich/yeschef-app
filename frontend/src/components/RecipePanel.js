import React, { useState, useRef, useEffect } from 'react';
import { formatRecipeText } from '../utils/recipeFormatting';
import './RecipePanel.css';

const RecipePanel = ({ recipe, isOpen, onClose, onEdit }) => {
  // Main mode state: 'view' or 'edit'
  const [mode, setMode] = useState('view');
  
  // Edited recipe data (only used in edit mode)
  const [editedRecipe, setEditedRecipe] = useState(null);
  
  // Full-screen mode state
  const [isFullScreen, setIsFullScreen] = useState(false);
  
  // Refs for auto-focus
  const ingredientsRef = useRef(null);
  const instructionsRef = useRef(null);

  // Reset to view mode when recipe changes
  useEffect(() => {
    if (recipe) {
      setMode('view');
      setEditedRecipe(null);
    }
  }, [recipe?.id]);

  // 🔧 Enhanced OCR text repair
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

  // 📋 Enhanced Recipe Field Parsing - converts to display array
  const formatRecipeField = (field) => {
    if (!field) return [];
    
    // Handle array of objects (from backend)
    if (Array.isArray(field)) {
      return field
        .filter(item => item)
        .map(item => {
          if (typeof item === 'object') {
            return item.ingredient || item.text || item.name || String(item);
          }
          return String(item);
        })
        .map(text => repairOCRText(text.trim()))
        .filter(text => text && text !== '[object Object]');
    }

    // Handle JSON string
    if (typeof field === 'string' && field.trim().startsWith('[')) {
      try {
        const parsed = JSON.parse(field);
        return formatRecipeField(parsed); // Recursive call
      } catch (e) {
        // Continue to text parsing
      }
    }

    // Handle plain text
    let text = repairOCRText(field.toString());
    
    if (text.includes('\n')) {
      return text.split('\n')
        .map(item => item.trim())
        .filter(item => item && item !== '\\n' && item !== 'null');
    } else if (text.includes('•')) {
      return text.split('•')
        .map(item => item.trim())
        .filter(item => item);
    } else {
      return [text];
    }
  };

  // Convert array back to editable text format
  const arrayToEditableText = (arr) => {
    if (!arr || !Array.isArray(arr)) return '';
    return arr.join('\n');
  };

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        if (isFullScreen) {
          setIsFullScreen(false);
        } else if (mode === 'edit') {
          handleCancelEdit();
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isFullScreen, mode]);

  // Full-screen mode handlers
  const toggleFullScreen = () => {
    setIsFullScreen(!isFullScreen);
  };

  // Early return AFTER all hooks
  if (!isOpen || !recipe) return null;

  // Process recipe data for display
  const ingredients = formatRecipeField(recipe.ingredients);
  const instructions = formatRecipeField(recipe.instructions);

  // Format metadata
  const formattedServings = recipe.servings ? `${recipe.servings} servings` : null;
  const formattedTime = recipe.cookTime || recipe.totalTime || recipe.prep_time ? 
    `${recipe.cookTime || recipe.totalTime || recipe.prep_time} min` : null;
  const formattedDifficulty = recipe.difficulty ? 
    recipe.difficulty.charAt(0).toUpperCase() + recipe.difficulty.slice(1) : null;

  // ==================== EDIT MODE HANDLERS ====================
  
  const handleStartEdit = () => {
    // Initialize edited recipe with current data
    setEditedRecipe({
      ...recipe,
      ingredients: arrayToEditableText(ingredients),
      instructions: arrayToEditableText(instructions)
    });
    setMode('edit');
    
    // Auto-focus first field after state update
    setTimeout(() => {
      if (ingredientsRef.current) {
        ingredientsRef.current.focus();
      }
    }, 100);
  };

  const handleSaveEdit = async () => {
    if (!editedRecipe) return;
    
    console.log('💾 Saving recipe edits:', editedRecipe);
    
    // Convert text back to array format for storage
    const updatedRecipe = {
      ...editedRecipe,
      ingredients: editedRecipe.ingredients.split('\n').filter(line => line.trim()),
      instructions: editedRecipe.instructions.split('\n').filter(line => line.trim())
    };
    
    // Call parent handler to save to backend
    if (onEdit) {
      await onEdit(updatedRecipe);
    }
    
    // Return to view mode
    setMode('view');
    setEditedRecipe(null);
  };

  const handleCancelEdit = () => {
    console.log('❌ Canceling recipe edits');
    setMode('view');
    setEditedRecipe(null);
  };

  const updateEditedField = (fieldName, value) => {
    setEditedRecipe(prev => ({
      ...prev,
      [fieldName]: value
    }));
  };

  // Auto-resize textarea
  const autoResize = (textarea) => {
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = textarea.scrollHeight + 'px';
    }
  };

  // ==================== RENDER VIEW MODE ====================
  
  if (mode === 'view') {
    return (
      <>
        {/* Background overlay */}
        {!isFullScreen && (
          <div className="recipe-panel-backdrop" onClick={onClose} />
        )}
        
        {/* Recipe Panel - View Mode */}
        <div className={`recipe-panel recipe-panel-view ${isFullScreen ? 'recipe-panel-fullscreen' : ''}`}>
          
          {/* Header */}
          <div className="recipe-panel-header">
            <div className="header-left-actions">
              <button 
                className="expand-panel-btn" 
                onClick={toggleFullScreen}
                title={isFullScreen ? "Exit full-screen (Esc)" : "Expand to full-screen"}
              >
                {isFullScreen ? '→' : '←'}
              </button>
            </div>
            <div className="recipe-title-section">
              <h1 className="recipe-title-large">{recipe.title || 'Untitled Recipe'}</h1>
            </div>
            <div className="header-actions">
              <button 
                className="edit-recipe-btn" 
                onClick={handleStartEdit}
                title="Edit this recipe"
              >
                ✏️ Edit
              </button>
              <button className="close-panel-btn" onClick={onClose}>✕</button>
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

          {/* Recipe Content */}
          <div className={`recipe-content-flow ${isFullScreen ? 'recipe-content-fullscreen' : ''}`}>
            
            {/* Description */}
            {recipe.description && (
              <div className="recipe-block description-block">
                <div className="block-content">
                  <p className="recipe-description">{recipe.description}</p>
                </div>
              </div>
            )}
            
            {/* Ingredients */}
            <div className="recipe-block ingredients-block">
              <h2 className="block-title">
                🛒 Ingredients {ingredients.length > 0 && `(${ingredients.length})`}
              </h2>
              <div className="block-content">
                {ingredients.length > 0 ? (
                  <ul className="ingredients-list">
                    {ingredients.map((ing, idx) => (
                      <li key={idx} className="ingredient-item">
                        {ing}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="empty-state">No ingredients listed</p>
                )}
              </div>
            </div>

            {/* Instructions */}
            <div className="recipe-block instructions-block">
              <h2 className="block-title">
                👨‍🍳 Instructions {instructions.length > 0 && `(${instructions.length} steps)`}
              </h2>
              <div className="block-content">
                {instructions.length > 0 ? (
                  <ol className="instructions-list">
                    {instructions.map((inst, idx) => (
                      <li key={idx} className="instruction-step">
                        {inst}
                      </li>
                    ))}
                  </ol>
                ) : (
                  <p className="empty-state">No instructions provided</p>
                )}
              </div>
            </div>

            {/* Source */}
            {recipe.source && (
              <div className="recipe-block source-block">
                <p className="recipe-source">
                  <span className="source-label">Source:</span> {recipe.source}
                </p>
              </div>
            )}

          </div>
        </div>
      </>
    );
  }

  // ==================== RENDER EDIT MODE ====================
  
  return (
    <>
      {/* Background overlay - not closeable in edit mode */}
      <div className="recipe-panel-backdrop recipe-panel-backdrop-editing" />
      
      {/* Recipe Panel - Edit Mode */}
      <div className={`recipe-panel recipe-panel-edit ${isFullScreen ? 'recipe-panel-fullscreen' : ''}`}>
        
        {/* Header with Save/Cancel */}
        <div className="recipe-panel-header recipe-panel-header-editing">
          <div className="header-left-actions">
            <span className="editing-indicator">✏️ Editing Recipe</span>
          </div>
          <div className="header-actions">
            <button 
              className="cancel-edit-btn" 
              onClick={handleCancelEdit}
              title="Cancel editing (Esc)"
            >
              Cancel
            </button>
            <button 
              className="save-edit-btn" 
              onClick={handleSaveEdit}
              title="Save changes"
            >
              💾 Save
            </button>
          </div>
        </div>

        {/* Edit Form */}
        <div className={`recipe-content-flow ${isFullScreen ? 'recipe-content-fullscreen' : ''}`}>
          
          {/* Title Field */}
          <div className="recipe-block edit-field-block">
            <label className="edit-field-label">Recipe Title</label>
            <input
              type="text"
              className="edit-input edit-title-input"
              value={editedRecipe?.title || ''}
              onChange={(e) => updateEditedField('title', e.target.value)}
              placeholder="Enter recipe title..."
            />
          </div>

          {/* Description Field */}
          <div className="recipe-block edit-field-block">
            <label className="edit-field-label">Description</label>
            <textarea
              className="edit-textarea edit-description-textarea"
              value={editedRecipe?.description || ''}
              onChange={(e) => {
                updateEditedField('description', e.target.value);
                autoResize(e.target);
              }}
              placeholder="Add a description for this recipe..."
              rows={3}
            />
          </div>

          {/* Metadata Fields */}
          <div className="recipe-block edit-metadata-block">
            <div className="edit-metadata-grid">
              <div className="edit-field-compact">
                <label className="edit-field-label-compact">Servings</label>
                <input
                  type="text"
                  className="edit-input-compact"
                  value={editedRecipe?.servings || ''}
                  onChange={(e) => updateEditedField('servings', e.target.value)}
                  placeholder="e.g., 4"
                />
              </div>
              <div className="edit-field-compact">
                <label className="edit-field-label-compact">Prep Time (min)</label>
                <input
                  type="text"
                  className="edit-input-compact"
                  value={editedRecipe?.prep_time || editedRecipe?.cookTime || ''}
                  onChange={(e) => updateEditedField('prep_time', e.target.value)}
                  placeholder="e.g., 30"
                />
              </div>
              <div className="edit-field-compact">
                <label className="edit-field-label-compact">Difficulty</label>
                <select
                  className="edit-input-compact"
                  value={editedRecipe?.difficulty || 'medium'}
                  onChange={(e) => updateEditedField('difficulty', e.target.value)}
                >
                  <option value="easy">Easy</option>
                  <option value="medium">Medium</option>
                  <option value="hard">Hard</option>
                </select>
              </div>
            </div>
          </div>

          {/* Ingredients Field */}
          <div className="recipe-block edit-field-block">
            <label className="edit-field-label">
              🛒 Ingredients
              <span className="edit-field-hint">One ingredient per line</span>
            </label>
            <textarea
              ref={ingredientsRef}
              className="edit-textarea edit-ingredients-textarea"
              value={editedRecipe?.ingredients || ''}
              onChange={(e) => {
                updateEditedField('ingredients', e.target.value);
                autoResize(e.target);
              }}
              placeholder="2 cups all-purpose flour&#10;1 tsp baking powder&#10;1/2 cup sugar&#10;..."
              rows={8}
            />
          </div>

          {/* Instructions Field */}
          <div className="recipe-block edit-field-block">
            <label className="edit-field-label">
              👨‍🍳 Instructions
              <span className="edit-field-hint">One step per line</span>
            </label>
            <textarea
              ref={instructionsRef}
              className="edit-textarea edit-instructions-textarea"
              value={editedRecipe?.instructions || ''}
              onChange={(e) => {
                updateEditedField('instructions', e.target.value);
                autoResize(e.target);
              }}
              placeholder="Preheat oven to 350°F&#10;Mix dry ingredients in a bowl&#10;Add wet ingredients and stir&#10;..."
              rows={10}
            />
          </div>

          {/* Source Field */}
          <div className="recipe-block edit-field-block">
            <label className="edit-field-label">Source (Optional)</label>
            <input
              type="text"
              className="edit-input"
              value={editedRecipe?.source || ''}
              onChange={(e) => updateEditedField('source', e.target.value)}
              placeholder="e.g., Grandma's cookbook, NYT Cooking..."
            />
          </div>

        </div>
      </div>
    </>
  );
};

export default RecipePanel;