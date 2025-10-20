import { useState } from 'react';

/**
 * Custom hook for managing meal planning state and operations
 * Simplified structure: Days contain recipes directly (no breakfast/lunch/dinner)
 */
export const useMealPlanner = () => {
    // Simplified meal plan state - just days with recipes
    const [mealPlan, setMealPlan] = useState({
        days: {
            'day1': { 
                name: 'Day 1',
                recipes: []  // Direct array of recipes, no meal types
            }
        },
        dayOrder: ['day1']
    });

    // Visibility state
    const [showMealPlanner, setShowMealPlanner] = useState(false);

    // Add recipe to day (simplified - no meal type)
    const addRecipeToMeal = (dayId, recipe) => {
        if (dayId && mealPlan.days[dayId]) {
            setMealPlan(prev => ({
                ...prev,
                days: {
                    ...prev.days,
                    [dayId]: {
                        ...prev.days[dayId],
                        recipes: [...prev.days[dayId].recipes, recipe]
                    }
                }
            }));
            return true;
        }
        return false;
    };

    // Remove recipe from day
    const removeRecipeFromMeal = (dayId, recipeIndex) => {
        if (dayId && mealPlan.days[dayId]) {
            setMealPlan(prev => ({
                ...prev,
                days: {
                    ...prev.days,
                    [dayId]: {
                        ...prev.days[dayId],
                        recipes: prev.days[dayId].recipes.filter((_, index) => index !== recipeIndex)
                    }
                }
            }));
            return true;
        }
        return false;
    };

    // Move recipe between days (simplified)
    const moveRecipe = (sourceDayId, sourceIndex, targetDayId, recipe) => {
        if (!sourceDayId || sourceIndex === undefined || !targetDayId) {
            return false;
        }

        // Don't move if source and target are the same
        if (sourceDayId === targetDayId) {
            return false;
        }

        setMealPlan(prev => {
            const newMealPlan = { ...prev };
            
            // Remove from source day
            newMealPlan.days = { ...newMealPlan.days };
            newMealPlan.days[sourceDayId] = {
                ...newMealPlan.days[sourceDayId],
                recipes: newMealPlan.days[sourceDayId].recipes.filter((_, index) => index !== sourceIndex)
            };

            // Add to target day
            newMealPlan.days[targetDayId] = {
                ...newMealPlan.days[targetDayId],
                recipes: [...newMealPlan.days[targetDayId].recipes, recipe]
            };

            return newMealPlan;
        });

        return true;
    };

    // Clear entire day (simplified)
    const clearDay = (dayId) => {
        if (dayId && mealPlan.days[dayId]) {
            setMealPlan(prev => ({
                ...prev,
                days: {
                    ...prev.days,
                    [dayId]: {
                        ...prev.days[dayId],
                        recipes: []
                    }
                }
            }));
            return true;
        }
        return false;
    };

    // Clear entire meal plan (simplified)
    const clearAllMeals = () => {
        setMealPlan({
            days: {
                'day1': { 
                    name: 'Day 1',
                    recipes: []
                }
            },
            dayOrder: ['day1']
        });
    };

    // Get all recipes in meal plan (simplified)
    const getAllMealPlanRecipes = () => {
        const allRecipes = [];
        Object.values(mealPlan.days || {}).forEach(day => {
            allRecipes.push(...(day.recipes || []));
        });
        return allRecipes;
    };

    // Get recipes for specific day (simplified)
    const getDayRecipes = (dayId) => {
        if (!mealPlan.days[dayId]) return [];
        return mealPlan.days[dayId].recipes || [];
    };

    // Toggle meal planner visibility
    const toggleMealPlanner = (forceValue) => {
        if (typeof forceValue === 'boolean') {
            setShowMealPlanner(forceValue);
        } else {
            setShowMealPlanner(!showMealPlanner);
        }
    };

    // Get meal plan statistics (simplified)
    const getMealPlanStats = () => {
        const stats = {
            totalRecipes: 0,
            totalDays: 0,
            daysWithRecipes: 0,
            emptyDays: 0
        };

        Object.values(mealPlan.days || {}).forEach(day => {
            stats.totalDays++;
            const recipeCount = day.recipes?.length || 0;
            stats.totalRecipes += recipeCount;

            if (recipeCount > 0) {
                stats.daysWithRecipes++;
            } else {
                stats.emptyDays++;
            }
        });

        return stats;
    };

    return {
        // State
        mealPlan,
        setMealPlan,
        showMealPlanner,

        // Actions
        addRecipeToMeal,
        removeRecipeFromMeal,
        moveRecipe,
        clearDay,
        clearAllMeals,
        toggleMealPlanner,

        // Getters
        getAllMealPlanRecipes,
        getDayRecipes,
        getMealPlanStats
    };
};
