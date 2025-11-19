/**
 * Whiteboard API Service
 * ======================
 * Client-side API wrapper for whiteboard endpoints
 * 
 * Matches V2 API structure from backend
 * Uses existing apiCall utility for consistency
 * 
 * Phase 1 - Week 3: Frontend Integration
 * Author: GitHub Copilot
 * Date: November 3, 2025
 */

import { apiCall } from '../utils/api';

/**
 * Whiteboard API
 * All endpoints use V2 format: {success, data, error, message}
 */
export const whiteboardAPI = {
  // =====================================================
  // WHITEBOARD CRUD
  // =====================================================

  /**
   * Get all whiteboards for household
   * @param {number} householdId - Household ID
   * @returns {Promise} Array of whiteboards
   */
  async getHouseholdWhiteboards(householdId) {
    return apiCall(`/api/v2/whiteboard/h/${householdId}`, {
      method: 'GET'
    });
  },

  /**
   * Create new whiteboard
   * @param {Object} data - {household_id, name, description, template_type}
   * @returns {Promise} Created whiteboard
   */
  async createWhiteboard(data) {
    return apiCall('/api/v2/whiteboard', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  /**
   * Get whiteboard with all objects
   * @param {number} whiteboardId - Whiteboard ID
   * @returns {Promise} Whiteboard with objects array
   */
  async getWhiteboard(whiteboardId) {
    return apiCall(`/api/v2/whiteboard/${whiteboardId}`, {
      method: 'GET'
    });
  },

  /**
   * Update whiteboard metadata
   * @param {number} whiteboardId - Whiteboard ID
   * @param {Object} data - {name?, description?, canvas_settings?}
   * @returns {Promise} Updated whiteboard
   */
  async updateWhiteboard(whiteboardId, data) {
    return apiCall(`/api/v2/whiteboard/${whiteboardId}`, {
      method: 'PATCH',
      body: JSON.stringify(data)
    });
  },

  /**
   * Soft delete whiteboard (move to trash)
   * @param {number} whiteboardId - Whiteboard ID
   * @returns {Promise} Success confirmation
   */
  async deleteWhiteboard(whiteboardId) {
    return apiCall(`/api/v2/whiteboard/${whiteboardId}`, {
      method: 'DELETE'
    });
  },

  /**
   * Restore whiteboard from trash
   * @param {number} whiteboardId - Whiteboard ID
   * @returns {Promise} Restored whiteboard
   */
  async restoreWhiteboard(whiteboardId) {
    return apiCall(`/api/v2/whiteboard/${whiteboardId}/restore`, {
      method: 'POST'
    });
  },

  // =====================================================
  // OBJECT MANAGEMENT
  // =====================================================

  /**
   * Create object on whiteboard
   * @param {number} whiteboardId - Whiteboard ID
   * @param {Object} data - {type, position, recipe_id?, grocery_list_id?, meal_plan_id?, content?, tags?}
   * @returns {Promise} Created object
   */
  async createObject(whiteboardId, data) {
    return apiCall(`/api/v2/whiteboard/${whiteboardId}/o`, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  /**
   * Update object (position, style, tags, content)
   * @param {number} whiteboardId - Whiteboard ID
   * @param {number} objectId - Object ID
   * @param {Object} data - {position?, style?, tags?, content?}
   * @returns {Promise} Updated object
   */
  async updateObject(whiteboardId, objectId, data) {
    return apiCall(`/api/v2/whiteboard/${whiteboardId}/o/${objectId}`, {
      method: 'PATCH',
      body: JSON.stringify(data)
    });
  },

  /**
   * Delete object from whiteboard
   * @param {number} whiteboardId - Whiteboard ID
   * @param {number} objectId - Object ID
   * @returns {Promise} Success confirmation
   */
  async deleteObject(whiteboardId, objectId) {
    return apiCall(`/api/v2/whiteboard/${whiteboardId}/o/${objectId}`, {
      method: 'DELETE'
    });
  },

  /**
   * Bulk update object positions (after drag)
   * @param {number} whiteboardId - Whiteboard ID
   * @param {Array} objects - [{recipe_id, position}, ...]
   * @returns {Promise} Success confirmation
   */
  async bulkUpdateObjects(whiteboardId, objects) {
    return apiCall(`/api/v2/whiteboard/${whiteboardId}/o/bulk`, {
      method: 'PATCH',
      body: JSON.stringify({ objects })
    });
  },

  /**
   * Create recipe card from existing recipe
   * @param {number} whiteboardId - Whiteboard ID
   * @param {number} recipeId - Recipe ID
   * @param {Array} position - [x, y, width, height, z-index]
   * @returns {Promise} Created recipe card object
   */
  async createRecipeCard(whiteboardId, recipeId, position) {
    return apiCall(`/api/v2/whiteboard/${whiteboardId}/o/from-r/${recipeId}`, {
      method: 'POST',
      body: JSON.stringify({ position })
    });
  },

  /**
   * Link object to entity (recipe/grocery/meal plan)
   * @param {number} whiteboardId - Whiteboard ID
   * @param {number} objectId - Object ID
   * @param {string} entityType - 'recipe', 'grocery_list', 'meal_plan'
   * @param {number} entityId - Entity ID
   * @returns {Promise} Updated object
   */
  async linkObjectToEntity(whiteboardId, objectId, entityType, entityId) {
    return apiCall(`/api/v2/whiteboard/${whiteboardId}/o/${objectId}/link`, {
      method: 'POST',
      body: JSON.stringify({ entity_type: entityType, entity_id: entityId })
    });
  },

  /**
   * Sync object from linked entity (refresh data)
   * @param {number} whiteboardId - Whiteboard ID
   * @param {number} objectId - Object ID
   * @returns {Promise} Updated object with fresh data
   */
  async syncObjectFromSource(whiteboardId, objectId) {
    return apiCall(`/api/v2/whiteboard/${whiteboardId}/o/${objectId}/sync`, {
      method: 'POST'
    });
  },

  // =====================================================
  // COMMENTS (Phase 4 - Stubs for now)
  // =====================================================

  /**
   * Get comments for object
   * @param {number} objectId - Object ID
   * @returns {Promise} Comments array
   */
  async getComments(objectId) {
    return apiCall(`/api/v2/whiteboard/o/${objectId}/cm`, {
      method: 'GET'
    });
  },

  /**
   * Add comment to object
   * @param {number} objectId - Object ID
   * @param {Object} data - {text, parent_comment_id?, mentioned_users?}
   * @returns {Promise} Created comment
   */
  async addComment(objectId, data) {
    return apiCall(`/api/v2/whiteboard/o/${objectId}/cm`, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  /**
   * Update comment
   * @param {number} commentId - Comment ID
   * @param {Object} data - {text}
   * @returns {Promise} Updated comment
   */
  async updateComment(commentId, data) {
    return apiCall(`/api/v2/whiteboard/cm/${commentId}`, {
      method: 'PATCH',
      body: JSON.stringify(data)
    });
  },

  /**
   * Delete comment
   * @param {number} commentId - Comment ID
   * @returns {Promise} Success confirmation
   */
  async deleteComment(commentId) {
    return apiCall(`/api/v2/whiteboard/cm/${commentId}`, {
      method: 'DELETE'
    });
  },

  /**
   * Add reaction to comment
   * @param {number} commentId - Comment ID
   * @param {string} emoji - Emoji reaction
   * @returns {Promise} Updated reactions
   */
  async addReaction(commentId, emoji) {
    return apiCall(`/api/v2/whiteboard/cm/${commentId}/rx`, {
      method: 'POST',
      body: JSON.stringify({ emoji })
    });
  },

  // =====================================================
  // COLLABORATION (Phase 3 - Stubs for now)
  // =====================================================

  /**
   * Get active collaborators on whiteboard
   * @param {number} whiteboardId - Whiteboard ID
   * @returns {Promise} Collaborators array
   */
  async getCollaborators(whiteboardId) {
    return apiCall(`/api/v2/whiteboard/${whiteboardId}/co`, {
      method: 'GET'
    });
  },

  /**
   * Update user presence on whiteboard
   * @param {number} whiteboardId - Whiteboard ID
   * @param {Object} data - {is_active, current_object_id?, activity_status?}
   * @returns {Promise} Updated presence
   */
  async updatePresence(whiteboardId, data) {
    return apiCall(`/api/v2/whiteboard/${whiteboardId}/pr`, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  /**
   * Get activity history for whiteboard
   * @param {number} whiteboardId - Whiteboard ID
   * @param {number} limit - Number of events to fetch
   * @returns {Promise} Events array
   */
  async getHistory(whiteboardId, limit = 20) {
    return apiCall(`/api/v2/whiteboard/${whiteboardId}/h?limit=${limit}`, {
      method: 'GET'
    });
  },

  // =====================================================
  // UTILITIES
  // =====================================================

  /**
   * Get available templates
   * @returns {Promise} Templates array
   */
  async getTemplates() {
    return apiCall('/api/v2/whiteboard/tpl', {
      method: 'GET'
    });
  },

  // =====================================================
  // GROCERY LISTS (Whiteboard Integration)
  // =====================================================

  /**
   * Get all grocery lists for whiteboard
   * @param {number} whiteboardId - Whiteboard ID
   * @returns {Promise} Array of grocery lists
   */
  async getWhiteboardGroceryLists(whiteboardId) {
    return apiCall(`/api/v2/whiteboard/${whiteboardId}/grocery-lists`, {
      method: 'GET'
    });
  },

  /**
   * Create grocery list on whiteboard
   * @param {number} whiteboardId - Whiteboard ID
   * @param {Object} data - {name, items, household_id, widget_position, linked_recipe_ids}
   * @returns {Promise} Created grocery list
   */
  async createWhiteboardGroceryList(whiteboardId, data) {
    return apiCall(`/api/v2/whiteboard/${whiteboardId}/grocery-lists`, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  /**
   * Update grocery list on whiteboard
   * @param {number} whiteboardId - Whiteboard ID
   * @param {number} listId - Grocery list ID
   * @param {Object} data - {name?, items?, widget_position?, linked_recipe_ids?}
   * @returns {Promise} Updated grocery list
   */
  async updateWhiteboardGroceryList(whiteboardId, listId, data) {
    return apiCall(`/api/v2/whiteboard/${whiteboardId}/grocery-lists/${listId}`, {
      method: 'PATCH',
      body: JSON.stringify(data)
    });
  },

  /**
   * Delete grocery list from whiteboard
   * @param {number} whiteboardId - Whiteboard ID
   * @param {number} listId - Grocery list ID
   * @returns {Promise} Success confirmation
   */
  async deleteWhiteboardGroceryList(whiteboardId, listId) {
    return apiCall(`/api/v2/whiteboard/${whiteboardId}/grocery-lists/${listId}`, {
      method: 'DELETE'
    });
  },

  // =====================================================
  // HOUSEHOLD DATA SHARING (Whiteboard Context)
  // =====================================================

  /**
   * Get recipe in whiteboard context (household-aware)
   * Allows viewing recipes created by other household members
   * @param {number} whiteboardId - Whiteboard ID
   * @param {number} recipeId - Recipe ID
   * @returns {Promise} Recipe data
   */
  async getWhiteboardRecipe(whiteboardId, recipeId) {
    return apiCall(`/api/v2/whiteboard/${whiteboardId}/recipes/${recipeId}`, {
      method: 'GET'
    });
  },

  /**
   * Get meal plan in whiteboard context (household-aware)
   * Allows viewing meal plans created by other household members
   * @param {number} whiteboardId - Whiteboard ID
   * @param {number} mealPlanId - Meal plan ID
   * @returns {Promise} Meal plan data
   */
  async getWhiteboardMealPlan(whiteboardId, mealPlanId) {
    return apiCall(`/api/v2/whiteboard/${whiteboardId}/meal-plans/${mealPlanId}`, {
      method: 'GET'
    });
  },

  // =====================================================
  // MEAL PLANS (Legacy)
  // =====================================================

  /**
   * Get meal plan by ID
   * @param {number} mealPlanId - Meal plan ID
   * @returns {Promise} Meal plan data
   */
  async getMealPlan(mealPlanId) {
    return apiCall(`/api/meal-plans/${mealPlanId}`, {
      method: 'GET'
    });
  },

  /**
   * Update meal plan
   * @param {number} mealPlanId - Meal plan ID
   * @param {Object} data - {plan_name?, meal_data?}
   * @returns {Promise} Updated meal plan
   */
  async updateMealPlan(mealPlanId, data) {
    return apiCall(`/api/meal-plans/${mealPlanId}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  },

  /**
   * Delete meal plan
   * @param {number} mealPlanId - Meal plan ID
   * @returns {Promise} Success confirmation
   */
  async deleteMealPlan(mealPlanId) {
    return apiCall(`/api/meal-plans/${mealPlanId}`, {
      method: 'DELETE'
    });
  },

  // =====================================================
  // UTILITIES
  // =====================================================

  /**
   * Duplicate whiteboard
   * @param {number} whiteboardId - Whiteboard ID
   * @param {Object} data - {name?, household_id?}
   * @returns {Promise} Duplicated whiteboard
   */
  async duplicateWhiteboard(whiteboardId, data = {}) {
    return apiCall(`/api/v2/whiteboard/${whiteboardId}/dup`, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  /**
   * Export whiteboard as JSON
   * @param {number} whiteboardId - Whiteboard ID
   * @returns {Promise} Export data
   */
  async exportWhiteboard(whiteboardId) {
    return apiCall(`/api/v2/whiteboard/${whiteboardId}/exp`, {
      method: 'GET'
    });
  },

  /**
   * Health check for whiteboard service
   * @returns {Promise} Service status
   */
  async healthCheck() {
    return apiCall('/api/v2/whiteboard/health', {
      method: 'GET'
    });
  }
};

/**
 * Helper functions for common patterns
 */
export const whiteboardHelpers = {
  /**
   * Check if whiteboard is in trash
   * @param {Object} whiteboard - Whiteboard object
   * @returns {boolean}
   */
  isDeleted(whiteboard) {
    return whiteboard.deleted_at !== null;
  },

  /**
   * Calculate days until permanent deletion
   * @param {Object} whiteboard - Whiteboard object
   * @returns {number} Days remaining
   */
  daysUntilPermanentDelete(whiteboard) {
    if (!whiteboard.deleted_at) return null;
    
    const deletedDate = new Date(whiteboard.deleted_at);
    const expiryDate = new Date(deletedDate.getTime() + (14 * 24 * 60 * 60 * 1000));
    const today = new Date();
    const daysLeft = Math.ceil((expiryDate - today) / (24 * 60 * 60 * 1000));
    
    return Math.max(0, daysLeft);
  },

  /**
   * Format position array for API
   * @param {number} x - X coordinate
   * @param {number} y - Y coordinate
   * @param {number} width - Width
   * @param {number} height - Height
   * @param {number} zIndex - Z-index
   * @returns {Array} Position array [x, y, w, h, z]
   */
  formatPosition(x, y, width = 300, height = 400, zIndex = 0) {
    return [x, y, width, height, zIndex];
  },

  /**
   * Parse position array from API
   * @param {Array} position - [x, y, w, h, z]
   * @returns {Object} {x, y, width, height, zIndex}
   */
  parsePosition(position) {
    const [x = 0, y = 0, width = 300, height = 400, zIndex = 0] = position || [];
    return { x, y, width, height, zIndex };
  },

  /**
   * Get object type display name
   * @param {string} type - Object type code
   * @returns {string} Display name
   */
  getObjectTypeName(type) {
    const types = {
      'rc': 'Recipe Card',
      'gl': 'Grocery List',
      'mp': 'Meal Plan',
      'nt': 'Note',
      'im': 'Image',
      'cn': 'Container',
      'sc': 'Section'
    };
    return types[type] || 'Unknown';
  }
};

export default whiteboardAPI;
