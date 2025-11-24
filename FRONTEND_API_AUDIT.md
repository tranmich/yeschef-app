# Frontend API Endpoint Audit
**Goal:** Map all sidebar navigation pages to their API endpoints and determine v1→v2 migration path

**Date:** November 17, 2025

---

## Executive Summary

**Current State:** Frontend uses BOTH v1 (hungie_server.py) and v2 (app/api/v2/) endpoints
**Problem:** Duplicate logic, inconsistent data formats, technical debt
**Solution:** Migrate all endpoints to v2, deprecate hungie_server.py routes

---

## Navigation Views (from MainApp.js)

1. **Cookbook** (`activeView === 'cookbook'`) - Recipe browsing
2. **Community** (`activeView === 'community'`) - Community recipes
3. **Friends** (`activeView === 'friends'`) - Friends management
4. **Households** (`activeView === 'households'`) - Household management  
5. **Grocery Manager** (`activeView === 'grocery-manager'`) - Grocery lists
6. **Import** (`activeView === 'import'`) - Photo/OCR import
7. **Sidebars:**
   - Pantry (toggle)
   - Meal Planner (toggle)

---

## Detailed Endpoint Audit

### 1. 🛒 **GROCERY MANAGER** (`GroceryManagerWorkspace.js`)

#### Current Endpoints (MIXED v1/v2):
```javascript
✅ /api/v2/grocery-lists/user/${userId}  [v2] - Get user lists
❌ /api/grocery-list [v1] - Legacy create
❌ /api/grocery-lists [v1] - Get/Create lists
❌ /api/grocery-lists/${listId} [v1] - Get/Update/Delete
❌ /api/pantry [v1] - Get pantry items
```

#### Migration Path:
| Current (v1) | Migrate To (v2) | Status | Notes |
|--------------|-----------------|--------|-------|
| `/api/grocery-lists` GET | `/api/v2/grocery-lists/user/${userId}` | ✅ DONE | Already using v2 for load |
| `/api/grocery-list` POST | `/api/v2/grocery-lists` | ❌ TODO | Create list |
| `/api/grocery-lists` POST | `/api/v2/grocery-lists` | ❌ TODO | Create list (duplicate?) |
| `/api/grocery-lists/${id}` GET | `/api/v2/grocery-lists/${id}` | ❌ TODO | Get single list |
| `/api/grocery-lists/${id}` PUT | `/api/v2/grocery-lists/${id}` | ❌ TODO | Update list |
| `/api/grocery-lists/${id}` DELETE | `/api/v2/grocery-lists/${id}` | ❌ TODO | Delete list |
| `/api/pantry` GET | `/api/v2/pantry` | ❌ TODO | Get pantry (needs v2 endpoint) |

**Database Tables Used:**
- `grocery_lists` (name, list_data, created_at, updated_at)
- `pantry` (if exists)

---

### 2. 📅 **MEAL PLANNER** (`LoadMealPlanPanel.js`, `MealPlannerPanel.js`)

#### Current Endpoints (ALL v1):
```javascript
❌ /api/meal-plans [v1] - GET, POST
❌ /api/meal-plans/${planId} [v1] - GET, PUT, DELETE
```

#### Migration Path:
| Current (v1) | Migrate To (v2) | Status | Notes |
|--------------|-----------------|--------|-------|
| `/api/meal-plans` GET | `/api/v2/meal-plans/user/${userId}` | ❌ TODO | Get user plans |
| `/api/meal-plans` POST | `/api/v2/meal-plans` | ❌ TODO | Create plan |
| `/api/meal-plans/${id}` GET | `/api/v2/meal-plans/${id}` | ❌ TODO | Get single plan |
| `/api/meal-plans/${id}` PUT | `/api/v2/meal-plans/${id}` | ❌ TODO | Update plan |
| `/api/meal-plans/${id}` DELETE | `/api/v2/meal-plans/${id}` | ❌ TODO | Delete plan |

**Database Tables Used:**
- `meal_plans` (needs schema audit)

**V2 Endpoint Exists:** ❓ UNKNOWN - Need to check

---

### 3. 🥘 **PANTRY** (`PantryPanel.js`)

#### Current Endpoints (ALL v1):
```javascript
❌ /api/pantry [v1] - GET
❌ /api/pantry/status [v1] - GET status
❌ /api/config/pantry/toggle [v1] - Toggle feature
❌ /api/ingredients [v1] - Search ingredients
❌ /api/ingredients?query=... [v1] - Autocomplete
```

#### Migration Path:
| Current (v1) | Migrate To (v2) | Status | Notes |
|--------------|-----------------|--------|-------|
| `/api/pantry` GET | `/api/v2/pantry/user/${userId}` | ❌ TODO | Get pantry items |
| `/api/pantry/status` GET | `/api/v2/pantry/status` | ❌ TODO | Feature status |
| `/api/ingredients` GET | `/api/v2/ingredients` | ❌ TODO | Ingredient search |

**Database Tables Used:**
- `pantry` (needs schema audit)
- `ingredients` (reference table)

**V2 Endpoint Exists:** ❓ UNKNOWN - Need to create

---

### 4. 📖 **COOKBOOK/RECIPES** (`RecipeListView.js`, Admin components)

#### Current Endpoints (ALL v1):
```javascript
❌ /api/recipes [v1] - GET, POST
❌ /api/recipes/${id} [v1] - GET, PUT, DELETE
❌ /api/recipes/${id}/claim [v1] - POST
❌ /api/recipes/${id}/edit [v1] - POST
❌ /api/recipes/${id}/category [v1] - PUT
❌ /api/recipes/${id}/info [v1] - GET
❌ /api/user/recipes [v1] - GET user's recipes
❌ /api/search [v1] - Search recipes
❌ /api/search/intelligent [v1] - AI search
❌ /api/categories [v1] - Get categories
```

#### Migration Path:
| Current (v1) | Migrate To (v2) | Status | Notes |
|--------------|-----------------|--------|-------|
| `/api/recipes` GET | `/api/v2/recipes` | ❌ TODO | List recipes |
| `/api/recipes` POST | `/api/v2/recipes` | ❌ TODO | Create recipe |
| `/api/recipes/${id}` GET | `/api/v2/recipes/${id}` | ❌ TODO | Get recipe |
| `/api/recipes/${id}` PUT | `/api/v2/recipes/${id}` | ❌ TODO | Update recipe |
| `/api/recipes/${id}` DELETE | `/api/v2/recipes/${id}` | ❌ TODO | Delete recipe |
| `/api/user/recipes` GET | `/api/v2/recipes/user/${userId}` | ❌ TODO | User's recipes |
| `/api/search` GET | `/api/v2/recipes/search` | ❌ TODO | Search |
| `/api/categories` GET | `/api/v2/categories` | ❌ TODO | Categories |

**Database Tables Used:**
- `recipes` (needs schema audit)
- `recipe_categories`
- `user_recipes` (junction table)

**V2 Endpoint Exists:** ❓ UNKNOWN - Need to create

---

### 5. 👥 **COMMUNITY** (`CommunityBrowserNew.js`)

#### Current Endpoints (ALL v1):
```javascript
❌ /api/community/recipes [v1] - GET
```

#### Migration Path:
| Current (v1) | Migrate To (v2) | Status | Notes |
|--------------|-----------------|--------|-------|
| `/api/community/recipes` GET | `/api/v2/community/recipes` | ❌ TODO | Browse community |

**Database Tables Used:**
- `recipes` (where is_public = true)

**V2 Endpoint Exists:** ❓ UNKNOWN - Need to create

---

### 6. 👫 **FRIENDS** (`FriendsView.js`)

#### Current Endpoints:
```javascript
⚠️ NO API CALLS FOUND - Component may be placeholder
```

#### Migration Path:
| Feature | V2 Endpoint Needed | Status |
|---------|-------------------|--------|
| Get friends | `/api/v2/friends/user/${userId}` | ❌ TODO |
| Add friend | `/api/v2/friends` POST | ❌ TODO |
| Remove friend | `/api/v2/friends/${id}` DELETE | ❌ TODO |

**Database Tables Used:**
- `friends` (or similar - needs audit)

**V2 Endpoint Exists:** ❓ UNKNOWN

---

### 7. 🏠 **HOUSEHOLDS** (`HouseholdSelector.js`)

#### Current Endpoints:
```javascript
✅ /api/v2/households [v2] - Already using v2!
✅ /api/v2/households/user/${userId} [v2] - Get user households
```

#### Status:
**✅ ALREADY V2! No migration needed.**

**Database Tables Used:**
- `households`
- `household_members`

---

### 8. 📸 **IMPORT** (`ImportRecipeModal.js`, `PhotoImportModal.js`)

#### Current Endpoints (ALL v1):
```javascript
❌ /api/recipes/import/ocr [v1] - OCR processing
❌ /api/recipes/voice/session/process [v1] - Voice import
```

#### Migration Path:
| Current (v1) | Migrate To (v2) | Status | Notes |
|--------------|-----------------|--------|-------|
| `/api/recipes/import/ocr` POST | `/api/v2/recipes/import/ocr` | ❌ TODO | Photo OCR |
| `/api/recipes/voice/session/process` POST | `/api/v2/recipes/import/voice` | ❌ TODO | Voice |

**Database Tables Used:**
- `recipes`
- Temp tables for processing

---

### 9. 🎨 **WHITEBOARD** (`WhiteboardApp.js`)

#### Current Endpoints:
```javascript
✅ /api/v2/whiteboards [v2] - Already using v2!
✅ /api/v2/whiteboard/... [v2] - All whiteboard operations
```

#### Status:
**✅ ALREADY V2! No migration needed.**

**Database Tables Used:**
- `wb` (whiteboards)
- `grocery_lists` (for grocery list widgets)

---

### 10. 🔧 **ADMIN** (`AdminDashboard.js`, `AdminRecipeOverlay.js`)

#### Current Endpoints (ALL v1):
```javascript
❌ /api/admin/check-access [v1]
❌ /api/admin/recipes/... [v1] - Various admin operations
❌ /api/admin/recipes/${id}/promote [v1]
❌ /api/admin/recipes/${id}/demote [v1]
❌ /api/admin/recipes/bulk-delete/... [v1]
```

#### Migration Path:
| Current (v1) | Migrate To (v2) | Status | Notes |
|--------------|-----------------|--------|-------|
| `/api/admin/check-access` GET | `/api/v2/admin/auth/check` | ❌ TODO | Auth check |
| `/api/admin/recipes/*` | `/api/v2/admin/recipes/*` | ❌ TODO | Admin operations |

**Database Tables Used:**
- `recipes`
- `users` (for admin permissions)

---

### 11. 📊 **ACTIVITY FEED** (`ActivityFeed.js`)

#### Current Endpoints:
```javascript
✅ /api/v2/activity/mark-read [v2] - Already using v2!
✅ /api/v2/activity/households/${id} [v2] - Get household activity
```

#### Status:
**✅ ALREADY V2! No migration needed.**

**Database Tables Used:**
- `household_activity`

---

## Summary Statistics

### Endpoint Status:
- ✅ **Already V2:** 4 features (Whiteboard, Households, Activity Feed, Grocery List Load)
- ❌ **Needs Migration:** 7 features
- ⚠️ **Needs Creation:** ~35+ endpoints

### Migration Priority (High to Low):

1. **🛒 Grocery Lists** - Partially done, finish remaining endpoints (HIGH)
2. **📖 Recipes** - Core feature, most endpoints (HIGH)
3. **📅 Meal Plans** - Important feature (MEDIUM)
4. **🥘 Pantry** - Important feature (MEDIUM)
5. **📸 Import** - Specialized feature (LOW)
6. **👥 Community** - Social feature (LOW)
7. **👫 Friends** - May be incomplete (LOW)
8. **🔧 Admin** - Internal tools (LOW)

---

## Database Schema Audit Needed

To complete v2 migration, we need to audit these tables:

1. ✅ `grocery_lists` - Already done (Phase 2)
2. ❌ `meal_plans` - Need to check columns
3. ❌ `pantry` - Need to check columns
4. ❌ `recipes` - Need to check columns
5. ❌ `recipe_categories` - Need to check structure
6. ❌ `friends` - Need to check if exists
7. ✅ `households` - Already v2 compatible
8. ✅ `household_activity` - Already v2 compatible

---

## Recommended Action Plan

### Phase 1: Complete Grocery Lists (1 hour)
- [x] Fix grocery list load endpoint
- [ ] Migrate remaining 5 endpoints to v2
- [ ] Test all operations

### Phase 2: Create Missing V2 Endpoints (4-6 hours)
- [ ] Meal Plans v2 endpoints
- [ ] Pantry v2 endpoints  
- [ ] Recipes v2 endpoints (largest)

### Phase 3: Frontend Migration (2-3 hours)
- [ ] Update all fetch calls to use v2
- [ ] Remove v1 endpoint references
- [ ] Test each feature

### Phase 4: Cleanup (1 hour)
- [ ] Deprecate hungie_server.py routes
- [ ] Drop legacy database columns
- [ ] Update documentation

**Total Estimated Time:** 8-11 hours

---

## Next Steps

1. **Start with Grocery Lists** - Finish what we started
2. **Audit remaining database tables** - Document current schema
3. **Create v2 endpoints systematically** - One feature at a time
4. **Migrate frontend in phases** - Test after each migration
5. **Delete legacy code** - Clean up hungie_server.py

**Want to proceed?**
