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
import { WhiteboardProvider } from '../contexts/WhiteboardContext';
import whiteboardAPI from '../services/whiteboardAPI';
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
  
  // Responsive detection
  const isMobile = useMediaQuery({ maxWidth: 768 });
  const isTablet = useMediaQuery({ minWidth: 769, maxWidth: 1024 });
  const isDesktop = useMediaQuery({ minWidth: 1025 });

  // Toast notifications
  const toast = useToast();

  // 🆕 AbortController for request cancellation
  const abortControllerRef = useRef(null);

  // Whiteboard state
  const [whiteboard, setWhiteboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // React Flow state
  const [nodes, setNodes] = useState([]);
  const nodesRef = useRef(nodes); // Keep track of latest nodes for save
  // Edges removed - connection lines feature not needed

  // Recipe Picker Panel state
  const [isPickerOpen, setIsPickerOpen] = useState(false);

  // Keyboard Shortcuts Modal state
  const [isShortcutsModalOpen, setIsShortcutsModalOpen] = useState(false);

  // Grocery List Widget state
  const [groceryListWidgets, setGroceryListWidgets] = useState([]);
  
  // Meal Plan Widget state  
  const [mealPlanWidgets, setMealPlanWidgets] = useState([]);
  
  const [selectedRecipes, setSelectedRecipes] = useState([]);
  // Connection lines removed - feature not needed
  
  // Track canvas viewport for zoom/pan - Increased default zoom from 0.5 to 0.8 for better readability
  const [canvasViewport, setCanvasViewport] = useState({ x: 0, y: 0, zoom: 0.8 });

  // Comments sidebar state
  const [isCommentsSidebarOpen, setIsCommentsSidebarOpen] = useState(false);
  const [selectedObjectForComments, setSelectedObjectForComments] = useState(null);
  
  // Note toolbar state (context-sensitive like Illustrator)
  const [selectedNote, setSelectedNote] = useState(null);
  const [noteToolbarVisible, setNoteToolbarVisible] = useState(false);
  
  // Comment counts state
  const [commentCounts, setCommentCounts] = useState({});
  
  // Tag filtering state
  const [selectedTags, setSelectedTags] = useState([]);
  const [isTagSidebarOpen, setIsTagSidebarOpen] = useState(false);
  
  // Recipe Detail Modal state
  const [selectedRecipeForDetail, setSelectedRecipeForDetail] = useState(null);
  const [isRecipeDetailOpen, setIsRecipeDetailOpen] = useState(false);
  
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
            handleDeleteRecipe(node.id, node.data.recipe_id, node.data.object_id);
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

  const loadWhiteboard = async () => {
    // 🆕 Cancel any previous in-flight request
    if (abortControllerRef.current) {
      console.log('🛑 Cancelling previous whiteboard load request');
      abortControllerRef.current.abort();
    }

    // 🆕 Create new AbortController for this request
    abortControllerRef.current = new AbortController();
    const signal = abortControllerRef.current.signal;

    try {
      setLoading(true);
      setError(null);

      // Handle 'default' whiteboard - get or create default whiteboard for household
      let actualWhiteboardId = whiteboardId;
      
      if (whiteboardId === 'default' && householdId) {
        console.log('🏠 Getting/creating default whiteboard for household:', householdId);
        
        // Fetch whiteboards for this household
        const whiteboardsResponse = await whiteboardAPI.getHouseholdWhiteboards(householdId);
        
        if (whiteboardsResponse.success && whiteboardsResponse.data?.length > 0) {
          // Use first whiteboard
          actualWhiteboardId = whiteboardsResponse.data[0].id;
          console.log('✅ Using existing whiteboard:', actualWhiteboardId);
        } else {
          // Create default whiteboard
          console.log('➕ Creating default whiteboard...');
          const createResponse = await whiteboardAPI.createWhiteboard({
            household_id: householdId,
            name: 'Main Planning Board',
            description: 'Your household meal planning and recipe board'
          });
          
          console.log('📥 Create response:', createResponse);
          
          if (createResponse.success) {
            // Backend returns data.whiteboard.id, not data.id
            actualWhiteboardId = createResponse.data?.whiteboard?.id || createResponse.data?.id;
            console.log('✅ Created whiteboard:', actualWhiteboardId);
            
            if (!actualWhiteboardId) {
              console.error('❌ No whiteboard ID in response:', createResponse);
              throw new Error('Created whiteboard but no ID returned');
            }
            
            toast.success('Created your planning board!');
          } else {
            throw new Error('Failed to create whiteboard');
          }
        }
      }

      console.log('📥 Fetching whiteboard:', actualWhiteboardId);
      const response = await whiteboardAPI.getWhiteboard(actualWhiteboardId);
      console.log('📥 Get whiteboard response:', response);

      if (response.success) {
        const whiteboardData = response.data.whiteboard;
        setWhiteboard(whiteboardData);
        
        console.log('📋 Whiteboard loaded:', whiteboardData.name);
        console.log('📦 Saved objects:', whiteboardData.objects?.length || 0);
        
        // Check if whiteboard has saved objects
        if (whiteboardData.objects && whiteboardData.objects.length > 0) {
          // Restore saved layout
          await loadSavedObjects(whiteboardData.objects);
        } else {
          // No saved objects - load newest recipes as starting point
          console.log('⚡ No saved objects, loading newest recipes...');
          await loadUserRecipes();
        }
        
        // Load saved grocery lists for this whiteboard
        await loadSavedGroceryLists(actualWhiteboardId);
        
        // Load saved meal plan day boxes from whiteboard data
        await loadSavedMealPlanDays(whiteboardData);
        
        // Fetch comment counts
        await fetchCommentCounts(actualWhiteboardId);
      } else {
        setError(response.message || 'Failed to load whiteboard');
      }
    } catch (err) {
      // 🆕 Don't show error if request was cancelled
      if (err.name === 'AbortError' || signal.aborted) {
        console.log('✋ Whiteboard load cancelled (newer request started)');
        return; // Exit silently
      }
      
      console.error('Error loading whiteboard:', err);
      setError('Failed to load whiteboard');
      toast.error('Failed to load whiteboard: ' + err.message);
    } finally {
      // 🆕 Only set loading false if this request wasn't cancelled
      if (!signal.aborted) {
        setLoading(false);
      }
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
      console.log('📦 Whiteboard objects:', whiteboardData.objects);
      
      // Filter whiteboard objects that have meal_plan references
      const mealPlanObjects = whiteboardData.objects?.filter(obj => {
        console.log('🔍 Checking object:', obj.object_type, obj.entity_type, obj.entity_id, obj.mid);
        return (obj.entity_type === 'meal_plan' || obj.object_type === 'mp') && (obj.entity_id || obj.mid);
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

  const loadSavedObjects = async (savedObjects) => {
    try {
      console.log('🔄 Loading saved objects from database...');
      console.log('📦 All objects:', savedObjects);
      
      // Filter for notes specifically
      const noteObjects = savedObjects.filter(obj => obj.type === 'nt' || obj.object_type === 'note');
      console.log('📝 Found note objects:', noteObjects);
      
      // HOUSEHOLD-AWARE: Fetch recipes individually using whiteboard context
      // This allows viewing recipes created by other household members
      const recipeMap = {};
      
      // Get unique recipe IDs from saved objects
      const recipeIds = [...new Set(
        savedObjects
          .filter(obj => obj.entity_type === 'recipe' && obj.entity_id)
          .map(obj => obj.entity_id)
      )];
      
      console.log(`🏠 Fetching ${recipeIds.length} recipes in household context (BATCH MODE)...`);
      
      // 🆕 BATCH FETCH: Get all recipes in ONE request instead of N requests!
      if (recipeIds.length > 0) {
        try {
          const result = await apiCall('/api/v2/recipes/batch', {
            method: 'POST',
            body: JSON.stringify({
              recipe_ids: recipeIds,
              user_id: user?.id
            })
          });
          
          if (result.success && result.data?.recipes) {
            // 🆕 ADD RECIPES TO CACHE (single source of truth!)
            const normalizedRecipes = result.data.recipes.map(normalizeRecipe);
            addRecipes(normalizedRecipes);
            
            // Store in map for node creation
            normalizedRecipes.forEach(recipe => {
              recipeMap[recipe.id] = recipe;
            });
            
            console.log(`✅ Batch loaded ${result.data.found_count}/${result.data.requested_count} recipes`);
            console.log(`   Authors: ${[...new Set(result.data.recipes.map(r => r.created_by_name || 'unknown'))].join(', ')}`);
            console.log(`📦 Recipe cache now contains ${getCacheStats().size} recipes`);
          } else {
            console.warn('⚠️ Batch recipe fetch returned no data');
          }
        } catch (error) {
          console.error('❌ Batch recipe fetch failed:', error);
          // Fallback to individual fetches if batch fails
          console.log('🔄 Falling back to individual recipe fetches...');
          for (const recipeId of recipeIds) {
            try {
              const result = await whiteboardAPI.getWhiteboardRecipe(whiteboardId, recipeId);
              if (result.success && result.data) {
                const recipeData = {
                  ...result.data,
                  id: result.data.id,
                  recipe: result.data
                };
                recipeMap[recipeId] = recipeData;
              }
            } catch (err) {
              console.warn(`⚠️ Failed to load recipe ${recipeId}:`, err.message);
            }
          }
        }
      }
      
      console.log(`📚 Loaded ${Object.keys(recipeMap).length} recipes from household members`);
      
      // Load ALL recipe objects (don't skip any!)
      // Meal plan relationships will be set later in loadSavedMealPlanDays
      console.log('📦 Loading all recipe objects from whiteboard...');
      
      // Convert saved objects to React Flow nodes
      const restoredNodes = savedObjects
        .filter(obj => {
          // Recipe or note objects
          return (obj.entity_type === 'recipe' && obj.entity_id) || obj.type === 'nt' || obj.object_type === 'note';
        })
        .map(obj => {
          // Handle notes
          if (obj.type === 'nt' || obj.object_type === 'note') {
            console.log('📝 Loading note:', obj);
            const noteContent = obj.content || {};
            
            // Position might be array [x, y, w, h, z] or object {x, y, width, height}
            let posX = 100, posY = 100, posW = 300, posH = 250;
            
            if (Array.isArray(obj.position)) {
              posX = obj.position[0] || 100;
              posY = obj.position[1] || 100;
              posW = obj.position[2] || 300;
              posH = obj.position[3] || 250;
              console.log('📍 Position (array):', { posX, posY, posW, posH });
            } else if (obj.position && typeof obj.position === 'object') {
              posX = obj.position.x || 100;
              posY = obj.position.y || 100;
              posW = obj.position.width || 300;
              posH = obj.position.height || 250;
              console.log('📍 Position (object):', { posX, posY, posW, posH });
            }
            
            const noteNode = {
              id: `note-${obj.id}`,
              type: 'note',
              position: { x: posX, y: posY },
              data: {
                name: noteContent.name || 'Note',  // Extract name from content
                content: noteContent.html || '<p></p>',
                backgroundColor: noteContent.backgroundColor || '#FEF3C7',
                fontSize: noteContent.fontSize || '18px', // Increased default from 14px to 18px for readability
                objectId: obj.id,  // Store object ID for comments
                commentCount: getCommentCount('note', obj.id),  // Get comment count
                createdBy: obj.created_by_name || obj.created_by_email || 'Unknown', // Add creator name from backend
                onDelete: handleDeleteNote, // Add delete handler to data
                onSave: (noteData) => {
                  // 🆕 Optimistic update (immediate UI feedback)
                  setNodes(prevNodes => prevNodes.map(n =>
                    n.id === `note-${obj.id}`
                      ? {
                          ...n,
                          data: {
                            ...n.data,
                            name: noteData.name,
                            content: noteData.content,
                            backgroundColor: noteData.backgroundColor,
                            fontSize: noteData.fontSize
                          }
                        }
                      : n
                  ));

                  // 🆕 Debounced save to backend (2 seconds after last change)
                  debouncedNoteSave(whiteboardId, obj.id, noteData);
                }
              },
              style: {
                width: posW,
                height: posH
              }
            };
            
            console.log('✅ Created note node:', noteNode);
            return noteNode;
          }
          
          // Handle recipes
          const recipe = recipeMap[obj.entity_id];
          
          if (!recipe) {
            console.warn(`⚠️ Recipe ${obj.entity_id} not found, skipping`);
            return null;
          }
          
          // Handle position (array or object)
          let posX = 200, posY = 150;
          if (Array.isArray(obj.position)) {
            posX = obj.position[0] || 200;
            posY = obj.position[1] || 150;
          } else if (obj.position && typeof obj.position === 'object') {
            posX = obj.position.x || 200;
            posY = obj.position.y || 150;
          }
          
          // 🆕 USE FACTORY - Creates lean node with recipe_id only!
          return createRecipeNode({
            recipeId: recipe.id,
            objectId: obj.id,
            position: { x: posX, y: posY },
            tags: obj.tags || [],
            backgroundColor: obj.background_color || '#FFFFFF',
            commentCount: getCommentCount('recipe', recipe.id),
            hasNewComments: false,
            onClick: handleRecipeClick,
            onDelete: handleDeleteRecipe,
            onTagsChange: handleTagsChange,
            onTagFilterClick: handleTagFilterClick,
            onColorChange: handleRecipeColorChange
          });
        })
        .filter(node => node !== null); // Remove null nodes
      
      console.log(`✅ Restored ${restoredNodes.length} recipe cards from saved positions`);
      console.log('📊 Recipe nodes structure:', restoredNodes.filter(n => n.type === 'recipeCard').map(n => ({
        id: n.id,
        type: n.type,
        hasRecipe: !!n.data?.recipe,
        recipeName: n.data?.recipe?.title || n.data?.recipe?.name,
        position: n.position
      })));
      setNodes(restoredNodes);
      // Edges removed - connection lines not needed
      
    } catch (err) {
      console.error('❌ Error loading saved objects:', err);
      // Fallback to loading newest recipes
      await loadUserRecipes();
    }
  };

  const loadUserRecipes = async () => {
    try {
      // Fetch user's recipes from the API using our auth-aware apiCall
      const data = await apiCall('/api/user/recipes?category=all');
      
      // API returns data in data.data array
      const recipes = data.data || data.recipes || [];

      console.log('📚 Loaded recipes:', recipes.length);
      console.log('📋 FULL first recipe object:', recipes[0]);
      console.log('📋 First 3 recipes with data:', recipes.slice(0, 3).map(r => ({
        id: r.id,
        name: r.name,
        title: r.title,
        recipe_name: r.recipe_name,
        image_url: r.image_url,
        category: r.category,
        prep_time: r.prep_time_minutes,
        cook_time: r.cook_time_minutes
      })));

      if (recipes.length === 0) {
        console.log('⚠️ No recipes found, loading mock data');
        loadMockRecipes();
        return;
      }

      // Sort by created_at to get newest recipes first
      const sortedRecipes = [...recipes].sort((a, b) => {
        const dateA = new Date(a.created_at || 0);
        const dateB = new Date(b.created_at || 0);
        return dateB - dateA; // Newest first
      });

      console.log('🆕 5 newest recipes:', sortedRecipes.slice(0, 5).map(r => ({
        id: r.id,
        name: r.name,
        created_at: r.created_at,
        has_image: !!r.image_url
      })));

      // Convert first 5 NEWEST recipes to whiteboard nodes
      const recipeNodes = sortedRecipes.slice(0, 5).map((recipe, index) => {
        // Position them in a nice layout
        const col = index % 3;
        const row = Math.floor(index / 3);
        
        // Fix image URLs - if it starts with /api, prepend the API base URL
        let imageUrl = recipe.image_url;
        if (imageUrl && imageUrl.startsWith('/api')) {
          imageUrl = `${process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000'}${imageUrl}`;
        }
        
        return {
          id: `recipe-${recipe.id}`,
          type: 'recipeCard',
          position: { 
            x: 200 + (col * 400), 
            y: 150 + (row * 350) 
          },
          data: {
            recipe: {
              ...recipe,
              image_url: imageUrl
            },
            recipe_id: recipe.id,
            name: recipe.title || recipe.name || 'Untitled Recipe', // Use title field!
            image_url: imageUrl, // Use fixed URL
            prep_time: recipe.prep_time, // Already in minutes
            cook_time: recipe.cook_time, // Already in minutes
            total_time: recipe.total_time,
            category: recipe.category,
            tags: [], // Empty tags for new recipes
            onClick: handleRecipeClick,
            onDelete: handleDeleteRecipe,
            onTagsChange: handleTagsChange,
            onTagFilterClick: handleTagFilterClick
          }
        };
      });

      console.log('🎨 Created recipe nodes:', recipeNodes.length);
      setNodes(recipeNodes);
      // Edges removed - connection lines not needed

    } catch (err) {
      console.error('Error loading recipes:', err);
      // Fall back to mock data if recipes fail to load
      loadMockRecipes();
    }
  };

  const loadMockRecipes = () => {
    console.log('⚠️ Loading mock recipes as fallback');
    
    // Phase 1: Add some test RECIPE CARD nodes with realistic data
    const testNodes = [
          {
            id: 'recipe-1',
            type: 'recipeCard',
            position: { x: 200, y: 150 },
            data: {
              recipe: {
                id: 1,
                name: 'Classic Margherita Pizza',
                image_url: 'https://images.unsplash.com/photo-1604068549290-dea0e4a305ca?w=400',
                prep_time: 20,
                cook_time: 15,
                category: 'dinner'
              },
              recipe_id: 1,
              name: 'Classic Margherita Pizza',
              image_url: 'https://images.unsplash.com/photo-1604068549290-dea0e4a305ca?w=400',
              prep_time: 20,
              cook_time: 15,
              category: 'dinner',
              onClick: handleRecipeClick
            }
          },
          {
            id: 'recipe-2',
            type: 'recipeCard',
            position: { x: 600, y: 150 },
            data: {
              recipe: {
                id: 2,
                name: 'Chocolate Chip Cookies',
                image_url: 'https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=400',
                prep_time: 15,
                cook_time: 12,
                category: 'dessert'
              },
              recipe_id: 2,
              name: 'Chocolate Chip Cookies',
              image_url: 'https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=400',
              prep_time: 15,
              cook_time: 12,
              category: 'dessert',
              onClick: handleRecipeClick
            }
          },
          {
            id: 'recipe-3',
            type: 'recipeCard',
            position: { x: 1000, y: 150 },
            data: {
              recipe: {
                id: 3,
                name: 'Caesar Salad with Grilled Chicken',
                image_url: 'https://images.unsplash.com/photo-1546793665-c74683f339c1?w=400',
                prep_time: 10,
                cook_time: 20,
                category: 'salad'
              },
              recipe_id: 3,
              name: 'Caesar Salad with Grilled Chicken',
              image_url: 'https://images.unsplash.com/photo-1546793665-c74683f339c1?w=400',
              prep_time: 10,
              cook_time: 20,
              category: 'salad',
              onClick: handleRecipeClick
            }
          },
          {
            id: 'recipe-4',
            type: 'recipeCard',
            position: { x: 400, y: 500 },
            data: {
              recipe: {
                id: 4,
                name: 'Blueberry Pancakes',
                image_url: 'https://images.unsplash.com/photo-1567620832903-9fc6debc209f?w=400',
                prep_time: 10,
                cook_time: 15,
                category: 'breakfast'
              },
              recipe_id: 4,
              name: 'Blueberry Pancakes',
              image_url: 'https://images.unsplash.com/photo-1567620832903-9fc6debc209f?w=400',
              prep_time: 10,
              cook_time: 15,
              category: 'breakfast',
              onClick: handleRecipeClick
            }
          },
          {
            id: 'recipe-5',
            type: 'recipeCard',
            position: { x: 800, y: 500 },
            data: { 
              recipe_id: 5,
              name: 'Creamy Tomato Soup',
              image_url: 'https://images.unsplash.com/photo-1547592166-23ac45744acd?w=400',
              prep_time: 10,
              cook_time: 30,
              category: 'soup',
              onClick: handleRecipeClick
            }
          }
        ];
        
        setNodes(testNodes);
        // Edges removed - connection lines not needed
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

    console.log('🎯 Selected nodes full data:', selected.map(n => ({
      id: n.id,
      recipe_id: n.data?.recipe_id,
      title: n.data?.title,
      hasIngredients: !!n.data?.ingredients,
      data: n.data
    })));

    try {
      toast.info('Generating shopping list...', 2000);

      // Fetch full recipe details for each selected card
      const recipePromises = selected.map(async (node) => {
        try {
          const response = await apiCall(`/api/recipes/${node.data.recipe_id}`);
          console.log(`📋 Recipe ${node.data.recipe_id} API response:`, response);
          
          // Handle different response formats
          const recipe = response.success 
            ? (response.recipe || response.data) 
            : null;
          
          if (recipe) {
            console.log(`✅ Recipe "${recipe.title}" structure:`, {
              hasIngredients: !!recipe.ingredients,
              ingredientsType: typeof recipe.ingredients,
              ingredientsLength: Array.isArray(recipe.ingredients) ? recipe.ingredients.length : 'N/A',
              sample: Array.isArray(recipe.ingredients) ? recipe.ingredients.slice(0, 2) : recipe.ingredients
            });
          }
            
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

      if (recipes.length === 0) {
        toast.error('Failed to load recipe details');
        return;
      }

      console.log('📋 Fetched recipes for grocery list:', recipes);

      // Extract and merge ingredients
      const allIngredients = [];
      recipes.forEach(recipe => {
        let ingredients = recipe.ingredients || [];
        
        // Parse if it's a JSON string
        if (typeof ingredients === 'string') {
          try {
            // Try parsing as JSON array
            ingredients = JSON.parse(ingredients);
          } catch (e) {
            // Not JSON - split by newlines or semicolons (plain text format)
            console.log(`📝 Recipe "${recipe.title}" has plain text ingredients, splitting...`);
            ingredients = ingredients
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
        if (typeof ingredients === 'object' && !Array.isArray(ingredients)) {
          ingredients = Object.values(ingredients);
        }

        console.log(`🥕 Recipe "${recipe.title || recipe.name}" has ${ingredients?.length || 0} ingredients:`, ingredients);

        // Add each ingredient
        if (Array.isArray(ingredients) && ingredients.length > 0) {
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
          console.warn(`⚠️ Recipe "${recipe.title}" has no ingredients array`);
        }
      });

      console.log('🥕 All ingredients before merge:', allIngredients);

      // Check if we got any ingredients
      if (allIngredients.length === 0) {
        toast.warning('No ingredients found in selected recipes. Try adding recipes with ingredient lists!');
        return;
      }

      // Use the smart consolidation logic from groceryListUtils
      const mergedItems = consolidateIngredients(allIngredients);

      console.log('✅ Merged items:', mergedItems);

      // Create new grocery list React Flow node
      const newGroceryListNode = {
        id: `grocery-list-${Date.now()}`,
        type: 'groceryListNode',
        position: { x: 800, y: 100 }, // Position on canvas
        draggable: true,
        width: 350,
        height: 500,
        data: {
          name: `Shopping List (${selected.length} recipes)`,
          items: mergedItems,
          linkedRecipeIds: selected.map(node => node.data.recipe_id),
          dbId: null, // Will be set after saving
          backgroundColor: '#D1FAE5',
          commentCount: 0,
          hasNewComments: false,
          onNameChange: handleGroceryListNameChange,
          onColorChange: handleGroceryListColorChange,
          onItemChecked: handleGroceryListItemChecked,
          onItemAdded: handleGroceryListItemAdded,
          onItemRemoved: handleGroceryListItemRemoved,
          onItemsReordered: handleGroceryListItemsReordered,
          onDelete: handleGroceryListDelete
        },
        style: {
          width: 350,
          height: 500,
          zIndex: 5 // Slightly above recipe cards but below modal
        }
      };

      // Add to React Flow nodes
      setNodes(prevNodes => [...prevNodes, newGroceryListNode]);

      toast.success(`Created list with ${mergedItems.length} items from ${selected.length} recipes!`);

    } catch (error) {
      console.error('Error generating grocery list:', error);
      toast.error('Failed to generate list: ' + error.message);
    }
  };

  const handleGroceryListNameChange = (nodeId, newName) => {
    // Update node data
    setNodes(prevNodes => prevNodes.map(n =>
      n.id === nodeId ? { ...n, data: { ...n.data, name: newName } } : n
    ));
    
    // Auto-save after a short delay (debounce)
    setTimeout(() => {
      handleSave();
    }, 500);
    
    toast.success(`Renamed to "${newName}"`);
  };

  const handleGroceryListColorChange = (nodeId, newColor) => {
    setNodes(prevNodes => prevNodes.map(n =>
      n.id === nodeId ? { ...n, data: { ...n.data, backgroundColor: newColor } } : n
    ));
  };

  const handleGroceryListItemChecked = (nodeId, itemId, checked) => {
    setNodes(prevNodes => prevNodes.map(n => {
      if (n.id === nodeId) {
        const updatedItems = n.data.items.map(item =>
          item.id === itemId ? { ...item, checked } : item
        );
        return { ...n, data: { ...n.data, items: updatedItems } };
      }
      return n;
    }));
    
    // Auto-save after checking/unchecking
    setTimeout(() => handleSave(), 500);
  };

  const handleGroceryListItemAdded = (nodeId, newItem) => {
    setNodes(prevNodes => prevNodes.map(n => {
      if (n.id === nodeId) {
        // Add new item at the TOP of the list
        const updatedItems = [newItem, ...n.data.items];
        return { ...n, data: { ...n.data, items: updatedItems } };
      }
      return n;
    }));
    
    // FIXED: Auto-save after adding item
    setTimeout(() => handleSave(), 500);
  };

  const handleGroceryListItemRemoved = (nodeId, itemId) => {
    setNodes(prevNodes => prevNodes.map(n => {
      if (n.id === nodeId) {
        const updatedItems = n.data.items.filter(item => item.id !== itemId);
        return { ...n, data: { ...n.data, items: updatedItems } };
      }
      return n;
    }));
    
    // Auto-save after removal
    setTimeout(() => handleSave(), 500);
  };

  const handleGroceryListItemsReordered = (nodeId, reorderedItems) => {
    // Update node data with reordered items
    setNodes(prevNodes => prevNodes.map(n => {
      if (n.id === nodeId) {
        return { ...n, data: { ...n.data, items: reorderedItems } };
      }
      return n;
    }));
    
    // Auto-save after reordering
    setTimeout(() => {
      handleSave();
    }, 500);
  };

  const handleGroceryListDelete = async (nodeId) => {
    const node = nodes.find(n => n.id === nodeId);
    
    if (!node) {
      console.error('❌ Node not found:', nodeId);
      return;
    }

    const dbId = node.data.dbId;
    const listName = node.data.name;

    if (window.confirm(`Delete grocery list "${listName}"?`)) {
      // Remove from React Flow
      setNodes(prevNodes => prevNodes.filter(n => n.id !== nodeId));

      // Delete from database if it was saved
      if (dbId && whiteboardId) {
        try {
          await whiteboardAPI.deleteWhiteboardGroceryList(whiteboardId, dbId);
        } catch (error) {
          console.error('❌ Error deleting grocery list:', error);
        }
      }

      toast.success('Grocery list deleted');
    }
  };

  const handleCloseGroceryList = (widgetId) => {
    setGroceryListWidgets(groceryListWidgets.filter(w => w.id !== widgetId));
  };

  const handleGroceryListPositionChange = (widgetId, newPosition) => {
    setGroceryListWidgets(groceryListWidgets.map(w =>
      w.id === widgetId ? { ...w, position: newPosition } : w
    ));
  };

  const handleGroceryListSizeChange = (widgetId, newSize) => {
    setGroceryListWidgets(groceryListWidgets.map(w =>
      w.id === widgetId ? { ...w, size: newSize } : w
    ));
  };

  const handleGroceryListSaved = (widgetId, savedData) => {
    console.log('🎉 Grocery list saved, updating widget state:', savedData);
    setGroceryListWidgets(groceryListWidgets.map(w =>
      w.id === widgetId ? { ...w, dbId: savedData.dbId, ...savedData } : w
    ));
  };

  const handleItemChecked = (widgetId, itemId, checked) => {
    // TODO: Broadcast via WebSocket
    console.log(`Item ${itemId} checked: ${checked}`);
  };

  const handleItemAdded = (widgetId, item) => {
    // TODO: Broadcast via WebSocket
    console.log('Item added:', item);
  };

  const handleItemRemoved = (widgetId, itemId) => {
    // TODO: Broadcast via WebSocket
    console.log('Item removed:', itemId);
  };

  // ====================================
  // MEAL PLAN WIDGET HANDLERS
  // ====================================

  const handleCloseMealPlanDay = async (widgetId) => {
    // Find the widget to get its objectId
    const widget = mealPlanWidgets.find(w => w.id === widgetId);
    
    // Remove from state immediately for responsive UI
    setMealPlanWidgets(mealPlanWidgets.filter(w => w.id !== widgetId));
    
    // If widget has an objectId, delete it from the database
    if (widget && widget.objectId) {
      try {
        console.log(`🗑️ Deleting meal plan whiteboard object ${widget.objectId}`);
        await whiteboardAPI.deleteObject(whiteboardId, widget.objectId);
        console.log(`✅ Meal plan object ${widget.objectId} deleted from database`);
      } catch (error) {
        console.error('❌ Error deleting meal plan object:', error);
        toast.error('Failed to delete meal plan');
        // Re-add widget on error
        setMealPlanWidgets(prev => [...prev, widget]);
      }
    }
  };

  const handleMealPlanPositionChange = (widgetId, data) => {
    // data can be {position, dimensions} or just position (backwards compat)
    const newPosition = data.position || data;
    const newDimensions = data.dimensions;
    
    setMealPlanWidgets(mealPlanWidgets.map(w =>
      w.id === widgetId ? {
        ...w,
        position: newPosition,
        ...(newDimensions && { dimensions: newDimensions })
      } : w
    ));
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
      console.log(`🛒 Generating grocery list from "${dayName}" with ${recipes.length} recipes`);
      
      // Fetch full recipe data for selected recipes
      const recipeDataPromises = recipes.map(recipe =>
        apiCall(`/api/recipes/${recipe.id}`)
      );
      
      const responses = await Promise.all(recipeDataPromises);
      const fullRecipes = responses.map(r => r.recipe || r.data).filter(Boolean);
      
      // Consolidate ingredients
      const allIngredients = [];
      fullRecipes.forEach(recipe => {
        const ingredients = Array.isArray(recipe.ingredients)
          ? recipe.ingredients
          : (typeof recipe.ingredients === 'string' 
              ? recipe.ingredients.split('\n').filter(Boolean).map(text => ({ ingredient: text }))
              : []);
        
        ingredients.forEach((ing, idx) => {
          allIngredients.push({
            id: `${recipe.id}-${idx}`,
            ingredient: ing.ingredient || ing,
            quantity: ing.quantity || '',
            checked: false,
            source_recipe_id: recipe.id,
            source_recipe_name: recipe.title || recipe.name
          });
        });
      });
      
      const mergedItems = consolidateIngredients(allIngredients);
      
      // FIXED: Save to backend FIRST to get database ID
      const groceryListData = {
        name: `${dayName} Shopping List`,
        items: mergedItems,
        household_id: householdId,
        widget_position: {
          x: 1000,
          y: 400,
          width: 350,
          height: 500
        },
        linked_recipe_ids: recipes.map(r => r.id)
      };
      
      console.log('💾 Saving grocery list to backend...');
      const createResponse = await whiteboardAPI.createWhiteboardGroceryList(whiteboardId, groceryListData);
      
      if (!createResponse.success) {
        throw new Error('Failed to create grocery list in database');
      }
      
      const dbId = createResponse.data.id;
      console.log('✅ Grocery list created in backend with ID:', dbId);
      
      // Create new grocery list React Flow NODE with REAL database ID
      const newGroceryListNode = {
        id: `grocery-list-${dbId}`,  // Use real DB ID, not timestamp!
        type: 'groceryListNode',
        position: { x: 1000, y: 400 },
        draggable: true,
        width: 350,
        height: 500,
        data: {
          name: `${dayName} Shopping List`,
          items: mergedItems,
          linkedRecipeIds: recipes.map(r => r.id),
          dbId: dbId,  // Store the real database ID
          backgroundColor: '#D1FAE5',
          commentCount: 0,
          hasNewComments: false,
          onNameChange: handleGroceryListNameChange,
          onColorChange: handleGroceryListColorChange,
          onItemChecked: handleGroceryListItemChecked,
          onItemAdded: handleGroceryListItemAdded,
          onItemRemoved: handleGroceryListItemRemoved,
          onItemsReordered: handleGroceryListItemsReordered,
          onDelete: handleGroceryListDelete
        },
        style: {
          width: 350,
          height: 500,
          zIndex: 5
        }
      };
      
      // Add to React Flow nodes
      setNodes(prevNodes => [...prevNodes, newGroceryListNode]);
      
      toast.success(`Created list with ${mergedItems.length} items from ${dayName}!`);
      
    } catch (error) {
      console.error('Error generating grocery list from meal plan:', error);
      toast.error('Failed to generate list: ' + error.message);
    }
  };

  // ====================================
  // NOTE CREATION HANDLER
  // ====================================

  const handleCreateNote = useCallback(async () => {
    try {
      console.log('📝 Creating new note block...');
      
      // Generate unique temp ID
      const tempId = `note-${Date.now()}`;
      
      // Calculate center position or offset from last note
      const existingNotes = nodes.filter(n => n.type === 'note');
      const offsetX = existingNotes.length * 50;
      const offsetY = existingNotes.length * 50;
      
      const position = {
        x: 100 + offsetX,
        y: 100 + offsetY,
        width: 300,
        height: 250,
      };
      
      // Create note in backend first
      const noteData = {
        type: 'nt',  // Note type (compact schema: nt)
        object_type: 'note', // For backward compatibility
        position: [position.x, position.y, position.width, position.height, 0], // [x, y, w, h, z]
        content: {
          type: 'note',
          name: 'Note',  // Include default name in content
          html: '<p></p>', // Empty note
          backgroundColor: '#fef3c7', // Default yellow
          fontSize: '18px' // Increased from 14px to 18px for better readability
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
      console.log('✅ Note created in backend with ID:', objectId);
      
      // Create React Flow node
      const newNoteNode = {
        id: `note-${objectId}`,
        type: 'note',
        position: { x: position.x, y: position.y },
        data: {
          name: 'Note',
          content: noteData.content.html,
          backgroundColor: noteData.content.backgroundColor,
          fontSize: noteData.content.fontSize,
          objectId: objectId,  // Store object ID for comments
          commentCount: 0,  // Initial count
          createdBy: user?.name || user?.email || 'Unknown', // Add creator name
          onDelete: handleDeleteNote, // Add delete handler to data
          onSave: (noteContent) => {
            // 🆕 Optimistic update (immediate UI feedback)
            setNodes(prevNodes => prevNodes.map(n =>
              n.id === `note-${objectId}`
                ? {
                    ...n,
                    data: {
                      ...n.data,
                      name: noteContent.name,
                      content: noteContent.content,
                      backgroundColor: noteContent.backgroundColor,
                      fontSize: noteContent.fontSize
                    }
                  }
                : n
            ));

            // 🆕 Debounced save to backend (2 seconds after last change)
            debouncedNoteSave(whiteboardId, objectId, noteContent);
          }
        },
        style: {
          width: position.width,
          height: position.height
        }
      };
      
      setNodes(prevNodes => [...prevNodes, newNoteNode]);
      toast.success('Note created! Start typing...');
      
    } catch (error) {
      console.error('❌ Error creating note:', error);
      toast.error('Failed to create note: ' + error.message);
    }
  }, [nodes, whiteboardId, user, handleDeleteNote, debouncedNoteSave, toast]);

  // Create Activity Feed Widget (no backend storage needed - just reads from activity_feed table)
  const handleCreateActivityFeed = useCallback(() => {
    try {
      console.log('🔔 Creating new activity feed widget...');
      
      // Calculate position (offset if there are existing widgets)
      const existingActivityFeeds = nodes.filter(n => n.type === 'activityFeed');
      const offsetX = existingActivityFeeds.length * 50;
      const offsetY = existingActivityFeeds.length * 50;
      
      const position = {
        x: 800 + offsetX,
        y: 100 + offsetY,
        width: 400,
        height: 600,
      };
      
      // Create a unique ID for this widget
      const widgetId = `activityFeed-${Date.now()}`;
      
      // Create React Flow node (no backend storage - it's just a view of existing data)
      const newActivityNode = {
        id: widgetId,
        type: 'activityFeed',
        position: { x: position.x, y: position.y },
        style: {
          width: position.width,
          height: position.height,
        },
        data: {
          householdId: householdId,
        },
      };
      
      setNodesWithZIndex(prevNodes => [...prevNodes, newActivityNode]);
      
      toast.success('� Activity feed added!');
      
      // Save whiteboard state (stores position in local storage or whiteboard metadata)
      // setTimeout(() => saveWhiteboard(), 500); // Commented out - not needed for activity feed
      
    } catch (error) {
      console.error('❌ Error creating activity feed:', error);
      toast.error('Failed to create activity feed');
    }
  }, [nodes, householdId, setNodesWithZIndex, toast]);

  const handleCreateDayBox = async () => {
    try {
      const dayNumber = mealPlanWidgets.length + 1;
      const dayName = `Day ${dayNumber}`;
      
      // Create meal plan in database immediately
      const mealData = {
        days: {
          [`day${dayNumber}`]: {
            name: dayName,
            recipes: []
          }
        }
      };
      
      console.log('📅 Creating meal plan in database...', mealData);
      
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
      
      // Create whiteboard object linking to meal plan
      const position = { 
        x: 400 + (mealPlanWidgets.length * 60), 
        y: 100 + (mealPlanWidgets.length * 60),
        width: 600,  // Larger for new container
        height: 800, // Larger for new container
        z_index: 0
      };
      
      const objectResponse = await whiteboardAPI.createObject(whiteboard.id, {
        type: 'mp',
        entity_type: 'meal_plan',
        entity_id: response.plan_id,
        position: position
      });
      
      if (!objectResponse.success) {
        throw new Error('Failed to create whiteboard object');
      }
      
      console.log(`✅ Whiteboard object created with ID: ${objectResponse.data.id}`);
      
      // Create new React Flow container node (meal plan container)
      const newContainerNode = {
        id: `meal-plan-${response.plan_id}`,
        type: 'mealPlanContainer',
        position: {
          x: position.x,
          y: position.y
        },
        draggable: true, // Make container draggable
        // Set dimensions at top level for React Flow
        width: position.width,
        height: position.height,
        data: {
          name: dayName,
          mealPlanDbId: response.plan_id,
          objectId: objectResponse.data.id,
          recipeCount: 0,
          backgroundColor: '#D1FAE5',
          commentCount: 0,
          hasNewComments: false,
          onNameChange: handleMealPlanNodeNameChange,
          onColorChange: handleMealPlanNodeColorChange,
          onDelete: handleMealPlanNodeDelete,
          onGenerateGroceryList: handleGenerateGroceryListFromMealPlanNode
        },
        style: {
          width: position.width,
          height: position.height
        }
      };
      
      console.log('✅ Creating new React Flow meal plan node:', newContainerNode);
      
      // Add to React Flow nodes
      setNodes(prevNodes => [...prevNodes, newContainerNode]);
      
      // Remove old widget creation - using React Flow nodes now
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

  // ====================================
  // SAVE HANDLER
  // ====================================

  const handleSave = async () => {
    if (!whiteboard && !whiteboardId) {
      console.error('❌ No whiteboard loaded - whiteboard:', whiteboard, 'whiteboardId:', whiteboardId);
      return;
    }

    const saveWhiteboardId = whiteboard?.id || whiteboardId;
    if (!saveWhiteboardId) {
      console.error('❌ No whiteboard ID available');
      return;
    }

    try {
      console.log('💾 Saving whiteboard (recipes + grocery lists)...', 'ID:', saveWhiteboardId);
      
      // Use nodesRef.current to get the latest state
      const currentNodes = nodesRef.current;
      
      // 1. Save recipe card positions and tags (only if there are recipes)
      const objects = currentNodes
        .filter(node => node.type === 'recipeCard' && node.data.recipe_id)
        .map(node => ({
          recipe_id: node.data.recipe_id,
          tags: node.data.tags || [], // Include tags
          position: {
            x: node.position.x,
            y: node.position.y,
            width: 300,  // Fixed width for now
            height: 400, // Fixed height for now
            z: 0         // z-index
          }
        }));

      console.log(`📦 Saving ${objects.length} recipe cards:`, objects);

      // Only call bulk save API if there are recipes to save
      let recipeResponse = { success: true, data: { updated_count: 0, created_count: 0, total_processed: 0 } };
      
      if (objects.length > 0) {
        recipeResponse = await whiteboardAPI.bulkUpdateObjects(saveWhiteboardId, objects);

        if (!recipeResponse.success) {
          console.error('❌ Recipe save failed:', recipeResponse);
          toast.error('Failed to save recipes: ' + (recipeResponse.message || 'Unknown error'));
          return;
        }

        console.log('✅ Recipes saved:', recipeResponse.data);
      }
      
      // 2. Save all grocery list nodes
      const groceryListNodes = currentNodes.filter(n => n.type === 'groceryListNode');
      console.log(`🛒 Saving ${groceryListNodes.length} grocery lists...`);
      
      let savedListsCount = 0;
      let createdListsCount = 0;
      let updatedListsCount = 0;
      
      for (const node of groceryListNodes) {
        console.log(`🛒 Processing grocery list node:`, {
          id: node.id,
          dbId: node.data.dbId,
          name: node.data.name,
          itemCount: node.data.items?.length || 0,
          items: node.data.items
        });
        
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
        
        console.log(`💾 Saving grocery list data:`, saveData);
        
        try {
          let result;
          
          if (node.data.dbId) {
            // Update existing list
            console.log(`📝 Updating existing list ID ${node.data.dbId}...`);
            result = await whiteboardAPI.updateWhiteboardGroceryList(
              saveWhiteboardId,
              node.data.dbId,
              saveData
            );
            if (result.success) {
              console.log(`✅ Updated grocery list ${node.data.dbId}`);
              updatedListsCount++;
            } else {
              console.error(`❌ Failed to update grocery list ${node.data.dbId}:`, result);
            }
          } else {
            // Create new list
            console.log(`➕ Creating new grocery list...`);
            result = await whiteboardAPI.createWhiteboardGroceryList(
              saveWhiteboardId,
              saveData
            );
            if (result.success) {
              console.log(`✅ Created grocery list with ID ${result.data.id}`);
              createdListsCount++;
              // Update node with new dbId
              setNodes(prevNodes => prevNodes.map(n =>
                n.id === node.id ? { ...n, data: { ...n.data, dbId: result.data.id } } : n
              ));
            } else {
              console.error(`❌ Failed to create grocery list:`, result);
            }
          }
          
          if (result.success) {
            savedListsCount++;
          }
        } catch (err) {
          console.error('❌ Error saving grocery list:', node.data.name, err);
        }
      }
      
      console.log(`✅ Grocery lists saved: ${savedListsCount}/${groceryListNodes.length}`);

      // 3. Save all meal plan containers (React Flow nodes)
      const mealPlanNodes = currentNodes.filter(n => n.type === 'mealPlanContainer');
      console.log(`📅 Saving ${mealPlanNodes.length} meal plan containers...`);
      
      let savedMealPlansCount = 0;
      
      for (const node of mealPlanNodes) {
        try {
          // Update whiteboard object position/size
          if (node.data.objectId && whiteboardId) {
            await whiteboardAPI.updateObject(whiteboardId, node.data.objectId, {
              position: {
                x: node.position.x,
                y: node.position.y,
                width: node.width || node.style?.width || 600,
                height: node.height || node.style?.height || 800
              }
            });
            savedMealPlansCount++;
            console.log(`✅ Saved meal plan "${node.data.name}" position/size`);
          }
        } catch (error) {
          console.error(`❌ Error saving meal plan "${node.data.name}":`, error);
        }
      }
      
      console.log(`✅ Meal plans saved: ${savedMealPlansCount}/${mealPlanNodes.length}`);

      // 4. Save all note blocks
      const noteNodes = currentNodes.filter(n => n.type === 'note');
      console.log(`📝 Saving ${noteNodes.length} notes...`);
      
      let savedNotesCount = 0;
      
      for (const node of noteNodes) {
        try {
          // Extract object ID from node.id (format: "note-{objectId}")
          const objectId = parseInt(node.id.replace('note-', ''));
          
          if (objectId && whiteboardId) {
            // Update position and dimensions
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
            savedNotesCount++;
          }
        } catch (error) {
          console.error(`❌ Error saving note:`, error);
        }
      }
      
      console.log(`✅ Notes saved: ${savedNotesCount}/${noteNodes.length}`);

      // Show success message
      toast.success(
        `✅ Saved! ${recipeResponse.data.updated_count} recipes, ${savedListsCount} grocery lists, ${savedMealPlansCount} meal plans, ${savedNotesCount} notes`
      );

    } catch (error) {
      console.error('❌ Error saving whiteboard:', error);
      toast.error('Error saving: ' + error.message);
    }
  };

  const handleAddRecipe = useCallback((recipe) => {
    console.log('➕ Adding recipe to canvas:', recipe.title || recipe.name);

    // Check if recipe already exists on canvas
    const existingNode = nodes.find(node => node.data.recipe_id === recipe.id);
    if (existingNode) {
      alert('This recipe is already on the canvas!');
      return;
    }

    // Fix image URL
    let imageUrl = recipe.image_url;
    if (imageUrl && imageUrl.startsWith('/api')) {
      imageUrl = `${process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000'}${imageUrl}`;
    }

    // Create new node at center of viewport
    // Note: We'll need to get viewport center, for now use a reasonable default
    const newNode = {
      id: `recipe-${recipe.id}`,
      type: 'recipeCard',
      position: {
        x: 400 + (nodes.length * 50), // Stagger slightly
        y: 200 + (nodes.length * 50)
      },
      data: {
        recipe_id: recipe.id,
        name: recipe.title || recipe.name || 'Untitled Recipe',
        image_url: imageUrl,
        prep_time: recipe.prep_time,
        cook_time: recipe.cook_time,
        total_time: recipe.total_time,
        category: recipe.category,
        tags: [], // Empty tags for newly added recipes
        backgroundColor: '#FFFFFF',
        commentCount: 0,
        hasNewComments: false,
        onClick: handleRecipeClick,
        onDelete: handleDeleteRecipe,
        onTagsChange: handleTagsChange,
        onTagFilterClick: handleTagFilterClick,
        onColorChange: handleRecipeColorChange
      }
    };

    // Add to canvas
    setNodes(prevNodes => [...prevNodes, newNode]);

    // Auto-save after adding
    setTimeout(() => {
      handleSave();
    }, 100);

    console.log('✅ Recipe added to canvas!');
  }, [nodes, handleRecipeClick, handleDeleteRecipe, handleRecipeColorChange, handleSave]);

  // Handle recipe card click to show detail modal
  const handleRecipeClick = useCallback(async (recipeId) => {
    try {
      console.log('👁️ Opening recipe detail for:', recipeId);
      
      // Fetch full recipe data
      const response = await apiCall(`/api/recipes/${recipeId}`);
      const recipe = response.recipe || response.data;
      
      if (recipe) {
        setSelectedRecipeForDetail(recipe);
        setIsRecipeDetailOpen(true);
      } else {
        toast.error('Recipe not found');
      }
    } catch (error) {
      console.error('❌ Error loading recipe:', error);
      toast.error('Failed to load recipe');
    }
  }, [toast]);

  // Handle recipe color change
  const handleRecipeColorChange = useCallback(async (nodeId, color, objectId) => {
    console.log('🎨 Changing recipe color:', { nodeId, color, objectId });
    
    // Update node color immediately
    setNodes(prevNodes =>
      prevNodes.map(node =>
        node.id === nodeId
          ? { ...node, data: { ...node.data, backgroundColor: color } }
          : node
      )
    );
    
    // Save to database if object exists
    if (objectId && whiteboardId) {
      try {
        await whiteboardAPI.updateObject(whiteboardId, objectId, {
          background_color: color
        });
        console.log('✅ Recipe color saved to database');
      } catch (error) {
        console.error('❌ Error saving recipe color:', error);
      }
    }
  }, [whiteboardId]);

  const handleDeleteRecipe = useCallback(async (nodeId, recipeId, objectId) => {
    console.log('🗑️ Deleting recipe from canvas:', { nodeId, recipeId, objectId, whiteboardId, hasWhiteboard: !!whiteboard });

    // Remove node from canvas immediately (optimistic update)
    setNodes(prevNodes => prevNodes.filter(node => node.id !== nodeId));
    toast.success('Recipe removed from canvas');
    
    // If we have an object_id and whiteboardId, delete from database
    if (objectId && whiteboardId) {
      try {
        console.log(`🔥 Calling delete API for object ${objectId} on whiteboard ${whiteboardId}`);
        const response = await whiteboardAPI.deleteObject(whiteboardId, objectId);
        
        if (response.success) {
          console.log('✅ Recipe removed from database!');
        } else {
          console.error('❌ Failed to delete from database:', response);
          toast.error('Failed to delete from database');
        }
      } catch (error) {
        console.error('❌ Error deleting from database:', error);
        toast.error('Error deleting: ' + error.message);
      }
    } else {
      // New object not yet saved - no need to delete from database
      console.log('ℹ️ Object not yet saved to database (objectId:', objectId, 'whiteboardId:', whiteboardId, '), only removed from canvas');
    }

    console.log('✅ Recipe removed from canvas!');
  }, [whiteboardId, whiteboard, toast]);

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
    console.log('📋 Generating grocery list from meal plan:', nodeId);
    
    // Get the meal plan container node
    const containerNode = nodes.find(n => n.id === nodeId);
    if (!containerNode || !containerNode.data.mealPlanDbId) {
      toast.error('Meal plan not found');
      return;
    }
    
    // Get all recipe nodes that belong to this meal plan
    const recipeNodes = nodes.filter(n => n.data.mealPlanId === containerNode.data.mealPlanDbId);
    
    if (recipeNodes.length === 0) {
      toast.error('No recipes in this meal plan');
      return;
    }
    
    console.log('📝 Recipes for grocery list:', recipeNodes.map(n => n.data.name));
    
    // Fetch full recipe data and generate grocery list
    try {
      const recipeDataPromises = recipeNodes.map(node =>
        apiCall(`/api/recipes/${node.data.recipe_id}`)
      );
      
      const responses = await Promise.all(recipeDataPromises);
      const fullRecipes = responses.map(r => r.recipe || r.data).filter(Boolean);
      
      // Consolidate ingredients
      const allIngredients = [];
      fullRecipes.forEach(recipe => {
        const ingredients = Array.isArray(recipe.ingredients)
          ? recipe.ingredients
          : (typeof recipe.ingredients === 'string' 
              ? recipe.ingredients.split('\n').filter(Boolean).map(text => ({ ingredient: text }))
              : []);
        
        ingredients.forEach((ing, idx) => {
          allIngredients.push({
            id: `${recipe.id}-${idx}`,
            ingredient: ing.ingredient || ing,
            quantity: ing.quantity || '',
            checked: false,
            source_recipe_id: recipe.id,
            source_recipe_name: recipe.title || recipe.name
          });
        });
      });
      
      const mergedItems = consolidateIngredients(allIngredients);
      
      // Create new grocery list widget
      const newWidget = {
        id: `grocery-list-temp-${Date.now()}`,
        name: `${containerNode.data.name} Shopping List`,
        items: mergedItems,
        linkedRecipeIds: recipeNodes.map(n => n.data.recipe_id),
        linkedRecipes: fullRecipes,
        position: { x: containerNode.position.x + 650, y: containerNode.position.y },
        size: 'medium'
      };
      
      setGroceryListWidgets([...groceryListWidgets, newWidget]);
      toast.success(`Created grocery list from ${containerNode.data.name}!`);
      
    } catch (error) {
      console.error('Error generating grocery list from meal plan:', error);
      toast.error('Failed to generate list: ' + error.message);
    }
  };

  const handleRecipeCardClick = (nodeId, recipe) => {
    console.log('🍕 Recipe card clicked:', nodeId, recipe);
    // TODO: Open recipe detail modal
  };

  const handleTagClick = (tag) => {
    console.log('🏷️ Tag clicked:', tag);
    // TODO: Filter by tag
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
    ? nodes.filter(node => {
        const nodeTags = node.data?.tags || [];
        // Node must have ALL selected tags
        return selectedTags.every(tag => nodeTags.includes(tag));
      })
    : nodes; // Show all nodes if no tags selected
  
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
        onAddRecipe={handleAddRecipe}
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

            {/* Connection Lines Overlay removed - feature not needed */}

            {/* Meal Plan Day Box Widgets - OLD SYSTEM (Being replaced by React Flow nodes) */}
            {/* TODO: Remove after confirming new system works */}
            {/*
            <div style={{ pointerEvents: 'auto' }}>
              {mealPlanWidgets.map(widget => {
                return (
                  <MealPlanFloatingWidget
                    key={widget.id}
                    mealPlanDay={widget}
                    householdId={householdId}
                    whiteboardId={whiteboard?.id || whiteboardId}
                    linkedRecipes={widget.linkedRecipes}
                    initialPosition={widget.position}
                    viewport={canvasViewport}
                    onPositionChange={(pos) => handleMealPlanPositionChange(widget.id, pos)}
                    onClose={() => handleCloseMealPlanDay(widget.id)}
                    onNameChange={(newName) => handleMealPlanNameChange(widget.id, newName)}
                    onGenerateGroceryList={handleGenerateGroceryListFromMealPlan}
                  />
                );
              })}
            </div>
            */}
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
