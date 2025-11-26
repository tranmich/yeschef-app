import { useEffect, useCallback, useRef } from 'react';
import { useWhiteboard } from '../contexts/WhiteboardContext';
import { useRecipeCache } from '../contexts/RecipeCacheContext';
import whiteboardAPI from '../services/whiteboardAPI';
import { createRecipeNode, normalizeRecipe } from '../utils/recipeNodeFactory';
import { apiCall } from '../utils/api';

/**
 * useWhiteboardData Hook
 * 
 * Handles all data loading for whiteboard:
 * - Load whiteboard metadata
 * - Load saved objects (recipes, notes, etc.)
 * - Load comment counts
 * - Load user recipes (for picker)
 * - Batch fetch recipes (N+1 optimization)
 * 
 * Extracted from WhiteboardApp.js (Week 1, Day 3)
 */
export function useWhiteboardData() {
  const {
    whiteboardId,
    householdId,
    setWhiteboard,
    setNodes,
    setLoading,
    setError,
    setCommentCounts,
    addNodes,
  } = useWhiteboard();
  
  const { addRecipes } = useRecipeCache();
  const abortControllerRef = useRef(null);
  
  // ==========================================
  // LOAD WHITEBOARD ON MOUNT
  // ==========================================
  useEffect(() => {
    if (whiteboardId) {
      loadWhiteboard();
    }
    
    // Cleanup: Cancel any in-flight requests
    return () => {
      if (abortControllerRef.current) {
        console.log('🧹 Cancelling in-flight requests');
        abortControllerRef.current.abort();
      }
    };
  }, [whiteboardId]);
  
  // ==========================================
  // MAIN LOAD FUNCTION
  // ==========================================
  const loadWhiteboard = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Cancel previous request if still running
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      abortControllerRef.current = new AbortController();
      const signal = abortControllerRef.current.signal;
      
      console.log('📋 Loading whiteboard:', whiteboardId);
      
      // 1. Load whiteboard metadata
      const whiteboardData = await whiteboardAPI.getWhiteboard(whiteboardId);
      
      // Check if aborted
      if (signal.aborted) {
        console.log('⚠️ Request aborted');
        return;
      }
      
      const whiteboard = whiteboardData?.whiteboard || whiteboardData?.data || null;
      
      if (!whiteboard) {
        throw new Error('Whiteboard data not found in response');
      }
      
      setWhiteboard(whiteboard);
      console.log('✅ Whiteboard metadata loaded');
      
      // 2. Load saved objects (parallel)
      const [nodes, commentCounts] = await Promise.all([
        loadSavedObjects(whiteboard, signal),
        loadCommentCounts(whiteboardId, signal)
      ]);
      
      // Check if aborted
      if (signal.aborted) {
        console.log('⚠️ Request aborted');
        return;
      }
      
      // 3. Set loaded data
      addNodes(nodes);  // Uses validation & normalization!
      setCommentCounts(commentCounts);
      
      setLoading(false);
      console.log('✅ Whiteboard loaded successfully');
      
    } catch (error) {
      if (error.name === 'AbortError') {
        console.log('⚠️ Request aborted');
        return;
      }
      
      console.error('❌ Error loading whiteboard:', error);
      setError(error.message);
      setLoading(false);
    }
  }, [whiteboardId, setWhiteboard, setNodes, setLoading, setError, setCommentCounts, addNodes]);
  
  // ==========================================
  // LOAD SAVED OBJECTS (RECIPES, NOTES, ETC.)
  // ==========================================
  const loadSavedObjects = useCallback(async (whiteboard, signal) => {
    try {
      const savedObjects = whiteboard.objects || [];
      console.log('📦 Loading saved objects:', savedObjects.length);
      
      if (savedObjects.length === 0) {
        return [];
      }
      
      // Get unique recipe IDs
      const recipeIds = [...new Set(
        savedObjects
          .filter(obj => obj.entity_type === 'recipe' && obj.entity_id)
          .map(obj => obj.entity_id)
      )];
      
      console.log(`🏠 Found ${recipeIds.length} unique recipes to load`);
      
      // Batch fetch all recipes (N+1 optimization from Fix #4)
      const recipeMap = await batchFetchRecipes(recipeIds, signal);
      
      if (signal.aborted) return [];
      
      // Convert saved objects to React Flow nodes
      const nodes = savedObjects
        .map(obj => {
          // Handle notes
          if (obj.type === 'nt' || obj.object_type === 'note') {
            return createNoteNode(obj);
          }
          
          // Handle recipes
          if (obj.entity_type === 'recipe' && obj.entity_id) {
            const recipe = recipeMap[obj.entity_id];
            if (!recipe) {
              console.warn(`⚠️ Recipe ${obj.entity_id} not found, skipping`);
              return null;
            }
            return createRecipeNodeFromSavedObject(obj, recipe);
          }
          
          // Handle other types (grocery lists, meal plans, etc.)
          // TODO: Add handlers for other node types
          
          return null;
        })
        .filter(node => node !== null);
      
      console.log(`✅ Created ${nodes.length} nodes from saved objects`);
      return nodes;
      
    } catch (error) {
      console.error('❌ Error loading saved objects:', error);
      return [];
    }
  }, []);
  
  // ==========================================
  // BATCH FETCH RECIPES (N+1 OPTIMIZATION)
  // ==========================================
  const batchFetchRecipes = useCallback(async (recipeIds, signal) => {
    if (recipeIds.length === 0) {
      return {};
    }
    
    try {
      console.log(`🚀 Batch fetching ${recipeIds.length} recipes...`);
      
      const result = await apiCall('/api/v2/recipes/batch', {
        method: 'POST',
        body: JSON.stringify({
          recipe_ids: recipeIds,
          user_id: null  // Let backend handle household context
        })
      });
      
      if (signal.aborted) return {};
      
      if (result.success && result.data?.recipes) {
        // Normalize and add to cache
        const normalizedRecipes = result.data.recipes.map(normalizeRecipe);
        addRecipes(normalizedRecipes);
        
        // Create map for easy lookup
        const recipeMap = {};
        normalizedRecipes.forEach(recipe => {
          recipeMap[recipe.id] = recipe;
        });
        
        console.log(`✅ Batch loaded ${result.data.found_count}/${result.data.requested_count} recipes`);
        return recipeMap;
      }
      
      console.warn('⚠️ Batch recipe fetch returned no data');
      return {};
      
    } catch (error) {
      if (error.name === 'AbortError') throw error;
      
      console.error('❌ Batch recipe fetch failed:', error);
      
      // Fallback: Individual fetches (slower but reliable)
      return await fallbackIndividualFetch(recipeIds, signal);
    }
  }, [addRecipes]);
  
  // ==========================================
  // FALLBACK: INDIVIDUAL RECIPE FETCHES
  // ==========================================
  const fallbackIndividualFetch = useCallback(async (recipeIds, signal) => {
    console.log('🔄 Falling back to individual recipe fetches...');
    const recipeMap = {};
    
    for (const recipeId of recipeIds) {
      if (signal.aborted) break;
      
      try {
        const result = await whiteboardAPI.getWhiteboardRecipe(whiteboardId, recipeId);
        if (result.success && result.data) {
          const normalized = normalizeRecipe(result.data);
          recipeMap[recipeId] = normalized;
          addRecipes([normalized]);
        }
      } catch (error) {
        console.warn(`⚠️ Failed to load recipe ${recipeId}:`, error.message);
      }
    }
    
    console.log(`✅ Fallback loaded ${Object.keys(recipeMap).length} recipes`);
    return recipeMap;
  }, [whiteboardId, addRecipes]);
  
  // ==========================================
  // LOAD COMMENT COUNTS
  // ==========================================
  const loadCommentCounts = useCallback(async (whiteboardId, signal) => {
    try {
      console.log('💬 Loading comment counts...');
      
      const response = await apiCall(`/api/v2/comments/count?whiteboard_id=${whiteboardId}`);
      
      if (signal.aborted) return {};
      
      if (response.success && response.counts) {
        console.log(`✅ Comment counts loaded: ${Object.keys(response.counts).length} types`);
        return response.counts;
      }
      
      return {};
    } catch (error) {
      if (error.name === 'AbortError') throw error;
      
      console.error('❌ Error loading comment counts:', error);
      return {};
    }
  }, []);
  
  // ==========================================
  // HELPER: CREATE NOTE NODE
  // ==========================================
  function createNoteNode(obj) {
    const noteContent = obj.content || {};
    
    // Handle position (array or object format)
    let posX = 100, posY = 100, posW = 300, posH = 250;
    
    if (Array.isArray(obj.position)) {
      posX = obj.position[0] || 100;
      posY = obj.position[1] || 100;
      posW = obj.position[2] || 300;
      posH = obj.position[3] || 250;
    } else if (obj.position && typeof obj.position === 'object') {
      posX = obj.position.x || 100;
      posY = obj.position.y || 100;
      posW = obj.position.width || 300;
      posH = obj.position.height || 250;
    }
    
    return {
      id: `note-${obj.id}`,
      type: 'note',
      position: { x: posX, y: posY },
      data: {
        object_id: obj.id,
        name: noteContent.name || 'Note',
        content: noteContent.html || '<p></p>',
        backgroundColor: noteContent.backgroundColor || '#FEF3C7',
        fontSize: noteContent.fontSize || '18px',
        commentCount: 0,  // Will be updated by comment counts
        createdBy: obj.created_by_name || obj.created_by_email || 'Unknown',
        // Handlers will be added by WhiteboardApp
      },
      style: {
        width: posW,
        height: posH
      }
    };
  }
  
  // ==========================================
  // HELPER: CREATE RECIPE NODE FROM SAVED OBJECT
  // ==========================================
  function createRecipeNodeFromSavedObject(obj, recipe) {
    // Handle position (array or object format)
    let posX = 200, posY = 150;
    
    if (Array.isArray(obj.position)) {
      posX = obj.position[0] || 200;
      posY = obj.position[1] || 150;
    } else if (obj.position && typeof obj.position === 'object') {
      posX = obj.position.x || 200;
      posY = obj.position.y || 150;
    }
    
    // Use factory for consistent structure
    return createRecipeNode({
      recipeId: recipe.id,
      objectId: obj.id,
      position: { x: posX, y: posY },
      tags: obj.tags || [],
      backgroundColor: obj.background_color || '#FFFFFF',
      commentCount: 0,  // Will be updated by comment counts
      hasNewComments: false,
      // Handlers will be added by WhiteboardApp
    });
  }
  
  // ==========================================
  // RETURN API
  // ==========================================
  return {
    loadWhiteboard,
    loading: false,  // Expose if needed
  };
}
