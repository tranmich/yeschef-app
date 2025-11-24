# Whiteboard Decomposition Plan - Technical Specification
**Date:** November 24, 2025  
**Version:** 1.0  
**Status:** Planning  
**Goal:** Refactor WhiteboardApp.js (3,095 lines) into maintainable modules using existing React patterns

---

## 📋 Document Overview

**Purpose:** Technical specification for breaking up the whiteboard monolith  
**Scope:** Frontend refactoring only - no backend changes, no new dependencies  
**Timeline:** 4 weeks  
**Stakeholders:** Frontend, Backend, Mobile teams

---

## 🎯 Core Architecture Principle

**Whiteboard is NOT an application - it's a CANVAS for features:**
- ✅ Recipe cards (links to recipes table)
- ✅ Grocery lists (links to grocery_lists table)
- ✅ Meal plans (links to meal_plans table)
- ✅ Notes (freeform content)
- ✅ Activity feed (events display)

**Current Problem:** Everything lives in WhiteboardApp.js (3,095 lines)  
**Solution:** Whiteboard = Canvas Component + Feature Modules + Shared Context

---

## 📊 Current State Analysis

### File Metrics
```
WhiteboardApp.js:
  Lines: 3,095
  Functions: 162
  State Variables: 20+
  Dependencies: 36 imports
  Complexity: God Object (unmaintainable)
```

### Existing Hooks
```
frontend/src/hooks/
├── useDragAndDrop.js      ✅ Keep - generic utility
├── useMealPlanner.js      ✅ Keep - used in MainApp
├── usePantry.js           ✅ Keep - pantry management
└── useSidebar.js          ✅ Keep - sidebar state
```

### Existing Contexts
```
frontend/src/contexts/
└── AuthContext.js         ✅ Pattern to follow for WhiteboardContext
    - Uses createContext/useContext
    - Provides auth state + actions
    - Clean API for consumers
```

---

## 🗄️ Database Schema Reference

### Primary Tables (from 20251103_create_whiteboard_tables.sql)

#### 1. `wb` (whiteboards)
```sql
id              SERIAL PRIMARY KEY
hid             INTEGER (household_id) - CASCADE DELETE
n               VARCHAR(255) (name)
d               TEXT (description)
tt              VARCHAR(20) (template_type: freeform, weekly_planner, party_board, meal_prep)
cs              JSONB (canvas_settings: viewport, background, grid)
cby             INTEGER (created_by user_id)
ca, ua, laa     TIMESTAMPS (created, updated, last_activity)
deleted_at      TIMESTAMP (soft delete)
deleted_by      INTEGER (user_id)
```

#### 2. `wbo` (whiteboard_objects)
```sql
id              SERIAL PRIMARY KEY
wid             INTEGER (whiteboard_id) - CASCADE DELETE
t               VARCHAR(10) (type: 'rc', 'gl', 'mp', 'nt', 'im', 'cn', 'sc')

-- Polymorphic references (NO data duplication)
rid             INTEGER (recipe_id) - SET NULL on delete
gid             INTEGER (grocery_list_id) - SET NULL on delete  
mid             INTEGER (meal_plan_id) - SET NULL on delete

p               JSONB [x, y, width, height, z-index]
s               JSONB (style: bg, borderColor, borderWidth, borderRadius)
tags            TEXT[] (organization tags)
c               JSONB (content - for notes/images only)

cby             INTEGER (created_by)
ca, ua          TIMESTAMPS
lby, lat        INTEGER, TIMESTAMP (lock for collaboration)
deleted_at      TIMESTAMP (soft delete)
```

#### 3. `wbc` (whiteboard_comments)
```sql
id              SERIAL PRIMARY KEY
oid             INTEGER (object_id) - CASCADE DELETE
pid             INTEGER (parent_id for threading)
td              INTEGER (thread_depth 0-5)
uid             INTEGER (user_id)
txt             TEXT (content)
rx              JSONB (reactions: {"👍":[user_ids]})
mu              INTEGER[] (mentioned_users)
rv              BOOLEAN (is_resolved)
rby, rat        INTEGER, TIMESTAMP (resolved_by, resolved_at)
ca, ua          TIMESTAMPS
deleted_at      TIMESTAMP
```

#### 4. `wbco` (whiteboard_collaborators)
```sql
PRIMARY KEY (wid, uid)
rl              VARCHAR(10) (role: 'admin', 'user')
ia              BOOLEAN (is_active - currently online)
lsa             TIMESTAMP (last_seen_at)
cp              JSONB (cursor_position [x, y])
coid            INTEGER (current_object_id being edited)
ast             VARCHAR(20) (activity_status: viewing, editing, commenting)
un, ua          VARCHAR, JSONB (cached user_name, user_avatar)
ja, ua_ts       TIMESTAMPS (joined_at, updated_at)
```

#### 5. `wbe` (whiteboard_events)
```sql
id              SERIAL PRIMARY KEY
wid             INTEGER (whiteboard_id)
et              VARCHAR(50) (event_type: whiteboard_created, object_created, etc.)
uid             INTEGER (user_id who triggered)
ed              JSONB (event_data: flexible metadata)
ca              TIMESTAMP
```

### Key Constraints
- One reference per object: `CHECK ((rid IS NOT NULL)::int + (gid IS NOT NULL)::int + (mid IS NOT NULL)::int <= 1)`
- Valid types: `'rc','gl','mp','nt','im','cn','sc'`
- Thread depth limit: `0-5` levels
- Soft delete: 14-day retention before permanent deletion

---

## 🔐 Authentication Requirements

### Current Auth System (from AuthContext.js)

**V2 Migration Complete** (Oct 31, 2025)

#### Auth State Structure
```javascript
{
  user: {
    id: number,
    email: string,
    name: string,
    // ... other user fields
  },
  token: string,  // JWT token
  loading: boolean,
  isAuthenticated: boolean
}
```

#### Auth API Endpoints (V2)
```
POST /api/v2/auth/register    - Create account
POST /api/v2/auth/login       - Login (returns token + user)
POST /api/v2/auth/logout      - Logout
GET  /api/v2/auth/me          - Get current user
```

#### Token Storage
- **Location:** `localStorage.getItem('authToken')`
- **Format:** JWT Bearer token
- **Header:** `Authorization: Bearer ${token}`

### Whiteboard Auth Requirements

#### Permission Model
1. **Household Member Check**
   - User must be member of household (via `household_members` table)
   - Verified via `households.owner_user_id` or `household_members.user_id`

2. **Whiteboard Access**
   - Admin: Full control (create, delete, manage users)
   - User: Can view + edit objects
   - Guest: View only (future feature)

3. **Object Ownership**
   - Creator can delete own objects
   - Admins can delete any object
   - Objects inherit whiteboard permissions

#### Auth Checks (Backend)
```python
def check_whiteboard_access(user_id, whiteboard_id):
    """Verify user has access to whiteboard"""
    whiteboard = get_whiteboard(whiteboard_id)
    household_id = whiteboard.hid
    
    # Check if user is member
    is_member = check_household_membership(user_id, household_id)
    if not is_member:
        raise PermissionError("Not a household member")
    
    # Check whiteboard collaborator role
    collaborator = get_collaborator(whiteboard_id, user_id)
    return collaborator.role  # 'admin' or 'user'
```

---

## 📦 Proposed Module Structure

```
src/features/whiteboard/
├── WhiteboardApp.js           (200 lines) - Main coordinator
├── contexts/
│   └── WhiteboardContext.js   (150 lines) - Shared state (pattern: AuthContext)
├── hooks/
│   ├── useWhiteboardData.js   (120 lines) - Load/save whiteboard
│   ├── useWhiteboardAuth.js   (80 lines) - Permission checks
│   ├── useRecipeNodes.js      (150 lines) - Recipe CRUD operations
│   ├── useGroceryNodes.js     (120 lines) - Grocery list operations
│   ├── useMealPlanNodes.js    (120 lines) - Meal plan operations
│   ├── useNoteNodes.js        (100 lines) - Note operations
│   ├── useCollaboration.js    (150 lines) - Pusher + presence
│   ├── useComments.js         (100 lines) - Comment operations
│   └── useAutoSave.js         (100 lines) - Auto-save logic
├── services/
│   ├── nodeFactory.js         (200 lines) - Create all node types
│   ├── whiteboardAPI.js       (existing) - API calls
│   └── nodeValidation.js      (80 lines) - Validate node structures
├── components/
│   ├── WhiteboardCanvas.jsx   (200 lines) - React Flow wrapper
│   ├── nodes/                 (existing) - Node components
│   ├── LeftToolbar.jsx        (existing)
│   ├── TagFilterSidebar.jsx   (existing)
│   └── CommentsSidebar.jsx    (existing)
└── utils/
    ├── permissions.js         (60 lines) - Permission helpers
    └── constants.js           (40 lines) - Node types, colors, etc.

Total: ~1,870 lines (vs 3,095)
Reduction: 40% smaller, infinitely more maintainable
```

---

## 🎣 Hook Specifications

### Hook Design Pattern
Following existing patterns from `usePantry.js` and `AuthContext.js`:
- Return object with state + actions
- Handle loading/error states
- Use useCallback for action functions
- Clean up effects on unmount
│   ├── components/
│   │   ├── WhiteboardCanvas.jsx       (200 lines) - React Flow wrapper
│   │   ├── LeftToolbar.jsx            (existing, good)
│   │   ├── TagFilterSidebar.jsx       (existing, good)
│   │   └── CommentsSidebar.jsx        (existing, good)
│   ├── hooks/
│   │   ├── useWhiteboardState.js      (50 lines) - Core state
│   │   ├── useAutoSave.js             (50 lines) - Auto-save logic
│   │   └── useCollaboration.js        (100 lines) - Pusher/presence
│   ├── services/
│   │   └── whiteboardAPI.js           (existing, good)
│   └── store/
│       └── whiteboardStore.js         (150 lines) - Zustand store
│
├── recipes/              ← Recipe feature
│   ├── components/
│   │   ├── RecipeCard.jsx             (existing, good)
│   │   ├── RecipePickerPanel.jsx      (existing, good)
│   │   └── RecipeDetailModal.jsx      (existing, good)
│   ├── hooks/
│   │   └── useRecipeNodes.js          (100 lines) - Recipe node logic
│   └── services/
│       └── recipeNodeFactory.js       (50 lines) - Create recipe nodes
│
├── grocery-lists/        ← Grocery list feature
│   ├── components/
│   │   └── GroceryListNode.jsx        (existing, good)
│   ├── hooks/
│   │   └── useGroceryLists.js         (100 lines) - Grocery logic
│   └── services/
│       └── groceryNodeFactory.js      (50 lines) - Create grocery nodes
│
├── meal-plans/           ← Meal planning feature
│   ├── components/
│   │   ├── MealPlanContainer.jsx      (existing, good)
│   │   └── MealPlanWidget.jsx         (existing, good)
│   ├── hooks/
│   │   └── useMealPlans.js            (100 lines) - Meal plan logic
│   └── services/
│       └── mealPlanNodeFactory.js     (50 lines) - Create meal plan nodes
│
├── notes/                ← Note/journal feature
│   ├── components/
│   │   └── NoteBlock.jsx              (existing, good)
│   ├── hooks/
│   │   └── useNotes.js                (80 lines) - Note logic
│   └── services/
│       └── noteNodeFactory.js         (30 lines) - Create note nodes
│
└── activity-feed/        ← Activity feed feature
    ├── components/
    │   └── ActivityFeedNode.jsx       (existing, good)
    └── hooks/
        └── useActivityFeed.js         (50 lines) - Activity logic

Total: ~1,200 lines (vs 3,095)
```

---

## 🔧 Phase 1: Extract State Management (WEEK 1)

### Create Zustand Store

**File:** `src/features/whiteboard/store/whiteboardStore.js`

```javascript
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export const useWhiteboardStore = create(
  devtools((set, get) => ({
    // ==========================================
    // STATE
    // ==========================================
    whiteboard: null,
    nodes: [],
    loading: false,
    error: null,
    
    // UI State
    isPickerOpen: false,
    isTagSidebarOpen: false,
    isCommentsSidebarOpen: false,
    selectedTags: [],
    selectedObjectForComments: null,
    
    // Comment counts
    commentCounts: {},
    
    // ==========================================
    // ACTIONS
    // ==========================================
    
    // Whiteboard actions
    setWhiteboard: (whiteboard) => set({ whiteboard }),
    setLoading: (loading) => set({ loading }),
    setError: (error) => set({ error }),
    
    // Node actions
    setNodes: (nodes) => set({ nodes }),
    addNode: (node) => set((state) => ({ 
      nodes: [...state.nodes, node] 
    })),
    updateNode: (id, data) => set((state) => ({
      nodes: state.nodes.map((n) =>
        n.id === id ? { ...n, data: { ...n.data, ...data } } : n
      )
    })),
    deleteNode: (id) => set((state) => ({
      nodes: state.nodes.filter((n) => n.id !== id)
    })),
    
    // UI actions
    openPicker: () => set({ isPickerOpen: true }),
    closePicker: () => set({ isPickerOpen: false }),
    openTagSidebar: () => set({ isTagSidebarOpen: true }),
    closeTagSidebar: () => set({ isTagSidebarOpen: false }),
    toggleTagSidebar: () => set((state) => ({ 
      isTagSidebarOpen: !state.isTagSidebarOpen 
    })),
    
    // Tag actions
    addTag: (tag) => set((state) => ({
      selectedTags: [...state.selectedTags, tag]
    })),
    removeTag: (tag) => set((state) => ({
      selectedTags: state.selectedTags.filter((t) => t !== tag)
    })),
    clearTags: () => set({ selectedTags: [] }),
    
    // Comment actions
    setCommentCounts: (counts) => set({ commentCounts: counts }),
    openComments: (object) => set({ 
      isCommentsSidebarOpen: true,
      selectedObjectForComments: object 
    }),
    closeComments: () => set({ 
      isCommentsSidebarOpen: false,
      selectedObjectForComments: null 
    }),
  }))
);
```

**Benefits:**
- Single source of truth
- Easy to debug (devtools)
- No prop drilling
- Easy to test
- Clear ownership

---

## 🧩 Phase 2: Extract Node Factories (WEEK 1)

### Recipe Node Factory

**File:** `src/features/recipes/services/recipeNodeFactory.js`

```javascript
/**
 * Single source of truth for creating recipe nodes
 * Use this EVERYWHERE - no more inconsistency!
 */

export function createRecipeNode(recipe, options = {}) {
  // Normalize recipe data (handle v1/v2)
  const normalized = normalizeRecipe(recipe);
  
  return {
    id: options.id || `recipe-${normalized.id}`,
    type: 'recipeCard',
    position: options.position || { x: 200, y: 150 },
    data: {
      // Single recipe object - no duplicates!
      recipe: normalized,
      
      // Whiteboard-specific data
      object_id: options.objectId,
      tags: options.tags || [],
      backgroundColor: options.backgroundColor || '#FFFFFF',
      
      // Comment data
      commentCount: options.commentCount || 0,
      hasNewComments: options.hasNewComments || false,
      
      // Handlers (passed from outside)
      onClick: options.onClick,
      onDelete: options.onDelete,
      onTagsChange: options.onTagsChange,
      onTagFilterClick: options.onTagFilterClick,
      onColorChange: options.onColorChange,
    }
  };
}

/**
 * Normalize recipe from API (v1 or v2)
 */
function normalizeRecipe(recipe) {
  return {
    id: recipe.id,
    title: recipe.title || recipe.name, // v2 | v1
    image_url: fixImageUrl(recipe.image_url),
    prep_time: recipe.prep_time || recipe.prep_time_minutes || 0,
    cook_time: recipe.cook_time || recipe.cook_time_minutes || 0,
    total_time: recipe.total_time,
    category: recipe.category,
    created_by: recipe.created_by,
    created_by_name: recipe.created_by_name,
    created_by_email: recipe.created_by_email,
  };
}

/**
 * Fix image URLs (handle relative paths)
 */
function fixImageUrl(url) {
  if (!url) return null;
  if (url.startsWith('/api')) {
    return `${process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000'}${url}`;
  }
  return url;
}

/**
 * Validate recipe node structure
 */
export function validateRecipeNode(node) {
  const errors = [];
  
  if (!node.data?.recipe) {
    errors.push('Missing recipe object');
  }
  if (!node.data?.recipe?.id) {
    errors.push('Missing recipe.id');
  }
  if (!node.data?.onClick || typeof node.data.onClick !== 'function') {
    errors.push('Invalid onClick handler');
  }
  
  if (errors.length > 0) {
    console.error('❌ Invalid recipe node:', node.id, errors);
    return false;
  }
  return true;
}
```

**Usage (everywhere):**
```javascript
// OLD (3 different ways):
// ... 50 lines of duplicate code ...

// NEW (one way):
import { createRecipeNode } from '@/features/recipes/services/recipeNodeFactory';

const node = createRecipeNode(recipe, {
  position: { x: 100, y: 200 },
  objectId: savedObject?.id,
  tags: savedObject?.tags || [],
  onClick: handleRecipeClick,
  onDelete: handleDeleteRecipe,
});
```

---

## 🎣 Phase 3: Extract Custom Hooks (WEEK 2)

### Recipe Nodes Hook

**File:** `src/features/recipes/hooks/useRecipeNodes.js`

```javascript
import { useCallback } from 'react';
import { useWhiteboardStore } from '@/features/whiteboard/store/whiteboardStore';
import { createRecipeNode } from '../services/recipeNodeFactory';
import { apiCall } from '@/utils/api';

export function useRecipeNodes() {
  const { addNode, updateNode, deleteNode } = useWhiteboardStore();
  
  // Add recipe to canvas
  const addRecipeToCanvas = useCallback(async (recipe, position) => {
    try {
      // Fetch full recipe data
      const response = await apiCall(`/api/v2/recipes/${recipe.id}`);
      const fullRecipe = response.recipe || response.data;
      
      // Create node
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
  }, [addNode]);
  
  // Delete recipe from canvas
  const handleDeleteRecipe = useCallback(async (nodeId, recipeId, objectId) => {
    if (!window.confirm('Remove recipe from canvas?')) return;
    
    try {
      // Delete from backend if it has an object_id
      if (objectId) {
        await whiteboardAPI.deleteObject(whiteboardId, objectId);
      }
      
      // Remove from canvas
      deleteNode(nodeId);
    } catch (error) {
      console.error('Failed to delete recipe:', error);
      throw error;
    }
  }, [deleteNode]);
  
  // Open recipe detail modal
  const openRecipeDetail = useCallback((recipeId) => {
    // ... modal logic
  }, []);
  
  // Handle tag changes
  const handleTagsChange = useCallback((nodeId, tags) => {
    updateNode(nodeId, { tags });
  }, [updateNode]);
  
  return {
    addRecipeToCanvas,
    handleDeleteRecipe,
    openRecipeDetail,
    handleTagsChange,
  };
}
```

---

## 🎨 Phase 4: Simplify WhiteboardCanvas (WEEK 2)

**File:** `src/features/whiteboard/components/WhiteboardCanvas.jsx`

```javascript
import React from 'react';
import { ReactFlow, Controls, Background } from '@xyflow/react';
import { useWhiteboardStore } from '../store/whiteboardStore';
import { useWhiteboardState } from '../hooks/useWhiteboardState';
import { useAutoSave } from '../hooks/useAutoSave';
import { useCollaboration } from '../hooks/useCollaboration';
import { nodeTypes } from './nodeTypes';

export function WhiteboardCanvas({ whiteboardId, householdId }) {
  // Store state
  const { nodes, loading, error } = useWhiteboardStore();
  
  // Custom hooks handle all logic
  useWhiteboardState(whiteboardId, householdId);
  useAutoSave(whiteboardId);
  useCollaboration(whiteboardId, householdId);
  
  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;
  
  return (
    <div className="whiteboard-canvas">
      <ReactFlow
        nodes={nodes}
        nodeTypes={nodeTypes}
        onNodesChange={handleNodesChange}
      >
        <Controls />
        <Background />
      </ReactFlow>
      
      {/* Sidebars and modals */}
      <RecipePickerPanel />
      <TagFilterSidebar />
      <CommentsSidebar />
      <RecipeDetailModal />
    </div>
  );
}
```

**Result:** ~200 lines (vs 3,095)

---

## 📋 Complete Migration Plan

### Week 1: Foundation
**Day 1-2: Setup**
- [ ] Install Zustand: `npm install zustand`
- [ ] Create folder structure
- [ ] Create whiteboardStore.js

**Day 3-4: Node Factories**
- [ ] Create recipeNodeFactory.js
- [ ] Create groceryNodeFactory.js
- [ ] Create mealPlanNodeFactory.js
- [ ] Create noteNodeFactory.js

**Day 5: Testing**
- [ ] Test node creation
- [ ] Test validation
- [ ] Verify no breaking changes

---

### Week 2: Extract Hooks
**Day 1-2: Recipe Hooks**
- [ ] Create useRecipeNodes.js
- [ ] Migrate recipe logic from WhiteboardApp
- [ ] Update WhiteboardApp to use hook

**Day 3: Other Hooks**
- [ ] Create useGroceryLists.js
- [ ] Create useMealPlans.js
- [ ] Create useNotes.js

**Day 4-5: Core Hooks**
- [ ] Create useWhiteboardState.js
- [ ] Create useAutoSave.js
- [ ] Create useCollaboration.js

---

### Week 3: Simplify Component
**Day 1-3: Extract to Store**
- [ ] Move all useState to whiteboardStore
- [ ] Update components to use store
- [ ] Remove useState from WhiteboardApp

**Day 4-5: Simplify Component**
- [ ] Create WhiteboardCanvas.jsx
- [ ] Move rendering to new component
- [ ] WhiteboardApp becomes thin wrapper

---

### Week 4: Cleanup & Test
**Day 1-2: Remove Duplicates**
- [ ] Remove duplicate code
- [ ] Remove v1 fallbacks
- [ ] Standardize on v2

**Day 3-4: Testing**
- [ ] Test all features
- [ ] Test collaboration
- [ ] Test household sharing
- [ ] Load test with 50+ recipes

**Day 5: Documentation**
- [ ] Document new structure
- [ ] Add JSDoc comments
- [ ] Update README

---

## 📊 Before vs After

### Before (Current):
```
WhiteboardApp.js: 3,095 lines
├── 162 functions
├── 20+ state variables
├── All logic mixed together
└── Impossible to maintain
```

### After (Goal):
```
Total: ~1,200 lines split across:
├── whiteboardStore.js (150 lines) - State
├── WhiteboardCanvas.jsx (200 lines) - UI
├── useRecipeNodes.js (100 lines) - Recipe logic
├── useGroceryLists.js (100 lines) - Grocery logic
├── useMealPlans.js (100 lines) - Meal plan logic
├── useNotes.js (80 lines) - Note logic
├── useWhiteboardState.js (50 lines) - Core logic
├── useAutoSave.js (50 lines) - Save logic
├── useCollaboration.js (100 lines) - Real-time
├── recipeNodeFactory.js (50 lines) - Create nodes
└── ... other factories (200 lines)

Easy to maintain ✅
Easy to test ✅
Easy to extend ✅
```

---

## 🎯 Success Metrics

### Code Quality:
- ✅ No file > 300 lines
- ✅ No function > 50 lines
- ✅ Single source of truth (store)
- ✅ One way to create nodes (factory)
- ✅ Separation of concerns (features)

### Maintainability:
- ✅ Can add feature without touching core
- ✅ Can fix bug in one place
- ✅ Can test features independently
- ✅ New dev can understand in < 1 hour

### Performance:
- ✅ Faster renders (fewer re-renders)
- ✅ Better memory (no duplicates)
- ✅ Cleaner code (easier to optimize)

---

## 📚 API Reference

### Backend Endpoints Required

#### Whiteboard Management
```
GET    /api/v2/whiteboard/:id                          - Get whiteboard metadata
GET    /api/v2/whiteboard/:id/objects                  - Get all objects
POST   /api/v2/whiteboard                              - Create whiteboard
PATCH  /api/v2/whiteboard/:id                          - Update whiteboard
DELETE /api/v2/whiteboard/:id                          - Soft delete whiteboard
POST   /api/v2/whiteboard/:id/restore                  - Restore from trash
```

#### Object Management
```
POST   /api/v2/whiteboard/:wid/objects                 - Create object
GET    /api/v2/whiteboard/:wid/o/:oid                  - Get single object
PATCH  /api/v2/whiteboard/:wid/o/:oid                  - Update object
DELETE /api/v2/whiteboard/:wid/o/:oid                  - Delete object
```

#### Recipe Operations
```
GET    /api/v2/recipes/:id                             - Get single recipe
GET    /api/v2/recipes?ids=1,2,3                       - Batch fetch recipes
GET    /api/v2/recipes?user_id=:id                     - User's recipes
```

#### Comment Operations
```
GET    /api/v2/comments?object_id=:oid                 - Get object comments
GET    /api/v2/comments/count?whiteboard_id=:wid      - Get all comment counts
POST   /api/v2/comments                                 - Create comment
PATCH  /api/v2/comments/:id                            - Update comment
DELETE /api/v2/comments/:id                            - Delete comment
POST   /api/v2/comments/:id/react                      - Add reaction
POST   /api/v2/comments/:id/resolve                    - Resolve thread
```

#### Collaboration
```
GET    /api/v2/whiteboard/:wid/collaborators          - Get all collaborators
POST   /api/v2/whiteboard/:wid/collaborators          - Add collaborator
DELETE /api/v2/whiteboard/:wid/collaborators/:uid     - Remove collaborator
PATCH  /api/v2/whiteboard/:wid/collaborators/:uid     - Update role
POST   /pusher/auth                                    - Authenticate Pusher channel
```

### Frontend-Mobile Data Contract

#### Node Structure (Shared)
All platforms use identical node structure from `nodeFactory.js`:

```javascript
// Recipe Node
{
  id: string,              // 'recipe-{id}'
  type: 'recipeCard',
  position: { x, y },
  data: {
    recipe: {              // SINGLE source of truth
      id: number,
      title: string,
      image_url: string,
      prep_time: number,   // minutes
      cook_time: number,
      category: string,
      created_by: number,
      created_by_name: string
    },
    object_id: number,     // wbo.id (optional for unsaved)
    tags: string[],
    backgroundColor: string,
    commentCount: number,
    onClick: Function,
    onDelete: Function,
    onTagsChange: Function
  }
}
```

**Mobile Import:**
```javascript
// Mobile can import and use same factory
import { createRecipeNode } from '@shared/nodeFactory';

const node = createRecipeNode(recipe, {
  position: { x: 100, y: 200 },
  onClick: handleRecipeClick
});
```

---

## 🔒 Security & Permissions Matrix

### Role-Based Access Control

| Action | Admin | User | Guest |
|--------|-------|------|-------|
| View whiteboard | ✅ | ✅ | ✅ |
| Add objects | ✅ | ✅ | ❌ |
| Edit objects | ✅ | ✅ | ❌ |
| Delete own objects | ✅ | ✅ | ❌ |
| Delete any objects | ✅ | ❌ | ❌ |
| Manage users | ✅ | ❌ | ❌ |
| Delete whiteboard | ✅ | ❌ | ❌ |
| Add comments | ✅ | ✅ | ✅ |
| Resolve comments | ✅ | ✅ | ❌ |

### Permission Helpers
```javascript
// utils/permissions.js

export function canEditObject(user, object) {
  if (!user) return false;
  if (user.role === 'admin') return true;
  if (object.created_by === user.id) return true;
  return user.role === 'user';
}

export function canDeleteObject(user, object) {
  if (!user) return false;
  if (user.role === 'admin') return true;
  if (object.created_by === user.id) return true;
  return false;
}

export function canManageUsers(user) {
  return user?.role === 'admin';
}
```

---

## 🧪 Testing Strategy

### Unit Tests
```javascript
// hooks/__tests__/useRecipeNodes.test.js
describe('useRecipeNodes', () => {
  test('addRecipe creates node with correct structure', async () => {
    const { result } = renderHook(() => useRecipeNodes());
    const node = await result.current.addRecipe(mockRecipe, { x: 100, y: 200 });
    
    expect(node.type).toBe('recipeCard');
    expect(node.data.recipe).toEqual(mockRecipe);
    expect(node.position).toEqual({ x: 100, y: 200 });
  });
  
  test('deleteRecipe calls API and removes node', async () => {
    // ... test implementation
  });
});
```

### Integration Tests
```javascript
// WhiteboardApp.integration.test.js
describe('Whiteboard Integration', () => {
  test('loads whiteboard with saved objects', async () => {
    render(<WhiteboardApp whiteboardId={1} householdId={1} />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Whiteboard')).toBeInTheDocument();
      expect(screen.getAllByTestId('recipe-card')).toHaveLength(5);
    });
  });
  
  test('adds recipe from picker', async () => {
    // ... test implementation
  });
});
```

### E2E Tests
```javascript
// e2e/whiteboard.spec.js
test('household members can collaborate', async ({ page, context }) => {
  // User 1: Create whiteboard, add recipe
  const page1 = await context.newPage();
  await page1.goto('/whiteboard/1');
  await page1.click('[data-testid="add-recipe"]');
  
  // User 2: See recipe appear in real-time
  const page2 = await context.newPage();
  await page2.goto('/whiteboard/1');
  await page2.waitForSelector('[data-testid="recipe-card"]');
});
```

---

## 📊 Performance Requirements

### Load Time Targets
- Initial page load: < 2 seconds
- Whiteboard data fetch: < 500ms
- Recipe batch fetch (10): < 300ms
- Auto-save operation: < 200ms

### Render Performance
- Whiteboard with 50 objects: 60 FPS
- Drag operation: No frame drops
- Real-time update latency: < 100ms

### Memory Constraints
- Whiteboard with 100 objects: < 50MB
- No memory leaks on object add/delete
- Efficient re-renders (React.memo where needed)

---

## 🚀 Migration Execution Plan

### Phase 0: Preparation (Week 0)
- [ ] Review this document with team
- [ ] Approve architecture
- [ ] Set up feature branch
- [ ] Create backup of WhiteboardApp.js
- [ ] Document current API behavior

### Phase 1: Foundation (Week 1)

**Day 1: Context Setup**
- [ ] Create `contexts/WhiteboardContext.js`
- [ ] Wrap WhiteboardApp with Provider
- [ ] Test app still works
- [ ] Commit: "feat: Add WhiteboardContext"

**Day 2: Node Factory**
- [ ] Create `services/nodeFactory.js`
- [ ] Add createRecipeNode function
- [ ] Add validation functions
- [ ] Test node creation
- [ ] Commit: "feat: Add node factory"

**Day 3: Data Hook**
- [ ] Create `hooks/useWhiteboardData.js`
- [ ] Extract loadWhiteboard logic
- [ ] Test data loading
- [ ] Commit: "refactor: Extract useWhiteboardData"

**Day 4: Recipe Hook**
- [ ] Create `hooks/useRecipeNodes.js`
- [ ] Extract recipe operations
- [ ] Update WhiteboardApp to use hook
- [ ] Test recipe operations
- [ ] Commit: "refactor: Extract useRecipeNodes"

**Day 5: Testing & Bug Fixes**
- [ ] Test all features work
- [ ] Fix any regressions
- [ ] Code review
- [ ] Commit: "fix: Week 1 bug fixes"

### Phase 2: Feature Hooks (Week 2)

**Days 1-4:** Extract remaining hooks
- [ ] useGroceryNodes.js
- [ ] useMealPlanNodes.js
- [ ] useNoteNodes.js
- [ ] useComments.js

**Day 5:** Integration Testing
- [ ] Test all features together
- [ ] Performance check
- [ ] Code review

### Phase 3: Simplification (Week 3)

**Days 1-2:** Canvas Component
- [ ] Create `components/WhiteboardCanvas.jsx`
- [ ] Move rendering logic
- [ ] Test rendering

**Days 3-4:** Simplify Main Component
- [ ] Simplify WhiteboardApp.js
- [ ] Should be < 200 lines
- [ ] Remove duplicate code

**Day 5:** Integration Testing
- [ ] Test complete flow
- [ ] Verify no regressions

### Phase 4: Cleanup (Week 4)

**Days 1-2:** Code Quality
- [ ] Remove all duplicate code
- [ ] Standardize node creation
- [ ] Add JSDoc comments
- [ ] Run linter

**Day 3:** Documentation
- [ ] Update README
- [ ] Document new architecture
- [ ] Create migration guide

**Day 4:** Testing
- [ ] Load test (50+ objects)
- [ ] Performance profiling
- [ ] Household collaboration test
- [ ] Mobile compatibility test

**Day 5:** Deploy
- [ ] Merge to main
- [ ] Deploy to staging
- [ ] QA testing
- [ ] Deploy to production
- [ ] Monitor for issues

---

## 📝 Success Criteria

### Code Quality Metrics
- ✅ No file > 300 lines
- ✅ No function > 50 lines
- ✅ All hooks < 150 lines
- ✅ Zero duplicate node creation code
- ✅ JSDoc comments on all public functions

### Functionality Requirements
- ✅ All features work as before
- ✅ No regressions
- ✅ Household sharing works
- ✅ Real-time collaboration works
- ✅ Mobile can use nodeFactory

### Performance Requirements
- ✅ Load time unchanged or better
- ✅ No memory leaks
- ✅ 60 FPS with 50+ objects
- ✅ Auto-save < 200ms

### Team Requirements
- ✅ Frontend team approves
- ✅ Backend team approves API contracts
- ✅ Mobile team can integrate
- ✅ Documentation complete

---

## 🔄 Rollback Plan

### If Critical Issues Arise

**Immediate Rollback (< 5 minutes):**
```bash
git revert HEAD~1
git push origin main --force-with-lease
```

**Partial Rollback (keep improvements):**
```bash
# Revert specific commits
git revert <bad-commit-hash>
git push origin main
```

**Full Rollback (nuclear option):**
```bash
# Restore backup
git checkout backup-branch
git merge --strategy=ours main
git push origin main
```

### Rollback Triggers
- Critical bug affecting > 50% users
- Data loss or corruption
- Performance regression > 50%
- Security vulnerability
- Cannot fix within 2 hours

---

## 👥 Team Responsibilities

### Frontend Team
- Implement refactoring
- Write unit tests
- Update documentation
- Code reviews

### Backend Team
- Verify API contracts
- Review permission logic
- Test collaboration endpoints
- Monitor performance

### Mobile Team
- Review nodeFactory structure
- Test shared code integration
- Verify data contracts
- Update mobile app

### QA Team
- Test all features
- Household collaboration testing
- Performance testing
- Cross-browser testing

---

## 📚 References

### Key Files
- Current: `src/pages/WhiteboardApp.js` (3,095 lines)
- Pattern: `src/contexts/AuthContext.js`
- Database: `migrations/20251103_create_whiteboard_tables.sql`
- API: `hungie_server.py` whiteboard routes

### Related Documents
- `WHITEBOARD_CODE_QUALITY_AUDIT.md` - Problem analysis
- `V1_REMOVAL_IMPACT_ANALYSIS.md` - V1 vs V2 analysis
- `WHITEBOARD_V2_AUDIT.md` - System audit

---

## 📞 Contact & Escalation

### Questions During Migration
- Architecture questions: See this document
- Auth issues: Check `AuthContext.js` pattern
- API questions: Backend team
- Permission issues: See permissions matrix above

### Decision Makers
- Frontend architecture: Frontend lead
- API changes: Backend lead
- Timeline changes: Project manager

---

**Document Status:** ✅ Ready for Review  
**Next Step:** Team review and approval  
**Target Start Date:** TBD  
**Estimated Completion:** 4 weeks from start

