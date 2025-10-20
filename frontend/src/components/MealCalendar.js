import React from 'react';
import { useDroppable, useDraggable } from '@dnd-kit/core';
import './MealCalendar.css';

const MealCalendar = ({ mealPlan, onRemoveRecipe, onAddDay, onRemoveDay, onRenameDay }) => {
    // Safety check for mealPlan structure
    if (!mealPlan || !mealPlan.days) {
        return (
            <div className="meal-calendar">
                <div className="calendar-header">
                    <h3>📅 Loading Meal Plan...</h3>
                </div>
                <div style={{ padding: '2rem', textAlign: 'center' }}>
                    <p>Initializing meal planner...</p>
                </div>
            </div>
        );
    }

    // Get dynamic days from the meal plan
    const days = mealPlan.dayOrder || Object.keys(mealPlan.days || {});
    
    const formatDayName = (dayId) => {
        return mealPlan.days[dayId]?.name || dayId;
    };

    // Draggable planned recipe component - Simplified
    const PlannedRecipe = ({ recipe, index, dayId }) => {
        const draggableId = `planned-${dayId}-${index}`;

        const {
            attributes,
            listeners,
            setNodeRef,
            transform,
            isDragging,
        } = useDraggable({
            id: draggableId,
            data: {
                type: 'planned-recipe',
                recipe: recipe,
                sourceDay: dayId,
                sourceIndex: index
            },
        });

        const style = {
            transform: transform ? `translate3d(${transform.x}px, ${transform.y}px, 0)` : undefined,
            opacity: isDragging ? 0.5 : 1,
            zIndex: isDragging ? 1000 : 1,
        };

        return (
            <div
                ref={setNodeRef}
                style={style}
                className={`planned-recipe ${isDragging ? 'dragging' : ''}`}
                {...listeners}
                {...attributes}
            >
                <button
                    onClick={(e) => {
                        e.stopPropagation();
                        onRemoveRecipe(dayId, index);
                    }}
                    className="remove-recipe-btn"
                    title="Remove recipe from meal plan"
                    aria-label="Remove recipe"
                >
                    ✕
                </button>
                <div className="recipe-info">
                    <span className="recipe-title" title={recipe.title}>
                        {recipe.title}
                    </span>
                    {recipe.hands_on_time && (
                        <span className="recipe-time">
                            ⏱️ {recipe.hands_on_time}
                        </span>
                    )}
                    {recipe.servings && (
                        <span className="recipe-servings">
                            👥 {recipe.servings}
                        </span>
                    )}
                </div>
            </div>
        );
    };

    // Simplified Day Slot - No meal types, just recipes per day
    const DaySlot = ({ dayId, recipes }) => {
        const { isOver, setNodeRef } = useDroppable({
            id: dayId,
        });

        const style = {
            backgroundColor: isOver ? '#e8f5e9' : 'white',
            border: isOver ? '2px dashed #AAC6AD' : '2px solid #e5e7eb',
        };

        return (
            <div
                ref={setNodeRef}
                className="day-slot"
                style={style}
            >
                <div className="day-slot-content">
                    {recipes.length === 0 ? (
                        <div className="empty-slot">
                            <span className="drop-hint">Drop recipes here</span>
                        </div>
                    ) : (
                        <div className="planned-recipes">
                            {recipes.map((recipe, index) => (
                                <PlannedRecipe
                                    key={`${dayId}-${index}`}
                                    recipe={recipe}
                                    index={index}
                                    dayId={dayId}
                                />
                            ))}
                        </div>
                    )}
                </div>
            </div>
        );
    };

    return (
        <div className="meal-calendar">
            <div className="calendar-header">
                <h3>📅 Meal Plan</h3>
            </div>

            <div className="calendar-grid-simple">
                {/* Render days dynamically - Simplified structure */}
                {days.map(dayId => {
                    const dayData = mealPlan.days[dayId];
                    if (!dayData) return null;
                    
                    return (
                        <div key={dayId} className="day-card">
                            {/* Day Header */}
                            <div className="day-header">
                                <span 
                                    className="day-name editable"
                                    onClick={() => {
                                        const newName = prompt('Rename day:', dayData.name);
                                        if (newName && newName.trim() && onRenameDay) {
                                            onRenameDay(dayId, newName.trim());
                                        }
                                    }}
                                    title="Click to rename"
                                >
                                    {dayData.name}
                                </span>
                                {(dayData.recipes?.length > 0) && (
                                    <span className="recipe-count">{dayData.recipes.length} {dayData.recipes.length === 1 ? 'recipe' : 'recipes'}</span>
                                )}
                                {days.length > 1 && (
                                    <button
                                        onClick={() => onRemoveDay && onRemoveDay(dayId)}
                                        className="remove-day-btn"
                                        title="Remove day"
                                    >
                                        ✕
                                    </button>
                                )}
                            </div>

                            {/* Day Content - Just recipes, no meal types */}
                            <DaySlot
                                dayId={dayId}
                                recipes={dayData.recipes || []}
                            />
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

// Helper function to count total recipes
const getTotalRecipeCount = (mealPlan) => {
    if (!mealPlan || !mealPlan.days) return 0;
    return Object.values(mealPlan.days).reduce((total, day) => {
        return total + (day.recipes?.length || 0);
    }, 0);
};

export default MealCalendar;
