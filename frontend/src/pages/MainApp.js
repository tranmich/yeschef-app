import React, { useState } from 'react';
import { DndContext, closestCenter } from '@dnd-kit/core';
import SidebarContainer from '../components/SidebarContainer';
import ChatInterface from '../components/ChatInterface';
import './MainApp.css';
import SessionMemoryManager from '../utils/SessionMemoryManager';
import { usePantry } from '../hooks/usePantry';
import { useMealPlanner, useDragAndDrop, useSidebar } from '../hooks';

const MainApp = () => {
  console.log('🚀 MainApp component loaded - ENHANCED SESSION VERSION 2025-08-16');

  // --- Enhanced Session Memory with Backend Coordination ---
  const [sessionMemory] = useState(() => new SessionMemoryManager());

  // --- Pantry Integration ---
  const { pantryItems, getPantryForAPI, hasItems: hasPantryItems } = usePantry();

  // --- Custom Hooks ---
  const mealPlannerHook = useMealPlanner();
  const sidebarHook = useSidebar();
  
  // Recipe container state
  const [containerRecipes, setContainerRecipes] = useState([]);
  
  // Grocery list navigation state
  const [showGroceryListFromNav, setShowGroceryListFromNav] = useState(false);
  
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
      <div className="app-container">
        {/* Main Content Area */}
        <div className="main-content">
          {/* Sidebar Container - Manages all sidebars */}
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
            onFeatureSelect={(feature) => {
              // Handle feature navigation
              console.log('Feature selected:', feature);
              if (feature === 'chat') {
                sidebarHook.closeAllSidebars();
              }
            }}
          />

          {/* Chat Area */}
          <div className={`chat-area ${sidebarHook.isMealPlannerVisible ? 'with-meal-planner' : ''} ${sidebarHook.isPantryVisible ? 'with-pantry' : ''} ${(sidebarHook.isPantryExpanded || sidebarHook.isMealPlannerExpanded) ? 'sidebar-expanded' : ''}`}>
            <ChatInterface
              sessionMemory={sessionMemory}
              getPantryForAPI={getPantryForAPI}
              hasPantryItems={hasPantryItems}
              pantryItems={pantryItems}
              setShowPantry={sidebarHook.setPantryVisible}
              isCompact={sidebarHook.isMealPlannerVisible || sidebarHook.isPantryVisible}
              isExtraCompact={sidebarHook.isMealPlannerVisible && sidebarHook.isPantryVisible}
            />
          </div>
        </div>
      </div>
    </DndContext>
  );
};

export default MainApp;
