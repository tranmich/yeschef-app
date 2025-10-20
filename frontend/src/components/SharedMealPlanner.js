import React, { useState, useEffect } from 'react';
import './SharedMealPlanner.css';

const SharedMealPlanner = ({ household }) => {
  const [mealPlan, setMealPlan] = useState({});
  const [selectedWeek, setSelectedWeek] = useState(0); // 0 = current week
  const [loading, setLoading] = useState(true);
  const [showAddMealModal, setShowAddMealModal] = useState(false);
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [availableRecipes, setAvailableRecipes] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
  const mealTypes = ['Breakfast', 'Lunch', 'Dinner'];

  useEffect(() => {
    if (household) {
      loadSharedMealPlan();
      loadAvailableRecipes();
    }
  }, [household, selectedWeek]);

  const loadSharedMealPlan = async () => {
    setLoading(true);
    setError('');
    
    try {
      // For now, we'll use localStorage to simulate shared meal plans
      // In a real implementation, this would be an API call
      const planKey = `household_mealplan_${household.id}_week_${selectedWeek}`;
      const savedPlan = localStorage.getItem(planKey);
      
      if (savedPlan) {
        setMealPlan(JSON.parse(savedPlan));
      } else {
        // Initialize empty meal plan
        const emptyPlan = {};
        daysOfWeek.forEach(day => {
          emptyPlan[day] = {};
          mealTypes.forEach(mealType => {
            emptyPlan[day][mealType] = null;
          });
        });
        setMealPlan(emptyPlan);
      }
    } catch (error) {
      setError('Failed to load shared meal plan');
      console.error('Error loading shared meal plan:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadAvailableRecipes = async () => {
    try {
      // For demo purposes, we'll create some sample recipes
      // In a real implementation, this would fetch from the user's recipe collection
      setAvailableRecipes([
        { id: 1, title: 'Spaghetti Carbonara', category: 'Italian', prep_time: '20 min', difficulty: 'Easy' },
        { id: 2, title: 'Chicken Stir Fry', category: 'Asian', prep_time: '25 min', difficulty: 'Medium' },
        { id: 3, title: 'Caesar Salad', category: 'Salads', prep_time: '15 min', difficulty: 'Easy' },
        { id: 4, title: 'Beef Tacos', category: 'Mexican', prep_time: '30 min', difficulty: 'Medium' },
        { id: 5, title: 'Pancakes', category: 'Breakfast', prep_time: '20 min', difficulty: 'Easy' },
        { id: 6, title: 'Grilled Salmon', category: 'Seafood', prep_time: '25 min', difficulty: 'Medium' },
        { id: 7, title: 'Vegetable Curry', category: 'Indian', prep_time: '35 min', difficulty: 'Medium' },
        { id: 8, title: 'Greek Yogurt Bowl', category: 'Breakfast', prep_time: '5 min', difficulty: 'Easy' }
      ]);
    } catch (error) {
      console.error('Error loading recipes:', error);
    }
  };

  const saveMealPlan = (updatedPlan) => {
    try {
      const planKey = `household_mealplan_${household.id}_week_${selectedWeek}`;
      localStorage.setItem(planKey, JSON.stringify(updatedPlan));
      setMealPlan(updatedPlan);
    } catch (error) {
      setError('Failed to save meal plan');
      console.error('Error saving meal plan:', error);
    }
  };

  const handleAddMeal = (day, mealType) => {
    setSelectedSlot({ day, mealType });
    setShowAddMealModal(true);
  };

  const handleAssignRecipe = (recipe) => {
    if (!selectedSlot) return;
    
    const { day, mealType } = selectedSlot;
    const mealEntry = {
      ...recipe,
      assignedBy: 'Current User', // In real implementation, get from auth context
      assignedAt: new Date().toLocaleDateString(),
      notes: ''
    };
    
    const updatedPlan = {
      ...mealPlan,
      [day]: {
        ...mealPlan[day],
        [mealType]: mealEntry
      }
    };
    
    saveMealPlan(updatedPlan);
    setShowAddMealModal(false);
    setSelectedSlot(null);
    setSuccess(`${recipe.title} added to ${day} ${mealType}!`);
    
    // Clear success message after 3 seconds
    setTimeout(() => setSuccess(''), 3000);
  };

  const handleRemoveMeal = (day, mealType) => {
    const updatedPlan = {
      ...mealPlan,
      [day]: {
        ...mealPlan[day],
        [mealType]: null
      }
    };
    
    saveMealPlan(updatedPlan);
    setSuccess('Meal removed from plan');
    setTimeout(() => setSuccess(''), 3000);
  };

  const getWeekDateRange = () => {
    const today = new Date();
    const currentWeekStart = new Date(today);
    currentWeekStart.setDate(today.getDate() - today.getDay() + 1); // Start from Monday
    
    const weekStart = new Date(currentWeekStart);
    weekStart.setDate(currentWeekStart.getDate() + (selectedWeek * 7));
    
    const weekEnd = new Date(weekStart);
    weekEnd.setDate(weekStart.getDate() + 6);
    
    return {
      start: weekStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      end: weekEnd.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    };
  };

  const generateShoppingList = () => {
    // Extract all planned meals and generate a shopping list
    const plannedMeals = [];
    Object.entries(mealPlan).forEach(([day, meals]) => {
      Object.entries(meals).forEach(([mealType, meal]) => {
        if (meal) {
          plannedMeals.push({ ...meal, day, mealType });
        }
      });
    });
    
    if (plannedMeals.length === 0) {
      setError('No meals planned yet. Add some meals to generate a shopping list.');
      setTimeout(() => setError(''), 3000);
      return;
    }
    
    // For demo purposes, we'll show a simple alert
    // In a real implementation, this would integrate with the grocery list
    const mealTitles = plannedMeals.map(meal => meal.title).join(', ');
    setSuccess(`Shopping list generated for: ${mealTitles}`);
    setTimeout(() => setSuccess(''), 5000);
  };

  if (loading) {
    return (
      <div className="shared-meal-loading">
        <div className="loading-spinner"></div>
        <p>Loading shared meal plan...</p>
      </div>
    );
  }

  const weekRange = getWeekDateRange();

  return (
    <div className="shared-meal-planner">
      <div className="meal-planner-header">
        <h3>🍽️ Shared Meal Plan</h3>
        <p className="meal-planner-subtitle">
          Planning meals for <strong>{household.name}</strong>
        </p>
        
        {/* Week Navigation */}
        <div className="week-navigation">
          <button
            className="week-nav-button"
            onClick={() => setSelectedWeek(selectedWeek - 1)}
          >
            ← Previous Week
          </button>
          <span className="week-display">
            Week of {weekRange.start} - {weekRange.end}
            {selectedWeek === 0 && ' (Current Week)'}
          </span>
          <button
            className="week-nav-button"
            onClick={() => setSelectedWeek(selectedWeek + 1)}
          >
            Next Week →
          </button>
        </div>

        {/* Action Buttons */}
        <div className="meal-plan-actions">
          <button
            className="primary-button"
            onClick={generateShoppingList}
          >
            🛒 Generate Shopping List
          </button>
        </div>
      </div>

      {/* Messages */}
      {error && (
        <div className="message error-message">
          ❌ {error}
          <button onClick={() => setError('')} className="close-message">×</button>
        </div>
      )}
      {success && (
        <div className="message success-message">
          ✅ {success}
          <button onClick={() => setSuccess('')} className="close-message">×</button>
        </div>
      )}

      {/* Meal Plan Grid */}
      <div className="meal-plan-grid">
        <div className="meal-grid-header">
          <div className="time-slot-header"></div>
          {mealTypes.map(mealType => (
            <div key={mealType} className="meal-type-header">
              {mealType}
            </div>
          ))}
        </div>

        {daysOfWeek.map(day => (
          <div key={day} className="meal-day-row">
            <div className="day-header">
              <strong>{day}</strong>
            </div>
            {mealTypes.map(mealType => {
              const meal = mealPlan[day]?.[mealType];
              return (
                <div key={`${day}-${mealType}`} className="meal-slot">
                  {meal ? (
                    <div className="planned-meal">
                      <h5 className="meal-title">{meal.title}</h5>
                      <p className="meal-meta">
                        {meal.category} • {meal.prep_time}
                      </p>
                      <p className="meal-assigned">
                        Added by {meal.assignedBy}
                      </p>
                      <button
                        className="remove-meal-button"
                        onClick={() => handleRemoveMeal(day, mealType)}
                        title="Remove meal"
                      >
                        ✕
                      </button>
                    </div>
                  ) : (
                    <button
                      className="add-meal-button"
                      onClick={() => handleAddMeal(day, mealType)}
                    >
                      + Add Meal
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        ))}
      </div>

      <div className="meal-planner-footer">
        <p className="collaboration-note">
          💡 <strong>Family Planning:</strong> All household members can add, remove, and modify meals in this shared plan.
        </p>
      </div>

      {/* Add Meal Modal */}
      {showAddMealModal && selectedSlot && (
        <div className="modal-overlay" onClick={() => setShowAddMealModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>🍽️ Add Meal for {selectedSlot.day} {selectedSlot.mealType}</h3>
              <button
                className="close-button"
                onClick={() => setShowAddMealModal(false)}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <p className="modal-instruction">Choose a recipe from your collection:</p>
              
              <div className="recipe-selection-list">
                {availableRecipes.map(recipe => (
                  <div key={recipe.id} className="recipe-selection-item">
                    <div className="recipe-info">
                      <h5 className="recipe-title">{recipe.title}</h5>
                      <p className="recipe-meta">
                        {recipe.category} • {recipe.prep_time} • {recipe.difficulty}
                      </p>
                    </div>
                    <button
                      className="select-recipe-button"
                      onClick={() => handleAssignRecipe(recipe)}
                    >
                      Add to Plan
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SharedMealPlanner;