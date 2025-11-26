# Whiteboard API Contract - Frontend/Backend Mapping

**Date:** November 26, 2025  
**Purpose:** Define the contract between frontend hooks and backend API to prevent mismatches

---

## 🎯 **Critical Issue This Solves**

**Problem:** Frontend sends `type: 'recipe'` → Backend expects `type: 'r'` → Database constraint violation!

**Solution:** This document maps EXACTLY what frontend should send vs what backend expects.

---

## 📦 **Object Type Mappings**

### **Database Schema (whiteboard_objects table)**

```sql
object_type VARCHAR(20) NOT NULL,
CONSTRAINT valid_object_type CHECK (object_type IN ('rc', 'note', 'image', 'list', 'link', 'container'))
```

### **Backend API Expected Values (whiteboards.py:661)**

| Object Type | Frontend Sends | Database Stores | Frontend Node Type | Description |
|---|---|---|---|---|
| Recipe Card | `'rc'` | `'rc'` | `'recipeCard'` | Recipe on canvas |
| Note Block | `'note'` | `'note'` | `'note'` | Text note |
| Grocery List | `'list'` | `'list'` | `'groceryListNode'` | Shopping list |
| Meal Plan | `'container'` | `'container'` | `'mealPlanContainer'` | Meal plan box |
| Activity Feed | `'af'` | (not in schema) | `'activityFeed'` | Activity widget |
| Image | `'img'` | `'image'` | `'image'` | Image object |
| Link | `'lnk'` | `'link'` | `'link'` | URL link |

---

## 🔌 **API Endpoint: Create Object**

### **Endpoint:**
```
POST /api/v2/whiteboard/{whiteboard_id}/o
```

### **Request Body Contract:**

```javascript
{
  // REQUIRED
  "type": "rc",             // Database values: 'rc', 'note', 'list', 'container', 'image', 'link'
  
  // OPTIONAL (for linked entities)
  "entity_type": "recipe",  // Full name: 'recipe', 'grocery_list', 'meal_plan'
  "entity_id": 123,         // ID of the linked entity
  
  // REQUIRED
  "position": [x, y, width, height, z_index],  // Array of 5 numbers
  
  // OPTIONAL
  "content": {},            // JSONB - for notes, images, custom data
  "tags": [],               // Array of strings
  "background_color": "#ffffff"  // Hex color
}
```

### **Backend Processing (whiteboards.py:672-675):**

```python
# Map entity_type to proper column
rid = entity_id if entity_type == 'recipe' else None
gid = entity_id if entity_type == 'grocery_list' else None
mid = entity_id if entity_type == 'meal_plan' else None
```

---

## 🎨 **Frontend → Backend Mapping**

### **Recipe Card**

**Frontend (useRecipeNodes.js):**
```javascript
await whiteboardAPI.createObject(whiteboardId, {
  type: 'rc',                   // ✅ CORRECT - matches database constraint
  entity_type: 'recipe',        // ✅ CORRECT
  entity_id: recipe.id,         // ✅ CORRECT
  position: [x, y, 300, 400, 0],
  tags: [],
  background_color: '#FFFFFF'
});
```

**Backend Stores:**
```sql
INSERT INTO wbo (wid, t, rid, gid, mid, p, c, tags, ...)
VALUES (59, 'rc', 2615, NULL, NULL, [x,y,w,h,z], {}, [], ...)
```

---

### **Grocery List Node**

**Frontend (nodeCreators.js):**
```javascript
await whiteboardAPI.createObject(whiteboardId, {
  type: 'list',                 // ✅ CORRECT - matches database constraint
  entity_type: 'grocery_list',  // ✅ CORRECT
  entity_id: groceryListId,     // ✅ CORRECT
  position: [x, y, 350, 500, 0],
  content: {
    items: [...],
    linkedRecipeIds: [...]
  }
});
```

**Backend Stores:**
```sql
INSERT INTO wbo (wid, t, rid, gid, mid, p, c, ...)
VALUES (59, 'list', NULL, 456, NULL, [x,y,w,h,z], {"items": [...]}, ...)
```

---

### **Note Block**

**Frontend (nodeCreators.js):**
```javascript
await whiteboardAPI.createObject(whiteboardId, {
  type: 'note',                 // ✅ CORRECT - matches database constraint
  entity_type: null,            // No linked entity
  entity_id: null,
  position: [x, y, 300, 200, 0],
  content: {
    html: '<p>Note content</p>',
    plainText: 'Note content'
  }
});
```

**Backend Stores:**
```sql
INSERT INTO wbo (wid, t, rid, gid, mid, p, c, ...)
VALUES (59, 'note', NULL, NULL, NULL, [x,y,w,h,z], {"html": "..."}, ...)
```

---

### **Meal Plan Container**

**Frontend (nodeCreators.js):**
```javascript
await whiteboardAPI.createObject(whiteboardId, {
  type: 'container',            // ✅ CORRECT - matches database constraint
  entity_type: 'meal_plan',     // ✅ CORRECT
  entity_id: mealPlanId,        // ✅ CORRECT
  position: [x, y, 600, 800, 0],
  content: {
    name: 'Monday',
    recipes: [...]
  }
});
```

**Backend Stores:**
```sql
INSERT INTO wbo (wid, t, rid, gid, mid, p, c, ...)
VALUES (59, 'container', NULL, NULL, 789, [x,y,w,h,z], {"name": "Monday"}, ...)
```

---

## ⚠️ **Common Mistakes to Avoid**

### **❌ WRONG - Don't Use Frontend Node Type Names**

```javascript
// ❌ WRONG
{
  type: 'recipe',           // Database doesn't accept this
  type: 'recipeCard',       // Database doesn't accept this
  type: 'groceryListNode',  // Database doesn't accept this
  type: 'r',                // Too short - not in constraint
  type: 'gl',               // Too short - not in constraint
}
```

### **✅ CORRECT - Use Database Constraint Values**

```javascript
// ✅ CORRECT - Must match database CHECK constraint
{
  type: 'rc',         // Recipe card
  type: 'note',       // Note
  type: 'list',       // Grocery list
  type: 'container',  // Meal plan container
  type: 'image',      // Image
  type: 'link',       // Link
}
```

---

## 📍 **Position Array Format**

**Backend expects EXACTLY 5 elements:**
```javascript
position: [x, y, width, height, z_index]
```

**Examples:**
```javascript
// Recipe card
[200, 150, 300, 400, 0]  // x=200, y=150, w=300, h=400, z=0

// Note
[500, 300, 250, 150, 0]  // x=500, y=300, w=250, h=150, z=0

// Grocery list
[1000, 400, 350, 500, 0] // x=1000, y=400, w=350, h=500, z=0
```

**⚠️ Backend validation (whiteboards.py:666-668):**
```python
# Ensure position is a list of 5 elements
if not isinstance(position, list) or len(position) != 5:
    position = [0, 0, 300, 400, 0]  # Default fallback
```

---

## 🔄 **Response Format**

**Backend returns (whiteboards.py:681-683):**
```python
RETURNING id, wid, t as type, rid, gid, mid, p as position, c as content, tags, ca as created_at
```

**Frontend receives:**
```javascript
{
  id: 157,              // Whiteboard object ID
  wid: 59,              // Whiteboard ID
  type: 'r',            // Object type (backend shorthand)
  rid: 2615,            // Recipe ID (if recipe)
  gid: null,            // Grocery list ID (if grocery list)
  mid: null,            // Meal plan ID (if meal plan)
  position: [200, 150, 300, 400, 0],
  content: {},          // JSONB content
  tags: [],
  created_at: '2025-11-26T17:42:56.693417'
}
```

---

## 🛠️ **Frontend Implementation Checklist**

### **useRecipeNodes.js**
- [x] ✅ Use `type: 'r'` not `type: 'recipe'`
- [x] ✅ Use `entity_type: 'recipe'`
- [x] ✅ Pass `entity_id: recipe.id`
- [x] ✅ Position array has 5 elements

### **nodeCreators.js**
- [ ] ⚠️ Verify all `createXxxNode()` functions use correct types
- [ ] ⚠️ Ensure position arrays are 5 elements
- [ ] ⚠️ Check content structure matches backend expectations

### **whiteboardSave.js**
- [ ] ⚠️ Verify save operations send correct types
- [ ] ⚠️ Check position updates maintain 5-element format

---

## 🧪 **Testing Checklist**

### **For Each Object Type:**
1. ✅ Create object via frontend
2. ✅ Verify backend receives correct `type` value
3. ✅ Check database `wbo.t` column has correct value
4. ✅ Confirm no constraint violations
5. ✅ Verify object loads correctly on refresh

### **Test Cases:**
```javascript
// Test 1: Recipe card
const recipe = { type: 'r', entity_type: 'recipe', entity_id: 123, ... };
// Expected: Saves successfully to wbo.t = 'r', wbo.rid = 123

// Test 2: Note
const note = { type: 'nt', content: { html: '...' }, ... };
// Expected: Saves successfully to wbo.t = 'nt'

// Test 3: Grocery list
const list = { type: 'gl', entity_type: 'grocery_list', entity_id: 456, ... };
// Expected: Saves successfully to wbo.t = 'gl', wbo.gid = 456

// Test 4: Meal plan
const plan = { type: 'mp', entity_type: 'meal_plan', entity_id: 789, ... };
// Expected: Saves successfully to wbo.t = 'mp', wbo.mid = 789
```

---

## 🔍 **Debugging**

### **Error: "violates check constraint wbo_valid_type"**

**Cause:** Frontend sent invalid `type` value

**Check:**
1. What did frontend send? (`type: 'recipe'` vs `type: 'r'`)
2. Is it in the allowed list? (`'rc', 'note', 'image', 'list', 'link', 'container'`)
3. Does backend map it correctly?

**Fix:** Use backend shorthand codes (`'r'`, `'nt'`, `'gl'`, `'mp'`, etc.)

---

### **Error: "Cannot read properties of undefined (reading 'objects')"**

**Cause:** Backend response structure mismatch

**Check:**
1. Is backend returning `whiteboard.objects`?
2. Is frontend looking for `whiteboardData.whiteboard.objects`?
3. Are null checks in place?

**Fix:** Add null checks: `whiteboardData?.whiteboard?.objects || []`

---

## 📚 **Reference Files**

### **Backend:**
- `app/api/v2/whiteboards.py:630-730` - Create object endpoint
- `database_tools/migrations/whiteboard_schema_v1.sql:89-94` - Schema constraint

### **Frontend:**
- `frontend/src/hooks/useRecipeNodes.js:63` - Recipe creation
- `frontend/src/utils/nodeCreators.js` - Node factory functions
- `frontend/src/services/whiteboardAPI.js:105` - API call wrapper

---

## 🎓 **Summary**

**Golden Rules:**
1. ✅ **Always use backend shorthand codes** (`'r'`, `'nt'`, `'gl'`, `'mp'`)
2. ✅ **Position arrays must have 5 elements** `[x, y, w, h, z]`
3. ✅ **Use entity_type + entity_id for linked objects**
4. ✅ **Add null checks for async data**
5. ✅ **Test both create AND load operations**

**When Adding New Object Types:**
1. Add to database constraint: `CHECK (object_type IN (...))`
2. Add backend shorthand mapping
3. Update this document
4. Create frontend factory function
5. Test end-to-end

---

**Last Updated:** November 26, 2025  
**Version:** 1.0  
**Status:** ✅ Active - Use this as source of truth for all whiteboard object operations
