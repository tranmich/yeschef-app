import { useState } from 'react';

/**
 * Custom hook for managing meal planning state and operations
 */
export const useMealPlanner = () => {
    // Enhanced meal plan state with dynamic days and meal types
    const [mealPlan, setMealPlan] = useState({
        days: {
            'day1': { 
                name: 'Day 1',
                meals: {
                    'breakfast': { name: 'Breakfast', recipes: [] },
                    'lunch': { name: 'Lunch', recipes: [] },
                    'dinner': { name: 'Dinner', recipes: [] }
                }
            }
        },
        dayOrder: ['day1']
    });

    // Visibility state
    const [showMealPlanner, setShowMealPlanner] = useState(false);

    // Add recipe to meal plan
    const addRecipeToMeal = (dayId, mealType, recipe) => {
        if (dayId && mealType && mealPlan.days[dayId] && mealPlan.days[dayId].meals[mealType]) {
            setMealPlan(prev => ({
                ...prev,
                days: {
                    ...prev.days,
                    [dayId]: {
                        ...prev.days[dayId],
                        meals: {
                            ...prev.days[dayId].meals,
                            [mealType]: {
                                ...prev.days[dayId].meals[mealType],
                                recipes: [...prev.days[dayId].meals[mealType].recipes, recipe]
                            }
                        }
                    }
                }
            }));
            return true;
        }
        return false;
    };

    // Remove recipe from meal plan
    const removeRecipeFromMeal = (dayId, mealType, recipeIndex) => {
        if (dayId && mealType && mealPlan.days[dayId] && mealPlan.days[dayId].meals[mealType]) {
            setMealPlan(prev => ({
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
            return true;
        }
        return false;
    };

    // Move recipe between meal slots
    const moveRecipe = (sourceDayId, sourceMealType, sourceIndex, targetDayId, targetMealType, recipe) => {
        if (!sourceDayId || !sourceMealType || sourceIndex === undefined || !targetDayId || !targetMealType) {
            return false;
        }

        // Don't move if source and target are the same
        if (sourceDayId === targetDayId && sourceMealType === targetMealType) {
            return false;
        }

        setMealPlan(prev => {
            const newMealPlan = { ...prev };
            
            // Remove from source
            newMealPlan.days = { ...newMealPlan.days };
            newMealPlan.days[sourceDayId] = {
                ...newMealPlan.days[sourceDayId],
                meals: {
                    ...newMealPlan.days[sourceDayId].meals,
                    [sourceMealType]: {
                        ...newMealPlan.days[sourceDayId].meals[sourceMealType],
                        recipes: newMealPlan.days[sourceDayId].meals[sourceMealType].recipes.filter((_, index) => index !== sourceIndex)
                    }
                }
            };

            // Add to target
            newMealPlan.days[targetDayId] = {
                ...newMealPlan.days[targetDayId],
                meals: {
                    ...newMealPlan.days[targetDayId].meals,
                    [targetMealType]: {
                        ...newMealPlan.days[targetDayId].meals[targetMealType],
                        recipes: [...newMealPlan.days[targetDayId].meals[targetMealType].recipes, recipe]
                    }
                }
            };

            return newMealPlan;
        });

        return true;
    };

    // Clear specific meal
    const clearMeal = (dayId, mealType) => {
        if (dayId && mealType && mealPlan.days[dayId] && mealPlan.days[dayId].meals[mealType]) {
            setMealPlan(prev => ({
                ...prev,
                days: {
                    ...prev.days,
                    [dayId]: {
                        ...prev.days[dayId],
                        meals: {
                            ...prev.days[dayId].meals,
                            [mealType]: {
                                ...prev.days[dayId].meals[mealType],
                                recipes: []
                            }
                        }
                    }
                }
            }));
            return true;
        }
        return false;
    };

    // Clear entire day
    const clearDay = (dayId) => {
        if (dayId && mealPlan.days[dayId]) {
            setMealPlan(prev => ({
                ...prev,
                days: {
                    ...prev.days,
                    [dayId]: {
                        ...prev.days[dayId],
                        meals: Object.keys(prev.days[dayId].meals).reduce((acc, mealType) => {
                            acc[mealType] = {
                                ...prev.days[dayId].meals[mealType],
                                recipes: []
                            };
                            return acc;
                        }, {})
                    }
                }
            }));
            return true;
        }
        return false;
    };

    // Clear entire meal plan
    const clearAllMeals = () => {
        setMealPlan({
            days: {
                'day1': { 
                    name: 'Day 1',
                    meals: {
                        'breakfast': { name: 'Breakfast', recipes: [] },
                        'lunch': { name: 'Lunch', recipes: [] },
                        'dinner': { name: 'Dinner', recipes: [] }
                    }
                }
            },
            dayOrder: ['day1']
        });
    };

    // Get all recipes in meal plan
    const getAllMealPlanRecipes = () => {
        const allRecipes = [];
        Object.values(mealPlan.days || {}).forEach(day => {
            Object.values(day.meals || {}).forEach(meal => {
                allRecipes.push(...(meal.recipes || []));
            });
        });
        return allRecipes;
    };

    // Get recipes for specific day
    const getDayRecipes = (dayId) => {
        if (!mealPlan.days[dayId]) return [];

        const dayRecipes = [];
        Object.values(mealPlan.days[dayId].meals || {}).forEach(meal => {
            dayRecipes.push(...(meal.recipes || []));
        });
        return dayRecipes;
    };

    // Toggle meal planner visibility
    const toggleMealPlanner = (forceValue) => {
        if (typeof forceValue === 'boolean') {
            setShowMealPlanner(forceValue);
        } else {
            setShowMealPlanner(!showMealPlanner);
        }
    };

    // Get meal plan statistics
    const getMealPlanStats = () => {
        const stats = {
            totalRecipes: 0,
            totalDays: 0,
            completeDays: 0,
            emptyDays: 0,
            byMealType: {
                breakfast: 0,
                lunch: 0,
                dinner: 0,
                snacks: 0
            }
        };

        Object.keys(mealPlan).forEach(day => {
            stats.totalDays++;
            let dayHasRecipes = false;
            let dayMealCount = 0;

            Object.keys(mealPlan[day]).forEach(mealType => {
                const mealRecipes = mealPlan[day][mealType].length;
                stats.totalRecipes += mealRecipes;
                stats.byMealType[mealType] += mealRecipes;

                if (mealRecipes > 0) {
                    dayHasRecipes = true;
                    dayMealCount++;
                }
            });

            if (dayHasRecipes) {
                if (dayMealCount >= 3) { // Has breakfast, lunch, and dinner
                    stats.completeDays++;
                }
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
        clearMeal,
        clearDay,
        clearAllMeals,
        toggleMealPlanner,

        // Getters
        getAllMealPlanRecipes,
        getDayRecipes,
        getMealPlanStats
    };
};
