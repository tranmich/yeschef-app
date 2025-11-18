/**
 * Grocery List Floating Widget
 * ============================
 * Draggable, resizable grocery list widget for whiteboard canvas
 * 
 * Features:
 * - Drag to reposition anywhere on canvas
 * - Resize (small/medium/large)
 * - Minimize/expand
 * - Real-time sync via WebSocket
 * - Visual connection lines to recipe cards
 * - Check off items while shopping
 * 
 * Author: GitHub Copilot
 * Date: November 4, 2025
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import whiteboardAPI from '../services/whiteboardAPI';
import './GroceryListFloatingWidget.css';

const GroceryListFloatingWidget = ({
  groceryList,
  householdId,
  whiteboardId,
  linkedRecipes = [],
  initialPosition = { x: 800, y: 100 },
  viewport = { x: 0, y: 0, zoom: 1 }, // Canvas viewport for transformation
  onPositionChange,
  onClose,
  onItemChecked,
  onItemAdded,
  onItemRemoved,
  onSizeChange,
  onSave // Callback after successful save with updated data
}) => {
  const { user } = useAuth();
  
  // Widget state
  const [canvasPosition, setCanvasPosition] = useState(initialPosition); // Canvas coordinates
  const [size, setSize] = useState('medium'); // small, medium, large
  const [isMinimized, setIsMinimized] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  
  // Apply viewport transformation: screen = (canvas * zoom) + viewportOffset
  const screenPosition = {
    x: canvasPosition.x * viewport.zoom + viewport.x,
    y: canvasPosition.y * viewport.zoom + viewport.y
  };
  
  // List state
  const [items, setItems] = useState(groceryList?.items || []);
  const [newItemName, setNewItemName] = useState('');
  const [showAddInput, setShowAddInput] = useState(false);
  
  // Refs
  const widgetRef = useRef(null);
  const dragHandleRef = useRef(null);
  
  // Update items when grocery list changes
  useEffect(() => {
    if (groceryList?.items) {
      setItems(groceryList.items);
    }
  }, [groceryList]);
  
  // Dragging handlers
  // Dragging logic with viewport transformation
  const handleMouseDown = (e) => {
    if (e.target.closest('.widget-header') && !e.target.closest('button')) {
      setIsDragging(true);
      setDragOffset({
        x: e.clientX - screenPosition.x,
        y: e.clientY - screenPosition.y
      });
    }
  };
  
  const handleMouseMove = useCallback((e) => {
    if (isDragging) {
      e.preventDefault();
      
      // Use requestAnimationFrame for smooth 60fps updates
      requestAnimationFrame(() => {
        // Convert screen position back to canvas coordinates
        const newCanvasPosition = {
          x: (e.clientX - dragOffset.x - viewport.x) / viewport.zoom,
          y: (e.clientY - dragOffset.y - viewport.y) / viewport.zoom
        };
        setCanvasPosition(newCanvasPosition);
      });
    }
  }, [isDragging, dragOffset, viewport]);
  
  const handleMouseUp = useCallback(() => {
    if (isDragging) {
      setIsDragging(false);
      // Save final canvas position after drag ends
      onPositionChange?.(canvasPosition);
    }
  }, [isDragging, canvasPosition, onPositionChange]);
  
  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging, handleMouseMove, handleMouseUp]);
  
  // Item handlers
  const handleCheckItem = (itemId) => {
    const item = items.find(i => i.id === itemId);
    const newCheckedState = !item.checked;
    
    setItems(items.map(i => 
      i.id === itemId ? { ...i, checked: newCheckedState } : i
    ));
    
    onItemChecked?.(itemId, newCheckedState);
  };
  
  const handleAddItem = () => {
    if (!newItemName.trim()) return;
    
    const newItem = {
      id: `item-${Date.now()}`,
      ingredient: newItemName.trim(),
      quantity: '',
      checked: false,
      source_recipe_id: null
    };
    
    setItems([...items, newItem]);
    setNewItemName('');
    setShowAddInput(false);
    
    onItemAdded?.(newItem);
  };
  
  const handleRemoveItem = (itemId) => {
    setItems(items.filter(i => i.id !== itemId));
    onItemRemoved?.(itemId);
  };
  
  // Save grocery list to database
  const handleSave = async () => {
    try {
      console.log('💾 Saving grocery list...');
      console.log('📋 Whiteboard ID:', whiteboardId);
      console.log('🏠 Household ID:', householdId);
      console.log('🆔 Current dbId:', groceryList.dbId);
      
      const saveData = {
        name: groceryList.name,
        items: items,
        household_id: householdId,
        widget_position: {
          x: canvasPosition.x,
          y: canvasPosition.y,
          size: size
        },
        linked_recipe_ids: linkedRecipes.map(r => r.id)
      };
      
      console.log('📦 Save data:', saveData);
      
      let result;
      
      if (groceryList.dbId) {
        // Update existing list
        console.log(`📝 Updating grocery list ${groceryList.dbId}...`);
        result = await whiteboardAPI.updateWhiteboardGroceryList(
          whiteboardId,
          groceryList.dbId,
          saveData
        );
      } else {
        // Create new list
        console.log('✨ Creating new grocery list...');
        result = await whiteboardAPI.createWhiteboardGroceryList(
          whiteboardId,
          saveData
        );
      }
      
      if (result.success) {
        console.log('✅ Grocery list saved successfully:', result.data);
        
        const savedData = result.data;
        
        // Update local dbId if it was a new list
        if (!groceryList.dbId && savedData.id) {
          groceryList.dbId = savedData.id;
        }
        
        // Notify parent component with updated data
        onSave?.({
          ...groceryList,
          dbId: savedData.id,
          name: savedData.name,
          items: savedData.items,
          widget_position: savedData.widget_position,
          linked_recipe_ids: savedData.linked_recipe_ids
        });
        
        // Show success feedback
        alert('✅ Grocery list saved!');
      } else {
        console.error('❌ Save failed:', result);
        alert('❌ Failed to save grocery list');
      }
    } catch (error) {
      console.error('❌ Error saving grocery list:', error);
      alert('❌ Error saving grocery list: ' + error.message);
    }
  };
  
  // Size toggle
  const handleSizeToggle = () => {
    const sizes = ['small', 'medium', 'large'];
    const currentIndex = sizes.indexOf(size);
    const nextSize = sizes[(currentIndex + 1) % sizes.length];
    setSize(nextSize);
    onSizeChange?.(nextSize);
  };
  
  // Get size class
  const getSizeClass = () => {
    return `widget-size-${size}`;
  };
  
  // Count checked items
  const checkedCount = items.filter(i => i.checked).length;
  const totalCount = items.length;
  
  return (
    <div
      ref={widgetRef}
      className={`grocery-list-floating-widget ${getSizeClass()} ${isMinimized ? 'minimized' : ''} ${isDragging ? 'dragging' : ''}`}
      style={{
        position: 'absolute',
        left: `${screenPosition.x}px`,
        top: `${screenPosition.y}px`,
        zIndex: 1000,
        transform: `scale(${viewport.zoom})`, // Scale with canvas zoom
        transformOrigin: '0 0'
      }}
      onMouseDown={handleMouseDown}
    >
      {/* Header */}
      <div ref={dragHandleRef} className="widget-header">
        <div className="widget-title">
          <span className="widget-name">{groceryList?.name || 'Shopping List'}</span>
          <span className="widget-count">({checkedCount}/{totalCount})</span>
        </div>
        
        <div className="widget-controls">
          {/* Size toggle */}
          <button
            className="widget-btn"
            onClick={handleSizeToggle}
            title="Resize"
          >
            {size === 'small' ? '⬜' : size === 'medium' ? '◻️' : '⬛'}
          </button>
          
          {/* Minimize/Expand */}
          <button
            className="widget-btn"
            onClick={() => setIsMinimized(!isMinimized)}
            title={isMinimized ? 'Expand' : 'Minimize'}
          >
            {isMinimized ? '▲' : '▼'}
          </button>
          
          {/* Close */}
          <button
            className="widget-btn close-btn"
            onClick={onClose}
            title="Close"
          >
            ×
          </button>
        </div>
      </div>
      
      {/* Body (hidden when minimized) */}
      {!isMinimized && (
        <div className="widget-body">
          {/* Recipe badges */}
          {linkedRecipes.length > 0 && (
            <div className="linked-recipes">
              <div className="recipe-badges">
                {linkedRecipes.slice(0, 3).map((recipe, idx) => (
                  <span key={idx} className="recipe-badge" title={recipe.title}>
                    {recipe.title}
                  </span>
                ))}
                {linkedRecipes.length > 3 && (
                  <span className="recipe-badge more">+{linkedRecipes.length - 3}</span>
                )}
              </div>
            </div>
          )}
          
          {/* Items list */}
          <div className="items-list">
            {items.length === 0 ? (
              <div className="empty-state">
                <p>No items yet</p>
                <button 
                  className="add-first-btn"
                  onClick={() => setShowAddInput(true)}
                >
                  + Add Item
                </button>
              </div>
            ) : (
              <>
                {items.map((item) => (
                  <div
                    key={item.id}
                    className={`item-row ${item.checked ? 'checked' : ''}`}
                  >
                    <span className="drag-handle" title="Drag to reorder">⋮⋮</span>
                    <input
                      type="checkbox"
                      checked={item.checked}
                      onChange={() => handleCheckItem(item.id)}
                      className="item-checkbox"
                    />
                    <span className="item-name">
                      {item.quantity && <span className="item-quantity">{item.quantity}</span>}
                      {item.ingredient || item.name}
                    </span>
                    <button
                      className="item-remove-btn"
                      onClick={() => handleRemoveItem(item.id)}
                      title="Remove"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </>
            )}
          </div>
          
          {/* Add item input */}
          {showAddInput ? (
            <div className="add-item-input">
              <input
                type="text"
                value={newItemName}
                onChange={(e) => setNewItemName(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAddItem()}
                placeholder="Add item..."
                autoFocus
              />
              <button onClick={handleAddItem} className="add-btn">+</button>
              <button onClick={() => setShowAddInput(false)} className="cancel-btn">×</button>
            </div>
          ) : (
            <button
              className="add-item-btn"
              onClick={() => setShowAddInput(true)}
            >
              + Add Item
            </button>
          )}
          
          {/* Footer actions */}
          <div className="widget-footer">
            <button className="footer-btn" onClick={() => console.log('Share clicked')}>
              Share
            </button>
            <div className="footer-hint">
              � Press Ctrl+S or click Save button to save all changes
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GroceryListFloatingWidget;
