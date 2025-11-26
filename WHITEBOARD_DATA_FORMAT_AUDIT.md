# Whiteboard Data Format Mismatch Audit

**Date:** November 26, 2025  
**Purpose:** Identify all data format mismatches between database, backend API, and frontend code

---

## 🎯 **Executive Summary**

**Status:** ✅ 1 Critical Fix Applied, 🟡 Multiple Potential Issues Identified

**What We're Auditing:**
- Object type naming (database `'rc'` vs frontend `'recipeCard'`)
- ID field names (database `rid, gid, mid` vs frontend `entity_id`)
- Position format (array vs object)
- Entity type checking

---

## ✅ **FIXED: Recipe Loading (Critical)**

### **Issue:**
Recipes were saving but not loading on page reload.

### **Root Cause:**
```javascript
// Database stores:
{ type: 'rc', rid: 2615 }

// Hook was checking:
if (obj.entity_type === 'recipe' && obj.entity_id) { ... }  // ❌ Never matches!
```

### **Fix Applied:**
```javascript
// Now checks all possible formats:
if (obj.type === 'rc' || obj.entity_type === 'recipe' || obj.rid) {
  const recipeId = obj.entity_id || obj.rid;  // Handle both formats
  // ...
}
```

**File:** `frontend/src/hooks/useWhiteboardData.js` (Lines 147-161)  
**Status:** ✅ Fixed and deployed

---

## 🟡 **POTENTIAL ISSUES TO MONITOR**

### **1. Meal Plan Loading** ⚠️ **HIGH PRIORITY**

**Location:** `WhiteboardApp.js:514`

**Current Code:**
```javascript
const mealPlanObjects = whiteboardData.objects?.filter(obj => {
  return (obj.entity_type === 'meal_plan' || obj.object_type === 'mp') 
    && (obj.entity_id || obj.mid);
}) || [];
```

**Database Reality:**
- Type stored: `'container'` (from constraint)
- ID field: `mid` (meal plan ID column)

**Recommendation:**
```javascript
// Add type='container' check:
const mealPlanObjects = whiteboardData.objects?.filter(obj => {
  return (obj.type === 'container' || obj.entity_type === 'meal_plan' || obj.object_type === 'mp') 
    && (obj.entity_id || obj.mid);
}) || [];
```

**Risk:** Medium - Meal plans may not load on refresh  
**Test:** Add meal plan → reload → verify it persists

---

### **2. Grocery List Loading** ⚠️ **HIGH PRIORITY**

**Location:** `WhiteboardApp.js:438-492`

**Current Code:**
Grocery lists are loaded via separate API endpoint (`/api/v2/whiteboard/59/grocery-lists`), not from whiteboard objects.

**Potential Issue:**
If grocery lists ARE stored as whiteboard objects (type='list'), they won't be recognized.

**Recommendation:**
Check if grocery lists should be loaded from:
1. Separate endpoint (current method) ✅
2. Whiteboard objects array (may need type='list' handler)

**Risk:** Low if using separate endpoint  
**Test:** Create grocery list → reload → verify visibility

---

### **3. Note Handling** ⚠️ **MEDIUM PRIORITY**

**Location:** `useWhiteboardData.js:147`

**Current Code:**
```javascript
if (obj.type === 'note' || obj.object_type === 'note') {
  return createNoteNode(obj);
}
```

**Database Reality:**
- Type stored: `'note'` ✅ (matches!)

**Status:** Looks correct, but needs testing  
**Test:** Create note → reload → verify it persists

---

## 📊 **Data Contract Matrix**

| Feature | Frontend Node Type | Backend Sends | Database Stores | ID Field | Status |
|---------|-------------------|---------------|-----------------|----------|--------|
| **Recipe** | `recipeCard` | `type: 'rc'` | `t = 'rc'` | `rid` | ✅ Fixed |
| **Note** | `note` | `type: 'note'` | `t = 'note'` | N/A | ⚠️ Needs test |
| **Grocery List** | `groceryListNode` | Via separate API | `t = 'list'` | `gid` | ⚠️ Needs test |
| **Meal Plan** | `mealPlanContainer` | `type: ?` | `t = 'container'` | `mid` | ⚠️ Needs fix |
| **Image** | `image` | `type: 'image'` | `t = 'image'` | N/A | ⚠️ Not implemented |
| **Link** | `link` | `type: 'link'` | `t = 'link'` | N/A | ⚠️ Not implemented |

---

## 🔍 **Code Locations to Monitor**

### **Type Checking (Frontend Node Types)**

All `node.type ===` checks in frontend code:

1. **WhiteboardApp.js:237** - `node.type === 'recipeCard'` ✅ Correct (frontend type)
2. **WhiteboardApp.js:268** - `node.type === 'recipeCard'` ✅ Correct
3. **WhiteboardApp.js:279** - `node.type === 'note'` ✅ Correct
4. **WhiteboardApp.js:641** - `node.type === 'recipeCard'` ✅ Correct
5. **WhiteboardApp.js:1495** - `node.type === 'mealPlanContainer'` ✅ Correct
6. **WhiteboardApp.js:1531** - `node.type === 'recipeCard'` ✅ Correct
7. **WhiteboardApp.js:1553** - `node.type === 'mealPlanContainer'` ✅ Correct

**Note:** These check frontend node types (after conversion) - these are CORRECT!

### **Object Type Checking (Database/Backend Types)**

All `obj.type ===` or `obj.entity_type ===` checks:

1. **useWhiteboardData.js:147** - `obj.type === 'note'` ✅ Fixed to check 'note' not 'nt'
2. **useWhiteboardData.js:151** - `obj.type === 'rc'` ✅ Fixed
3. **WhiteboardApp.js:514** - `obj.entity_type === 'meal_plan'` ⚠️ Needs type='container' check

---

## 🎨 **ID Field Access Patterns**

### **Recipe IDs:**
- Database column: `rid`
- Backend may return: `entity_id` OR `rid`
- Frontend uses: `node.data.recipe_id` (after conversion)

**Status:** ✅ Fixed with `obj.entity_id || obj.rid`

### **Grocery List IDs:**
- Database column: `gid`
- Backend may return: `entity_id` OR `gid`
- Frontend uses: `node.data.dbId`

**Status:** ⚠️ Needs testing

### **Meal Plan IDs:**
- Database column: `mid`
- Backend may return: `entity_id` OR `mid`
- Frontend uses: `obj.entity_id || obj.mid` ✅

**Status:** ⚠️ Needs type checking fix

---

## 📍 **Position Format Handling**

### **Frontend Sends (Create):**
```javascript
position: [x, y, width, height, z]  // Array (5 elements)
```

### **Database Stores:**
```sql
p DECIMAL[]  -- Array [x, y, w, h, z]
```

### **Backend Returns:**
```javascript
position: [x, y, w, h, z]  // Array (5 elements)
```

### **Frontend Node Uses:**
```javascript
node.position = { x, y }  // Object (React Flow format)
```

**Status:** ✅ Correctly handled in `createRecipeNodeFromSavedObject()`

---

## 🛠️ **Recommended Fixes**

### **Priority 1: Meal Plan Type Checking**

**File:** `WhiteboardApp.js:514`

```javascript
// Current:
return (obj.entity_type === 'meal_plan' || obj.object_type === 'mp') 
  && (obj.entity_id || obj.mid);

// Recommended:
return (obj.type === 'container' || obj.entity_type === 'meal_plan' || obj.object_type === 'mp') 
  && (obj.entity_id || obj.mid);
```

**Reason:** Database stores meal plans with `type='container'`

---

### **Priority 2: Add Defensive Logging**

Add to `useWhiteboardData.js` line 157:

```javascript
// Current:
console.warn(`⚠️ Unknown object type: ${obj.type}, entity_type: ${obj.entity_type}`);

// Recommended (add more detail):
console.warn(`⚠️ Unknown object type:`, {
  id: obj.id,
  type: obj.type,
  entity_type: obj.entity_type,
  rid: obj.rid,
  gid: obj.gid,
  mid: obj.mid,
  fullObject: obj
});
```

**Reason:** Help debug any objects that don't match our patterns

---

### **Priority 3: Grocery List Object Handling**

**Question to Answer:** Are grocery lists stored as whiteboard objects (type='list') or only via separate table?

**If stored as objects:**
Add to `useWhiteboardData.js:151`:

```javascript
// Handle grocery lists (type='list' from database)
if (obj.type === 'list' || obj.entity_type === 'grocery_list' || obj.gid) {
  const listId = obj.entity_id || obj.gid;
  // Create grocery list node
  return createGroceryListNodeFromSavedObject(obj, listId);
}
```

**Status:** Needs investigation

---

## 🧪 **Testing Checklist**

### **For Each Feature, Test:**

#### **✅ Recipe Cards (VERIFIED WORKING)**
- [x] Create recipe on canvas
- [x] Reload page
- [x] Recipe persists ✅
- [x] Recipe loads correctly ✅
- [x] Position preserved ✅

#### **🟡 Notes (NEEDS TESTING)**
- [ ] Create note on canvas
- [ ] Reload page
- [ ] Note persists?
- [ ] Note content preserved?
- [ ] Position preserved?

#### **🟡 Grocery Lists (NEEDS TESTING)**
- [ ] Create grocery list
- [ ] Reload page
- [ ] List persists?
- [ ] Items preserved?
- [ ] Position preserved?
- [ ] Widget dimensions preserved?

#### **🟡 Meal Plans (NEEDS TESTING & FIX)**
- [ ] Create meal plan container
- [ ] Add recipes to container
- [ ] Reload page
- [ ] Container persists?
- [ ] Recipes linked correctly?
- [ ] Position preserved?

---

## 📚 **Reference: Database Constraint**

```sql
-- From whiteboard_schema_v1.sql
CONSTRAINT valid_object_type CHECK (
  object_type IN ('rc', 'note', 'image', 'list', 'link', 'container')
)
```

**These are the ONLY values allowed in database!**

Any code checking for other values will fail.

---

## 🔄 **Update History**

| Date | Issue | Fix | Status |
|------|-------|-----|--------|
| 2025-11-26 | Recipes not loading | Added `obj.type === 'rc'` check | ✅ Fixed |
| 2025-11-26 | Position format | Already handled correctly | ✅ OK |
| 2025-11-26 | Meal plan type check | Identified, not yet fixed | 🟡 Pending |

---

## 💡 **Pattern for Future Fixes**

When adding new object types:

1. **Check database constraint** - what value is stored in `t` column?
2. **Update API contract doc** - add new type mapping
3. **Add to useWhiteboardData hook** - handle in loadSavedObjects()
4. **Test create → save → reload cycle**
5. **Update this audit doc**

---

## 🎓 **Key Learnings**

### **Why This Happened:**

1. **Database optimized for storage** → Short codes (`'rc'`, `'nt'`, etc.)
2. **Frontend optimized for clarity** → Descriptive names (`'recipeCard'`, `'note'`)
3. **Backend is pass-through** → No translation layer!
4. **Result:** Mismatches everywhere 😵

### **The Solution:**

**Defensive coding with multiple checks:**

```javascript
// GOOD Pattern:
if (obj.type === 'rc' || obj.entity_type === 'recipe' || obj.rid) {
  const recipeId = obj.entity_id || obj.rid;
  // Handle it
}

// BAD Pattern:
if (obj.entity_type === 'recipe') {  // Too narrow, will miss objects!
  // Handle it
}
```

---

## 📞 **Next Actions**

1. ✅ **DONE:** Fix recipe loading
2. 🟡 **TODO:** Fix meal plan type checking (Priority 1)
3. 🟡 **TODO:** Test notes (Priority 2)
4. 🟡 **TODO:** Test grocery lists (Priority 3)
5. 🟡 **TODO:** Add defensive logging (Priority 2)
6. 📋 **FUTURE:** Consider backend translation layer

---

**Last Updated:** November 26, 2025  
**Status:** Active - Living Document  
**Maintainer:** Update this as you find and fix issues!
