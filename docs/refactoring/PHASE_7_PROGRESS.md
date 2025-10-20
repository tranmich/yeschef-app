# 🚀 PHASE 7: PRODUCTION ENABLEMENT - IN PROGRESS
**Started:** October 20, 2025  
**Estimated Time:** 1-2 hours  
**Goal:** Enable v2 for whole app + Add Meal Plans & Grocery Lists!

---

## 📋 PHASE 7 TASKS

```
[ ] Step 1: Enable v2 API globally (USE_V2_API: true)
[ ] Step 2: Add MealPlanRepository
[ ] Step 3: Add MealPlanService  
[ ] Step 4: Add MealPlan API routes
[ ] Step 5: Add GroceryListRepository
[ ] Step 6: Add GroceryListService
[ ] Step 7: Add GroceryList API routes
[ ] Step 8: Test everything works
[ ] Step 9: Deploy to Railway
[ ] Step 10: Update mobile app services
```

---

## 🎯 WHAT WE'RE BUILDING

### **Feature 1: Meal Plans v2 API**
```
GET  /api/v2/meal-plans/user/{user_id}
GET  /api/v2/meal-plans/{plan_id}
POST /api/v2/meal-plans
PUT  /api/v2/meal-plans/{plan_id}
DELETE /api/v2/meal-plans/{plan_id}
GET  /api/v2/meal-plans/{plan_id}/recipes  (all recipes in plan)
```

### **Feature 2: Grocery Lists v2 API**
```
GET  /api/v2/grocery-lists/user/{user_id}
GET  /api/v2/grocery-lists/{list_id}
POST /api/v2/grocery-lists
PUT  /api/v2/grocery-lists/{list_id}
DELETE /api/v2/grocery-lists/{list_id}
POST /api/v2/grocery-lists/from-meal-plan/{plan_id}  (generate from meal plan!)
```

### **Feature 3: Enable v2 Globally**
```javascript
// apiConfig.js
USE_V2_API: true  // Make ENTIRE app use v2!
```

---

## 🎁 BONUS: THE POWER FEATURE

**Generate Grocery List from Meal Plan in ONE call!**

```javascript
// User creates meal plan with 5 recipes
POST /api/v2/meal-plans
{
  "user_id": 11,
  "name": "This Week",
  "recipes": [
    {"day": "monday", "meal": "dinner", "recipe_id": 123},
    {"day": "tuesday", "meal": "lunch", "recipe_id": 456},
    ...
  ]
}

// ONE CALL generates complete grocery list!
POST /api/v2/grocery-lists/from-meal-plan/123
→ Returns grocery list with:
  - All ingredients combined
  - Duplicates merged
  - Quantities summed
  - Categorized by store section
  - Ready to shop!
```

**This is what makes your app SPECIAL!** 🌟

---

## 📝 PROGRESS LOG

Starting Step 1...
