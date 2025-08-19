import { useState } from 'react';

/**
 * Custom hook for managing meal planning state and operations
 */
export const useMealPlanner = () => {
  // Meal plan state with default weekly structure
  const [mealPlan, setMealPlan] = useState({
    monday: { breakfast: [], lunch: [], dinner: [], snacks: [] },
    tuesday: { breakfast: [], lunch: [], dinner: [], snacks: [] },
    wednesday: { breakfast: [], lunch: [], dinner: [], snacks: [] },
    thursday: { breakfast: [], lunch: [], dinner: [], snacks: [] },
    friday: { breakfast: [], lunch: [], dinner: [], snacks: [] },
    saturday: { breakfast: [], lunch: [], dinner: [], snacks: [] },
    sunday: { breakfast: [], lunch: [], dinner: [], snacks: [] }
  });

  // Visibility state
  const [showMealPlanner, setShowMealPlanner] = useState(false);

  // Add recipe to meal plan
  const addRecipeToMeal = (day, mealType, recipe) => {
    if (day && mealType && mealPlan[day] && mealPlan[day][mealType] !== undefined) {
      setMealPlan(prev => ({
        ...prev,
        [day]: {
          ...prev[day],
          [mealType]: [...prev[day][mealType], recipe]
        }
      }));
      return true;
    }
    return false;
  };

  // Remove recipe from meal plan
  const removeRecipeFromMeal = (day, mealType, recipeIndex) => {
    if (day && mealType && mealPlan[day] && mealPlan[day][mealType] !== undefined) {
      setMealPlan(prev => ({
        ...prev,
        [day]: {
          ...prev[day],
          [mealType]: prev[day][mealType].filter((_, index) => index !== recipeIndex)
        }
      }));
      return true;
    }
    return false;
  };

  // Move recipe between meal slots
  const moveRecipe = (sourceDay, sourceMealType, sourceIndex, targetDay, targetMealType, recipe) => {
    if (!sourceDay || !sourceMealType || sourceIndex === undefined || !targetDay || !targetMealType) {
      return false;
    }

    // Don't move if source and target are the same
    if (sourceDay === targetDay && sourceMealType === targetMealType) {
      return false;
    }

    setMealPlan(prev => {
      // Remove from source
      const newMealPlan = { ...prev };
      newMealPlan[sourceDay] = {
        ...newMealPlan[sourceDay],
        [sourceMealType]: newMealPlan[sourceDay][sourceMealType].filter((_, index) => index !== sourceIndex)
      };

      // Add to target
      newMealPlan[targetDay] = {
        ...newMealPlan[targetDay],
        [targetMealType]: [...newMealPlan[targetDay][targetMealType], recipe]
      };

      return newMealPlan;
    });

    return true;
  };

  // Clear specific meal
  const clearMeal = (day, mealType) => {
    if (day && mealType && mealPlan[day] && mealPlan[day][mealType] !== undefined) {
      setMealPlan(prev => ({
        ...prev,
        [day]: {
          ...prev[day],
          [mealType]: []
        }
      }));
      return true;
    }
    return false;
  };

  // Clear entire day
  const clearDay = (day) => {
    if (day && mealPlan[day]) {
      setMealPlan(prev => ({
        ...prev,
        [day]: { breakfast: [], lunch: [], dinner: [], snacks: [] }
      }));
      return true;
    }
    return false;
  };

  // Clear entire meal plan
  const clearAllMeals = () => {
    setMealPlan({
      monday: { breakfast: [], lunch: [], dinner: [], snacks: [] },
      tuesday: { breakfast: [], lunch: [], dinner: [], snacks: [] },
      wednesday: { breakfast: [], lunch: [], dinner: [], snacks: [] },
      thursday: { breakfast: [], lunch: [], dinner: [], snacks: [] },
      friday: { breakfast: [], lunch: [], dinner: [], snacks: [] },
      saturday: { breakfast: [], lunch: [], dinner: [], snacks: [] },
      sunday: { breakfast: [], lunch: [], dinner: [], snacks: [] }
    });
  };

  // Get all recipes in meal plan
  const getAllMealPlanRecipes = () => {
    const allRecipes = [];
    Object.keys(mealPlan).forEach(day => {
      Object.keys(mealPlan[day]).forEach(mealType => {
        allRecipes.push(...mealPlan[day][mealType]);
      });
    });
    return allRecipes;
  };

  // Get recipes for specific day
  const getDayRecipes = (day) => {
    if (!mealPlan[day]) return [];
    
    const dayRecipes = [];
    Object.keys(mealPlan[day]).forEach(mealType => {
      dayRecipes.push(...mealPlan[day][mealType]);
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
