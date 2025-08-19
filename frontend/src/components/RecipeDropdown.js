import React, { useState } from 'react';
import { useDraggable } from '@dnd-kit/core';
import './RecipeDropdown.css';

const RecipeDropdown = ({ recipe, index }) => {
  const [open, setOpen] = useState(false);

  // Create a robust unique ID for dragging
  const draggableId = recipe.id || `recipe-${recipe.name || recipe.title || 'unknown'}-${index || 0}`;

  // Make only the drag handle draggable
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    isDragging,
  } = useDraggable({
    id: draggableId,
    data: {
      type: 'recipe',
      recipe: recipe,
    },
  });

  const style = {
    transform: transform ? `translate3d(${transform.x}px, ${transform.y}px, 0)` : undefined,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div 
      className="recipe-dropdown"
      ref={setNodeRef}
      style={style}
      {...listeners}
      {...attributes}
    >
      <div className="recipe-dropdown-header">
        <button 
          className="dropdown-toggle" 
          onClick={(e) => {
            e.stopPropagation(); // Prevent drag when clicking dropdown
            setOpen(o => !o);
          }}
        >
          <span>{open ? '▼' : '▶'} </span>
          <strong>{recipe.name || recipe.title}</strong>
        </button>
      </div>
      {open && (
        <div className="dropdown-content">
          {recipe.description && <p className="dropdown-description">{recipe.description}</p>}
          <h5>Ingredients:</h5>
          <ul className="dropdown-ingredients">
            {recipe.ingredients && (
              Array.isArray(recipe.ingredients) 
                ? recipe.ingredients.map((ing, idx) => (
                    <li key={idx}>{ing.ingredient || ing}</li>
                  ))
                : <li>{recipe.ingredients}</li>
            )}
          </ul>
          <h5>Instructions:</h5>
          <div className="dropdown-instructions">
            {recipe.instructions && (
              Array.isArray(recipe.instructions) 
                ? (
                  <ol>
                    {recipe.instructions.map((step, idx) => (
                      <li key={idx}>{step.text || step}</li>
                    ))}
                  </ol>
                )
                : (
                  // Parse string instructions into numbered steps
                  (() => {
                    const instructionText = recipe.instructions;
                    // Split by numbered steps (1., 2., etc.) or periods followed by capital letters
                    const steps = instructionText
                      .split(/(?=\d+\.)/)
                      .filter(step => step.trim())
                      .map(step => step.replace(/^\d+\./, '').trim())
                      .filter(step => step.length > 0);
                    
                    if (steps.length > 1) {
                      return (
                        <ol>
                          {steps.map((step, idx) => (
                            <li key={idx}>{step}</li>
                          ))}
                        </ol>
                      );
                    } else {
                      // If no numbered steps found, display as formatted text
                      return <div className="instruction-text">{instructionText}</div>;
                    }
                  })()
                )
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default RecipeDropdown;
