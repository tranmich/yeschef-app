# Grocery List Field Mapping Audit
# ===================================
# Understanding what each platform ACTUALLY uses

## DISCOVERY PHASE: What fields exist now?

### 1. DATABASE (Source of Truth)
```sql
Table: grocery_lists
├── id (primary key)
├── user_id
│
├── NAMES (3 versions - THIS IS THE PROBLEM):
│   ├── name (Phase 2, JSONB column - NEW)
│   ├── list_name (legacy TEXT - OLD)
│   └── [no third version]
│
├── ITEMS (3 versions - THIS IS THE PROBLEM):
│   ├── list_data (Phase 2, JSONB - NEW, preferred)
│   ├── items_json (legacy TEXT - OLD)
│   └── [no third version]
│
├── TIMESTAMPS (2 versions each):
│   ├── created_at (Phase 2 - NEW)
│   ├── created_date (legacy - OLD)
│   ├── updated_at (Phase 2 - NEW)
│   └── updated_date (legacy - OLD)
│
└── METADATA:
    ├── household_id (or hid - compact)
    ├── whiteboard_id (or wid - compact)
    ├── meal_plan_id
    ├── widget_position (or wp - compact)
    └── linked_recipe_ids (or lr - compact)
```

### 2. WHITEBOARD (Frontend)
**What it sends to API:**
```javascript
{
  name: "Shopping List",           // ✅ Correct
  items: [
    {
      id: "temp-123",
      ingredient: "bananas",         // ❌ WRONG - should be "name"
      checked: false
    }
  ]
}
```

**What it expects from API:**
```javascript
{
  name: "...",                      // ✅ Correct
  items: [...]                      // ✅ Correct structure, wrong item fields
}
```

### 3. WEB MANAGER (Frontend)
**What it sends to API:**
```javascript
{
  name: "...",                      // ✅ Correct
  items: [
    { id: "1", name: "milk", checked: false }  // ✅ Correct!
  ]
}
```

**What it expects from API:**
```javascript
// Can handle both:
{
  name: "..." || list_name: "...",  // ❌ Fallback shouldn't be needed
  items: [...] || list_data: [...]  // ❌ Fallback shouldn't be needed
}
```

### 4. MOBILE (React Native)
**What it sends to API:**
```javascript
{
  name: "...",                      // ✅ Correct
  items: [
    { id: "1", name: "eggs", checked: false }  // ✅ Correct!
  ]
}
```

**What it expects from API:**
```javascript
{
  name: "...",                      // ✅ Correct
  items: [...]                      // ✅ Structure correct
}
```

But adapter checks:
```javascript
item.name || item.ingredient || item.ingredient_name || item.display_text
```
❌ Should ONLY check `item.name`

### 5. BACKEND API (Python)
**Repository returns:**
```python
{
    'id': 114,
    'name': 'Shopping List',         # ✅ Phase 2 standardized
    'items': [...],                  # ✅ Phase 2 standardized (from list_data)
    'household_id': 11,
    'created_at': '...',
    'updated_at': '...'
}
```

Currently correct! ✅

---

## 🎯 THE STANDARD (What Everything Should Use)

### **Single Canonical Format:**

```javascript
GroceryList {
  // Identifiers
  id: number,
  user_id: number,
  
  // Core data
  name: string,              // ← List name (ONLY THIS FIELD)
  items: [                   // ← Items array (ONLY THIS FIELD)
    {
      id: string,
      name: string,          // ← Item text (ONLY THIS FIELD)
      checked: boolean,
      quantity?: string,
      unit?: string,
      category?: string
    }
  ],
  
  // Metadata
  household_id?: number,
  whiteboard_id?: number,
  meal_plan_id?: number,
  widget_position?: object,
  linked_recipe_ids?: number[],
  
  // Timestamps
  created_at: string,        // ← ISO format (ONLY THIS FIELD)
  updated_at: string         // ← ISO format (ONLY THIS FIELD)
}
```

### **Rules:**
1. ✅ List name = `name` (never `list_name`)
2. ✅ Items array = `items` (never `list_data`, `items_json`, `sections`)
3. ✅ Item text = `name` (never `ingredient`, `ingredient_name`, `display_text`)
4. ✅ Timestamps = `created_at`, `updated_at` (never `_date` suffix)

---

## 📋 PHASED STANDARDIZATION PLAN

### **Phase A: Fix the Root (Backend) - 30 minutes**

Make backend ONLY return standard format:

**Files to change:**
1. `app/database/repositories/grocery_list_repository.py` ✅ Already done (Phase 2)
2. Verify all methods return: `name`, `items` (from `list_data`), `created_at`, `updated_at`

**Status:** ✅ ALREADY COMPLETE (Phase 2 did this!)

---

### **Phase B: Fix Whiteboard (Frontend) - 20 minutes**

Change whiteboard to use `name` instead of `ingredient` for items.

**File:** `frontend/src/components/whiteboard/nodes/GroceryListNode.js`

**Find all instances of:**
```javascript
ingredient: "bananas"
```

**Replace with:**
```javascript
name: "bananas"
```

**Estimated changes:** ~5-10 lines in 2 files

---

### **Phase C: Simplify Web Manager (Frontend) - 15 minutes**

Remove fallback chains.

**File:** `frontend/src/components/GroceryManagerWorkspace.js`

**Current (with fallbacks):**
```javascript
const listName = loadedList.name || loadedList.list_name;
const listData = loadedList.items || loadedList.list_data;
```

**After (direct access):**
```javascript
const listName = loadedList.name;
const listData = loadedList.items;
```

**Estimated changes:** ~3-5 lines

---

### **Phase D: Simplify Mobile (React Native) - 15 minutes**

Remove fallback chains from adapter.

**File:** `YesChefMobile/src/services/MobileGroceryAdapter.js`

**Current:**
```javascript
item.display_text || item.name || item.ingredient || item.ingredient_name || 'Unknown'
```

**After:**
```javascript
item.name || 'Unknown item'
```

**Estimated changes:** ~3-4 lines

---

### **Phase E: Drop Legacy Database Columns - 10 minutes**

After all platforms are updated and tested:

**File:** `phase2_drop_columns.py` (already exists!)

```python
# Drop legacy columns
ALTER TABLE grocery_lists DROP COLUMN list_name;
ALTER TABLE grocery_lists DROP COLUMN items_json;
ALTER TABLE grocery_lists DROP COLUMN created_date;
ALTER TABLE grocery_lists DROP COLUMN updated_date;
```

---

## 📊 COMPARISON

### Your Approach (Direct Standardization):
```
Phase A: Backend ✅ Already done
Phase B: Whiteboard (20 min)
Phase C: Web Manager (15 min)
Phase D: Mobile (15 min)
Phase E: Drop columns (10 min)

Total: ~1 hour (backend already done!)
Files changed: ~5 files
Complexity: Low (just renaming fields)
```

### My Original Approach (Normalizer):
```
Step 1: Create normalizer (done)
Step 2: Integrate in repository (30 min)
Step 3: Update API (20 min)
Step 4: Fix platforms (2 hours)
Step 7: Remove normalizer fallbacks (20 min)

Total: ~3 hours
Files changed: ~10 files
Complexity: Medium (new abstraction layer)
```

---

## ✅ YOUR APPROACH IS BETTER!

**Why:**
- ✅ Simpler (no new abstraction)
- ✅ Faster (1 hour vs 3 hours)
- ✅ Direct (just rename fields)
- ✅ Backend already done (Phase 2)

**The normalizer was overengineering!**

---

## 🚀 SIMPLIFIED PLAN

Let's just do direct field standardization:

1. **Whiteboard:** Change `ingredient` → `name`
2. **Web Manager:** Remove fallbacks
3. **Mobile:** Remove fallbacks
4. **Database:** Drop legacy columns

**Want me to start with Whiteboard (Phase B)?** It's the only platform still using wrong field names.
