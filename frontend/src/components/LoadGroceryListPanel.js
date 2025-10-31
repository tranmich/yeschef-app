import React, { useState, useEffect } from 'react';
import './LoadGroceryListPanel.css';
import { getApiUrl } from '../utils/api';
import { useAuth } from '../contexts/AuthContext';

const LoadGroceryListPanel = ({ isOpen, onClose, onLoadList }) => {
    const { token } = useAuth();
    const [savedLists, setSavedLists] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        if (isOpen) {
            loadSavedLists();
        }
    }, [isOpen]);

    const loadSavedLists = async () => {
        setLoading(true);
        setError(null);

        try {
            const headers = {
                'Content-Type': 'application/json'
            };
            
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }

            const response = await fetch(`${getApiUrl()}/api/grocery-lists`, {
                headers
            });
            const data = await response.json();

            if (data.success) {
                setSavedLists(data.grocery_lists || []);
            } else {
                setError(data.error || 'Failed to load grocery lists');
            }
        } catch (err) {
            setError('Network error: ' + err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleLoadList = async (listId) => {
        try {
            const headers = {
                'Content-Type': 'application/json'
            };
            
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }

            const response = await fetch(`${getApiUrl()}/api/grocery-lists/${listId}`, {
                headers
            });
            const data = await response.json();

            if (data.success) {
                onLoadList(data.grocery_list);
                onClose();
            } else {
                alert('Failed to load list: ' + data.error);
            }
        } catch (err) {
            alert('Network error: ' + err.message);
        }
    };

    const handleDeleteList = async (listId, listName, e) => {
        e.stopPropagation(); // Prevent triggering load
        
        if (!window.confirm(`Are you sure you want to delete "${listName}"?`)) {
            return;
        }

        try {
            const headers = {
                'Content-Type': 'application/json'
            };
            
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }

            const response = await fetch(`${getApiUrl()}/api/grocery-lists/${listId}`, {
                method: 'DELETE',
                headers
            });

            const data = await response.json();

            if (data.success) {
                setSavedLists(prev => prev.filter(list => list.id !== listId));
            } else {
                alert('Failed to delete list: ' + data.error);
            }
        } catch (err) {
            alert('Network error: ' + err.message);
        }
    };

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        const now = new Date();
        const diffTime = Math.abs(now - date);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

        if (diffDays === 0) return 'Today';
        if (diffDays === 1) return 'Yesterday';
        if (diffDays < 7) return `${diffDays} days ago`;
        
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
        });
    };

    const filteredLists = savedLists.filter(list =>
        list.list_name.toLowerCase().includes(searchTerm.toLowerCase())
    );

    if (!isOpen) return null;

    return (
        <>
            {/* Background overlay */}
            <div className="load-panel-backdrop" onClick={onClose} />
            
            {/* Slide-in panel from right */}
            <div className={`load-panel ${isOpen ? 'load-panel-open' : ''}`}>
                
                {/* Header */}
                <div className="load-panel-header">
                    <h2>Saved Grocery Lists</h2>
                    <button className="load-panel-close-btn" onClick={onClose}>✕</button>
                </div>

                {/* Search */}
                <div className="load-panel-search">
                    <input
                        type="text"
                        placeholder="Search lists..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="load-panel-search-input"
                    />
                </div>

                {/* Content */}
                <div className="load-panel-content">
                    {loading && (
                        <div className="load-panel-loading">
                            <p>Loading grocery lists...</p>
                        </div>
                    )}

                    {error && (
                        <div className="load-panel-error">
                            <p>{error}</p>
                            <button onClick={loadSavedLists} className="retry-btn">
                                Retry
                            </button>
                        </div>
                    )}

                    {!loading && !error && filteredLists.length === 0 && (
                        <div className="load-panel-empty">
                            <p>No saved grocery lists found</p>
                            {searchTerm && <p className="empty-hint">Try a different search term</p>}
                        </div>
                    )}

                    {!loading && !error && filteredLists.length > 0 && (
                        <div className="saved-lists-container">
                            {filteredLists.map(list => (
                                <div 
                                    key={list.id} 
                                    className="saved-list-item"
                                    onClick={() => handleLoadList(list.id)}
                                >
                                    <div className="list-item-main">
                                        <div className="list-item-info">
                                            <h3 className="list-item-name">{list.list_name}</h3>
                                            <div className="list-item-meta">
                                                <span className="list-item-date">
                                                    {formatDate(list.created_at)}
                                                </span>
                                                {list.recipe_ids && list.recipe_ids.length > 0 && (
                                                    <span className="list-item-recipes">
                                                        • {list.recipe_ids.length} recipe{list.recipe_ids.length !== 1 ? 's' : ''}
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                    <div className="list-item-actions">
                                        <button
                                            className="list-action-btn delete-btn"
                                            onClick={(e) => handleDeleteList(list.id, list.list_name, e)}
                                            title="Delete this list"
                                        >
                                            ×
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="load-panel-footer">
                    <p className="load-panel-count">
                        {filteredLists.length} list{filteredLists.length !== 1 ? 's' : ''} 
                        {searchTerm && ' found'}
                    </p>
                </div>
            </div>
        </>
    );
};

export default LoadGroceryListPanel;
