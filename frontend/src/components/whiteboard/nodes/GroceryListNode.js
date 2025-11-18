/**
 * Grocery List Node
 * ==================
 * React Flow node for grocery lists with resize handles
 * 
 * Features:
 * - Resizable container (like meal plan)
 * - Real-time item checking
 * - Add/remove items
 * - Auto-save to database
 * - Visual connection lines to recipe cards
 * 
 * Author: GitHub Copilot
 * Date: November 5, 2025
 */

import React, { useState, useRef, useEffect } from 'react';
import { NodeResizer } from '@xyflow/react';
import { useAuth } from '../../../contexts/AuthContext';
import './GroceryListNode.css';

// Color options for grocery list (matching NoteBlock pattern)
const COLOR_OPTIONS = [
  { name: 'Mint', value: '#D1FAE5' },
  { name: 'Sky Blue', value: '#DBEAFE' },
  { name: 'Lavender', value: '#E9D5FF' },
  { name: 'Soft Yellow', value: '#FEF3C7' },
  { name: 'Peach', value: '#FED7AA' },
  { name: 'Light Pink', value: '#FCE7F3' },
  { name: 'Sage', value: '#D1F4E0' },
  { name: 'Light Coral', value: '#FFE4E1' },
  { name: 'White', value: '#FFFFFF' },
  { name: 'Light Gray', value: '#F3F4F6' },
];

const GroceryListNode = ({ id, data, selected }) => {
  const { user } = useAuth();
  
  const [isEditingName, setIsEditingName] = useState(false);
  const [name, setName] = useState(data.name || 'Shopping List');
  const [items, setItems] = useState(data.items || []);
  const [newItemName, setNewItemName] = useState('');
  const [backgroundColor, setBackgroundColor] = useState(data.backgroundColor || '#D1FAE5');
  const [showColorPicker, setShowColorPicker] = useState(false);
  const [draggedItemId, setDraggedItemId] = useState(null);
  const [dragOverItemId, setDragOverItemId] = useState(null);
  const [editingItemId, setEditingItemId] = useState(null);
  const [editingItemValue, setEditingItemValue] = useState('');
  
  const nameInputRef = useRef(null);
  const addInputRef = useRef(null);
  const addInputContainerRef = useRef(null);
  const colorPickerRef = useRef(null);
  const itemsRef = useRef(items); // Track current items for save
  const editInputRef = useRef(null);

  // Debug: Log when component receives new dimensions
  useEffect(() => {
    // Removed debug logs - component working correctly
  }, [id, data]);

  // Debug: Log input container dimensions after render
  useEffect(() => {
    // Removed debug logs - component working correctly
  });

  // Focus input when editing
  useEffect(() => {
    if (isEditingName && nameInputRef.current) {
      nameInputRef.current.focus();
      nameInputRef.current.select();
    }
  }, [isEditingName]);

  // Focus edit input when editing item
  useEffect(() => {
    if (editingItemId && editInputRef.current) {
      editInputRef.current.focus();
      editInputRef.current.select();
    }
  }, [editingItemId]);

  // Keep itemsRef in sync with items state for reliable saves
  useEffect(() => {
    itemsRef.current = items;
  }, [items]);

  // Update local state when data changes
  useEffect(() => {
    setName(data.name || 'Shopping List');
  }, [data.name]);

  // Update local state when data changes (but not during drag to prevent jumps)
  useEffect(() => {
    if (!draggedItemId) {
      setItems(data.items || []);
    }
  }, [data.items, draggedItemId]);

  useEffect(() => {
    setBackgroundColor(data.backgroundColor || '#D1FAE5');
  }, [data.backgroundColor]);

  // Close color picker when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (colorPickerRef.current && !colorPickerRef.current.contains(event.target)) {
        setShowColorPicker(false);
      }
    };

    if (showColorPicker) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [showColorPicker]);

  const handleNameClick = () => {
    setIsEditingName(true);
  };

  const handleNameBlur = () => {
    setIsEditingName(false);
    if (name !== data.name) {
      data.onNameChange?.(id, name);
    }
  };

  const handleColorChange = (newColor) => {
    setBackgroundColor(newColor);
    setShowColorPicker(false);
    data.onColorChange?.(id, newColor);
  };

  const handleNameKeyDown = (e) => {
    e.stopPropagation();
    
    if (e.key === 'Enter') {
      setIsEditingName(false);
      if (name !== data.name) {
        data.onNameChange?.(id, name);
      }
    } else if (e.key === 'Escape') {
      setName(data.name || 'Shopping List');
      setIsEditingName(false);
    }
  };

  const handleItemCheck = (itemId, checked) => {
    const updatedItems = items.map(item =>
      item.id === itemId ? { ...item, checked } : item
    );
    setItems(updatedItems);
    data.onItemChecked?.(id, itemId, checked);
  };

  const handleAddItem = () => {
    if (newItemName.trim()) {
      const newItem = {
        id: `temp-${Date.now()}`,
        name: newItemName.trim(),
        checked: false
      };
      // Add new item at the TOP of the list
      const updatedItems = [newItem, ...items];
      setItems(updatedItems);
      setNewItemName('');
      data.onItemAdded?.(id, newItem);
    }
  };

  const handleRemoveItem = (itemId) => {
    const updatedItems = items.filter(item => item.id !== itemId);
    setItems(updatedItems);
    data.onItemRemoved?.(id, itemId);
  };

  const handleAddKeyDown = (e) => {
    e.stopPropagation();
    
    if (e.key === 'Enter') {
      handleAddItem();
    } else if (e.key === 'Escape') {
      setNewItemName('');
    }
  };

  const handleDelete = (e) => {
    e.stopPropagation();
    if (window.confirm(`Delete "${name}"?`)) {
      data.onDelete?.(id);
    }
  };

    // Drag and drop handlers for reordering items
  const handleDragStart = (e, itemId) => {
    e.stopPropagation(); // Prevent React Flow from handling this drag
    
    // Prevent the default drag behavior that React Flow uses
    if (e.dataTransfer) {
      e.dataTransfer.effectAllowed = 'move';
      e.dataTransfer.setData('text/plain', itemId); // Set some data
    }
    
    setDraggedItemId(itemId);
    
    // Create a drag ghost image for better visual feedback
    const dragImage = e.currentTarget.cloneNode(true);
    dragImage.style.opacity = '0.5';
    dragImage.style.position = 'absolute';
    dragImage.style.top = '-1000px';
    document.body.appendChild(dragImage);
    
    if (e.dataTransfer) {
      e.dataTransfer.setDragImage(dragImage, 0, 0);
    }
    
    setTimeout(() => {
      if (document.body.contains(dragImage)) {
        document.body.removeChild(dragImage);
      }
    }, 0);
  };

  const handleDragOver = (e, itemId) => {
    e.preventDefault();
    e.stopPropagation();
    if (draggedItemId !== itemId) {
      setDragOverItemId(itemId);
    }
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOverItemId(null);
  };

  const handleDrop = (e, dropTargetId) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (!draggedItemId || draggedItemId === dropTargetId) {
      setDraggedItemId(null);
      setDragOverItemId(null);
      return;
    }

    // Use current items from ref for accurate reordering
    const currentItems = itemsRef.current;
    const draggedIndex = currentItems.findIndex(item => item.id === draggedItemId);
    const targetIndex = currentItems.findIndex(item => item.id === dropTargetId);

    if (draggedIndex !== -1 && targetIndex !== -1) {
      const newItems = [...currentItems];
      const [draggedItem] = newItems.splice(draggedIndex, 1);
      newItems.splice(targetIndex, 0, draggedItem);
      
      // Update local state immediately - this prevents visual jump
      setItems(newItems);
      itemsRef.current = newItems; // Update ref immediately too
      
      // Clear drag states immediately for smooth transition
      setDraggedItemId(null);
      setDragOverItemId(null);
      
      // Update parent state and trigger save after a brief delay
      if (data.onItemsReordered) {
        setTimeout(() => {
          data.onItemsReordered(id, newItems);
        }, 50);
      }
    } else {
      setDraggedItemId(null);
      setDragOverItemId(null);
    }
  };

  const handleDragEnd = (e) => {
    e.preventDefault();
    setDraggedItemId(null);
    setDragOverItemId(null);
  };

  // Item editing handlers
  const handleItemNameClick = (item) => {
    setEditingItemId(item.id);
    setEditingItemValue(item.name);
  };

  const handleItemNameBlur = () => {
    if (editingItemId && editingItemValue.trim()) {
      // Update the item name
      const updatedItems = items.map(item =>
        item.id === editingItemId
          ? { ...item, name: editingItemValue.trim() }
          : item
      );
      setItems(updatedItems);
      itemsRef.current = updatedItems; // Update ref immediately
      
      // Notify parent to save
      if (data.onItemsReordered) {
        setTimeout(() => {
          data.onItemsReordered(id, updatedItems);
        }, 50);
      }
    }
    setEditingItemId(null);
    setEditingItemValue('');
  };

  const handleItemNameKeyDown = (e) => {
    e.stopPropagation();
    
    if (e.key === 'Enter') {
      handleItemNameBlur();
    } else if (e.key === 'Escape') {
      setEditingItemId(null);
      setEditingItemValue('');
    }
  };

  const checkedCount = items.filter(item => item.checked).length;
  const totalCount = items.length;

  return (
    <>
      {/* Resize handles */}
      <NodeResizer
        isVisible={selected}
        minWidth={300}
        minHeight={250}
        handleClassName="custom-resize-handle"
      />

      <div className={`grocery-list-node ${selected ? 'selected' : ''}`} style={{ backgroundColor }}>
        {/* Header - draggable area */}
        <div className="node-header">
          <div className="header-left">
            {/* Comment Badge */}
            {data.commentCount > 0 && (
              <div className={`comment-badge-header ${data.hasNewComments ? 'has-new' : ''}`}>
                💬 {data.commentCount}
              </div>
            )}
            {isEditingName ? (
              <input
                ref={nameInputRef}
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                onBlur={handleNameBlur}
                onKeyDown={handleNameKeyDown}
                className="name-input noDrag"
                maxLength={40}
              />
            ) : (
              <span 
                className="node-title noDrag" 
                onClick={handleNameClick}
                style={{ cursor: 'pointer' }}
              >
                🛒 {name}
              </span>
            )}
            <span className="item-count">
              {checkedCount}/{totalCount}
            </span>
          </div>
          <div className="header-right noDrag">
            {/* Color picker button - only show when selected */}
            {selected && (
              <div className="color-picker-wrapper" ref={colorPickerRef}>
                <button
                  className="header-btn color-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    setShowColorPicker(!showColorPicker);
                  }}
                  title="Change color"
                  style={{ backgroundColor }}
                >
                  🎨
                </button>
                {showColorPicker && (
                  <div className="color-picker-dropdown">
                    {COLOR_OPTIONS.map((option) => (
                      <button
                        key={option.value}
                        className="color-option"
                        style={{ backgroundColor: option.value }}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleColorChange(option.value);
                        }}
                        title={option.name}
                      >
                        {backgroundColor === option.value && '✓'}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
            <button className="header-btn delete-btn" onClick={handleDelete} title="Delete list">
              ×
            </button>
          </div>
        </div>

        {/* Items list */}
        <div className="node-content noDrag">
          {/* Add item input - always visible at top */}
          <div className="add-item-input" ref={addInputContainerRef}>
            <input
              ref={addInputRef}
              type="text"
              value={newItemName}
              onChange={(e) => setNewItemName(e.target.value)}
              onKeyDown={handleAddKeyDown}
              placeholder="Type to add item..."
              className="item-input"
              maxLength={100}
            />
          </div>

          <div className="items-list noDrag">
            {items.length === 0 ? (
              <div className="empty-state">
                <p>📝 No items yet</p>
                <span className="hint">Type above to add items</span>
              </div>
            ) : (
              items.map(item => (
                <div
                  key={item.id}
                  className={`grocery-item ${item.checked ? 'checked' : ''} ${dragOverItemId === item.id ? 'drag-over' : ''} ${draggedItemId === item.id ? 'dragging' : ''}`}
                  onDragOver={(e) => handleDragOver(e, item.id)}
                  onDragLeave={handleDragLeave}
                  onDrop={(e) => handleDrop(e, item.id)}
                  onMouseDown={(e) => {
                    // Prevent React Flow from dragging the node when clicking on items
                    e.stopPropagation();
                  }}
                >
                  <span 
                    className="drag-handle" 
                    title="Drag to reorder"
                    style={{ cursor: 'grab' }}
                    draggable="true"
                    onMouseDown={(e) => {
                      // CRITICAL: Prevent React Flow from starting node drag
                      e.stopPropagation();
                    }}
                    onDragStart={(e) => handleDragStart(e, item.id)}
                    onDragEnd={handleDragEnd}
                  >
                    ⋮⋮
                  </span>
                  <input
                    type="checkbox"
                    checked={item.checked}
                    onChange={(e) => handleItemCheck(item.id, e.target.checked)}
                    className="item-checkbox noDrag"
                    onClick={(e) => e.stopPropagation()}
                  />
                  {editingItemId === item.id ? (
                    <input
                      ref={editInputRef}
                      type="text"
                      value={editingItemValue}
                      onChange={(e) => setEditingItemValue(e.target.value)}
                      onBlur={handleItemNameBlur}
                      onKeyDown={handleItemNameKeyDown}
                      className="item-name-input noDrag"
                      maxLength={100}
                    />
                  ) : (
                    <span 
                      className="item-name" 
                      onClick={() => handleItemNameClick(item)}
                      style={{ cursor: 'text' }}
                    >
                      {item.name}
                    </span>
                  )}
                  {item.source_recipe_name && (
                    <span className="item-source" title={`From: ${item.source_recipe_name}`}>
                      📖
                    </span>
                  )}
                  <button
                    className="remove-item-btn noDrag"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleRemoveItem(item.id);
                    }}
                    title="Remove item"
                  >
                    ×
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </>
  );
};

export default GroceryListNode;
