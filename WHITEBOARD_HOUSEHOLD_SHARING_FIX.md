# Whiteboard Household Data Sharing Fix

**Date:** November 19, 2025  
**Issue:** Whiteboard users in same household cannot see each other's recipes/meal plans  
**Root Cause:** V2 API enforces user_id ownership without household context

---

## 🔴 **Problem Statement:**

When user `test1@gmail.com` (ID: 13) views a whiteboard in household 11:
- ❌ Cannot see recipes created by `tran.mich@gmail.com` (ID: 11)
- ❌ Cannot see meal plans created by primary user
- ✅ Can see notes (stored in whiteboard, not user-owned)

**Error Logs:**
```
⚠️ Recipe 2609 not found, skipping
⚠️ Recipe 2690 not found, skipping
GET /api/meal-plans/194 404 (Not Found)
Failed to load meal plan 194: Error: Meal plan not found or access denied
```

---

## 🎯 **Solution: Household Context API**

### **Option 1: Add Household ID to Whiteboard API Calls (Quick Fix)**

**Frontend Change:**
```javascript
// WhiteboardApp.js - Add household_id to API calls
const loadRecipeForWhiteboard = async (recipeId) => {
  try {
    // Include household_id to enable household-level access
    const recipe = await api.get(`/api/v2/recipes/${recipeId}`, {
      params: {
        user_id: currentUser.id,
        household_id: currentHousehold.id  // ✅ New: Enable household sharing
      }
    });
    return recipe;
  } catch (error) {
    console.error(`Failed to load recipe ${recipeId}:`, error);
    return null;
  }
};
```

**Backend Change (recipes.py):**
```python
@recipe_bp.route('/<int:recipe_id>', methods=['GET'])
@handle_errors
def get_recipe(recipe_id):
    """
    Get recipe by ID with optional household context
    
    If household_id is provided and user is member of that household,
    allow access to any recipe owned by household members
    """
    recipe_service = get_recipe_service()
    user_id = request.args.get('user_id', type=int)
    household_id = request.args.get('household_id', type=int)  # ✅ New
    
    # If household_id provided, check household membership
    if household_id:
        from app.database.repositories.household_repository import HouseholdRepository
        household_repo = HouseholdRepository()
        
        # Verify user is in household
        if household_repo.is_member(household_id, user_id):
            # Get recipe with household context (allows access to any member's recipe)
            result = recipe_service.get_recipe_for_household(recipe_id, household_id)
            
            if result['success']:
                return jsonify(result), 200
            else:
                status_code = 404 if result.get('error_code') == 'NOT_FOUND' else 403
                return jsonify(result), status_code
    
    # Standard user-only access (existing behavior)
    result = recipe_service.get_recipe_by_id(recipe_id, user_id)
    
    if result['success']:
        return jsonify(result), 200
    else:
        status_code = 404 if result.get('error_code') == 'NOT_FOUND' else 403
        return jsonify(result), status_code
```

**Backend Service (recipe_service.py):**
```python
def get_recipe_for_household(self, recipe_id, household_id):
    """
    Get recipe for household context
    Allows any household member to view recipes created by other members
    """
    try:
        # Get recipe (no user_id filter, just household context)
        recipe = self.recipe_repository.get_by_id(recipe_id)
        
        if not recipe:
            return {
                'success': False,
                'error': 'Recipe not found',
                'error_code': 'NOT_FOUND'
            }
        
        # Verify recipe owner is in the household
        household_repo = HouseholdRepository()
        recipe_owner_id = recipe['user_id']
        
        if not household_repo.is_member(household_id, recipe_owner_id):
            return {
                'success': False,
                'error': 'Recipe owner not in household',
                'error_code': 'FORBIDDEN'
            }
        
        # Allow access
        return {
            'success': True,
            'data': recipe
        }
        
    except Exception as e:
        logger.error(f"Error getting recipe for household: {e}")
        return {
            'success': False,
            'error': 'Internal server error'
        }
```

---

### **Option 2: Whiteboard-Specific Endpoints (Recommended)**

Create dedicated endpoints for whiteboard data access that handle household context automatically:

**New Routes:**
```python
# app/api/v2/whiteboards.py - Add these routes

@whiteboard_bp.route('/<int:wid>/recipes/<int:recipe_id>', methods=['GET'])
def get_whiteboard_recipe(wid, recipe_id):
    """
    Get recipe in context of whiteboard
    Automatically checks household membership
    """
    user_id = request.args.get('user_id', type=int)
    
    # Get whiteboard to determine household
    whiteboard = whiteboard_service.get_whiteboard(wid, user_id)
    if not whiteboard['success']:
        return jsonify(whiteboard), 403
    
    household_id = whiteboard['data']['hid']
    
    # Get recipe with household context
    recipe = recipe_service.get_recipe_for_household(recipe_id, household_id)
    return jsonify(recipe), 200 if recipe['success'] else 404


@whiteboard_bp.route('/<int:wid>/meal-plans/<int:meal_plan_id>', methods=['GET'])
def get_whiteboard_meal_plan(wid, meal_plan_id):
    """
    Get meal plan in context of whiteboard
    Automatically checks household membership
    """
    user_id = request.args.get('user_id', type=int)
    
    # Get whiteboard to determine household
    whiteboard = whiteboard_service.get_whiteboard(wid, user_id)
    if not whiteboard['success']:
        return jsonify(whiteboard), 403
    
    household_id = whiteboard['data']['hid']
    
    # Get meal plan with household context
    meal_plan = meal_plan_service.get_meal_plan_for_household(meal_plan_id, household_id)
    return jsonify(meal_plan), 200 if meal_plan['success'] else 404
```

**Frontend Changes:**
```javascript
// frontend/src/utils/whiteboardAPI.js

export const getWhiteboardRecipe = async (whiteboardId, recipeId, userId) => {
  return apiCall(`/api/v2/whiteboard/${whiteboardId}/recipes/${recipeId}?user_id=${userId}`);
};

export const getWhiteboardMealPlan = async (whiteboardId, mealPlanId, userId) => {
  return apiCall(`/api/v2/whiteboard/${whiteboardId}/meal-plans/${mealPlanId}?user_id=${userId}`);
};
```

```javascript
// WhiteboardApp.js - Use new endpoints

const loadRecipeForWhiteboard = async (recipeId) => {
  try {
    const recipe = await whiteboardAPI.getWhiteboardRecipe(
      currentWhiteboardId,
      recipeId,
      currentUser.id
    );
    return recipe;
  } catch (error) {
    console.error(`Failed to load recipe ${recipeId}:`, error);
    return null;
  }
};
```

---

## 🔧 **Additional Fix: Pusher Presence Auth Error**

**Error:**
```
POST /api/v2/pusher/auth 500 (Internal Server Error)
app_id should be a string instead it is a <class 'NoneType'>
```

**Cause:** Missing Pusher environment variables on Railway

**Fix:** Add to Railway environment variables:
```bash
PUSHER_APP_ID=your_app_id
PUSHER_KEY=your_key
PUSHER_SECRET=your_secret
PUSHER_CLUSTER=us2
```

**Backend Check (pusher_auth.py):**
```python
import os
from pusher import Pusher

# Verify all Pusher env vars are set
required_vars = ['PUSHER_APP_ID', 'PUSHER_KEY', 'PUSHER_SECRET', 'PUSHER_CLUSTER']
missing = [var for var in required_vars if not os.getenv(var)]

if missing:
    logger.error(f"Missing Pusher environment variables: {missing}")
    raise ValueError(f"Missing required Pusher config: {missing}")

pusher_client = Pusher(
    app_id=os.getenv('PUSHER_APP_ID'),
    key=os.getenv('PUSHER_KEY'),
    secret=os.getenv('PUSHER_SECRET'),
    cluster=os.getenv('PUSHER_CLUSTER'),
    ssl=True
)
```

---

## 📋 **Implementation Checklist:**

### **Phase 1: Quick Fix (Option 1)**
- [ ] Update `recipes.py` - add household_id parameter support
- [ ] Update `meal_plans.py` - add household_id parameter support
- [ ] Add `get_recipe_for_household()` to RecipeService
- [ ] Add `get_meal_plan_for_household()` to MealPlanService
- [ ] Add `is_member()` to HouseholdRepository
- [ ] Update `WhiteboardApp.js` - pass household_id in API calls
- [ ] Test with multi-user household

### **Phase 2: Proper Solution (Option 2)**
- [ ] Create whiteboard-specific recipe endpoint
- [ ] Create whiteboard-specific meal plan endpoint
- [ ] Update `whiteboardAPI.js` - use new endpoints
- [ ] Update `WhiteboardApp.js` - call new API functions
- [ ] Add proper error handling

### **Phase 3: Pusher Fix**
- [ ] Add Pusher env vars to Railway
- [ ] Add env var validation in pusher_auth.py
- [ ] Test presence channel subscription
- [ ] Verify online/offline indicators work

---

## 🎯 **Recommended Approach:**

**Start with Option 2** (Whiteboard-specific endpoints) because:
1. ✅ Cleaner separation of concerns
2. ✅ Easier to add whiteboard-specific permissions later
3. ✅ More explicit about household context
4. ✅ Better error messages for debugging
5. ✅ Doesn't pollute existing recipe/meal plan APIs

**Implementation Time:** ~2 hours
- Backend: 1 hour (new endpoints + services)
- Frontend: 30 minutes (update API calls)
- Testing: 30 minutes (multi-user scenarios)

---

## 📊 **Expected Result:**

After fix:
```
✅ test1@gmail.com can see recipes created by tran.mich@gmail.com
✅ Recipes load on whiteboard for all household members
✅ Meal plans load for all household members
✅ Pusher presence shows online users correctly
✅ Real-time collaboration works across users
```

---

**Status:** Ready to implement  
**Priority:** HIGH - Blocks core whiteboard collaboration feature
