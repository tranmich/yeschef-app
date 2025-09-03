import React, { useState, useEffect } from 'react';
import './GroceryListManager.css';
import GroceryListGenerator from './GroceryListGenerator';
import { getApiUrl } from '../utils/api';

const GroceryListManager = ({ isVisible, onClose, currentMealPlanRecipes = [] }) => {
    const [savedLists, setSavedLists] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [selectedList, setSelectedList] = useState(null);
    const [showCurrentList, setShowCurrentList] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        if (isVisible) {
            loadSavedLists();
        }
    }, [isVisible]);

    const loadSavedLists = async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await fetch(`${getApiUrl()}/api/grocery-lists`);
            const data = await response.json();

            if (data.success) {
                setSavedLists(data.grocery_lists);
            } else {
                setError(data.error || 'Failed to load grocery lists');
            }
        } catch (err) {
            setError('Network error: ' + err.message);
        } finally {
            setLoading(false);
        }
    };

    const deleteList = async (listId, listName) => {
        if (!window.confirm(`Are you sure you want to delete "${listName}"?`)) {
            return;
        }

        try {
            const response = await fetch(`${getApiUrl()}/api/grocery-lists/${listId}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (data.success) {
                setSavedLists(prev => prev.filter(list => list.id !== listId));
                alert(`"${listName}" deleted successfully`);
            } else {
                alert('Failed to delete list: ' + data.error);
            }
        } catch (err) {
            alert('Network error: ' + err.message);
        }
    };

    const loadListDetails = async (listId) => {
        try {
            const response = await fetch(`${getApiUrl()}/api/grocery-lists/${listId}`);
            const data = await response.json();

            if (data.success) {
                setSelectedList(data.grocery_list);
            } else {
                alert('Failed to load list: ' + data.error);
            }
        } catch (err) {
            alert('Network error: ' + err.message);
        }
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const filteredLists = savedLists.filter(list =>
        list.list_name.toLowerCase().includes(searchTerm.toLowerCase())
    );

    if (!isVisible) return null;

    // Show selected list details
    if (selectedList) {
        return (
            <GroceryListGenerator
                recipeIds={selectedList.recipe_ids || []}
                savedListData={selectedList}
                onClose={() => setSelectedList(null)}
                onSave={(updatedData) => {
                    // Handle saving updates to existing list
                    setSelectedList(null);
                    loadSavedLists(); // Reload the list
                }}
            />
        );
    }

    // Show current meal plan grocery list
    if (showCurrentList) {
        return (
            <GroceryListGenerator
                recipeIds={currentMealPlanRecipes}
                onClose={() => setShowCurrentList(false)}
                onSave={(savedData) => {
                    setShowCurrentList(false);
                    loadSavedLists(); // Reload to show the new saved list
                }}
            />
        );
    }

    return (
        <div className="grocery-list-manager-modal">
            <div className="grocery-list-manager-content">
                {/* Header */}
                <div className="grocery-list-manager-header">
                    <h2>🛒 Grocery List Manager</h2>
                    <button onClick={onClose} className="close-btn">❌</button>
                </div>

                {/* Current List Section */}
                <div className="current-list-section">
                    <div className="section-title">
                        <h3>📋 Current Meal Plan List</h3>
                        <span className="recipe-count">
                            {currentMealPlanRecipes.length} recipe{currentMealPlanRecipes.length !== 1 ? 's' : ''}
                        </span>
                    </div>
                    {currentMealPlanRecipes.length > 0 ? (
                        <button
                            className="open-current-list-btn"
                            onClick={() => setShowCurrentList(true)}
                        >
                            📝 Open Current List
                        </button>
                    ) : (
                        <p className="no-current-list">
                            Add recipes to your meal planner to create a grocery list
                        </p>
                    )}
                </div>

                {/* Saved Lists Section */}
                <div className="saved-lists-section">
                    <div className="section-header">
                        <h3>💾 Saved Grocery Lists</h3>
                        <div className="list-controls">
                            <input
                                type="text"
                                placeholder="Search lists..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="search-input"
                            />
                            <button
                                onClick={loadSavedLists}
                                className="refresh-btn"
                                title="Refresh lists"
                            >
                                🔄
                            </button>
                        </div>
                    </div>

                    {loading && (
                        <div className="loading-state">
                            <p>📋 Loading your grocery lists...</p>
                        </div>
                    )}

                    {error && (
                        <div className="error-state">
                            <p>❌ {error}</p>
                            <button onClick={loadSavedLists} className="retry-btn">
                                🔄 Retry
                            </button>
                        </div>
                    )}

                    {!loading && !error && (
                        <div className="lists-grid">
                            {filteredLists.length === 0 ? (
                                <div className="no-lists">
                                    <p>📝 No saved grocery lists yet</p>
                                    <p className="help-text">
                                        Create grocery lists from your meal planner and save them for future use!
                                    </p>
                                </div>
                            ) : (
                                filteredLists.map(list => (
                                    <div key={list.id} className="list-card">
                                        <div className="list-card-header">
                                            <h4 className="list-name">{list.list_name}</h4>
                                            <button
                                                className="delete-btn"
                                                onClick={() => deleteList(list.id, list.list_name)}
                                                title="Delete list"
                                            >
                                                🗑️
                                            </button>
                                        </div>
                                        
                                        <div className="list-stats">
                                            <span className="item-count">
                                                📊 {list.item_count || 0} items
                                            </span>
                                            {list.recipe_ids && list.recipe_ids.length > 0 && (
                                                <span className="recipe-count">
                                                    🍳 {list.recipe_ids.length} recipe{list.recipe_ids.length !== 1 ? 's' : ''}
                                                </span>
                                            )}
                                        </div>

                                        <div className="list-dates">
                                            <div className="date-info">
                                                <small>Created: {formatDate(list.created_at)}</small>
                                            </div>
                                            {list.updated_at !== list.created_at && (
                                                <div className="date-info">
                                                    <small>Updated: {formatDate(list.updated_at)}</small>
                                                </div>
                                            )}
                                        </div>

                                        <div className="list-actions">
                                            <button
                                                className="open-list-btn"
                                                onClick={() => loadListDetails(list.id)}
                                            >
                                                📝 Open & Edit
                                            </button>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    )}
                </div>

                {/* Help Section */}
                <div className="help-section">
                    <h4>💡 How to use Grocery Lists:</h4>
                    <ul>
                        <li>📋 Create lists from your meal planner</li>
                        <li>💾 Save lists with custom names</li>
                        <li>✏️ Edit and update saved lists</li>
                        <li>🔄 Reuse lists for similar shopping trips</li>
                        <li>📱 Export to Google Keep for mobile shopping</li>
                    </ul>
                </div>
            </div>
        </div>
    );
};

export default GroceryListManager;
