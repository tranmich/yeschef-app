import React from 'react';
import { useDraggable } from '@dnd-kit/core';
import './DraggableRecipeCard.css';

const DraggableRecipeCard = ({ recipe, id, onToggleFavorite, isFavorite = false, compact = false }) => {
    const {
        attributes,
        listeners,
        setNodeRef,
        transform,
        isDragging,
    } = useDraggable({
        id: id,
    });

    const style = transform ? {
        transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`,
        opacity: isDragging ? 0.5 : 1,
        zIndex: isDragging ? 1000 : 1,
    } : undefined;

    const formatTime = (time) => {
        if (!time) return '';
        return time.toString().replace(/[^\d\w\s]/g, '');
    };

    const truncateText = (text, maxLength = 100) => {
        if (!text) return '';
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    };

    return (
        <div
            ref={setNodeRef}
            style={style}
            className={`draggable-recipe-card ${isDragging ? 'dragging' : ''} ${compact ? 'compact' : ''}`}
            {...listeners}
            {...attributes}
        >
            <div className="recipe-card-header">
                <h4 className="recipe-title" title={recipe.title}>
                    {recipe.title}
                </h4>
                
                <button
                    className={`favorite-btn ${isFavorite ? 'favorited' : ''}`}
                    onClick={(e) => {
                        e.stopPropagation();
                        if (onToggleFavorite) onToggleFavorite(recipe);
                    }}
                    title={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
                >
                    {isFavorite ? '⭐' : '☆'}
                </button>
            </div>

            <div className="recipe-card-content">
                {recipe.description && (
                    <p className="recipe-description">
                        {truncateText(recipe.description, 80)}
                    </p>
                )}

                <div className="recipe-meta">
                    {recipe.hands_on_time && (
                        <span className="recipe-time" title="Hands-on time">
                            ⏱️ {formatTime(recipe.hands_on_time)}
                        </span>
                    )}
                    
                    {recipe.total_time && recipe.total_time !== recipe.hands_on_time && (
                        <span className="recipe-total-time" title="Total time">
                            🕐 {formatTime(recipe.total_time)}
                        </span>
                    )}
                    
                    {recipe.servings && (
                        <span className="recipe-servings" title="Servings">
                            👥 {recipe.servings}
                        </span>
                    )}
                    
                    {recipe.category && (
                        <span className="recipe-category" title="Category">
                            🏷️ {recipe.category}
                        </span>
                    )}
                </div>

                {/* Show ingredients count if available */}
                {recipe.ingredients && (
                    <div className="recipe-ingredients-info">
                        <span className="ingredients-count">
                            🥗 {Array.isArray(recipe.ingredients) 
                                ? recipe.ingredients.length 
                                : recipe.ingredients.split(',').length} ingredients
                        </span>
                    </div>
                )}
            </div>

            <div className="recipe-card-footer">
                <div className="drag-hint">
                    🖱️ Drag to meal plan
                </div>
            </div>
        </div>
    );
};

export default DraggableRecipeCard;
