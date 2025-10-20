import React, { useState, useEffect } from 'react';
import './GroceryListGenerator.css';
import { getApiUrl } from '../utils/api';

const GroceryListGenerator = ({ recipeIds = [], onClose, savedListData = null, onSave = null }) => {
    const [groceryList, setGroceryList] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [viewMode, setViewMode] = useState('sections'); // 'sections', 'alphabetical', 'text'
    
    // Enhanced state for customization
    const [customItems, setCustomItems] = useState([]);
    const [newItemText, setNewItemText] = useState('');
    const [checkedItems, setCheckedItems] = useState(new Set());
    const [isAddingItem, setIsAddingItem] = useState(false);
    const [draggedItem, setDraggedItem] = useState(null);
    const [hiddenSections, setHiddenSections] = useState(new Set());
    const [sectionOrder, setSectionOrder] = useState([]);
    const [reorderedItems, setReorderedItems] = useState({}); // Track reordered items per section
    
    // Save functionality state
    const [showSaveDialog, setShowSaveDialog] = useState(false);
    const [saveListName, setSaveListName] = useState('');
    const [isSaving, setIsSaving] = useState(false);

    useEffect(() => {
        if (recipeIds.length > 0) {
            generateGroceryList();
        }
    }, [recipeIds]);

    // Load saved list data if provided
    useEffect(() => {
        if (savedListData && savedListData.list_data) {
            const listData = savedListData.list_data;
            setGroceryList(listData.grocery_list || listData);
            
            // Restore custom state if available
            if (listData.customState) {
                setCustomItems(listData.customState.customItems || []);
                setCheckedItems(new Set(listData.customState.checkedItems || []));
                setHiddenSections(new Set(listData.customState.hiddenSections || []));
                setSectionOrder(listData.customState.sectionOrder || []);
                setReorderedItems(listData.customState.reorderedItems || {});
            }
            
            // Set the list name for updating
            setSaveListName(savedListData.list_name || '');
        }
    }, [savedListData]);

    // Initialize section order when grocery list is loaded
    useEffect(() => {
        if (groceryList && groceryList.by_section && sectionOrder.length === 0) {
            const defaultOrder = Object.keys(groceryList.by_section);
            setSectionOrder(defaultOrder);
        }
    }, [groceryList]);

    // Helper function to get ordered items for a section
    const getOrderedItemsForSection = (section) => {
        if (!groceryList || !groceryList.by_section) return [];
        
        // Get recipe items for this section
        const recipeItems = groceryList.by_section[section] || [];
        
        // Get custom items for this section
        const sectionCustomItems = customItems.filter(item => (item.section || 'other') === section);
        
        // Combine all items
        const allItems = [...recipeItems, ...sectionCustomItems];
        
        // Apply custom ordering if it exists
        if (reorderedItems[section]) {
            const orderedItems = [];
            reorderedItems[section].forEach(itemRef => {
                const item = allItems.find(i => {
                    if (itemRef.isCustom) {
                        return i.id === itemRef.id;
                    } else {
                        return i.name === itemRef.name && !i.isCustom;
                    }
                });
                if (item) orderedItems.push(item);
            });
            
            // Add any new items that weren't in the reordered list
            allItems.forEach(item => {
                const exists = orderedItems.find(i => {
                    if (item.isCustom) {
                        return i.id === item.id;
                    } else {
                        return i.name === item.name && !item.isCustom;
                    }
                });
                if (!exists) orderedItems.push(item);
            });
            
            return orderedItems;
        }
        
        return allItems;
    };

    const generateGroceryList = async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await fetch(`${getApiUrl()}/api/grocery-list`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    recipe_ids: recipeIds
                })
            });

            const data = await response.json();

            if (data.success) {
                setGroceryList(data.grocery_list);
            } else {
                setError(data.message || 'Failed to generate grocery list');
            }
        } catch (err) {
            setError('Network error: ' + err.message);
        } finally {
            setLoading(false);
        }
    };

    // Enhanced functionality for customization
    const addCustomItem = () => {
        if (!newItemText.trim()) return;

        const customItem = {
            id: `custom-${Date.now()}`,
            name: newItemText.trim(),
            display_text: newItemText.trim(),
            recipes: [],
            isCustom: true,
            section: 'other' // Default section for custom items
        };

        setCustomItems(prev => [...prev, customItem]);
        setNewItemText('');
        setIsAddingItem(false);
    };

    const removeCustomItem = (itemId) => {
        setCustomItems(prev => prev.filter(item => item.id !== itemId));
        setCheckedItems(prev => {
            const newSet = new Set(prev);
            newSet.delete(itemId);
            return newSet;
        });
    };

    const toggleItemCheck = (itemId) => {
        setCheckedItems(prev => {
            const newSet = new Set(prev);
            if (newSet.has(itemId)) {
                newSet.delete(itemId);
            } else {
                newSet.add(itemId);
            }
            return newSet;
        });
    };

    const toggleSectionVisibility = (section) => {
        setHiddenSections(prev => {
            const newSet = new Set(prev);
            if (newSet.has(section)) {
                newSet.delete(section);
            } else {
                newSet.add(section);
            }
            return newSet;
        });
    };

    const handleSectionDragStart = (e, section) => {
        setDraggedItem({ type: 'section', section });
        e.dataTransfer.effectAllowed = 'move';
    };

    const handleSectionDrop = (e, targetSection) => {
        e.preventDefault();
        if (!draggedItem || draggedItem.type !== 'section') return;

        const sourceSection = draggedItem.section;
        if (sourceSection === targetSection) return;

        setSectionOrder(prev => {
            const newOrder = [...prev];
            const sourceIndex = newOrder.indexOf(sourceSection);
            const targetIndex = newOrder.indexOf(targetSection);
            
            // Remove source and insert at target position
            newOrder.splice(sourceIndex, 1);
            newOrder.splice(targetIndex, 0, sourceSection);
            
            return newOrder;
        });
        
        setDraggedItem(null);
    };

    const handleItemDragStart = (e, item, section, itemIndex) => {
        setDraggedItem({ type: 'item', item, section, itemIndex });
        e.dataTransfer.effectAllowed = 'move';
    };

    const handleItemDrop = (e, targetSection, targetIndex) => {
        e.preventDefault();
        if (!draggedItem || draggedItem.type !== 'item') return;

        const { section: sourceSection, itemIndex: sourceIndex, item } = draggedItem;
        
        console.log('Item drop:', {
            item: item.name || item.display_text,
            from: `${sourceSection}[${sourceIndex}]`,
            to: `${targetSection}[${targetIndex}]`
        });

        // Handle custom items
        if (item.isCustom) {
            setCustomItems(prev => {
                const newItems = [...prev];
                const itemToMove = newItems.find(i => i.id === item.id);
                if (itemToMove) {
                    itemToMove.section = targetSection;
                }
                return newItems;
            });
        }

        // Update the ordering for both source and target sections
        setReorderedItems(prev => {
            const newReordered = { ...prev };
            
            // Get current items for both sections
            const sourceItems = getOrderedItemsForSection(sourceSection);
            const targetItems = sourceSection === targetSection ? sourceItems : getOrderedItemsForSection(targetSection);
            
            // Create item reference
            const itemRef = {
                id: item.id,
                name: item.name || item.display_text,
                isCustom: !!item.isCustom
            };
            
            if (sourceSection === targetSection) {
                // Moving within same section
                const newOrder = [...(newReordered[sourceSection] || sourceItems.map(i => ({
                    id: i.id,
                    name: i.name || i.display_text,
                    isCustom: !!i.isCustom
                })))];
                
                // Remove from source position
                const sourceItem = newOrder.splice(sourceIndex, 1)[0];
                
                // Insert at target position
                const insertIndex = targetIndex > sourceIndex ? targetIndex - 1 : targetIndex;
                newOrder.splice(insertIndex, 0, sourceItem);
                
                newReordered[sourceSection] = newOrder;
            } else {
                // Moving between sections
                // Remove from source section
                if (newReordered[sourceSection]) {
                    newReordered[sourceSection] = newReordered[sourceSection].filter((_, index) => index !== sourceIndex);
                } else {
                    const sourceOrder = sourceItems.map(i => ({
                        id: i.id,
                        name: i.name || i.display_text,
                        isCustom: !!i.isCustom
                    }));
                    sourceOrder.splice(sourceIndex, 1);
                    newReordered[sourceSection] = sourceOrder;
                }
                
                // Add to target section
                if (newReordered[targetSection]) {
                    newReordered[targetSection].splice(targetIndex, 0, itemRef);
                } else {
                    const targetOrder = targetItems.map(i => ({
                        id: i.id,
                        name: i.name || i.display_text,
                        isCustom: !!i.isCustom
                    }));
                    targetOrder.splice(targetIndex, 0, itemRef);
                    newReordered[targetSection] = targetOrder;
                }
            }
            
            return newReordered;
        });

        setDraggedItem(null);
    };

    const handleDragStart = (e, item, section) => {
        // This function is now handled by handleItemDragStart
        handleItemDragStart(e, item, section, 0);
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
    };

    const handleDrop = (e, targetSection) => {
        // This function is now handled by handleItemDrop
        handleItemDrop(e, targetSection, 0);
    };

    const getAllItemsForExport = () => {
        const allItems = [];
        
        if (groceryList) {
            // Use custom section order if available
            const orderedSections = sectionOrder.length > 0 ? sectionOrder : Object.keys(groceryList.by_section || {});
            
            // Add any sections that might have only custom items
            const allSections = new Set([...orderedSections]);
            customItems.forEach(item => {
                const section = item.section || 'other';
                allSections.add(section);
            });

            if (viewMode === 'sections') {
                Array.from(allSections).forEach(section => {
                    const items = getOrderedItemsForSection(section);
                    items.forEach(item => {
                        allItems.push({
                            ...item,
                            section,
                            id: item.id || `recipe-${item.name}-${section}`
                        });
                    });
                });
            } else if (viewMode === 'alphabetical' && groceryList.alphabetical) {
                // For alphabetical, combine and sort all items
                const allCombined = [];
                
                // Add recipe items
                groceryList.alphabetical.forEach(item => {
                    allCombined.push({
                        ...item,
                        section: 'other',
                        id: `recipe-${item.name}`
                    });
                });
                
                // Add custom items
                customItems.forEach(item => {
                    allCombined.push(item);
                });
                
                // Sort alphabetically
                allCombined.sort((a, b) => {
                    const nameA = (a.display_text || a.name).toLowerCase();
                    const nameB = (b.display_text || b.name).toLowerCase();
                    return nameA.localeCompare(nameB);
                });
                
                allItems.push(...allCombined);
            }
        }

        return allItems;
    };

    const exportToGoogleKeepEnhanced = () => {
        const allItems = getAllItemsForExport();
        
        // Create checkbox format for Google Keep
        const checkboxItems = allItems.map(item => {
            const isChecked = checkedItems.has(item.id);
            const checkbox = isChecked ? '☑️' : '☐';
            return `${checkbox} ${item.display_text || item.name}`;
        });

        // Group by sections for better organization
        let formattedList = '';
        if (viewMode === 'sections') {
            const sections = {};
            allItems.forEach(item => {
                const section = item.section || 'other';
                if (!sections[section]) sections[section] = [];
                sections[section].push(item);
            });

            Object.entries(sections).forEach(([section, items]) => {
                formattedList += `\n${section.replace('_', ' ').toUpperCase()}:\n`;
                items.forEach(item => {
                    const isChecked = checkedItems.has(item.id);
                    const checkbox = isChecked ? '☑️' : '☐';
                    formattedList += `${checkbox} ${item.display_text || item.name}\n`;
                });
            });
        } else {
            formattedList = checkboxItems.join('\n');
        }

        copyToClipboard(formattedList);
    };

    const saveGroceryList = async () => {
        if (!saveListName.trim()) {
            alert('Please enter a name for your grocery list');
            return;
        }

        setIsSaving(true);
        
        try {
            const listData = {
                grocery_list: groceryList,
                customState: {
                    customItems,
                    checkedItems: Array.from(checkedItems),
                    hiddenSections: Array.from(hiddenSections),
                    sectionOrder,
                    reorderedItems
                }
            };

            const payload = {
                list_name: saveListName.trim(),
                list_data: listData,
                recipe_ids: recipeIds
            };

            let response;
            if (savedListData && savedListData.id) {
                // Update existing list
                response = await fetch(`${getApiUrl()}/api/grocery-lists/${savedListData.id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload)
                });
            } else {
                // Create new list
                response = await fetch(`${getApiUrl()}/api/grocery-lists`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload)
                });
            }

            const data = await response.json();

            if (data.success) {
                alert(`Grocery list "${saveListName}" ${savedListData ? 'updated' : 'saved'} successfully!`);
                setShowSaveDialog(false);
                setSaveListName('');
                
                // Call onSave callback if provided
                if (onSave) {
                    onSave(data);
                }
            } else {
                alert('Failed to save grocery list: ' + data.error);
            }
        } catch (err) {
            alert('Network error: ' + err.message);
        } finally {
            setIsSaving(false);
        }
    };

    const copyToClipboard = (text) => {
        navigator.clipboard.writeText(text).then(() => {
            alert('Grocery list copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy: ', err);
            alert('Failed to copy to clipboard');
        });
    };

    const exportToGoogleKeep = () => {
        exportToGoogleKeepEnhanced();
    };

    const renderSectionView = () => {
        if (!groceryList || !groceryList.by_section) return null;

        // Use custom section order if available, otherwise use default
        const orderedSections = sectionOrder.length > 0 ? sectionOrder : Object.keys(groceryList.by_section);

        // Add any sections that might have only custom items
        const allSections = new Set([...orderedSections]);
        customItems.forEach(item => {
            const section = item.section || 'other';
            allSections.add(section);
        });

        return (
            <div className="grocery-sections">
                {/* Add Custom Item Section */}
                <div className="add-item-section">
                    {!isAddingItem ? (
                        <button 
                            className="add-item-btn"
                            onClick={() => setIsAddingItem(true)}
                        >
                            ➕ Add Custom Item
                        </button>
                    ) : (
                        <div className="add-item-form">
                            <input
                                type="text"
                                value={newItemText}
                                onChange={(e) => setNewItemText(e.target.value)}
                                placeholder="Enter item (e.g., ketchup, dryer sheets)"
                                className="add-item-input"
                                onKeyPress={(e) => {
                                    if (e.key === 'Enter') addCustomItem();
                                    if (e.key === 'Escape') {
                                        setIsAddingItem(false);
                                        setNewItemText('');
                                    }
                                }}
                                autoFocus
                            />
                            <button onClick={addCustomItem} className="add-item-confirm">✅</button>
                            <button 
                                onClick={() => {
                                    setIsAddingItem(false);
                                    setNewItemText('');
                                }} 
                                className="add-item-cancel"
                            >❌</button>
                        </div>
                    )}
                </div>

                {Array.from(allSections).map((section) => {
                    const items = getOrderedItemsForSection(section);
                    const isHidden = hiddenSections.has(section);
                    
                    // Skip empty sections
                    if (items.length === 0) return null;
                    
                    return (
                        <div 
                            key={section} 
                            className={`grocery-section ${isHidden ? 'hidden-section' : ''}`}
                            onDragOver={handleDragOver}
                            onDrop={(e) => handleSectionDrop(e, section)}
                        >
                            <div 
                                className="section-header"
                                draggable={true}
                                onDragStart={(e) => handleSectionDragStart(e, section)}
                            >
                                <h4 className="section-title">
                                    <span className="section-drag-handle">⋮⋮</span>
                                    {section.replace('_', ' ').toUpperCase()}
                                    <span className="section-count">({items.length})</span>
                                    <button 
                                        className="section-toggle"
                                        onClick={() => toggleSectionVisibility(section)}
                                        title={isHidden ? 'Show section' : 'Hide section'}
                                    >
                                        {isHidden ? '👁️' : '🙈'}
                                    </button>
                                </h4>
                            </div>
                            
                            {!isHidden && (
                                <ul className="section-items">
                                    {items.map((item, index) => {
                                        const itemId = item.id || `recipe-${item.name}-${section}`;
                                        const isChecked = checkedItems.has(itemId);
                                        return (
                                            <li 
                                                key={`${itemId}-${index}`} 
                                                className={`grocery-item ${isChecked ? 'checked' : ''} ${item.isCustom ? 'custom-item' : ''}`}
                                                draggable={true}
                                                onDragStart={(e) => handleItemDragStart(e, item, section, index)}
                                                onDragOver={handleDragOver}
                                                onDrop={(e) => handleItemDrop(e, section, index)}
                                            >
                                                <label className="grocery-item-label">
                                                    <input
                                                        type="checkbox"
                                                        className="grocery-checkbox"
                                                        checked={isChecked}
                                                        onChange={() => toggleItemCheck(itemId)}
                                                    />
                                                    <span className={`item-text ${isChecked ? 'strikethrough' : ''}`}>
                                                        {item.display_text || item.name}
                                                    </span>
                                                    {item.recipes && item.recipes.length > 0 && (
                                                        <span className="item-recipes">
                                                            (from: {item.recipes.join(', ')})
                                                        </span>
                                                    )}
                                                    {item.isCustom && (
                                                        <button
                                                            className="remove-custom-btn"
                                                            onClick={(e) => {
                                                                e.preventDefault();
                                                                removeCustomItem(item.id);
                                                            }}
                                                            title="Remove custom item"
                                                        >
                                                            🗑️
                                                        </button>
                                                    )}
                                                </label>
                                                <div className="drag-handle" title="Drag to reorder">⋮⋮</div>
                                            </li>
                                        );
                                    })}
                                </ul>
                            )}
                        </div>
                    );
                })}
            </div>
        );
    };

    const renderAlphabeticalView = () => {
        if (!groceryList || !groceryList.alphabetical) return null;

        // Combine recipe items with custom items and sort alphabetically
        const allItems = [
            ...groceryList.alphabetical,
            ...customItems
        ].sort((a, b) => {
            const nameA = (a.display_text || a.name).toLowerCase();
            const nameB = (b.display_text || b.name).toLowerCase();
            return nameA.localeCompare(nameB);
        });

        return (
            <div className="grocery-alphabetical">
                {/* Add Custom Item Section */}
                <div className="add-item-section">
                    {!isAddingItem ? (
                        <button 
                            className="add-item-btn"
                            onClick={() => setIsAddingItem(true)}
                        >
                            ➕ Add Custom Item
                        </button>
                    ) : (
                        <div className="add-item-form">
                            <input
                                type="text"
                                value={newItemText}
                                onChange={(e) => setNewItemText(e.target.value)}
                                placeholder="Enter item (e.g., ketchup, dryer sheets)"
                                className="add-item-input"
                                onKeyPress={(e) => {
                                    if (e.key === 'Enter') addCustomItem();
                                    if (e.key === 'Escape') {
                                        setIsAddingItem(false);
                                        setNewItemText('');
                                    }
                                }}
                                autoFocus
                            />
                            <button onClick={addCustomItem} className="add-item-confirm">✅</button>
                            <button 
                                onClick={() => {
                                    setIsAddingItem(false);
                                    setNewItemText('');
                                }} 
                                className="add-item-cancel"
                            >❌</button>
                        </div>
                    )}
                </div>

                <ul className="alphabetical-items">
                    {allItems.map((item, index) => {
                        const itemId = item.id || `recipe-${item.name}`;
                        const isChecked = checkedItems.has(itemId);
                        return (
                            <li 
                                key={itemId} 
                                className={`grocery-item ${isChecked ? 'checked' : ''} ${item.isCustom ? 'custom-item' : ''}`}
                                draggable={true}
                                onDragStart={(e) => handleDragStart(e, item, 'alphabetical')}
                            >
                                <label className="grocery-item-label">
                                    <input
                                        type="checkbox"
                                        className="grocery-checkbox"
                                        checked={isChecked}
                                        onChange={() => toggleItemCheck(itemId)}
                                    />
                                    <span className={`item-text ${isChecked ? 'strikethrough' : ''}`}>
                                        {item.display_text || item.name}
                                    </span>
                                    {item.recipes && item.recipes.length > 0 && (
                                        <span className="item-recipes">
                                            (from: {item.recipes.join(', ')})
                                        </span>
                                    )}
                                    {item.isCustom && (
                                        <button
                                            className="remove-custom-btn"
                                            onClick={(e) => {
                                                e.preventDefault();
                                                removeCustomItem(item.id);
                                            }}
                                            title="Remove custom item"
                                        >
                                            🗑️
                                        </button>
                                    )}
                                </label>
                                <div className="drag-handle" title="Drag to reorder">⋮⋮</div>
                            </li>
                        );
                    })}
                </ul>
            </div>
        );
    };

    const renderTextView = () => {
        if (!groceryList || !groceryList.text_format) return null;

        return (
            <div className="grocery-text">
                <pre className="text-format">
                    {groceryList.text_format}
                </pre>
            </div>
        );
    };

    if (recipeIds.length === 0) {
        return (
            <div className="grocery-list-modal">
                <div className="grocery-list-content">
                    <div className="grocery-list-header">
                        <h3>🛒 Grocery List Generator</h3>
                        <button onClick={onClose} className="close-btn">❌</button>
                    </div>
                    <div className="no-recipes">
                        <p>Add some recipes to your meal plan to generate a grocery list!</p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="grocery-list-modal">
            <div className="grocery-list-content">
                <div className="grocery-list-header">
                    <h3>🛒 Grocery List</h3>
                    <div className="header-controls">
                        <span className="recipe-count">
                            From {recipeIds.length} recipe{recipeIds.length !== 1 ? 's' : ''}
                        </span>
                        <button onClick={onClose} className="close-btn">❌</button>
                    </div>
                </div>

                {loading && (
                    <div className="loading-state">
                        <p>🔄 Generating grocery list...</p>
                    </div>
                )}

                {error && (
                    <div className="error-state">
                        <p>❌ {error}</p>
                        <button onClick={generateGroceryList} className="retry-btn">
                            🔄 Retry
                        </button>
                    </div>
                )}

                {groceryList && !loading && !error && (
                    <>
                        <div className="grocery-list-controls">
                            <div className="view-mode-selector">
                                <button
                                    className={`view-btn ${viewMode === 'sections' ? 'active' : ''}`}
                                    onClick={() => setViewMode('sections')}
                                >
                                    📂 By Section
                                </button>
                                <button
                                    className={`view-btn ${viewMode === 'alphabetical' ? 'active' : ''}`}
                                    onClick={() => setViewMode('alphabetical')}
                                >
                                    🔤 Alphabetical
                                </button>
                                <button
                                    className={`view-btn ${viewMode === 'text' ? 'active' : ''}`}
                                    onClick={() => setViewMode('text')}
                                >
                                    📄 Text Format
                                </button>
                            </div>

                            <div className="export-controls">
                                <button
                                    onClick={() => setShowSaveDialog(true)}
                                    className="export-btn save-btn"
                                    title="Save this grocery list"
                                >
                                    💾 {savedListData ? 'Update List' : 'Save List'}
                                </button>
                                <button
                                    onClick={exportToGoogleKeepEnhanced}
                                    className="export-btn google-keep-btn"
                                    title="Export with checkboxes for Google Keep"
                                >
                                    📱 Export to Google Keep
                                </button>
                                <button
                                    onClick={() => {
                                        const allItems = getAllItemsForExport();
                                        const textList = allItems.map(item => 
                                            `• ${item.display_text || item.name}`
                                        ).join('\n');
                                        copyToClipboard(textList);
                                    }}
                                    className="export-btn copy-btn"
                                >
                                    📋 Copy as Text
                                </button>
                                <button
                                    onClick={() => {
                                        const checkedCount = checkedItems.size;
                                        const totalCount = getAllItemsForExport().length;
                                        if (checkedCount === 0) {
                                            alert('No items checked yet!');
                                        } else {
                                            alert(`Shopping progress: ${checkedCount}/${totalCount} items completed`);
                                        }
                                    }}
                                    className="export-btn progress-btn"
                                    title="Check shopping progress"
                                >
                                    � Progress ({checkedItems.size})
                                </button>
                            </div>
                        </div>

                        <div className="grocery-list-summary">
                            <span>
                                📊 {(groceryList.ingredient_count || 0) + customItems.length} total items
                                {customItems.length > 0 && (
                                    <span className="custom-count"> ({customItems.length} custom)</span>
                                )}
                                {checkedItems.size > 0 && (
                                    <span className="checked-count"> • ✅ {checkedItems.size} completed</span>
                                )}
                            </span>
                        </div>

                        <div className="grocery-list-body">
                            {viewMode === 'sections' && renderSectionView()}
                            {viewMode === 'alphabetical' && renderAlphabeticalView()}
                            {viewMode === 'text' && renderTextView()}
                        </div>

                        <div className="grocery-list-footer">
                            <p className="footer-text">
                                💡 Tips: Check off items as you shop • Add custom items • Drag to reorder • Export to Google Keep with checkboxes!
                            </p>
                        </div>
                    </>
                )}

                {/* Save Dialog */}
                {showSaveDialog && (
                    <div className="save-dialog-overlay">
                        <div className="save-dialog">
                            <h3>💾 {savedListData ? 'Update' : 'Save'} Grocery List</h3>
                            <input
                                type="text"
                                value={saveListName}
                                onChange={(e) => setSaveListName(e.target.value)}
                                placeholder="Enter list name (e.g., 'Weekly Shopping', 'Holiday Dinner')"
                                className="save-list-name-input"
                                autoFocus
                                onKeyPress={(e) => {
                                    if (e.key === 'Enter') saveGroceryList();
                                    if (e.key === 'Escape') setShowSaveDialog(false);
                                }}
                            />
                            <div className="save-dialog-actions">
                                <button
                                    onClick={saveGroceryList}
                                    disabled={isSaving || !saveListName.trim()}
                                    className="save-confirm-btn"
                                >
                                    {isSaving ? '💾 Saving...' : `💾 ${savedListData ? 'Update' : 'Save'}`}
                                </button>
                                <button
                                    onClick={() => {
                                        setShowSaveDialog(false);
                                        setSaveListName('');
                                    }}
                                    className="save-cancel-btn"
                                    disabled={isSaving}
                                >
                                    ❌ Cancel
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default GroceryListGenerator;
