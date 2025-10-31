import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import './ImportRecipeModal.css';

// Helper function to extract clean image URL from corrupted data
const extractCleanImageUrl = (imageData) => {
  if (!imageData) return null;
  
  // If it's already a clean URL, return it
  if (typeof imageData === 'string' && imageData.startsWith('http')) {
    return imageData;
  }
  
  // If it's a corrupted dict string, extract contentUrl
  if (typeof imageData === 'string' && imageData.includes("'contentUrl':")) {
    try {
      const match = imageData.match(/'contentUrl':\s*'([^']+)'/);
      if (match && match[1]) {
        return match[1];
      }
      // Try 'url' field as fallback
      const urlMatch = imageData.match(/'url':\s*'([^']+)'/);
      if (urlMatch && urlMatch[1]) {
        return urlMatch[1];
      }
    } catch (e) {
      console.error('Failed to extract image URL:', e);
    }
  }
  
  return null;
};

const ImportRecipeModal = ({ isOpen, onClose, onImport, isInlineView = false }) => {
  const { user, token } = useAuth();
  const [importType, setImportType] = useState('url'); // Changed default to 'url' (Web first)
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [showPreview, setShowPreview] = useState(false);
  const [editableRecipe, setEditableRecipe] = useState(null);
  
  // Photo/OCR state
  const [selectedImages, setSelectedImages] = useState([]);
  const [imagePreviews, setImagePreviews] = useState([]);
  
  // Voice recording state
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [recordingTime, setRecordingTime] = useState(0);
  const [mediaRecorder, setMediaRecorder] = useState(null);

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
    if (importType === 'photo') {
      await handlePhotoImport();
      return;
    }
    
    if (importType === 'voice') {
      await handleVoiceImport();
      return;
    }
    
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
        console.log('✅ Import successful, showing preview for editing:', data);
        
        setResult(data);
        
        // Create editable version of the recipe data
        const editableData = {
          title: data.recipe_data.title || '',
          description: data.recipe_data.description || '',
          ingredients: data.recipe_data.ingredients || '',
          instructions: data.recipe_data.instructions || '',
          servings: data.recipe_data.servings || '',
          cook_time: data.recipe_data.cook_time || '',
          prep_time: data.recipe_data.prep_time || '',
          category: data.recipe_data.category || '',
          source_url: data.recipe_data.source_url || '',
          image_url: data.recipe_data.image_url || ''
        };
        
        setEditableRecipe(editableData);
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

  // Photo/OCR handlers
  const handleImageSelect = (e) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;

    setSelectedImages(files);
    
    // Create preview URLs
    const previews = files.map(file => URL.createObjectURL(file));
    setImagePreviews(previews);
    setError(null);
  };

  const handleRemoveImage = (index) => {
    const newImages = selectedImages.filter((_, i) => i !== index);
    const newPreviews = imagePreviews.filter((_, i) => i !== index);
    
    // Cleanup old preview URL
    URL.revokeObjectURL(imagePreviews[index]);
    
    setSelectedImages(newImages);
    setImagePreviews(newPreviews);
  };

  const handlePhotoImport = async () => {
    if (selectedImages.length === 0) {
      setError('Please select at least one image');
      return;
    }

    if (!user || !token) {
      setError('You must be logged in to import recipes');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      
      // Add images to form data
      selectedImages.forEach((image, index) => {
        formData.append(`image_${index}`, image);
      });

      // Add metadata
      formData.append('metadata', JSON.stringify({
        user_id: user.id,
        image_count: selectedImages.length
      }));

      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/recipes/import/ocr`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          ...(token && { 'Authorization': `Bearer ${token}` })
        },
        body: formData
      });

      const data = await response.json();

      if (data.success) {
        setResult(data);
        setEditableRecipe({
          title: data.recipe_data.title || '',
          description: data.recipe_data.description || '',
          ingredients: data.recipe_data.ingredients || '',
          instructions: data.recipe_data.instructions || '',
          servings: data.recipe_data.servings || '',
          cook_time: data.recipe_data.cook_time || '',
          prep_time: data.recipe_data.prep_time || '',
          category: data.recipe_data.category || ''
        });
        setShowPreview(true);
      } else {
        setError(data.error || 'OCR import failed');
      }
    } catch (err) {
      setError(`Network error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Voice recording handlers
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunks.push(e.data);
        }
      };

      recorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/webm' });
        setAudioBlob(blob);
        stream.getTracks().forEach(track => track.stop());
      };

      recorder.start();
      setMediaRecorder(recorder);
      setIsRecording(true);
      setRecordingTime(0);
      setError(null);

      // Start timer
      const timer = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);

      // Store timer ID on recorder for cleanup
      recorder.timerId = timer;
    } catch (err) {
      setError('Microphone access denied. Please enable microphone permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorder && isRecording) {
      mediaRecorder.stop();
      clearInterval(mediaRecorder.timerId);
      setIsRecording(false);
    }
  };

  const handleVoiceImport = async () => {
    if (!audioBlob) {
      setError('Please record audio first');
      return;
    }

    if (!user || !token) {
      setError('You must be logged in to import recipes');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      
      // Add audio as single segment
      formData.append('segment_0', audioBlob, 'recording.webm');

      // Add metadata
      formData.append('metadata', JSON.stringify({
        session_id: `web_${Date.now()}`,
        total_duration_ms: recordingTime * 1000,
        segments: [{
          label: 'Full Recording',
          duration_ms: recordingTime * 1000
        }],
        language_config: {
          whisperCode: 'en',
          culture: 'English',
          displayName: 'English'
        }
      }));

      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/recipes/voice/session/process`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          ...(token && { 'Authorization': `Bearer ${token}` })
        },
        body: formData
      });

      const data = await response.json();

      if (data.success) {
        setResult(data);
        setEditableRecipe({
          title: data.recipe_data?.title || '',
          description: data.recipe_data?.description || '',
          ingredients: data.recipe_data?.ingredients || '',
          instructions: data.recipe_data?.instructions || '',
          servings: data.recipe_data?.servings || '',
          cook_time: data.recipe_data?.cook_time || '',
          prep_time: data.recipe_data?.prep_time || '',
          category: data.recipe_data?.category || ''
        });
        setShowPreview(true);
      } else {
        setError(data.error || 'Voice import failed');
      }
    } catch (err) {
      setError(`Network error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const formatRecordingTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Helper function to render the photo import section
  const renderPhotoImport = () => {
    return (
      <div className="photo-import-section">
        <div className="photo-upload-area">
          <input
            type="file"
            multiple
            accept="image/*"
            onChange={handleImageSelect}
            className="photo-input"
            id="photo-input"
          />
          <label htmlFor="photo-input" className="photo-upload-label">
            Click to select photos or drag & drop
          </label>
        </div>

        {imagePreviews.length > 0 && (
          <div className="image-previews">
            {imagePreviews.map((preview, index) => (
              <div key={index} className="image-preview">
                <img src={preview} alt={`Preview ${index + 1}`} />
                <button
                  onClick={() => handleRemoveImage(index)}
                  className="remove-image-btn"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        )}

        <div className="import-option-description">
          <p>Take photos of recipe pages, cookbooks, or handwritten recipes</p>
          <p>YesChef will extract text and create a structured recipe</p>
        </div>
      </div>
    );
  };

  // Helper function to render the voice import section
  const renderVoiceImport = () => {
    return (
      <div className="voice-import-section">
        <div className="voice-controls">
          <button
            onClick={isRecording ? stopRecording : startRecording}
            className={`voice-button ${isRecording ? 'recording' : ''}`}
          >
            {isRecording ? 'Stop Recording' : 'Start Recording'}
          </button>

          {isRecording && (
            <div className="recording-indicator">
              <span className="recording-time">
                {formatRecordingTime(recordingTime)}
              </span>
            </div>
          )}

          {audioBlob && !isRecording && (
            <div className="audio-preview">
              <audio controls src={URL.createObjectURL(audioBlob)} />
            </div>
          )}
        </div>

        <div className="voice-help">
          <p>Record yourself reading a recipe out loud</p>
          <p>YesChef will transcribe and structure your recipe</p>
        </div>
      </div>
    );
  };

  // Helper function to render import content
  const renderImportContent = () => {
    return (
      <>
        {/* Input Area */}
        <div className="input-section">
          {importType === 'url' ? (
            <div>
              <label htmlFor="recipe-url">Recipe Website URL:</label>
              <input
                id="recipe-url"
                type="url"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="https://example.com/recipe"
                className="recipe-url-input"
              />
              <div className="url-help">
                <p>Paste a recipe URL from your favorite cooking site</p>
                <p>Works with BonAppetit, Food Network, AllRecipes, and many more!</p>
              </div>
            </div>
          ) : importType === 'text' ? (
            <div>
              <label htmlFor="recipe-text">Paste Recipe Text:</label>
              <textarea
                id="recipe-text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder={sampleRecipe}
                className="recipe-text-input"
                rows={15}
              />
              <div className="text-help">
                <p>Paste recipe text from any source</p>
                <p>YesChef will intelligently parse ingredients and instructions</p>
              </div>
            </div>
          ) : importType === 'photo' ? (
            renderPhotoImport()
          ) : importType === 'voice' ? (
            renderVoiceImport()
          ) : null}
        </div>

        {/* Action Buttons */}
        <div className="action-buttons">
          <button
            onClick={handleImport}
            disabled={isLoading || (!inputValue && importType !== 'photo' && importType !== 'voice')}
            className="import-button"
          >
            {isLoading ? 'Processing...' : 'Import Recipe'}
          </button>
        </div>

        {error && (
          <div className="error-message">
            <p>{error}</p>
          </div>
        )}
      </>
    );
  };

  // Helper function to render results
  const renderResult = () => {
    // If showPreview is true, render the editable preview
    if (showPreview && editableRecipe) {
      return (
        <div className="recipe-preview-edit">
          <div className="preview-header">
            <h3>Review & Edit Recipe</h3>
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

            {/* Image Preview */}
            {editableRecipe?.image_url && (
              <div className="edit-field">
                <label>Recipe Image:</label>
                <div className="recipe-image-preview">
                  <img 
                    src={extractCleanImageUrl(editableRecipe.image_url) || `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}${editableRecipe.image_url}`}
                    alt={editableRecipe.title || 'Recipe'}
                    onError={(e) => {
                      console.error('❌ Image failed to load');
                      // Show a placeholder instead of hiding
                      const svgPlaceholder = `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='300'%3E%3Crect fill='%23e5e7eb' width='400' height='300'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='system-ui' font-size='16' fill='%239ca3af'%3EImage Not Available%3C/text%3E%3C/svg%3E`;
                      e.target.src = svgPlaceholder;
                    }}
                    onLoad={() => {
                      console.log('✅ Image loaded successfully');
                    }}
                  />
                </div>
              </div>
            )}

            {/* Category and Servings Row */}
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

            {/* Times Row */}
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
      );
    }

    // Otherwise, show the simple success message
    return (
      <div className="result-section">
        {result && (
          <>
            <div className="success-message">
              <p>✅ Recipe imported successfully!</p>
            </div>
            
            {result.recipe_data && (
              <div className="recipe-preview-section">
                <h3>📖 Recipe Preview</h3>
                <div className="recipe-summary">
                  <h4>{result.recipe_data.title}</h4>
                  {result.recipe_data.description && (
                    <p className="recipe-description">{result.recipe_data.description}</p>
                  )}
                  
                  <div className="recipe-meta-grid">
                    {result.recipe_data.prep_time && (
                      <div className="meta-item">
                        <span className="meta-label">⏱️ Prep:</span>
                        <span className="meta-value">{result.recipe_data.prep_time}</span>
                      </div>
                    )}
                    {result.recipe_data.cook_time && (
                      <div className="meta-item">
                        <span className="meta-label">🔥 Cook:</span>
                        <span className="meta-value">{result.recipe_data.cook_time}</span>
                      </div>
                    )}
                    {result.recipe_data.servings && (
                      <div className="meta-item">
                        <span className="meta-label">🍽️ Serves:</span>
                        <span className="meta-value">{result.recipe_data.servings}</span>
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="action-buttons">
                  <button
                    onClick={() => {
                      onImport(result);
                      resetForm();
                    }}
                    className="confirm-button"
                  >
                    ✅ Add to My Recipes
                  </button>
                  <button
                    onClick={() => setShowPreview(true)}
                    className="preview-button"
                  >
                    👁️ Full Preview
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    );
  };

  const resetForm = () => {
    setInputValue('');
    setResult(null);
    setError(null);
    setSelectedImages([]);
    setImagePreviews([]);
    setAudioBlob(null);
    setRecordingTime(0);
    setIsRecording(false);
  };

  if (!isOpen) return null;

  // Render inline view for main app integration
  if (isInlineView) {
    return (
      <div className="import-modal-inline">
        <div className="modal-header-inline">
          <h2>➕ Add Recipe</h2>
          <button className="close-button-inline" onClick={onClose}>
            ← Back to Recipes
          </button>
        </div>

        <div className="modal-content-inline">
          {!result ? (
            <>
              {/* Import Type Selector - 4 Tabs: Web, Manual, Photo, Voice */}
              <div className="import-type-selector">
                <button
                  className={`type-button ${importType === 'url' ? 'active' : ''}`}
                  onClick={() => setImportType('url')}
                >
                  From Web
                </button>
                <button
                  className={`type-button ${importType === 'text' ? 'active' : ''}`}
                  onClick={() => setImportType('text')}
                >
                  Manual Entry
                </button>
                <button
                  className={`type-button ${importType === 'photo' ? 'active' : ''}`}
                  onClick={() => setImportType('photo')}
                >
                  From Photo
                </button>
                <button
                  className={`type-button ${importType === 'voice' ? 'active' : ''}`}
                  onClick={() => setImportType('voice')}
                >
                  Voice Recipe
                </button>
              </div>

              {/* Rest of the content will be rendered here */}
              {renderImportContent()}
            </>
          ) : (
            renderResult()
          )}
        </div>
      </div>
    );
  }

  // Original modal rendering for other uses
  return (
    <div className="modal-overlay" onClick={handleClose}>
      <div className="import-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>➕ Add Recipe</h2>
          <button className="close-button" onClick={handleClose}>
            ×
          </button>
        </div>

        <div className="modal-content">
          {!result ? (
            <>
              {/* Import Type Selector - 4 Tabs: Web, Manual, Photo, Voice */}
              <div className="import-type-selector">
                <button
                  className={`type-button ${importType === 'url' ? 'active' : ''}`}
                  onClick={() => setImportType('url')}
                >
                  From Web
                </button>
                <button
                  className={`type-button ${importType === 'text' ? 'active' : ''}`}
                  onClick={() => setImportType('text')}
                >
                  Manual Entry
                </button>
                <button
                  className={`type-button ${importType === 'photo' ? 'active' : ''}`}
                  onClick={() => setImportType('photo')}
                >
                  Photo/Scan
                </button>
                <button
                  className={`type-button ${importType === 'voice' ? 'active' : ''}`}
                  onClick={() => setImportType('voice')}
                >
                  Voice
                </button>
              </div>

              {/* Input Area */}
              <div className="input-section">
                {importType === 'url' ? (
                  <div>
                    <label htmlFor="recipe-url">Recipe Website URL:</label>
                    <input
                      id="recipe-url"
                      type="url"
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      placeholder="https://example.com/recipe"
                      className="recipe-url-input"
                    />
                    <div className="url-help">
                      <p>✨ Paste a recipe URL from your favorite cooking site</p>
                      <p>🍳 Works with BonAppetit, Food Network, AllRecipes, and many more!</p>
                    </div>
                  </div>
                ) : importType === 'text' ? (
                  <div>
                    <label htmlFor="recipe-text">Paste Recipe Text:</label>
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
                ) : importType === 'photo' ? (
                  <div>
                    <label>Upload Recipe Photos:</label>
                    <div className="photo-upload-area">
                      <input
                        type="file"
                        id="photo-input"
                        accept="image/*"
                        multiple
                        onChange={handleImageSelect}
                        style={{ display: 'none' }}
                      />
                      <label htmlFor="photo-input" className="photo-upload-button">
                        <span className="upload-icon">📸</span>
                        <span className="upload-text">Click to Upload Photos</span>
                        <span className="upload-hint">or drag and drop</span>
                      </label>
                    </div>
                    
                    {imagePreviews.length > 0 && (
                      <div className="image-previews">
                        {imagePreviews.map((preview, index) => (
                          <div key={index} className="image-preview">
                            <img src={preview} alt={`Preview ${index + 1}`} />
                            <button
                              className="remove-image-btn"
                              onClick={() => handleRemoveImage(index)}
                              type="button"
                            >
                              ×
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                    
                    <div className="photo-help">
                      <p>📷 Take clear photos of recipe cards, cookbook pages, or handwritten recipes</p>
                      <p>✨ Our AI will extract the text and format it for you!</p>
                    </div>
                  </div>
                ) : importType === 'voice' ? (
                  <div>
                    <label>Record Recipe:</label>
                    <div className="voice-recorder">
                      {!audioBlob ? (
                        <>
                          <div className="recording-controls">
                            {!isRecording ? (
                              <button
                                className="record-button"
                                onClick={startRecording}
                                type="button"
                              >
                                <span className="record-icon">🎤</span>
                                <span>Start Recording</span>
                              </button>
                            ) : (
                              <>
                                <div className="recording-indicator">
                                  <span className="recording-dot">●</span>
                                  <span className="recording-time">{formatRecordingTime(recordingTime)}</span>
                                </div>
                                <button
                                  className="stop-button"
                                  onClick={stopRecording}
                                  type="button"
                                >
                                  <span>⏹ Stop</span>
                                </button>
                              </>
                            )}
                          </div>
                        </>
                      ) : (
                        <div className="audio-preview">
                          <div className="audio-info">
                            <span className="audio-icon">🎵</span>
                            <span className="audio-duration">{formatRecordingTime(recordingTime)}</span>
                          </div>
                          <button
                            className="re-record-button"
                            onClick={() => {
                              setAudioBlob(null);
                              setRecordingTime(0);
                            }}
                            type="button"
                          >
                            🔄 Re-record
                          </button>
                        </div>
                      )}
                    </div>
                    
                    <div className="voice-help">
                      <p>🎤 Speak your recipe out loud - include ingredients and instructions</p>
                      <p>✨ Our AI will transcribe and format it for you!</p>
                    </div>
                  </div>
                ) : null}
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

                {/* Image Preview */}
                {editableRecipe?.image_url && (
                  <div className="edit-field">
                    <label>Recipe Image:</label>
                    <div className="recipe-image-preview">
                      <img 
                        src={extractCleanImageUrl(editableRecipe.image_url) || `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}${editableRecipe.image_url}`}
                        alt={editableRecipe.title || 'Recipe'}
                        onError={(e) => {
                          console.error('❌ Image failed to load');
                          const svgPlaceholder = `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='300'%3E%3Crect fill='%23e5e7eb' width='400' height='300'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='system-ui' font-size='16' fill='%239ca3af'%3EImage Not Available%3C/text%3E%3C/svg%3E`;
                          e.target.src = svgPlaceholder;
                        }}
                        onLoad={() => {
                          console.log('✅ Image loaded successfully');
                        }}
                      />
                    </div>
                  </div>
                )}

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
