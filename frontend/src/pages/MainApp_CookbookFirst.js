import React, { useState, useEffect } from 'react';
import { DndContext, closestCenter } from '@dnd-kit/core';
import SidebarContainer from '../components/SidebarContainer';
import ChatInterface from '../components/ChatInterface';
import CookbookSidebar from '../components/CookbookSidebar';
import RecipeListView from '../components/RecipeListView';
import RecipeEditModal from '../components/RecipeEditModal';
import './MainApp.css';
import SessionMemoryManager from '../utils/SessionMemoryManager';
import { usePantry } from '../hooks/usePantry';
import { useMealPlanner, useDragAndDrop, useSidebar } from '../hooks';
import * as api from '../utils/api';

const MainApp = () => {
  console.log('🚀 MainApp component loaded - COOKBOOK-FIRST VERSION 2025-08-22');

  // --- Enhanced Session Memory with Backend Coordination ---
  const [sessionMemory] = useState(() => new SessionMemoryManager());

  // --- Pantry Integration ---
  const { pantryItems, getPantryForAPI, hasItems: hasPantryItems } = usePantry();

  // --- Custom Hooks ---
  const mealPlannerHook = useMealPlanner();
  const sidebarHook = useSidebar();

  // --- Cookbook State ---
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [customCategories, setCustomCategories] = useState([]);
  const [recipeCounts, setRecipeCounts] = useState({});
  const [showChat, setShowChat] = useState(false);
  const [editingRecipe, setEditingRecipe] = useState(null);

  // Recipe container state
  const [containerRecipes, setContainerRecipes] = useState([]);

  // Grocery list navigation state
  const [showGroceryListFromNav, setShowGroceryListFromNav] = useState(false);

  // Load recipes on component mount
  useEffect(() => {
    loadRecipes();
  }, []);

  // Calculate recipe counts when recipes change
  useEffect(() => {
    calculateRecipeCounts();
  }, [recipes]);

  const loadRecipes = async () => {
    setLoading(true);
    try {
      // Use existing search endpoint to get all recipes
      const response = await api.searchRecipes('', { limit: 1000 });
      setRecipes(response.recipes || []);
    } catch (error) {
      console.error('Error loading recipes:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateRecipeCounts = () => {
    const counts = {
      all: recipes.length,
      breakfast: 0,
      lunch: 0,
      dinner: 0,
      desserts: 0,
      'one-pot': 0,
      quick: 0,
      favorites: 0
    };

    recipes.forEach(recipe => {
      // Count by meal role
      if (recipe.meal_role === 'breakfast') counts.breakfast++;
      else if (recipe.meal_role === 'lunch') counts.lunch++;
      else if (recipe.meal_role === 'dinner') counts.dinner++;
      else if (recipe.meal_role === 'dessert') counts.desserts++;

      // Count by characteristics
      if (recipe.is_one_pot) counts['one-pot']++;
      if (recipe.time_min && recipe.time_min <= 30) counts.quick++;
      if (recipe.is_favorite) counts.favorites++;
    });

    setRecipeCounts(counts);
  };

  const getFilteredRecipes = () => {
    if (selectedCategory === 'all') return recipes;
    
    return recipes.filter(recipe => {
      switch (selectedCategory) {
        case 'breakfast':
        case 'lunch':
        case 'dinner':
          return recipe.meal_role === selectedCategory;
        case 'desserts':
          return recipe.meal_role === 'dessert';
        case 'one-pot':
          return recipe.is_one_pot === true;
        case 'quick':
          return recipe.time_min && recipe.time_min <= 30;
        case 'favorites':
          return recipe.is_favorite === true;
        default:
          return true;
      }
    });
  };

  const handleCategorySelect = (categoryId) => {
    setSelectedCategory(categoryId);
  };

  const handleAddCategory = (newCategory) => {
    setCustomCategories(prev => [...prev, newCategory]);
  };

  const handleToggleChat = () => {
    setShowChat(!showChat);
  };

  const handleRecipeClick = (recipe) => {
    // For now, just log - could open a detail view
    console.log('Recipe clicked:', recipe.title);
  };

  const handleRecipeEdit = (recipe) => {
    setEditingRecipe(recipe);
  };

  const handleSaveRecipe = async (updatedRecipe) => {
    try {
      // Call API to update recipe (we'll need to add this endpoint)
      console.log('Saving recipe:', updatedRecipe);
      
      // For now, just update local state
      setRecipes(prev => prev.map(r => 
        r.id === updatedRecipe.id ? updatedRecipe : r
      ));
      
      setEditingRecipe(null);
    } catch (error) {
      console.error('Error saving recipe:', error);
      throw error;
    }
  };

  // Handle adding recipe to container
  const handleRecipeAddedToContainer = (recipe) => {
    setContainerRecipes(prev => {
      const exists = prev.find(r => r.id === recipe.id);
      if (!exists) {
        return [...prev, recipe];
      }
      return prev;
    });
  };

  // Handle grocery list activation from navigation
  const handleShowGroceryList = () => {
    // First ensure meal planner is visible
    if (!sidebarHook.isMealPlannerVisible) {
      sidebarHook.toggleMealPlanner();
    }
    // Signal to show grocery list
    setShowGroceryListFromNav(true);
  };

  // Drag and drop with meal planner and container integration
  const dragAndDropHook = useDragAndDrop(
    (day, mealType, recipe) => {
      return mealPlannerHook.addRecipeToMeal(day, mealType, recipe);
    },
    handleRecipeAddedToContainer,
    (sourceDay, sourceMealType, sourceIndex, targetDay, targetMealType, recipe) => {
      return mealPlannerHook.moveRecipe(sourceDay, sourceMealType, sourceIndex, targetDay, targetMealType, recipe);
    }
  );

  return (
    <DndContext
      sensors={dragAndDropHook.sensors}
      collisionDetection={closestCenter}
      onDragStart={dragAndDropHook.handleDragStart}
      onDragEnd={dragAndDropHook.handleDragEnd}
      onDragCancel={dragAndDropHook.handleDragCancel}
    >
      <div className="app-container cookbook-first">
        {/* Cookbook Sidebar */}
        <CookbookSidebar
          categories={customCategories}
          selectedCategory={selectedCategory}
          onCategorySelect={handleCategorySelect}
          recipeCounts={recipeCounts}
          onAddCategory={handleAddCategory}
        />

        {/* Main Content Area */}
        <div className="main-content">
          {/* Recipe List View */}
          <RecipeListView
            recipes={getFilteredRecipes()}
            selectedCategory={selectedCategory}
            onRecipeClick={handleRecipeClick}
            onRecipeEdit={handleRecipeEdit}
            loading={loading}
          />

          {/* Sidebar Container - Meal Planner, Pantry, etc. */}
          <SidebarContainer
            showMealPlanner={sidebarHook.isMealPlannerVisible}
            onToggleMealPlanner={sidebarHook.toggleMealPlanner}
            showPantry={sidebarHook.isPantryVisible}
            onTogglePantry={sidebarHook.togglePantry}
            isPantryExpanded={sidebarHook.isPantryExpanded}
            isMealPlannerExpanded={sidebarHook.isMealPlannerExpanded}
            onTogglePantryExpand={sidebarHook.togglePantryExpand}
            onToggleMealPlannerExpand={sidebarHook.toggleMealPlannerExpand}
            mealPlan={mealPlannerHook.mealPlan}
            setMealPlan={mealPlannerHook.setMealPlan}
            containerRecipes={containerRecipes}
            setContainerRecipes={setContainerRecipes}
            showGroceryListFromNav={showGroceryListFromNav}
            setShowGroceryListFromNav={setShowGroceryListFromNav}
            onShowGroceryList={handleShowGroceryList}
            showChat={showChat}
            onToggleChat={handleToggleChat}
            onFeatureSelect={(feature) => {
              console.log('Feature selected:', feature);
              if (feature === 'cookbook') {
                setShowChat(false);
                sidebarHook.closeAllSidebars();
              }
            }}
          />

          {/* Chat Panel - Toggle Overlay */}
          {showChat && (
            <div className="chat-overlay">
              <div className="chat-panel">
                <div className="chat-header">
                  <h3>🤖 AI Cooking Assistant</h3>
                  <button 
                    className="close-chat-btn"
                    onClick={() => setShowChat(false)}
                  >
                    ×
                  </button>
                </div>
                <ChatInterface
                  sessionMemory={sessionMemory}
                  getPantryForAPI={getPantryForAPI}
                  hasPantryItems={hasPantryItems}
                  pantryItems={pantryItems}
                  setShowPantry={sidebarHook.setPantryVisible}
                  isCompact={true}
                  isExtraCompact={false}
                  onAddToMealPlan={(day, mealType, recipe) => {
                    // Show meal planner if not visible
                    if (!sidebarHook.isMealPlannerVisible) {
                      sidebarHook.toggleMealPlanner();
                    }
                    // Add recipe to meal plan
                    return mealPlannerHook.addRecipeToMeal(day, mealType, recipe);
                  }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Recipe Edit Modal */}
        <RecipeEditModal
          recipe={editingRecipe}
          isOpen={!!editingRecipe}
          onClose={() => setEditingRecipe(null)}
          onSave={handleSaveRecipe}
        />
      </div>
    </DndContext>
  );
};

export default MainApp;
