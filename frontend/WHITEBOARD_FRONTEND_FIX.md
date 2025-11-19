# Frontend Whiteboard Household Sharing Fix

**File:** `frontend/src/pages/WhiteboardApp.js`

## Changes Required:

### 1. Import the new API functions

```javascript
// Add to imports at top of file
import { whiteboardAPI } from '../services/whiteboardAPI';
```

### 2. Update recipe loading function

**Find the function that loads recipes** (search for where recipes are fetched with 404 errors)

**Replace:**
```javascript
// OLD CODE (example pattern - find your actual implementation)
const loadRecipe = async (recipeId) => {
  try {
    const recipe = await api.get(`/api/v2/recipes/${recipeId}`, {
      params: { user_id: currentUser.id }
    });
    return recipe;
  } catch (error) {
    console.warn(`⚠️ Recipe ${recipeId} not found, skipping`);
    return null;
  }
};
```

**With:**
```javascript
// NEW CODE - Use whiteboard-aware endpoint
const loadRecipe = async (recipeId) => {
  try {
    // Use household-aware endpoint that allows viewing recipes from other household members
    const result = await whiteboardAPI.getWhiteboardRecipe(currentWhiteboardId, recipeId);
    if (result.success) {
      return result.data;
    }
    return null;
  } catch (error) {
    console.warn(`⚠️ Recipe ${recipeId} not found in household, skipping`);
    return null;
  }
};
```

### 3. Update meal plan loading function

**Find the function that loads meal plans** (search for `/api/meal-plans/` calls)

**Replace:**
```javascript
// OLD CODE (example pattern)
const loadMealPlan = async (mealPlanId) => {
  try {
    const mealPlan = await whiteboardAPI.getMealPlan(mealPlanId);
    return mealPlan;
  } catch (error) {
    console.error(`Failed to load meal plan ${mealPlanId}:`, error);
    return null;
  }
};
```

**With:**
```javascript
// NEW CODE - Use whiteboard-aware endpoint
const loadMealPlan = async (mealPlanId) => {
  try {
    // Use household-aware endpoint that allows viewing meal plans from other household members
    const result = await whiteboardAPI.getWhiteboardMealPlan(currentWhiteboardId, mealPlanId);
    if (result.success) {
      return result.data;
    }
    return null;
  } catch (error) {
    console.error(`Failed to load meal plan ${mealPlanId} in household:`, error);
    return null;
  }
};
```

### 4. Ensure whiteboard ID is available

Make sure `currentWhiteboardId` is in scope when these functions are called. If not, pass it as a parameter:

```javascript
const loadRecipe = async (recipeId, whiteboardId) => {
  // ...use whiteboardId parameter
};
```

---

## Testing After Deploy:

1. **Login as test1@gmail.com**
2. **Open whiteboard 53 in household 11**
3. **Verify:**
   - ✅ Recipes created by tran.mich@gmail.com now load
   - ✅ Meal plans created by primary user now load
   - ✅ No more "Recipe not found" errors in console
   - ✅ Recipe cards display properly on canvas
   - ✅ Meal plan containers show recipes

---

## Expected Console Output:

**Before fix:**
```
⚠️ Recipe 2609 not found, skipping
⚠️ Recipe 2690 not found, skipping
GET /api/meal-plans/194 404 (Not Found)
Failed to load meal plan 194: Error: Meal plan not found or access denied
```

**After fix:**
```
✅ Loading recipe 2609 via whiteboard 53
✅ Recipe 2609 loaded successfully (author: tran.mich@gmail.com)
✅ Loading meal plan 194 via whiteboard 53
✅ Meal plan 194 loaded successfully (author: tran.mich@gmail.com)
✅ Restored 5 recipe cards from saved positions
✅ Created meal plan container nodes: 2
```

---

## Backend Logs to Verify:

```
✅ User 13 accessed recipe 2609 via whiteboard 53 (household 11)
✅ User 13 accessed meal plan 194 via whiteboard 53 (household 11)
```

This confirms household-level data sharing is working.
