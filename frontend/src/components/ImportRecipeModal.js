import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import './ImportRecipeModal.css';

const ImportRecipeModal = ({ isOpen, onClose, onImport }) => {
  const { user, token } = useAuth();
  const [importType, setImportType] = useState('text');
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [showPreview, setShowPreview] = useState(false);
  const [editableRecipe, setEditableRecipe] = useState(null);

  // Sample recipe text for demonstration
  const sampleRecipe = `Spaghetti Carbonara

Ingredients:
- 400g spaghetti
- 200g pancetta, diced
- 4 large eggs
- 100g Parmesan cheese, grated
- Black pepper
- Salt

Instructions:
1. Cook spaghetti according to package directions
2. Fry pancetta until crispy
3. Beat eggs with Parmesan
4. Combine hot pasta with pancetta
5. Add egg mixture and toss quickly
6. Season with pepper and serve`;

  const handleImport = async () => {
    if (!inputValue.trim()) {
      setError('Please enter recipe text or URL');
      return;
    }

    // Check if user is authenticated
    if (!user || !token) {
      setError('You must be logged in to import recipes');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const endpoint = importType === 'text' 
        ? '/api/recipes/import/text'
        : '/api/recipes/import/url';

      const requestBody = importType === 'text'
        ? { recipe_text: inputValue, user_id: user.id }
        : { url: inputValue, user_id: user.id };

      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}${endpoint}`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` })
        },
        body: JSON.stringify(requestBody),
      });

      console.log('🌐 Import API Response Status:', response.status);
      console.log('🌐 Import API Response Headers:', response.headers);

      const data = await response.json();
      console.log('🌐 Import API Response Data:', data);

      if (data.success) {
        setResult(data);
        console.log('✅ Import successful, showing preview for editing:', data);
        
        // Create editable version of the recipe data
        setEditableRecipe({
          title: data.recipe_data.title || '',
          description: data.recipe_data.description || '',
          ingredients: data.recipe_data.ingredients || '',
          instructions: data.recipe_data.instructions || '',
          servings: data.recipe_data.servings || '',
          cook_time: data.recipe_data.cook_time || '',
          prep_time: data.recipe_data.prep_time || '',
          category: data.recipe_data.category || '',
          source_url: data.recipe_data.source_url || ''
        });
        
        setShowPreview(true);
      } else {
        console.error('❌ Import failed on server:', data);
        setError(data.error || 'Import failed');
      }
    } catch (err) {
      setError(`Network error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUseSample = () => {
    setInputValue(sampleRecipe);
    setImportType('text');
  };

  const handleClose = () => {
    setInputValue('');
    setResult(null);
    setError(null);
    setShowPreview(false);
    setEditableRecipe(null);
    setImportType('text');
    onClose();
  };

  const handlePreviewEdit = (field, value) => {
    setEditableRecipe(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleConfirmImport = () => {
    console.log('✅ User confirmed import with edits:', editableRecipe);
    
    // Create the final result with user edits
    const finalResult = {
      ...result,
      recipe_data: {
        ...result.recipe_data,
        ...editableRecipe
      }
    };
    
    if (onImport) {
      onImport(finalResult);
    }
    handleClose();
  };

  const handleCancelPreview = () => {
    setShowPreview(false);
    setEditableRecipe(null);
    setResult(null);
  };

  const handleSaveImported = () => {
    // Close modal and trigger any necessary updates
    handleClose();
    // No need to reload page - recipe already added to list
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={handleClose}>
      <div className="import-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>📥 Import Recipe</h2>
          <button className="close-button" onClick={handleClose}>
            ×
          </button>
        </div>

        <div className="modal-content">
          {!result ? (
            <>
              {/* Import Type Selector */}
              <div className="import-type-selector">
                <button
                  className={`type-button ${importType === 'text' ? 'active' : ''}`}
                  onClick={() => setImportType('text')}
                >
                  📝 Text/Paste
                </button>
                <button
                  className={`type-button ${importType === 'url' ? 'active' : ''}`}
                  onClick={() => setImportType('url')}
                >
                  🌐 Website URL
                </button>
              </div>

              {/* Input Area */}
              <div className="input-section">
                {importType === 'text' ? (
                  <div>
                    <label htmlFor="recipe-text">Recipe Text:</label>
                    <textarea
                      id="recipe-text"
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      placeholder="Paste your recipe here...&#10;&#10;Include title, ingredients, and instructions for best results."
                      rows={12}
                      className="recipe-text-input"
                    />
                    <button 
                      className="sample-button"
                      onClick={handleUseSample}
                      type="button"
                    >
                      📋 Use Sample Recipe
                    </button>
                  </div>
                ) : (
                  <div>
                    <label htmlFor="recipe-url">Recipe URL:</label>
                    <input
                      id="recipe-url"
                      type="url"
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      placeholder="https://example.com/recipe"
                      className="recipe-url-input"
                    />
                    <div className="url-help">
                      <p>📍 Supported sites: BonAppetit, Food Network, AllRecipes, and many more!</p>
                      <p>🚧 <em>URL import coming in Day 2 - testing with placeholder for now</em></p>
                    </div>
                  </div>
                )}
              </div>

              {/* Error Display */}
              {error && (
                <div className="error-message">
                  ❌ {error}
                </div>
              )}

              {/* Import Button */}
              <div className="modal-actions">
                <button
                  className="cancel-button"
                  onClick={handleClose}
                  disabled={isLoading}
                >
                  Cancel
                </button>
                <button
                  className="import-button"
                  onClick={handleImport}
                  disabled={isLoading || !inputValue.trim()}
                >
                  {isLoading ? '⏳ Processing...' : '📥 Import Recipe'}
                </button>
              </div>
            </>
          ) : showPreview ? (
            /* Recipe Preview & Edit Interface */
            <div className="recipe-preview-edit">
              <div className="preview-header">
                <h3>📝 Review & Edit Recipe</h3>
                <div className="confidence-indicator">
                  <span>Extraction Confidence: {Math.round(result.confidence * 100)}%</span>
                  <div className="confidence-bar">
                    <div 
                      className="confidence-fill"
                      style={{width: `${result.confidence * 100}%`}}
                    ></div>
                  </div>
                </div>
                <p className="preview-help">Review the imported recipe and make any necessary corrections before saving.</p>
              </div>

              <div className="editable-fields">
                {/* Title */}
                <div className="edit-field">
                  <label htmlFor="edit-title">Recipe Title:</label>
                  <input
                    id="edit-title"
                    type="text"
                    value={editableRecipe?.title || ''}
                    onChange={(e) => handlePreviewEdit('title', e.target.value)}
                    className="edit-input"
                    placeholder="Enter recipe title"
                  />
                </div>

                {/* Description */}
                <div className="edit-field">
                  <label htmlFor="edit-description">Description:</label>
                  <textarea
                    id="edit-description"
                    value={editableRecipe?.description || ''}
                    onChange={(e) => handlePreviewEdit('description', e.target.value)}
                    className="edit-textarea short"
                    placeholder="Brief recipe description"
                    rows={2}
                  />
                </div>

                {/* Category and Times Row */}
                <div className="edit-row">
                  <div className="edit-field">
                    <label htmlFor="edit-category">Category:</label>
                    <input
                      id="edit-category"
                      type="text"
                      value={editableRecipe?.category || ''}
                      onChange={(e) => handlePreviewEdit('category', e.target.value)}
                      className="edit-input"
                      placeholder="e.g., Main Course"
                    />
                  </div>
                  <div className="edit-field">
                    <label htmlFor="edit-servings">Servings:</label>
                    <input
                      id="edit-servings"
                      type="text"
                      value={editableRecipe?.servings || ''}
                      onChange={(e) => handlePreviewEdit('servings', e.target.value)}
                      className="edit-input"
                      placeholder="e.g., 4"
                    />
                  </div>
                </div>

                <div className="edit-row">
                  <div className="edit-field">
                    <label htmlFor="edit-prep-time">Prep Time:</label>
                    <input
                      id="edit-prep-time"
                      type="text"
                      value={editableRecipe?.prep_time || ''}
                      onChange={(e) => handlePreviewEdit('prep_time', e.target.value)}
                      className="edit-input"
                      placeholder="e.g., 15 minutes"
                    />
                  </div>
                  <div className="edit-field">
                    <label htmlFor="edit-cook-time">Cook Time:</label>
                    <input
                      id="edit-cook-time"
                      type="text"
                      value={editableRecipe?.cook_time || ''}
                      onChange={(e) => handlePreviewEdit('cook_time', e.target.value)}
                      className="edit-input"
                      placeholder="e.g., 30 minutes"
                    />
                  </div>
                </div>

                {/* Ingredients */}
                <div className="edit-field">
                  <label htmlFor="edit-ingredients">Ingredients:</label>
                  <textarea
                    id="edit-ingredients"
                    value={editableRecipe?.ingredients || ''}
                    onChange={(e) => handlePreviewEdit('ingredients', e.target.value)}
                    className="edit-textarea"
                    placeholder="Enter ingredients (one per line)"
                    rows={8}
                  />
                </div>

                {/* Instructions */}
                <div className="edit-field">
                  <label htmlFor="edit-instructions">Instructions:</label>
                  <textarea
                    id="edit-instructions"
                    value={editableRecipe?.instructions || ''}
                    onChange={(e) => handlePreviewEdit('instructions', e.target.value)}
                    className="edit-textarea"
                    placeholder="Enter cooking instructions"
                    rows={8}
                  />
                </div>

                {/* Source URL (read-only) */}
                <div className="edit-field">
                  <label htmlFor="edit-source">Source URL:</label>
                  <input
                    id="edit-source"
                    type="url"
                    value={editableRecipe?.source_url || ''}
                    className="edit-input readonly"
                    disabled
                  />
                </div>
              </div>

              {/* Preview Actions */}
              <div className="preview-actions">
                <button
                  className="cancel-button"
                  onClick={handleCancelPreview}
                >
                  ← Back to Import
                </button>
                <button
                  className="confirm-button"
                  onClick={handleConfirmImport}
                >
                  ✅ Save Recipe
                </button>
              </div>
            </div>
          ) : (
            /* Import Success Result (old success display) */
            <div className="import-result">
              <div className="result-header">
                <h3>✅ Import Successful!</h3>
                <div className="confidence-indicator">
                  <span>Confidence: {Math.round(result.confidence * 100)}%</span>
                  <div className="confidence-bar">
                    <div 
                      className="confidence-fill"
                      style={{width: `${result.confidence * 100}%`}}
                    ></div>
                  </div>
                </div>
              </div>

              <div className="result-details">
                <div className="recipe-preview">
                  <h4>📖 Recipe Preview:</h4>
                  <div className="preview-field">
                    <strong>Title:</strong> {result.recipe_data?.title || 'Imported Recipe'}
                  </div>
                  <div className="preview-field">
                    <strong>Category:</strong> {result.recipe_data?.category || 'imported'}
                  </div>
                  <div className="preview-field">
                    <strong>Ingredients:</strong>
                    <div className="ingredients-preview">
                      {result.recipe_data?.ingredients?.split('\n').slice(0, 3).map((ingredient, idx) => (
                        <div key={idx}>• {ingredient}</div>
                      ))}
                      {result.recipe_data?.ingredients?.split('\n').length > 3 && (
                        <div>... and {result.recipe_data.ingredients.split('\n').length - 3} more</div>
                      )}
                    </div>
                  </div>
                </div>

                <div className="import-stats">
                  <div className="stat">
                    <span className="stat-label">Processing Time:</span>
                    <span className="stat-value">{result.processing_time?.toFixed(2)}s</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Extraction Method:</span>
                    <span className="stat-value">{result.extraction_method}</span>
                  </div>
                  {result.recipe_id && (
                    <div className="stat">
                      <span className="stat-label">Recipe ID:</span>
                      <span className="stat-value">#{result.recipe_id}</span>
                    </div>
                  )}
                </div>

                {result.needs_review && (
                  <div className="review-notice">
                    ⚠️ This recipe needs review due to low confidence. You can still save it and edit later.
                  </div>
                )}

                {result.warnings && result.warnings.length > 0 && (
                  <div className="warnings">
                    <h5>⚠️ Warnings:</h5>
                    {result.warnings.map((warning, idx) => (
                      <div key={idx}>• {warning}</div>
                    ))}
                  </div>
                )}
              </div>

              <div className="result-actions">
                <button
                  className="secondary-button"
                  onClick={() => setResult(null)}
                >
                  ← Import Another
                </button>
                <button
                  className="primary-button"
                  onClick={handleSaveImported}
                >
                  ✅ Done
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ImportRecipeModal;
