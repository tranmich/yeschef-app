/**
 * Meal Plan Container Node
 * =========================
 * React Flow parent node that contains recipe card children
 * 
 * Features:
 * - Editable meal plan name
 * - Auto-resizes to fit children
 * - Drop zone for recipe cards
 * - Generate grocery list from recipes
 * - Delete meal plan
 * 
 * Author: GitHub Copilot
 * Date: November 5, 2025
 */

import React, { useState, useRef, useEffect } from 'react';
import { Handle, Position, NodeResizer } from '@xyflow/react';
import './MealPlanContainerNode.css';

// Color options for meal plan (matching NoteBlock and GroceryList pattern)
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

const MealPlanContainerNode = ({ id, data, selected }) => {
  const [isEditingName, setIsEditingName] = useState(false);
  const [name, setName] = useState(data.name || 'Meal Plan');
  const [isDragOver, setIsDragOver] = useState(false);
  const [backgroundColor, setBackgroundColor] = useState(data.backgroundColor || '#D1FAE5');
  const [showColorPicker, setShowColorPicker] = useState(false);
  const nameInputRef = useRef(null);
  const colorPickerRef = useRef(null);

  // Focus input when editing
  useEffect(() => {
    if (isEditingName && nameInputRef.current) {
      nameInputRef.current.focus();
      nameInputRef.current.select();
    }
  }, [isEditingName]);

  // Update name when data changes
  useEffect(() => {
    setName(data.name || 'Meal Plan');
  }, [data.name]);

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
    // Prevent event from bubbling up to React Flow (which might delete nodes on backspace)
    e.stopPropagation();
    
    if (e.key === 'Enter') {
      setIsEditingName(false);
      if (name !== data.name) {
        data.onNameChange?.(id, name);
      }
    } else if (e.key === 'Escape') {
      setName(data.name || 'Meal Plan');
      setIsEditingName(false);
    }
  };

  const handleDelete = (e) => {
    e.stopPropagation();
    if (window.confirm(`Delete "${name}"?`)) {
      data.onDelete?.(id);
    }
  };

  const handleGenerateGroceryList = (e) => {
    e.stopPropagation();
    data.onGenerateGroceryList?.(id);
  };

  // Drag over handling for drop zone
  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  };

  const recipeCount = data.recipeCount || 0;

  return (
    <>
      {/* Resize handles - show when selected */}
      <NodeResizer
        isVisible={selected}
        minWidth={400}
        minHeight={300}
        handleClassName="custom-resize-handle"
      />

      <div
        className={`meal-plan-container-node ${isDragOver ? 'drag-over' : ''} ${selected ? 'selected' : ''}`}
        style={{ backgroundColor }}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        {/* Header */}
        <div className="node-header">
          <div className="header-left nodrag">
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
                className="name-input"
                maxLength={30}
              />
            ) : (
              <span className="node-title" onClick={handleNameClick}>
                {name}
              </span>
            )}
          </div>
          <div className="header-right nodrag">
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
            <button className="header-btn delete-btn" onClick={handleDelete} title="Delete meal plan">
              ×
            </button>
          </div>
        </div>

        {/* Content area - children render here automatically by React Flow */}
        <div className="node-content">
          {recipeCount === 0 ? (
            <div className="empty-state">
              <p>💡 Drag recipe cards here</p>
              <span className="hint">or add recipes from the toolbar</span>
            </div>
          ) : (
            <div className="recipe-summary">
              <span className="count">{recipeCount}</span>
              <span className="label">{recipeCount === 1 ? 'recipe' : 'recipes'}</span>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="node-footer nodrag">
          <button
            className="footer-btn"
            onClick={handleGenerateGroceryList}
            disabled={recipeCount === 0}
          >
            📋 Generate Grocery List
          </button>
          <div className="footer-hint">
            {recipeCount > 0 && `${recipeCount} ${recipeCount === 1 ? 'recipe' : 'recipes'} selected`}
          </div>
        </div>
      </div>
    </>
  );
};

export default MealPlanContainerNode;
