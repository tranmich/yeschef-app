# Whiteboard Frontend Fix - Implementation Plan
**Date:** November 24, 2025  
**Priority:** HIGH  
**Estimated Time:** 2-3 days within Week 1-2 of refactoring

---

## 🎯 What We're Fixing

**Problem:** Frontend duplicates recipe data instead of linking to shared data  
**Impact:** Data sync issues, memory waste, no single source of truth  
**Solution:** Implement recipe cache + clean node structure

---

## 📅 WHEN to Fix

### Integration with Refactoring Timeline

**Week 1, Day 2-3** (After Context Setup, During Node Factory Creation)

```
Week 1 Schedule:
├── Day 1: WhiteboardContext.js ✅
├── Day 2: Add recipeCache to context 🔧 FIX HERE
├── Day 3: nodeFactory.js with clean structure 🔧 FIX HERE
├── Day 4: useRecipeNodes.js
└── Day 5: Testing
```

**Why This Timing?**
- Context already created (Day 1)
- Before extracting hooks (Day 4+)
- Minimal disruption to existing code
- Can test immediately (Day 5)

---

## 📍 WHERE to Fix

### Files to Create/Modify

```
Week 1, Day 2-3:
1. ✏️ Modify: src/features/whiteboard/contexts/WhiteboardContext.js
   - Add recipeCache state
   - Add batch fetch function
   
2. 🆕 Create: src/features/whiteboard/services/nodeFactory.js
   - Clean node creation (no duplicates)
   
3. ✏️ Modify: src/features/whiteboard/hooks/useWhiteboardData.js
   - Load recipes into cache
   
4. ✏️ Modify: src/components/whiteboard/nodes/RecipeCardNode.js
   - Read from cache instead of node.data
   
5. ✏️ Modify: src/pages/WhiteboardApp.js
   - Use nodeFactory
   - Remove duplicate data creation
```

---

## 🔧 HOW to Fix - Step by Step

### Step 1: Add Recipe Cache to Context (Day 2 - 1 hour)

**File:** `src/features/whiteboard/contexts/WhiteboardContext.js`

**What to Add:**
```javascript
export function WhiteboardProvider({ children, whiteboardId, householdId }) {
  // Existing state...
  const [nodes, setNodes] = useState([]);
  
  // 🆕 ADD: Recipe cache
  const [recipeCache, setRecipeCache] = useState({});
  const [groceryCache, setGroceryCache] = useState({});
  const [mealPlanCache, setMealPlanCache] = useState({});
  
  // 🆕 ADD: Batch fetch recipes
  const loadRecipes = useCallback(async (recipeIds) => {
    if (recipeIds.length === 0) return;
    
    try {
      console.log('📚 Batch fetching recipes:', recipeIds);
      
      // Batch fetch from API
      const response = await apiCall(
        `/api/v2/recipes?ids=${recipeIds.join(',')}`
      );
      
      const recipes = response.recipes || response.data || [];
      
      // Build cache { recipe_id: recipe_data }
      const cache = {};
      recipes.forEach(recipe => {
        cache[recipe.id] = recipe;
      });
      
      setRecipeCache(prev => ({ ...prev, ...cache }));
      console.log('✅ Recipe cache updated:', Object.keys(cache).length, 'recipes');
      
    } catch (error) {
      console.error('❌ Failed to load recipes:', error);
    }
  }, []);
  
  // 🆕 ADD: Get recipe from cache
  const getRecipe = useCallback((recipeId) => {
    return recipeCache[recipeId] || null;
  }, [recipeCache]);
  
  const value = {
    // Existing...
    nodes, setNodes,
    
    // 🆕 ADD to value
    recipeCache,
    groceryCache,
    mealPlanCache,
    loadRecipes,
    getRecipe,
  };
  
  return (
    <WhiteboardContext.Provider value={value}>
      {children}
    </WhiteboardContext.Provider>
  );
}
```

**Changes:**
- ✅ Add `recipeCache` state
- ✅ Add `loadRecipes()` function for batch fetching
- ✅ Add `getRecipe()` helper
- ✅ Export in context value

**Test:**
```javascript
// In any component
const { recipeCache, getRecipe } = useWhiteboard();
const recipe = getRecipe(123);
console.log(recipe?.title); // Should work
```

---

### Step 2: Create Clean Node Factory (Day 2-3 - 2 hours)

**File:** `src/features/whiteboard/services/nodeFactory.js` (NEW FILE)

**Full Implementation:**
```javascript
/**
 * Node Factory - Single source of truth for node creation
 * Creates nodes with ONLY links + visual properties (NO data duplication)
 */

// ==========================================
// RECIPE NODES
// ==========================================

export function createRecipeNode(recipeId, options = {}) {
  if (!recipeId) {
    throw new Error('createRecipeNode requires recipeId');
  }
  
  return {
    id: options.id || `recipe-${recipeId}`,
    type: 'recipeCard',
    position: options.position || { x: 200, y: 150 },
    data: {
      // ✅ ONLY store link + visual properties
      object_id: options.objectId,      // wbo.id (if saved)
      recipe_id: recipeId,              // ✅ Link to recipes table
      
      // Visual properties
      tags: options.tags || [],
      backgroundColor: options.backgroundColor || '#FFFFFF',
      
      // Comment data
      commentCount: options.commentCount || 0,
      hasNewComments: options.hasNewComments || false,
      
      // Handlers (passed from hook)
      onClick: options.onClick,
      onDelete: options.onDelete,
      onTagsChange: options.onTagsChange,
      onTagFilterClick: options.onTagFilterClick,
      onColorChange: options.onColorChange,
    }
  };
}

/**
 * Validate recipe node structure
 */
export function validateRecipeNode(node) {
  if (!node.data?.recipe_id) {
    console.error('❌ Invalid recipe node: missing recipe_id', node);
    return false;
  }
  if (node.data.recipe) {
    console.warn('⚠️ Recipe node contains duplicate recipe data', node);
  }
  return true;
}

// ==========================================
// GROCERY LIST NODES
// ==========================================

export function createGroceryListNode(listId, options = {}) {
  return {
    id: options.id || `grocery-${listId}`,
    type: 'groceryListNode',
    position: options.position || { x: 200, y: 150 },
    data: {
      object_id: options.objectId,
      list_id: listId,              // ✅ Link to grocery_lists table
      commentCount: options.commentCount || 0,
      onDelete: options.onDelete,
    }
  };
}

// ==========================================
// MEAL PLAN NODES
// ==========================================

export function createMealPlanNode(mealPlanId, options = {}) {
  return {
    id: options.id || `meal-plan-${mealPlanId}`,
    type: 'mealPlanContainer',
    position: options.position || { x: 200, y: 150 },
    width: options.width || 400,
    height: options.height || 500,
    data: {
      object_id: options.objectId,
      meal_plan_id: mealPlanId,    // ✅ Link to meal_plans table
      backgroundColor: options.backgroundColor || '#D1FAE5',
      commentCount: options.commentCount || 0,
      onNameChange: options.onNameChange,
      onColorChange: options.onColorChange,
      onDelete: options.onDelete,
    }
  };
}

// ==========================================
// NOTE NODES (no external link - freeform)
// ==========================================

export function createNoteNode(options = {}) {
  return {
    id: options.id || `note-${Date.now()}`,
    type: 'note',
    position: options.position || { x: 200, y: 150 },
    data: {
      object_id: options.objectId,
      name: options.name || 'Untitled Note',
      content: options.content || '<p></p>',
      backgroundColor: options.backgroundColor || '#FEF3C7',
      fontSize: options.fontSize || 18,
      commentCount: options.commentCount || 0,
      createdBy: options.createdBy || 'Unknown',
      onDelete: options.onDelete,
      onSave: options.onSave,
    }
  };
}
```

**Changes:**
- ✅ Nodes store ONLY `recipe_id` (not full recipe)
- ✅ Nodes store ONLY `list_id` (not full list)
- ✅ Nodes store ONLY `meal_plan_id` (not full plan)
- ✅ No duplicate fields
- ✅ Clean, testable functions

**Test:**
```javascript
import { createRecipeNode } from './nodeFactory';

const node = createRecipeNode(123, {
  position: { x: 100, y: 200 },
  tags: ['dinner'],
  onClick: handleClick
});

console.log(node.data.recipe_id); // 123 ✅
console.log(node.data.recipe);     // undefined ✅
console.log(node.data.name);       // undefined ✅
```

---

### Step 3: Update Data Loading Hook (Day 3 - 1 hour)

**File:** `src/features/whiteboard/hooks/useWhiteboardData.js`

**What to Change:**
```javascript
import { useEffect } from 'react';
import { useWhiteboard } from '../contexts/WhiteboardContext';
import { createRecipeNode, createGroceryListNode } from '../services/nodeFactory';
import whiteboardAPI from '../services/whiteboardAPI';

export function useWhiteboardData() {
  const { 
    whiteboardId,
    setWhiteboard,
    setNodes,
    setLoading,
    setError,
    loadRecipes,         // 🆕 Use from context
    setCommentCounts 
  } = useWhiteboard();
  
  useEffect(() => {
    loadWhiteboard();
  }, [whiteboardId]);
  
  async function loadWhiteboard() {
    try {
      setLoading(true);
      
      // 1. Load whiteboard metadata
      const response = await whiteboardAPI.getWhiteboard(whiteboardId);
      setWhiteboard(response.whiteboard);
      
      // 2. Load objects
      const objects = response.objects || [];
      
      // 3. Extract unique IDs
      const recipeIds = [...new Set(
        objects
          .filter(obj => obj.rid)
          .map(obj => obj.rid)
      )];
      
      const groceryIds = [...new Set(
        objects
          .filter(obj => obj.gid)
          .map(obj => obj.gid)
      )];
      
      // 4. 🆕 Batch fetch recipes into cache
      if (recipeIds.length > 0) {
        await loadRecipes(recipeIds);
      }
      
      // TODO: Load grocery lists, meal plans similarly
      
      // 5. Create nodes (NO recipe data, just IDs)
      const nodes = objects.map(obj => {
        if (obj.rid) {
          // 🆕 Use factory - only stores recipe_id
          return createRecipeNode(obj.rid, {
            id: `recipe-${obj.rid}`,
            objectId: obj.id,
            position: parsePosition(obj.position),
            tags: obj.tags || [],
            backgroundColor: obj.background_color,
            commentCount: obj.comment_count || 0,
            onClick: handleRecipeClick,
            onDelete: handleDeleteRecipe,
            // ... other handlers
          });
        }
        
        if (obj.gid) {
          return createGroceryListNode(obj.gid, {
            objectId: obj.id,
            position: parsePosition(obj.position),
            onDelete: handleDeleteGroceryList,
          });
        }
        
        // ... other object types
        
        return null;
      }).filter(Boolean);
      
      setNodes(nodes);
      
      // 6. Load comment counts
      const counts = await loadCommentCounts(whiteboardId);
      setCommentCounts(counts);
      
      setLoading(false);
      
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  }
  
  function parsePosition(position) {
    if (Array.isArray(position)) {
      return { x: position[0] || 0, y: position[1] || 0 };
    }
    return position || { x: 0, y: 0 };
  }
}

function handleRecipeClick(recipeId) {
  // Handler will be passed from useRecipeNodes hook
}

function handleDeleteRecipe(nodeId, recipeId, objectId) {
  // Handler will be passed from useRecipeNodes hook
}
```

**Changes:**
- ✅ Extract recipe IDs from objects
- ✅ Batch fetch recipes into cache
- ✅ Use nodeFactory (no duplicate data)
- ✅ Nodes store only IDs

---

### Step 4: Update RecipeCardNode Component (Day 3 - 1 hour)

**File:** `src/components/whiteboard/nodes/RecipeCardNode.js`

**What to Change:**
```javascript
import React from 'react';
import { Handle, Position } from '@xyflow/react';
import { useWhiteboard } from '@/features/whiteboard/contexts/WhiteboardContext';
import './RecipeCardNode.css';

function RecipeCardNode({ id, data, selected }) {
  // 🆕 Get recipe from cache instead of data
  const { getRecipe } = useWhiteboard();
  const recipe = getRecipe(data.recipe_id);
  
  // ❌ OLD: const recipe = data.recipe || {};
  // ❌ OLD: const name = recipe.title || recipe.name || data.name || 'Untitled';
  
  // 🆕 NEW: Read from cache
  const name = recipe?.title || 'Loading...';
  const imageUrl = recipe?.image_url;
  const prepTime = recipe?.prep_time;
  const cookTime = recipe?.cook_time;
  const category = recipe?.category;
  
  // Visual properties from node data (not from recipe)
  const { 
    tags, 
    backgroundColor, 
    commentCount,
    onClick,
    onDelete,
    onTagsChange,
    onColorChange 
  } = data;
  
  if (!recipe) {
    return (
      <div className="recipe-card loading">
        <p>Loading recipe...</p>
      </div>
    );
  }
  
  return (
    <div 
      className={`recipe-card ${selected ? 'selected' : ''}`}
      style={{ backgroundColor }}
    >
      <Handle type="target" position={Position.Top} />
      
      {/* Image */}
      {imageUrl && (
        <img src={imageUrl} alt={name} className="recipe-image" />
      )}
      
      {/* Title */}
      <h3 className="recipe-title">{name}</h3>
      
      {/* Time info */}
      <div className="recipe-info">
        {prepTime && <span>⏱️ {prepTime}m prep</span>}
        {cookTime && <span>🔥 {cookTime}m cook</span>}
      </div>
      
      {/* Category badge */}
      {category && (
        <span className="category-badge">{category}</span>
      )}
      
      {/* Tags */}
      {tags && tags.length > 0 && (
        <div className="recipe-tags">
          {tags.map(tag => (
            <span key={tag} className="tag">{tag}</span>
          ))}
        </div>
      )}
      
      {/* Actions */}
      <div className="recipe-actions">
        <button onClick={() => onClick?.(data.recipe_id)}>
          View Recipe
        </button>
        <button onClick={() => onDelete?.(id, data.recipe_id, data.object_id)}>
          Remove
        </button>
      </div>
      
      {/* Comment badge */}
      {commentCount > 0 && (
        <div className="comment-badge">
          💬 {commentCount}
        </div>
      )}
      
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}

export default RecipeCardNode;
```

**Changes:**
- ✅ Use `getRecipe(data.recipe_id)` instead of `data.recipe`
- ✅ Show loading state while recipe fetches
- ✅ Read visual properties from `data` (tags, colors)
- ✅ No more `data.name`, `data.image_url`, etc.

---

### Step 5: Update WhiteboardApp to Use Factory (Day 3 - 1 hour)

**File:** `src/pages/WhiteboardApp.js`

**Find and Replace (3 locations):**

**Location 1: loadSavedObjects() ~line 800**
```javascript
// ❌ DELETE THIS (lines 795-830):
return {
  id: `recipe-${recipe.id}`,
  type: 'recipeCard',
  position: { x: posX, y: posY },
  data: {
    recipe: { ...recipe, image_url: imageUrl },
    object_id: obj.id,
    recipe_id: recipe.id,
    name: recipe.title || recipe.name,
    image_url: imageUrl,
    prep_time: recipe.prep_time,
    // ... all the duplicate fields
  }
};

// 🆕 REPLACE WITH:
import { createRecipeNode } from '../features/whiteboard/services/nodeFactory';

return createRecipeNode(recipe.id, {
  objectId: obj.id,
  position: { x: posX, y: posY },
  tags: obj.tags || [],
  backgroundColor: obj.background_color || '#FFFFFF',
  commentCount: getCommentCount('recipe', recipe.id),
  onClick: handleRecipeClick,
  onDelete: handleDeleteRecipe,
  onTagsChange: handleTagsChange,
  onTagFilterClick: handleTagFilterClick,
  onColorChange: handleRecipeColorChange
});
```

**Location 2: loadUserRecipes() ~line 900**
```javascript
// ❌ DELETE duplicate node creation

// 🆕 REPLACE WITH factory
const recipeNodes = sortedRecipes.slice(0, 5).map((recipe, idx) => {
  return createRecipeNode(recipe.id, {
    position: { x: 200 + (col * 400), y: 150 + (row * 350) },
    onClick: handleRecipeClick,
    onDelete: handleDeleteRecipe,
    onTagsChange: handleTagsChange,
    onTagFilterClick: handleTagFilterClick,
  });
});
```

**Location 3: handleAddRecipe() ~line 1100** (if exists)
```javascript
// 🆕 Use factory everywhere
const newNode = createRecipeNode(fullRecipe.id, {
  position: dropPosition || { x: 300, y: 300 },
  onClick: handleRecipeClick,
  onDelete: handleDeleteRecipe,
  // ...
});
```

---

### Step 6: Remove Old Data Fetching (Day 3 - 30 min)

**File:** `src/pages/WhiteboardApp.js`

**Find and Remove:**
```javascript
// ❌ DELETE: Individual recipe fetching in loadSavedObjects

// OLD (lines ~650-680):
const recipeIds = savedObjects
  .filter(obj => obj.entity_type === 'recipe')
  .map(obj => obj.entity_id);

const recipePromises = recipeIds.map(id =>
  whiteboardAPI.getWhiteboardRecipe(whiteboardId, id)
);

const recipeResponses = await Promise.all(recipePromises);
const recipeMap = {};
recipeResponses.forEach(r => {
  if (r.recipe) recipeMap[r.recipe.id] = r.recipe;
});

// ✅ REPLACED BY: Batch fetch in useWhiteboardData hook
// Recipes are now in recipeCache, accessed via getRecipe()
```

---

## ✅ Testing Checklist (Day 3 - 1 hour)

### Manual Tests

**Test 1: Recipe Cache**
```javascript
// Open browser console
// Navigate to whiteboard

const { recipeCache } = window.__WHITEBOARD_CONTEXT__;
console.log('Recipe cache:', recipeCache);
// Should see: { 123: {id: 123, title: "...", ...}, 124: {...} }
```

**Test 2: Node Structure**
```javascript
// Check node data
const { nodes } = window.__WHITEBOARD_CONTEXT__;
const firstRecipeNode = nodes.find(n => n.type === 'recipeCard');
console.log('Node data:', firstRecipeNode.data);

// ✅ Should have: recipe_id
// ❌ Should NOT have: recipe, name, image_url (duplicates)
```

**Test 3: Display**
- [ ] Recipe cards display correctly
- [ ] Images load
- [ ] Titles show
- [ ] Time info appears
- [ ] Tags display

**Test 4: Sync**
- [ ] Edit recipe in MainApp (change title)
- [ ] Refresh whiteboard
- [ ] Should show NEW title ✅

**Test 5: Memory**
```javascript
// Check memory usage
performance.memory.usedJSHeapSize / 1024 / 1024; // MB
// Should be ~40-50% less than before
```

---

## 📊 Before & After Comparison

### Code Comparison

**Before (WhiteboardApp.js ~line 800):**
```javascript
// ❌ 35 lines of duplicate data
data: {
  recipe: { ...recipe, image_url: imageUrl },  // Full object
  object_id: obj.id,
  recipe_id: recipe.id,                        // Duplicate
  name: recipe.title || recipe.name,           // Duplicate
  image_url: imageUrl,                         // Duplicate
  prep_time: recipe.prep_time,                 // Duplicate
  cook_time: recipe.cook_time,                 // Duplicate
  total_time: recipe.total_time,               // Duplicate
  category: recipe.category,                   // Duplicate
  tags: obj.tags || [],
  backgroundColor: obj.background_color || '#FFFFFF',
  commentCount: getCommentCount('recipe', recipe.id),
  onClick: handleRecipeClick,
  onDelete: handleDeleteRecipe,
  // ... more
}
```

**After (using nodeFactory):**
```javascript
// ✅ 8 lines, clean
createRecipeNode(recipe.id, {
  objectId: obj.id,
  position: { x: posX, y: posY },
  tags: obj.tags || [],
  backgroundColor: obj.background_color,
  commentCount: getCommentCount('recipe', recipe.id),
  onClick: handleRecipeClick,
  onDelete: handleDeleteRecipe,
})
```

**Savings:** 27 lines removed per location × 3 locations = **81 lines removed**

---

### Memory Comparison

**Before:**
```
100 recipes × 2.5 KB per node = 250 KB
```

**After:**
```
100 recipes × 0.1 KB per node = 10 KB (nodes)
100 recipes × 1.5 KB in cache = 150 KB (cache)
Total: 160 KB

Savings: 90 KB (36%)
```

---

## 🚨 Rollback Plan

If something breaks:

**Quick Rollback:**
```bash
# Revert specific commit
git log --oneline  # Find commit hash
git revert <commit-hash>
git push origin main
```

**Manual Rollback:**
1. Comment out `recipeCache` in WhiteboardContext
2. Restore old node creation in WhiteboardApp.js
3. Restore old RecipeCardNode component
4. Test that whiteboard works again
5. Debug and retry

---

## 📝 Commit Strategy

**Day 2:**
```bash
git add src/features/whiteboard/contexts/WhiteboardContext.js
git commit -m "feat: Add recipe cache to WhiteboardContext

- Add recipeCache state
- Add loadRecipes batch fetch
- Add getRecipe helper
- Prepare for clean node structure"
git push origin main
```

**Day 3 - Part 1:**
```bash
git add src/features/whiteboard/services/nodeFactory.js
git commit -m "feat: Create node factory with clean structure

- createRecipeNode stores only recipe_id
- createGroceryListNode stores only list_id
- No data duplication
- Validation functions included"
git push origin main
```

**Day 3 - Part 2:**
```bash
git add src/features/whiteboard/hooks/useWhiteboardData.js
git add src/components/whiteboard/nodes/RecipeCardNode.js
git add src/pages/WhiteboardApp.js
git commit -m "refactor: Use node factory and recipe cache

- useWhiteboardData batch fetches recipes
- RecipeCardNode reads from cache
- WhiteboardApp uses factory everywhere
- Remove duplicate data creation
- Fixes data sync issues
- Reduces memory by ~40%"
git push origin main
```

---

## 🎯 Success Criteria

After implementation, verify:

- [ ] ✅ No `data.recipe` in nodes
- [ ] ✅ No duplicate fields (name, image_url, etc.)
- [ ] ✅ recipeCache populated on load
- [ ] ✅ Recipe cards display correctly
- [ ] ✅ Edit recipe in MainApp → whiteboard syncs
- [ ] ✅ Memory usage reduced
- [ ] ✅ No console errors
- [ ] ✅ Tests pass

---

## 📞 Support

**If you encounter issues:**

1. Check browser console for errors
2. Verify `recipeCache` is populated
3. Check node structure (no duplicates)
4. Verify API responses
5. Use rollback plan if needed

**Need help?** Reference:
- `WHITEBOARD_DATA_FLOW_ANALYSIS.md` - Problem analysis
- `WHITEBOARD_DECOMPOSITION_PLAN.md` - Full refactoring plan
- This document - Implementation details

