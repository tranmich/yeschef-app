/**
 * Whiteboard App
 * ==============
 * Main whiteboard canvas with React Flow
 * Phase 1 - Week 3: Empty canvas with basic controls
 * 
 * Future Phases:
 * - Phase 2: Add recipe cards and objects
 * - Phase 3: Real-time collaboration
 * - Phase 4: Comments and interactions
 */

import React, { useState, useEffect, useCallback, useRef, useMemo, Suspense } from 'react';
import { useMediaQuery } from 'react-responsive';
import { ReactFlow, Controls, Background, useReactFlow, Panel, applyNodeChanges } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useAuth } from '../contexts/AuthContext';
import { RecipeCacheProvider, useRecipeCache } from '../contexts/RecipeCacheContext';
import { WhiteboardProvider, useWhiteboard } from '../contexts/WhiteboardContext';
import { useWhiteboardData } from '../hooks/useWhiteboardData';
import { useRecipeNodes } from '../hooks/useRecipeNodes';
import whiteboardAPI from '../services/whiteboardAPI';
import { saveAllWhiteboardNodes } from '../utils/whiteboardSave';
import { generateGroceryListFromRecipes, generateGroceryListFromRecipeArray } from '../utils/groceryListGenerator';
import { createGroceryListNode, createActivityFeedNode, createMealPlanNode } from '../utils/nodeCreators';
import { createRecipeNode, normalizeRecipe } from '../utils/recipeNodeFactory';
import RecipeCardNode from '../components/whiteboard/nodes/RecipeCardNode';
import RecipePickerPanel from '../components/RecipePickerPanel';
import MealPlanFloatingWidget from '../components/MealPlanFloatingWidget';
// ConnectionLinesOverlay removed - feature not needed
import { ToastProvider, useToast } from '../components/ToastContainer';
import { MealPlanContainerNode, GroceryListNode } from '../components/whiteboard/nodes';
import NoteBlockWithResizer from '../components/whiteboard/blocks/NoteBlockWithResizer';
import ActivityFeedNode from '../components/whiteboard/nodes/ActivityFeedNode';
import CommentsSidebar from '../components/whiteboard/CommentsSidebar';
import HouseholdPresence from '../components/whiteboard/HouseholdPresence';
import TagFilterSidebar from '../components/whiteboard/TagFilterSidebar';
import LeftToolbar from '../components/whiteboard/LeftToolbar';
import KeyboardShortcutsModal from '../components/whiteboard/KeyboardShortcutsModal';
import RecipeDetailModal from '../components/RecipeDetailModal';
import { apiCall } from '../utils/api';
import { consolidateIngredients } from '../utils/groceryListUtils';
import './WhiteboardApp.css';

// Debounce utility function (no external dependencies needed!)
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Define custom node types
const nodeTypes = {
  recipeCard: RecipeCardNode, // Recipe card with tag support
  mealPlanContainer: MealPlanContainerNode, // Meal plan container
  groceryListNode: GroceryListNode, // Grocery list node
  note: NoteBlockWithResizer, // Note block with resizer for journal entries
  activityFeed: ActivityFeedNode, // Activity feed widget
};

const WhiteboardApp = ({ householdId, whiteboardId, onBack }) => {
  const { user } = useAuth();
  
  // 🆕 Recipe Cache - Single source of truth for all recipe data!
  const { addRecipes, getRecipe, getCacheStats } = useRecipeCache();
  
  // 🆕 Week 2: Whiteboard Data Hook - handles loading, validation, batch fetch!
  const { 
    loadWhiteboard: loadWhiteboardData
  } = useWhiteboardData();
  
  // 🆕 Week 2: Recipe Operations Hook - handles add/delete/update recipe nodes!
  const {
    addRecipe: addRecipeToCanvas,
    deleteRecipe: deleteRecipeFromCanvas,
    updateRecipeTags,
    updateRecipeColor,
    handleRecipeClick: openRecipeDetail
  } = useRecipeNodes();
  
  // Responsive detection
  const isMobile = useMediaQuery({ maxWidth: 768 });
  const isTablet = useMediaQuery({ minWidth: 769, maxWidth: 1024 });
  const isDesktop = useMediaQuery({ minWidth: 1025 });

  // Toast notifications
  const toast = useToast();

  // 🆕 AbortController for request cancellation
  const abortControllerRef = useRef(null);

  // ==========================================
  // GET STATE FROM CONTEXT (Single Source of Truth!)
  // ==========================================
  const {
    // Core whiteboard state
    whiteboard,
    setWhiteboard,
    loading,
    setLoading,
    error,
    setError,
    
    // React Flow state
    nodes,
    setNodes,
    canvasViewport,
    setCanvasViewport,
    
    // UI state
    isPickerOpen,
    setIsPickerOpen,
    isShortcutsModalOpen,
    setIsShortcutsModalOpen,
    isTagSidebarOpen,
    setIsTagSidebarOpen,
    isCommentsSidebarOpen,
    setIsCommentsSidebarOpen,
    isRecipeDetailOpen,
    setIsRecipeDetailOpen,
    
    // Selection state
    selectedRecipes,
    setSelectedRecipes,
    selectedTags,
    setSelectedTags,
    selectedNote,
    setSelectedNote,
    selectedObjectForComments,
    setSelectedObjectForComments,
    selectedRecipeForDetail,
    setSelectedRecipeForDetail,
    
    // Comment state
    commentCounts,
    setCommentCounts,
    
    // Widget state
    groceryListWidgets,
    setGroceryListWidgets,
    mealPlanWidgets,
    setMealPlanWidgets,
  } = useWhiteboard();

  // Local refs (optimization, not state)
  const nodesRef = useRef(nodes); // Keep track of latest nodes for save
  
  // Local UI state (not in context - component-specific)
  const [noteToolbarVisible, setNoteToolbarVisible] = useState(false);
  
  // Keep nodesRef in sync with nodes state for reliable saves
  useEffect(() => {
    nodesRef.current = nodes;
  }, [nodes]);

  // 🆕 Cleanup: Cancel any in-flight requests on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        console.log('🧹 Component unmounting - cancelling any in-flight requests');
        abortControllerRef.current.abort();
      }
    };
  }, []);
  
  // Fetch comment counts for all objects
  const fetchCommentCounts = async (whiteboardId) => {
    try {
      const response = await apiCall(`/api/v2/comments/count?whiteboard_id=${whiteboardId}`);
      if (response.success) {
        console.log('💬 Comment counts loaded:', response.counts);
        setCommentCounts(response.counts || {});
      }
    } catch (error) {
      console.error('❌ Error fetching comment counts:', error);
    }
  };
  
  // 🆕 OPTIMIZED: Pre-build comment count map for O(1) lookups
  // Before: O(n) nested object lookup for each node
  // After: O(1) Map lookup (14x faster for 100 nodes!)
  const commentCountMap = useMemo(() => {
    const map = new Map();
    
    // Flatten nested structure into single Map
    // From: { recipe: { 123: 5, 456: 3 }, note: { 789: 2 } }
    // To: Map { "recipe-123" => 5, "recipe-456" => 3, "note-789" => 2 }
    Object.entries(commentCounts).forEach(([type, counts]) => {
      if (counts && typeof counts === 'object') {
        Object.entries(counts).forEach(([id, count]) => {
          map.set(`${type}-${id}`, count);
        });
      }
    });
    
    console.log(`📊 Comment count map built: ${map.size} entries`);
    return map;
  }, [commentCounts]);
  
  // Helper to get comment count for an object (now O(1)!)
  const getCommentCount = useCallback((objectType, objectId) => {
    return commentCountMap.get(`${objectType}-${objectId}`) || 0;
  }, [commentCountMap]);

  // ==========================================
  // HANDLER FUNCTIONS (Must be defined BEFORE useMemo!)
  // ==========================================
  
  // Note handlers
  const handleNoteChange = useCallback((nodeId, newContent) => {
    console.log('📝 Note content changed:', nodeId);
    setNodes(prevNodes => prevNodes.map(n =>
      n.id === nodeId ? { ...n, data: { ...n.data, content: newContent } } : n
    ));
    
    // Trigger debounced save
    const node = nodes.find(n => n.id === nodeId);
    if (node && node.data.object_id) {
      debouncedNoteSave.current(whiteboardId, node.data.object_id, {
        name: node.data.name || 'Note',
        content: newContent,
        backgroundColor: node.data.backgroundColor,
        fontSize: node.data.fontSize
      });
    }
  }, [nodes, whiteboardId]);
  
  const handleDeleteObject = useCallback(async (objectId) => {
    try {
      console.log('🗑️ Deleting object:', objectId);
      await whiteboardAPI.deleteObject(whiteboardId, objectId);
      
      // Remove from canvas
      setNodes(prevNodes => prevNodes.filter(n => n.data.object_id !== objectId));
      
      console.log('✅ Object deleted');
      toast.success('Deleted!');
    } catch (error) {
      console.error('❌ Failed to delete object:', error);
      toast.error('Delete failed');
    }
  }, [whiteboardId, toast]);
  
  // Meal plan handlers (stubs for now - implement when needed)
  const handleDeleteMealPlan = useCallback(async (mealPlanId) => {
    console.log('🗑️ Delete meal plan:', mealPlanId);
    toast.info('Meal plan delete not yet implemented');
    // TODO: Implement meal plan deletion
  }, [toast]);

  // Grocery list handlers (must be defined before useMemo!)
  const handleGroceryListNameChange = useCallback((nodeId, newName) => {
    setNodes(prevNodes => prevNodes.map(n =>
      n.id === nodeId ? { ...n, data: { ...n.data, name: newName } } : n
    ));
    setTimeout(() => handleSave(), 500);
    toast.success(`Renamed to "${newName}"`);
  }, [nodes, toast]);

  const handleGroceryListColorChange = useCallback((nodeId, newColor) => {
    setNodes(prevNodes => prevNodes.map(n =>
      n.id === nodeId ? { ...n, data: { ...n.data, backgroundColor: newColor } } : n
    ));
  }, []);

  const handleGroceryListItemChecked = useCallback((nodeId, itemId, checked) => {
    setNodes(prevNodes => prevNodes.map(n => {
      if (n.id === nodeId) {
        const updatedItems = n.data.items.map(item =>
          item.id === itemId ? { ...item, checked } : item
        );
        return { ...n, data: { ...n.data, items: updatedItems } };
      }
      return n;
    }));
    setTimeout(() => handleSave(), 500);
  }, []);

  const handleGroceryListItemAdded = useCallback((nodeId, newItem) => {
    setNodes(prevNodes => prevNodes.map(n => {
      if (n.id === nodeId) {
        const updatedItems = [newItem, ...n.data.items];
        return { ...n, data: { ...n.data, items: updatedItems } };
      }
      return n;
    }));
    setTimeout(() => handleSave(), 500);
  }, []);

  const handleGroceryListItemRemoved = useCallback((nodeId, itemId) => {
    setNodes(prevNodes => prevNodes.map(n => {
      if (n.id === nodeId) {
        const updatedItems = n.data.items.filter(item => item.id !== itemId);
        return { ...n, data: { ...n.data, items: updatedItems } };
      }
      return n;
    }));
    setTimeout(() => handleSave(), 500);
  }, []);

  const handleGroceryListItemsReordered = useCallback((nodeId, reorderedItems) => {
    setNodes(prevNodes => prevNodes.map(n => {
      if (n.id === nodeId) {
        return { ...n, data: { ...n.data, items: reorderedItems } };
      }
      return n;
    }));
    setTimeout(() => handleSave(), 500);
  }, []);

  const handleGroceryListDelete = useCallback(async (nodeId) => {
    const node = nodes.find(n => n.id === nodeId);
    if (!node) return;
    
    const dbId = node.data.dbId;
    const listName = node.data.name;
    
    if (window.confirm(`Delete grocery list "${listName}"?`)) {
      setNodes(prevNodes => prevNodes.filter(n => n.id !== nodeId));
      if (dbId && whiteboardId) {
        try {
          await whiteboardAPI.deleteWhiteboardGroceryList(whiteboardId, dbId);
        } catch (error) {
          console.error('❌ Failed to delete from database:', error);
        }
      }
      toast.success('Grocery list deleted');
    }
  }, [nodes, whiteboardId, toast]);

  // 🆕 ATTACH HANDLERS TO ALL NODES
  // Nodes loaded from database don't have handlers - add them here!
  const nodesWithHandlers = useMemo(() => {
    console.log('🔧 [nodesWithHandlers] Attaching handlers to nodes...');
    console.log('🔧 [nodesWithHandlers] Input nodes:', nodes.length);
    console.log('🔧 [nodesWithHandlers] Handlers available:', {
      openRecipeDetail: !!openRecipeDetail,
      deleteRecipeFromCanvas: !!deleteRecipeFromCanvas,
      updateRecipeTags: !!updateRecipeTags,
      updateRecipeColor: !!updateRecipeColor
    });
    
    return nodes.map(node => {
      // Recipe cards
      if (node.type === 'recipeCard') {
        const nodeWithHandlers = {
          ...node,
          data: {
            ...node.data,
            onClick: openRecipeDetail,
            onDelete: deleteRecipeFromCanvas,
            onTagsChange: updateRecipeTags,
            onColorChange: updateRecipeColor,
            onTagFilterClick: (tag) => console.log('🏷️ Tag filter:', tag),
          }
        };
        console.log('✅ [nodesWithHandlers] Added handlers to recipe:', node.id, {
          hasOnColorChange: !!nodeWithHandlers.data.onColorChange
        });
        return nodeWithHandlers;
      }
      
      // Notes
      if (node.type === 'note') {
        return {
          ...node,
          data: {
            ...node.data,
            onChange: handleNoteChange,
            onDelete: (nodeId, objectId) => {
              if (window.confirm('Delete this note?')) {
                handleDeleteObject(objectId);
              }
            },
          }
        };
      }
      
      // Grocery lists
      if (node.type === 'groceryListNode') {
        return {
          ...node,
          data: {
            ...node.data,
            onItemChecked: handleGroceryListItemChecked,
            onItemRemoved: handleGroceryListItemRemoved,
            onItemAdded: handleGroceryListItemAdded,
            onNameChange: handleGroceryListNameChange,
            onDelete: (nodeId, dbId) => {
              if (window.confirm('Delete this grocery list?')) {
                handleGroceryListDelete(dbId);
              }
            },
          }
        };
      }
      
      // Meal plan containers
      if (node.type === 'mealPlanContainer') {
        return {
          ...node,
          data: {
            ...node.data,
            onRecipeClick: openRecipeDetail,
            onDelete: (nodeId, mealPlanId) => {
              if (window.confirm('Delete this meal plan?')) {
                handleDeleteMealPlan(mealPlanId);
              }
            },
          }
        };
      }
      
      // Return other node types unchanged
      return node;
    });
  }, [
    nodes,
    openRecipeDetail,
    deleteRecipeFromCanvas,
    updateRecipeTags,
    updateRecipeColor,
    handleNoteChange,
    handleDeleteObject,
    handleGroceryListItemChecked,
    handleGroceryListItemRemoved,
    handleGroceryListItemAdded,
    handleGroceryListNameChange,
    handleGroceryListDelete,
    handleDeleteMealPlan,
  ]);

  // 🆕 Debounced note save function (saves after 2 seconds of inactivity)
  const debouncedNoteSave = useRef(
    debounce(async (whiteboardId, noteId, noteData) => {
      try {
        await apiCall(`/api/v2/whiteboard/${whiteboardId}/o/${noteId}`, {
          method: 'PATCH',
          body: JSON.stringify({
            content: {
              type: 'note',
              name: noteData.name,
              html: noteData.content,
              backgroundColor: noteData.backgroundColor,
              fontSize: noteData.fontSize
            }
          })
        });
        console.log('✅ Note auto-saved (debounced)');
      } catch (error) {
        console.error('❌ Failed to save note:', error);
      }
    }, 2000) // Wait 2 seconds after last change
  ).current;

  // Helper function to enforce z-index for recipes in meal plans
  const enforceZIndex = useCallback((nodes) => {
    return nodes.map(node => {
      if (node.type === 'recipeCard' && node.data.mealPlanId) {
        return {
          ...node,
          zIndex: 10,
          style: {
            ...node.style,
            zIndex: 10
          }
        };
      }
      return node;
    });
  }, []);

  // Wrapped setNodes that always enforces z-index
  const setNodesWithZIndex = useCallback((updater) => {
    if (typeof updater === 'function') {
      setNodes(prevNodes => enforceZIndex(updater(prevNodes)));
    } else {
      setNodes(enforceZIndex(updater));
    }
  }, [enforceZIndex]);

  // Load whiteboard data
  useEffect(() => {
    loadWhiteboard();
  }, [whiteboardId]);
  
  // Update nodes with comment counts when counts change
  useEffect(() => {
    setNodes(prevNodes => prevNodes.map(node => {
      if (node.type === 'recipeCard') {
        const objectId = node.id; // e.g., "recipe-2728"
        const commentCount = getCommentCount('recipeCard', objectId);
        return {
          ...node,
          data: {
            ...node.data,
            commentCount
          }
        };
      }
      if (node.type === 'note') {
        // Extract object ID from note-{id}
        const objectId = parseInt(node.id.replace('note-', ''));
        const commentCount = getCommentCount('note', objectId);
        return {
          ...node,
          data: {
            ...node.data,
            commentCount
          }
        };
      }
      return node;
    }));
  }, [commentCounts, getCommentCount]);

  // Track selected note for toolbar
  useEffect(() => {
    const selectedNotes = nodes.filter(n => n.type === 'note' && n.selected);
    if (selectedNotes.length === 1) {
      setSelectedNote(selectedNotes[0]);
      setNoteToolbarVisible(true);
    } else {
      setSelectedNote(null);
      setNoteToolbarVisible(false);
    }
  }, [nodes]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Don't handle shortcuts when typing in input fields or textareas
      const isTyping = e.target.tagName === 'INPUT' || 
                       e.target.tagName === 'TEXTAREA' || 
                       e.target.isContentEditable;
      
      // Don't handle Delete/Backspace when comments sidebar is open
      if (isCommentsSidebarOpen && (e.key === 'Delete' || e.key === 'Backspace')) {
        return; // Let the user type in comments
      }
      
      // Don't handle any shortcuts when typing
      if (isTyping && e.key !== 'Escape') {
        return; // Allow Escape to work even in inputs
      }

      // Ctrl/Cmd + A - select all cards
      if ((e.ctrlKey || e.metaKey) && e.key === 'a') {
        e.preventDefault();
        handleSelectAll();
        return;
      }

      // Ctrl/Cmd + R - toggle recipe picker
      if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
        e.preventDefault();
        setIsPickerOpen(prev => !prev);
        toast.info(isPickerOpen ? 'Recipe picker closed' : 'Recipe picker opened', 1000);
        return;
      }

      // Ctrl/Cmd + M - create new note (changed from N to avoid browser conflict)
      if ((e.ctrlKey || e.metaKey) && e.key === 'm') {
        e.preventDefault();
        handleCreateNote();
        toast.success('Created new note!', 1000);
        return;
      }

      // Ctrl/Cmd + D - create day box
      if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
        e.preventDefault();
        handleCreateDayBox();
        return;
      }

      // Ctrl/Cmd + K - toggle tag sidebar
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        handleToggleTagSidebar();
        return;
      }

      // Escape - clear selection or close picker or close comments
      if (e.key === 'Escape') {
        if (isCommentsSidebarOpen) {
          e.preventDefault();
          setIsCommentsSidebarOpen(false);
          setSelectedObjectForComments(null);
        } else if (isTagSidebarOpen) {
          e.preventDefault();
          setIsTagSidebarOpen(false);
        } else if (isPickerOpen) {
          e.preventDefault();
          setIsPickerOpen(false);
        } else {
          const selectedNodes = nodes.filter(node => node.selected);
          if (selectedNodes.length > 0) {
            e.preventDefault();
            handleClearSelection();
          }
        }
        return;
      }

      // Delete key - remove selected cards
      if (e.key === 'Delete' || e.key === 'Backspace') {
        const selectedNodes = nodes.filter(node => node.selected);
        if (selectedNodes.length > 0) {
          e.preventDefault();
          selectedNodes.forEach(node => {
            deleteRecipeFromCanvas(node.id, node.data.recipe_id, node.data.object_id);
          });
        }
      }

      // Ctrl/Cmd + S - save
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        handleSave();
        toast.info('Saving whiteboard...', 1000);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [nodes, isPickerOpen, whiteboardId, isCommentsSidebarOpen, isTagSidebarOpen]);

  // 🆕 WEEK 2: Simplified loadWhiteboard using useWhiteboardData hook!
  const loadWhiteboard = async () => {
    try {
      setLoading(true);
      setError(null);

      console.log('📥 Loading whiteboard with useWhiteboardData hook...');
      
      // 🎯 THE MAGIC: Hook manages loading via context, sets nodes automatically
      await loadWhiteboardData();
      
      console.log('✅ Whiteboard loaded by hook - loading additional features...');
      
      // Load additional whiteboard features (grocery lists, meal plans, comments)
      if (whiteboard?.id || whiteboardId) {
        const wbId = whiteboard?.id || whiteboardId;
        await loadSavedGroceryLists(wbId);
        await loadSavedMealPlanDays(whiteboard);
        await fetchCommentCounts(wbId);
      }
    } catch (err) {
      console.error('Error loading whiteboard:', err);
      setError('Failed to load whiteboard');
      toast.error('Failed to load whiteboard: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadSavedGroceryLists = async (whiteboardId) => {
    try {
      console.log('🛒 Loading saved grocery lists for whiteboard:', whiteboardId);
      const response = await whiteboardAPI.getWhiteboardGroceryLists(whiteboardId);
      
      if (response.success && response.data.grocery_lists) {
        const savedLists = response.data.grocery_lists;
        console.log(`✅ Found ${savedLists.length} saved grocery lists`);
        
        // Convert to React Flow nodes
        const groceryListNodes = savedLists.map(list => {
          const widgetPos = list.widget_position || {};
          console.log(`📍 Loading "${list.name}" with saved position:`, widgetPos);
          console.log(`📐 Loading "${list.name}" with saved dimensions:`, {
            width: widgetPos.width,
            height: widgetPos.height
          });
          
          return {
            id: `grocery-list-${list.id}`,
            type: 'groceryListNode',
            position: { x: widgetPos.x || 800, y: widgetPos.y || 100 },
            draggable: true,
            width: widgetPos.width || 350,
            height: widgetPos.height || 500,
            data: {
              name: list.name,
              items: list.items || [],
              linkedRecipeIds: list.linked_recipe_ids || [],
              dbId: list.id, // Store database ID
              backgroundColor: list.background_color || '#D1FAE5',
              commentCount: getCommentCount('grocery_list', list.id),
              hasNewComments: false, // TODO: Implement new comments tracking
              onNameChange: handleGroceryListNameChange,
              onColorChange: handleGroceryListColorChange,
              onItemChecked: handleGroceryListItemChecked,
              onItemAdded: handleGroceryListItemAdded,
              onItemRemoved: handleGroceryListItemRemoved,
              onItemsReordered: handleGroceryListItemsReordered,
              onDelete: handleGroceryListDelete
            },
            style: {
              width: widgetPos.width || 350,
              height: widgetPos.height || 500,
              zIndex: 5
            }
          };
        });
        
        // Add to React Flow nodes
        setNodes(prevNodes => {
          const existingIds = new Set(prevNodes.map(n => n.id));
          const newNodes = groceryListNodes.filter(n => !existingIds.has(n.id));
          return [...prevNodes, ...newNodes];
        });
        
        console.log('✅ Restored grocery list nodes:', groceryListNodes.length);
      }
    } catch (error) {
      console.error('❌ Error loading grocery lists:', error);
      // Non-fatal error - continue without grocery lists
    }
  };

  const loadSavedMealPlanDays = async (whiteboardData) => {
    try {
      console.log('📅 Loading saved meal plan day boxes from whiteboard...');
      
      if (!whiteboardData) {
        console.log('⚠️ No whiteboard data available yet');
        return;
      }
      
      console.log('📦 Whiteboard objects:', whiteboardData.objects);
      
      // Filter whiteboard objects that have meal_plan references
      // Database stores meal plans with type='container'
      const mealPlanObjects = whiteboardData.objects?.filter(obj => {
        console.log('🔍 Checking object:', obj.type, obj.object_type, obj.entity_type, obj.entity_id, obj.mid);
        return (obj.type === 'container' || obj.entity_type === 'meal_plan' || obj.object_type === 'mp') && (obj.entity_id || obj.mid);
      }) || [];
      
      if (mealPlanObjects.length === 0) {
        console.log('No meal plan day boxes found');
        return;
      }
      
      console.log(`📅 Found ${mealPlanObjects.length} meal plan objects on whiteboard`);
      
      // Group by meal_plan_id to fetch unique meal plans
      const uniqueMealPlanIds = [...new Set(mealPlanObjects.map(obj => obj.entity_id || obj.mid))];
      
      // HOUSEHOLD-AWARE: Fetch meal plan data using whiteboard context
      const mealPlanDataMap = {};
      for (const planId of uniqueMealPlanIds) {
        try {
          // Use household-aware endpoint to allow viewing meal plans from other members
          const response = await whiteboardAPI.getWhiteboardMealPlan(whiteboardId, planId);
          console.log(`📅 Fetched meal plan ${planId}:`, response);
          if (response.success) {
            // V2 household-aware API returns {success: true, data: {...}}
            const mealPlan = response.data;
            mealPlanDataMap[planId] = mealPlan;
            console.log(`✅ Loaded meal plan ${planId} (author: ${mealPlan.author_name || 'unknown'})`);
          }
        } catch (err) {
          console.warn(`⚠️ Failed to load meal plan ${planId} in household context:`, err.message);
        }
      }
      
      // Get all recipe IDs from meal plans to know which recipes belong to plans
      const mealPlanRecipeMap = {}; // recipe_id -> mealPlanDbId
      for (const obj of mealPlanObjects) {
        const planId = obj.entity_id || obj.mid;
        const mealPlan = mealPlanDataMap[planId];
        
        if (!mealPlan) continue;
        
        // Parse meal_data to get recipe IDs
        const mealData = typeof mealPlan.meal_data === 'string' 
          ? JSON.parse(mealPlan.meal_data)
          : (mealPlan.meal_data || {});
        
        const days = mealData.days || {};
        Object.values(days).forEach(day => {
          (day.recipes || []).forEach(recipe => {
            mealPlanRecipeMap[recipe.id] = planId;
          });
        });
      }
      
      console.log('🗺️ Meal plan recipe map:', mealPlanRecipeMap);
      
      // Create meal plan container nodes (parent nodes without children!)
      const mealPlanNodes = [];
      
      for (const obj of mealPlanObjects) {
        const planId = obj.entity_id || obj.mid;
        const mealPlan = mealPlanDataMap[planId];
        
        if (!mealPlan) {
          console.warn(`Meal plan ${obj.entity_id} not found`);
          continue;
        }
        
        // Parse meal_data to get day info
        const mealData = typeof mealPlan.meal_data === 'string' 
          ? JSON.parse(mealPlan.meal_data)
          : (mealPlan.meal_data || {});
        
        console.log('🔍 Parsed meal_data:', mealData);
        
        const days = mealData.days || {};
        const dayEntries = Object.entries(days);
        const [dayId, dayData] = dayEntries[0] || ['day1', { name: 'Day 1', recipes: [] }];
        const dayName = dayData.name || mealPlan.plan_name || 'Day 1';
        const recipes = dayData.recipes || [];
        
        console.log('🍽️ Day data:', { dayId, dayName, recipeCount: recipes.length, recipes });
        
        // Create meal plan container node (independent, no children!)
        const containerNodeId = `meal-plan-${planId}`;
        const containerNode = {
          id: containerNodeId,
          type: 'mealPlanContainer',
          position: {
            x: obj.position?.x || 400,
            y: obj.position?.y || 100
          },
          draggable: true,
          width: obj.position?.width || 600,
          height: obj.position?.height || 800,
          data: {
            name: dayName,
            mealPlanDbId: planId,
            objectId: obj.id,
            recipeCount: recipes.length,
            backgroundColor: obj.background_color || '#D1FAE5',
            commentCount: getCommentCount('meal_plan', planId),
            hasNewComments: false,
            onNameChange: handleMealPlanNodeNameChange,
            onColorChange: handleMealPlanNodeColorChange,
            onDelete: handleMealPlanNodeDelete,
            onGenerateGroceryList: handleGenerateGroceryListFromMealPlanNode
          },
          style: {
            width: obj.position?.width || 600,
            height: obj.position?.height || 800
          }
        };
        
        mealPlanNodes.push(containerNode);
      }
      
      // Add meal plan nodes to React Flow (no child nodes created here!)
      setNodes(prevNodes => {
        const existingIds = new Set(prevNodes.map(n => n.id));
        const newNodes = mealPlanNodes.filter(n => !existingIds.has(n.id));
        return [...prevNodes, ...newNodes];
      });
      
      console.log('✅ Created meal plan container nodes:', mealPlanNodes.length);
      
      // Now update existing recipe nodes to link them to meal plans
      // Recipe nodes are already loaded by loadSavedObjects with full data!
      setNodes(prevNodes => prevNodes.map(node => {
        if (node.type === 'recipeCard' && node.data.recipe_id) {
          const mealPlanId = mealPlanRecipeMap[node.data.recipe_id];
          if (mealPlanId) {
            console.log(`🔗 Linking recipe ${node.data.recipe_id} to meal plan ${mealPlanId}`);
            return {
              ...node,
              data: {
                ...node.data,
                mealPlanId: mealPlanId
              },
              // Set higher z-index so recipes appear ON TOP of container
              zIndex: 10,
              style: {
                ...node.style,
                zIndex: 10
              }
            };
          }
        }
        return node;
      }));
      
      console.log('✅ Linked existing recipe nodes to meal plans');
      
      // FINAL DEBUG: Check what nodes we have after all loading
      setNodes(prevNodes => {
        console.log('🎯 FINAL NODES STATE:');
        console.log(`   Total nodes: ${prevNodes.length}`);
        console.log(`   Recipe cards: ${prevNodes.filter(n => n.type === 'recipeCard').length}`);
        console.log(`   Meal plans: ${prevNodes.filter(n => n.type === 'mealPlanContainer').length}`);
        console.log(`   Grocery lists: ${prevNodes.filter(n => n.type === 'groceryListNode').length}`);
        console.log(`   Notes: ${prevNodes.filter(n => n.type === 'note').length}`);
        console.log('   Recipe card details:', prevNodes.filter(n => n.type === 'recipeCard').map(n => ({
          id: n.id,
          hasRecipe: !!n.data?.recipe,
          position: n.position,
          visible: n.hidden !== true
        })));
        return prevNodes; // Return unchanged
      });
      
    } catch (error) {
      console.error('❌ Error loading meal plan day boxes:', error);
    }
  };

  // ====================================
  // SELECTION HANDLERS (Canva-style)
  // ====================================

  const handleSelectAll = useCallback(() => {
    setNodes(nodes.map(node => ({ ...node, selected: true })));
    toast.info(`Selected ${nodes.length} cards`);
  }, [nodes, toast]);

  const handleClearSelection = useCallback(() => {
    setNodes(nodes.map(node => ({ ...node, selected: false })));
  }, []);

  const handleToggleSelection = useCallback((nodeId) => {
    setNodes(nodes.map(node =>
      node.id === nodeId
        ? { ...node, selected: !node.selected }
        : node
    ));
  }, [nodes]);

  // ====================================
  // GROCERY LIST WIDGET HANDLERS
  // ====================================

  const handleGenerateGroceryList = async () => {
    // Get selected recipe cards
    const selected = nodes.filter(node => node.selected);
    
    if (selected.length === 0) {
      toast.warning('Select recipe cards first!');
      return;
    }

    try {
      toast.info('Generating shopping list...', 2000);

      // Use utility to generate grocery list from recipes
      const groceryData = await generateGroceryListFromRecipes(selected);

      // Create grocery list node with handlers
      const handlers = {
        onNameChange: handleGroceryListNameChange,
        onColorChange: handleGroceryListColorChange,
        onItemChecked: handleGroceryListItemChecked,
        onItemAdded: handleGroceryListItemAdded,
        onItemRemoved: handleGroceryListItemRemoved,
        onItemsReordered: handleGroceryListItemsReordered,
        onDelete: handleGroceryListDelete
      };

      const newNode = createGroceryListNode(groceryData, handlers);

      // Add to canvas
      setNodes(prevNodes => [...prevNodes, newNode]);
      
      // Auto-save
      setTimeout(() => handleSave(), 500);
      
      toast.success(`Created shopping list with ${groceryData.items.length} items!`);
    } catch (error) {
      console.error('❌ Error generating grocery list:', error);
      toast.error(error.message || 'Failed to generate grocery list');
    }
  };

  const handleMealPlanNameChange = async (widgetId, newName) => {
    // Update local state immediately (optimistic update)
    setMealPlanWidgets(mealPlanWidgets.map(w =>
      w.id === widgetId ? { ...w, name: newName } : w
    ));
    
    // Find the widget to get its mealPlanDbId
    const widget = mealPlanWidgets.find(w => w.id === widgetId);
    if (!widget || !widget.mealPlanDbId) {
      console.warn('⚠️ Cannot save name: widget or mealPlanDbId not found');
      return;
    }
    
    try {
      // Fetch current plan data to update it properly
      const currentPlan = await whiteboardAPI.getMealPlan(widget.mealPlanDbId);
      
      if (currentPlan.success) {
        // V1 API uses meal_data, not plan_data!
        const mealData = typeof currentPlan.meal_plan.meal_data === 'string'
          ? JSON.parse(currentPlan.meal_plan.meal_data)
          : currentPlan.meal_plan.meal_data || {};
        
        // Update the day name in meal_data
        mealData.days = mealData.days || {};
        mealData.days[widget.dayId] = mealData.days[widget.dayId] || {};
        mealData.days[widget.dayId].name = newName;
        
        console.log(`🔍 Updating meal plan ${widget.mealPlanDbId} with meal_data:`, JSON.stringify(mealData, null, 2));
        
        // Save to database with meal_data (V1 API field name)
        const response = await apiCall(`/api/meal-plans/${widget.mealPlanDbId}`, {
          method: 'PUT',
          body: JSON.stringify({
            meal_data: mealData  // ← V1 API uses meal_data!
          })
        });
        
        if (response.success) {
          console.log(`✅ Meal plan name saved: "${newName}"`);
        } else {
          console.error('❌ Failed to save meal plan name:', response);
          toast.error('Failed to save name');
        }
      }
    } catch (error) {
      console.error('❌ Error saving meal plan name:', error);
      toast.error('Failed to save name');
    }
  };

  const handleGenerateGroceryListFromMealPlan = async (recipes, dayName) => {
    try {
      console.log(`🛒 Generating grocery list from "${dayName}"`);
      
      // Use utility to generate grocery list
      const groceryData = await generateGroceryListFromRecipeArray(recipes, `${dayName} Shopping List`);

      // Save to backend first
      const groceryListData = {
        name: `${dayName} Shopping List`,
        items: groceryData.items,
        household_id: householdId,
        widget_position: { x: 1000, y: 400, width: 350, height: 500 },
        linked_recipe_ids: groceryData.linkedRecipeIds
      };
      
      const createResponse = await whiteboardAPI.createWhiteboardGroceryList(whiteboardId, groceryListData);
      
      if (!createResponse.success) {
        throw new Error('Failed to create grocery list');
      }
      
      const dbId = createResponse.data.id;
      console.log('✅ Grocery list created with ID:', dbId);
      
      // Create node with handlers
      const handlers = {
        onNameChange: handleGroceryListNameChange,
        onColorChange: handleGroceryListColorChange,
        onItemChecked: handleGroceryListItemChecked,
        onItemAdded: handleGroceryListItemAdded,
        onItemRemoved: handleGroceryListItemRemoved,
        onItemsReordered: handleGroceryListItemsReordered,
        onDelete: handleGroceryListDelete
      };

      const newNode = createGroceryListNode(groceryData, handlers, { x: 1000, y: 400 });
      newNode.id = `grocery-list-${dbId}`;
      newNode.data.name = `${dayName} Shopping List`;
      newNode.data.dbId = dbId;

      setNodes(prevNodes => [...prevNodes, newNode]);
      toast.success(`Created list with ${groceryData.items.length} items!`);
      
    } catch (error) {
      console.error('Error generating grocery list:', error);
      toast.error('Failed to generate list: ' + error.message);
    }
  };

  // Note creation
  const handleCreateNote = useCallback(async () => {
    try {
      console.log('📝 Creating new note block...');
      
      // Calculate position with offset
      const existingNotes = nodes.filter(n => n.type === 'note');
      const offset = existingNotes.length * 50;
      const position = { x: 100 + offset, y: 100 + offset };
      
      // Create note in backend
      const noteData = {
        type: 'note',  // Database constraint requires 'note' not 'nt'
        position: [position.x, position.y, 300, 250, 0],
        content: {
          type: 'note',
          name: 'Note',
          html: '<p></p>',
          backgroundColor: '#fef3c7',
          fontSize: '18px'
        }
      };
      
      const response = await apiCall(`/api/v2/whiteboard/${whiteboardId}/o`, {
        method: 'POST',
        body: JSON.stringify(noteData)
      });
      
      if (!response.success) {
        throw new Error(response.error || 'Failed to create note');
      }
      
      const objectId = response.data.id;
      console.log('✅ Note created with ID:', objectId);
      
      // Create React Flow node with save handler
      const newNoteNode = {
        id: `note-${objectId}`,
        type: 'note',
        position,
        data: {
          name: 'Note',
          content: noteData.content.html,
          backgroundColor: noteData.content.backgroundColor,
          fontSize: noteData.content.fontSize,
          objectId,
          commentCount: 0,
          createdBy: user?.name || user?.email || 'Unknown',
          onSave: (noteContent) => {
            // Optimistic update
            setNodes(prevNodes => prevNodes.map(n =>
              n.id === `note-${objectId}` 
                ? { ...n, data: { ...n.data, ...noteContent } }
                : n
            ));
            // Debounced backend save
            debouncedNoteSave(whiteboardId, objectId, noteContent);
          }
        },
        style: { width: 300, height: 250 }
      };
      
      setNodes(prevNodes => [...prevNodes, newNoteNode]);
      toast.success('Note created! Start typing...');
      
    } catch (error) {
      console.error('❌ Error creating note:', error);
      toast.error('Failed to create note: ' + error.message);
    }
  }, [nodes, whiteboardId, user, debouncedNoteSave, toast]);
  const handleCreateActivityFeed = useCallback(() => {
    try {
      console.log('🔔 Creating activity feed widget...');
      
      // Calculate position with offset
      const existingFeeds = nodes.filter(n => n.type === 'activityFeed');
      const offset = existingFeeds.length * 50;
      const position = { x: 800 + offset, y: 100 + offset };
      
      // Use node creator utility
      const newNode = createActivityFeedNode(householdId, position);
      
      setNodesWithZIndex(prevNodes => [...prevNodes, newNode]);
      toast.success('📊 Activity feed added!');
      
    } catch (error) {
      console.error('❌ Error creating activity feed:', error);
      toast.error('Failed to create activity feed');
    }
  }, [nodes, householdId, setNodesWithZIndex, toast]);
  const handleCreateDayBox = async () => {
    try {
      const dayNumber = mealPlanWidgets.length + 1;
      const dayName = `Day ${dayNumber}`;
      
      // Create meal plan in database
      const mealData = {
        days: { [`day${dayNumber}`]: { name: dayName, recipes: [] } }
      };
      
      console.log('📅 Creating meal plan in database...');
      
      const response = await apiCall('/api/meal-plans', {
        method: 'POST',
        body: JSON.stringify({
          plan_name: dayName,
          week_start_date: new Date().toISOString().split('T')[0],
          meal_data: mealData,
          user_id: householdId
        })
      });
      
      if (!response.success || !response.plan_id) {
        throw new Error('Failed to create meal plan');
      }
      
      console.log(`✅ Meal plan created with ID: ${response.plan_id}`);
      
      // Create whiteboard object
      const position = { 
        x: 400 + (mealPlanWidgets.length * 60), 
        y: 100 + (mealPlanWidgets.length * 60),
        width: 600,
        height: 800,
        z_index: 0
      };
      
      const objectResponse = await whiteboardAPI.createObject(whiteboard.id, {
        type: 'mp',
        entity_type: 'meal_plan',
        entity_id: response.plan_id,
        position
      });
      
      if (!objectResponse.success) {
        throw new Error('Failed to create whiteboard object');
      }
      
      console.log(`✅ Whiteboard object created with ID: ${objectResponse.data.id}`);
      
      // Create meal plan node
      const handlers = {
        onNameChange: handleMealPlanNodeNameChange,
        onColorChange: handleMealPlanNodeColorChange,
        onDelete: handleMealPlanNodeDelete,
        onGenerateGroceryList: handleGenerateGroceryListFromMealPlanNode
      };
      
      const mealPlanData = {
        id: response.plan_id,
        name: dayName,
        backgroundColor: '#D1FAE5'
      };
      
      const newNode = createMealPlanNode(mealPlanData, position, handlers);
      newNode.data.objectId = objectResponse.data.id;
      newNode.data.recipeCount = 0;
      newNode.data.commentCount = 0;
      newNode.data.hasNewComments = false;
      
      setNodes(prevNodes => [...prevNodes, newNode]);
      toast.success(`Created ${dayName} meal plan!`);
      
    } catch (error) {
      console.error('❌ Error creating day box:', error);
      toast.error('Failed to create meal plan: ' + error.message);
    }
  };
  // ====================================
  // TAG HANDLERS
  // ====================================

  const handleTagsChange = (nodeId, newTags) => {
    console.log('🏷️ Updating tags for node:', nodeId, newTags);
    
    // Update node data
    setNodes(prevNodes => prevNodes.map(node =>
      node.id === nodeId
        ? { ...node, data: { ...node.data, tags: newTags } }
        : node
    ));
    
    // Auto-save tags to backend
    setTimeout(() => {
      handleSave();
    }, 500);
  };

  const handleTagFilterClick = (tag) => {
    console.log('🔍 Filtering by tag:', tag);
    
    // Toggle tag selection
    setSelectedTags(prevTags => {
      if (prevTags.includes(tag)) {
        // Remove tag
        return prevTags.filter(t => t !== tag);
      } else {
        // Add tag
        return [...prevTags, tag];
      }
    });
    
    // Open sidebar if not open
    if (!isTagSidebarOpen) {
      setIsTagSidebarOpen(true);
    }
  };

  const handleTagToggle = (tag) => {
    setSelectedTags(prevTags => {
      if (prevTags.includes(tag)) {
        return prevTags.filter(t => t !== tag);
      } else {
        return [...prevTags, tag];
      }
    });
  };

  const handleClearAllTags = () => {
    setSelectedTags([]);
  };

  const handleToggleTagSidebar = () => {
    setIsTagSidebarOpen(!isTagSidebarOpen);
  };

  // Save handler
  const handleSave = async () => {
    if (!whiteboard && !whiteboardId) {
      console.error('❌ No whiteboard loaded');
      return;
    }

    const saveWhiteboardId = whiteboard?.id || whiteboardId;
    if (!saveWhiteboardId) {
      console.error('❌ No whiteboard ID available');
      return;
    }

    try {
      console.log('💾 Saving whiteboard...', 'ID:', saveWhiteboardId);
      
      // Use nodesRef.current to get the latest state
      const currentNodes = nodesRef.current;

      // Callback to update node with new dbId after creating grocery list
      const updateNodeWithDbId = (nodeId, dbId) => {
        setNodes(prevNodes => prevNodes.map(n =>
          n.id === nodeId ? { ...n, data: { ...n.data, dbId } } : n
        ));
      };

      // Use utility to save all nodes
      const results = await saveAllWhiteboardNodes(
        currentNodes,
        saveWhiteboardId,
        householdId,
        updateNodeWithDbId
      );

      // Show success message
      toast.success(
        `✅ Saved! ${results.recipes} recipes, ${results.groceryLists} grocery lists, ${results.mealPlans} meal plans, ${results.notes} notes`
      );

    } catch (error) {
      console.error('❌ Error saving whiteboard:', error);
      toast.error('Error saving: ' + error.message);
    }
  };
  const handleDeleteNote = useCallback(async (nodeId, objectId) => {
    console.log('🗑️ Deleting note from canvas:', { nodeId, objectId, whiteboardId });

    // Remove node from canvas immediately (optimistic update)
    setNodes(prevNodes => prevNodes.filter(node => node.id !== nodeId));
    toast.success('Note deleted');
    
    // If we have an object_id and whiteboardId, delete from database
    if (objectId && whiteboardId) {
      try {
        console.log(`🔥 Calling delete API for object ${objectId} on whiteboard ${whiteboardId}`);
        const response = await apiCall(`/api/v2/whiteboard/${whiteboardId}/o/${objectId}`, {
          method: 'DELETE'
        });
        
        if (response.success) {
          console.log('✅ Note removed from database!');
        } else {
          console.error('❌ Failed to delete from database:', response);
          toast.error('Failed to delete from database');
        }
      } catch (error) {
        console.error('❌ Error deleting from database:', error);
        toast.error('Error deleting: ' + error.message);
      }
    } else {
      console.log('ℹ️ Object not yet saved to database, only removed from canvas');
    }

    console.log('✅ Note removed from canvas!');
  }, [whiteboardId, toast]);

  // Handler functions for new React Flow nodes
  const handleMealPlanNodeNameChange = async (nodeId, newName) => {
    console.log('✏️ Meal plan name changed:', nodeId, newName);
    
    // Update node data
    setNodes(prevNodes => prevNodes.map(node =>
      node.id === nodeId
        ? { ...node, data: { ...node.data, name: newName } }
        : node
    ));
    
    // Save to database
    setTimeout(() => saveMealPlanToDatabase(nodeId), 300);
    toast.success(`Renamed to "${newName}"`);
  };

  const handleMealPlanNodeColorChange = (nodeId, newColor) => {
    console.log('🎨 Meal plan color changed:', nodeId, newColor);
    
    // Update node data
    setNodes(prevNodes => prevNodes.map(node =>
      node.id === nodeId
        ? { ...node, data: { ...node.data, backgroundColor: newColor } }
        : node
    ));
    
    // Save to database
    setTimeout(() => saveMealPlanToDatabase(nodeId), 300);
  };

  const handleMealPlanNodeDelete = async (nodeId) => {
    console.log('🗑️ Deleting meal plan:', nodeId);
    
    // Get node data before deleting
    let nodeToDelete = null;
    setNodes(prevNodes => {
      nodeToDelete = prevNodes.find(n => n.id === nodeId);
      return prevNodes;
    });
    
    if (!nodeToDelete) {
      console.warn('⚠️ Node to delete not found:', nodeId);
      return;
    }
    
    // Remove meal plan container and unlink associated recipes
    setNodes(prevNodes => prevNodes.map(node => {
      // Remove the container itself
      if (node.id === nodeId) return null;
      
      // Unlink recipes that belonged to this meal plan
      if (node.data.mealPlanId === nodeToDelete.data.mealPlanDbId) {
        return {
          ...node,
          data: {
            ...node.data,
            mealPlanId: null,
            mealPlanName: null
          }
        };
      }
      
      return node;
    }).filter(Boolean)); // Remove nulls
    
    // Delete from database
    if (nodeToDelete.data.mealPlanDbId) {
      try {
        const response = await whiteboardAPI.deleteMealPlan(nodeToDelete.data.mealPlanDbId);
        if (response.success) {
          console.log('✅ Meal plan deleted from database');
        }
      } catch (error) {
        console.error('❌ Error deleting meal plan:', error);
      }
    }
    
    // Delete whiteboard object
    if (nodeToDelete.data.objectId && whiteboardId) {
      try {
        await whiteboardAPI.deleteObject(whiteboardId, nodeToDelete.data.objectId);
        console.log('✅ Whiteboard object deleted');
      } catch (error) {
        console.error('❌ Error deleting whiteboard object:', error);
      }
    }
    
    toast.success('Meal plan deleted');
  };

  const handleGenerateGroceryListFromMealPlanNode = async (nodeId) => {
    try {
      console.log('📋 Generating grocery list from meal plan:', nodeId);
      
      // Get meal plan container
      const containerNode = nodes.find(n => n.id === nodeId);
      if (!containerNode || !containerNode.data.mealPlanDbId) {
        toast.error('Meal plan not found');
        return;
      }
      
      // Get recipe nodes
      const recipeNodes = nodes.filter(n => n.data.mealPlanId === containerNode.data.mealPlanDbId);
      
      if (recipeNodes.length === 0) {
        toast.error('No recipes in this meal plan');
        return;
      }
      
      // Convert to recipe array and use utility
      const recipes = recipeNodes.map(n => ({ id: n.data.recipe_id }));
      const groceryData = await generateGroceryListFromRecipeArray(recipes, `${containerNode.data.name} Shopping List`);

      // Create grocery list widget
      const newWidget = {
        id: `grocery-list-temp-${Date.now()}`,
        name: `${containerNode.data.name} Shopping List`,
        items: groceryData.items,
        linkedRecipeIds: groceryData.linkedRecipeIds,
        position: { x: containerNode.position.x + 650, y: containerNode.position.y },
        size: 'medium'
      };
      
      setGroceryListWidgets([...groceryListWidgets, newWidget]);
      toast.success(`Created grocery list from ${containerNode.data.name}!`);
      
    } catch (error) {
      console.error('Error generating grocery list:', error);
      toast.error('Failed to generate list: ' + error.message);
    }
  };

  // Save meal plan changes to database
  const saveMealPlanToDatabase = useCallback(async (containerNodeId) => {
    try {
      // Get current nodes from state
      let containerNode = null;
      let recipeNodes = [];
      
      setNodes(prevNodes => {
        containerNode = prevNodes.find(n => n.id === containerNodeId);
        // Filter recipes by mealPlanId
        recipeNodes = prevNodes.filter(n => n.data.mealPlanId === containerNode?.data.mealPlanDbId);
        return prevNodes; // Don't change anything, just read
      });
      
      // Wait a tick for state to settle
      await new Promise(resolve => setTimeout(resolve, 50));
      
      // Now get fresh references
      setNodes(prevNodes => {
        containerNode = prevNodes.find(n => n.id === containerNodeId);
        recipeNodes = prevNodes.filter(n => n.data.mealPlanId === containerNode?.data.mealPlanDbId);
        return prevNodes;
      });
      
      if (!containerNode || containerNode.type !== 'mealPlanContainer') {
        console.warn('⚠️ Container node not found:', containerNodeId);
        return;
      }

      const mealPlanDbId = containerNode.data.mealPlanDbId;
      if (!mealPlanDbId) {
        console.warn('⚠️ No mealPlanDbId found for node:', containerNodeId);
        return;
      }

      // Extract recipe IDs from nodes (they have full recipe data!)
      const recipes = recipeNodes.map(node => ({
        id: node.data.recipe_id
      }));

      console.log('💾 Saving meal plan to database:', {
        mealPlanDbId,
        containerNodeId,
        recipeCount: recipes.length,
        recipes
      });

      // Update meal plan via V1 API
      // The meal_data structure for V1 API
      const mealData = {
        days: {
          day1: {
            name: containerNode.data.name,
            recipes: recipes
          }
        }
      };

      const response = await whiteboardAPI.updateMealPlan(mealPlanDbId, {
        plan_name: containerNode.data.name,
        meal_data: mealData  // Send as object, not stringified!
      });

      if (response.success) {
        console.log('✅ Meal plan saved successfully');
      } else {
        console.error('❌ Failed to save meal plan:', response);
        toast.error('Failed to save meal plan');
      }

      // Also update whiteboard object position/size
      if (containerNode.data.objectId && whiteboardId) {
        await whiteboardAPI.updateObject(whiteboardId, containerNode.data.objectId, {
          position: {
            x: containerNode.position.x,
            y: containerNode.position.y,
            width: containerNode.style?.width || 600,
            height: containerNode.style?.height || 800
          }
        });
        console.log('✅ Whiteboard object updated');
      }

    } catch (error) {
      console.error('❌ Error saving meal plan:', error);
      toast.error('Error saving: ' + error.message);
    }
  }, [whiteboardId, toast]);

  // React Flow callbacks
  const onNodesChange = useCallback((changes) => {
    // Handle meal plan container dragging - move associated recipes
    const positionChanges = changes.filter(c => c.type === 'position' && c.dragging);
    
    if (positionChanges.length > 0) {
      setNodes(prevNodes => {
        let updatedNodes = [...prevNodes];
        
        // For each position change, check if it's a meal plan container
        for (const change of positionChanges) {
          const node = updatedNodes.find(n => n.id === change.id);
          
          if (node && node.type === 'mealPlanContainer' && change.position) {
            // Calculate delta from current position
            const delta = {
              x: change.position.x - node.position.x,
              y: change.position.y - node.position.y
            };
            
            // Move all associated recipes by the same delta
            if (delta.x !== 0 || delta.y !== 0) {
              updatedNodes = updatedNodes.map(n => {
                if (n.data.mealPlanId === node.data.mealPlanDbId) {
                  return {
                    ...n,
                    position: {
                      x: n.position.x + delta.x,
                      y: n.position.y + delta.y
                    }
                  };
                }
                return n;
              });
            }
          }
        }
        
        return updatedNodes;
      });
    }
    
    // Apply the changes normally and ALWAYS enforce z-index
    setNodes((nds) => {
      const updatedNodes = applyNodeChanges(changes, nds);
      
      // CRITICAL: ALWAYS preserve z-index for recipes in meal plans after ANY change
      // This ensures z-index persists through drag, resize, select, rename, etc.
      return updatedNodes.map(node => {
        if (node.type === 'recipeCard' && node.data.mealPlanId) {
          return {
            ...node,
            zIndex: 10,
            style: {
              ...node.style,
              zIndex: 10
            }
          };
        }
        return node;
      });
    });
  }, []);

  // Edge handlers removed - connection lines feature not needed

  // Handle drag end - Simple spatial grouping (no parent-child hierarchy!)
  const onNodeDragStop = useCallback((event, node) => {
    console.log('🎯 Node drag stopped:', node.id);
    
    // Handle meal plan container drag - move all associated recipes with it
    if (node.type === 'mealPlanContainer') {
      console.log('🏠 Meal plan container dragged:', node.id);
      
      // Find the previous position of this container
      const oldPosition = nodes.find(n => n.id === node.id)?.position;
      if (!oldPosition) return;
      
      // Calculate the delta (how much the parent moved)
      const delta = {
        x: node.position.x - oldPosition.x,
        y: node.position.y - oldPosition.y
      };
      
      console.log('📏 Container moved by:', delta);
      
      // Update all recipes that belong to this meal plan
      if (delta.x !== 0 || delta.y !== 0) {
        setNodes(prevNodes => prevNodes.map(n => {
          // If this recipe belongs to the moved container, move it by the same delta
          if (n.data.mealPlanId === node.data.mealPlanDbId) {
            console.log(`  ↔️ Moving recipe ${n.id} by delta`);
            return {
              ...n,
              position: {
                x: n.position.x + delta.x,
                y: n.position.y + delta.y
              }
            };
          }
          return n;
        }));
      }
      
      return; // Don't process recipe drag logic below
    }
    
    // Only handle recipe cards below this point
    if (node.type !== 'recipeCardNew' && node.type !== 'recipeCard') {
      return;
    }
    
    // Check if recipe card is being dragged over a meal plan container
    const mealPlanContainers = nodes.filter(n => n.type === 'mealPlanContainer');
    
    let targetContainer = null;
    let isInsideContainer = false;
    
    // Check each meal plan container to see if recipe is inside its bounds
    for (const container of mealPlanContainers) {
      const containerBounds = {
        left: container.position.x,
        right: container.position.x + (container.width || container.style?.width || 600),
        top: container.position.y,
        bottom: container.position.y + (container.height || container.style?.height || 800)
      };
      
      const recipeBounds = {
        x: node.position.x + 140, // Center of recipe card (280px / 2)
        y: node.position.y + 175  // Center of recipe card (350px / 2)
      };
      
      // Check if recipe center is inside container
      if (
        recipeBounds.x >= containerBounds.left &&
        recipeBounds.x <= containerBounds.right &&
        recipeBounds.y >= containerBounds.top &&
        recipeBounds.y <= containerBounds.bottom
      ) {
        targetContainer = container;
        isInsideContainer = true;
        console.log('✅ Recipe inside meal plan:', container.data.name);
        break;
      }
    }
    
    // Simple spatial grouping: just update mealPlanId
    const currentMealPlanId = node.data.mealPlanId;
    const targetMealPlanId = isInsideContainer ? targetContainer.data.mealPlanDbId : null;
    
    if (currentMealPlanId !== targetMealPlanId) {
      console.log('📝 Updating mealPlanId:', currentMealPlanId, '→', targetMealPlanId);
      
      setNodes(prevNodes => prevNodes.map(n => {
        if (n.id === node.id) {
          // Update which meal plan this recipe belongs to
          return {
            ...n,
            data: {
              ...n.data,
              mealPlanId: targetMealPlanId,
              mealPlanName: isInsideContainer ? targetContainer.data.name : null
            },
            // Set higher z-index so recipes appear ON TOP of container
            zIndex: targetMealPlanId ? 10 : 0,
            style: {
              ...n.style,
              zIndex: targetMealPlanId ? 10 : 0
            }
          };
        }
        return n;
      }));
      
      if (targetMealPlanId) {
        toast.success(`Added to "${targetContainer.data.name}"`);
        // Save meal plan after a short delay
        setTimeout(() => saveMealPlanToDatabase(targetContainer.id), 500);
      } else if (currentMealPlanId) {
        toast.success(`Removed from meal plan`);
        // Find the old container and save it
        const oldContainer = mealPlanContainers.find(c => c.data.mealPlanDbId === currentMealPlanId);
        if (oldContainer) {
          setTimeout(() => saveMealPlanToDatabase(oldContainer.id), 500);
        }
      }
    }
    
  }, [nodes, toast, saveMealPlanToDatabase]);

  if (loading) {
    return (
      <div className="whiteboard-app loading mint-theme">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading whiteboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="whiteboard-app error">
        <div className="error-container">
          <h2>Error</h2>
          <p>{error}</p>
          <button onClick={loadWhiteboard}>Try Again</button>
          <button onClick={onBack}>Back to Whiteboards</button>
        </div>
      </div>
    );
  }

  // Mobile view (simplified list)
  if (isMobile) {
    return (
      <div className="whiteboard-app mobile embedded">
        <div className="mobile-header">
          <button className="back-button" onClick={onBack}>
            ← Back
          </button>
          <h1>{whiteboard?.name || 'Whiteboard'}</h1>
          <button className="save-button" onClick={handleSave}>
            Save
          </button>
        </div>

        <div className="mobile-content">
          <div className="phase-badge">
            Phase 1 - Mobile View Coming Soon!
          </div>
          <p>Mobile whiteboard view will be available in Phase 2.</p>
          <p>For now, please use a desktop browser to access whiteboards.</p>
        </div>
      </div>
    );
  }

  // Filter nodes by selected tags (AND logic - must have ALL selected tags)
  const filteredNodes = selectedTags.length > 0
    ? nodesWithHandlers.filter(node => {
        const nodeTags = node.data?.tags || [];
        // Node must have ALL selected tags
        return selectedTags.every(tag => nodeTags.includes(tag));
      })
    : nodesWithHandlers; // Show all nodes if no tags selected (with handlers attached!)
  
  // Desktop view (React Flow canvas)
  return (
    <div className="whiteboard-app desktop embedded">
      {/* Toolbar */}
      <div className="whiteboard-toolbar embedded">
        <div className="toolbar-left">
          <button className="back-button" onClick={onBack}>
            ← Back
          </button>
          <h1>{whiteboard?.name || 'Whiteboard'}</h1>
          <span className="phase-badge">Phase 2</span>
          
          {/* Selection info */}
          {nodes.filter(n => n.selected).length > 0 && (
            <div className="selection-info">
              <span className="selection-count">
                {nodes.filter(n => n.selected).length} selected
              </span>
              <button className="selection-btn" onClick={handleClearSelection} title="Clear selection (Esc)">
                Clear
              </button>
            </div>
          )}
        </div>

        <div className="toolbar-right">
          {/* Removed: Add Recipe, Create Day Box, Add Note, Tags, Select All - now in LeftToolbar */}
          
          <button 
            className="toolbar-button grocery-list-btn" 
            onClick={handleGenerateGroceryList}
            title="Generate grocery list from selected recipes"
            disabled={nodes.filter(n => n.selected).length === 0}
          >
            Grocery List
            {nodes.filter(n => n.selected).length > 0 && (
              <span className="selection-badge">
                {nodes.filter(n => n.selected).length}
              </span>
            )}
          </button>
          
          {/* Connection lines button removed - feature not needed */}
          
          <button className="toolbar-button" title="Export (Phase 5)">
            <span className="btn-icon">↗</span> Export
          </button>
          <button className="toolbar-button" title="Share (Phase 3)">
            <span className="btn-icon">⊕</span> Share
          </button>
          <button className="toolbar-button primary" onClick={handleSave}>
            <span className="btn-icon">✓</span> Save
          </button>
        </div>
      </div>

      {/* Context-Sensitive Note Toolbar - DISABLED, using NoteBlock's internal toolbar instead */}
      {/* {noteToolbarVisible && selectedNote && (
        <div className="note-context-toolbar">
          <div className="note-toolbar-content">
            <span className="note-toolbar-label">📝 Note Editing:</span>
            
            <div className="note-toolbar-group">
              <label>Color:</label>
              <input
                type="color"
                value={selectedNote.data.backgroundColor || '#fef08a'}
                onChange={(e) => {
                  const newColor = e.target.value;
                  setNodes(prevNodes => prevNodes.map(n =>
                    n.id === selectedNote.id
                      ? { ...n, data: { ...n.data, backgroundColor: newColor } }
                      : n
                  ));
                }}
                className="note-color-input"
              />
              <span className="note-color-preview" style={{ backgroundColor: selectedNote.data.backgroundColor || '#fef08a' }}></span>
            </div>
            
            <div className="note-toolbar-group">
              <label>Size:</label>
              <select
                value={selectedNote.data.fontSize || '14px'}
                onChange={(e) => {
                  const newSize = e.target.value;
                  setNodes(prevNodes => prevNodes.map(n =>
                    n.id === selectedNote.id
                      ? { ...n, data: { ...n.data, fontSize: newSize } }
                      : n
                  ));
                }}
                className="note-font-select"
              >
                <option value="12px">Small</option>
                <option value="14px">Medium</option>
                <option value="16px">Large</option>
                <option value="18px">X-Large</option>
              </select>
            </div>
            
            <div className="note-toolbar-divider"></div>
            
            <span className="note-toolbar-hint">💡 Click inside note to type, drag edges to move</span>
          </div>
        </div>
      )} */}

      {/* Recipe Picker Panel */}
      <RecipePickerPanel
        isOpen={isPickerOpen}
        onClose={() => setIsPickerOpen(false)}
        onAddRecipe={addRecipeToCanvas}
      />

      {/* React Flow Canvas */}
      <div className="whiteboard-canvas">
        <ReactFlow
          nodes={filteredNodes}
          onNodesChange={onNodesChange}
          onNodeDragStop={onNodeDragStop}
          onNodeDoubleClick={(event, node) => {
            // Double-click to open comments
            setSelectedObjectForComments(node);
            setIsCommentsSidebarOpen(true);
          }}
          onMove={(event, viewport) => setCanvasViewport(viewport)} // Track viewport
          nodeTypes={nodeTypes}
          fitView
          className="react-flow-container"
          // Enable pan and zoom interactions
          panOnDrag={true}
          panOnScroll={false}
          zoomOnScroll={true}
          zoomOnPinch={true}
          zoomOnDoubleClick={true}
          minZoom={0.1}
          maxZoom={4}
          defaultViewport={{ x: 0, y: 0, zoom: 0.8 }} // Increased from 0.5 to 0.8 for better readability
          // Prevent dragging when interacting with content
          noDragClassName="noDrag"        // Elements with this class won't trigger drag
          // Enable Canva-style selection
          selectNodesOnDrag={false}      // Don't select while dragging
          elementsSelectable={true}       // Allow selection
          nodesDraggable={true}           // Allow dragging
          nodesResizable={true}           // Allow resizing nodes
          multiSelectionKeyCode="Control" // Ctrl/Cmd for multi-select (null makes it always multi-select)
          selectionKeyCode="Shift"        // Shift for box select (future)
          deleteKeyCode="Delete"          // Delete key to remove
          elevateNodesOnSelect={false}    // DON'T change z-index on select - keep recipes on top!
        >
          {/* Background grid */}
          <Background
            variant="dots"
            gap={20}
            size={1}
            color="#e5e7eb"
          />

          {/* Controls (zoom, fit view, etc.) */}
          <Controls
            showZoom={true}
            showFitView={true}
            showInteractive={true}
            position="bottom-right"
            style={{
              backgroundColor: 'white',
              border: '2px solid #e5e7eb',
              borderRadius: '8px',
              padding: '4px'
            }}
          />

          {/* Mini map - REMOVED for cleaner UI */}

          {/* Custom overlay panel for connection lines and widgets */}
          <Panel position="top-left" style={{ 
            width: '100%', 
            height: '100%', 
            pointerEvents: 'none',
            position: 'relative'
          }}>
            {/* Empty State - Show when no content */}
            {nodes.length === 0 && !loading && (
              <div className="empty-canvas-overlay">
                <h2>🍳 Your Whiteboard Awaits</h2>
                <p>Start organizing your recipes visually. Add recipes, create notes, or build meal plans!</p>
                <div className="empty-actions">
                  <button 
                    className="empty-action-btn primary"
                    onClick={() => setIsPickerOpen(true)}
                  >
                    <span>🍽️</span> Add Recipes
                  </button>
                  <button 
                    className="empty-action-btn"
                    onClick={handleCreateNote}
                  >
                    <span>📝</span> Create Note
                  </button>
                  <button 
                    className="empty-action-btn"
                    onClick={handleCreateDayBox}
                  >
                    <span>📅</span> Add Day Box
                  </button>
                </div>
              </div>
            )}

          </Panel>
        </ReactFlow>
        
        {/* Comments Sidebar */}
        <CommentsSidebar
          whiteboardId={whiteboardId}
          isOpen={isCommentsSidebarOpen}
          onClose={() => {
            setIsCommentsSidebarOpen(false);
            setSelectedObjectForComments(null);
            // Refetch comment counts when sidebar closes
            if (whiteboardId) {
              fetchCommentCounts(whiteboardId);
            }
          }}
          selectedObject={selectedObjectForComments}
        />
        
        {/* Tag Filter Sidebar */}
        <TagFilterSidebar
          nodes={nodes}
          selectedTags={selectedTags}
          onTagToggle={handleTagToggle}
          onClearAll={handleClearAllTags}
          isOpen={isTagSidebarOpen}
          onToggleSidebar={handleToggleTagSidebar}
        />
        
        {/* Left Toolbar - NEW! */}
        <LeftToolbar
          onAddRecipe={() => setIsPickerOpen(true)}
          onAddNote={handleCreateNote}
          onAddDayBox={handleCreateDayBox}
          onAddActivityFeed={handleCreateActivityFeed}
          onToggleShortcuts={() => setIsShortcutsModalOpen(true)}
          onToggleTags={handleToggleTagSidebar}
          isTagSidebarOpen={isTagSidebarOpen}
          selectedTags={selectedTags}
        />
        
        {/* Household Presence Indicator */}
        {householdId && <HouseholdPresence householdId={householdId} />}

        {/* Keyboard Shortcuts Modal */}
        <KeyboardShortcutsModal
          isOpen={isShortcutsModalOpen}
          onClose={() => setIsShortcutsModalOpen(false)}
        />

        {/* Recipe Detail Modal */}
        <RecipeDetailModal
          recipe={selectedRecipeForDetail}
          isOpen={isRecipeDetailOpen}
          onClose={() => {
            setIsRecipeDetailOpen(false);
            setSelectedRecipeForDetail(null);
          }}
        />
      </div>
    </div>
  );
};

// Wrap with ToastProvider, RecipeCacheProvider, and WhiteboardProvider
const WhiteboardAppWithProviders = (props) => {
  return (
    <ToastProvider>
      <RecipeCacheProvider>
        <WhiteboardProvider 
          whiteboardId={props.whiteboardId} 
          householdId={props.householdId}
        >
          <WhiteboardApp {...props} />
        </WhiteboardProvider>
      </RecipeCacheProvider>
    </ToastProvider>
  );
};

export default WhiteboardAppWithProviders;
