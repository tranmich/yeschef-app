import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../contexts/AuthContext';
import { api } from '../utils/api';
import './AdminDashboard.css';

const AdminDashboard = () => {
  const { user } = useContext(AuthContext);
  const [adminMode, setAdminMode] = useState(false);
  const [activeTab, setActiveTab] = useState('stats');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState({});
  const [error, setError] = useState('');

  // Check admin access on mount
  useEffect(() => {
    checkAdminAccess();
  }, []);

  const checkAdminAccess = async () => {
    try {
      const response = await fetch('/api/admin/check-access', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      });
      const result = await response.json();
      if (result.success) {
        console.log('✅ Admin access confirmed');
      } else {
        setError('Admin access denied');
      }
    } catch (err) {
      setError('Failed to verify admin access');
    }
  };

  const fetchData = async (endpoint, key) => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`/api/admin/${endpoint}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      });
      const result = await response.json();
      if (result.success) {
        setData(prev => ({ ...prev, [key]: result.data }));
      } else {
        setError(result.error || 'Failed to fetch data');
      }
    } catch (err) {
      setError('Network error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    switch (tab) {
      case 'stats':
        fetchData('stats', 'stats');
        break;
      case 'duplicates':
        fetchData('duplicates', 'duplicates');
        break;
      case 'broken':
        fetchData('broken-recipes', 'broken');
        break;
      case 'templates':
        fetchData('template-analytics', 'templates');
        break;
      case 'logs':
        fetchData('logs', 'logs');
        break;
    }
  };

  // Only show to admin email
  if (!user || user.email !== 'tran.mich@gmail.com') {
    return null;
  }

  return (
    <div className="admin-dashboard">
      {/* Admin Mode Toggle */}
      <div className="admin-header">
        <h1>🔧 Admin Dashboard</h1>
        <button
          className={`admin-toggle ${adminMode ? 'active' : ''}`}
          onClick={() => setAdminMode(!adminMode)}
        >
          {adminMode ? '🔧 Admin ON' : '⚙️ Admin Mode'}
        </button>
      </div>

      {adminMode && (
        <div className="admin-content">
          {/* Navigation Tabs */}
          <div className="admin-tabs">
            <button 
              className={activeTab === 'stats' ? 'active' : ''}
              onClick={() => handleTabChange('stats')}
            >
              📊 Database Stats
            </button>
            <button 
              className={activeTab === 'duplicates' ? 'active' : ''}
              onClick={() => handleTabChange('duplicates')}
            >
              🔍 Find Duplicates
            </button>
            <button 
              className={activeTab === 'broken' ? 'active' : ''}
              onClick={() => handleTabChange('broken')}
            >
              🔧 Broken Recipes
            </button>
            <button 
              className={activeTab === 'templates' ? 'active' : ''}
              onClick={() => handleTabChange('templates')}
            >
              ⭐ Template Analytics
            </button>
            <button 
              className={activeTab === 'logs' ? 'active' : ''}
              onClick={() => handleTabChange('logs')}
            >
              📝 Admin Logs
            </button>
          </div>

          {/* Content Area */}
          <div className="admin-tab-content">
            {error && <div className="admin-error">❌ {error}</div>}
            {loading && <div className="admin-loading">⏳ Loading...</div>}

            {activeTab === 'stats' && data.stats && (
              <DatabaseStats stats={data.stats} />
            )}

            {activeTab === 'duplicates' && data.duplicates && (
              <DuplicateAnalysis duplicates={data.duplicates} />
            )}

            {activeTab === 'broken' && data.broken && (
              <BrokenRecipes broken={data.broken} />
            )}

            {activeTab === 'templates' && data.templates && (
              <TemplateAnalytics templates={data.templates} />
            )}

            {activeTab === 'logs' && data.logs && (
              <AdminLogs logs={data.logs} />
            )}
          </div>
        </div>
      )}
    </div>
  );
};

// Database Statistics Component
const DatabaseStats = ({ stats }) => (
  <div className="database-stats">
    <h2>📊 Database Overview</h2>
    <div className="stats-grid">
      <div className="stat-card">
        <h3>Total Recipes</h3>
        <div className="stat-number">{stats.total_recipes}</div>
      </div>
      <div className="stat-card">
        <h3>Template Recipes</h3>
        <div className="stat-number">{stats.template_recipes}</div>
      </div>
      <div className="stat-card">
        <h3>User Recipes</h3>
        <div className="stat-number">{stats.user_recipes}</div>
      </div>
      <div className="stat-card">
        <h3>Active Users</h3>
        <div className="stat-number">{stats.users_with_recipes}</div>
      </div>
      <div className="stat-card">
        <h3>Template Copies</h3>
        <div className="stat-number">{stats.template_copies}</div>
      </div>
    </div>

    <div className="quality-issues">
      <h3>🔧 Quality Issues</h3>
      <div className="issue-list">
        <div className="issue-item">
          Missing Ingredients: {stats.recipes_missing_ingredients}
        </div>
        <div className="issue-item">
          Missing Instructions: {stats.recipes_missing_instructions}
        </div>
        <div className="issue-item">
          Missing Titles: {stats.recipes_missing_title}
        </div>
      </div>
    </div>

    {stats.duplicate_titles && stats.duplicate_titles.length > 0 && (
      <div className="duplicate-preview">
        <h3>🔍 Duplicate Titles (Top 10)</h3>
        {stats.duplicate_titles.map((dup, index) => (
          <div key={index} className="duplicate-item">
            "{dup.title}" ({dup.count} copies)
          </div>
        ))}
      </div>
    )}
  </div>
);

// Duplicate Analysis Component
const DuplicateAnalysis = ({ duplicates }) => (
  <div className="duplicate-analysis">
    <h2>🔍 Duplicate Recipe Analysis</h2>
    
    <div className="duplicate-summary">
      <div className="summary-stat">
        <strong>Exact Title Matches:</strong> {duplicates.total_exact_duplicates}
      </div>
      <div className="summary-stat">
        <strong>Identical Ingredients:</strong> {duplicates.total_ingredient_duplicates}
      </div>
    </div>

    {duplicates.exact_title_matches && duplicates.exact_title_matches.length > 0 && (
      <div className="exact-matches">
        <h3>📋 Exact Title Matches</h3>
        {duplicates.exact_title_matches.map((group, index) => (
          <div key={index} className="duplicate-group">
            <strong>"{group.title}"</strong> ({group.count} copies)
            <div className="recipe-ids">IDs: {group.recipe_ids.join(', ')}</div>
            <BulkDeleteButton recipeIds={group.recipe_ids} />
          </div>
        ))}
      </div>
    )}
  </div>
);

// Broken Recipes Component
const BrokenRecipes = ({ broken }) => (
  <div className="broken-recipes">
    <h2>🔧 Broken Recipe Analysis</h2>
    
    {broken.missing_fields && broken.missing_fields.length > 0 && (
      <div className="missing-fields">
        <h3>📋 Missing Essential Fields</h3>
        {broken.missing_fields.map((recipe, index) => (
          <div key={index} className="broken-item">
            <strong>ID {recipe.id}:</strong> {recipe.title || 'No Title'} 
            <span className="issue-type">({recipe.issue_type.replace('_', ' ')})</span>
            <RecipeActionButtons recipeId={recipe.id} />
          </div>
        ))}
      </div>
    )}

    {broken.orphaned_copies && broken.orphaned_copies.length > 0 && (
      <div className="orphaned-copies">
        <h3>🔗 Orphaned Template Copies</h3>
        {broken.orphaned_copies.map((recipe, index) => (
          <div key={index} className="broken-item">
            <strong>ID {recipe.id}:</strong> {recipe.title}
            <span className="issue-type">(Template {recipe.template_id} not found)</span>
            <RecipeActionButtons recipeId={recipe.id} />
          </div>
        ))}
      </div>
    )}
  </div>
);

// Template Analytics Component
const TemplateAnalytics = ({ templates }) => (
  <div className="template-analytics">
    <h2>⭐ Template Usage Analytics</h2>
    
    <div className="template-summary">
      <strong>Total Templates:</strong> {templates.total_templates}
    </div>

    {templates.template_stats && templates.template_stats.length > 0 && (
      <div className="template-stats">
        <h3>📊 Template Performance</h3>
        {templates.template_stats.map((template, index) => (
          <div key={index} className="template-item">
            <div className="template-header">
              <strong>{template.title}</strong>
              <span className="template-author">by {template.original_author}</span>
            </div>
            <div className="template-metrics">
              <span>Copies: {template.copy_count}</span>
              <span>Users: {template.unique_users}</span>
              <span>Meal Role: {template.meal_role}</span>
            </div>
            <TemplateActionButtons templateId={template.id} />
          </div>
        ))}
      </div>
    )}
  </div>
);

// Admin Logs Component
const AdminLogs = ({ logs }) => (
  <div className="admin-logs">
    <h2>📝 Recent Admin Actions</h2>
    {logs.map((log, index) => (
      <div key={index} className="log-entry">
        <div className="log-header">
          <span className="log-action">{log.action}</span>
          <span className="log-timestamp">{new Date(log.timestamp).toLocaleString()}</span>
        </div>
        <div className="log-details">
          <span>Target: {log.target_type} {log.target_id}</span>
          <span>By: {log.admin_email}</span>
        </div>
      </div>
    ))}
  </div>
);

// Action Buttons Components
const RecipeActionButtons = ({ recipeId }) => (
  <div className="recipe-actions">
    <button className="admin-btn view" onClick={() => window.open(`/recipe/${recipeId}`, '_blank')}>
      👀 View
    </button>
    <button className="admin-btn delete" onClick={() => deleteRecipe(recipeId)}>
      🗑️ Delete
    </button>
  </div>
);

const TemplateActionButtons = ({ templateId }) => (
  <div className="template-actions">
    <button className="admin-btn demote" onClick={() => demoteTemplate(templateId)}>
      ⬇️ Demote
    </button>
    <button className="admin-btn view" onClick={() => window.open(`/recipe/${templateId}`, '_blank')}>
      👀 View
    </button>
  </div>
);

const BulkDeleteButton = ({ recipeIds }) => {
  const [showConfirm, setShowConfirm] = useState(false);
  const [confirmText, setConfirmText] = useState('');

  const handleBulkDelete = async () => {
    const expectedText = `DELETE ${recipeIds.length} RECIPES FROM LIVE DATABASE`;
    if (confirmText !== expectedText) {
      alert(`Please type exactly: "${expectedText}"`);
      return;
    }

    try {
      const response = await fetch('/api/admin/recipes/bulk-delete/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify({
          recipe_ids: recipeIds,
          confirmation_text: confirmText
        })
      });

      const result = await response.json();
      if (result.success) {
        alert(`✅ Successfully deleted ${result.deleted_count} recipes`);
        window.location.reload(); // Refresh the page
      } else {
        alert(`❌ Error: ${result.error}`);
      }
    } catch (err) {
      alert(`❌ Network error: ${err.message}`);
    }
  };

  return (
    <div className="bulk-delete">
      <button 
        className="admin-btn bulk-delete"
        onClick={() => setShowConfirm(!showConfirm)}
      >
        🗑️ Bulk Delete ({recipeIds.length})
      </button>
      
      {showConfirm && (
        <div className="bulk-delete-confirm">
          <p>⚠️ This will permanently delete {recipeIds.length} recipes from the live database!</p>
          <input
            type="text"
            placeholder={`Type: DELETE ${recipeIds.length} RECIPES FROM LIVE DATABASE`}
            value={confirmText}
            onChange={(e) => setConfirmText(e.target.value)}
            className="confirm-input"
          />
          <div className="confirm-buttons">
            <button onClick={handleBulkDelete} className="admin-btn danger">
              🗑️ Confirm Delete
            </button>
            <button onClick={() => setShowConfirm(false)} className="admin-btn">
              ❌ Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

// Helper functions
const deleteRecipe = async (recipeId) => {
  if (!confirm(`Are you sure you want to delete recipe ${recipeId} from the live database?`)) {
    return;
  }

  try {
    const response = await fetch(`/api/admin/recipes/${recipeId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`
      }
    });

    const result = await response.json();
    if (result.success) {
      alert('✅ Recipe deleted successfully');
      window.location.reload();
    } else {
      alert(`❌ Error: ${result.error}`);
    }
  } catch (err) {
    alert(`❌ Network error: ${err.message}`);
  }
};

const demoteTemplate = async (templateId) => {
  if (!confirm(`Remove template status from recipe ${templateId}?`)) {
    return;
  }

  try {
    const response = await fetch(`/api/admin/recipes/${templateId}/demote`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`
      }
    });

    const result = await response.json();
    if (result.success) {
      alert('✅ Template status removed');
      window.location.reload();
    } else {
      alert(`❌ Error: ${result.error}`);
    }
  } catch (err) {
    alert(`❌ Network error: ${err.message}`);
  }
};

export default AdminDashboard;
