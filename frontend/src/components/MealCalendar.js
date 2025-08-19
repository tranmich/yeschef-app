import React from 'react';
import { useDroppable, useDraggable } from '@dnd-kit/core';
import './MealCalendar.css';

const MealCalendar = ({ mealPlan, onRemoveRecipe, onMoveRecipe }) => {
    const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
    const mealTypes = ['breakfast', 'lunch', 'dinner']; // Removed 'snacks' - desserts can go in any meal section

    const formatDayName = (day) => {
        return day.charAt(0).toUpperCase() + day.slice(1);
    };

    const formatMealType = (mealType) => {
        return mealType.charAt(0).toUpperCase() + mealType.slice(1);
    };

    // Draggable planned recipe component
    const PlannedRecipe = ({ recipe, index, day, mealType }) => {
        const draggableId = `planned-${day}-${mealType}-${index}`;
        
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
                sourceDay: day,
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
                <button
                    onClick={(e) => {
                        e.stopPropagation();
                        onRemoveRecipe(day, mealType, index);
                    }}
                    className="remove-recipe-btn"
                    title="Remove recipe"
                >
                    ❌
                </button>
            </div>
        );
    };

    const MealSlot = ({ day, mealType, recipes }) => {
        const { isOver, setNodeRef } = useDroppable({
            id: `${day}-${mealType}`,
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
                    <span className="meal-type">{formatMealType(mealType)}</span>
                    {recipes.length > 0 && (
                        <span className="recipe-count">({recipes.length})</span>
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
                                    key={`${day}-${mealType}-${index}`}
                                    recipe={recipe}
                                    index={index}
                                    day={day}
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
                <h3>📅 Weekly Meal Plan</h3>
                <div className="week-info">
                    {getCurrentWeekRange()}
                </div>
            </div>
            
            <div className="calendar-grid">
                {/* Header row with meal types */}
                <div className="calendar-row header-row">
                    <div className="day-header">Day</div>
                    {mealTypes.map(mealType => (
                        <div key={mealType} className="meal-header">
                            {formatMealType(mealType)}
                        </div>
                    ))}
                </div>

                {/* Calendar days */}
                {days.map(day => (
                    <div key={day} className="calendar-row">
                        <div className="day-label">
                            <span className="day-name">{formatDayName(day)}</span>
                            <span className="day-date">{getDayDate(day)}</span>
                        </div>
                        
                        {mealTypes.map(mealType => (
                            <MealSlot
                                key={`${day}-${mealType}`}
                                day={day}
                                mealType={mealType}
                                recipes={mealPlan[day]?.[mealType] || []}
                            />
                        ))}
                    </div>
                ))}
            </div>

            <div className="calendar-footer">
                <div className="calendar-stats">
                    <span>Total Recipes: {getTotalRecipeCount(mealPlan)}</span>
                    <span>Meals Planned: {getPlannedMealsCount(mealPlan)}</span>
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
    Object.values(mealPlan).forEach(day => {
        Object.values(day).forEach(meals => {
            count += meals.length;
        });
    });
    return count;
};

const getPlannedMealsCount = (mealPlan) => {
    let count = 0;
    Object.values(mealPlan).forEach(day => {
        Object.values(day).forEach(meals => {
            if (meals.length > 0) count++;
        });
    });
    return count;
};

export default MealCalendar;
