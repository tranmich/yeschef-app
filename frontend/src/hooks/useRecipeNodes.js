import { useCallback, useState } from 'react';
import { useWhiteboard } from '../contexts/WhiteboardContext';
import { useRecipeCache } from '../contexts/RecipeCacheContext';
import { createRecipeNode, normalizeRecipe } from '../utils/recipeNodeFactory';
import whiteboardAPI from '../services/whiteboardAPI';
import { apiCall } from '../utils/api';

/**
 * useRecipeNodes Hook
 * 
 * Handles all recipe-related operations on whiteboard:
 * - Add recipe to canvas
 * - Delete recipe from canvas
 * - Update recipe tags
 * - Update recipe colors
 * - Open recipe detail modal
 * - Handle recipe clicks
 * 
 * Extracted from WhiteboardApp.js (Week 1, Day 4)
 */
export function useRecipeNodes() {
  const {
    whiteboardId,
    nodes,
    addNode,
    updateNode,
    deleteNode,
    openRecipeDetail,
  } = useWhiteboard();
  
  const { addRecipes: addRecipesToCache, getRecipe } = useRecipeCache();
  
  // Local state for recipe detail modal
  const [selectedRecipe, setSelectedRecipe] = useState(null);
  const [isDetailOpen, setIsDetailOpen] = useState(false);
  
  // ==========================================
  // ADD RECIPE TO CANVAS
  // ==========================================
  
  /**
   * Add a recipe to the whiteboard canvas
   * @param {Object} recipe - Recipe object from picker
   * @param {Object} position - {x, y} position on canvas
   * @returns {Promise<Object>} Created node
   */
  const addRecipe = useCallback(async (recipe, position = { x: 200, y: 150 }) => {
    try {
      console.log('🍕 Adding recipe to canvas:', recipe.id);
      
      // 1. Fetch full recipe data if needed
      let fullRecipe = recipe;
      if (!recipe.ingredients || !recipe.instructions) {
        const response = await apiCall(`/api/v2/recipes/${recipe.id}`);
        fullRecipe = response.data || response.recipe;
      }
      
      // 2. Normalize and add to cache
      const normalized = normalizeRecipe(fullRecipe);
      addRecipesToCache([normalized]);
      
      // 3. Save to whiteboard database
      const savedObject = await whiteboardAPI.createObject(whiteboardId, {
        type: 'rc',  // Database constraint requires 'rc' for recipe cards
        entity_type: 'recipe',
        entity_id: recipe.id,
        position: [position.x, position.y, 300, 400, 0],  // [x, y, width, height, z_index]
        tags: [],
        background_color: '#FFFFFF'
      });
      
      // 4. Create node using factory
      const node = createRecipeNode({
        recipeId: recipe.id,
        objectId: savedObject.id,
        position,
        tags: [],
        backgroundColor: '#FFFFFF',
        commentCount: 0,
        hasNewComments: false,
        onClick: handleRecipeClick,
        onDelete: handleDeleteRecipe,
        onTagsChange: handleTagsChange,
        onColorChange: handleRecipeColorChange,
        onTagFilterClick: handleTagFilterClick,
      });
      
      // 5. Add to canvas (validates & normalizes)
      addNode(node);
      
      console.log('✅ Recipe added to canvas:', recipe.id);
      return node;
      
    } catch (error) {
      console.error('❌ Failed to add recipe:', error);
      throw error;
    }
  }, [whiteboardId, addRecipesToCache, addNode]);
  
  // ==========================================
  // DELETE RECIPE FROM CANVAS
  // ==========================================
  
  /**
   * Delete a recipe from the whiteboard
   * @param {string} nodeId - React Flow node ID
   * @param {number} recipeId - Recipe ID
   * @param {number} objectId - Whiteboard object ID
   */
  const handleDeleteRecipe = useCallback(async (nodeId, recipeId, objectId) => {
    try {
      // Confirm deletion
      if (!window.confirm('Remove this recipe from the whiteboard?')) {
        return;
      }
      
      console.log('🗑️ Deleting recipe:', nodeId, recipeId, objectId);
      
      // Delete from database
      if (objectId && whiteboardId) {
        await whiteboardAPI.deleteObject(whiteboardId, objectId);
        console.log('✅ Recipe deleted from database');
      }
      
      // Remove from canvas
      deleteNode(nodeId);
      console.log('✅ Recipe removed from canvas');
      
    } catch (error) {
      console.error('❌ Failed to delete recipe:', error);
      // Still remove from canvas even if database delete fails
      deleteNode(nodeId);
    }
  }, [whiteboardId, deleteNode]);
  
  // ==========================================
  // UPDATE RECIPE TAGS
  // ==========================================
  
  /**
   * Update tags for a recipe node
   * @param {string} nodeId - React Flow node ID
   * @param {Array<string>} newTags - New tags array
   */
  const handleTagsChange = useCallback(async (nodeId, newTags) => {
    try {
      console.log('🏷️ Updating tags for node:', nodeId, newTags);
      
      // Find the node to get object_id
      const node = nodes.find(n => n.id === nodeId);
      if (!node || !node.data.object_id) {
        console.warn('⚠️ Cannot update tags: node or object_id not found');
        return;
      }
      
      // Update in database
      await whiteboardAPI.updateObject(whiteboardId, node.data.object_id, {
        tags: newTags
      });
      
      // Update in local state
      updateNode(nodeId, { tags: newTags });
      
      console.log('✅ Tags updated');
      
    } catch (error) {
      console.error('❌ Failed to update tags:', error);
    }
  }, [whiteboardId, nodes, updateNode]);
  
  // ==========================================
  // UPDATE RECIPE COLOR
  // ==========================================
  
  /**
   * Update background color for a recipe node
   * @param {string} nodeId - React Flow node ID
   * @param {string} color - Hex color code
   */
  const handleRecipeColorChange = useCallback(async (nodeId, color) => {
    try {
      console.log('🎨 Updating color for node:', nodeId, color);
      
      // Find the node to get object_id
      const node = nodes.find(n => n.id === nodeId);
      if (!node || !node.data.object_id) {
        console.warn('⚠️ Cannot update color: node or object_id not found');
        return;
      }
      
      // Update in database using 'style' field (backend expects style object)
      await whiteboardAPI.updateObject(whiteboardId, node.data.object_id, {
        style: {
          backgroundColor: color,
          borderColor: node.data.borderColor || '#e5e7eb',
          borderWidth: node.data.borderWidth || 1,
          borderRadius: node.data.borderRadius || 8
        }
      });
      
      // Update in local state
      updateNode(nodeId, { backgroundColor: color });
      
      console.log('✅ Color updated and saved');
      
    } catch (error) {
      console.error('❌ Failed to update color:', error);
    }
  }, [whiteboardId, nodes, updateNode]);
  
  // ==========================================
  // HANDLE RECIPE CLICK (OPEN DETAIL)
  // ==========================================
  
  /**
   * Handle recipe card click - open detail modal
   * @param {number} recipeId - Recipe ID
   */
  const handleRecipeClick = useCallback((recipeId) => {
    console.log('👆 Recipe clicked:', recipeId);
    
    // Get recipe from cache
    const recipe = getRecipe(recipeId);
    
    if (!recipe) {
      console.warn('⚠️ Recipe not found in cache:', recipeId);
      return;
    }
    
    console.log('📖 Opening recipe detail for:', recipe.title || recipe.name);
    
    // Open detail modal using local state
    setSelectedRecipe(recipe);
    setIsDetailOpen(true);
  }, [getRecipe]);
  
  // ==========================================
  // CLOSE RECIPE DETAIL MODAL
  // ==========================================
  
  /**
   * Close the recipe detail modal
   */
  const closeRecipeDetail = useCallback(() => {
    setIsDetailOpen(false);
    setSelectedRecipe(null);
  }, []);
  
  // ==========================================
  // HANDLE TAG FILTER CLICK
  // ==========================================
  
  /**
   * Handle clicking a tag to filter by that tag
   * @param {string} tag - Tag to filter by
   */
  const handleTagFilterClick = useCallback((tag) => {
    console.log('🏷️ Tag filter clicked:', tag);
    // This will be implemented when we extract tag filtering logic
    // For now, just log it
  }, []);
  
  // ==========================================
  // BULK OPERATIONS
  // ==========================================
  
  /**
   * Add multiple recipes at once
   * @param {Array<Object>} recipes - Array of recipe objects
   * @param {Object} startPosition - Starting position {x, y}
   * @returns {Promise<Array<Object>>} Created nodes
   */
  const addRecipes = useCallback(async (recipes, startPosition = { x: 200, y: 150 }) => {
    console.log(`🍕 Adding ${recipes.length} recipes to canvas...`);
    
    const nodes = [];
    const spacing = 250; // Horizontal spacing between cards
    
    for (let i = 0; i < recipes.length; i++) {
      const recipe = recipes[i];
      const position = {
        x: startPosition.x + (i * spacing),
        y: startPosition.y
      };
      
      try {
        const node = await addRecipe(recipe, position);
        nodes.push(node);
      } catch (error) {
        console.error(`❌ Failed to add recipe ${recipe.id}:`, error);
      }
    }
    
    console.log(`✅ Added ${nodes.length}/${recipes.length} recipes`);
    return nodes;
  }, [addRecipe]);
  
  /**
   * Delete multiple recipes at once
   * @param {Array<string>} nodeIds - Array of node IDs to delete
   */
  const deleteRecipes = useCallback(async (nodeIds) => {
    console.log(`🗑️ Deleting ${nodeIds.length} recipes...`);
    
    for (const nodeId of nodeIds) {
      const node = nodes.find(n => n.id === nodeId);
      if (node && node.type === 'recipeCard') {
        await handleDeleteRecipe(
          nodeId,
          node.data.recipe_id,
          node.data.object_id
        );
      }
    }
    
    console.log('✅ Recipes deleted');
  }, [nodes, handleDeleteRecipe]);
  
  /**
   * Update tags for multiple recipes at once
   * @param {Array<string>} nodeIds - Array of node IDs
   * @param {Array<string>} tags - Tags to apply
   */
  const bulkUpdateTags = useCallback(async (nodeIds, tags) => {
    console.log(`🏷️ Bulk updating tags for ${nodeIds.length} recipes...`);
    
    for (const nodeId of nodeIds) {
      await handleTagsChange(nodeId, tags);
    }
    
    console.log('✅ Bulk tags updated');
  }, [handleTagsChange]);
  
  // ==========================================
  // HELPER: GET RECIPE NODE BY ID
  // ==========================================
  
  /**
   * Get a recipe node by recipe ID
   * @param {number} recipeId - Recipe ID
   * @returns {Object|null} Node or null if not found
   */
  const getRecipeNode = useCallback((recipeId) => {
    return nodes.find(n => 
      n.type === 'recipeCard' && 
      n.data.recipe_id === recipeId
    ) || null;
  }, [nodes]);
  
  /**
   * Check if a recipe is already on the canvas
   * @param {number} recipeId - Recipe ID
   * @returns {boolean} True if recipe is on canvas
   */
  const isRecipeOnCanvas = useCallback((recipeId) => {
    return getRecipeNode(recipeId) !== null;
  }, [getRecipeNode]);
  
  /**
   * Get all recipe nodes on canvas
   * @returns {Array<Object>} Array of recipe nodes
   */
  const getAllRecipeNodes = useCallback(() => {
    return nodes.filter(n => n.type === 'recipeCard');
  }, [nodes]);
  
  // ==========================================
  // RETURN API
  // ==========================================
  return {
    // Single operations
    addRecipe,
    deleteRecipe: handleDeleteRecipe,
    updateTags: handleTagsChange,
    updateColor: handleRecipeColorChange,
    
    // UI interactions
    handleRecipeClick,
    closeRecipeDetail,
    handleTagFilterClick,
    
    // Bulk operations
    addRecipes,
    deleteRecipes,
    bulkUpdateTags,
    
    // Helpers
    getRecipeNode,
    isRecipeOnCanvas,
    getAllRecipeNodes,
    
    // Modal state
    selectedRecipe,
    isDetailOpen,
  };
}
