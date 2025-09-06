import React, { useState, useEffect } from 'react';
import { api } from '../utils/api';
import { formatRecipeText } from '../utils/recipeFormatting';
import './AdminDashboard.css';

// Get the correct API base URL for admin endpoints
const getApiBaseUrl = () => {
  // In development, use localhost:5000, in production use the configured API URL
  if (process.env.NODE_ENV === 'development') {
    return 'http://localhost:5000';
  }
  return process.env.REACT_APP_API_URL || 'https://yeschefapp-production.up.railway.app';
};

const API_BASE_URL = getApiBaseUrl();

const AdminDashboard = () => {
  // Debug: Log component mount
  console.log('🔧 AdminDashboard component mounting...');
  
  // Remove dependency on useAuth for now - parent component handles admin check
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
      const token = localStorage.getItem('authToken');
      console.log('🔑 Token from localStorage:', token ? `${token.substring(0, 20)}...` : 'NULL');
      console.log('🌐 API Base URL:', API_BASE_URL);
      
      if (!token) {
        setError('No authentication token found - please log in again');
        return;
      }
      
      const response = await fetch(`${API_BASE_URL}/api/admin/check-access`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      console.log('🔧 Admin check response status:', response.status);
      
      const result = await response.json();
      console.log('🔧 Admin check result:', result);
      
      if (result.success) {
        console.log('✅ Admin access confirmed');
      } else {
        setError('Admin access denied: ' + (result.error || 'Unknown error'));
      }
    } catch (err) {
      console.error('🔧 Admin check error:', err);
      setError('Failed to verify admin access: ' + err.message);
    }
  };

  const fetchData = async (endpoint, key) => {
    setLoading(true);
    setError('');
    try {
      const token = localStorage.getItem('authToken');
      console.log(`🔑 Fetching ${endpoint} with token:`, token ? `${token.substring(0, 20)}...` : 'NULL');
      console.log(`🌐 Fetching from: ${API_BASE_URL}/api/admin/${endpoint}`);
      
      if (!token) {
        setError('No authentication token found - please log in again');
        setLoading(false);
        return;
      }
      
      const response = await fetch(`${API_BASE_URL}/api/admin/${endpoint}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      console.log(`🔧 ${endpoint} response status:`, response.status);
      console.log(`🔧 ${endpoint} response headers:`, response.headers);
      
      const result = await response.json();
      console.log(`🔧 ${endpoint} result:`, result);
      
      if (result.success) {
        setData(prev => ({ ...prev, [key]: result.data }));
      } else {
        setError(result.error || 'Failed to fetch data');
      }
    } catch (err) {
      console.error(`🔧 ${endpoint} error:`, err);
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
      case 'browse':
        fetchData('all-recipes', 'allRecipes');
        break;
      case 'logs':
        fetchData('logs', 'logs');
        break;
    }
  };

  const handleBulkDeleteConfirmation = async (recipeIds, isForceDelete = false) => {
    console.log('🔧 Main handleBulkDeleteConfirmation called with:', recipeIds, typeof recipeIds, 'force:', isForceDelete);
    
    // Ensure recipeIds is always an array
    const recipeIdsArray = Array.isArray(recipeIds) ? recipeIds : [recipeIds];
    console.log('🔧 Converted to array:', recipeIdsArray);
    
    const confirmMessage = isForceDelete 
      ? `🔥 FORCE DELETE: This will permanently delete ${recipeIdsArray.length} recipes, ignoring ALL safety checks!\n\nType: DELETE`
      : `⚠️ This will permanently delete ${recipeIdsArray.length} recipes from the live database!\n\nType: DELETE`;
    
    const confirmText = prompt(confirmMessage);
    const expectedText = `DELETE`;
    
    if (confirmText !== expectedText) {
      alert(`Please type exactly: "${expectedText}"`);
      return;
    }

    try {
      const token = localStorage.getItem('authToken');
      const requestBody = {
        recipe_ids: recipeIdsArray,
        confirmation_text: "DELETE",
        force_delete_templates: isForceDelete
      };
      
      console.log('🔧 Sending bulk delete request:', requestBody);
      
      const response = await fetch(`${API_BASE_URL}/api/admin/recipes/bulk-delete/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(requestBody)
      });

      console.log('🔧 Bulk delete response status:', response.status);
      const result = await response.json();
      console.log('🔧 Bulk delete result:', result);
      
      if (result.errors && result.errors.length > 0) {
        console.log('🔧 Deletion errors:', result.errors);
      }

      if (result.success) {
        alert(`✅ Successfully deleted ${result.deleted_count} recipes`);
        
        // Refresh the data to show updated counts
        switch (activeTab) {
          case 'duplicates':
            fetchData('duplicates', 'duplicates');
            break;
          case 'allRecipes':
            fetchData('all-recipes', 'allRecipes');
            break;
        }
        
      } else {
        alert(`❌ Error: ${result.error}`);
      }
    } catch (err) {
      alert(`❌ Network error: ${err.message}`);
    }
  };

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
            className={activeTab === 'browse' ? 'active' : ''}
            onClick={() => handleTabChange('browse')}
          >
            📚 Browse All Recipes
          </button>
          <button 
            className={activeTab === 'logs' ? 'active' : ''}
            onClick={() => handleTabChange('logs')}
          >
            📝 Admin Logs
          </button>
          <button 
            className="refresh-data-btn"
            onClick={() => handleTabChange(activeTab)}
            title="Refresh current tab data"
          >
            🔄 Refresh Data
          </button>
        </div>          {/* Content Area */}
          <div className="admin-tab-content">
            {error && <div className="admin-error">❌ {error}</div>}
            {loading && <div className="admin-loading">⏳ Loading...</div>}

            {activeTab === 'stats' && data.stats && (
              <DatabaseStats stats={data.stats} />
            )}

            {activeTab === 'duplicates' && data.duplicates && (
              <DuplicateAnalysis 
                duplicates={data.duplicates} 
                handleBulkDeleteConfirmation={handleBulkDeleteConfirmation}
              />
            )}

            {activeTab === 'broken' && data.broken && (
              <BrokenRecipes broken={data.broken} />
            )}

            {activeTab === 'templates' && data.templates && (
              <TemplateAnalytics templates={data.templates} />
            )}

            {activeTab === 'browse' && data.allRecipes && (
              <BrowseAllRecipes recipes={data.allRecipes} />
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
const DuplicateAnalysis = ({ duplicates, handleBulkDeleteConfirmation: onBulkDeleteConfirmation }) => {
  const [selectedRecipes, setSelectedRecipes] = useState(new Set());
  const [expandedRecipes, setExpandedRecipes] = useState(new Set());
  const [expandedGroups, setExpandedGroups] = useState(new Set()); // New: for cascading groups
  const [recipeDetails, setRecipeDetails] = useState({});
  const [loading, setLoading] = useState(false);
  const [forceDelete, setForceDelete] = useState(false);

  const toggleGroupExpansion = (groupIndex) => {
    const newExpanded = new Set(expandedGroups);
    if (newExpanded.has(groupIndex)) {
      newExpanded.delete(groupIndex);
    } else {
      newExpanded.add(groupIndex);
    }
    setExpandedGroups(newExpanded);
  };

  const deleteSelectedRecipes = async () => {
    if (selectedRecipes.size === 0) {
      alert('Please select recipes to delete');
      return;
    }

    const recipeIds = Array.from(selectedRecipes);
    
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_BASE_URL}/api/admin/recipes/bulk-delete/preview`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          recipe_ids: recipeIds
        })
      });

      const preview = await response.json();
      
      if (!preview.success) {
        alert(`❌ Error getting deletion preview: ${preview.error}`);
        return;
      }

      const safeToDelete = Array.isArray(preview.data.safe_to_delete) ? preview.data.safe_to_delete : [];
      const templatesWithCopies = Array.isArray(preview.data.templates_with_copies) ? preview.data.templates_with_copies : [];
      const orphanedCopies = Array.isArray(preview.data.orphaned_copies) ? preview.data.orphaned_copies : [];

      console.log('🔧 Preview data:', { safeToDelete, templatesWithCopies, orphanedCopies });

      // Handle force delete vs normal delete
      if (forceDelete) {
        const finalDeletionList = [...safeToDelete, ...templatesWithCopies];
        if (finalDeletionList.length === 0) {
          alert('No recipes selected for deletion.');
          return;
        }
        
        let confirmMessage = `⚠️ BULK DELETE ANALYSIS:\n\n`;
        confirmMessage += `🔥 FORCE DELETE MODE ENABLED\n`;
        confirmMessage += `⚠️ Will delete ${finalDeletionList.length} recipes, ignoring all safety checks!\n`;
        if (templatesWithCopies.length > 0) {
          confirmMessage += `⚠️ This includes ${templatesWithCopies.length} templates with user copies!\n`;
          confirmMessage += `⚠️ This will break template relationships and may orphan user recipes!\n`;
        }
        
        // Show the analysis but proceed directly to confirmation for force delete
        alert(confirmMessage);
        await onBulkDeleteConfirmation(finalDeletionList, true); // true = force delete
        
        // Clear selections after successful deletion
        setSelectedRecipes(new Set());
        setExpandedRecipes(new Set());
        
      } else {
        // Normal delete - existing safety checks
        if (templatesWithCopies.length > 0) {
          let confirmMessage = `⚠️ BULK DELETE ANALYSIS:\n\n`;
          confirmMessage += `🚫 Cannot delete: ${templatesWithCopies.length} templates with user copies\n`;
          confirmMessage += `Please unselect template recipes, demote them first, or enable Force Delete.`;
          alert(confirmMessage);
          return;
        }

        if (safeToDelete.length === 0) {
          alert('No recipes can be safely deleted from your selection.');
          return;
        }

        // Show the analysis but proceed directly to confirmation
        alert(`⚠️ BULK DELETE ANALYSIS:\n\n✅ Safe to delete: ${safeToDelete.length} recipes\n🗑️ Proceeding will delete ${safeToDelete.length} recipes permanently.`);

        // Proceed with deletion of safe recipes only
        await onBulkDeleteConfirmation(safeToDelete, false); // false = normal delete
        
        // Clear selections after successful deletion
        setSelectedRecipes(new Set());
        setExpandedRecipes(new Set());
      }

    } catch (error) {
      alert(`❌ Error analyzing deletion: ${error.message}`);
    }
  };

  const toggleRecipeSelection = (recipeId) => {
    const newSelected = new Set(selectedRecipes);
    if (newSelected.has(recipeId)) {
      newSelected.delete(recipeId);
    } else {
      newSelected.add(recipeId);
    }
    setSelectedRecipes(newSelected);
  };

  const toggleRecipeExpansion = async (recipeId) => {
    const newExpanded = new Set(expandedRecipes);
    if (newExpanded.has(recipeId)) {
      newExpanded.delete(recipeId);
    } else {
      newExpanded.add(recipeId);
      // Load recipe details if not already loaded
      if (!recipeDetails[recipeId]) {
        await loadRecipeDetails(recipeId);
      }
    }
    setExpandedRecipes(newExpanded);
  };

  const loadRecipeDetails = async (recipeId) => {
    try {
      setLoading(true);
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_BASE_URL}/api/admin/recipes/${recipeId}/details`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      const result = await response.json();
      if (result.success) {
        setRecipeDetails(prev => ({
          ...prev,
          [recipeId]: result.data
        }));
      }
    } catch (error) {
      console.error('Failed to load recipe details:', error);
    } finally {
      setLoading(false);
    }
  };

  const deleteIndividualRecipe = async (recipeId) => {
    // First check if this recipe can be safely deleted
    try {
      const token = localStorage.getItem('authToken');
      const previewResponse = await fetch(`${API_BASE_URL}/api/admin/recipes/bulk-delete/preview`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          recipe_ids: [recipeId]
        })
      });

      const preview = await previewResponse.json();
      
      if (!preview.success) {
        alert(`❌ Error checking recipe: ${preview.error}`);
        return;
      }

      const templatesWithCopies = preview.data.templates_with_copies || [];
      const orphanedCopies = preview.data.orphaned_copies || [];

      if (templatesWithCopies.includes(recipeId)) {
        alert(`🚫 Cannot delete recipe ${recipeId}:\n\nThis is a template recipe with user copies. Deleting it would break users' recipe collections.\n\nTo delete this recipe:\n1. First demote it from template status, or\n2. Delete all user copies first`);
        return;
      }

      let confirmMessage = `Delete recipe ${recipeId}?`;
      if (orphanedCopies.length > 0) {
        confirmMessage = `⚠️ Delete recipe ${recipeId}?\n\nThis will orphan ${orphanedCopies.length} user copies (they'll lose the connection to the original).`;
      }

      if (!window.confirm(confirmMessage)) {
        return;
      }

      const response = await fetch(`${API_BASE_URL}/api/admin/recipes/${recipeId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const result = await response.json();
      if (result.success) {
        console.log(`✅ Recipe ${recipeId} deleted successfully`);
        
        // Remove from selection if it was selected
        setSelectedRecipes(prev => {
          const newSelected = new Set(prev);
          newSelected.delete(recipeId);
          return newSelected;
        });
        
        // Remove from expanded if it was expanded
        setExpandedRecipes(prev => {
          const newExpanded = new Set(prev);
          newExpanded.delete(recipeId);
          return newExpanded;
        });
        
        // Show success message but don't reload
        alert(`✅ Recipe ${recipeId} deleted successfully! Refresh the tab to see updated duplicate analysis.`);
        
      } else {
        alert(`❌ Error: ${result.error}`);
      }
    } catch (err) {
      alert(`❌ Network error: ${err.message}`);
    }
  };

  const bulkDeleteSelected = async () => {
    if (selectedRecipes.size === 0) {
      alert('Please select recipes to delete');
      return;
    }

    const recipeIds = Array.from(selectedRecipes);
    
    // First, get a preview of what will be deleted to check for templates
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_BASE_URL}/api/admin/recipes/bulk-delete/preview`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          recipe_ids: recipeIds
        })
      });

      const preview = await response.json();
      
      if (!preview.success) {
        alert(`❌ Error getting deletion preview: ${preview.error}`);
        return;
      }

      // Show detailed preview before deletion
      const safeToDelete = preview.data.safe_to_delete || [];
      const templatesWithCopies = preview.data.templates_with_copies || [];
      const orphanedCopies = preview.data.orphaned_copies || [];

      console.log('🔧 Preview data:', { safeToDelete, templatesWithCopies, orphanedCopies });

      let confirmMessage = `⚠️ BULK DELETE ANALYSIS:\n\n`;
      
      if (safeToDelete.length > 0) {
        confirmMessage += `✅ Safe to delete: ${safeToDelete.length} recipes\n`;
      }
      
      if (templatesWithCopies.length > 0) {
        confirmMessage += `🚫 Cannot delete: ${templatesWithCopies.length} templates with user copies\n`;
        confirmMessage += `   Template IDs: ${templatesWithCopies.join(', ')}\n`;
      }
      
      if (orphanedCopies.length > 0) {
        confirmMessage += `⚠️ Will orphan: ${orphanedCopies.length} user copies\n`;
      }

      // Handle force delete vs normal delete
      if (forceDelete) {
        const finalDeletionList = [...safeToDelete, ...templatesWithCopies];
        if (finalDeletionList.length === 0) {
          alert('No recipes selected for deletion.');
          return;
        }
        
        confirmMessage += `\n🔥 FORCE DELETE MODE ENABLED\n`;
        confirmMessage += `⚠️ Will delete ${finalDeletionList.length} recipes, ignoring all safety checks!\n`;
        if (templatesWithCopies.length > 0) {
          confirmMessage += `⚠️ This includes ${templatesWithCopies.length} templates with user copies!\n`;
          confirmMessage += `⚠️ This will break template relationships and may orphan user recipes!\n`;
        }
        
        // Show the analysis but proceed directly to confirmation for force delete
        alert(confirmMessage);
        await handleBulkDeleteConfirmation(finalDeletionList, true); // true = force delete
        
      } else {
        // Normal delete - existing safety checks
        if (templatesWithCopies.length > 0) {
          confirmMessage += `\n❌ DELETION BLOCKED: Cannot proceed with templates that have user copies.\n`;
          confirmMessage += `Please unselect template recipes, demote them first, or enable Force Delete.`;
          alert(confirmMessage);
          return;
        }

        if (safeToDelete.length === 0) {
          alert('No recipes can be safely deleted from your selection.');
          return;
        }

        // Show the analysis but proceed directly to confirmation
        alert(`⚠️ BULK DELETE ANALYSIS:\n\n✅ Safe to delete: ${safeToDelete.length} recipes\n${templatesWithCopies.length > 0 ? `🚫 Cannot delete: ${templatesWithCopies.length} templates with user copies\n` : ''}\n🗑️ Proceeding will delete ${safeToDelete.length} recipes permanently.`);

        // Proceed with deletion of safe recipes only
        await handleBulkDeleteConfirmation(safeToDelete, false); // false = normal delete
      }

    } catch (error) {
      alert(`❌ Error analyzing deletion: ${error.message}`);
    }
  };

  const handleBulkDeleteConfirmation = async (recipeIds, isForceDelete = false) => {
    console.log('🔧 handleBulkDeleteConfirmation called with:', recipeIds, typeof recipeIds, 'force:', isForceDelete);
    
    // Ensure recipeIds is always an array
    const recipeIdsArray = Array.isArray(recipeIds) ? recipeIds : [recipeIds];
    console.log('🔧 Converted to array:', recipeIdsArray);
    
    const confirmMessage = isForceDelete 
      ? `🔥 FORCE DELETE: This will permanently delete ${recipeIdsArray.length} recipes, ignoring ALL safety checks!\n\nType: DELETE`
      : `⚠️ This will permanently delete ${recipeIdsArray.length} recipes from the live database!\n\nType: DELETE`;
    
    const confirmText = prompt(confirmMessage);
    const expectedText = `DELETE`;
    
    if (confirmText !== expectedText) {
      alert(`Please type exactly: "${expectedText}"`);
      return;
    }

    try {
      const token = localStorage.getItem('authToken');
      const requestBody = {
        recipe_ids: recipeIdsArray,
        confirmation_text: "DELETE",
        force_delete_templates: isForceDelete
      };
      
      console.log('🔧 Sending bulk delete request:', requestBody);
      
      const response = await fetch(`${API_BASE_URL}/api/admin/recipes/bulk-delete/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(requestBody)
      });

      console.log('🔧 Bulk delete response status:', response.status);
      const result = await response.json();
      console.log('🔧 Bulk delete result:', result);
      
      if (result.errors && result.errors.length > 0) {
        console.log('🔧 Deletion errors:', result.errors);
      }
      if (result.success) {
        alert(`✅ Successfully deleted ${result.deleted_count} recipes`);
        
        // Remove from selections
        const deletedIds = new Set(recipeIdsArray);
        setSelectedRecipes(prevSelected => {
          const newSelected = new Set(prevSelected);
          recipeIdsArray.forEach(id => newSelected.delete(id));
          return newSelected;
        });
        
        // Remove from expanded
        setExpandedRecipes(prevExpanded => {
          const newExpanded = new Set(prevExpanded);
          recipeIdsArray.forEach(id => newExpanded.delete(id));
          return newExpanded;
        });
        
        // Show message but suggest refresh for duplicate analysis update
        alert(`✅ Successfully deleted ${result.deleted_count} recipes! The duplicate analysis will be updated when you refresh this tab.`);
        
      } else {
        alert(`❌ Error: ${result.error}`);
      }
    } catch (err) {
      alert(`❌ Network error: ${err.message}`);
    }
  };

  return (
    <div className="duplicate-analysis">
      <h2>🔍 Duplicate Recipe Analysis</h2>
      
      <div className="duplicate-summary">
        <div className="summary-stat">
          <strong>Exact Title Matches:</strong> {duplicates.total_exact_duplicates}
        </div>
        <div className="summary-stat">
          <strong>Identical Ingredients:</strong> {duplicates.total_ingredient_duplicates}
        </div>
        {selectedRecipes.size > 0 && (
          <div className="selection-summary">
            <strong>{selectedRecipes.size} recipes selected</strong>
            <div className="bulk-delete-options">
              <label className="force-delete-checkbox">
                <input
                  type="checkbox"
                  checked={forceDelete}
                  onChange={(e) => setForceDelete(e.target.checked)}
                />
                🔥 Force Delete (ignores all safety checks)
              </label>
              <button 
                className="bulk-action-btn bulk-delete"
                onClick={deleteSelectedRecipes}
              >
                🗑️ Delete Selected ({selectedRecipes.size})
              </button>
            </div>
          </div>
        )}
      </div>

      {duplicates.exact_title_matches && duplicates.exact_title_matches.length > 0 && (
        <div className="exact-matches">
          <h3>📋 Exact Title Matches</h3>
          {duplicates.exact_title_matches.map((group, groupIndex) => (
            <div key={groupIndex} className="duplicate-group">
              <div className="group-header" onClick={() => toggleGroupExpansion(groupIndex)}>
                <div className="group-title-info">
                  <strong>"{group.title}"</strong> 
                  <span className="group-count">({group.count} copies)</span>
                  <button className="expand-group-btn">
                    {expandedGroups.has(groupIndex) ? '🔽 Hide IDs' : '▶️ Show IDs'}
                  </button>
                </div>
              </div>
              
              {expandedGroups.has(groupIndex) && (
                <div className="compact-recipe-list">
                  {group.recipe_ids.map((recipeId, index) => (
                    <div key={recipeId} className="compact-recipe-item">
                      <input
                        type="checkbox"
                        checked={selectedRecipes.has(recipeId)}
                        onChange={() => toggleRecipeSelection(recipeId)}
                        className="recipe-checkbox"
                      />
                      <span className="recipe-id">ID: {recipeId}</span>
                      {recipeDetails[recipeId] && (
                        <span className="recipe-badges">
                          {recipeDetails[recipeId].is_template && (
                            <span className="badge template-badge">⭐</span>
                          )}
                          {recipeDetails[recipeId].template_id && (
                            <span className="badge copy-badge">📄</span>
                          )}
                        </span>
                      )}
                      <button
                        className="compact-expand-btn"
                        onClick={() => toggleRecipeExpansion(recipeId)}
                      >
                        {expandedRecipes.has(recipeId) ? '📖' : '👀'}
                      </button>
                      <button
                        className="compact-delete-btn"
                        onClick={() => deleteIndividualRecipe(recipeId)}
                        title="Delete this recipe"
                      >
                        🗑️
                      </button>

                      {expandedRecipes.has(recipeId) && (
                        <div className="compact-recipe-details">
                          {loading && <div className="loading">Loading...</div>}
                          {recipeDetails[recipeId] && (
                            <RecipeDetailView 
                              recipe={recipeDetails[recipeId]} 
                              recipeId={recipeId}
                              onUpdate={() => loadRecipeDetails(recipeId)}
                            />
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

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

// Browse All Recipes Component
const BrowseAllRecipes = ({ recipes }) => {
  const [selectedRecipes, setSelectedRecipes] = useState(new Set());
  const [expandedRecipes, setExpandedRecipes] = useState(new Set());
  const [recipeDetails, setRecipeDetails] = useState({});
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all'); // all, templates, copies, standalone
  const [currentPage, setCurrentPage] = useState(1);
  const [totalRecipes, setTotalRecipes] = useState(0);
  const [allRecipes, setAllRecipes] = useState(recipes || []);
  const [forceDelete, setForceDelete] = useState(false);
  const recipesPerPage = 200; // Increased from 50 to 200 for better admin browsing

  // Load recipes with pagination
  const loadRecipes = async (page = 1, search = '', filter = 'all') => {
    try {
      setLoading(true);
      const offset = (page - 1) * recipesPerPage;
      const token = localStorage.getItem('authToken');
      
      let url = `${API_BASE_URL}/api/admin/all-recipes?limit=${recipesPerPage}&offset=${offset}`;
      if (search) {
        url += `&search=${encodeURIComponent(search)}`;
      }
      if (filter !== 'all') {
        url += `&filter=${filter}`;
      }

      console.log(`🔧 Loading recipes: page ${page}, search: "${search}", filter: ${filter}`);
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      const result = await response.json();
      if (result.success) {
        setAllRecipes(result.data);
        setTotalRecipes(result.total_count);
        setCurrentPage(page);
        console.log(`✅ Loaded ${result.data.length} recipes, total: ${result.total_count}`);
      } else {
        console.error('Failed to load recipes:', result.error);
      }
    } catch (error) {
      console.error('Error loading recipes:', error);
    } finally {
      setLoading(false);
    }
  };

  // Load initial recipes
  useEffect(() => {
    loadRecipes(1, searchTerm, filterType);
  }, []);

  // Handle search with debouncing
  useEffect(() => {
    const delayedSearch = setTimeout(() => {
      if (currentPage === 1) {
        loadRecipes(1, searchTerm, filterType);
      } else {
        setCurrentPage(1);
        loadRecipes(1, searchTerm, filterType);
      }
    }, 500);

    return () => clearTimeout(delayedSearch);
  }, [searchTerm]);

  // Handle filter change
  useEffect(() => {
    setCurrentPage(1);
    loadRecipes(1, searchTerm, filterType);
  }, [filterType]);

  const totalPages = Math.ceil(totalRecipes / recipesPerPage);

  const goToPage = (page) => {
    if (page >= 1 && page <= totalPages) {
      loadRecipes(page, searchTerm, filterType);
    }
  };

  const toggleRecipeSelection = (recipeId) => {
    const newSelected = new Set(selectedRecipes);
    if (newSelected.has(recipeId)) {
      newSelected.delete(recipeId);
    } else {
      newSelected.add(recipeId);
    }
    setSelectedRecipes(newSelected);
  };

  const selectAllOnPage = () => {
    const newSelected = new Set(selectedRecipes);
    allRecipes.forEach(recipe => newSelected.add(recipe.id));
    setSelectedRecipes(newSelected);
  };

  const deselectAllOnPage = () => {
    const newSelected = new Set(selectedRecipes);
    allRecipes.forEach(recipe => newSelected.delete(recipe.id));
    setSelectedRecipes(newSelected);
  };

  const toggleRecipeExpansion = async (recipeId) => {
    const newExpanded = new Set(expandedRecipes);
    if (newExpanded.has(recipeId)) {
      newExpanded.delete(recipeId);
    } else {
      newExpanded.add(recipeId);
      if (!recipeDetails[recipeId]) {
        await loadRecipeDetails(recipeId);
      }
    }
    setExpandedRecipes(newExpanded);
  };

  const loadRecipeDetails = async (recipeId) => {
    try {
      setLoading(true);
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_BASE_URL}/api/admin/recipes/${recipeId}/details`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      const result = await response.json();
      if (result.success) {
        setRecipeDetails(prev => ({
          ...prev,
          [recipeId]: result.data
        }));
      }
    } catch (error) {
      console.error('Failed to load recipe details:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleTemplateStatus = async (recipeId, isCurrentlyTemplate) => {
    try {
      const token = localStorage.getItem('authToken');
      const endpoint = isCurrentlyTemplate ? 'demote' : 'promote';
      const response = await fetch(`${API_BASE_URL}/api/admin/recipes/${recipeId}/${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({})
      });

      const result = await response.json();
      if (result.success) {
        console.log(`✅ Recipe ${recipeId} ${endpoint}d successfully`);
        
        // Update the recipe in the current list instead of full reload
        setAllRecipes(prevRecipes => 
          prevRecipes.map(recipe => 
            recipe.id === recipeId 
              ? { ...recipe, is_template: !isCurrentlyTemplate }
              : recipe
          )
        );
        
        // Also update details if expanded
        if (expandedRecipes.has(recipeId)) {
          await loadRecipeDetails(recipeId);
        }
        
        // Show success message
        alert(`✅ Recipe ${recipeId} ${isCurrentlyTemplate ? 'removed from template collection' : 'added to template collection'} successfully!`);
      } else {
        alert(`❌ Error: ${result.error}`);
      }
    } catch (err) {
      alert(`❌ Network error: ${err.message}`);
    }
  };

  const deleteSelectedRecipes = async () => {
    if (selectedRecipes.size === 0) {
      alert('Please select recipes to delete');
      return;
    }

    const recipeIds = Array.from(selectedRecipes);
    
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_BASE_URL}/api/admin/recipes/bulk-delete/preview`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          recipe_ids: recipeIds
        })
      });

      const preview = await response.json();
      
      if (!preview.success) {
        alert(`❌ Error getting deletion preview: ${preview.error}`);
        return;
      }

      const safeToDelete = preview.data.safe_to_delete || [];
      const templatesWithCopies = preview.data.templates_with_copies || [];

      let confirmMessage = `⚠️ BULK DELETE ANALYSIS:\n\n`;
      
      if (safeToDelete.length > 0) {
        confirmMessage += `✅ Safe to delete: ${safeToDelete.length} recipes\n`;
      }
      
      if (templatesWithCopies.length > 0) {
        confirmMessage += `🚫 Cannot delete: ${templatesWithCopies.length} templates with user copies\n`;
      }

      if (templatesWithCopies.length > 0) {
        confirmMessage += `\n❌ DELETION BLOCKED: Cannot proceed with templates that have user copies.`;
        alert(confirmMessage);
        return;
      }

      if (safeToDelete.length === 0) {
        alert('No recipes can be safely deleted from your selection.');
        return;
      }

      confirmMessage += `\nType: DELETE`;

      const confirmText = prompt(confirmMessage);
      const expectedText = `DELETE`;
      
      if (confirmText !== expectedText) {
        alert(`Please type exactly: "${expectedText}"`);
        return;
      }

      // Execute deletion
      const deleteResponse = await fetch(`${API_BASE_URL}/api/admin/recipes/bulk-delete/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          recipe_ids: safeToDelete,
          confirmation_text: "DELETE"
        })
      });

      const deleteResult = await deleteResponse.json();
      if (deleteResult.success) {
        alert(`✅ Successfully deleted ${deleteResult.deleted_count} recipes`);
        
        // Remove deleted recipes from current list instead of full reload
        const deletedIds = new Set(safeToDelete);
        setAllRecipes(prevRecipes => 
          prevRecipes.filter(recipe => !deletedIds.has(recipe.id))
        );
        
        // Update total count
        setTotalRecipes(prev => prev - deleteResult.deleted_count);
        
        // Clear selections for deleted recipes
        setSelectedRecipes(prevSelected => {
          const newSelected = new Set(prevSelected);
          safeToDelete.forEach(id => newSelected.delete(id));
          return newSelected;
        });
        
        // Clear expanded recipes for deleted ones
        setExpandedRecipes(prevExpanded => {
          const newExpanded = new Set(prevExpanded);
          safeToDelete.forEach(id => newExpanded.delete(id));
          return newExpanded;
        });
        
        // If current page is now empty, go to previous page
        const remainingOnPage = allRecipes.length - deleteResult.deleted_count;
        if (remainingOnPage === 0 && currentPage > 1) {
          goToPage(currentPage - 1);
        }
        
      } else {
        alert(`❌ Error: ${deleteResult.error}`);
      }

    } catch (error) {
      alert(`❌ Error analyzing deletion: ${error.message}`);
    }
  };

  return (
    <div className="browse-all-recipes">
      <h2>📚 Browse All Recipes</h2>
      
      <div className="browse-controls">
        <div className="search-controls">
          <input
            type="text"
            placeholder="Search recipes by title, ingredients, or author..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Recipes</option>
            <option value="templates">Templates Only</option>
            <option value="copies">User Copies Only</option>
            <option value="standalone">Standalone Recipes</option>
          </select>
        </div>
        
        <div className="pagination-controls">
          <div className="pagination-info">
            <span>
              Showing {((currentPage - 1) * recipesPerPage) + 1} - {Math.min(currentPage * recipesPerPage, totalRecipes)} of {totalRecipes} recipes
            </span>
            <span>Page {currentPage} of {totalPages}</span>
          </div>
          
          <div className="pagination-buttons">
            <button 
              onClick={() => goToPage(1)}
              disabled={currentPage === 1}
              className="pagination-btn"
            >
              ⏮️ First
            </button>
            <button 
              onClick={() => goToPage(currentPage - 1)}
              disabled={currentPage === 1}
              className="pagination-btn"
            >
              ⬅️ Prev
            </button>
            <button 
              onClick={() => goToPage(currentPage + 1)}
              disabled={currentPage === totalPages}
              className="pagination-btn"
            >
              Next ➡️
            </button>
            <button 
              onClick={() => goToPage(totalPages)}
              disabled={currentPage === totalPages}
              className="pagination-btn"
            >
              Last ⏭️
            </button>
          </div>
        </div>
        
        <div className="selection-controls">
          <div className="selection-actions">
            <button onClick={selectAllOnPage} className="select-btn select-all">
              ☑️ Select All on Page
            </button>
            <button onClick={deselectAllOnPage} className="select-btn deselect-all">
              ☐ Deselect All on Page
            </button>
          </div>
          
          {selectedRecipes.size > 0 && (
            <div className="selection-summary">
              <strong>{selectedRecipes.size} recipes selected</strong>
              <button 
                className="bulk-action-btn bulk-delete"
                onClick={deleteSelectedRecipes}
              >
                🗑️ Delete Selected ({selectedRecipes.size})
              </button>
            </div>
          )}
        </div>
      </div>

      {loading && <div className="loading-indicator">🔄 Loading recipes...</div>}

      <div className="recipe-list">
        {allRecipes.map((recipe) => (
          <div key={recipe.id} className="recipe-item">
            <div className="recipe-row">
              <div className="recipe-controls">
                <input
                  type="checkbox"
                  checked={selectedRecipes.has(recipe.id)}
                  onChange={() => toggleRecipeSelection(recipe.id)}
                  className="recipe-checkbox"
                />
                <div className="recipe-info">
                  <span className="recipe-id">ID: {recipe.id}</span>
                  <span className="recipe-title">{recipe.title}</span>
                  <div className="recipe-badges">
                    {recipe.is_template && (
                      <span className="badge template-badge">⭐ Template</span>
                    )}
                    {recipe.template_id && (
                      <span className="badge copy-badge">📄 Copy of {recipe.template_id}</span>
                    )}
                    {recipe.user_id && (
                      <span className="badge user-badge">👤 User: {recipe.user_id}</span>
                    )}
                  </div>
                </div>
                <div className="recipe-actions">
                  <button
                    className="expand-btn"
                    onClick={() => toggleRecipeExpansion(recipe.id)}
                  >
                    {expandedRecipes.has(recipe.id) ? '📖 Hide Details' : '👀 View Details'}
                  </button>
                  <button
                    className={`template-btn ${recipe.is_template ? 'demote' : 'promote'}`}
                    onClick={() => toggleTemplateStatus(recipe.id, recipe.is_template)}
                  >
                    {recipe.is_template ? '⬇️ Remove from Template' : '➕ Add to Template'}
                  </button>
                </div>
              </div>

              {expandedRecipes.has(recipe.id) && (
                <div className="recipe-details">
                  {loading && <div className="loading">Loading recipe details...</div>}
                  {recipeDetails[recipe.id] && (
                    <RecipeDetailView 
                      recipe={recipeDetails[recipe.id]} 
                      recipeId={recipe.id}
                      onUpdate={() => loadRecipeDetails(recipe.id)}
                    />
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
const RecipeDetailView = ({ recipe, recipeId, onUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedRecipe, setEditedRecipe] = useState(recipe);

  const saveRecipe = async () => {
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_BASE_URL}/api/recipes/${recipeId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(editedRecipe)
      });

      const result = await response.json();
      if (result.success) {
        console.log('✅ Recipe updated successfully');
        setIsEditing(false);
        onUpdate(); // Refresh the recipe details
      } else {
        alert(`❌ Error updating recipe: ${result.error}`);
      }
    } catch (err) {
      alert(`❌ Network error: ${err.message}`);
    }
  };

  const cancelEdit = () => {
    setEditedRecipe(recipe);
    setIsEditing(false);
  };

  return (
    <div className="recipe-detail-view">
      <div className="recipe-detail-header">
        <h4>📋 Recipe Details</h4>
        <div className="recipe-actions">
          {!isEditing ? (
            <button 
              className="edit-btn"
              onClick={() => setIsEditing(true)}
            >
              ✏️ Edit
            </button>
          ) : (
            <>
              <button 
                className="save-btn"
                onClick={saveRecipe}
              >
                💾 Save
              </button>
              <button 
                className="cancel-btn"
                onClick={cancelEdit}
              >
                ❌ Cancel
              </button>
            </>
          )}
        </div>
      </div>

      <div className="recipe-fields">
        <div className="field-group">
          <label>Title:</label>
          {isEditing ? (
            <input
              type="text"
              value={editedRecipe.title || ''}
              onChange={(e) => setEditedRecipe({...editedRecipe, title: e.target.value})}
              className="edit-input"
            />
          ) : (
            <span className="field-value">{recipe.title || 'No title'}</span>
          )}
        </div>

        <div className="field-group">
          <label>Ingredients:</label>
          {isEditing ? (
            <textarea
              value={editedRecipe.ingredients || ''}
              onChange={(e) => setEditedRecipe({...editedRecipe, ingredients: e.target.value})}
              className="edit-textarea"
              rows="4"
            />
          ) : (
            <div className="field-value ingredients">
              {recipe.ingredients ? (
                recipe.ingredients.split('\n').map((ingredient, i) => (
                  <div key={i} className="ingredient-line">• {ingredient}</div>
                ))
              ) : (
                'No ingredients'
              )}
            </div>
          )}
        </div>

        <div className="field-group">
          <label>Instructions:</label>
          {isEditing ? (
            <textarea
              value={editedRecipe.instructions || ''}
              onChange={(e) => setEditedRecipe({...editedRecipe, instructions: e.target.value})}
              className="edit-textarea"
              rows="6"
            />
          ) : (
            <div className="field-value instructions">
              {recipe.instructions ? (
                recipe.instructions.split('\n').map((step, i) => (
                  <div key={i} className="instruction-step">{i + 1}. {step}</div>
                ))
              ) : (
                'No instructions'
              )}
            </div>
          )}
        </div>

        <div className="recipe-metadata">
          <div className="metadata-item">
            <strong>Time:</strong> {formatRecipeText.formatTime(recipe.cooking_time || recipe.prep_time || recipe.cook_time) || 'Not specified'}
          </div>
          <div className="metadata-item">
            <strong>Servings:</strong> {formatRecipeText.formatServings(recipe.servings) || 'Not specified'}
          </div>
          <div className="metadata-item">
            <strong>Difficulty:</strong> {formatRecipeText.formatDifficulty(recipe.difficulty) || 'Not specified'}
          </div>
          <div className="metadata-item">
            <strong>Cuisine:</strong> {formatRecipeText.formatCuisineType(recipe.cuisine_type) || 'Not specified'}
          </div>
          <div className="metadata-item">
            <strong>Meal Role:</strong> {recipe.meal_role || 'Not specified'}
          </div>
          {recipe.is_template && (
            <div className="metadata-item template-badge">
              ⭐ Template Recipe
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
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
      const response = await fetch(`${API_BASE_URL}/api/admin/recipes/bulk-delete/execute`, {
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
        alert(`✅ Successfully deleted ${result.deleted_count} recipes! Use "Refresh Data" to see updated data.`);
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
  if (!window.confirm(`Are you sure you want to delete recipe ${recipeId} from the live database?`)) {
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/admin/recipes/${recipeId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`
      }
    });

    const result = await response.json();
    if (result.success) {
      alert('✅ Recipe deleted successfully! Use "Refresh Data" to see updated data.');
    } else {
      alert(`❌ Error: ${result.error}`);
    }
  } catch (err) {
    alert(`❌ Network error: ${err.message}`);
  }
};

const demoteTemplate = async (templateId) => {
  if (!window.confirm(`Remove template status from recipe ${templateId}?`)) {
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/admin/recipes/${templateId}/demote`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`
      }
    });

    const result = await response.json();
    if (result.success) {
      alert('✅ Template status removed successfully! Use "Refresh Data" to see updated template analytics.');
    } else {
      alert(`❌ Error: ${result.error}`);
    }
  } catch (err) {
    alert(`❌ Network error: ${err.message}`);
  }
};

export default AdminDashboard;
