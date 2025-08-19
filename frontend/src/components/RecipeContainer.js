import React, { useState, useEffect } from 'react';
import { useDroppable } from '@dnd-kit/core';
import DraggableRecipeCard from './DraggableRecipeCard';
import './RecipeContainer.css';

const RecipeContainer = ({ searchResults = [], onAddRecipe, droppedRecipes = [] }) => {
    const [containerRecipes, setContainerRecipes] = useState([]);
    
    // Update container when recipes are dropped from parent component
    useEffect(() => {
        if (droppedRecipes.length > 0) {
            setContainerRecipes(droppedRecipes);
        }
    }, [droppedRecipes]);
    
    const { isOver, setNodeRef } = useDroppable({
        id: 'recipe-container',
    });

    const addRecipeToContainer = (recipe) => {
        // Check if recipe is already in container
        const exists = containerRecipes.find(r => r.id === recipe.id);
        if (!exists) {
            const newRecipes = [...containerRecipes, recipe];
            setContainerRecipes(newRecipes);
            if (onAddRecipe) {
                onAddRecipe(recipe, newRecipes);
            }
        }
    };

    const removeRecipeFromContainer = (recipeId) => {
        const newRecipes = containerRecipes.filter(r => r.id !== recipeId);
        setContainerRecipes(newRecipes);
        if (onAddRecipe) {
            onAddRecipe(null, newRecipes); // Signal removal
        }
    };

    const clearContainer = () => {
        setContainerRecipes([]);
        if (onAddRecipe) {
            onAddRecipe(null, []); // Signal clear
        }
    };

    const style = {
        backgroundColor: isOver ? '#e8f5e8' : 'white',
        border: isOver ? '2px dashed #4caf50' : '1px solid #e0e0e0',
        borderRadius: '8px',
        transition: 'all 0.2s ease'
    };

    return (
        <div className="recipe-container">
            <div className="container-header">
                <h3>📦 Recipe Container</h3>
                <div className="header-actions">
                    <span className="recipe-count">
                        {containerRecipes.length} recipe{containerRecipes.length !== 1 ? 's' : ''}
                    </span>
                    {containerRecipes.length > 0 && (
                        <button
                            onClick={clearContainer}
                            className="clear-container-btn"
                            title="Clear all recipes"
                        >
                            🗑️ Clear
                        </button>
                    )}
                </div>
            </div>
            
            <div 
                ref={setNodeRef}
                className="container-drop-zone"
                style={style}
            >
                <div className="container-recipes">
                    {containerRecipes.map(recipe => (
                        <div key={`container-${recipe.id}`} className="container-recipe-item">
                            <DraggableRecipeCard
                                recipe={recipe}
                                id={`container-${recipe.id}`}
                                compact={true}
                            />
                            <button
                                onClick={() => removeRecipeFromContainer(recipe.id)}
                                className="remove-recipe-btn"
                                title="Remove from container"
                            >
                                ❌
                            </button>
                        </div>
                    ))}
                    
                    {containerRecipes.length === 0 && (
                        <div className="empty-container">
                            <div className="drop-hint">
                                {isOver ? 
                                    "Drop recipe here!" : 
                                    "Drag recipes from chat to collect them here"
                                }
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default RecipeContainer;
