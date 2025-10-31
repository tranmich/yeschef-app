import React, { useState } from 'react';
import './PhotoImportModal.css';

const PhotoImportModal = ({ isOpen, onClose, onImport }) => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [previews, setPreviews] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [extractionMode, setExtractionMode] = useState('ai'); // 'ai' or 'manual'

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    setSelectedFiles(files);

    // Generate previews
    const newPreviews = files.map(file => ({
      file,
      url: URL.createObjectURL(file),
      name: file.name
    }));
    setPreviews(newPreviews);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files).filter(file => 
      file.type.startsWith('image/')
    );
    
    if (files.length > 0) {
      setSelectedFiles(files);
      const newPreviews = files.map(file => ({
        file,
        url: URL.createObjectURL(file),
        name: file.name
      }));
      setPreviews(newPreviews);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const removePreview = (index) => {
    setPreviews(prev => prev.filter((_, i) => i !== index));
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleImport = async () => {
    if (selectedFiles.length === 0) return;

    setUploading(true);

    try {
      // Create FormData for file upload
      const formData = new FormData();
      selectedFiles.forEach((file, index) => {
        formData.append(`photos`, file);
      });
      formData.append('extraction_mode', extractionMode);
      formData.append('user_id', localStorage.getItem('userId') || '1');

      // Call the import handler
      await onImport(formData);

      // Reset state
      setSelectedFiles([]);
      setPreviews([]);
      onClose();
    } catch (error) {
      console.error('Photo import error:', error);
      alert('Failed to import photos. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="photo-import-modal-overlay" onClick={onClose}>
      <div className="photo-import-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Import Recipe from Photo</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          {previews.length === 0 ? (
            <div 
              className="dropzone"
              onDrop={handleDrop}
              onDragOver={handleDragOver}
            >
              <div className="dropzone-content">
                <h3>Drag & Drop Photos Here</h3>
                <p>or</p>
                <label className="file-select-btn">
                  Choose Files
                  <input
                    type="file"
                    multiple
                    accept="image/*"
                    onChange={handleFileSelect}
                    style={{ display: 'none' }}
                  />
                </label>
                <p className="dropzone-hint">
                  Supports: JPG, PNG, HEIC • Recipe cards, cookbook pages, screenshots
                </p>
              </div>
            </div>
          ) : (
            <>
              <div className="preview-grid">
                {previews.map((preview, index) => (
                  <div key={index} className="preview-card">
                    <img src={preview.url} alt={`Preview ${index + 1}`} />
                    <button
                      className="remove-preview-btn"
                      onClick={() => removePreview(index)}
                    >
                      ✕
                    </button>
                    <p className="preview-name">{preview.name}</p>
                  </div>
                ))}
              </div>

              <div className="add-more-section">
                <label className="add-more-btn">
                  + Add More Photos
                  <input
                    type="file"
                    multiple
                    accept="image/*"
                    onChange={(e) => {
                      const newFiles = Array.from(e.target.files);
                      setSelectedFiles(prev => [...prev, ...newFiles]);
                      const newPreviews = newFiles.map(file => ({
                        file,
                        url: URL.createObjectURL(file),
                        name: file.name
                      }));
                      setPreviews(prev => [...prev, ...newPreviews]);
                    }}
                    style={{ display: 'none' }}
                  />
                </label>
              </div>

              <div className="extraction-mode-section">
                <h3>Extraction Method</h3>
                <div className="mode-options">
                  <label className={`mode-option ${extractionMode === 'ai' ? 'active' : ''}`}>
                    <input
                      type="radio"
                      name="extraction"
                      value="ai"
                      checked={extractionMode === 'ai'}
                      onChange={(e) => setExtractionMode(e.target.value)}
                    />
                    <div className="mode-content">
                      <div>
                        <strong>AI Extraction</strong>
                        <p>Automatically extract recipe details (recommended)</p>
                      </div>
                    </div>
                  </label>

                  <label className={`mode-option ${extractionMode === 'manual' ? 'active' : ''}`}>
                    <input
                      type="radio"
                      name="extraction"
                      value="manual"
                      checked={extractionMode === 'manual'}
                      onChange={(e) => setExtractionMode(e.target.value)}
                    />
                    <div className="mode-content">
                      <div>
                        <strong>Manual Entry</strong>
                        <p>I'll type the recipe details myself</p>
                      </div>
                    </div>
                  </label>
                </div>
              </div>
            </>
          )}
        </div>

        <div className="modal-footer">
          <button className="cancel-btn" onClick={onClose} disabled={uploading}>
            Cancel
          </button>
          <button
            className="import-btn"
            onClick={handleImport}
            disabled={previews.length === 0 || uploading}
          >
            {uploading ? (
              <>Processing...</>
            ) : (
              `Import ${previews.length} ${previews.length === 1 ? 'Photo' : 'Photos'}`
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default PhotoImportModal;
