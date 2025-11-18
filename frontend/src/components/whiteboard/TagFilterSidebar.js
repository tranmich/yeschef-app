/**
 * Tag Filter Sidebar
 * ==================
 * Sidebar for filtering whiteboard by tags
 * 
 * Features:
 * - Display all tags used on whiteboard
 * - Click tag to filter
 * - Multi-tag filtering (AND logic)
 * - Tag count indicators
 * - Clear all filters
 * - Categorized tags
 * 
 * Author: GitHub Copilot
 * Date: November 9, 2025
 */

import React, { useMemo } from 'react';
import './TagFilterSidebar.css';

// Tag categories from TagSystem
const TAG_CATEGORIES = {
  'Meal Type': ['breakfast', 'lunch', 'dinner', 'snack', 'dessert'],
  'Speed': ['under-15min', 'under-30min', 'quick', 'make-ahead', 'slow-cooker'],
  'Difficulty': ['easy', 'medium', 'advanced', 'kid-can-help'],
  'Diet': ['vegetarian', 'vegan', 'gluten-free', 'dairy-free', 'low-carb', 'keto'],
  'Occasion': ['weeknight', 'party', 'holiday', 'meal-prep', 'date-night'],
  'Method': ['one-pan', 'instant-pot', 'slow-cooker', 'no-cook', 'grill', 'air-fryer'],
  'Family': ['kid-friendly', 'toddler-approved', 'picky-eater', 'crowd-pleaser'],
  'Main Ingredient': ['chicken', 'beef', 'pork', 'fish', 'pasta', 'rice', 'vegetarian', 'seafood']
};

const TagFilterSidebar = ({ 
  nodes = [], 
  selectedTags = [], 
  onTagToggle, 
  onClearAll,
  isOpen = true,
  onToggleSidebar
}) => {
  // Calculate tag usage across all nodes
  const tagStats = useMemo(() => {
    const stats = {};
    
    nodes.forEach(node => {
      const nodeTags = node.data?.tags || [];
      nodeTags.forEach(tag => {
        if (!stats[tag]) {
          stats[tag] = 0;
        }
        stats[tag]++;
      });
    });
    
    return stats;
  }, [nodes]);

  // Get all unique tags sorted by usage
  const allTags = useMemo(() => {
    return Object.keys(tagStats).sort((a, b) => tagStats[b] - tagStats[a]);
  }, [tagStats]);

  // Categorize tags
  const categorizedTags = useMemo(() => {
    const categorized = {};
    const uncategorized = [];

    allTags.forEach(tag => {
      let foundCategory = false;
      
      for (const [category, categoryTags] of Object.entries(TAG_CATEGORIES)) {
        if (categoryTags.includes(tag)) {
          if (!categorized[category]) {
            categorized[category] = [];
          }
          categorized[category].push(tag);
          foundCategory = true;
          break;
        }
      }
      
      if (!foundCategory) {
        uncategorized.push(tag);
      }
    });

    if (uncategorized.length > 0) {
      categorized['Custom'] = uncategorized;
    }

    return categorized;
  }, [allTags]);

  const handleTagClick = (tag) => {
    onTagToggle(tag);
  };

  const isTagSelected = (tag) => {
    return selectedTags.includes(tag);
  };

  const filteredNodeCount = useMemo(() => {
    if (selectedTags.length === 0) return nodes.length;
    
    return nodes.filter(node => {
      const nodeTags = node.data?.tags || [];
      // AND logic: node must have ALL selected tags
      return selectedTags.every(tag => nodeTags.includes(tag));
    }).length;
  }, [nodes, selectedTags]);

  // Always render both, use CSS to show/hide
  return (
    <>
      {/* Main sidebar with open class */}
      <div className={`tag-filter-sidebar ${isOpen ? 'open' : ''}`}>
        {/* Header */}
        <div className="tag-sidebar-header">
          <div className="tag-sidebar-title">
            <span className="tag-icon">🏷️</span>
            <h3>Filter by Tag</h3>
          </div>
          <button 
            className="tag-sidebar-close"
            onClick={onToggleSidebar}
            title="Hide sidebar"
          >
            ×
          </button>
        </div>

      {/* Filter Summary */}
      {selectedTags.length > 0 && (
        <div className="tag-filter-summary">
          <div className="filter-info">
            <span className="filter-count">{filteredNodeCount}</span>
            <span className="filter-text">
              {filteredNodeCount === 1 ? 'recipe' : 'recipes'} match
              {selectedTags.length > 1 ? 'es all filters' : 'es'}
            </span>
          </div>
          <button 
            className="clear-filters-btn"
            onClick={onClearAll}
          >
            Clear All
          </button>
        </div>
      )}

      {/* No Tags Message */}
      {allTags.length === 0 && (
        <div className="no-tags-message">
          <p>No tags yet!</p>
          <p className="no-tags-hint">
            Add tags to recipes to organize your whiteboard.
          </p>
        </div>
      )}

      {/* Tag Categories */}
      <div className="tag-categories">
        {Object.entries(categorizedTags).map(([category, categoryTags]) => (
          <div key={category} className="tag-category">
            <h4 className="category-title">{category}</h4>
            <div className="category-tags">
              {categoryTags.map(tag => (
                <button
                  key={tag}
                  className={`tag-filter-pill ${isTagSelected(tag) ? 'selected' : ''}`}
                  onClick={() => handleTagClick(tag)}
                  title={`${tagStats[tag]} recipe${tagStats[tag] !== 1 ? 's' : ''}`}
                >
                  <span className="tag-name">{tag}</span>
                  <span className="tag-count">{tagStats[tag]}</span>
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Footer Tips */}
      <div className="tag-sidebar-footer">
        <p className="filter-tip">
          💡 <strong>Tip:</strong> Select multiple tags to narrow results
        </p>
      </div>
    </div>
    </>
  );
};

export default TagFilterSidebar;
