import React, { useState } from 'react';
import './CreateHouseholdModal.css';

const CreateHouseholdModal = ({ isOpen, onClose, onCreate }) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!name.trim()) {
      setError('Please enter a household name');
      return;
    }

    setIsCreating(true);
    setError('');

    try {
      const result = await onCreate(name.trim(), description.trim());
      
      if (result.success) {
        // Reset form
        setName('');
        setDescription('');
        onClose();
      } else {
        setError(result.error || 'Failed to create household');
      }
    } catch (err) {
      setError('An error occurred. Please try again.');
    } finally {
      setIsCreating(false);
    }
  };

  const handleClose = () => {
    if (!isCreating) {
      setName('');
      setDescription('');
      setError('');
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={handleClose}>
      <div className="modal-content create-household-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>🏠 Create New Household</h2>
          <button className="modal-close-btn" onClick={handleClose} disabled={isCreating}>
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="household-form">
          <div className="form-group">
            <label htmlFor="household-name">
              Household Name <span className="required">*</span>
            </label>
            <input
              id="household-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., Smith Family, Roommates, The Team"
              maxLength={100}
              disabled={isCreating}
              autoFocus
            />
          </div>

          <div className="form-group">
            <label htmlFor="household-description">
              Description <span className="optional">(optional)</span>
            </label>
            <textarea
              id="household-description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="What's this household for?"
              rows={3}
              maxLength={255}
              disabled={isCreating}
            />
          </div>

          {error && (
            <div className="error-message">
              ⚠️ {error}
            </div>
          )}

          <div className="form-actions">
            <button
              type="button"
              className="cancel-btn"
              onClick={handleClose}
              disabled={isCreating}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="create-btn"
              disabled={isCreating || !name.trim()}
            >
              {isCreating ? '⏳ Creating...' : '✨ Create Household'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateHouseholdModal;
