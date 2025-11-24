# WhiteboardApp Refactoring - No New Tech
**Date:** November 24, 2025  
**Goal:** Break up WhiteboardApp.js using ONLY existing React patterns

---

## 🎯 Core Principle: Extract, Don't Replace

**Use what you have:**
- ✅ React hooks (useState, useEffect, useCallback)
- ✅ Context API (already using AuthContext)
- ✅ Custom hooks (already have some)
- ✅ Component composition
- ✅ Service files (already have whiteboardAPI)

**NO new libraries:**
- ❌ No Zustand
- ❌ No Redux
- ❌ No new dependencies

---

## 📦 New Structure (Using Existing Patterns)

```
src/features/whiteboard/
├── WhiteboardApp.js           (200 lines) - Main coordinator
├── contexts/
│   └── WhiteboardContext.js   (100 lines) - Shared state (like AuthContext)
├── hooks/
│   ├── useWhiteboardData.js   (100 lines) - Load/save whiteboard
│   ├── useRecipeNodes.js      (150 lines) - Recipe operations
│   ├── useGroceryNodes.js     (100 lines) - Grocery operations
│   ├── useMealPlanNodes.js    (100 lines) - Meal plan operations
│   ├── useNoteNodes.js        (80 lines) - Note operations
│   └── useAutoSave.js         (80 lines) - Auto-save logic
├── services/
│   ├── nodeFactory.js         (100 lines) - Create all node types
│   └── whiteboardAPI.js       (existing, good)
└── components/
    ├── WhiteboardCanvas.jsx   (150 lines) - React Flow wrapper
    └── (existing components)  (all good)

Total: ~1,160 lines (vs 3,095)
```

---

## 🔧 Step 1: Create WhiteboardContext (Like AuthContext)

**File:** `src/features/whiteboard/contexts/WhiteboardContext.js`

```javascript
import React, { createContext, useContext, useState, useCallback } from 'react';

const WhiteboardContext = createContext(null);

export function WhiteboardProvider({ children, whiteboardId, householdId }) {
  // All shared state
  const [whiteboard, setWhiteboard] = useState(null);
  const [nodes, setNodes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // UI state
  const [isPickerOpen, setIsPickerOpen] = useState(false);
  const [isTagSidebarOpen, setIsTagSidebarOpen] = useState(false);
  const [isCommentsSidebarOpen, setIsCommentsSidebarOpen] = useState(false);
  const [selectedTags, setSelectedTags] = useState([]);
  const [selectedObjectForComments, setSelectedObjectForComments] = useState(null);
  const [commentCounts, setCommentCounts] = useState({});
  
  // Node operations
  const addNode = useCallback((node) => {
    setNodes(prev => [...prev, node]);
  }, []);
  
  const updateNode = useCallback((id, updates) => {
    setNodes(prev => prev.map(n => 
      n.id === id ? { ...n, data: { ...n.data, ...updates } } : n
    ));
  }, []);
  
  const deleteNode = useCallback((id) => {
    setNodes(prev => prev.filter(n => n.id !== id));
  }, []);
  
  // UI actions
  const openPicker = useCallback(() => setIsPickerOpen(true), []);
  const closePicker = useCallback(() => setIsPickerOpen(false), []);
  const toggleTagSidebar = useCallback(() => setIsTagSidebarOpen(prev => !prev), []);
  
  const value = {
    // State
    whiteboard, setWhiteboard,
    nodes, setNodes,
    loading, setLoading,
    error, setError,
    isPickerOpen,
    isTagSidebarOpen,
    isCommentsSidebarOpen,
    selectedTags,
    selectedObjectForComments,
    commentCounts, setCommentCounts,
    whiteboardId,
    householdId,
    
    // Actions
    addNode,
    updateNode,
    deleteNode,
    openPicker,
    closePicker,
    toggleTagSidebar,
  };
  
  return (
    <WhiteboardContext.Provider value={value}>
      {children}
    </WhiteboardContext.Provider>
  );
}

export function useWhiteboard() {
  const context = useContext(WhiteboardContext);
  if (!context) {
    throw new Error('useWhiteboard must be used within WhiteboardProvider');
  }
  return context;
}
```

**Benefits:**
- Same pattern as AuthContext (already familiar)
- No prop drilling
- Centralized state
- Easy to use

---

## 🎣 Step 2: Extract Custom Hooks

### A. Data Loading Hook

**File:** `src/features/whiteboard/hooks/useWhiteboardData.js`

```javascript
import { useEffect } from 'react';
import { useWhiteboard } from '../contexts/WhiteboardContext';
import whiteboardAPI from '../services/whiteboardAPI';

export function useWhiteboardData() {
  const { 
    whiteboardId, 
    householdId,
    setWhiteboard, 
    setNodes, 
    setLoading, 
    setError,
    setCommentCounts 
  } = useWhiteboard();
  
  useEffect(() => {
    loadWhiteboard();
  }, [whiteboardId]);
  
  async function loadWhiteboard() {
    try {
      setLoading(true);
      
      // Load whiteboard
      const response = await whiteboardAPI.getWhiteboard(whiteboardId);
      setWhiteboard(response.whiteboard);
      
      // Load saved objects
      const nodes = await loadSavedObjects(response.whiteboard);
      setNodes(nodes);
      
      // Load comment counts
      const counts = await loadCommentCounts(whiteboardId);
      setCommentCounts(counts);
      
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  }
  
  async function loadSavedObjects(whiteboard) {
    // Extract this logic from WhiteboardApp
    // Return array of nodes
  }
  
  async function loadCommentCounts(whiteboardId) {
    // Extract this logic from WhiteboardApp
    // Return comment counts object
  }
}
```

---

### B. Recipe Nodes Hook

**File:** `src/features/whiteboard/hooks/useRecipeNodes.js`

```javascript
import { useCallback } from 'react';
import { useWhiteboard } from '../contexts/WhiteboardContext';
import { createRecipeNode } from '../services/nodeFactory';
import { apiCall } from '@/utils/api';
import whiteboardAPI from '../services/whiteboardAPI';

export function useRecipeNodes() {
  const { 
    whiteboardId, 
    addNode, 
    updateNode, 
    deleteNode,
    nodes 
  } = useWhiteboard();
  
  // Add recipe to canvas
  const addRecipe = useCallback(async (recipe, position) => {
    try {
      // Fetch full recipe data
      const response = await apiCall(`/api/v2/recipes/${recipe.id}`);
      const fullRecipe = response.recipe || response.data;
      
      // Create node using factory
      const node = createRecipeNode(fullRecipe, {
        position,
        onClick: openRecipeDetail,
        onDelete: handleDeleteRecipe,
        onTagsChange: handleTagsChange,
      });
      
      // Add to canvas
      addNode(node);
      
      return node;
    } catch (error) {
      console.error('Failed to add recipe:', error);
      throw error;
    }
  }, [addNode, whiteboardId]);
  
  // Delete recipe
  const handleDeleteRecipe = useCallback(async (nodeId, recipeId, objectId) => {
    if (!window.confirm('Remove recipe from canvas?')) return;
    
    try {
      if (objectId && whiteboardId) {
        await whiteboardAPI.deleteObject(whiteboardId, objectId);
      }
      deleteNode(nodeId);
    } catch (error) {
      console.error('Failed to delete recipe:', error);
    }
  }, [deleteNode, whiteboardId]);
  
  // Open recipe detail
  const openRecipeDetail = useCallback((recipeId) => {
    // Modal logic
  }, []);
  
  // Handle tag changes
  const handleTagsChange = useCallback((nodeId, tags) => {
    updateNode(nodeId, { tags });
  }, [updateNode]);
  
  return {
    addRecipe,
    handleDeleteRecipe,
    openRecipeDetail,
    handleTagsChange,
  };
}
```

---

### C. Auto-Save Hook

**File:** `src/features/whiteboard/hooks/useAutoSave.js`

```javascript
import { useEffect, useRef } from 'react';
import { useWhiteboard } from '../contexts/WhiteboardContext';
import whiteboardAPI from '../services/whiteboardAPI';

export function useAutoSave() {
  const { whiteboardId, nodes } = useWhiteboard();
  const saveTimeoutRef = useRef(null);
  const nodesRef = useRef(nodes);
  
  // Keep ref in sync
  useEffect(() => {
    nodesRef.current = nodes;
  }, [nodes]);
  
  // Auto-save on changes
  useEffect(() => {
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current);
    }
    
    saveTimeoutRef.current = setTimeout(() => {
      handleSave();
    }, 2000); // Save after 2 seconds of inactivity
    
    return () => clearTimeout(saveTimeoutRef.current);
  }, [nodes]);
  
  async function handleSave() {
    try {
      await whiteboardAPI.saveWhiteboard(whiteboardId, {
        objects: nodesRef.current
      });
      console.log('✅ Auto-saved');
    } catch (error) {
      console.error('❌ Auto-save failed:', error);
    }
  }
  
  return { handleSave };
}
```

---

## 🏭 Step 3: Create Node Factory

**File:** `src/features/whiteboard/services/nodeFactory.js`

```javascript
/**
 * Single source of truth for creating all node types
 * Use these functions EVERYWHERE
 */

// ==========================================
// RECIPE NODES
// ==========================================

export function createRecipeNode(recipe, options = {}) {
  const normalized = normalizeRecipe(recipe);
  
  return {
    id: options.id || `recipe-${normalized.id}`,
    type: 'recipeCard',
    position: options.position || { x: 200, y: 150 },
    data: {
      recipe: normalized,
      object_id: options.objectId,
      tags: options.tags || [],
      backgroundColor: options.backgroundColor || '#FFFFFF',
      commentCount: options.commentCount || 0,
      hasNewComments: options.hasNewComments || false,
      onClick: options.onClick,
      onDelete: options.onDelete,
      onTagsChange: options.onTagsChange,
      onTagFilterClick: options.onTagFilterClick,
      onColorChange: options.onColorChange,
    }
  };
}

function normalizeRecipe(recipe) {
  return {
    id: recipe.id,
    title: recipe.title || recipe.name,
    image_url: fixImageUrl(recipe.image_url),
    prep_time: recipe.prep_time || 0,
    cook_time: recipe.cook_time || 0,
    total_time: recipe.total_time,
    category: recipe.category,
    created_by: recipe.created_by,
    created_by_name: recipe.created_by_name,
  };
}

function fixImageUrl(url) {
  if (!url) return null;
  if (url.startsWith('/api')) {
    return `${process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000'}${url}`;
  }
  return url;
}

// ==========================================
// GROCERY LIST NODES
// ==========================================

export function createGroceryListNode(groceryList, options = {}) {
  return {
    id: options.id || `grocery-${groceryList.id}`,
    type: 'groceryListNode',
    position: options.position || { x: 200, y: 150 },
    data: {
      list_id: groceryList.id,
      name: groceryList.name,
      items: groceryList.items || [],
      object_id: options.objectId,
      commentCount: options.commentCount || 0,
      onDelete: options.onDelete,
    }
  };
}

// ==========================================
// MEAL PLAN NODES
// ==========================================

export function createMealPlanNode(mealPlan, options = {}) {
  return {
    id: options.id || `meal-plan-${mealPlan.id}`,
    type: 'mealPlanContainer',
    position: options.position || { x: 200, y: 150 },
    width: options.width || 400,
    height: options.height || 500,
    data: {
      name: mealPlan.name,
      mealPlanDbId: mealPlan.id,
      objectId: options.objectId,
      recipeCount: options.recipeCount || 0,
      backgroundColor: options.backgroundColor || '#D1FAE5',
      commentCount: options.commentCount || 0,
      onNameChange: options.onNameChange,
      onColorChange: options.onColorChange,
      onDelete: options.onDelete,
    }
  };
}

// ==========================================
// NOTE NODES
// ==========================================

export function createNoteNode(note, options = {}) {
  return {
    id: options.id || `note-${note.id || Date.now()}`,
    type: 'note',
    position: options.position || { x: 200, y: 150 },
    data: {
      object_id: note.id,
      name: note.name || 'Untitled Note',
      content: note.content || '',
      backgroundColor: note.backgroundColor || '#FEF3C7',
      fontSize: note.fontSize || 14,
      commentCount: options.commentCount || 0,
      createdBy: options.createdBy || 'Unknown',
      onDelete: options.onDelete,
      onSave: options.onSave,
    }
  };
}
```

---

## 📱 Step 4: Simplified WhiteboardApp

**File:** `src/features/whiteboard/WhiteboardApp.js`

```javascript
import React from 'react';
import { WhiteboardProvider } from './contexts/WhiteboardContext';
import WhiteboardCanvas from './components/WhiteboardCanvas';
import './WhiteboardApp.css';

/**
 * Main whiteboard coordinator
 * Now just 200 lines - all logic extracted to hooks/contexts
 */
function WhiteboardApp({ householdId, whiteboardId, onBack }) {
  return (
    <WhiteboardProvider whiteboardId={whiteboardId} householdId={householdId}>
      <div className="whiteboard-app">
        <WhiteboardCanvas onBack={onBack} />
      </div>
    </WhiteboardProvider>
  );
}

export default WhiteboardApp;
```

---

## 🎨 Step 5: Canvas Component

**File:** `src/features/whiteboard/components/WhiteboardCanvas.jsx`

```javascript
import React from 'react';
import { ReactFlow, Controls, Background } from '@xyflow/react';
import { useWhiteboard } from '../contexts/WhiteboardContext';
import { useWhiteboardData } from '../hooks/useWhiteboardData';
import { useRecipeNodes } from '../hooks/useRecipeNodes';
import { useAutoSave } from '../hooks/useAutoSave';
import { nodeTypes } from './nodeTypes';

// Existing components
import LeftToolbar from '../../../components/whiteboard/LeftToolbar';
import RecipePickerPanel from '../../../components/RecipePickerPanel';
import TagFilterSidebar from '../../../components/whiteboard/TagFilterSidebar';
import CommentsSidebar from '../../../components/whiteboard/CommentsSidebar';
import RecipeDetailModal from '../../../components/RecipeDetailModal';

function WhiteboardCanvas({ onBack }) {
  const { 
    nodes, 
    loading, 
    error,
    isPickerOpen,
    whiteboard 
  } = useWhiteboard();
  
  // All logic in hooks
  useWhiteboardData();
  const recipeNodes = useRecipeNodes();
  useAutoSave();
  
  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  
  return (
    <>
      {/* Toolbar */}
      <div className="whiteboard-toolbar">
        <button onClick={onBack}>← Back</button>
        <h1>{whiteboard?.name || 'Whiteboard'}</h1>
      </div>
      
      {/* Canvas */}
      <ReactFlow
        nodes={nodes}
        nodeTypes={nodeTypes}
        onNodesChange={handleNodesChange}
      >
        <Controls />
        <Background />
      </ReactFlow>
      
      {/* Sidebars & Modals - Already good components */}
      <LeftToolbar />
      {isPickerOpen && <RecipePickerPanel />}
      <TagFilterSidebar />
      <CommentsSidebar />
      <RecipeDetailModal />
    </>
  );
}

export default WhiteboardCanvas;
```

---

## 📋 Migration Steps

### Week 1: Extract Foundation
**Day 1:**
- [ ] Create `contexts/WhiteboardContext.js`
- [ ] Wrap WhiteboardApp with provider
- [ ] Test that it still works

**Day 2:**
- [ ] Create `services/nodeFactory.js`
- [ ] Add all create functions
- [ ] Test node creation

**Day 3:**
- [ ] Create `hooks/useWhiteboardData.js`
- [ ] Move loadWhiteboard logic
- [ ] Test loading

**Day 4:**
- [ ] Create `hooks/useRecipeNodes.js`
- [ ] Move recipe logic
- [ ] Update WhiteboardApp to use hook

**Day 5:**
- [ ] Test everything still works
- [ ] Fix any issues

---

### Week 2: Extract Remaining Features
**Day 1:**
- [ ] Create `hooks/useGroceryNodes.js`
- [ ] Move grocery logic

**Day 2:**
- [ ] Create `hooks/useMealPlanNodes.js`
- [ ] Move meal plan logic

**Day 3:**
- [ ] Create `hooks/useNoteNodes.js`
- [ ] Move note logic

**Day 4:**
- [ ] Create `hooks/useAutoSave.js`
- [ ] Move save logic

**Day 5:**
- [ ] Test all features work
- [ ] Fix issues

---

### Week 3: Simplify Main Component
**Day 1-2:**
- [ ] Create `components/WhiteboardCanvas.jsx`
- [ ] Move rendering logic

**Day 3-4:**
- [ ] Simplify WhiteboardApp.js
- [ ] Should be < 200 lines now

**Day 5:**
- [ ] Test everything
- [ ] Verify no regressions

---

### Week 4: Cleanup
**Day 1-2:**
- [ ] Remove duplicate code
- [ ] Standardize node creation (use factory everywhere)

**Day 3:**
- [ ] Test with household sharing
- [ ] Test with multiple users

**Day 4:**
- [ ] Load test (50+ recipes)
- [ ] Performance check

**Day 5:**
- [ ] Documentation
- [ ] Celebrate! 🎉

---

## 📊 Before vs After

### Before:
```
WhiteboardApp.js
├── 3,095 lines
├── 162 functions
├── 20+ useState hooks
├── Everything mixed together
└── Can't change anything without breaking everything
```

### After:
```
Total: ~1,160 lines split across:

WhiteboardApp.js (200 lines)
  └── Just coordinator

WhiteboardContext.js (100 lines)
  └── Shared state (like AuthContext)

useWhiteboardData.js (100 lines)
  └── Load/save logic

useRecipeNodes.js (150 lines)
  └── Recipe operations

useGroceryNodes.js (100 lines)
  └── Grocery operations

useMealPlanNodes.js (100 lines)
  └── Meal plan operations

useNoteNodes.js (80 lines)
  └── Note operations

useAutoSave.js (80 lines)
  └── Auto-save logic

nodeFactory.js (100 lines)
  └── Create all node types

WhiteboardCanvas.jsx (150 lines)
  └── Rendering only
```

---

## ✅ Benefits

### Maintainability:
- ✅ Each file < 200 lines
- ✅ Single responsibility
- ✅ Easy to find code
- ✅ Easy to test
- ✅ Can change recipes without touching grocery

### Frontend Communication:
- ✅ Clear API (context + hooks)
- ✅ No prop drilling
- ✅ Predictable state updates

### Backend Communication:
- ✅ All API calls in hooks
- ✅ Easy to see what calls what
- ✅ Easy to update endpoints

### Mobile Communication:
- ✅ nodeFactory.js = single source of truth
- ✅ Mobile can import same factories
- ✅ Consistent data structures

---

## 🎯 Next Step

Want me to **start with Week 1, Day 1?**

I'll create:
1. `WhiteboardContext.js` (like AuthContext)
2. Test it works
3. Then move to Day 2

**No new tech. Just better organized React code.**

