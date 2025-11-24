# Whiteboard Data Flow Analysis
**Date:** November 24, 2025  
**Question:** Is the whiteboard reading shared data or duplicating it?

---

## 🎯 Expected Behavior

**Whiteboard SHOULD:**
- ✅ **Read:** Link to existing data (recipes, grocery lists, meal plans)
- ✅ **Write:** Save only positions, tags, and visual properties
- ✅ **Never:** Duplicate recipe/grocery/meal plan data

**Database Design (Correct):**
```sql
-- wbo table stores ONLY links + visual properties
wbo (
  id              -- Object ID
  wid             -- Whiteboard ID
  t               -- Type ('rc', 'gl', 'mp', 'nt')
  rid             -- Recipe ID (foreign key) ✅ LINK ONLY
  gid             -- Grocery List ID (foreign key) ✅ LINK ONLY
  mid             -- Meal Plan ID (foreign key) ✅ LINK ONLY
  p               -- Position [x, y, w, h, z]
  tags            -- Organization tags
  -- NO recipe data stored here!
)
```

---

## ✅ CORRECT: Backend Implementation

### Backend DOES Read + Link (Correct)

**File:** `app/api/v2/whiteboards.py:679`

```python
# INSERT only stores LINKS, not data
INSERT INTO wbo (wid, t, rid, gid, mid, p, c, tags, cby, ca, ua)
VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s, %s, ...)

# rid = recipe_id (link to recipes table) ✅
# gid = grocery_list_id (link to grocery_lists table) ✅
# mid = meal_plan_id (link to meal_plans table) ✅
# NO recipe.title, recipe.ingredients stored!
```

**Backend correctly:**
- Stores only `rid` (recipe ID link)
- Stores only `gid` (grocery list ID link)
- Stores only `mid` (meal plan ID link)
- Stores position, tags, visual properties
- **Does NOT duplicate recipe data**

---

## ⚠️ PROBLEM: Frontend Implementation

### Frontend DUPLICATES Data (Incorrect)

**File:** `frontend/src/pages/WhiteboardApp.js:800-830`

```javascript
// LINE 800-830: loadSavedObjects()
return {
  id: `recipe-${recipe.id}`,
  type: 'recipeCard',
  position: { x: posX, y: posY },
  data: {
    recipe: {                        // ❌ FULL recipe object
      ...recipe,                     // ❌ All recipe fields
      image_url: imageUrl
    },
    object_id: obj.id,
    recipe_id: recipe.id,             // ❌ DUPLICATE
    name: recipe.title || recipe.name, // ❌ DUPLICATE
    image_url: imageUrl,              // ❌ DUPLICATE
    prep_time: recipe.prep_time,      // ❌ DUPLICATE
    cook_time: recipe.cook_time,      // ❌ DUPLICATE
    total_time: recipe.total_time,    // ❌ DUPLICATE
    category: recipe.category,        // ❌ DUPLICATE
    tags: obj.tags || [],
    backgroundColor: obj.background_color || '#FFFFFF',
    // ... handlers
  }
};
```

**Problems:**
1. **Stores full recipe object** in `data.recipe`
2. **ALSO duplicates** `recipe_id`, `name`, `image_url`, `prep_time`, `cook_time`, etc.
3. **Same data 3 times:**
   - `data.recipe.title`
   - `data.name`
   - `recipe.title` (original)

4. **Memory waste:** 100 recipes = 3x memory usage

5. **State management nightmare:**
   - If recipe changes in database, whiteboard is out of sync
   - Have to update recipe in multiple places
   - No single source of truth

---

## 🔍 Data Flow Comparison

### Backend (Correct) ✅

```
User adds recipe to canvas
    ↓
Backend saves:
    wbo.rid = 123 (link to recipes.id)
    wbo.p = [100, 200, 300, 400, 0]
    wbo.tags = ['dinner']
    ↓
Backend fetches recipe separately:
    SELECT * FROM recipes WHERE id = 123
    ↓
Returns:
    {
      object: { id: 456, rid: 123, position: [...] },
      recipe: { id: 123, title: "Pasta", ... }
    }
```

**Clean separation:** Object metadata + Linked recipe data

---

### Frontend (Incorrect) ❌

```
Frontend receives from backend:
    {
      object: { id: 456, rid: 123, position: [...] },
      recipe: { id: 123, title: "Pasta", ... }
    }
    ↓
Frontend creates node:
    {
      data: {
        recipe: { id: 123, title: "Pasta", ... },  // Full copy
        recipe_id: 123,                             // Duplicate
        name: "Pasta",                              // Duplicate
        image_url: "...",                           // Duplicate
        prep_time: 30,                              // Duplicate
        // ... more duplicates
      }
    }
    ↓
Stored in React state (nodes array)
```

**Problem:** Data duplicated 3x in memory

---

## 💥 Real-World Impact

### Scenario: User edits recipe in MainApp

```
1. User opens recipe "Chicken Pasta" in MainApp
2. Changes title to "Creamy Chicken Pasta"
3. Saves to database
   ↓
   recipes.title = "Creamy Chicken Pasta" ✅ Updated
   ↓
4. User returns to whiteboard
   ↓
   whiteboard still shows "Chicken Pasta" ❌ OUT OF SYNC
```

**Why?** Because whiteboard stored a COPY of recipe data, not a link.

---

### Scenario: Mobile updates recipe

```
1. Mobile app edits recipe ingredients
2. Saves to backend (recipes table updated)
3. Frontend whiteboard loads
   ↓
   Shows OLD ingredients from cached node data ❌
```

**Why?** Whiteboard doesn't re-fetch recipe data on load, uses stale copy.

---

## ✅ CORRECT Implementation

### What Frontend SHOULD Do

**File:** `nodeFactory.js` (proposed)

```javascript
export function createRecipeNode(recipe, options = {}) {
  return {
    id: `recipe-${recipe.id}`,
    type: 'recipeCard',
    position: options.position || { x: 200, y: 150 },
    data: {
      // ✅ ONLY store link + visual properties
      object_id: options.objectId,
      recipe_id: recipe.id,              // ✅ Link only
      tags: options.tags || [],
      backgroundColor: options.backgroundColor || '#FFFFFF',
      commentCount: options.commentCount || 0,
      
      // ✅ Handlers
      onClick: options.onClick,
      onDelete: options.onDelete,
      onTagsChange: options.onTagsChange,
    }
  };
}
```

**NO `data.recipe` object!**  
**NO duplicate fields!**

---

### How to Get Recipe Data?

**Option 1: Fetch on demand**
```javascript
// RecipeCardNode.jsx
function RecipeCardNode({ data }) {
  const [recipe, setRecipe] = useState(null);
  
  useEffect(() => {
    // Fetch recipe when node renders
    apiCall(`/api/v2/recipes/${data.recipe_id}`)
      .then(r => setRecipe(r.recipe));
  }, [data.recipe_id]);
  
  return (
    <div className="recipe-card">
      <h3>{recipe?.title || 'Loading...'}</h3>
      <img src={recipe?.image_url} />
      <p>Prep: {recipe?.prep_time} min</p>
    </div>
  );
}
```

**Problem:** 100 recipes = 100 API calls (slow)

---

**Option 2: Context/Store (RECOMMENDED)**
```javascript
// WhiteboardContext.js
const WhiteboardContext = createContext();

export function WhiteboardProvider({ children }) {
  const [nodes, setNodes] = useState([]);
  const [recipeCache, setRecipeCache] = useState({}); // Cache recipes
  
  // Fetch recipes once when loading whiteboard
  const loadWhiteboard = async (whiteboardId) => {
    const wb = await whiteboardAPI.getWhiteboard(whiteboardId);
    const objects = wb.objects;
    
    // Get unique recipe IDs
    const recipeIds = objects
      .filter(o => o.rid)
      .map(o => o.rid);
    
    // Batch fetch all recipes
    const recipes = await apiCall(`/api/v2/recipes?ids=${recipeIds.join(',')}`);
    
    // Build cache { recipe_id: recipe_data }
    const cache = {};
    recipes.forEach(r => { cache[r.id] = r; });
    setRecipeCache(cache);
    
    // Create nodes (no recipe data stored)
    const nodes = objects.map(obj => createRecipeNode(cache[obj.rid], {
      objectId: obj.id,
      position: obj.position,
      tags: obj.tags,
    }));
    setNodes(nodes);
  };
  
  return (
    <WhiteboardContext.Provider value={{ nodes, recipeCache }}>
      {children}
    </WhiteboardContext.Provider>
  );
}
```

```javascript
// RecipeCardNode.jsx
function RecipeCardNode({ data }) {
  const { recipeCache } = useWhiteboard();
  const recipe = recipeCache[data.recipe_id]; // ✅ Get from cache
  
  return (
    <div className="recipe-card">
      <h3>{recipe?.title}</h3>
      <img src={recipe?.image_url} />
      <p>Prep: {recipe?.prep_time} min</p>
    </div>
  );
}
```

**Benefits:**
- ✅ Single source of truth (recipeCache)
- ✅ One batch API call
- ✅ No duplicated data
- ✅ Easy to refresh (reload cache)
- ✅ Consistent across app

---

## 📊 Memory Comparison

### Current (Incorrect)
```
100 recipes on whiteboard:

nodes array: [
  { data: { recipe: {...}, recipe_id: 1, name: "...", image_url: "..." } },
  { data: { recipe: {...}, recipe_id: 2, name: "...", image_url: "..." } },
  // ... 100 times
]

Memory per recipe: ~2-3 KB (full object + duplicates)
Total: 200-300 KB
```

---

### Proposed (Correct)
```
100 recipes on whiteboard:

nodes array: [
  { data: { recipe_id: 1, tags: [], backgroundColor: "#fff" } },
  { data: { recipe_id: 2, tags: [], backgroundColor: "#fff" } },
  // ... 100 times (TINY objects)
]

recipeCache: {
  1: { id: 1, title: "...", image_url: "..." },
  2: { id: 2, title: "...", image_url: "..." },
  // ... 100 times (stored ONCE)
}

Memory per node: ~0.1 KB (just IDs + properties)
Memory per recipe: ~1.5 KB (stored once in cache)
Total: 10 KB (nodes) + 150 KB (cache) = 160 KB

SAVINGS: 40-50% less memory!
```

---

## 🎯 Answer to Your Question

> "The whiteboard should essentially be reading and displaying data that is shared by the users in frontend, mobile and backend. When it writes, the data should be replaced. Is that currently happening?"

### Answer: **NO, it's NOT happening correctly** ❌

**What's Wrong:**
1. ❌ Frontend duplicates entire recipe object in node data
2. ❌ Recipe data stored 3 times (recipe object + individual fields)
3. ❌ No single source of truth
4. ❌ Changes to recipes don't sync to whiteboard
5. ❌ Memory waste (2-3x more than needed)

**What Backend Does Right:**
1. ✅ Stores only links (rid, gid, mid)
2. ✅ Stores only position + visual properties
3. ✅ Fetches actual data separately
4. ✅ Clean separation of concerns

**What Frontend Should Do:**
1. ✅ Store only recipe_id in node data
2. ✅ Maintain recipeCache in context
3. ✅ Fetch recipes once in batch
4. ✅ Components read from cache
5. ✅ Easy to refresh when data changes

---

## 🚀 Recommended Fix

### Phase 1: Add Recipe Cache (Week 1)
- [ ] Add `recipeCache` to WhiteboardContext
- [ ] Batch fetch recipes on load
- [ ] Update RecipeCardNode to read from cache

### Phase 2: Remove Duplicates (Week 2)
- [ ] Remove `data.recipe` from nodes
- [ ] Remove duplicate fields (name, image_url, etc.)
- [ ] Use nodeFactory to create clean nodes

### Phase 3: Test Sync (Week 3)
- [ ] Edit recipe in MainApp
- [ ] Refresh whiteboard
- [ ] Verify updated data appears
- [ ] Test mobile integration

---

## 📝 Priority: HIGH

**Why?**
- Current design violates single source of truth
- Causes data sync issues
- Wastes memory
- Makes mobile integration inconsistent
- Gets worse as whiteboard scales

**Effort:** Medium (part of refactoring plan)  
**Impact:** High (fixes fundamental architecture issue)

**Should be fixed during Week 1-2 of decomposition plan**

