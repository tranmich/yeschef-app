/**
 * Whiteboard Navigator
 * ====================
 * Lists all whiteboards for a household
 * Allows creating, viewing, and managing whiteboards
 * 
 * Phase 1 - Week 3
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import whiteboardAPI from '../services/whiteboardAPI';
import { ToastProvider, useToast } from '../components/ToastContainer';
import './WhiteboardNavigator.css';

const WhiteboardNavigator = ({ householdId, onBack, onSelectWhiteboard }) => {
  const { user } = useAuth();
  const toast = useToast();

  const [whiteboards, setWhiteboards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newWhiteboardName, setNewWhiteboardName] = useState('');
  const [newWhiteboardDescription, setNewWhiteboardDescription] = useState('');
  const [creating, setCreating] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState(null); // { id, name }

  // Load whiteboards on mount
  useEffect(() => {
    loadWhiteboards();
  }, [householdId]);

  // Reload whiteboards when window regains focus (catches updates from whiteboard)
  useEffect(() => {
    const handleFocus = () => {
      console.log('🔄 Window focused - reloading whiteboards to catch any updates');
      loadWhiteboards();
    };

    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, [householdId]);

  const loadWhiteboards = async () => {
    try {
      setLoading(true);
      setError(null);

      console.log('📋 Loading whiteboards for household:', householdId);
      const response = await whiteboardAPI.getHouseholdWhiteboards(householdId);
      console.log('📋 Whiteboards response:', response);

      if (response.success) {
        const whiteboardsList = response.data.whiteboards || response.data || [];
        console.log('✅ Setting whiteboards:', whiteboardsList.length, 'whiteboards');
        setWhiteboards(whiteboardsList);
      } else {
        setError(response.message || 'Failed to load whiteboards');
      }
    } catch (err) {
      console.error('Error loading whiteboards:', err);
      setError('Failed to load whiteboards');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateWhiteboard = async (e) => {
    e.preventDefault();

    if (!newWhiteboardName.trim()) {
      toast.warning('Please enter a whiteboard name');
      return;
    }

    try {
      setCreating(true);

      const response = await whiteboardAPI.createWhiteboard({
        household_id: parseInt(householdId),
        name: newWhiteboardName.trim(),
        description: newWhiteboardDescription.trim() || null,
        template_type: 'freeform'
      });

      if (response.success) {
        // Close modal
        setShowCreateModal(false);
        setNewWhiteboardName('');
        setNewWhiteboardDescription('');

        toast.success(`Created: ${newWhiteboardName.trim()}`);
        
        // Navigate to new whiteboard
        onSelectWhiteboard(response.data.whiteboard.id);
      } else {
        toast.error(response.message || 'Failed to create whiteboard');
      }
    } catch (err) {
      console.error('Error creating whiteboard:', err);
      toast.error('Failed to create whiteboard');
    } finally {
      setCreating(false);
    }
  };

  const handleOpenWhiteboard = (whiteboardId) => {
    onSelectWhiteboard(whiteboardId);
  };

  const handleDeleteWhiteboard = async () => {
    if (!deleteConfirm) return;

    try {
      console.log('🗑️ Deleting whiteboard:', deleteConfirm.id);
      const response = await whiteboardAPI.deleteWhiteboard(deleteConfirm.id);
      console.log('🗑️ Delete response:', response);

      if (response.success) {
        toast.success(`Deleted: ${deleteConfirm.name}`);
        setDeleteConfirm(null);
        
        // Reload whiteboards
        console.log('🔄 Reloading whiteboards...');
        await loadWhiteboards();
      } else {
        toast.error(response.message || 'Failed to delete whiteboard');
      }
    } catch (err) {
      console.error('Error deleting whiteboard:', err);
      toast.error('Failed to delete whiteboard');
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    
    return date.toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="whiteboard-navigator">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading whiteboards...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="whiteboard-navigator">
        <div className="error-container">
          <h2>Error</h2>
          <p>{error}</p>
          <button onClick={loadWhiteboards}>Try Again</button>
        </div>
      </div>
    );
  }

  return (
    <div className="whiteboard-navigator embedded">
      {/* Header */}
      <div className="navigator-header embedded">
        <div className="header-left">
          <button className="back-button" onClick={onBack}>
            ← Back to Households
          </button>
          <h1>Household Whiteboards</h1>
        </div>
        <div className="header-right">
          <button className="create-button" onClick={() => setShowCreateModal(true)}>
            + New Whiteboard
          </button>
        </div>
      </div>

      {/* Whiteboards Grid */}
      <div className="whiteboards-container">
        {whiteboards.length === 0 ? (
          <div className="empty-state">
            <h2>No Whiteboards Yet</h2>
            <p>Create your first whiteboard to start organizing meals!</p>
            <button className="create-button-large" onClick={() => setShowCreateModal(true)}>
              Create First Whiteboard
            </button>
          </div>
        ) : (
          <div className="whiteboards-grid">
            {whiteboards.map((wb) => (
              <div
                key={wb.id}
                className="whiteboard-card"
                onClick={() => handleOpenWhiteboard(wb.id)}
              >
                {/* Delete button */}
                <button
                  className="whiteboard-delete-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    setDeleteConfirm({ id: wb.id, name: wb.name });
                  }}
                  title="Delete whiteboard"
                >
                  ×
                </button>

                <div className="card-header">
                  <h3>{wb.name}</h3>
                  <span className="card-badge">Phase 1</span>
                </div>
                {wb.description && (
                  <p className="card-description">{wb.description}</p>
                )}
                <div className="card-footer">
                  <span className="card-meta">
                    Updated {formatDate(wb.updated_at || wb.created_at)}
                  </span>
                  <button className="open-button">Open</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Create New Whiteboard</h2>
              <button className="close-button" onClick={() => setShowCreateModal(false)}>
                ×
              </button>
            </div>

            <form onSubmit={handleCreateWhiteboard}>
              <div className="form-group">
                <label htmlFor="whiteboard-name">Name *</label>
                <input
                  id="whiteboard-name"
                  type="text"
                  placeholder="e.g., Weekly Meal Plan"
                  value={newWhiteboardName}
                  onChange={(e) => setNewWhiteboardName(e.target.value)}
                  autoFocus
                  disabled={creating}
                />
              </div>

              <div className="form-group">
                <label htmlFor="whiteboard-description">Description (optional)</label>
                <textarea
                  id="whiteboard-description"
                  placeholder="What's this whiteboard for?"
                  value={newWhiteboardDescription}
                  onChange={(e) => setNewWhiteboardDescription(e.target.value)}
                  rows={3}
                  disabled={creating}
                />
              </div>

              <div className="modal-actions">
                <button
                  type="button"
                  className="cancel-button"
                  onClick={() => setShowCreateModal(false)}
                  disabled={creating}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="create-button"
                  disabled={creating || !newWhiteboardName.trim()}
                >
                  {creating ? 'Creating...' : 'Create Whiteboard'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deleteConfirm && (
        <div className="modal-overlay" onClick={() => setDeleteConfirm(null)}>
          <div className="modal-content delete-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Delete Whiteboard?</h2>
              <button className="close-button" onClick={() => setDeleteConfirm(null)}>
                ×
              </button>
            </div>

            <div className="modal-body">
              <p>Are you sure you want to delete <strong>{deleteConfirm.name}</strong>?</p>
              <p className="warning-text">This action cannot be undone. All recipes and objects on this whiteboard will be lost.</p>
            </div>

            <div className="modal-actions">
              <button
                className="cancel-button"
                onClick={() => setDeleteConfirm(null)}
              >
                Cancel
              </button>
              <button
                className="delete-confirm-button"
                onClick={handleDeleteWhiteboard}
              >
                Delete Whiteboard
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Wrap with ToastProvider
const WhiteboardNavigatorWithToast = (props) => {
  return (
    <ToastProvider>
      <WhiteboardNavigator {...props} />
    </ToastProvider>
  );
};

export default WhiteboardNavigatorWithToast;
