import React from 'react';
import { useDroppable, useDraggable } from '@dnd-kit/core';
import './MealCalendar.css';

const MealCalendar = ({ mealPlan, onRemoveRecipe, onAddDay, onRemoveDay, onAddMealType, onRemoveMealType, onRenameDay, onRenameMealType }) => {
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

    // Get dynamic days and meal types from the meal plan
    const days = mealPlan.dayOrder || Object.keys(mealPlan.days || {});
    
    const formatDayName = (dayId) => {
        return mealPlan.days[dayId]?.name || dayId;
    };

    const formatMealType = (mealType, dayId) => {
        return mealPlan.days[dayId]?.meals[mealType]?.name || mealType;
    };

    const getMealTypes = (dayId) => {
        return Object.keys(mealPlan.days[dayId]?.meals || {});
    };

    // Draggable planned recipe component
    const PlannedRecipe = ({ recipe, index, dayId, mealType }) => {
        const draggableId = `planned-${dayId}-${mealType}-${index}`;

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
                sourceMealType: mealType,
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
                        onRemoveRecipe(dayId, mealType, index);
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

    const MealSlot = ({ dayId, mealType, recipes, dayData }) => {
        const { isOver, setNodeRef } = useDroppable({
            id: `${dayId}-${mealType}`,
        });

        const style = {
            backgroundColor: isOver ? '#e3f2fd' : 'white',
            border: isOver ? '2px dashed #2196f3' : '1px solid #e0e0e0',
        };

        return (
            <div
                ref={setNodeRef}
                className="meal-slot"
                style={style}
            >
                <div className="meal-slot-header">
                    <span 
                        className="meal-type editable" 
                        onClick={() => {
                            const newName = prompt('Rename meal type:', formatMealType(mealType, dayId));
                            if (newName && newName.trim() && onRenameMealType) {
                                onRenameMealType(dayId, mealType, newName.trim());
                            }
                        }}
                        title="Click to rename"
                    >
                        {formatMealType(mealType, dayId)}
                    </span>
                    {recipes.length > 0 && (
                        <span className="recipe-count">({recipes.length})</span>
                    )}
                    {Object.keys(dayData.meals).length > 1 && (
                        <button
                            onClick={() => onRemoveMealType && onRemoveMealType(dayId, mealType)}
                            className="remove-meal-btn"
                            title="Remove meal type"
                        >
                            ✕
                        </button>
                    )}
                </div>

                <div className="meal-slot-content">
                    {recipes.length === 0 ? (
                        <div className="empty-slot">
                            <span className="drop-hint">Drop recipe here</span>
                        </div>
                    ) : (
                        <div className="planned-recipes">
                            {recipes.map((recipe, index) => (
                                <PlannedRecipe
                                    key={`${dayId}-${mealType}-${index}`}
                                    recipe={recipe}
                                    index={index}
                                    dayId={dayId}
                                    mealType={mealType}
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

            <div className="calendar-grid-dynamic">
                {/* Render days dynamically */}
                {days.map(dayId => {
                    const dayData = mealPlan.days[dayId];
                    if (!dayData) return null;
                    
                    const mealTypes = getMealTypes(dayId);
                    
                    return (
                        <div key={dayId} className="day-column">
                            {/* Day Header */}
                            <div className="day-header-dynamic">
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
                                <div className="day-controls">
                                    <button
                                        onClick={() => {
                                            const mealName = prompt('New meal type name:', 'Snacks');
                                            if (mealName && mealName.trim() && onAddMealType) {
                                                onAddMealType(dayId, mealName.trim());
                                            }
                                        }}
                                        className="add-meal-btn"
                                        title="Add meal type"
                                    >
                                        ➕
                                    </button>
                                    {days.length > 1 && (
                                        <button
                                            onClick={() => onRemoveDay && onRemoveDay(dayId)}
                                            className="remove-day-btn"
                                            title="Remove day"
                                        >
                                            🗑️
                                        </button>
                                    )}
                                </div>
                            </div>

                            {/* Meal Slots */}
                            <div className="day-meals">
                                {mealTypes.map(mealType => (
                                    <MealSlot
                                        key={`${dayId}-${mealType}`}
                                        dayId={dayId}
                                        mealType={mealType}
                                        recipes={dayData.meals[mealType]?.recipes || []}
                                        dayData={dayData}
                                    />
                                ))}
                            </div>
                        </div>
                    );
                })}
            </div>

            <div className="calendar-footer">
                <div className="calendar-stats">
                    <span>Total Recipes: {getTotalRecipeCount(mealPlan)}</span>
                    <span>Days Planned: {days.length}</span>
                </div>
            </div>
        </div>
    );
};

// Helper functions
const getCurrentWeekRange = () => {
    const today = new Date();
    const firstDayOfWeek = today.getDate() - today.getDay() + 1; // Monday
    const monday = new Date(today.setDate(firstDayOfWeek));
    const sunday = new Date(monday);
    sunday.setDate(monday.getDate() + 6);

    return `${monday.toLocaleDateString()} - ${sunday.toLocaleDateString()}`;
};

const getDayDate = (dayName) => {
    const dayIndex = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'].indexOf(dayName);
    const today = new Date();
    const firstDayOfWeek = today.getDate() - today.getDay() + 1; // Monday
    const targetDay = new Date(today.setDate(firstDayOfWeek + dayIndex));

    return targetDay.getDate();
};

const getTotalRecipeCount = (mealPlan) => {
    let count = 0;
    Object.values(mealPlan.days || {}).forEach(day => {
        Object.values(day.meals || {}).forEach(meal => {
            count += (meal.recipes || []).length;
        });
    });
    return count;
};

export default MealCalendar;
