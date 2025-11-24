/**
 * Recipe Node Factory
 * 
 * Creates React Flow nodes for recipes with MINIMAL data duplication
 * Uses Recipe Cache as single source of truth
 */

/**
 * Create a recipe node for React Flow
 * 
 * BEFORE (duplicated data):
 * {
 *   data: {
 *     recipe: { id, title, image_url, prep_time, ... }, // Full object
 *     recipe_id: 123,  // Duplicate
 *     name: "Recipe Title",  // Duplicate
 *     image_url: "...",  // Duplicate
 *     prep_time: 30,  // Duplicate
 *     // ... more duplicates
 *   }
 * }
 * 
 * AFTER (lean data):
 * {
 *   data: {
 *     recipe_id: 123,  // ONLY store ID
 *     object_id: 456,  // Node-specific data
 *     tags: [...],  // Node-specific data
 *     backgroundColor: "#FFF",  // Node-specific data
 *     // ... only node-specific data
 *   }
 * }
 * 
 * RecipeCardNode will fetch recipe from cache using recipe_id!
 * 
 * @param {Object} options - Node configuration
 * @param {number} options.recipeId - Recipe ID (lookup in cache)
 * @param {number} options.objectId - Whiteboard object ID
 * @param {Object} options.position - {x, y} position
 * @param {Array} options.tags - Node tags
 * @param {string} options.backgroundColor - Node background color
 * @param {Function} options.onClick - Click handler
 * @param {Function} options.onDelete - Delete handler
 * @param {Function} options.onTagsChange - Tag change handler
 * @param {Function} options.onColorChange - Color change handler
 * @param {Function} options.onTagFilterClick - Tag filter handler
 * @param {number} options.commentCount - Comment count
 * @returns {Object} React Flow node
 */
export function createRecipeNode(options) {
  const {
    recipeId,
    objectId,
    position = { x: 200, y: 150 },
    tags = [],
    backgroundColor = '#FFFFFF',
    onClick,
    onDelete,
    onTagsChange,
    onColorChange,
    onTagFilterClick,
    commentCount = 0,
    hasNewComments = false
  } = options;
  
  return {
    id: `recipe-${recipeId}`,
    type: 'recipeCard',
    position,
    data: {
      // 🎯 LEAN DATA - Only store what's node-specific
      recipe_id: recipeId,  // ID to lookup in cache
      object_id: objectId,  // Whiteboard object ID
      
      // Node-specific data (not in recipe)
      tags,
      backgroundColor,
      commentCount,
      hasNewComments,
      
      // Handlers
      onClick,
      onDelete,
      onTagsChange,
      onColorChange,
      onTagFilterClick
    }
  };
}

/**
 * Normalize recipe data from API
 * Handles v1/v2 differences
 * 
 * @param {Object} apiRecipe - Recipe from API
 * @returns {Object} Normalized recipe
 */
export function normalizeRecipe(apiRecipe) {
  // Fix image URL if it starts with /api
  let imageUrl = apiRecipe.image_url;
  if (imageUrl && imageUrl.startsWith('/api')) {
    imageUrl = `${process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000'}${imageUrl}`;
  }
  
  return {
    id: apiRecipe.id,
    title: apiRecipe.title || apiRecipe.name || 'Untitled Recipe', // v2 vs v1
    image_url: imageUrl,
    prep_time: apiRecipe.prep_time || apiRecipe.prep_time_minutes || 0, // v2 vs v1
    cook_time: apiRecipe.cook_time || apiRecipe.cook_time_minutes || 0, // v2 vs v1
    total_time: apiRecipe.total_time,
    category: apiRecipe.category,
    created_by: apiRecipe.created_by || apiRecipe.user_id,
    created_by_name: apiRecipe.created_by_name || apiRecipe.author_name || 'Unknown',
    ingredients: apiRecipe.ingredients,
    instructions: apiRecipe.instructions,
    is_community_shared: apiRecipe.is_community_shared || false
  };
}
