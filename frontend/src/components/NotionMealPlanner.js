import React, { useState, useCallback } from 'react';
import { DndContext, closestCenter, useDraggable, useDroppable } from '@dnd-kit/core';
import { arrayMove, SortableContext, verticalListSortingStrategy, horizontalListSortingStrategy } from '@dnd-kit/sortable';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import './NotionMealPlanner.css';
import { getApiUrl } from '../utils/api';

const NotionMealPlanner = ({ 
    searchResults = [], 
    containerRecipes = [],
    isVisible = false 
}) => {
    // Dynamic meal plan structure
    const [mealPlan, setMealPlan] = useState({
        days: [
            { id: 'day-1', name: 'Day 1' }
        ],
        columns: [
            { id: 'breakfast', name: 'Breakfast' },
            { id: 'lunch', name: 'Lunch' },
            { id: 'dinner', name: 'Dinner' }
        ],
        data: {
            'day-1': {
                'breakfast': [],
                'lunch': [],
                'dinner': []
            }
        }
    });

    // UI State
    const [planName, setPlanName] = useState('');
    const [loading, setLoading] = useState(false);
    const [savedPlans, setSavedPlans] = useState([]);
    const [showSavedPlans, setShowSavedPlans] = useState(false);
    const [editingDay, setEditingDay] = useState(null);
    const [editingColumn, setEditingColumn] = useState(null);

    // Add new day
    const addDay = () => {
        const nextDayNumber = mealPlan.days.length + 1;
        const newDayId = `day-${nextDayNumber}`;
        const newDay = { id: newDayId, name: `Day ${nextDayNumber}` };

        // Create empty data structure for new day
        const newData = { ...mealPlan.data };
        newData[newDayId] = {};
        mealPlan.columns.forEach(column => {
            newData[newDayId][column.id] = [];
        });

        setMealPlan(prev => ({
            ...prev,
            days: [...prev.days, newDay],
            data: newData
        }));
    };

    // Add new column
    const addColumn = () => {
        const columnName = prompt('Enter column name (e.g., "Snacks", "Dessert", "Drinks"):');
        if (!columnName) return;

        const columnId = columnName.toLowerCase().replace(/[^a-z0-9]/g, '_');
        const newColumn = { id: columnId, name: columnName };

        // Add column to all existing days
        const newData = { ...mealPlan.data };
        mealPlan.days.forEach(day => {
            newData[day.id][columnId] = [];
        });

        setMealPlan(prev => ({
            ...prev,
            columns: [...prev.columns, newColumn],
            data: newData
        }));
    };

    // Remove day
    const removeDay = (dayId) => {
        if (mealPlan.days.length === 1) {
            alert('Cannot remove the last day!');
            return;
        }

        if (!window.confirm('Remove this day and all its recipes?')) return;

        const newData = { ...mealPlan.data };
        delete newData[dayId];

        setMealPlan(prev => ({
            ...prev,
            days: prev.days.filter(day => day.id !== dayId),
            data: newData
        }));
    };

    // Remove column
    const removeColumn = (columnId) => {
        if (mealPlan.columns.length === 1) {
            alert('Cannot remove the last column!');
            return;
        }

        if (!window.confirm('Remove this column and all its recipes?')) return;

        const newData = { ...mealPlan.data };
        mealPlan.days.forEach(day => {
            delete newData[day.id][columnId];
        });

        setMealPlan(prev => ({
            ...prev,
            columns: prev.columns.filter(col => col.id !== columnId),
            data: newData
        }));
    };

    // Edit day name
    const editDayName = (dayId, newName) => {
        if (!newName.trim()) return;
        
        setMealPlan(prev => ({
            ...prev,
            days: prev.days.map(day => 
                day.id === dayId ? { ...day, name: newName.trim() } : day
            )
        }));
        setEditingDay(null);
    };

    // Edit column name
    const editColumnName = (columnId, newName) => {
        if (!newName.trim()) return;
        
        setMealPlan(prev => ({
            ...prev,
            columns: prev.columns.map(col => 
                col.id === columnId ? { ...col, name: newName.trim() } : col
            )
        }));
        setEditingColumn(null);
    };

    // Add recipe to cell
    const addRecipeToCell = (dayId, columnId, recipe) => {
        setMealPlan(prev => ({
            ...prev,
            data: {
                ...prev.data,
                [dayId]: {
                    ...prev.data[dayId],
                    [columnId]: [...prev.data[dayId][columnId], recipe]
                }
            }
        }));
    };

    // Remove recipe from cell
    const removeRecipeFromCell = (dayId, columnId, recipeIndex) => {
        setMealPlan(prev => ({
            ...prev,
            data: {
                ...prev.data,
                [dayId]: {
                    ...prev.data[dayId],
                    [columnId]: prev.data[dayId][columnId].filter((_, index) => index !== recipeIndex)
                }
            }
        }));
    };

    // Save meal plan
    const saveMealPlan = async () => {
        if (!planName.trim()) {
            alert('Please enter a plan name');
            return;
        }

        setLoading(true);
        try {
            const response = await fetch(`${getApiUrl()}/api/meal-plans`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    plan_name: planName,
                    meal_data: mealPlan,
                    plan_type: 'notion_style'
                })
            });

            const data = await response.json();
            if (data.success) {
                alert('Meal plan saved successfully!');
                setPlanName('');
                loadSavedPlans();
            } else {
                alert('Error saving plan: ' + data.error);
            }
        } catch (error) {
            alert('Error saving plan: ' + error.message);
        } finally {
            setLoading(false);
        }
    };

    // Load saved plans
    const loadSavedPlans = async () => {
        try {
            const response = await fetch(`${getApiUrl()}/api/meal-plans`);
            const data = await response.json();
            if (data.success) {
                setSavedPlans(data.meal_plans.filter(plan => 
                    plan.meal_data && plan.meal_data.days
                ));
            }
        } catch (error) {
            console.error('Error loading plans:', error);
        }
    };

    // Load specific plan
    const loadPlan = (plan) => {
        if (plan.meal_data && plan.meal_data.days) {
            setMealPlan(plan.meal_data);
            setPlanName(plan.plan_name);
            setShowSavedPlans(false);
        }
    };

    // Clear plan
    const clearPlan = () => {
        if (!window.confirm('Clear the entire meal plan?')) return;

        setMealPlan({
            days: [{ id: 'day-1', name: 'Day 1' }],
            columns: [
                { id: 'breakfast', name: 'Breakfast' },
                { id: 'lunch', name: 'Lunch' },
                { id: 'dinner', name: 'Dinner' }
            ],
            data: {
                'day-1': {
                    'breakfast': [],
                    'lunch': [],
                    'dinner': []
                }
            }
        });
        setPlanName('');
    };

    // Drag and drop handler
    const handleDragEnd = (event) => {
        const { active, over } = event;
        if (!over) return;

        const activeData = active.data.current;
        const overData = over.data.current;

        // Handle recipe drops
        if (activeData?.type === 'recipe' && overData?.type === 'meal-cell') {
            const recipe = activeData.recipe;
            const { dayId, columnId } = overData;
            addRecipeToCell(dayId, columnId, recipe);
        }
    };

    if (!isVisible) return null;

    return (
        <DndContext 
            collisionDetection={closestCenter}
            onDragEnd={handleDragEnd}
        >
            <div className="notion-meal-planner">
                {/* Header */}
                <div className="planner-header">
                    <div className="header-left">
                        <h2>🗓️ Notion-Style Meal Planner</h2>
                        <p className="subtitle">Customize your meal planning with dynamic days and columns</p>
                    </div>
                    
                    <div className="header-controls">
                        <input
                            type="text"
                            placeholder="Plan name..."
                            value={planName}
                            onChange={(e) => setPlanName(e.target.value)}
                            className="plan-name-input"
                        />
                        <button onClick={saveMealPlan} disabled={loading} className="save-btn">
                            💾 Save
                        </button>
                        <button onClick={() => setShowSavedPlans(!showSavedPlans)} className="load-btn">
                            📋 Load
                        </button>
                        <button onClick={clearPlan} className="clear-btn">
                            🗑️ Clear
                        </button>
                    </div>
                </div>

                {/* Meal Plan Grid */}
                <div className="meal-plan-container">
                    <div className="meal-plan-grid">
                        {/* Header Row - Column Names */}
                        <div className="grid-header-row">
                            <div className="day-label-cell">
                                <span>Days</span>
                                <button onClick={addDay} className="add-day-btn" title="Add Day">
                                    ➕
                                </button>
                            </div>
                            
                            {mealPlan.columns.map(column => (
                                <div key={column.id} className="column-header-cell">
                                    {editingColumn === column.id ? (
                                        <input
                                            type="text"
                                            defaultValue={column.name}
                                            onBlur={(e) => editColumnName(column.id, e.target.value)}
                                            onKeyPress={(e) => {
                                                if (e.key === 'Enter') {
                                                    editColumnName(column.id, e.target.value);
                                                }
                                            }}
                                            autoFocus
                                            className="edit-input"
                                        />
                                    ) : (
                                        <span 
                                            onClick={() => setEditingColumn(column.id)}
                                            className="editable-label"
                                        >
                                            {column.name}
                                        </span>
                                    )}
                                    
                                    <div className="column-actions">
                                        <button 
                                            onClick={() => removeColumn(column.id)}
                                            className="remove-column-btn"
                                            title="Remove Column"
                                        >
                                            ❌
                                        </button>
                                    </div>
                                </div>
                            ))}
                            
                            <div className="add-column-cell">
                                <button onClick={addColumn} className="add-column-btn" title="Add Column">
                                    ➕ Add Column
                                </button>
                            </div>
                        </div>

                        {/* Data Rows */}
                        {mealPlan.days.map(day => (
                            <div key={day.id} className="grid-data-row">
                                {/* Day Label */}
                                <div className="day-label-cell">
                                    {editingDay === day.id ? (
                                        <input
                                            type="text"
                                            defaultValue={day.name}
                                            onBlur={(e) => editDayName(day.id, e.target.value)}
                                            onKeyPress={(e) => {
                                                if (e.key === 'Enter') {
                                                    editDayName(day.id, e.target.value);
                                                }
                                            }}
                                            autoFocus
                                            className="edit-input"
                                        />
                                    ) : (
                                        <span 
                                            onClick={() => setEditingDay(day.id)}
                                            className="editable-label"
                                        >
                                            {day.name}
                                        </span>
                                    )}
                                    
                                    <button 
                                        onClick={() => removeDay(day.id)}
                                        className="remove-day-btn"
                                        title="Remove Day"
                                    >
                                        ❌
                                    </button>
                                </div>

                                {/* Meal Cells */}
                                {mealPlan.columns.map(column => (
                                    <MealCell
                                        key={`${day.id}-${column.id}`}
                                        dayId={day.id}
                                        columnId={column.id}
                                        recipes={mealPlan.data[day.id]?.[column.id] || []}
                                        onRemoveRecipe={(index) => removeRecipeFromCell(day.id, column.id, index)}
                                    />
                                ))}
                                
                                <div className="empty-cell"></div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Recipe Sources */}
                <div className="recipe-sources">
                    <h3>📚 Recipe Sources</h3>
                    <div className="sources-grid">
                        {/* Search Results */}
                        {searchResults.length > 0 && (
                            <div className="source-section">
                                <h4>🔍 Search Results</h4>
                                <div className="recipe-list">
                                    {searchResults.slice(0, 6).map(recipe => (
                                        <DraggableRecipe key={recipe.id} recipe={recipe} />
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Container Recipes */}
                        {containerRecipes.length > 0 && (
                            <div className="source-section">
                                <h4>📦 Recipe Container</h4>
                                <div className="recipe-list">
                                    {containerRecipes.slice(0, 6).map(recipe => (
                                        <DraggableRecipe key={recipe.id} recipe={recipe} />
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Helpful message if no sources */}
                        {searchResults.length === 0 && containerRecipes.length === 0 && (
                            <div className="no-sources">
                                <p>🔍 Search for recipes or add them to your container to start planning!</p>
                            </div>
                        )}
                    </div>
                </div>

                {/* Saved Plans Modal */}
                {showSavedPlans && (
                    <div className="saved-plans-modal">
                        <div className="modal-content">
                            <div className="modal-header">
                                <h3>📋 Saved Plans</h3>
                                <button onClick={() => setShowSavedPlans(false)}>❌</button>
                            </div>
                            <div className="plans-list">
                                {savedPlans.map(plan => (
                                    <div key={plan.id} className="plan-item">
                                        <span>{plan.plan_name}</span>
                                        <button onClick={() => loadPlan(plan)}>📂 Load</button>
                                    </div>
                                ))}
                                {savedPlans.length === 0 && (
                                    <p>No Notion-style plans saved yet!</p>
                                )}
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </DndContext>
    );
};

// Meal Cell Component
const MealCell = ({ dayId, columnId, recipes, onRemoveRecipe }) => {
    const { setNodeRef } = useDroppable({
        id: `${dayId}-${columnId}`,
        data: {
            type: 'meal-cell',
            dayId,
            columnId
        }
    });

    return (
        <div ref={setNodeRef} className="meal-cell">
            {recipes.length === 0 ? (
                <div className="empty-meal-cell">
                    <span className="drop-hint">Drop recipe here</span>
                </div>
            ) : (
                <div className="meal-recipes">
                    {recipes.map((recipe, index) => (
                        <div key={`${recipe.id}-${index}`} className="meal-recipe-card">
                            <span className="recipe-title">{recipe.title}</span>
                            <button 
                                onClick={() => onRemoveRecipe(index)}
                                className="remove-recipe-btn"
                            >
                                ❌
                            </button>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

// Draggable Recipe Component
const DraggableRecipe = ({ recipe }) => {
    const {
        attributes,
        listeners,
        setNodeRef,
        transform,
        isDragging,
    } = useDraggable({
        id: `recipe-${recipe.id}`,
        data: {
            type: 'recipe',
            recipe
        }
    });

    const style = {
        transform: transform ? `translate3d(${transform.x}px, ${transform.y}px, 0)` : undefined,
        opacity: isDragging ? 0.5 : 1,
    };

    return (
        <div
            ref={setNodeRef}
            style={style}
            {...listeners}
            {...attributes}
            className="draggable-recipe"
        >
            <span className="recipe-title">{recipe.title}</span>
            <span className="drag-indicator">⋮⋮</span>
        </div>
    );
};

export default NotionMealPlanner;
