import { useState } from 'react';
import { PointerSensor, useSensor, useSensors } from '@dnd-kit/core';

/**
 * Custom hook for managing drag and drop operations
 */
export const useDragAndDrop = (onRecipeDropped, onRecipeAddedToContainer, onRecipeMoved) => {
    // Drag state
    const [draggedRecipe, setDraggedRecipe] = useState(null);
    const [isDragging, setIsDragging] = useState(false);

    // Configure drag sensors with distance threshold
    const sensors = useSensors(
        useSensor(PointerSensor, {
            activationConstraint: {
                distance: 8,
            },
        })
    );

    // Drag handlers
    const handleDragStart = (event) => {
        // Get recipe directly from the drag data instead of searching by ID
        const recipe = event.active.data.current?.recipe;
        setDraggedRecipe(recipe);
        setIsDragging(true);

        console.log('🎯 Drag started:', recipe?.title || 'Unknown recipe');
    };

    const handleDragEnd = (event) => {
        const { over, active } = event;

        // Only process if there's a valid drop target AND dragged recipe
        if (over && draggedRecipe) {
            const dropZoneId = over.id;
            const draggedItemData = active.data.current;

            console.log('🎯 Drag ended:', {
                recipe: draggedRecipe?.title,
                dropZone: dropZoneId,
                draggedItemData
            });

            // Check if dropping into recipe container
            if (dropZoneId === 'recipe-container') {
                if (onRecipeAddedToContainer) {
                    onRecipeAddedToContainer(draggedRecipe);
                    console.log('✅ Recipe added to container');
                }
            } else if (draggedItemData?.type === 'planned-recipe') {
                // Moving an existing recipe from one day to another (simplified - no meal types)
                const targetDay = dropZoneId;  // Just the day ID now
                const { sourceDay, sourceIndex } = draggedItemData;

                if (onRecipeMoved && sourceDay !== targetDay) {
                    onRecipeMoved(sourceDay, sourceIndex, targetDay, draggedRecipe);
                    console.log('✅ Recipe moved between days');
                }
            } else {
                // Adding a new recipe to meal plan from chat/container (simplified - just day)
                const day = dropZoneId;  // Just the day ID

                // Call the meal plan callback function
                if (onRecipeDropped) {
                    const success = onRecipeDropped(day, draggedRecipe);
                    if (success) {
                        console.log('✅ Recipe successfully added to meal plan');
                    } else {
                        console.log('❌ Failed to add recipe to meal plan');
                    }
                }
            }
        } else {
            console.log('🎯 Drag ended without valid drop target');
        }

        // Reset drag state
        setDraggedRecipe(null);
        setIsDragging(false);
    };

    const handleDragCancel = () => {
        console.log('🎯 Drag cancelled');
        // Reset drag state if drag is cancelled
        setDraggedRecipe(null);
        setIsDragging(false);
    };

    // Drag over handler for visual feedback (simplified)
    const handleDragOver = (event) => {
        const { over } = event;

        if (over && draggedRecipe) {
            // Add visual feedback for valid drop zones
            const dropZoneId = over.id;  // Just the day ID

            // You can emit events or update state for visual feedback here
            console.log('🎯 Dragging over day:', dropZoneId);
        }
    };

    // Check if a recipe is currently being dragged
    const isRecipeDragging = (recipeId) => {
        return isDragging && draggedRecipe?.id === recipeId;
    };

    // Get current drag state
    const getDragState = () => ({
        isDragging,
        draggedRecipe,
        draggedRecipeId: draggedRecipe?.id || null,
        draggedRecipeTitle: draggedRecipe?.title || null
    });

    return {
        // Sensors for DndContext
        sensors,

        // State
        draggedRecipe,
        isDragging,

        // Handlers
        handleDragStart,
        handleDragEnd,
        handleDragCancel,
        handleDragOver,

        // Utilities
        isRecipeDragging,
        getDragState
    };
};
