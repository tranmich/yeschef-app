# Whiteboard V2 System Audit
**Date:** November 24, 2025  
**Issue:** Inconsistent naming and data structures between v1/v2 causing fragile integrations

## 🚨 Critical Issues Found

### 1. Recipe Data Structure Inconsistencies

#### API Response (v2)
```javascript
{
  id: 2772,
  title: "Recipe Name",        // NOT "name"!
  image_url: "...",
  prep_time: 20,               // NOT "prep_time_minutes"
  cook_time: 30,
  category: "dinner",
  created_by: 11,
  created_at: "..."
}
```

#### Component Expectations
```javascript
// RecipeCardNode.js expects:
const recipe = data.recipe || {};
const recipeName = recipe.title || recipe.name || 'Unnamed Recipe';

// WHY checking both? Because v1 used "name", v2 uses "title"
```

#### WhiteboardApp Creates
```javascript
data: {
  recipe: { ...recipe, image_url: imageUrl },  // Full object
  recipe_id: recipe.id,                         // Duplicate
  name: recipe.title || recipe.name,            // Duplicate
  image_url: imageUrl,                          // Duplicate
  prep_time: recipe.prep_time,                  // Duplicate
  // ... MORE DUPLICATES
}
```

**PROBLEM:** Data is duplicated 3 ways (recipe object, individual props, backward compat)

---

### 2. Component Type Naming Chaos

| Location | Name Used | Type |
|----------|-----------|------|
| Database `whiteboard_objects.object_type` | `'rc'` | String code |
| React Flow `node.type` | `'recipeCard'` | camelCase |
| Component Import | `RecipeCardNode` | PascalCase |
| nodeTypes config | `recipeCard:` | camelCase |

**PROBLEM:** 4 different naming conventions for the same thing!

---

### 3. Handler Function Mismatches

#### LoadSavedObjects (existing whiteboards)
```javascript
onClick: handleRecipeClick,          // ✅ Correct
onDelete: handleDeleteRecipe,        // ✅ Correct
onTagsChange: handleTagsChange,      // ✅ Correct
```

#### LoadUserRecipes (new whiteboards)
```javascript
onClick: (id) => { console.log('🍕 Clicked recipe:', id); },  // ❌ STUB!
onDelete: handleDeleteRecipe,        // ✅ Correct
onTagsChange: handleTagsChange,      // ✅ Correct
```

**PROBLEM:** Different code paths assign different handlers!

---

### 4. Object ID Confusion

```javascript
// Database has:
whiteboard_objects.id = 123           // object DB ID
whiteboard_objects.related_id = 2772  // recipe ID

// Frontend creates:
node.id = 'recipe-2772'               // String with prefix
node.data.object_id = 123             // DB object ID
node.data.recipe_id = 2772            // Recipe ID
node.data.recipe.id = 2772            // SAME as recipe_id (duplicate)
```

**PROBLEM:** 3 different IDs for same recipe, easy to mix up!

---

### 5. Household vs Personal Recipe Loading

```javascript
// loadSavedObjects (household context):
await whiteboardAPI.getWhiteboardRecipe(whiteboardId, recipeId);
// Returns: recipe from ANY household member

// loadUserRecipes (personal context):
await apiCall(`/api/v2/recipes`);
// Returns: ONLY current user's recipes

// handleAddRecipe (adding from picker):
// Uses personal recipes but saves to household whiteboard
```

**PROBLEM:** Mixed contexts - sometimes household-aware, sometimes not!

---

## 🎯 Root Causes

### 1. Incomplete V2 Migration
- V1 → V2 API migration left backward compatibility code everywhere
- Components checking both `recipe.title` and `recipe.name`
- Handlers sometimes use v1 endpoints, sometimes v2

### 2. No Single Source of Truth
- Recipe data duplicated across multiple properties
- Same concept named 4 different ways
- No centralized type definitions

### 3. Multiple Code Paths
- `loadSavedObjects` vs `loadUserRecipes` vs `handleAddRecipe`
- Each creates nodes differently
- Easy for one path to get out of sync

### 4. Component Duplication
- Had TWO `RecipeCardNode` components with different APIs
- Imported wrong one for months
- No one noticed until household sharing exposed it

---

## ✅ Recommended Solutions

### Phase 1: Standardize Data Structures (URGENT)

#### Create TypeScript Interfaces
```typescript
// types/whiteboard.ts
interface Recipe {
  id: number;
  title: string;  // V2 standard
  image_url: string;
  prep_time: number;  // minutes
  cook_time: number;
  category: string;
  created_by: number;
}

interface RecipeNodeData {
  recipe: Recipe;  // Single source of truth
  object_id?: number;  // DB object ID (optional for new nodes)
  tags: string[];
  backgroundColor: string;
  commentCount: number;
  onClick: (recipeId: number) => void;
  onDelete: (nodeId: string, recipeId: number, objectId?: number) => void;
  onTagsChange: (nodeId: string, tags: string[]) => void;
}
```

#### Create Helper Functions
```javascript
// utils/whiteboardHelpers.js

/**
 * SINGLE function to create recipe nodes
 * Use this EVERYWHERE - no more inconsistency!
 */
export function createRecipeNode(recipe, position, options = {}) {
  return {
    id: `recipe-${recipe.id}`,
    type: 'recipeCard',
    position: { x: position.x, y: position.y },
    data: {
      recipe: {
        id: recipe.id,
        title: recipe.title || recipe.name,  // Handle v1 fallback
        image_url: fixImageUrl(recipe.image_url),
        prep_time: recipe.prep_time || recipe.prep_time_minutes,
        cook_time: recipe.cook_time || recipe.cook_time_minutes,
        category: recipe.category,
        created_by: recipe.created_by
      },
      object_id: options.objectId,
      tags: options.tags || [],
      backgroundColor: options.backgroundColor || '#FFFFFF',
      commentCount: options.commentCount || 0,
      hasNewComments: false,
      onClick: options.onClick || handleRecipeClick,
      onDelete: options.onDelete || handleDeleteRecipe,
      onTagsChange: options.onTagsChange || handleTagsChange,
      onTagFilterClick: options.onTagFilterClick || handleTagFilterClick,
      onColorChange: options.onColorChange || handleRecipeColorChange
    }
  };
}

/**
 * Normalize recipe data from API
 */
export function normalizeRecipe(apiRecipe) {
  return {
    id: apiRecipe.id,
    title: apiRecipe.title || apiRecipe.name,
    image_url: fixImageUrl(apiRecipe.image_url),
    prep_time: apiRecipe.prep_time || apiRecipe.prep_time_minutes || 0,
    cook_time: apiRecipe.cook_time || apiRecipe.cook_time_minutes || 0,
    total_time: apiRecipe.total_time,
    category: apiRecipe.category,
    created_by: apiRecipe.created_by,
    created_by_name: apiRecipe.created_by_name
  };
}
```

### Phase 2: Unify Code Paths

#### Before (3 different ways):
```javascript
loadSavedObjects()    → creates nodes one way
loadUserRecipes()     → creates nodes different way  
handleAddRecipe()     → creates nodes third way
```

#### After (single way):
```javascript
// ALL use the same helper
const node = createRecipeNode(normalizeRecipe(recipe), position, {
  objectId: savedObject?.id,
  tags: savedObject?.tags || [],
  onClick: handleRecipeClick,
  // ...
});
```

### Phase 3: Standardize Naming

| Concept | Standard Name | Everywhere |
|---------|--------------|------------|
| Database code | `'rc'` | `whiteboard_objects.object_type` |
| React Flow type | `'recipeCard'` | `node.type`, `nodeTypes` |
| Component | `RecipeCardNode` | Imports, files |
| Recipe field | `title` | API v2, prefer over `name` |
| Time field | `prep_time` (minutes) | Prefer over `prep_time_minutes` |

### Phase 4: Add Validation

```javascript
// utils/validators.js
export function validateRecipeNode(node) {
  const errors = [];
  
  if (!node.data?.recipe) {
    errors.push('Missing recipe object');
  }
  if (!node.data?.recipe?.id) {
    errors.push('Missing recipe.id');
  }
  if (!node.data?.onClick || typeof node.data.onClick !== 'function') {
    errors.push('Invalid or missing onClick handler');
  }
  
  if (errors.length > 0) {
    console.error('❌ Invalid recipe node:', node.id, errors);
    return false;
  }
  return true;
}

// Use in WhiteboardApp:
const newNodes = recipeNodes.filter(validateRecipeNode);
setNodes(newNodes);
```

---

## 📊 Impact Analysis

### What Causes "Glass House" Fragility?

1. **No Type Safety** → Easy to pass wrong data structure
2. **Duplicated Data** → Data can get out of sync
3. **Multiple Code Paths** → One path breaks, others work (false confidence)
4. **Backward Compat Everywhere** → Code checks 3 ways to do same thing
5. **Component Duplication** → Imported wrong component for months

### Why Guest Info Broke Recipe Cards

```
1. Added household-aware recipe loading
   ↓
2. Changed API call to use whiteboard context
   ↓
3. API returned v2 recipe structure
   ↓
4. But was using OLD RecipeCardNode component
   ↓
5. OLD component expected individual props (name, image_url)
   ↓
6. NEW data had recipe.title, recipe.image_url
   ↓
7. Component received wrong data structure → BLANK CARDS
```

**The real issue:** No validation, no type safety, wrong component import hidden for months.

---

## 🚀 Implementation Plan

### Week 1: Foundation
- [ ] Create `types/whiteboard.ts` with interfaces
- [ ] Create `utils/whiteboardHelpers.js` with helpers
- [ ] Create `utils/validators.js` with validation

### Week 2: Migration
- [ ] Replace `loadSavedObjects` to use helpers
- [ ] Replace `loadUserRecipes` to use helpers
- [ ] Replace `handleAddRecipe` to use helpers
- [ ] Add validation at node creation

### Week 3: Cleanup
- [ ] Remove duplicate data properties
- [ ] Remove backward compatibility checks
- [ ] Add JSDoc comments everywhere
- [ ] Update tests

### Week 4: Testing
- [ ] Test all whiteboard operations
- [ ] Test household sharing
- [ ] Test recipe loading/adding
- [ ] Load testing with 50+ recipes

---

## 📝 Notes

- **Why TypeScript?** Type safety prevents passing wrong data structures
- **Why Helpers?** Single source of truth, one place to fix bugs
- **Why Validation?** Catch errors immediately, not 3 bugs later
- **Risk Level:** Medium - requires touching core whiteboard code
- **Time Estimate:** 2-3 weeks for full cleanup

---

## 🎯 Priority Fixes (Do First)

1. ✅ **DONE:** Fix RecipeCardNode import (use correct component)
2. ✅ **DONE:** Fix handleRecipeClick in loadUserRecipes
3. ⚠️ **TODO:** Create `createRecipeNode` helper
4. ⚠️ **TODO:** Create `normalizeRecipe` helper
5. ⚠️ **TODO:** Replace all 3 code paths to use helpers
6. ⚠️ **TODO:** Add validation before setNodes()

