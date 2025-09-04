import React, { useState, useEffect } from 'react';
import MealCalendar from './MealCalendar';
import GroceryListGenerator from './GroceryListGenerator';
import DraggableRecipeCard from './DraggableRecipeCard';
import { getApiUrl } from '../utils/api';
import './MealPlannerView.css';

const MealPlannerView = ({
    searchResults = [],
    isVisible = false,
    isCompactMode = false,
    chatRecipes = [],
    mealPlan,
    setMealPlan,
    containerRecipes,
    setContainerRecipes
}) => {
    // Use the meal plan from props (which comes from the hook)
    const currentMealPlan = mealPlan;
    const updateMealPlan = setMealPlan;

    const [savedMealPlans, setSavedMealPlans] = useState([]);
    const [currentPlanName, setCurrentPlanName] = useState('');
    const [showGroceryList, setShowGroceryList] = useState(false);
    const [showSavedPlansModal, setShowSavedPlansModal] = useState(false);
    const [loading, setLoading] = useState(false);

    // Load saved meal plans on component mount
    useEffect(() => {
        loadSavedMealPlans();
    }, []);

    const loadSavedMealPlans = async () => {
        try {
            const response = await fetch(`${getApiUrl()}/api/meal-plans`);
            const data = await response.json();

            if (data.success) {
                setSavedMealPlans(data.meal_plans);
            } else {
                // Gracefully handle disabled/unavailable meal planning system
                console.log('Meal planning system not available:', data.error);
                setSavedMealPlans([]);
            }
        } catch (error) {
            console.error('Error loading meal plans:', error);
            setSavedMealPlans([]);
        }
    };

    const removeRecipeFromMealPlan = (dayId, mealType, recipeIndex) => {
        updateMealPlan(prev => ({
            ...prev,
            days: {
                ...prev.days,
                [dayId]: {
                    ...prev.days[dayId],
                    meals: {
                        ...prev.days[dayId].meals,
                        [mealType]: {
                            ...prev.days[dayId].meals[mealType],
                            recipes: prev.days[dayId].meals[mealType].recipes.filter((_, index) => index !== recipeIndex)
                        }
                    }
                }
            }
        }));
    };

    // Add new day function
    const addNewDay = () => {
        const newDayId = `day${Object.keys(currentMealPlan.days).length + 1}`;
        const dayNumber = Object.keys(currentMealPlan.days).length + 1;
        
        updateMealPlan(prev => ({
            ...prev,
            days: {
                ...prev.days,
                [newDayId]: {
                    name: `Day ${dayNumber}`,
                    meals: {
                        'breakfast': { name: 'Breakfast', recipes: [] },
                        'lunch': { name: 'Lunch', recipes: [] },
                        'dinner': { name: 'Dinner', recipes: [] }
                    }
                }
            },
            dayOrder: [...prev.dayOrder, newDayId]
        }));
    };

    // Remove day function
    const removeDay = (dayId) => {
        if (currentMealPlan.dayOrder.length <= 1) {
            alert('Cannot remove the last day');
            return;
        }
        
        if (window.confirm('Are you sure you want to remove this day and all its meals?')) {
            updateMealPlan(prev => {
                const newDays = { ...prev.days };
                delete newDays[dayId];
                
                return {
                    ...prev,
                    days: newDays,
                    dayOrder: prev.dayOrder.filter(id => id !== dayId)
                };
            });
        }
    };

    // Add new meal type function
    const addMealType = (dayId, mealName = 'New Meal') => {
        const mealId = mealName.toLowerCase().replace(/\s+/g, '');
        
        updateMealPlan(prev => ({
            ...prev,
            days: {
                ...prev.days,
                [dayId]: {
                    ...prev.days[dayId],
                    meals: {
                        ...prev.days[dayId].meals,
                        [mealId]: { name: mealName, recipes: [] }
                    }
                }
            }
        }));
    };

    // Remove meal type function
    const removeMealType = (dayId, mealId) => {
        const mealCount = Object.keys(currentMealPlan.days[dayId].meals).length;
        if (mealCount <= 1) {
            alert('Cannot remove the last meal type');
            return;
        }
        
        if (window.confirm('Are you sure you want to remove this meal type and all its recipes?')) {
            updateMealPlan(prev => {
                const newMeals = { ...prev.days[dayId].meals };
                delete newMeals[mealId];
                
                return {
                    ...prev,
                    days: {
                        ...prev.days,
                        [dayId]: {
                            ...prev.days[dayId],
                            meals: newMeals
                        }
                    }
                };
            });
        }
    };

    // Rename day function
    const renameDay = (dayId, newName) => {
        updateMealPlan(prev => ({
            ...prev,
            days: {
                ...prev.days,
                [dayId]: {
                    ...prev.days[dayId],
                    name: newName
                }
            }
        }));
    };

    // Rename meal type function
    const renameMealType = (dayId, mealId, newName) => {
        updateMealPlan(prev => ({
            ...prev,
            days: {
                ...prev.days,
                [dayId]: {
                    ...prev.days[dayId],
                    meals: {
                        ...prev.days[dayId].meals,
                        [mealId]: {
                            ...prev.days[dayId].meals[mealId],
                            name: newName
                        }
                    }
                }
            }
        }));
    };

    const saveMealPlan = async () => {
        if (!currentPlanName.trim()) {
            alert('Please enter a name for your meal plan');
            return;
        }

        setLoading(true);
        try {
            const response = await fetch(`${getApiUrl()}/api/meal-plans`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    plan_name: currentPlanName,
                    week_start_date: getCurrentWeekStart(),
                    meal_data: currentMealPlan
                })
            });

            const data = await response.json();

            if (data.success) {
                alert('Meal plan saved successfully!');
                setCurrentPlanName('');
                loadSavedMealPlans();
            } else {
                alert('Error saving meal plan: ' + data.error);
            }
        } catch (error) {
            console.error('Error saving meal plan:', error);
            alert('Error saving meal plan');
        } finally {
            setLoading(false);
        }
    };

    const loadMealPlan = async (planId) => {
        setLoading(true);
        try {
            const response = await fetch(`${getApiUrl()}/api/meal-plans/${planId}`);
            const data = await response.json();

            if (data.success) {
                updateMealPlan(data.meal_plan.meal_data);
                setCurrentPlanName(data.meal_plan.plan_name);
            } else {
                alert('Error loading meal plan: ' + data.error);
            }
        } catch (error) {
            console.error('Error loading meal plan:', error);
            alert('Error loading meal plan');
        } finally {
            setLoading(false);
        }
    };

    const clearMealPlan = () => {
        if (window.confirm('Are you sure you want to clear the current meal plan?')) {
            updateMealPlan({
                days: {
                    'day1': { 
                        name: 'Day 1',
                        meals: {
                            'breakfast': { name: 'Breakfast', recipes: [] },
                            'lunch': { name: 'Lunch', recipes: [] },
                            'dinner': { name: 'Dinner', recipes: [] }
                        }
                    },
                    'day2': { 
                        name: 'Day 2',
                        meals: {
                            'breakfast': { name: 'Breakfast', recipes: [] },
                            'lunch': { name: 'Lunch', recipes: [] },
                            'dinner': { name: 'Dinner', recipes: [] }
                        }
                    },
                    'day3': { 
                        name: 'Day 3',
                        meals: {
                            'breakfast': { name: 'Breakfast', recipes: [] },
                            'lunch': { name: 'Lunch', recipes: [] },
                            'dinner': { name: 'Dinner', recipes: [] }
                        }
                    }
                },
                dayOrder: ['day1', 'day2', 'day3']
            });
            setCurrentPlanName('');
        }
    };

    const getCurrentWeekStart = () => {
        const today = new Date();
        const firstDayOfWeek = today.getDate() - today.getDay() + 1; // Monday
        const monday = new Date(today.setDate(firstDayOfWeek));
        return monday.toISOString().split('T')[0];
    };

    const getAllRecipeIds = () => {
        const recipeIds = [];
        Object.values(currentMealPlan.days || {}).forEach(day => {
            Object.values(day.meals || {}).forEach(meal => {
                (meal.recipes || []).forEach(recipe => {
                    recipeIds.push(recipe.id || recipe.recipe_id);
                });
            });
        });
        return recipeIds;
    };

    if (!isVisible) return null;

    return (
        <div className="meal-planner-view">
            {/* Enhanced Header with Controls */}
            <div className="meal-planner-header">
                <div className="header-left">
                    <h2>Custom Meal Planner</h2>
                    <button
                        onClick={addNewDay}
                        className="add-day-btn"
                        title="Add New Day"
                    >
                        ➕ Day
                    </button>
                    <button
                        onClick={clearMealPlan}
                        className="clear-plan-btn-small"
                    >
                        Clear
                    </button>
                </div>

                <div className="header-right">
                    <input
                        type="text"
                        placeholder="Meal plan name..."
                        value={currentPlanName}
                        onChange={(e) => setCurrentPlanName(e.target.value)}
                        className="meal-plan-name-input"
                    />

                    <button
                        onClick={saveMealPlan}
                        disabled={loading || !currentPlanName.trim()}
                        className="save-plan-btn-icon"
                        title="Save Plan"
                    >
                        💾
                    </button>

                    <button
                        onClick={() => setShowSavedPlansModal(true)}
                        className="load-saved-plans-btn"
                    >
                        📋 Load
                    </button>

                    <button
                        onClick={() => setShowGroceryList(!showGroceryList)}
                        className="grocery-list-btn"
                    >
                        🛒 Grocery List
                    </button>
                </div>
            </div>

            <div className="meal-planner-content">
                {/* Meal Calendar - Main area */}
                <div className="meal-calendar-section">
                    <MealCalendar
                        mealPlan={currentMealPlan}
                        onRemoveRecipe={removeRecipeFromMealPlan}
                        onAddDay={addNewDay}
                        onRemoveDay={removeDay}
                        onAddMealType={addMealType}
                        onRemoveMealType={removeMealType}
                        onRenameDay={renameDay}
                        onRenameMealType={renameMealType}
                    />
                </div>
            </div>

            {/* Grocery List */}
            {showGroceryList && (
                <GroceryListGenerator
                    recipeIds={getAllRecipeIds()}
                    onClose={() => setShowGroceryList(false)}
                />
            )}

            {/* Saved Plans Modal */}
            {showSavedPlansModal && (
                <div className="saved-plans-modal-overlay" onClick={() => setShowSavedPlansModal(false)}>
                    <div className="saved-plans-modal" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h3>📋 Saved Meal Plans</h3>
                            <button
                                className="modal-close-btn"
                                onClick={() => setShowSavedPlansModal(false)}
                            >
                                ✕
                            </button>
                        </div>
                        <div className="modal-content">
                            <div className="saved-plans-list">
                                {savedMealPlans.map(plan => (
                                    <div key={plan.id} className="saved-plan-item">
                                        <div className="plan-info">
                                            <strong>{plan.plan_name}</strong>
                                            <small>{plan.week_start_date}</small>
                                        </div>
                                        <button
                                            onClick={() => {
                                                loadMealPlan(plan.id);
                                                setShowSavedPlansModal(false);
                                            }}
                                            className="load-plan-btn"
                                        >
                                            📂 Load
                                        </button>
                                    </div>
                                ))}
                                {savedMealPlans.length === 0 && (
                                    <p className="no-saved-plans">
                                        No saved meal plans yet. Create and save a meal plan to see it here!
                                    </p>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default MealPlannerView;
