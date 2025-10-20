/**
 * 🏠 Household API Utilities
 * API functions for household management and collaboration
 */

import { getApiUrl } from './api';

// Get auth token from localStorage
const getAuthToken = () => {
  return localStorage.getItem('authToken');
};

// Create headers with auth token
const getHeaders = () => {
  const token = getAuthToken();
  return {
    'Content-Type': 'application/json',
    'Authorization': token ? `Bearer ${token}` : ''
  };
};

// ==================== HOUSEHOLD MANAGEMENT ====================

/**
 * Get all households for the current user
 */
export const getHouseholds = async () => {
  try {
    const response = await fetch(`${getApiUrl()}/api/households/list`, {
      method: 'GET',
      headers: getHeaders()
    });
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('❌ Error fetching households:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Create a new household
 * @param {string} name - Household name
 * @param {string} description - Household description (optional)
 */
export const createHousehold = async (name, description = '') => {
  try {
    const response = await fetch(`${getApiUrl()}/api/households/create`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ name, description })
    });
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('❌ Error creating household:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Delete a household (owner only)
 * @param {number} householdId - Household ID
 */
export const deleteHousehold = async (householdId) => {
  try {
    const response = await fetch(`${getApiUrl()}/api/households/${householdId}/delete`, {
      method: 'DELETE',
      headers: getHeaders()
    });
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('❌ Error deleting household:', error);
    return { success: false, error: error.message };
  }
};

// ==================== MEMBER MANAGEMENT ====================

/**
 * Get all members of a household
 * @param {number} householdId - Household ID
 */
export const getHouseholdMembers = async (householdId) => {
  try {
    const response = await fetch(`${getApiUrl()}/api/households/${householdId}/members`, {
      method: 'GET',
      headers: getHeaders()
    });
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('❌ Error fetching household members:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Add a member to household (must be friends)
 * @param {number} householdId - Household ID
 * @param {number} userId - User ID to add
 */
export const addHouseholdMember = async (householdId, userId) => {
  try {
    const response = await fetch(`${getApiUrl()}/api/households/${householdId}/members/add`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ user_id: userId })
    });
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('❌ Error adding household member:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Remove a member from household
 * @param {number} householdId - Household ID
 * @param {number} memberId - Member user ID to remove
 */
export const removeHouseholdMember = async (householdId, memberId) => {
  try {
    const response = await fetch(
      `${getApiUrl()}/api/households/${householdId}/members/${memberId}/remove`,
      {
        method: 'DELETE',
        headers: getHeaders()
      }
    );
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('❌ Error removing household member:', error);
    return { success: false, error: error.message };
  }
};

// ==================== COLLABORATION/SHARING ====================

/**
 * Share a resource (grocery list or meal plan) with a household
 * @param {string} resourceType - 'grocery_list' or 'meal_plan'
 * @param {number} resourceId - Resource ID
 * @param {number} householdId - Household ID
 * @param {string} permissionLevel - 'editor' or 'viewer' (default: 'editor')
 */
export const shareWithHousehold = async (
  resourceType,
  resourceId,
  householdId,
  permissionLevel = 'editor'
) => {
  try {
    const response = await fetch(`${getApiUrl()}/api/collaboration/invite`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        resource_type: resourceType,
        resource_id: resourceId,
        household_id: householdId,
        permission_level: permissionLevel
      })
    });
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('❌ Error sharing with household:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Get all resources shared with the current user
 */
export const getSharedResources = async () => {
  try {
    const response = await fetch(`${getApiUrl()}/api/collaboration/my-shared`, {
      method: 'GET',
      headers: getHeaders()
    });
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('❌ Error fetching shared resources:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Check if current user has access to a resource
 * @param {string} resourceType - 'grocery_list' or 'meal_plan'
 * @param {number} resourceId - Resource ID
 */
export const checkResourceAccess = async (resourceType, resourceId) => {
  try {
    const response = await fetch(
      `${getApiUrl()}/api/collaboration/check-access/${resourceType}/${resourceId}`,
      {
        method: 'GET',
        headers: getHeaders()
      }
    );
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('❌ Error checking resource access:', error);
    return { success: false, error: error.message };
  }
};

export default {
  // Household Management
  getHouseholds,
  createHousehold,
  deleteHousehold,
  
  // Member Management
  getHouseholdMembers,
  addHouseholdMember,
  removeHouseholdMember,
  
  // Collaboration
  shareWithHousehold,
  getSharedResources,
  checkResourceAccess
};
