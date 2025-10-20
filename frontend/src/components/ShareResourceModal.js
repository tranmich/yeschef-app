import React, { useState, useEffect } from 'react';
import * as householdAPI from '../utils/householdAPI';
import './ShareResourceModal.css';

const ShareResourceModal = ({ 
  isOpen, 
  onClose, 
  resourceType, // 'grocery_list' or 'meal_plan'
  resourceId, 
  resourceName,
  onShare 
}) => {
  const [households, setHouseholds] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sharing, setSharing] = useState(false);
  const [error, setError] = useState('');
  const [selectedHousehold, setSelectedHousehold] = useState(null);
  const [permissionLevel, setPermissionLevel] = useState('editor');

  useEffect(() => {
    if (isOpen) {
      loadHouseholds();
    }
  }, [isOpen]);

  const loadHouseholds = async () => {
    setLoading(true);
    setError('');
    
    try {
      const result = await householdAPI.getHouseholds();
      
      if (result.success) {
        setHouseholds(result.households || []);
      } else {
        setError(result.error || 'Failed to load households');
      }
    } catch (err) {
      setError('An error occurred while loading households');
      console.error('Load households error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleShare = async () => {
    if (!selectedHousehold) {
      setError('Please select a household');
      return;
    }

    setSharing(true);
    setError('');

    try {
      const result = await householdAPI.shareWithHousehold(
        resourceType,
        resourceId,
        selectedHousehold.id,
        permissionLevel
      );

      if (result.success) {
        onShare?.(selectedHousehold, result);
        handleClose();
      } else {
        setError(result.error || 'Failed to share resource');
      }
    } catch (err) {
      setError('An error occurred while sharing');
      console.error('Share error:', err);
    } finally {
      setSharing(false);
    }
  };

  const handleClose = () => {
    setSelectedHousehold(null);
    setPermissionLevel('editor');
    setError('');
    onClose();
  };

  if (!isOpen) return null;

  const resourceTypeLabel = resourceType === 'grocery_list' ? 'Grocery List' : 'Meal Plan';

  return (
    <div className="modal-overlay" onClick={handleClose}>
      <div className="modal-content share-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <h2>🔗 Share {resourceTypeLabel}</h2>
            {resourceName && (
              <p className="modal-subtitle">Share "{resourceName}" with a household</p>
            )}
          </div>
          <button className="modal-close-btn" onClick={handleClose} disabled={sharing}>
            ✕
          </button>
        </div>

        {error && (
          <div className="error-message">
            ⚠️ {error}
          </div>
        )}

        {loading ? (
          <div className="loading-container">
            <div className="loading-spinner-small"></div>
            <p>Loading households...</p>
          </div>
        ) : households.length === 0 ? (
          <div className="empty-state-small">
            <div className="empty-icon">🏠</div>
            <h3>No Households Yet</h3>
            <p>Create a household in the Friends section to start sharing!</p>
          </div>
        ) : (
          <>
            <div className="share-form">
              <div className="form-group">
                <label>Select Household</label>
                <div className="households-list">
                  {households.map((household) => (
                    <div
                      key={household.id}
                      className={`household-option ${selectedHousehold?.id === household.id ? 'selected' : ''}`}
                      onClick={() => setSelectedHousehold(household)}
                    >
                      <div className="household-option-icon">🏠</div>
                      <div className="household-option-info">
                        <div className="household-option-name">{household.name}</div>
                        <div className="household-option-meta">
                          {household.members} {household.members === 1 ? 'member' : 'members'}
                          {household.role === 'owner' && ' • You own this'}
                        </div>
                      </div>
                      {selectedHousehold?.id === household.id && (
                        <div className="selected-check">✓</div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              <div className="form-group">
                <label>Permission Level</label>
                <div className="permission-options">
                  <label className="permission-option">
                    <input
                      type="radio"
                      name="permission"
                      value="editor"
                      checked={permissionLevel === 'editor'}
                      onChange={(e) => setPermissionLevel(e.target.value)}
                      disabled={sharing}
                    />
                    <div className="permission-label">
                      <div className="permission-name">✏️ Editor</div>
                      <div className="permission-desc">Can view and edit</div>
                    </div>
                  </label>
                  <label className="permission-option">
                    <input
                      type="radio"
                      name="permission"
                      value="viewer"
                      checked={permissionLevel === 'viewer'}
                      onChange={(e) => setPermissionLevel(e.target.value)}
                      disabled={sharing}
                    />
                    <div className="permission-label">
                      <div className="permission-name">👁️ Viewer</div>
                      <div className="permission-desc">Can only view</div>
                    </div>
                  </label>
                </div>
              </div>
            </div>

            <div className="modal-actions">
              <button
                className="cancel-btn"
                onClick={handleClose}
                disabled={sharing}
              >
                Cancel
              </button>
              <button
                className="share-btn"
                onClick={handleShare}
                disabled={!selectedHousehold || sharing}
              >
                {sharing ? '⏳ Sharing...' : '🔗 Share Now'}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default ShareResourceModal;
