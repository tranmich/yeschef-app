import React, { useState, useEffect } from 'react';
import MealCalendar from './MealCalendar';
import GroceryListGenerator from './GroceryListGenerator';
import FavoritesPanel from './FavoritesPanel';
import DraggableRecipeCard from './DraggableRecipeCard';
import './MealPlannerView.css';

const MealPlannerView = ({ 
    searchResults = [], 
    isVisible = false, 
    isCompactMode = false, 
    chatRecipes = [],
    mealPlan,
    setMealPlan
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
    const [favorites, setFavorites] = useState([]);
    const [loading, setLoading] = useState(false);

    // Load saved meal plans on component mount
    useEffect(() => {
        loadSavedMealPlans();
        loadFavorites();
    }, []);

    const loadSavedMealPlans = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/meal-plans');
            const data = await response.json();
            
            if (data.success) {
                setSavedMealPlans(data.meal_plans);
            }
        } catch (error) {
            console.error('Error loading meal plans:', error);
        }
    };

    const loadFavorites = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/favorites');
            const data = await response.json();
            
            if (data.success) {
                setFavorites(data.favorites);
            }
        } catch (error) {
            console.error('Error loading favorites:', error);
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
            const response = await fetch('http://localhost:5000/api/meal-plans', {
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
            const response = await fetch(`http://localhost:5000/api/meal-plans/${planId}`);
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

    const toggleFavorite = async (recipe) => {
        try {
            const response = await fetch('http://localhost:5000/api/favorites', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    recipe_id: recipe.id || recipe.recipe_id
                })
            });

            const data = await response.json();

            if (data.success) {
                loadFavorites(); // Reload favorites list
            }
        } catch (error) {
            console.error('Error toggling favorite:', error);
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
            <div className="meal-planner-header">
                <h2>🍽️ Meal Planner</h2>
                
                <div className="meal-planner-controls">
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
                        className="save-plan-btn"
                    >
                        {loading ? '💾 Saving...' : '💾 Save Plan'}
                    </button>
                    
                    <button 
                        onClick={() => setShowGroceryList(!showGroceryList)}
                        className="grocery-list-btn"
                    >
                        🛒 {showGroceryList ? 'Hide' : 'Show'} Grocery List
                    </button>
                    
                    <button 
                        onClick={clearMealPlan}
                        className="clear-plan-btn"
                    >
                        🗑️ Clear Plan
                    </button>
                </div>
            </div>

            <div className="meal-planner-content">
                <div className={`meal-planner-layout ${isCompactMode ? 'compact' : ''}`}>
                        {/* Recipe Sources Panel - Hide in compact mode */}
                        {!isCompactMode && (
                            <div className="recipe-sources-panel">
                                <div className="search-results-section">
                                    <h3>🔍 Search Results</h3>
                                    <div className="draggable-recipes scrollable">
                                        {searchResults.map(recipe => (
                                            <DraggableRecipeCard
                                                key={`search-${recipe.id}`}
                                                recipe={recipe}
                                                id={recipe.id.toString()}
                                                onToggleFavorite={() => toggleFavorite(recipe)}
                                                compact={true}
                                            />
                                        ))}
                                        {searchResults.length === 0 && (
                                            <p className="no-results">
                                                {isCompactMode ? 
                                                    "Drag recipes from the chat to add to your meal plan" :
                                                    "Search for recipes or drag from chat to add to your meal plan"
                                                }
                                            </p>
                                        )}
                                    </div>
                                </div>

                                <FavoritesPanel
                                    favorites={favorites}
                                    onToggleFavorite={toggleFavorite}
                                    onRefresh={loadFavorites}
                                />
                            </div>
                        )}

                        {/* Meal Calendar */}
                        <div className="meal-calendar-section">
                            <MealCalendar
                                mealPlan={currentMealPlan}
                                onRemoveRecipe={removeRecipeFromMealPlan}
                            />
                        </div>

                        {/* Saved Plans Panel - Compact in sidebar mode */}
                        <div className={`saved-plans-panel ${isCompactMode ? 'compact' : ''}`}>
                            <h3>📋 Saved Plans</h3>
                            <div className="saved-plans-list">
                                {savedMealPlans.map(plan => (
                                    <div key={plan.id} className="saved-plan-item">
                                        <div className="plan-info">
                                            <strong>{plan.plan_name}</strong>
                                            <small>{plan.week_start_date}</small>
                                        </div>
                                        <button
                                            onClick={() => loadMealPlan(plan.id)}
                                            className="load-plan-btn"
                                        >
                                            📂 Load
                                        </button>
                                    </div>
                                ))}
                                {savedMealPlans.length === 0 && (
                                    <p className="no-saved-plans">
                                        No saved meal plans yet
                                    </p>
                                )}
                            </div>
                        </div>
                    </div>
                </div>

            {/* Grocery List */}
            {showGroceryList && (
                <GroceryListGenerator
                    recipeIds={getAllRecipeIds()}
                    onClose={() => setShowGroceryList(false)}
                />
            )}
        </div>
    );
};

export default MealPlannerView;
