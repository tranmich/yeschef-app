/**
 * Node Creation Utilities
 * 
 * Factory functions for creating standardized React Flow nodes
 * Extracted from WhiteboardApp.js
 */

/**
 * Create a grocery list node for the canvas
 * @param {Object} data - Grocery list data
 * @param {Array} data.items - Grocery items
 * @param {Array} data.linkedRecipeIds - Source recipe IDs
 * @param {number} data.recipeCount - Number of source recipes
 * @param {Object} handlers - Event handlers
 * @param {Object} position - {x, y} position on canvas
 * @returns {Object} React Flow node object
 */
export function createGroceryListNode(data, handlers, position = { x: 800, y: 100 }) {
  return {
    id: `grocery-list-${Date.now()}`,
    type: 'groceryListNode',
    position,
    draggable: true,
    width: 350,
    height: 500,
    data: {
      name: `Shopping List (${data.recipeCount} recipes)`,
      items: data.items,
      linkedRecipeIds: data.linkedRecipeIds,
      dbId: null, // Will be set after saving
      backgroundColor: '#D1FAE5',
      commentCount: 0,
      hasNewComments: false,
      ...handlers
    },
    style: {
      width: 350,
      height: 500
    }
  };
}

/**
 * Create a note node for the canvas
 * @param {Object} position - {x, y} position on canvas
 * @param {Object} data - Note data
 * @returns {Object} React Flow node object
 */
export function createNoteNode(position, data = {}) {
  return {
    id: `note-${Date.now()}`,
    type: 'note',
    position,
    draggable: true,
    data: {
      content: data.content || '',
      backgroundColor: data.backgroundColor || '#FFF9C4',
      fontSize: data.fontSize || '14px',
      ...data
    },
    style: {
      width: 300,
      height: 250
    }
  };
}

/**
 * Create a meal plan container node
 * @param {Object} mealPlan - Meal plan data
 * @param {Object} position - {x, y} position on canvas
 * @param {Object} handlers - Event handlers
 * @returns {Object} React Flow node object
 */
export function createMealPlanNode(mealPlan, position, handlers = {}) {
  return {
    id: `meal-plan-${Date.now()}`,
    type: 'mealPlanContainer',
    position,
    draggable: true,
    data: {
      mealPlanDbId: mealPlan.id,
      name: mealPlan.name || 'Untitled Plan',
      backgroundColor: mealPlan.backgroundColor || '#E3F2FD',
      ...handlers
    },
    style: {
      width: 600,
      height: 800
    }
  };
}

/**
 * Create an activity feed node
 * @param {number} householdId - Household ID
 * @param {Object} position - {x, y} position on canvas
 * @returns {Object} React Flow node object
 */
export function createActivityFeedNode(householdId, position = { x: 1400, y: 150 }) {
  return {
    id: `activity-feed-${Date.now()}`,
    type: 'activityFeed',
    position,
    draggable: true,
    data: {
      householdId,
      backgroundColor: '#FFF3E0',
      commentCount: 0,
      hasNewComments: false
    },
    style: {
      width: 400,
      height: 600
    }
  };
}
