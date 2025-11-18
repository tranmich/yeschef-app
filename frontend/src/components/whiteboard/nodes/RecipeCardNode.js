/**
 * Recipe Card Node
 * ================
 * React Flow node for displaying full-size recipe cards
 * Can be standalone or child of meal plan container
 * 
 * Features:
 * - Full-size recipe display with thumbnail
 * - Tag management with inline editing
 * - Draggable (React Flow native)
 * - Click to view details
 * - Hover effects
 * 
 * Author: GitHub Copilot
 * Date: November 5, 2025 (Updated: November 9, 2025)
 */

import React, { useState } from 'react';
import TagSystem from '../TagSystem';
import './RecipeCardNode.css';

const RecipeCardNode = ({ id, data, selected }) => {
  const recipe = data.recipe || {};
  const tags = data.tags || [];
  const commentCount = data.commentCount || 0;
  const hasNewComments = data.hasNewComments || false;
  const [isEditingTags, setIsEditingTags] = useState(false);
  
  const recipeName = recipe.title || recipe.name || 'Unnamed Recipe';
  const recipeImage = recipe.image_url || recipe.image;
  const recipeDescription = recipe.description || '';
  const prepTime = recipe.prep_time;
  const cookTime = recipe.cook_time;

  const handleCardClick = (e) => {
    // Don't trigger if clicking on tag editor or tags
    if (e.target.closest('.recipe-tags') || e.target.closest('.tag-system')) return;
    
    e.stopPropagation();
    data.onClick?.(id, recipe);
  };

  const handleTagClick = (e, tag) => {
    e.stopPropagation();
    data.onTagFilterClick?.(tag);
  };

  const handleTagsChange = (newTags) => {
    data.onTagsChange?.(id, newTags);
  };

  const handleAddTagClick = (e) => {
    e.stopPropagation();
    setIsEditingTags(true);
  };

  return (
    <div
      className={`recipe-card-node ${selected ? 'selected' : ''}`}
      onClick={handleCardClick}
      title={recipeName}
    >
      {/* Comment Badge */}
      {commentCount > 0 && (
        <div className={`comment-badge ${hasNewComments ? 'has-new' : ''}`}>
          💬 {commentCount}
        </div>
      )}
      
      {/* Thumbnail */}
      <div className="recipe-thumbnail">
        {recipeImage ? (
          <img 
            src={recipeImage} 
            alt={recipeName}
            onError={(e) => {
              e.target.style.display = 'none';
              e.target.nextElementSibling.style.display = 'flex';
            }}
          />
        ) : null}
        <div 
          className="recipe-placeholder" 
          style={{ display: recipeImage ? 'none' : 'flex' }}
        >
          🍳
        </div>
      </div>

      {/* Content */}
      <div className="recipe-content">
        <h3 className="recipe-title">{recipeName}</h3>
        
        {recipeDescription && (
          <p className="recipe-description">{recipeDescription}</p>
        )}

        {/* Metadata */}
        {(prepTime || cookTime) && (
          <div className="recipe-metadata">
            {prepTime && (
              <span className="metadata-item">
                ⏱️ {prepTime} min
              </span>
            )}
            {cookTime && (
              <span className="metadata-item">
                🔥 {cookTime} min
              </span>
            )}
          </div>
        )}
      </div>

      {/* Tags */}
      <div className="recipe-tags nodrag">
        {/* Show tag editor when selected and editing */}
        {selected && isEditingTags ? (
          <div className="tag-editor-wrapper" onClick={(e) => e.stopPropagation()}>
            <TagSystem 
              tags={tags}
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
            {tags.length > 0 && tags.map((tag, index) => (
              <span
                key={index}
                className="recipe-tag"
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
    </div>
  );
};

export default RecipeCardNode;
