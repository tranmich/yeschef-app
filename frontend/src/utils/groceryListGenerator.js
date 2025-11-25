/**
 * Grocery List Generation Utilities
 * 
 * Extracted from WhiteboardApp.js to improve maintainability
 * Handles fetching recipes and consolidating ingredients
 */

import { apiCall } from './api';
import { consolidateIngredients } from './groceryListUtils';

/**
 * Fetch full recipe details for a list of recipe nodes
 * @param {Array} recipeNodes - Selected recipe nodes from canvas
 * @returns {Promise<Array>} Full recipe objects with ingredients
 */
export async function fetchRecipesForGroceryList(recipeNodes) {
  const recipePromises = recipeNodes.map(async (node) => {
    try {
      const response = await apiCall(`/api/recipes/${node.data.recipe_id}`);
      console.log(`📋 Recipe ${node.data.recipe_id} fetched`);
      
      // Handle different response formats
      const recipe = response.success 
        ? (response.recipe || response.data) 
        : null;
      
      return recipe;
    } catch (err) {
      console.error(`Failed to fetch recipe ${node.data.recipe_id}:`, err);
      // Fallback: use node data if API fails
      console.warn(`⚠️ Using fallback data for recipe ${node.data.recipe_id}`);
      return {
        id: node.data.recipe_id,
        title: node.data.title || node.data.name,
        ingredients: node.data.ingredients || []
      };
    }
  });

  const recipes = (await Promise.all(recipePromises)).filter(r => r !== null);
  console.log(`📋 Fetched ${recipes.length} recipes for grocery list`);
  
  return recipes;
}

/**
 * Parse ingredients from various formats (JSON string, array, object, plain text)
 * @param {*} ingredients - Ingredients in any format
 * @param {string} recipeTitle - Recipe title for logging
 * @returns {Array} Normalized ingredient array
 */
export function parseIngredients(ingredients, recipeTitle) {
  let parsed = ingredients || [];
  
  // Parse if it's a JSON string
  if (typeof parsed === 'string') {
    try {
      // Try parsing as JSON array
      parsed = JSON.parse(parsed);
    } catch (e) {
      // Not JSON - split by newlines or semicolons (plain text format)
      console.log(`📝 Recipe "${recipeTitle}" has plain text ingredients, splitting...`);
      parsed = parsed
        .split(/[\n;]/) // Split by newline or semicolon
        .map(line => line.trim())
        .filter(line => line.length > 0)
        .map(line => ({
          ingredient: line,
          name: line
        }));
    }
  }

  // Convert to array if it's an object
  if (typeof parsed === 'object' && !Array.isArray(parsed)) {
    parsed = Object.values(parsed);
  }

  console.log(`🥕 Recipe "${recipeTitle}" has ${parsed?.length || 0} ingredients`);
  
  return Array.isArray(parsed) ? parsed : [];
}

/**
 * Extract and normalize all ingredients from recipes
 * @param {Array} recipes - Recipe objects with ingredients
 * @returns {Array} Flat array of ingredient objects with source recipe info
 */
export function extractAllIngredients(recipes) {
  const allIngredients = [];
  
  recipes.forEach(recipe => {
    const ingredients = parseIngredients(
      recipe.ingredients, 
      recipe.title || recipe.name
    );

    // Add each ingredient with source info
    if (ingredients.length > 0) {
      ingredients.forEach(ing => {
        // Handle both string and object formats
        const ingredientData = typeof ing === 'string' 
          ? { ingredient: ing, name: ing }
          : ing;
          
        allIngredients.push({
          ...ingredientData,
          source_recipe_id: recipe.id,
          source_recipe_name: recipe.title || recipe.name
        });
      });
    } else {
      console.warn(`⚠️ Recipe "${recipe.title}" has no ingredients`);
    }
  });

  console.log(`🥕 Extracted ${allIngredients.length} total ingredients`);
  return allIngredients;
}

/**
 * Main function: Generate grocery list from selected recipe nodes
 * @param {Array} selectedNodes - Selected recipe nodes from canvas
 * @returns {Promise<Object>} Object with { items, linkedRecipeIds, recipeTitles }
 */
export async function generateGroceryListFromRecipes(selectedNodes) {
  if (!selectedNodes || selectedNodes.length === 0) {
    throw new Error('No recipes selected');
  }

  console.log(`🎯 Generating grocery list from ${selectedNodes.length} recipes`);

  // 1. Fetch full recipe details
  const recipes = await fetchRecipesForGroceryList(selectedNodes);
  
  if (recipes.length === 0) {
    throw new Error('Failed to load recipe details');
  }

  // 2. Extract all ingredients
  const allIngredients = extractAllIngredients(recipes);
  
  if (allIngredients.length === 0) {
    throw new Error('No ingredients found in selected recipes');
  }

  // 3. Consolidate/merge duplicate ingredients
  const mergedItems = consolidateIngredients(allIngredients);
  
  console.log(`✅ Generated grocery list with ${mergedItems.length} items`);

  return {
    items: mergedItems,
    linkedRecipeIds: selectedNodes.map(node => node.data.recipe_id),
    recipeCount: selectedNodes.length
  };
}
