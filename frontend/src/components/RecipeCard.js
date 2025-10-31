import React from 'react';
import { useDraggable } from '@dnd-kit/core';
import './RecipeCard.css';

const RecipeCard = ({ recipe, onClick }) => {
  // Draggable setup
  const {
    attributes,
    listeners,
    setNodeRef,
    isDragging,
  } = useDraggable({
    id: `recipe-card-${recipe.id}`,
    data: {
      type: 'recipe',
      recipe: recipe
    }
  });

  // Don't apply transform - let DragOverlay handle it
  const style = isDragging ? {
    opacity: 0.4,
    filter: 'grayscale(50%)',
  } : undefined;
  // Format time
  const formatTime = (time) => {
    if (!time) return 'N/A';
    
    // If it's already a formatted string (like "1 hour" or "30 minutes"), return as-is
    if (typeof time === 'string' && (time.includes('hour') || time.includes('min'))) {
      return time;
    }
    
    // Otherwise treat as minutes and format
    const minutes = parseInt(time);
    if (isNaN(minutes)) return 'N/A';
    if (minutes < 60) return `${minutes}mins`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
  };

  // Format servings
  const formatServings = (servings) => {
    if (!servings) return 'N/A';
    return `${servings} people`;
  };

  // Format difficulty
  const formatDifficulty = (difficulty) => {
    if (!difficulty) return 'N/A';
    return difficulty.charAt(0).toUpperCase() + difficulty.slice(1);
  };

  // Construct full image URL
  const getImageUrl = () => {
    let imageUrl = recipe.image_url || recipe.image;
    
    // Fix: Handle corrupted image_url data (Python dict strings from old imports)
    if (imageUrl && typeof imageUrl === 'string' && imageUrl.includes("'contentUrl':")) {
      try {
        // Extract the actual URL from the corrupted dict string
        const match = imageUrl.match(/'contentUrl':\s*'([^']+)'/);
        if (match && match[1]) {
          imageUrl = match[1];
          console.log(`🔧 Fixed corrupted image URL for "${recipe.title}": ${imageUrl}`);
        } else {
          imageUrl = null; // Can't parse, use placeholder
        }
      } catch (e) {
        console.error(`❌ Failed to parse corrupted image URL for "${recipe.title}"`, e);
        imageUrl = null;
      }
    }
    
    // If no valid image URL, return placeholder
    if (!imageUrl) {
      // Use a color that matches our design instead of via.placeholder
      return `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='300'%3E%3Crect fill='%23e5e7eb' width='400' height='300'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='system-ui' font-size='20' fill='%239ca3af'%3ENo Image%3C/text%3E%3C/svg%3E`;
    }
    
    // If it's already a full URL (starts with http), use it as-is
    if (imageUrl.startsWith('http')) {
      return imageUrl;
    }
    
    // If it's a relative path, construct full URL
    const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000';
    const fullUrl = `${apiUrl}${imageUrl}`;
    
    return fullUrl;
  };

  const recipeImage = getImageUrl();
  
  // Get time from various possible fields (recipes use different field names)
  const time = recipe.time_min 
    || recipe.total_time 
    || recipe.hands_on_time 
    || recipe.cooking_time 
    || recipe.cook_time
    || recipe.prep_time;
    
  const servings = recipe.servings;
  const difficulty = recipe.difficulty;

  return (
    <div 
      ref={setNodeRef}
      style={style}
      className={`recipe-card-v2 ${isDragging ? 'dragging' : ''}`}
      {...listeners}
      {...attributes}
    >
      <div className="recipe-image-container" onClick={onClick}>
        <img 
          src={recipeImage} 
          alt={recipe.title || recipe.name}
          className="recipe-image"
          onError={(e) => {
            // Use inline SVG placeholder instead of external service
            const svgPlaceholder = `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='300'%3E%3Crect fill='%23e5e7eb' width='400' height='300'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='system-ui' font-size='20' fill='%239ca3af'%3ENo Image%3C/text%3E%3C/svg%3E`;
            if (e.target.src !== svgPlaceholder) {
              e.target.onerror = null; // Remove error handler
              e.target.src = svgPlaceholder;
            }
          }}
        />
      </div>
      
      <div className="recipe-card-body" onClick={onClick}>
        <h3 className="recipe-card-title">
          {recipe.title || recipe.name}
        </h3>
        
        <div className="recipe-card-meta">
          <span className="meta-item">
            <svg className="meta-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="10" strokeWidth="2"/>
              <path d="M12 6v6l4 2" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            {formatTime(time)}
          </span>
          
          <span className="meta-item">
            <svg className="meta-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" strokeWidth="2" strokeLinecap="round"/>
              <circle cx="9" cy="7" r="4" strokeWidth="2"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87" strokeWidth="2" strokeLinecap="round"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            {formatServings(servings)}
          </span>
          
          <span className="meta-item">
            <svg className="meta-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M12 2L2 7l10 5 10-5-10-5z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M2 17l10 5 10-5M2 12l10 5 10-5" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            {formatDifficulty(difficulty)}
          </span>
        </div>
        
        <button className="view-recipe-button" onClick={(e) => { e.stopPropagation(); onClick(e); }}>
          VIEW RECIPE
        </button>
      </div>
    </div>
  );
};

export default RecipeCard;
