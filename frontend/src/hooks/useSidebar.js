import { useState } from 'react';

/**
 * Custom hook for managing sidebar state and visibility
 */
export const useSidebar = () => {
  // Sidebar visibility states
  const [isPantryVisible, setIsPantryVisible] = useState(false);
  const [isMealPlannerVisible, setIsMealPlannerVisible] = useState(false);
  
  // Expand states for full-width mode
  const [isPantryExpanded, setIsPantryExpanded] = useState(false);
  const [isMealPlannerExpanded, setIsMealPlannerExpanded] = useState(false);

  // Toggle functions
  const togglePantry = () => {
    setIsPantryVisible(prev => {
      const newState = !prev;
      // Close meal planner when opening pantry
      if (newState) {
        setIsMealPlannerVisible(false);
        setIsMealPlannerExpanded(false);
      }
      // Reset expanded state when closing
      if (!newState) {
        setIsPantryExpanded(false);
      }
      console.log('🥘 Pantry visibility:', newState);
      return newState;
    });
  };

  const toggleMealPlanner = () => {
    setIsMealPlannerVisible(prev => {
      const newState = !prev;
      // Close pantry when opening meal planner
      if (newState) {
        setIsPantryVisible(false);
        setIsPantryExpanded(false);
      }
      // Reset expanded state when closing
      if (!newState) {
        setIsMealPlannerExpanded(false);
      }
      console.log('📅 Meal Planner visibility:', newState);
      return newState;
    });
  };

  // Expand/collapse functions
  const togglePantryExpand = () => {
    setIsPantryExpanded(prev => !prev);
  };

  const toggleMealPlannerExpand = () => {
    setIsMealPlannerExpanded(prev => !prev);
  };

  // Close all sidebars
  const closeAllSidebars = () => {
    setIsPantryVisible(false);
    setIsMealPlannerVisible(false);
    setIsPantryExpanded(false);
    setIsMealPlannerExpanded(false);
    console.log('🔒 All sidebars closed');
  };

  // Close specific sidebar
  const closePantry = () => {
    setIsPantryVisible(false);
    setIsPantryExpanded(false);
    console.log('🔒 Pantry closed');
  };

  const closeMealPlanner = () => {
    setIsMealPlannerVisible(false);
    setIsMealPlannerExpanded(false);
    console.log('🔒 Meal Planner closed');
  };

  // Check if any sidebar is open
  const isAnySidebarOpen = () => {
    return isPantryVisible || isMealPlannerVisible;
  };

  // Check if specific sidebar is open
  const getSidebarState = () => ({
    isPantryVisible,
    isMealPlannerVisible,
    isAnySidebarOpen: isAnySidebarOpen()
  });

  // Get active sidebar name
  const getActiveSidebar = () => {
    if (isPantryVisible) return 'pantry';
    if (isMealPlannerVisible) return 'mealPlanner';
    return null;
  };

  // Set specific sidebar state
  const setPantryVisible = (visible) => {
    setIsPantryVisible(visible);
    if (visible) {
      setIsMealPlannerVisible(false);
    }
    console.log('🥘 Pantry set to:', visible);
  };

  const setMealPlannerVisible = (visible) => {
    setIsMealPlannerVisible(visible);
    if (visible) {
      setIsPantryVisible(false);
    }
    console.log('📅 Meal Planner set to:', visible);
  };

  return {
    // State
    isPantryVisible,
    isMealPlannerVisible,
    isPantryExpanded,
    isMealPlannerExpanded,
    
    // Toggle functions
    togglePantry,
    toggleMealPlanner,
    togglePantryExpand,
    toggleMealPlannerExpand,
    
    // Close functions
    closeAllSidebars,
    closePantry,
    closeMealPlanner,
    
    // Set functions
    setPantryVisible,
    setMealPlannerVisible,
    
    // Utilities
    isAnySidebarOpen,
    getSidebarState,
    getActiveSidebar
  };
};
