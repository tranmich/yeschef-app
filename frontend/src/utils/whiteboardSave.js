/**
 * Whiteboard Save Utilities
 * 
 * Extracted from WhiteboardApp.js to improve maintainability
 * Handles saving all node types to the database
 */

import whiteboardAPI from '../services/whiteboardAPI';
import { apiCall } from './api';

/**
 * Save recipe card nodes to whiteboard
 * @param {Array} nodes - All canvas nodes
 * @param {number} whiteboardId - Whiteboard ID
 * @returns {Promise<Object>} Response with counts
 */
export async function saveRecipeNodes(nodes, whiteboardId) {
  const recipeNodes = nodes
    .filter(node => node.type === 'recipeCard' && node.data.recipe_id)
    .map(node => ({
      recipe_id: node.data.recipe_id,
      tags: node.data.tags || [],
      position: {
        x: node.position.x,
        y: node.position.y,
        width: 300,
        height: 400,
        z: 0
      }
    }));

  console.log(`📦 Saving ${recipeNodes.length} recipe cards`);

  if (recipeNodes.length === 0) {
    return { success: true, data: { updated_count: 0, created_count: 0, total_processed: 0 } };
  }

  const response = await whiteboardAPI.bulkUpdateObjects(whiteboardId, recipeNodes);
  
  if (!response.success) {
    throw new Error(response.message || 'Failed to save recipes');
  }

  console.log('✅ Recipes saved:', response.data);
  return response;
}

/**
 * Save grocery list nodes to whiteboard
 * @param {Array} nodes - All canvas nodes
 * @param {number} whiteboardId - Whiteboard ID
 * @param {number} householdId - Household ID
 * @param {Function} updateNodeCallback - Callback to update node with new dbId
 * @returns {Promise<Object>} Response with counts
 */
export async function saveGroceryListNodes(nodes, whiteboardId, householdId, updateNodeCallback) {
  const groceryListNodes = nodes.filter(n => n.type === 'groceryListNode');
  console.log(`🛒 Saving ${groceryListNodes.length} grocery lists...`);

  let savedCount = 0;
  let createdCount = 0;
  let updatedCount = 0;

  for (const node of groceryListNodes) {
    const saveData = {
      name: node.data.name,
      items: node.data.items || [],
      household_id: householdId,
      widget_position: {
        x: node.position.x,
        y: node.position.y,
        width: node.width || node.style?.width || 350,
        height: node.height || node.style?.height || 500
      },
      linked_recipe_ids: node.data.linkedRecipeIds || []
    };

    try {
      let result;

      if (node.data.dbId) {
        // Update existing
        result = await whiteboardAPI.updateWhiteboardGroceryList(
          whiteboardId,
          node.data.dbId,
          saveData
        );
        if (result.success) {
          updatedCount++;
          console.log(`✅ Updated grocery list ${node.data.dbId}`);
        }
      } else {
        // Create new
        result = await whiteboardAPI.createWhiteboardGroceryList(whiteboardId, saveData);
        if (result.success) {
          createdCount++;
          console.log(`✅ Created grocery list ${result.data.id}`);
          
          // Update node with new dbId via callback
          if (updateNodeCallback) {
            updateNodeCallback(node.id, result.data.id);
          }
        }
      }

      if (result.success) {
        savedCount++;
      }
    } catch (err) {
      console.error('❌ Error saving grocery list:', node.data.name, err);
    }
  }

  console.log(`✅ Grocery lists saved: ${savedCount}/${groceryListNodes.length}`);
  return { savedCount, createdCount, updatedCount, total: groceryListNodes.length };
}

/**
 * Save meal plan container nodes to whiteboard
 * @param {Array} nodes - All canvas nodes
 * @param {number} whiteboardId - Whiteboard ID
 * @returns {Promise<Object>} Response with counts
 */
export async function saveMealPlanNodes(nodes, whiteboardId) {
  const mealPlanNodes = nodes.filter(n => n.type === 'mealPlanContainer');
  console.log(`📅 Saving ${mealPlanNodes.length} meal plan containers...`);

  let savedCount = 0;

  for (const node of mealPlanNodes) {
    try {
      if (node.data.objectId && whiteboardId) {
        await whiteboardAPI.updateObject(whiteboardId, node.data.objectId, {
          position: {
            x: node.position.x,
            y: node.position.y,
            width: node.width || node.style?.width || 600,
            height: node.height || node.style?.height || 800
          }
        });
        savedCount++;
        console.log(`✅ Saved meal plan "${node.data.name}" position/size`);
      }
    } catch (error) {
      console.error(`❌ Error saving meal plan "${node.data.name}":`, error);
    }
  }

  console.log(`✅ Meal plans saved: ${savedCount}/${mealPlanNodes.length}`);
  return { savedCount, total: mealPlanNodes.length };
}

/**
 * Save note nodes to whiteboard
 * @param {Array} nodes - All canvas nodes
 * @param {number} whiteboardId - Whiteboard ID
 * @returns {Promise<Object>} Response with counts
 */
export async function saveNoteNodes(nodes, whiteboardId) {
  const noteNodes = nodes.filter(n => n.type === 'note');
  console.log(`📝 Saving ${noteNodes.length} notes...`);

  let savedCount = 0;

  for (const node of noteNodes) {
    try {
      // Extract object ID from node.id (format: "note-{objectId}")
      const objectId = parseInt(node.id.replace('note-', ''));

      if (objectId && whiteboardId) {
        await apiCall(`/api/v2/whiteboard/${whiteboardId}/o/${objectId}`, {
          method: 'PATCH',
          body: JSON.stringify({
            position: [
              node.position.x,
              node.position.y,
              node.width || node.style?.width || 300,
              node.height || node.style?.height || 250,
              0 // z-index
            ],
            content: {
              type: 'note',
              html: node.data.content,
              backgroundColor: node.data.backgroundColor,
              fontSize: node.data.fontSize
            }
          })
        });
        savedCount++;
      }
    } catch (error) {
      console.error(`❌ Error saving note:`, error);
    }
  }

  console.log(`✅ Notes saved: ${savedCount}/${noteNodes.length}`);
  return { savedCount, total: noteNodes.length };
}

/**
 * Main save function - orchestrates saving all node types
 * @param {Array} nodes - All canvas nodes
 * @param {number} whiteboardId - Whiteboard ID
 * @param {number} householdId - Household ID
 * @param {Function} updateNodeCallback - Callback to update nodes
 * @returns {Promise<Object>} Summary of what was saved
 */
export async function saveAllWhiteboardNodes(nodes, whiteboardId, householdId, updateNodeCallback) {
  // Save all node types
  const recipeResult = await saveRecipeNodes(nodes, whiteboardId);
  const groceryResult = await saveGroceryListNodes(nodes, whiteboardId, householdId, updateNodeCallback);
  const mealPlanResult = await saveMealPlanNodes(nodes, whiteboardId);
  const noteResult = await saveNoteNodes(nodes, whiteboardId);

  return {
    recipes: recipeResult.data?.updated_count || 0,
    groceryLists: groceryResult.savedCount,
    mealPlans: mealPlanResult.savedCount,
    notes: noteResult.savedCount
  };
}
