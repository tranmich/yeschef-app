import React, { useState, useEffect } from 'react';
import MealCalendar from './MealCalendar';
import GroceryListGenerator from './GroceryListGenerator';
import RecipeContainer from './RecipeContainer';
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
    setContainerRecipes,
    showGroceryListFromNav,
    setShowGroceryListFromNav
}) => {
    // Use meal plan state from parent if provided, otherwise create local state
    const [localMealPlan, setLocalMealPlan] = useState({
        monday: { breakfast: [], lunch: [], dinner: [] },
        tuesday: { breakfast: [], lunch: [], dinner: [] },
        wednesday: { breakfast: [], lunch: [], dinner: [] },
        thursday: { breakfast: [], lunch: [], dinner: [] },
        friday: { breakfast: [], lunch: [], dinner: [] },
        saturday: { breakfast: [], lunch: [], dinner: [] },
        sunday: { breakfast: [], lunch: [], dinner: [] }
    });

    // Use external meal plan if provided, otherwise use local
    const currentMealPlan = mealPlan || localMealPlan;
    const updateMealPlan = setMealPlan || setLocalMealPlan;

    const [savedMealPlans, setSavedMealPlans] = useState([]);
    const [currentPlanName, setCurrentPlanName] = useState('');
    const [showGroceryList, setShowGroceryList] = useState(false);
    const [showSavedPlansModal, setShowSavedPlansModal] = useState(false);
    const [loading, setLoading] = useState(false);

    // Load saved meal plans on component mount
    useEffect(() => {
        loadSavedMealPlans();
    }, []);

    // Handle grocery list activation from navigation
    useEffect(() => {
        if (showGroceryListFromNav) {
            setShowGroceryList(true);
            setShowGroceryListFromNav?.(false); // Reset the flag
        }
    }, [showGroceryListFromNav, setShowGroceryListFromNav]);

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

    const removeRecipeFromMealPlan = (day, mealType, recipeIndex) => {
        updateMealPlan(prev => ({
            ...prev,
            [day]: {
                ...prev[day],
                [mealType]: prev[day][mealType].filter((_, index) => index !== recipeIndex)
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
                monday: { breakfast: [], lunch: [], dinner: [], snacks: [] },
                tuesday: { breakfast: [], lunch: [], dinner: [], snacks: [] },
                wednesday: { breakfast: [], lunch: [], dinner: [], snacks: [] },
                thursday: { breakfast: [], lunch: [], dinner: [], snacks: [] },
                friday: { breakfast: [], lunch: [], dinner: [], snacks: [] },
                saturday: { breakfast: [], lunch: [], dinner: [], snacks: [] },
                sunday: { breakfast: [], lunch: [], dinner: [], snacks: [] }
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
        Object.values(currentMealPlan).forEach(day => {
            Object.values(day).forEach(meals => {
                meals.forEach(recipe => {
                    recipeIds.push(recipe.id || recipe.recipe_id);
                });
            });
        });
        return recipeIds;
    };

    if (!isVisible) return null;

    return (
        <div className="meal-planner-view">
            {/* New Header with Controls */}
            <div className="meal-planner-header">
                <div className="header-left">
                    <h2>Weekly Meal Planner</h2>
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
                    />
                </div>

                {/* Recipe Container - Bottom area */}
                <RecipeContainer 
                    searchResults={searchResults}
                    droppedRecipes={containerRecipes}
                    onAddRecipe={(recipe, newRecipes) => {
                        if (newRecipes) {
                            setContainerRecipes(newRecipes);
                        }
                    }}
                />
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
