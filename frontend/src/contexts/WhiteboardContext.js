import React, { createContext, useContext, useState, useCallback } from 'react';
import { validateNode, normalizeNode } from '../utils/nodeValidation';

/**
 * Whiteboard Context
 * 
 * Centralized state management for whiteboard (similar to AuthContext pattern)
 * 
 * BEFORE: All state scattered across WhiteboardApp component (3,161 lines)
 * AFTER: Shared state accessible via useWhiteboard() hook
 * 
 * Benefits:
 * - No prop drilling
 * - Centralized state updates
 * - Easy to test
 * - Clear separation of concerns
 */

const WhiteboardContext = createContext(null);

export function WhiteboardProvider({ children, whiteboardId, householdId }) {
  // ==========================================
  // CORE WHITEBOARD STATE
  // ==========================================
  const [whiteboard, setWhiteboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // ==========================================
  // REACT FLOW STATE
  // ==========================================
  const [nodes, setNodes] = useState([]);
  const [canvasViewport, setCanvasViewport] = useState({ x: 0, y: 0, zoom: 0.8 });
  
  // ==========================================
  // UI STATE
  // ==========================================
  const [isPickerOpen, setIsPickerOpen] = useState(false);
  const [isShortcutsModalOpen, setIsShortcutsModalOpen] = useState(false);
  const [isTagSidebarOpen, setIsTagSidebarOpen] = useState(false);
  const [isCommentsSidebarOpen, setIsCommentsSidebarOpen] = useState(false);
  const [isRecipeDetailOpen, setIsRecipeDetailOpen] = useState(false);
  
  // ==========================================
  // SELECTION STATE
  // ==========================================
  const [selectedRecipes, setSelectedRecipes] = useState([]);
  const [selectedTags, setSelectedTags] = useState([]);
  const [selectedNote, setSelectedNote] = useState(null);
  const [selectedObjectForComments, setSelectedObjectForComments] = useState(null);
  const [selectedRecipeForDetail, setSelectedRecipeForDetail] = useState(null);
  
  // ==========================================
  // COMMENT STATE
  // ==========================================
  const [commentCounts, setCommentCounts] = useState({});
  
  // ==========================================
  // WIDGET STATE
  // ==========================================
  const [groceryListWidgets, setGroceryListWidgets] = useState([]);
  const [mealPlanWidgets, setMealPlanWidgets] = useState([]);
  
  // ==========================================
  // NODE OPERATIONS (Memoized for performance)
  // ==========================================
  
  /**
   * Add a single node to the canvas
   * Validates and normalizes node structure
   */
  const addNode = useCallback((node) => {
    try {
      // 🔍 VALIDATE: Ensure node structure is correct
      validateNode(node);
      
      // 🔧 NORMALIZE: Handle v1/v2 differences
      const normalizedNode = normalizeNode(node);
      
      setNodes(prev => [...prev, normalizedNode]);
      console.log(`✅ Node added: ${normalizedNode.id} (${normalizedNode.type})`);
    } catch (error) {
      console.error('❌ Failed to add node:', error.message);
      console.error('Invalid node:', node);
      throw error;
    }
  }, []);
  
  /**
   * Add multiple nodes at once
   * Validates and normalizes all nodes
   */
  const addNodes = useCallback((newNodes) => {
    try {
      // 🔍 VALIDATE & NORMALIZE: Process all nodes
      const normalizedNodes = newNodes.map(node => {
        validateNode(node);
        return normalizeNode(node);
      });
      
      setNodes(prev => [...prev, ...normalizedNodes]);
      console.log(`✅ ${normalizedNodes.length} nodes added`);
    } catch (error) {
      console.error('❌ Failed to add nodes:', error.message);
      throw error;
    }
  }, []);
  
  /**
   * Update a node's data
   */
  const updateNode = useCallback((nodeId, updates) => {
    setNodes(prev => prev.map(n => 
      n.id === nodeId 
        ? { ...n, data: { ...n.data, ...updates } }
        : n
    ));
    console.log(`🔄 Node updated: ${nodeId}`);
  }, []);
  
  /**
   * Update multiple nodes at once
   */
  const updateNodes = useCallback((updates) => {
    setNodes(prev => prev.map(node => {
      const update = updates.find(u => u.id === node.id);
      return update 
        ? { ...node, data: { ...node.data, ...update.data } }
        : node;
    }));
    console.log(`🔄 ${updates.length} nodes updated`);
  }, []);
  
  /**
   * Delete a node from canvas
   */
  const deleteNode = useCallback((nodeId) => {
    setNodes(prev => prev.filter(n => n.id !== nodeId));
    console.log(`🗑️ Node deleted: ${nodeId}`);
  }, []);
  
  /**
   * Delete multiple nodes at once
   */
  const deleteNodes = useCallback((nodeIds) => {
    setNodes(prev => prev.filter(n => !nodeIds.includes(n.id)));
    console.log(`🗑️ ${nodeIds.length} nodes deleted`);
  }, []);
  
  /**
   * Clear all nodes (reset canvas)
   */
  const clearNodes = useCallback(() => {
    setNodes([]);
    console.log('🧹 All nodes cleared');
  }, []);
  
  // ==========================================
  // UI ACTIONS (Memoized for performance)
  // ==========================================
  
  const openPicker = useCallback(() => setIsPickerOpen(true), []);
  const closePicker = useCallback(() => setIsPickerOpen(false), []);
  const togglePicker = useCallback(() => setIsPickerOpen(prev => !prev), []);
  
  const openTagSidebar = useCallback(() => setIsTagSidebarOpen(true), []);
  const closeTagSidebar = useCallback(() => setIsTagSidebarOpen(false), []);
  const toggleTagSidebar = useCallback(() => setIsTagSidebarOpen(prev => !prev), []);
  
  const openCommentsSidebar = useCallback(() => setIsCommentsSidebarOpen(true), []);
  const closeCommentsSidebar = useCallback(() => setIsCommentsSidebarOpen(false), []);
  const toggleCommentsSidebar = useCallback(() => setIsCommentsSidebarOpen(prev => !prev), []);
  
  const openShortcutsModal = useCallback(() => setIsShortcutsModalOpen(true), []);
  const closeShortcutsModal = useCallback(() => setIsShortcutsModalOpen(false), []);
  
  const openRecipeDetail = useCallback((recipe) => {
    setSelectedRecipeForDetail(recipe);
    setIsRecipeDetailOpen(true);
  }, []);
  
  const closeRecipeDetail = useCallback(() => {
    setIsRecipeDetailOpen(false);
    setSelectedRecipeForDetail(null);
  }, []);
  
  // ==========================================
  // CONTEXT VALUE
  // ==========================================
  const value = {
    // IDs
    whiteboardId,
    householdId,
    
    // Core state
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
    
    // Node operations
    addNode,
    addNodes,
    updateNode,
    updateNodes,
    deleteNode,
    deleteNodes,
    clearNodes,
    
    // UI actions
    openPicker,
    closePicker,
    togglePicker,
    openTagSidebar,
    closeTagSidebar,
    toggleTagSidebar,
    openCommentsSidebar,
    closeCommentsSidebar,
    toggleCommentsSidebar,
    openShortcutsModal,
    closeShortcutsModal,
    openRecipeDetail,
    closeRecipeDetail,
  };
  
  return (
    <WhiteboardContext.Provider value={value}>
      {children}
    </WhiteboardContext.Provider>
  );
}

/**
 * Hook to access whiteboard context
 * Must be used within WhiteboardProvider
 */
export function useWhiteboard() {
  const context = useContext(WhiteboardContext);
  if (!context) {
    throw new Error('useWhiteboard must be used within WhiteboardProvider');
  }
  return context;
}

/**
 * Hook to check if we're within WhiteboardProvider (optional check)
 */
export function useWhiteboardOptional() {
  return useContext(WhiteboardContext);
}
