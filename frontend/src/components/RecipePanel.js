import React, { useState, useRef, useEffect } from 'react';
import { formatRecipeText } from '../utils/recipeFormatting';
import './RecipePanel.css';

const RecipePanel = ({ recipe, isOpen, onClose, onEdit }) => {
  // Inline editing states for different fields
  const [editingField, setEditingField] = useState(null);
  const [tempValues, setTempValues] = useState({});
  
  // Full-screen mode state
  const [isFullScreen, setIsFullScreen] = useState(false);
  
  // Refs for auto-focus
  const inputRefs = useRef({});

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

  // Handle keyboard shortcuts (moved before early return)
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isFullScreen) {
        setIsFullScreen(false);
      } else if (e.key === 'f' && e.ctrlKey) { // Ctrl+F for full-screen
        e.preventDefault();
        toggleFullScreen();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isFullScreen]);

  // Full-screen mode handlers
  const toggleFullScreen = () => {
    setIsFullScreen(!isFullScreen);
  };

  // Early return AFTER all hooks are declared
  if (!isOpen || !recipe) return null;

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
  console.log('🎨 RecipePanel - Recipe data:', recipe);
  console.log('🎨 RecipePanel - Ingredients type:', typeof recipe.ingredients, recipe.ingredients);
  console.log('🎨 RecipePanel - Instructions type:', typeof recipe.instructions, recipe.instructions);
  
  // Check if ingredients is an array of objects
  if (Array.isArray(recipe.ingredients) && recipe.ingredients.length > 0) {
    console.log('🎨 RecipePanel - First ingredient:', recipe.ingredients[0]);
    console.log('🎨 RecipePanel - Ingredient keys:', Object.keys(recipe.ingredients[0] || {}));
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

  console.log('🎨 RecipePanel - Processed ingredients:', ingredients);
  console.log('🎨 RecipePanel - Processed instructions:', instructions);

  // Helper function to clean text for editing (remove formatting characters)
  const cleanTextForEditing = (text) => {
    if (!text) return '';
    
    // If it's formatted ingredients or instructions, clean them up
    let cleaned = text;
    
    // Handle JSON stringified arrays first
    if (typeof cleaned === 'string' && cleaned.startsWith('[') && cleaned.endsWith(']')) {
      try {
        const parsed = JSON.parse(cleaned);
        if (Array.isArray(parsed)) {
          // Extract text from array of objects or strings
          cleaned = parsed.map(item => {
            if (typeof item === 'object' && item.ingredient) {
              return item.ingredient;
            } else if (typeof item === 'object' && item.text) {
              return item.text;
            } else if (typeof item === 'string') {
              return item;
            }
            return String(item);
          }).join('\n');
        }
      } catch (e) {
        // If parsing fails, continue with string processing
      }
    }
    
    // Convert to string if not already
    cleaned = String(cleaned);
    
    // Remove bullet points and numbers from formatted text
    cleaned = cleaned.replace(/^[•\-\*]\s*/gm, ''); // Remove bullet points
    cleaned = cleaned.replace(/^\d+\.\s*/gm, ''); // Remove numbered lists
    cleaned = cleaned.replace(/\n\s*\n/g, '\n'); // Remove extra line breaks
    cleaned = cleaned.trim();
    
    return cleaned;
  };

  // Helper function to convert back to display format
  const formatTextForDisplay = (text, fieldName) => {
    if (!text) return '';
    
    // For ingredients and instructions, apply basic formatting
    if (fieldName === 'ingredients') {
      return text.split('\n').filter(line => line.trim()).map(line => 
        line.trim().startsWith('•') ? line.trim() : `• ${line.trim()}`
      ).join('\n');
    } else if (fieldName === 'instructions') {
      return text.split('\n').filter(line => line.trim()).map((line, index) => 
        line.trim().match(/^\d+\./) ? line.trim() : `${index + 1}. ${line.trim()}`
      ).join('\n');
    }
    
    return text;
  };

  // Inline editing handlers
  const startEdit = (fieldName, currentValue) => {
    console.log(`✏️ Starting edit for ${fieldName}:`, currentValue);
    console.log(`✏️ Value type:`, typeof currentValue);
    console.log(`✏️ Is ingredients/instructions:`, fieldName === 'ingredients' || fieldName === 'instructions');
    
    // Clean the text for a better editing experience
    const cleanedValue = fieldName === 'ingredients' || fieldName === 'instructions' 
      ? cleanTextForEditing(currentValue) 
      : currentValue;
    
    console.log(`✏️ Cleaned value:`, cleanedValue);
    
    setEditingField(fieldName);
    setTempValues(prev => ({
      ...prev,
      [fieldName]: cleanedValue || ''
    }));
    
    // Auto-focus the input after state update
    setTimeout(() => {
      const input = inputRefs.current[fieldName];
      if (input) {
        input.focus();
        input.select();
      }
    }, 0);
  };

  const saveEdit = (fieldName) => {
    const newValue = tempValues[fieldName];
    console.log(`💾 Saving edit for ${fieldName}:`, newValue);
    
    if (newValue && newValue.trim() !== '') {
      // Apply formatting for specific fields before saving
      const formattedValue = formatTextForDisplay(newValue.trim(), fieldName);
      
      // Create updated recipe object
      const updatedRecipe = {
        ...recipe,
        [fieldName]: formattedValue
      };
      
      console.log('📝 Updated recipe:', updatedRecipe);
      
      // Call the parent edit handler
      if (onEdit) {
        onEdit(updatedRecipe);
      }
    }
    
    // Clear editing state
    setEditingField(null);
    setTempValues(prev => {
      const newState = { ...prev };
      delete newState[fieldName];
      return newState;
    });
  };

  const cancelEdit = (fieldName) => {
    console.log(`❌ Canceling edit for ${fieldName}`);
    setEditingField(null);
    setTempValues(prev => {
      const newState = { ...prev };
      delete newState[fieldName];
      return newState;
    });
  };

  const handleKeyDown = (e, fieldName) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      saveEdit(fieldName);
    } else if (e.key === 'Escape') {
      e.preventDefault();
      cancelEdit(fieldName);
    }
  };

  // Editable text component
  const EditableText = ({ 
    fieldName, 
    value, 
    placeholder = "Click to edit", 
    className = "", 
    multiline = false,
    displayValue = null 
  }) => {
    const isEditing = editingField === fieldName;
    const displayText = displayValue || value || placeholder;
    
    // Auto-resize function for textareas
    const autoResize = (textarea) => {
      if (textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
      }
    };
    
    if (isEditing) {
      const InputComponent = multiline ? 'textarea' : 'input';
      return (
        <InputComponent
          ref={el => {
            inputRefs.current[fieldName] = el;
            if (multiline && el) {
              // Auto-resize on mount
              setTimeout(() => autoResize(el), 0);
            }
          }}
          type={multiline ? undefined : "text"}
          value={tempValues[fieldName] || ''}
          onChange={(e) => {
            setTempValues(prev => ({
              ...prev,
              [fieldName]: e.target.value
            }));
            // Auto-resize on change
            if (multiline) {
              autoResize(e.target);
            }
          }}
          onBlur={() => saveEdit(fieldName)}
          onKeyDown={(e) => handleKeyDown(e, fieldName)}
          className={`inline-edit-input ${className}`}
          placeholder={placeholder}
          style={multiline ? { 
            overflow: 'hidden', // Hide scrollbar
            resize: 'none' // Disable manual resize
          } : {}}
        />
      );
    }

    return (
      <span
        className={`inline-edit-text ${className}`}
        onClick={() => startEdit(fieldName, value)} // Use raw value, not displayValue
        title="Click to edit"
      >
        {displayText}
      </span>
    );
  };

  return (
    <>
      {/* Background overlay - clickable to close, but not in full-screen */}
      {!isFullScreen && (
        <div className="recipe-panel-backdrop" onClick={onClose} />
      )}
      
      {/* Slide-in panel from right with full-screen capability */}
      <div className={`recipe-panel ${isFullScreen ? 'recipe-panel-fullscreen' : ''}`}>
        
        {/* Header Section - Notion-style with inline editing and expand button */}
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
            <EditableText
              fieldName="title"
              value={recipe.title}
              placeholder="Untitled Recipe"
              className="recipe-title-large"
            />
          </div>
          <div className="header-actions">
            <button className="close-panel-btn" onClick={onClose}>✕</button>
          </div>
        </div>

        {/* Recipe Metadata Bar - with inline editing */}
        <div className="recipe-metadata-bar">
          {(formattedServings || editingField === 'servings') && (
            <div className="metadata-item">
              <span className="metadata-icon">🍽️</span>
              <EditableText
                fieldName="servings"
                value={recipe.servings}
                placeholder="Add servings"
                className="metadata-value"
                displayValue={formattedServings}
              />
            </div>
          )}
          
          {(formattedTime || editingField === 'cooking_time') && (
            <div className="metadata-item">
              <span className="metadata-icon">⏱️</span>
              <EditableText
                fieldName="cooking_time"
                value={recipe.cooking_time || recipe.time_min || recipe.prep_time}
                placeholder="Add time"
                className="metadata-value"
                displayValue={formattedTime}
              />
            </div>
          )}
          
          {(formattedDifficulty || editingField === 'difficulty') && (
            <div className="metadata-item">
              <span className="metadata-icon">📊</span>
              <span className="metadata-label">Level:</span>
              <EditableText
                fieldName="difficulty"
                value={recipe.difficulty}
                placeholder="Add difficulty"
                className="metadata-value"
                displayValue={formattedDifficulty}
              />
            </div>
          )}
          
          {(recipe.rating || editingField === 'rating') && (
            <div className="metadata-item">
              <span className="metadata-icon">⭐</span>
              <span className="metadata-label">Rating:</span>
              <EditableText
                fieldName="rating"
                value={recipe.rating}
                placeholder="Add rating"
                className="metadata-value"
                displayValue={recipe.rating ? `${recipe.rating}/5` : null}
              />
            </div>
          )}
        </div>

        {/* Recipe Content - Block-based structure with inline editing */}
        <div className={`recipe-content-flow ${isFullScreen ? 'recipe-content-fullscreen' : ''}`}>
          
          {/* Description Block */}
          <div className="recipe-block description-block">
            <div className="block-content">
              <EditableText
                fieldName="description"
                value={recipe.description}
                placeholder="Add a description for this recipe..."
                className="recipe-description"
                multiline={true}
              />
            </div>
          </div>
          
          {/* Ingredients Block */}
          <div className="recipe-block ingredients-block">
            <EditableText
              fieldName="ingredients-title"
              value={`🛒 Ingredients${ingredients && ingredients.length > 0 ? ` (${ingredients.length})` : ''}`}
              className="block-title"
            />
            <div className="block-content">
              <EditableText
                fieldName="ingredients"
                value={typeof processedRecipe.ingredients === 'string' ? processedRecipe.ingredients : JSON.stringify(processedRecipe.ingredients)}
                placeholder="Add ingredients..."
                className="formatted-recipe-text"
                displayValue={ingredients && ingredients.length > 0 ? ingredients.map(ing => `• ${ing}`).join('\n') : ''}
                multiline={true}
              />
            </div>
          </div>

          {/* Instructions Block */}
          <div className="recipe-block instructions-block">
            <EditableText
              fieldName="instructions-title"
              value={`👨‍🍳 Instructions${instructions && instructions.length > 0 ? ` (${instructions.length} steps)` : ''}`}
              className="block-title"
            />
            <div className="block-content">
              <EditableText
                fieldName="instructions"
                value={typeof processedRecipe.instructions === 'string' ? processedRecipe.instructions : JSON.stringify(processedRecipe.instructions)}
                placeholder="Add cooking instructions..."
                className="formatted-recipe-text"
                displayValue={instructions && instructions.length > 0 ? instructions.map((inst, idx) => `${idx + 1}. ${inst}`).join('\n') : ''}
                multiline={true}
              />
            </div>
          </div>

        </div>

      </div>
    </>
  );
};

export default RecipePanel;
