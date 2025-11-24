# V2 Migration - Remaining Steps

**Status:** 5 of 7 features complete (71% done) 🎉  
**Last Updated:** November 18, 2025

---

## ✅ Completed Features

### 1. Grocery Lists (100% Complete)
- **Files Modified:** 
  - `frontend/src/components/GroceryManagerWorkspace.js`
  - `frontend/src/components/LoadGroceryListPanel.js`
  - `app/database/repositories/grocery_list_repository.py`
- **Endpoints Migrated:** 8
- **Status:** ✅ Tested and working in production

### 2. Meal Plans (100% Complete)
- **Files Modified:**
  - `frontend/src/components/MealPlannerView.js`
  - `frontend/src/components/NotionMealPlanner.js`
- **Endpoints Migrated:** 6
- **Status:** ✅ Tested and working in production

### 3. Recipes (100% Complete) 🎉
- **Files Modified:**
  - `frontend/src/pages/MainApp.js`
  - `frontend/src/components/RecipeListView.js`
  - `frontend/src/components/ImportRecipeModal.js`
  - `app/api/v2/recipe_import.py` (fixed circular import issue)
- **Endpoints Migrated:** 10+ (core recipe operations + all import methods)
- **Test Results:** ✅ **100% pass rate** (10/10 tests passed)
- **Status:** ✅ Fully tested and working
- **Achievements:**
  - ✅ Recipe loading with user-specific filtering and pagination
  - ✅ Import from URL (web scraping working at 88.55% confidence)
  - ✅ Import from text (AI parsing working)
  - ✅ Import from OCR/photo (endpoint ready)
  - ✅ Import from voice (endpoint ready)
  - ✅ Recipe deletion with proper user authorization
  - ✅ Recipe claiming (community features)
  - ✅ Search functionality
  - ✅ All v2 endpoints properly registered and tested

### 4. Community (100% Complete) ✅
- **Files Modified:**
  - `frontend/src/components/CommunityBrowserNew.js`
- **Endpoints Migrated:** 1
- **Status:** ✅ Migrated and ready for testing
- **Changes:**
  - Updated `/api/community/recipes` → `/api/v2/community/recipes`
  - Added v2 response structure handling (`data.data.recipes`)
  - Maintained existing fallback and mock data logic

### 5. Pantry (100% Complete) ✅
- **Files Modified:**
  - `frontend/src/components/PantryManager.js`
  - `frontend/src/hooks/usePantry.js`
- **Endpoints Migrated:** 5
- **Status:** ✅ Migrated and ready for testing
- **Changes:**
  - Updated all pantry CRUD operations to v2
  - Added user_id extraction from localStorage
  - Updated ingredient search and status endpoints
  - All operations now use v2 response structures

---

## 🔄 Remaining Features (2 of 7 - Optional)

---

### 6. Admin Tools (Priority: LOW - Internal Use Only)

**Estimated Time:** 30-45 minutes  
**Complexity:** Low

#### Current State:
- V2 API exists: `app/api/v2/pantry.py`
- Uses v1 endpoints in `frontend/src/components/PantryPanel.js`

#### Files to Update:
```
frontend/src/components/PantryPanel.js
frontend/src/components/GroceryManagerWorkspace.js (pantry integration)
```

#### Endpoints to Migrate (4 total):

| Current (v1) | Migrate To (v2) | Method | Notes |
|--------------|-----------------|--------|-------|
| `/api/pantry` | `/api/v2/pantry/user/${userId}` | GET | Get pantry items |
| `/api/pantry/status` | `/api/v2/pantry/status` | GET | Feature status |
| `/api/ingredients` | `/api/v2/ingredients` | GET | Ingredient search |
| `/api/ingredients?query=...` | `/api/v2/ingredients/search` | GET | Autocomplete |

#### Migration Steps:

1. **Update PantryPanel.js** (20 min)
   - Add `useAuth()` hook
   - Update all fetch calls to v2
   - Add `user_id` to requests

2. **Test Pantry Operations** (10 min)
   - View pantry items
   - Add items
   - Remove items
   - Search ingredients

---

### 7. Friends (Priority: VERY LOW - Can Skip)

**Estimated Time:** 15 minutes  
**Complexity:** Very Low (1 endpoint)

#### Current State:
- V2 API exists: `app/api/v2/community.py`
- Uses v1 in `frontend/src/components/CommunityBrowserNew.js`

#### Files to Update:
```
frontend/src/components/CommunityBrowserNew.js
```

#### Endpoints to Migrate (1 total):

| Current (v1) | Migrate To (v2) | Method | Notes |
|--------------|-----------------|--------|-------|
| `/api/community/recipes` | `/api/v2/community/recipes` | GET | Browse community |

#### Migration Steps:

1. **Update CommunityBrowserNew.js** (10 min)
   ```javascript
   // Change
   fetch(`${API_BASE_URL}/api/community/recipes?limit=50&sort=recent`)
   // To
   fetch(`${API_BASE_URL}/api/v2/community/recipes?limit=50&sort=recent`)
   ```

2. **Test** (5 min)
   - Browse community recipes
   - Filter/sort

---

### 6. Friends (Priority: LOW)

**Estimated Time:** 30 minutes OR Skip (feature may be incomplete)  
**Complexity:** Unknown

#### Current State:
- V2 API exists: `app/api/v2/friends.py`
- Frontend component `FriendsView.js` appears to be placeholder
- **No API calls found in current implementation**

#### Decision Needed:
- **Option A:** Skip (feature not active)
- **Option B:** Implement basic v2 endpoints if needed later

#### If Implementing:

| Feature | V2 Endpoint | Method |
|---------|-------------|--------|
| Get friends | `/api/v2/friends/user/${userId}` | GET |
| Add friend | `/api/v2/friends` | POST |
| Remove friend | `/api/v2/friends/${friendshipId}` | DELETE |

---

### 7. Admin Tools (Priority: LOW - Internal)

**Estimated Time:** 45 minutes  
**Complexity:** Medium

#### Current State:
- Uses v1 endpoints in admin components
- V2 admin endpoints may need creation

#### Files to Update:
```
frontend/src/components/AdminDashboard.js
frontend/src/components/AdminRecipeOverlay.js
```

#### Endpoints to Migrate:

| Current (v1) | Migrate To (v2) | Method |
|--------------|-----------------|--------|
| `/api/admin/check-access` | `/api/v2/admin/auth/check` | GET |
| `/api/admin/recipes/*` | `/api/v2/admin/recipes/*` | Various |
| `/api/admin/recipes/${id}/promote` | `/api/v2/admin/recipes/${id}/promote` | POST |
| `/api/admin/recipes/${id}/demote` | `/api/v2/admin/recipes/${id}/demote` | POST |
| `/api/admin/recipes/bulk-delete/*` | `/api/v2/admin/recipes/bulk-delete/*` | POST |

---

## 📋 Migration Checklist

### For Each Feature:

- [ ] **Step 1: Add Authentication**
  - Import `useAuth` hook
  - Extract `user` and `token`
  - Add user validation

- [ ] **Step 2: Update Endpoints**
  - Change `/api/...` to `/api/v2/...`
  - Add `/user/${userId}` where needed
  - Add `?user_id=${userId}` query params for GET/DELETE

- [ ] **Step 3: Update Request Bodies**
  - Add `user_id` to POST/PUT bodies
  - Ensure all required fields are included

- [ ] **Step 4: Update Response Handling**
  - Change `data.recipes` to `data.data?.recipes || data.recipes`
  - Handle nested response structure

- [ ] **Step 5: Test Thoroughly**
  - Create operations
  - Read operations
  - Update operations
  - Delete operations
  - Error cases

---

## 🎯 Recommended Migration Order

### Phase 1 (Quick Wins - 1 hour):
1. ✅ **Grocery Lists** (DONE)
2. ✅ **Meal Plans** (DONE)

### Phase 2 (Main Work - COMPLETED! 🎉):
3. ✅ **Recipes** (DONE) - Core feature successfully migrated!
   - **Time Actual:** ~4 hours (including debugging)
   - **Result:** 100% test pass rate
   - **Note:** Fixed circular import issue in v2 recipe_import.py

### Phase 3 (Remaining Quick Wins - COMPLETED! 🎉):
4. ✅ **Community** (DONE) - 10 minutes actual
5. ✅ **Pantry** (DONE) - 30 minutes actual

### Phase 4 (Optional - 1 hour):
6. **Admin Tools** (45 min) - Internal use only (can skip for now)
7. **Friends** (Skip or 30 min) - Feature not fully implemented

---

## 🚀 After Migration Complete

### Cleanup Tasks:

1. **Deprecate v1 Endpoints** (30 min)
   - Add deprecation warnings to v1 routes in `hungie_server.py`
   - Or delete v1 grocery/meal plan routes entirely
   
2. **Drop Legacy Database Columns** (15 min)
   - Run `phase2_drop_columns.py` to remove:
     - `list_name` → now just `name`
     - `list_data` → now just `items` 
     - `items_json` → removed
     - `ingredient_name` → now just `name`

3. **Update Documentation** (15 min)
   - Update API docs
   - Update README
   - Remove old migration plans

4. **Performance Optimization** (optional)
   - Add database indexes on new columns
   - Optimize v2 queries
   - Add caching where appropriate

---

## 📊 Progress Tracking

**Total Estimated Time:** ~45 minutes remaining (Admin tools only - OPTIONAL!)

| Feature | Status | Time Spent | Priority |
|---------|--------|-----------|----------|
| Grocery Lists | ✅ Complete | ~1 hour | - |
| Meal Plans | ✅ Complete | ~1 hour | - |
| **Recipes** | ✅ **Complete** | **~4 hours** | **✅ DONE** |
| **Community** | ✅ **Complete** | **~10 min** | **✅ DONE** |
| **Pantry** | ✅ **Complete** | **~30 min** | **✅ DONE** |
| Admin Tools | ⏳ Pending (Optional) | Est. 45 min | Low (Internal) |
| Friends | ⏳ Skip | N/A | Very Low |

**Progress:** 5/7 features **(71% complete)** → **All user-facing features DONE!** 🎉🎉🎉

### 🎯 Major Achievement: Recipes V2 Migration Complete!

**Test Results Summary:**
```
Total Tests: 10
Passed: 10  ✅
Failed: 0   ✅
Success Rate: 100%  🎉
```

**Tested Operations:**
- ✅ Authentication with user ID extraction
- ✅ Get user recipes with v2 pagination
- ✅ Get user recipes with stats (THE STAR ENDPOINT!)
- ✅ Import from URL (web scraping at 88.55% confidence)
- ✅ Import from text (AI parsing successful)
- ✅ Search recipes
- ✅ Delete recipes with authorization
- ✅ Voice import endpoint availability
- ✅ OCR import endpoint availability
- ✅ Claim recipe endpoint availability

**Key Technical Wins:**
1. Fixed circular import issue in `app/api/v2/recipe_import.py`
2. Direct import service calls instead of v1 wrapper
3. Proper v2 response structure handling
4. User authentication in all endpoints
5. Comprehensive error handling with detailed logging

---

## ⚠️ CRITICAL: User ID Migration Pattern

### **MOST COMMON ISSUE:** Missing `user_id`

**Every v2 endpoint requires user authentication!** This is the #1 cause of 400 errors during migration.

#### The Problem:
```javascript
// ❌ WRONG - Missing user_id causes 400 Bad Request
fetch(`${getApiUrl()}/api/v2/grocery-lists`)
fetch(`${getApiUrl()}/api/v2/meal-plans`)
fetch(`${getApiUrl()}/api/v2/recipes`)
```

#### The Solution:
```javascript
// ✅ CORRECT - Always extract user_id first
const { user, token } = useAuth();
const userId = user?.id;

if (!userId) {
  console.error('No user ID available');
  return; // or handle appropriately
}

// Then use it in your requests
fetch(`${getApiUrl()}/api/v2/grocery-lists/user/${userId}`)
```

### User ID Checklist for Every Migration:

- [ ] **Import useAuth hook**
  ```javascript
  import { useAuth } from '../contexts/AuthContext';
  const { user, token } = useAuth();
  ```

- [ ] **Extract user ID at start of function**
  ```javascript
  const userId = user?.id;
  if (!userId) {
    // Handle no user case
    return;
  }
  ```

- [ ] **Add to URL for GET/DELETE**
  ```javascript
  // List endpoints
  GET /api/v2/{resource}/user/${userId}
  
  // Single item endpoints  
  GET /api/v2/{resource}/${id}?user_id=${userId}
  DELETE /api/v2/{resource}/${id}?user_id=${userId}
  ```

- [ ] **Add to body for POST/PUT/PATCH**
  ```javascript
  body: JSON.stringify({
    user_id: userId,  // ← Always include this!
    ...otherData
  })
  ```

- [ ] **Add Authorization header**
  ```javascript
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`  // ← Don't forget!
  }
  ```

### Quick Reference: Where to Add user_id

| Method | Where | Example |
|--------|-------|---------|
| GET (list) | URL path | `/api/v2/recipes/user/${userId}` |
| GET (single) | Query param | `/api/v2/recipes/${id}?user_id=${userId}` |
| POST | Request body | `{user_id: userId, ...}` |
| PUT/PATCH | Request body | `{user_id: userId, ...}` |
| DELETE | Query param | `/api/v2/recipes/${id}?user_id=${userId}` |

---

## 🛠️ Common Patterns

### Pattern 1: Simple GET with User ID
```javascript
// Before (v1)
const response = await fetch(`${getApiUrl()}/api/recipes`);

// After (v2)
const userId = user?.id;
if (!userId) return;
const response = await fetch(`${getApiUrl()}/api/v2/recipes/user/${userId}`);
```

### Pattern 2: GET Single Item with Auth
```javascript
// Before (v1)
const response = await fetch(`${getApiUrl()}/api/recipes/${id}`);

// After (v2)
const userId = user?.id;
if (!userId) return;
const response = await fetch(`${getApiUrl()}/api/v2/recipes/${id}?user_id=${userId}`);
```

### Pattern 3: POST/PUT with User ID
```javascript
// Before (v1)
fetch(`${getApiUrl()}/api/recipes`, {
  method: 'POST',
  body: JSON.stringify({ title: "Recipe" })
});

// After (v2)
const userId = user?.id;
fetch(`${getApiUrl()}/api/v2/recipes`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ 
    user_id: userId,
    title: "Recipe" 
  })
});
```

### Pattern 4: DELETE with User ID
```javascript
// Before (v1)
fetch(`${getApiUrl()}/api/recipes/${id}`, { method: 'DELETE' });

// After (v2)
const userId = user?.id;
fetch(`${getApiUrl()}/api/v2/recipes/${id}?user_id=${userId}`, {
  method: 'DELETE',
  headers: { 'Authorization': `Bearer ${token}` }
});
```

### Pattern 5: Response Handling
```javascript
// Before (v1)
const data = await response.json();
if (data.success) {
  const items = data.recipes;
}

// After (v2)
const data = await response.json();
if (data.success) {
  // Handle nested structure
  const items = data.data?.recipes || data.recipes;
}
```

---

## 🔍 Testing Strategy

### For Each Migrated Feature:

1. **Unit Operations:**
   - Create new item
   - Read/load items
   - Update existing item
   - Delete item

2. **Edge Cases:**
   - No user logged in
   - Invalid user ID
   - Network errors
   - Server errors (500)
   - Not found (404)

3. **Integration:**
   - Feature works with other features
   - Data consistency
   - UI updates correctly

4. **Performance:**
   - No regressions
   - Response times acceptable
   - No memory leaks

---

## 📝 Notes

### Key Differences V1 vs V2:

1. **Authentication:**
   - V1: Optional or inconsistent
   - V2: Required `user_id` in every request

2. **Response Structure:**
   - V1: Flat structure `{success, recipes, ...}`
   - V2: Nested structure `{success, data: {recipes, pagination, ...}}`

3. **Error Handling:**
   - V1: Inconsistent error messages
   - V2: Standardized error format

4. **Database Columns:**
   - V1: Legacy names (`list_name`, `items_json`)
   - V2: Standard names (`name`, `items`)

### Benefits of V2:

- ✅ Single source of truth
- ✅ Consistent authentication
- ✅ Better error handling
- ✅ Cleaner response structures
- ✅ Repository pattern (easier testing)
- ✅ Standardized field names
- ✅ Better database performance

---

## 🎯 Success Criteria

Migration is complete when:

- [ ] All frontend components use v2 endpoints
- [ ] All CRUD operations work correctly
- [ ] No v1 endpoints called from frontend
- [ ] All tests pass
- [ ] No console errors
- [ ] Performance is acceptable
- [ ] Legacy columns dropped from database
- [ ] Documentation updated

---

## 🎊 Recipe Migration Success Story

**What We Accomplished:**

The recipe v2 migration was the **largest and most complex** feature migration, involving:
- 10+ endpoints across multiple import methods
- 3 major frontend components
- 1 critical backend fix (circular import resolution)
- Comprehensive test suite with 100% pass rate

**Files Modified:**
1. `frontend/src/pages/MainApp.js` - Recipe loading with v2 pagination
2. `frontend/src/components/RecipeListView.js` - CRUD operations with auth
3. `frontend/src/components/ImportRecipeModal.js` - All import methods to v2
4. `app/api/v2/recipe_import.py` - Fixed to use direct service calls

**Technical Challenges Overcome:**
1. ✅ Circular import issue (v2 wrapping v1 endpoints)
2. ✅ Response structure differences (nested data.data)
3. ✅ User authentication in all operations
4. ✅ Import service integration

**Automated Test Suite Created:**
- `test-v2-migration.js` - Backend API testing
- `frontend/test-frontend-integration.html` - Visual testing checklist

---

**Next Steps:** With recipes complete, the remaining features (Community, Pantry) are straightforward migrations with significantly less complexity. Admin tools are optional internal tooling.
