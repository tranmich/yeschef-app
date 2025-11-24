/**
 * RecipeCardNode - Custom React Flow Node
 * ========================================
 * A beautiful recipe card component for the whiteboard canvas
 * 
 * Features:
 * - Recipe image thumbnail
 * - Recipe name
 * - Cook time, prep time
 * - Category badge
 * - Tag management with inline editing
 * - Hover effects
 * - Click to view details
 * 
 * Updated: November 9, 2025 - Added tag support
 */

import React, { useState, useRef, useEffect } from 'react';
import { Handle, Position } from '@xyflow/react';
import TagSystem from '../TagSystem';
import { useRecipeCache } from '../../../contexts/RecipeCacheContext';
import './RecipeCardNode.css';

// 12 Pastel color options for recipe cards
const COLOR_OPTIONS = [
  { name: 'White', value: '#FFFFFF' },
  { name: 'Soft Yellow', value: '#FEF3C7' },
  { name: 'Peach', value: '#FED7AA' },
  { name: 'Light Pink', value: '#FCE7F3' },
  { name: 'Lavender', value: '#E9D5FF' },
  { name: 'Sky Blue', value: '#DBEAFE' },
  { name: 'Mint', value: '#D1FAE5' },
  { name: 'Sage', value: '#D1F4E0' },
  { name: 'Pale Green', value: '#E0F2D9' },
  { name: 'Light Coral', value: '#FFE4E1' },
  { name: 'Cream', value: '#FAF3DD' },
  { name: 'Light Gray', value: '#F3F4F6' },
];

const RecipeCardNode = ({ data, id, selected }) => {
  // 🆕 USE RECIPE CACHE - Single source of truth!
  const { getRecipe } = useRecipeCache();
  
  // Extract node-specific data
  const {
    recipe_id,
    object_id,
    onClick,
    onDelete,
    onTagsChange,
    onTagFilterClick,
    onColorChange,
    tags,
    commentCount,
    hasNewComments,
    backgroundColor
  } = data;
  
  // 🆕 GET RECIPE FROM CACHE (not from node data!)
  const recipe = getRecipe(recipe_id) || {};
  
  // Extract recipe properties from cached recipe
  const name = recipe.title || 'Untitled Recipe';
  const image_url = recipe.image_url;
  const prep_time = recipe.prep_time;
  const cook_time = recipe.cook_time;
  const total_time = recipe.total_time;
  const category = recipe.category;

  // Tag editor state
  const [isEditingTags, setIsEditingTags] = useState(false);
  
  // Color picker state
  const [showColorPicker, setShowColorPicker] = useState(false);
  const [cardColor, setCardColor] = useState(backgroundColor || '#FFFFFF');
  const colorPickerRef = useRef(null);

  // Click outside to close color picker
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (colorPickerRef.current && !colorPickerRef.current.contains(event.target)) {
        setShowColorPicker(false);
      }
    };

    if (showColorPicker) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }
  }, [showColorPicker]);

  // Handle card click
  const handleClick = (e) => {
    // Don't trigger if clicking on tag editor or tags
    if (e.target.closest('.recipe-card-tags') || e.target.closest('.tag-system')) return;
    
    if (onClick) {
      onClick(recipe_id);
    }
  };

  // Handle delete button click
  const handleDelete = (e) => {
    e.stopPropagation(); // Prevent card click event
    
    if (window.confirm(`Remove "${name}" from canvas?`)) {
      if (onDelete) {
        onDelete(id, recipe_id, object_id); // Pass object_id for database deletion
      }
    }
  };

  // Format time display
  const formatTime = (minutes) => {
    if (!minutes) return null;
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
  };

  // Get category color
  const getCategoryColor = (cat) => {
    const colors = {
      'breakfast': '#f59e0b',
      'lunch': '#10b981',
      'dinner': '#3b82f6',
      'dessert': '#ec4899',
      'snack': '#8b5cf6',
      'appetizer': '#f97316',
      'salad': '#84cc16',
      'soup': '#06b6d4',
      'beverage': '#6366f1',
      'default': '#6b7280'
    };
    return colors[cat?.toLowerCase()] || colors.default;
  };

  // Tag handlers
  const handleTagClick = (e, tag) => {
    e.stopPropagation();
    if (onTagFilterClick) {
      onTagFilterClick(tag);
    }
  };

  const handleTagsChange = (newTags) => {
    if (onTagsChange) {
      onTagsChange(id, newTags);
    }
  };

  const handleAddTagClick = (e) => {
    e.stopPropagation();
    setIsEditingTags(true);
  };

  // Color picker handlers
  const handleColorChange = (color) => {
    setCardColor(color);
    setShowColorPicker(false);
    
    if (onColorChange) {
      onColorChange(id, color, object_id);
    }
  };

  // Fallback image if none provided - use a food-themed emoji or solid color
  const displayImage = image_url || null;

  return (
    <div className="recipe-card-wrapper" style={{ backgroundColor: cardColor }}>
      
      {/* Header - Universal drag handle + actions */}
      <div className="recipe-card-header" title="Drag to move recipe">
        <div className="header-left">
          {/* Comment Badge in header */}
          {commentCount > 0 && (
            <div className={`comment-badge-header ${hasNewComments ? 'has-new' : ''}`}>
              💬 {commentCount}
            </div>
          )}
        </div>
        <div className="header-right nodrag">
          {/* Color picker - only show when selected */}
          {selected && (
            <div className="color-picker-wrapper" ref={colorPickerRef}>
              <button
                className="header-btn color-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  setShowColorPicker(!showColorPicker);
                }}
                title="Change color"
              >
                🎨
              </button>
              {showColorPicker && (
                <div className="color-picker-dropdown">
                  {COLOR_OPTIONS.map((color) => (
                    <button
                      key={color.value}
                      className="color-option"
                      style={{ backgroundColor: color.value }}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleColorChange(color.value);
                      }}
                      title={color.name}
                    >
                      {cardColor === color.value && '✓'}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
          {/* Delete button */}
          <button 
            className="header-btn delete-btn"
            onClick={handleDelete}
            title="Remove from canvas"
          >
            ×
          </button>
        </div>
      </div>
      
      {/* Main recipe card */}
      <div className="recipe-card-node">

      {/* Image */}
      <div className="recipe-card-image">
        {displayImage ? (
          <img 
            src={displayImage} 
            alt={name}
            onError={(e) => {
              // If image fails, hide it and show placeholder
              e.target.style.display = 'none';
            }}
          />
        ) : (
          <div style={{
            width: '100%',
            height: '100%',
            background: 'linear-gradient(135deg, #AAC6AD 0%, #98b89b 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '4rem',
            color: 'white',
            fontWeight: '300'
          }}>
            ◈
          </div>
        )}
        
        {/* Category badge */}
        {category && (
          <div 
            className="recipe-card-badge"
            style={{ backgroundColor: getCategoryColor(category) }}
          >
            {category}
          </div>
        )}
      </div>

      {/* Content */}
      <div className="recipe-card-content">
        <h3 className="recipe-card-title">{name || 'Untitled Recipe'}</h3>
        
        {/* Time info removed - reduces clutter, available in View Recipe */}
      </div>

      {/* View Recipe Button - Centered, Mint Green */}
      <div className="recipe-card-view-section">
        <button 
          className="recipe-view-btn nodrag"
          onClick={(e) => {
            e.stopPropagation();
            if (onClick) onClick(recipe_id);
          }}
        >
          View Recipe
        </button>
      </div>

      {/* Tags Section */}
      <div className="recipe-card-tags nodrag">
        {/* Show tag editor when selected and editing */}
        {selected && isEditingTags ? (
          <div className="tag-editor-wrapper" onClick={(e) => e.stopPropagation()}>
            <TagSystem 
              tags={tags || []}
              onChange={handleTagsChange}
              placeholder="Add tags..."
              allowCustom={true}
            />
            <button 
              className="close-tag-editor"
              onClick={(e) => {
                e.stopPropagation();
                setIsEditingTags(false);
              }}
            >
              Done
            </button>
          </div>
        ) : (
          <>
            {/* Display tags as clickable pills */}
            {tags && tags.length > 0 && tags.map((tag, index) => (
              <span
                key={index}
                className="recipe-card-tag"
                onClick={(e) => handleTagClick(e, tag)}
                title={`Click to filter by "${tag}"`}
              >
                {tag}
              </span>
            ))}
            
            {/* Add tag button (only show when selected) */}
            {selected && (
              <button 
                className="add-tag-btn"
                onClick={handleAddTagClick}
                title="Add tags"
              >
                + Add Tag
              </button>
            )}
          </>
        )}
      </div>

      {/* Connection handles (for future linking features) */}
      <Handle
        type="source"
        position={Position.Right}
        id="recipe-output"
        style={{ opacity: 0 }}
      />
      <Handle
        type="target"
        position={Position.Left}
        id="recipe-input"
        style={{ opacity: 0 }}
      />
      </div>
    </div>
  );
};

export default RecipeCardNode;
