import React, { useState, useEffect } from 'react';
import { DndContext, closestCenter } from '@dnd-kit/core';
import './GroceryManagerWorkspace.css';
import { getApiUrl } from '../utils/api';

const GroceryManagerWorkspace = ({ mealPlanRecipes = [] }) => {
    // Main state
    const [savedLists, setSavedLists] = useState([]);
    const [selectedListId, setSelectedListId] = useState(null);
    const [currentList, setCurrentList] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // Workspace state
    const [sections, setSections] = useState({
        produce: { name: 'Produce', items: [] },
        meat_seafood: { name: 'Meat & Seafood', items: [] },
        pantry: { name: 'Pantry', items: [] },
        other: { name: 'Other', items: [] }
    });

    // UI state
    const [selectedFolder, setSelectedFolder] = useState(null);
    const [folders, setFolders] = useState([
        { id: 'recent', name: 'Recent Lists', lists: [] },
        { id: 'favorites', name: 'Favorites', lists: [] }
    ]);
    const [isCreatingList, setIsCreatingList] = useState(false);
    const [newListName, setNewListName] = useState('');

    // Load saved lists on component mount
    useEffect(() => {
        loadSavedLists();
        // Auto-load from meal planner if available
        if (mealPlanRecipes.length > 0) {
            generateListFromMealPlan();
        }
    }, [mealPlanRecipes]);

    const loadSavedLists = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${getApiUrl()}/api/grocery-lists`);
            const data = await response.json();

            if (data.success) {
                setSavedLists(data.grocery_lists);
                // Organize into folders
                const recentLists = data.grocery_lists.slice(0, 5);
                setFolders(prev => prev.map(folder => 
                    folder.id === 'recent' 
                        ? { ...folder, lists: recentLists }
                        : folder
                ));
            } else {
                setError(data.error || 'Failed to load grocery lists');
            }
        } catch (err) {
            setError('Network error: ' + err.message);
        } finally {
            setLoading(false);
        }
    };

    const generateListFromMealPlan = async () => {
        if (mealPlanRecipes.length === 0) return;

        try {
            const response = await fetch(`${getApiUrl()}/api/grocery-list`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ recipe_ids: mealPlanRecipes })
            });

            const data = await response.json();
            if (data.success && data.grocery_list) {
                // Convert to our section format
                const newSections = { ...sections };
                Object.entries(data.grocery_list.by_section || {}).forEach(([sectionKey, items]) => {
                    if (newSections[sectionKey]) {
                        newSections[sectionKey].items = items.map(item => ({
                            id: `recipe-${item.name}`,
                            name: item.display_text || item.name,
                            recipes: item.recipes || [],
                            isCustom: false
                        }));
                    }
                });
                setSections(newSections);
                setCurrentList({
                    id: 'current',
                    name: 'Current Meal Plan List',
                    isFromMealPlan: true
                });
            }
        } catch (err) {
            console.error('Failed to generate grocery list:', err);
        }
    };

    const createNewList = () => {
        setIsCreatingList(true);
        setNewListName('');
    };

    const saveNewList = async () => {
        if (!newListName.trim()) return;

        const listData = {
            sections,
            created_from_meal_plan: mealPlanRecipes.length > 0,
            recipe_ids: mealPlanRecipes
        };

        try {
            const response = await fetch(`${getApiUrl()}/api/grocery-lists`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    list_name: newListName.trim(),
                    list_data: listData,
                    recipe_ids: mealPlanRecipes
                })
            });

            const data = await response.json();
            if (data.success) {
                setCurrentList({
                    id: data.list_id,
                    name: newListName.trim(),
                    isFromMealPlan: false
                });
                setIsCreatingList(false);
                setNewListName('');
                loadSavedLists(); // Refresh the saved lists
            }
        } catch (err) {
            console.error('Failed to save list:', err);
        }
    };

    const loadList = async (listId) => {
        try {
            const response = await fetch(`${getApiUrl()}/api/grocery-lists/${listId}`);
            const data = await response.json();

            if (data.success && data.grocery_list.list_data) {
                const listData = data.grocery_list.list_data;
                if (listData.sections) {
                    setSections(listData.sections);
                    setCurrentList({
                        id: listId,
                        name: data.grocery_list.list_name,
                        isFromMealPlan: false
                    });
                    setSelectedListId(listId);
                }
            }
        } catch (err) {
            console.error('Failed to load list:', err);
        }
    };

    const addCustomItem = (sectionKey, itemName) => {
        const newItem = {
            id: `custom-${Date.now()}`,
            name: itemName,
            isCustom: true,
            recipes: []
        };

        setSections(prev => ({
            ...prev,
            [sectionKey]: {
                ...prev[sectionKey],
                items: [...prev[sectionKey].items, newItem]
            }
        }));
    };

    const removeItem = (sectionKey, itemId) => {
        setSections(prev => ({
            ...prev,
            [sectionKey]: {
                ...prev[sectionKey],
                items: prev[sectionKey].items.filter(item => item.id !== itemId)
            }
        }));
    };

    return (
        <div className="grocery-manager-workspace">
            {/* Left Sidebar - List Navigation */}
            <div className="grocery-sidebar">
                <div className="grocery-sidebar-header">
                    <h3>🛒 Grocery Lists</h3>
                    <button 
                        className="create-list-btn"
                        onClick={createNewList}
                        title="Create new grocery list"
                    >
                        ➕
                    </button>
                </div>

                {/* Create New List Form */}
                {isCreatingList && (
                    <div className="create-list-form">
                        <input
                            type="text"
                            value={newListName}
                            onChange={(e) => setNewListName(e.target.value)}
                            placeholder="List name..."
                            className="new-list-input"
                            autoFocus
                            onKeyPress={(e) => {
                                if (e.key === 'Enter') saveNewList();
                                if (e.key === 'Escape') setIsCreatingList(false);
                            }}
                        />
                        <div className="create-list-actions">
                            <button onClick={saveNewList} className="save-btn">✅</button>
                            <button onClick={() => setIsCreatingList(false)} className="cancel-btn">❌</button>
                        </div>
                    </div>
                )}

                {/* Current List Indicator */}
                {currentList && (
                    <div className="current-list-indicator">
                        <span className="current-list-name">📝 {currentList.name}</span>
                        {currentList.isFromMealPlan && (
                            <span className="meal-plan-badge">From Meal Plan</span>
                        )}
                    </div>
                )}

                {/* Folders and Lists */}
                <div className="folders-container">
                    {folders.map(folder => (
                        <div key={folder.id} className="folder">
                            <div 
                                className="folder-header"
                                onClick={() => setSelectedFolder(selectedFolder === folder.id ? null : folder.id)}
                            >
                                <span className="folder-icon">📁</span>
                                <span className="folder-name">{folder.name}</span>
                                <span className="folder-toggle">
                                    {selectedFolder === folder.id ? '📖' : '📁'}
                                </span>
                            </div>
                            
                            {selectedFolder === folder.id && (
                                <div className="folder-lists">
                                    {folder.lists.map(list => (
                                        <div 
                                            key={list.id}
                                            className={`list-item ${selectedListId === list.id ? 'selected' : ''}`}
                                            onClick={() => loadList(list.id)}
                                        >
                                            <span className="list-name">{list.list_name}</span>
                                            <span className="list-meta">
                                                {list.item_count || 0} items
                                            </span>
                                        </div>
                                    ))}
                                    {folder.lists.length === 0 && (
                                        <div className="empty-folder">No lists yet</div>
                                    )}
                                </div>
                            )}
                        </div>
                    ))}
                </div>

                {/* Loading/Error States */}
                {loading && <div className="sidebar-loading">Loading lists...</div>}
                {error && <div className="sidebar-error">Error: {error}</div>}
            </div>

            {/* Main Canvas - Grocery List Workspace */}
            <div className="grocery-main-content">
                <div className="grocery-workspace-header">
                    <h2>{currentList ? currentList.name : 'Select or Create a Grocery List'}</h2>
                    <div className="workspace-controls">
                        <button className="export-btn">📱 Export</button>
                        <button className="save-btn">💾 Save Changes</button>
                    </div>
                </div>

                {currentList ? (
                    <DndContext collisionDetection={closestCenter}>
                        <div className="grocery-columns">
                            {Object.entries(sections).map(([sectionKey, section]) => (
                                <div key={sectionKey} className="grocery-column">
                                    <div className="column-header">
                                        <h4 className="column-title">{section.name}</h4>
                                        <span className="item-count">({section.items.length})</span>
                                        <button 
                                            className="add-item-btn"
                                            onClick={() => {
                                                const itemName = prompt(`Add item to ${section.name}:`);
                                                if (itemName) addCustomItem(sectionKey, itemName);
                                            }}
                                        >
                                            ➕
                                        </button>
                                    </div>
                                    
                                    <div className="column-items">
                                        {section.items.map(item => (
                                            <div key={item.id} className="grocery-item-card">
                                                <div className="item-content">
                                                    <span className="item-name">{item.name}</span>
                                                    {item.recipes && item.recipes.length > 0 && (
                                                        <span className="item-recipes">
                                                            from: {item.recipes.join(', ')}
                                                        </span>
                                                    )}
                                                </div>
                                                <div className="item-actions">
                                                    {item.isCustom && (
                                                        <button 
                                                            className="remove-btn"
                                                            onClick={() => removeItem(sectionKey, item.id)}
                                                        >
                                                            🗑️
                                                        </button>
                                                    )}
                                                    <div className="drag-handle">⋮⋮</div>
                                                </div>
                                            </div>
                                        ))}
                                        
                                        {section.items.length === 0 && (
                                            <div className="empty-column">
                                                <p>No items yet</p>
                                                <button 
                                                    className="add-first-item"
                                                    onClick={() => {
                                                        const itemName = prompt(`Add first item to ${section.name}:`);
                                                        if (itemName) addCustomItem(sectionKey, itemName);
                                                    }}
                                                >
                                                    ➕ Add Item
                                                </button>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </DndContext>
                ) : (
                    <div className="empty-workspace">
                        <div className="empty-workspace-content">
                            <h3>Welcome to Your Grocery Manager</h3>
                            <p>Create a new list or select an existing one to get started</p>
                            
                            {mealPlanRecipes.length > 0 && (
                                <button 
                                    className="generate-from-meal-plan-btn"
                                    onClick={generateListFromMealPlan}
                                >
                                    📋 Generate from Meal Plan ({mealPlanRecipes.length} recipes)
                                </button>
                            )}
                            
                            <button 
                                className="create-empty-list-btn"
                                onClick={createNewList}
                            >
                                ➕ Create Empty List
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default GroceryManagerWorkspace;
