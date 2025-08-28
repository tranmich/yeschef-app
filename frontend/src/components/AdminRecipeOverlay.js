import React, { useState, useContext } from 'react';
import { AuthContext } from '../contexts/AuthContext';
import './AdminRecipeOverlay.css';

const AdminRecipeOverlay = ({ recipe, adminMode, onUpdate }) => {
  const { user } = useContext(AuthContext);
  const [loading, setLoading] = useState(false);

  // Only show to admin in admin mode
  if (!adminMode || !user || user.email !== 'tran.mich@gmail.com') {
    return null;
  }

  const promoteToTemplate = async () => {
    if (!confirm(`Promote "${recipe.title}" to default template? This will make it available to all new users.`)) {
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`/api/admin/recipes/${recipe.id}/promote`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify({
          original_author: 'Me Hungie Team'
        })
      });

      const result = await response.json();
      if (result.success) {
        alert('✅ Recipe promoted to template!');
        if (onUpdate) onUpdate();
      } else {
        alert(`❌ Error: ${result.error}`);
      }
    } catch (err) {
      alert(`❌ Network error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const removeFromTemplate = async () => {
    if (!confirm(`Remove "${recipe.title}" from default templates? New users will no longer get this recipe.`)) {
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`/api/admin/recipes/${recipe.id}/demote`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      });

      const result = await response.json();
      if (result.success) {
        alert('✅ Template status removed!');
        if (onUpdate) onUpdate();
      } else {
        alert(`❌ Error: ${result.error}`);
      }
    } catch (err) {
      alert(`❌ Network error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const deleteRecipe = async () => {
    const confirmText = `DELETE RECIPE ${recipe.id} FROM LIVE DATABASE`;
    const userInput = prompt(`⚠️ This will permanently delete "${recipe.title}" from the live database.\n\nType "${confirmText}" to confirm:`);
    
    if (userInput !== confirmText) {
      alert('Deletion cancelled - confirmation text did not match.');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`/api/admin/recipes/${recipe.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      });

      const result = await response.json();
      if (result.success) {
        alert('✅ Recipe deleted successfully!');
        if (onUpdate) onUpdate();
      } else {
        alert(`❌ Error: ${result.error}`);
      }
    } catch (err) {
      alert(`❌ Network error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const openRawEditor = () => {
    // Open admin dashboard in new tab focused on this recipe
    window.open(`/admin?recipe=${recipe.id}`, '_blank');
  };

  return (
    <div className="admin-overlay" onClick={(e) => e.stopPropagation()}>
      <div className="admin-actions">
        {!recipe.is_template ? (
          <button 
            className="admin-btn promote" 
            onClick={promoteToTemplate}
            disabled={loading}
            title="Make this recipe a default template for new users"
          >
            ⭐ Make Default
          </button>
        ) : (
          <button 
            className="admin-btn remove-template" 
            onClick={removeFromTemplate}
            disabled={loading}
            title="Remove from default templates"
          >
            ❌ Remove Default
          </button>
        )}
        
        <button 
          className="admin-btn delete" 
          onClick={deleteRecipe}
          disabled={loading}
          title="Permanently delete this recipe"
        >
          🗑️ Delete Recipe
        </button>
        
        <button 
          className="admin-btn edit-raw" 
          onClick={openRawEditor}
          title="Open detailed admin view"
        >
          📝 Admin View
        </button>
      </div>
      
      <div className="admin-info">
        <span className={`template-status ${recipe.is_template ? 'is-template' : ''}`}>
          {recipe.is_template ? '⭐ DEFAULT' : '👤 USER'}
        </span>
        <span className="recipe-id">ID: {recipe.id}</span>
        {recipe.copy_count !== undefined && (
          <span className="usage-count">Copies: {recipe.copy_count}</span>
        )}
        {recipe.owner_email && (
          <span className="owner-info">Owner: {recipe.owner_email}</span>
        )}
      </div>
      
      {loading && (
        <div className="admin-loading-overlay">
          <div className="admin-spinner">⏳</div>
        </div>
      )}
    </div>
  );
};

export default AdminRecipeOverlay;
