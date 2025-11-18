/**
 * Tag System Component
 * ====================
 * Autocomplete tag input with predefined tags
 * 
 * Features:
 * - Tag autocomplete with suggestions
 * - Predefined tag categories
 * - Custom user tags
 * - Visual tag pills
 * - Add/remove tags
 * 
 * Author: GitHub Copilot
 * Date: November 9, 2025
 */

import React, { useState, useRef, useEffect } from 'react';
import './TagSystem.css';

// Predefined tag categories for YesChef
const PREDEFINED_TAGS = {
  'Meal Type': ['breakfast', 'lunch', 'dinner', 'snack', 'dessert'],
  'Speed': ['under-15min', 'under-30min', 'quick', 'make-ahead', 'slow-cooker'],
  'Difficulty': ['easy', 'medium', 'advanced', 'kid-can-help'],
  'Diet': ['vegetarian', 'vegan', 'gluten-free', 'dairy-free', 'low-carb', 'keto'],
  'Occasion': ['weeknight', 'party', 'holiday', 'meal-prep', 'date-night'],
  'Method': ['one-pan', 'instant-pot', 'slow-cooker', 'no-cook', 'grill', 'air-fryer'],
  'Family': ['kid-friendly', 'toddler-approved', 'picky-eater', 'crowd-pleaser'],
  'Main Ingredient': ['chicken', 'beef', 'pork', 'fish', 'pasta', 'rice', 'vegetarian', 'seafood']
};

const TagSystem = ({ tags = [], onChange, placeholder = 'Add tag...', allowCustom = true }) => {
  const [inputValue, setInputValue] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef(null);
  const suggestionsRef = useRef(null);

  // Get all predefined tags as flat array
  const allPredefinedTags = Object.values(PREDEFINED_TAGS).flat();

  // Get all existing tags from the component's current state
  const existingTags = tags || [];

  // Filter suggestions based on input
  useEffect(() => {
    if (inputValue.length > 0) {
      const searchTerm = inputValue.toLowerCase();
      
      // Filter predefined tags that match input and aren't already added
      const filtered = allPredefinedTags.filter(tag => 
        tag.toLowerCase().includes(searchTerm) && 
        !existingTags.includes(tag)
      );

      setSuggestions(filtered);
      setShowSuggestions(filtered.length > 0 || allowCustom);
      setSelectedIndex(0);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  }, [inputValue, existingTags, allPredefinedTags, allowCustom]);

  // Handle tag addition
  const addTag = (tag) => {
    const trimmedTag = tag.trim().toLowerCase();
    
    if (!trimmedTag) return;
    if (existingTags.includes(trimmedTag)) {
      // Tag already exists
      setInputValue('');
      setShowSuggestions(false);
      return;
    }

    // Add tag
    const newTags = [...existingTags, trimmedTag];
    onChange(newTags);
    setInputValue('');
    setShowSuggestions(false);
  };

  // Handle tag removal
  const removeTag = (tagToRemove) => {
    const newTags = existingTags.filter(tag => tag !== tagToRemove);
    onChange(newTags);
  };

  // Handle input change
  const handleInputChange = (e) => {
    setInputValue(e.target.value);
  };

  // Handle key down
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      
      if (suggestions.length > 0 && selectedIndex >= 0) {
        // Add selected suggestion
        addTag(suggestions[selectedIndex]);
      } else if (allowCustom && inputValue.trim()) {
        // Add custom tag
        addTag(inputValue);
      }
    } else if (e.key === 'Backspace' && inputValue === '' && existingTags.length > 0) {
      // Remove last tag on backspace
      removeTag(existingTags[existingTags.length - 1]);
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(prev => Math.min(prev + 1, suggestions.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(prev => Math.max(prev - 1, 0));
    } else if (e.key === 'Escape') {
      setShowSuggestions(false);
    }
  };

  // Handle suggestion click
  const handleSuggestionClick = (tag) => {
    addTag(tag);
  };

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        suggestionsRef.current && 
        !suggestionsRef.current.contains(event.target) &&
        inputRef.current &&
        !inputRef.current.contains(event.target)
      ) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="tag-system">
      {/* Tag Pills */}
      <div className="tag-pills-container">
        {existingTags.map((tag, index) => (
          <span key={index} className="tag-pill">
            <span className="tag-text">{tag}</span>
            <button 
              className="tag-remove"
              onClick={() => removeTag(tag)}
              title={`Remove ${tag}`}
            >
              ×
            </button>
          </span>
        ))}
        
        {/* Tag Input */}
        <div className="tag-input-wrapper">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            onFocus={() => inputValue && setShowSuggestions(true)}
            placeholder={existingTags.length === 0 ? placeholder : ''}
            className="tag-input"
          />
          
          {/* Suggestions Dropdown */}
          {showSuggestions && (
            <div ref={suggestionsRef} className="tag-suggestions">
              {suggestions.length > 0 ? (
                <>
                  {suggestions.map((tag, index) => (
                    <div
                      key={index}
                      className={`tag-suggestion ${index === selectedIndex ? 'selected' : ''}`}
                      onClick={() => handleSuggestionClick(tag)}
                      onMouseEnter={() => setSelectedIndex(index)}
                    >
                      🏷️ {tag}
                    </div>
                  ))}
                </>
              ) : allowCustom && inputValue.trim() ? (
                <div className="tag-suggestion create-new">
                  ➕ Create "{inputValue.trim()}"
                </div>
              ) : null}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TagSystem;
