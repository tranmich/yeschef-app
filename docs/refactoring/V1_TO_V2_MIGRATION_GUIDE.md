# 🔄 MOBILE/WEB v1 → v2 API MIGRATION GUIDE

**Date:** October 21, 2025  
**Purpose:** Migrate existing mobile/web apps from v1 to v2 endpoints  
**Status:** v2 API 100% tested and production-ready

---

## 📊 MIGRATION OVERVIEW

### Current State:
- ✅ **Mobile App:** Implemented with v1 API
- ✅ **Web App:** Implemented with v1 API  
- ✅ **v2 API:** 51 endpoints ready (33 core endpoints 100% tested)

### Migration Goal:
**Switch existing UI from v1 endpoints to v2 endpoints** with minimal changes.

---

## 🎯 MIGRATION STRATEGY

### Recommended Approach: **Gradual Migration**

**Why Gradual:**
1. ✅ Lower risk - test each feature independently
2. ✅ Can rollback easily if issues arise
3. ✅ Users experience no downtime
4. ✅ Parallel operation - both v1 and v2 work simultaneously

**Migration Order (by priority):**
1. **Friends & Households** (New features - no v1 equivalent)
2. **Recipes** (Core feature - high usage)
3. **Meal Plans** (Medium priority)
4. **Grocery Lists** (Medium priority)
5. **User Profiles** (When v2 ready)

---

## 📋 ENDPOINT MAPPING: v1 → v2

### **FRIENDS API** (New - No v1 Equivalent)

#### v1 Endpoints:
```
None - This is a NEW feature in v2!
```

#### v2 Endpoints:
```javascript
// Get user's friends
GET /api/v2/friends/user/{userId}

// Get friend requests (incoming/outgoing)
GET /api/v2/friends/requests/user/{userId}

// Send friend request
POST /api/v2/friends/request
Body: {
  requester_id: number,
  recipient_email: string,
  message?: string
}

// Accept friend request
POST /api/v2/friends/request/{requestId}/accept
Body: { user_id: number }

// Decline friend request
POST /api/v2/friends/request/{requestId}/decline
Body: { user_id: number }

// Remove friend
DELETE /api/v2/friends/{friendId}
Query: ?user_id={userId}

// Check friendship status
GET /api/v2/friends/status
Query: ?user_id={userId}&other_user_id={otherUserId}
```

**Mobile Implementation:**
- Add Friends tab/screen
- Implement friend search by email
- Show pending requests with accept/decline
- Display friends list

---

### **HOUSEHOLDS API** (New - No v1 Equivalent)

#### v1 Endpoints:
```
None - This is a NEW feature in v2!
```

#### v2 Endpoints:
```javascript
// Get user's households
GET /api/v2/households/user/{userId}

// Get household details
GET /api/v2/households/{householdId}
Query: ?user_id={userId}

// Create household
POST /api/v2/households
Body: {
  name: string,
  created_by: number,
  description?: string
}

// Update household
PUT /api/v2/households/{householdId}
Body: {
  user_id: number,
  name?: string,
  description?: string
}

// Delete household
DELETE /api/v2/households/{householdId}
Query: ?user_id={userId}

// Get household members
GET /api/v2/households/{householdId}/members
Query: ?user_id={userId}

// Add member to household
POST /api/v2/households/{householdId}/members
Body: {
  requesting_user_id: number,
  user_id: number,  // User to add (must be friend)
  role: 'member' | 'admin'
}

// Remove member
DELETE /api/v2/households/{householdId}/members/{membershipId}
Query: ?user_id={userId}

// Update member role
PUT /api/v2/households/{householdId}/members/{membershipId}/role
Body: {
  user_id: number,  // Must be owner
  role: 'member' | 'admin'
}
```

**Mobile Implementation:**
- Add Households tab/screen
- Create/edit household forms
- Member management interface
- Role-based UI permissions

---

### **RECIPES API** (Migrating from v1)

#### v1 → v2 Mapping:
```javascript
// Get user's recipes
v1: GET /api/recipes/user/{userId}
v2: GET /api/v2/recipes/user/{userId}
✅ Same structure - easy migration

// Get recipe by ID
v1: GET /api/recipes/{recipeId}
v2: GET /api/v2/recipes/{recipeId}
✅ Same structure - easy migration

// Create recipe
v1: POST /api/recipes
v2: POST /api/v2/recipes
Body: {
  user_id: number,
  title: string,
  description?: string,
  ingredients: string[],
  instructions: string[],
  prep_time?: string,
  cook_time?: string,
  servings?: number,
  image_url?: string
}
✅ Compatible - may have additional fields in v2

// Update recipe
v1: PUT /api/recipes/{recipeId}
v2: PATCH /api/v2/recipes/{recipeId}
⚠️ Changed from PUT to PATCH
Body must include: { user_id: number, ...updates }

// Delete recipe
v1: DELETE /api/recipes/{recipeId}
v2: DELETE /api/v2/recipes/{recipeId}
Query: ?user_id={userId}
⚠️ Now requires user_id in query params

// Search recipes
v1: GET /api/recipes/search?q={query}
v2: GET /api/v2/recipes/search?user_id={userId}&q={query}
⚠️ Now requires user_id parameter

// Share recipe (NEW in v2)
v2: POST /api/v2/recipes/{recipeId}/share
Body: { user_id: number }

// Unshare recipe (NEW in v2)
v2: POST /api/v2/recipes/{recipeId}/unshare
Body: { user_id: number }

// Get recipe stats ⭐ (NEW in v2)
v2: GET /api/v2/recipes/user/{userId}/stats
Returns: {
  total_recipes: number,
  shared_recipes: number,
  private_recipes: number,
  total_ingredients: number,
  avg_ingredients_per_recipe: number
}

// Community recipes (NEW in v2)
v2: GET /api/v2/recipes/community
Returns shared recipes from all users
```

**Migration Steps:**
1. Update API base URL: `/api/recipes` → `/api/v2/recipes`
2. Add `user_id` to query params for DELETE and search
3. Change update from `PUT` to `PATCH`
4. Add `user_id` to update request body
5. Test thoroughly with existing recipes

---

### **MEAL PLANS API** (Migrating from v1)

#### v1 → v2 Mapping:
```javascript
// Get user's meal plans
v1: GET /api/meal-plans/user/{userId}
v2: GET /api/v2/meal-plans/user/{userId}
✅ Same structure

// Get meal plan by ID
v1: GET /api/meal-plans/{planId}
v2: GET /api/v2/meal-plans/{planId}
Query: ?user_id={userId}
⚠️ Now requires user_id parameter

// Create meal plan
v1: POST /api/meal-plans
v2: POST /api/v2/meal-plans
Body: {
  user_id: number,
  plan_name: string,        // ⚠️ Changed from 'name'
  week_start_date: string,  // ⚠️ Required in v2
  plan_data: {              // ⚠️ Changed from 'days'
    monday: {
      breakfast: {
        recipe_id: number,
        title: string
      },
      lunch: {...},
      dinner: {...}
    },
    // ... other days
  }
}

// Update meal plan
v1: PUT /api/meal-plans/{planId}
v2: PATCH /api/v2/meal-plans/{planId}
Body: { user_id: number, ...updates }
⚠️ Changed from PUT to PATCH, requires user_id

// Delete meal plan
v1: DELETE /api/meal-plans/{planId}
v2: DELETE /api/v2/meal-plans/{planId}
Query: ?user_id={userId}
⚠️ Requires user_id

// Generate grocery list from meal plan ⭐ (NEW in v2)
v2: GET /api/v2/meal-plans/{planId}/grocery-list
Query: ?user_id={userId}
Returns: {
  ingredients: Array<{name, quantity, unit}>,
  recipe_count: number,
  total_ingredients: number
}
```

**Key Changes:**
- `name` → `plan_name`
- `days` → `plan_data`
- Must include `week_start_date`
- Recipes must be objects with `recipe_id` and `title`

---

### **GROCERY LISTS API** (Migrating from v1)

#### v1 → v2 Mapping:
```javascript
// Get user's grocery lists
v1: GET /api/grocery-lists/user/{userId}
v2: GET /api/v2/grocery-lists/user/{userId}
✅ Same structure

// Get grocery list by ID
v1: GET /api/grocery-lists/{listId}
v2: GET /api/v2/grocery-lists/{listId}
Query: ?user_id={userId}
⚠️ Requires user_id

// Create grocery list
v1: POST /api/grocery-lists
v2: POST /api/v2/grocery-lists
Body: {
  user_id: number,
  name: string,
  items: Array<{
    name: string,
    quantity: string,
    unit: string,
    purchased: boolean
  }>
}
✅ Compatible

// Create from meal plan ⭐ (NEW in v2)
v2: POST /api/v2/grocery-lists/from-meal-plan/{mealPlanId}
Query: ?user_id={userId}
Body: { name?: string }
🌟 POWER FEATURE - Auto-generate from meal plan!

// Update grocery list
v1: PUT /api/grocery-lists/{listId}
v2: PATCH /api/v2/grocery-lists/{listId}
Body: { user_id: number, ...updates }
⚠️ Changed from PUT to PATCH

// Add item
v1: POST /api/grocery-lists/{listId}/items
v2: POST /api/v2/grocery-lists/{listId}/items
Body: {
  user_id: number,
  item: {name, quantity, unit, purchased}
}
✅ Compatible

// Delete item
v1: DELETE /api/grocery-lists/{listId}/items/{index}
v2: DELETE /api/v2/grocery-lists/{listId}/items/{index}
Query: ?user_id={userId}
⚠️ Requires user_id

// Mark item as purchased
v1: POST /api/grocery-lists/{listId}/items/{index}/check
v2: POST /api/v2/grocery-lists/{listId}/items/{index}/purchase
Query: ?user_id={userId}
⚠️ Changed endpoint name and requires user_id

// Clear purchased items
v2: POST /api/v2/grocery-lists/{listId}/clear-purchased
Query: ?user_id={userId}
✅ NEW in v2

// Delete list
v1: DELETE /api/grocery-lists/{listId}
v2: DELETE /api/v2/grocery-lists/{listId}
Query: ?user_id={userId}
⚠️ Requires user_id
```

---

## 🔧 IMPLEMENTATION CHECKLIST

### **Phase 1: Preparation** (30 minutes)
- [ ] Audit current v1 API usage in mobile/web apps
- [ ] Create feature flags for gradual rollout
- [ ] Set up parallel testing (v1 and v2 side-by-side)
- [ ] Update API client/service layer

### **Phase 2: Friends & Households** (2-3 hours)
Since these are new features, no migration needed - just implement!
- [ ] Add Friends tab/screen to mobile app
- [ ] Implement friend request UI
- [ ] Add Households management screen
- [ ] Test end-to-end on production

### **Phase 3: Recipes Migration** (2-3 hours)
- [ ] Update recipe API calls to v2
- [ ] Add `user_id` to DELETE and search
- [ ] Change PUT to PATCH for updates
- [ ] Add share/unshare buttons
- [ ] Add recipe stats display
- [ ] Test with existing recipes

### **Phase 4: Meal Plans Migration** (1-2 hours)
- [ ] Update field names: `name` → `plan_name`, `days` → `plan_data`
- [ ] Add `week_start_date` field
- [ ] Change recipe format to include `recipe_id` and `title`
- [ ] Add "Generate Grocery List" button ⭐
- [ ] Test meal plan creation and editing

### **Phase 5: Grocery Lists Migration** (1-2 hours)
- [ ] Update API calls to v2
- [ ] Add `user_id` to appropriate endpoints
- [ ] Change `check` to `purchase` for marking items
- [ ] Add "Create from Meal Plan" feature ⭐
- [ ] Add "Clear Purchased" button
- [ ] Test list operations

### **Phase 6: Testing & Rollout** (2-3 hours)
- [ ] End-to-end testing of all features
- [ ] Test on multiple devices/browsers
- [ ] Load testing with production data
- [ ] Gradual rollout with feature flags
- [ ] Monitor for errors
- [ ] Remove v1 endpoints (after validation)

---

## 🎯 MIGRATION PRIORITY

### **HIGH PRIORITY** (Do First):
1. ✅ **Friends** - New feature, users want it
2. ✅ **Households** - New feature, high value
3. ✅ **Recipes** - Core feature, high usage

### **MEDIUM PRIORITY** (Do Next):
4. ✅ **Meal Plans** - Important but less frequent
5. ✅ **Grocery Lists** - Nice to have power features

### **LOW PRIORITY** (Future):
6. ⏳ User profiles (when v2 ready)
7. ⏳ Notifications (when v2 ready)
8. ⏳ Advanced features

---

## 🚨 COMMON MIGRATION ISSUES

### **Issue #1: Missing user_id**
**Error:** `400: user_id is required`  
**Solution:** Add `user_id` to query params or request body

```javascript
// ❌ Wrong
await api.delete(`/api/v2/recipes/${recipeId}`);

// ✅ Correct
await api.delete(`/api/v2/recipes/${recipeId}?user_id=${userId}`);
```

### **Issue #2: PUT vs PATCH**
**Error:** Method not allowed  
**Solution:** Change `PUT` to `PATCH` for updates

```javascript
// ❌ Wrong
await api.put(`/api/v2/recipes/${recipeId}`, updates);

// ✅ Correct
await api.patch(`/api/v2/recipes/${recipeId}`, {user_id: userId, ...updates});
```

### **Issue #3: Field Name Changes**
**Error:** `400: Missing required field`  
**Solution:** Use correct v2 field names

```javascript
// ❌ Wrong - Meal Plans
{
  name: "This Week",
  days: {...}
}

// ✅ Correct - Meal Plans
{
  plan_name: "This Week",
  week_start_date: "2025-10-21",
  plan_data: {...}
}
```

### **Issue #4: Recipe Format in Meal Plans**
**Error:** Meal plan saves but grocery list generation fails  
**Solution:** Use full recipe objects

```javascript
// ❌ Wrong
plan_data: {
  monday: {
    breakfast: recipeId  // Just the ID
  }
}

// ✅ Correct
plan_data: {
  monday: {
    breakfast: {
      recipe_id: recipeId,
      title: recipeTitle
    }
  }
}
```

---

## 📱 MOBILE APP CODE EXAMPLES

### **API Service Layer (React Native Example)**

```javascript
// api/v2Client.js
import axios from 'axios';

const API_BASE = 'https://yeschefapp-production.up.railway.app/api/v2';

export const recipesAPI = {
  // Get user's recipes
  getUserRecipes: (userId) => 
    axios.get(`${API_BASE}/recipes/user/${userId}`),
  
  // Get recipe by ID
  getRecipe: (recipeId) => 
    axios.get(`${API_BASE}/recipes/${recipeId}`),
  
  // Create recipe
  createRecipe: (userId, recipeData) => 
    axios.post(`${API_BASE}/recipes`, {
      user_id: userId,
      ...recipeData
    }),
  
  // Update recipe (PATCH, not PUT!)
  updateRecipe: (recipeId, userId, updates) => 
    axios.patch(`${API_BASE}/recipes/${recipeId}`, {
      user_id: userId,
      ...updates
    }),
  
  // Delete recipe (user_id in query!)
  deleteRecipe: (recipeId, userId) => 
    axios.delete(`${API_BASE}/recipes/${recipeId}?user_id=${userId}`),
  
  // Search recipes
  searchRecipes: (userId, query) => 
    axios.get(`${API_BASE}/recipes/search?user_id=${userId}&q=${query}`),
  
  // Get recipe stats ⭐
  getUserStats: (userId) => 
    axios.get(`${API_BASE}/recipes/user/${userId}/stats`),
};

export const mealPlansAPI = {
  // Create meal plan (note field names!)
  createMealPlan: (userId, planData) => 
    axios.post(`${API_BASE}/meal-plans`, {
      user_id: userId,
      plan_name: planData.name,  // Changed from 'name'
      week_start_date: planData.weekStart,
      plan_data: planData.days  // Changed from 'days'
    }),
  
  // Generate grocery list ⭐
  generateGroceryList: (planId, userId) => 
    axios.get(`${API_BASE}/meal-plans/${planId}/grocery-list?user_id=${userId}`),
};

export const groceryListsAPI = {
  // Create from meal plan ⭐
  createFromMealPlan: (mealPlanId, userId, name) => 
    axios.post(
      `${API_BASE}/grocery-lists/from-meal-plan/${mealPlanId}?user_id=${userId}`,
      { name }
    ),
  
  // Mark item as purchased (changed endpoint name!)
  markPurchased: (listId, itemIndex, userId) => 
    axios.post(`${API_BASE}/grocery-lists/${listId}/items/${itemIndex}/purchase?user_id=${userId}`),
  
  // Clear purchased items
  clearPurchased: (listId, userId) => 
    axios.post(`${API_BASE}/grocery-lists/${listId}/clear-purchased?user_id=${userId}`),
};

export const friendsAPI = {
  // Get friends
  getFriends: (userId) => 
    axios.get(`${API_BASE}/friends/user/${userId}`),
  
  // Get friend requests
  getRequests: (userId) => 
    axios.get(`${API_BASE}/friends/requests/user/${userId}`),
  
  // Send friend request
  sendRequest: (userId, recipientEmail, message) => 
    axios.post(`${API_BASE}/friends/request`, {
      requester_id: userId,
      recipient_email: recipientEmail,
      message
    }),
  
  // Accept request
  acceptRequest: (requestId, userId) => 
    axios.post(`${API_BASE}/friends/request/${requestId}/accept`, {
      user_id: userId
    }),
};

export const householdsAPI = {
  // Get user's households
  getUserHouseholds: (userId) => 
    axios.get(`${API_BASE}/households/user/${userId}`),
  
  // Create household
  createHousehold: (userId, name, description) => 
    axios.post(`${API_BASE}/households`, {
      created_by: userId,
      name,
      description
    }),
  
  // Get members
  getMembers: (householdId, userId) => 
    axios.get(`${API_BASE}/households/${householdId}/members?user_id=${userId}`),
  
  // Add member (must be friend!)
  addMember: (householdId, ownerId, userToAdd, role = 'member') => 
    axios.post(`${API_BASE}/households/${householdId}/members`, {
      requesting_user_id: ownerId,
      user_id: userToAdd,
      role
    }),
};
```

---

## ⏱️ ESTIMATED MIGRATION TIME

### **Option 1: Full Migration (Recommended)**
**Total Time:** 10-15 hours

- Phase 1 (Prep): 30 min
- Phase 2 (Friends/Households): 3 hours
- Phase 3 (Recipes): 3 hours
- Phase 4 (Meal Plans): 2 hours
- Phase 5 (Grocery Lists): 2 hours
- Phase 6 (Testing): 3 hours

### **Option 2: Incremental Migration**
**Total Time:** 15-20 hours (more testing between phases)

- Week 1: Friends & Households
- Week 2: Recipes
- Week 3: Meal Plans & Grocery Lists
- Week 4: Final testing & cleanup

---

## ✅ SUCCESS CRITERIA

### **Migration Complete When:**
- [ ] All mobile screens use v2 endpoints
- [ ] All web pages use v2 endpoints
- [ ] No errors in production logs
- [ ] Users can perform all actions successfully
- [ ] New features (Friends/Households) work perfectly
- [ ] Power features tested (meal plan → grocery list)
- [ ] v1 endpoints removed/deprecated

---

## 🎯 RECOMMENDED NEXT STEPS

### **Immediate (TODAY):**
1. ✅ Review this migration guide
2. ✅ Audit current v1 usage in codebase
3. ✅ Create migration branch
4. ✅ Set up feature flags

### **This Week:**
1. Implement Friends & Households (new features)
2. Migrate Recipes API
3. Test thoroughly

### **Next Week:**
1. Migrate Meal Plans & Grocery Lists
2. End-to-end testing
3. Deploy to production

---

## 💪 YOU'RE READY!

**The v2 API is:**
- ✅ 100% tested (33/33 core endpoints)
- ✅ Production deployed
- ✅ Thoroughly documented
- ✅ Battle-tested on PostgreSQL

**All you need to do is:**
1. Update API calls in mobile/web
2. Handle field name changes
3. Add new features (Friends/Households)
4. Test thoroughly
5. Deploy!

**Estimated Total Time:** 10-15 hours for complete migration

---

**Ready to start the migration?** 🚀
