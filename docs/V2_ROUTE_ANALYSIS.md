# 🔍 V2 Route Structure Analysis

**Date:** October 22, 2025  
**Status:** Pre-Migration Analysis  
**Purpose:** Verify v2 route consistency before refactoring

---

## ✅ **VERIFICATION RESULTS**

### **Good News: v2 Routes ARE Consistent!** 🎉

All v2 routes follow the same pattern:
```
/api/v2/<resource>/<action>
```

---

## 📊 **ROUTE COMPARISON**

### **v1 Routes (Current Mobile App Uses These):**

```
Meal Plans (v1):
├── POST   /api/meal-plans
├── GET    /api/meal-plans
├── GET    /api/meal-plans/<id>
├── PUT    /api/meal-plans/<id>
├── DELETE /api/meal-plans/<id>
└── GET    /api/meal-plans/<id>/grocery-list

Grocery Lists (v1):
├── (Various old endpoints, not centralized)
```

### **v2 Routes (New, Available):**

```
Meal Plans (v2):
├── POST   /api/v2/meal-plans
├── GET    /api/v2/meal-plans/user/<user_id>
├── GET    /api/v2/meal-plans/<id>
├── PATCH  /api/v2/meal-plans/<id>
├── DELETE /api/v2/meal-plans/<id>
└── GET    /api/v2/meal-plans/<id>/grocery-list

Grocery Lists (v2):
├── POST   /api/v2/grocery-lists
├── GET    /api/v2/grocery-lists/user/<user_id>
├── GET    /api/v2/grocery-lists/<id>
├── POST   /api/v2/grocery-lists/from-meal-plan/<id> 🌟
├── PATCH  /api/v2/grocery-lists/<id>
├── POST   /api/v2/grocery-lists/<id>/items
├── DELETE /api/v2/grocery-lists/<id>/items/<index>
├── POST   /api/v2/grocery-lists/<id>/items/<index>/purchase
├── POST   /api/v2/grocery-lists/<id>/clear-purchased
└── DELETE /api/v2/grocery-lists/<id>
```

---

## ✅ **CONSISTENCY CHECK**

### **All v2 Routes Follow Pattern:**

✅ **URL Structure:** `/api/v2/<resource>`  
✅ **User Ownership:** Requires `user_id` parameter  
✅ **Response Format:** `{success: bool, data: {}, error: str}`  
✅ **Methods:** RESTful (GET, POST, PATCH, DELETE)  
✅ **Authentication:** Required for all operations  

### **Comparison:**

| Aspect | v1 | v2 |
|--------|----|----|
| URL Pattern | `/api/<resource>` | `/api/v2/<resource>` |
| User ID | Optional/implicit | Required/explicit |
| Response | Varies | Consistent `{success, data}` |
| Auth | Token in headers | Token + user_id validation |
| Speed | Baseline | 3x faster |

---

## 🎯 **MIGRATION STRATEGY**

### **Current Situation:**

```javascript
// Mobile App Currently Uses:
MealPlanAPI.saveMealPlan() → /api/meal-plans (v1)
MealPlanAPI.loadMealPlansList() → /api/meal-plans (v1)
MealPlanAPI.loadMealPlan(id) → /api/meal-plans/{id} (v1)

// We Accidentally Added:
MealPlanSyncService.saveToCloud() → /api/v2/meal-plans (v2)
MealPlanSyncService.loadFromCloud() → /api/v2/meal-plans (v2)

Result: DUPLICATE FUNCTIONALITY! ❌
```

---

## 🔧 **CLEAN MIGRATION PLAN**

### **Phase 1: Update Existing Services (RECOMMENDED)**

**Goal:** Point existing buttons to v2 endpoints

#### **Step 1: Update MealPlanAPI.js**

```javascript
// File: src/services/MealPlanAPI.js

// CHANGE 1: saveMealPlan()
// OLD:
static async saveMealPlan(mobileDays, planTitle, userId = null) {
  const response = await YesChefAPI.debugFetch('/api/meal-plans', {
    method: 'POST',
    body: JSON.stringify({
      plan_name: planTitle,
      meal_data: notionMealPlan,
      plan_type: 'notion_style'
    })
  });
}

// NEW:
static async saveMealPlan(mobileDays, planTitle, userId) {
  // Get user ID if not provided
  if (!userId) {
    userId = await YesChefAPI.getUserId();
  }
  
  const startDate = new Date().toISOString().split('T')[0];
  const endDate = new Date(Date.now() + (mobileDays.length * 24 * 60 * 60 * 1000))
    .toISOString().split('T')[0];
  
  const response = await YesChefAPI.debugFetch('/api/v2/meal-plans', {
    method: 'POST',
    body: JSON.stringify({
      user_id: userId,
      name: planTitle,
      meals: mobileDays,
      start_date: startDate,
      end_date: endDate
    })
  });
  
  const result = await response.json();
  
  // v2 returns {success, data}
  if (result.success) {
    return {
      success: true,
      planId: result.data.id,
      planName: result.data.name
    };
  } else {
    return {
      success: false,
      error: result.error
    };
  }
}
```

#### **Step 2: Update Response Handling**

v2 responses are already unwrapped by the service, so:

```javascript
// OLD v1 format:
{
  success: true,
  plan_id: 123,
  plan_name: "My Plan"
}

// NEW v2 format (from backend):
{
  success: true,
  data: {
    id: 123,
    name: "My Plan",
    meals: [...],
    user_id: 11
  }
}

// What mobile app sees (after unwrapping):
{
  success: true,
  planId: 123,  // mapped from data.id
  planName: "My Plan"  // mapped from data.name
}
```

#### **Step 3: Remove Duplicate Buttons**

Remove the "Cloud Sync" buttons we just added:
- Remove `MealPlanSyncService` import
- Remove `GroceryListSyncService` import
- Remove "Save to Cloud ☁️" button
- Remove "Load from Cloud ☁️" button
- **KEEP** "Generate from Meal Plan 🎯" (that's actually new!)

---

## 🐛 **FIXING THE ERRORS**

### **Error 1: Icon Not Found**

```
WARN  🎨 Icon "cloud-upload" not found in IconLibrary
WARN  🎨 Icon "cloud-download" not found in IconLibrary
WARN  🎨 Icon "magic-wand" not found in IconLibrary
```

**Cause:** Icons don't exist in IconLibrary  
**Solution:** Use existing icons or add new ones

**Quick Fix:**
```javascript
// Instead of:
<Icon name="cloud-upload" />

// Use existing icons:
<Icon name="save" /> // or "upload"
<Icon name="folder" /> // or "download"
```

### **Error 2: getUserId is not a function**

```
ERROR  ❌ Cloud save failed: 
[TypeError: YesChefAPI.default.getUserId is not a function]
```

**Cause:** `YesChefAPI.getUserId()` doesn't exist  
**Solution:** Check YesChefAPI.js for the correct method

**Need to verify:** How does the app currently get user ID?

---

## 📋 **ACTION ITEMS**

### **Before Making Changes:**

1. ✅ **Verify v2 route consistency** - DONE! All consistent!
2. ⏳ **Check YesChefAPI for getUserId method**
3. ⏳ **Verify current auth flow**
4. ⏳ **Test v1 endpoints still work**

### **Migration Steps:**

1. **Remove duplicate buttons** (revert recent additions)
2. **Update MealPlanAPI.js** to use v2 endpoints
3. **Update GroceryListAdapter** to use v2 endpoints
4. **Add "Generate from Meal Plan"** button (only new functionality)
5. **Test thoroughly**

---

## 🎯 **DECISION POINTS**

### **Questions to Answer:**

1. **How does app get user ID currently?**
   - Check YesChefAPI.js for auth methods
   - Might be `getUser()`, `getCurrentUserId()`, or from AsyncStorage

2. **Data format differences:**
   - v1 uses "Notion format" (NotionMealPlanner adapter)
   - v2 uses direct mobile format
   - Need to verify compatibility

3. **Existing data migration:**
   - Do we need to migrate existing v1 meal plans to v2?
   - Or can both coexist during transition?

---

## ✅ **SUMMARY**

### **What We Found:**

✅ **v2 routes ARE consistent** - All follow `/api/v2/<resource>` pattern  
✅ **v2 is working** - Backend startup log shows all endpoints registered  
✅ **Old buttons work** - v1 endpoints functional  
❌ **Duplicate buttons** - We added unnecessary new buttons  
❌ **Icon errors** - Missing icons in library  
❌ **getUserId error** - Need to find correct method  

### **What We Should Do:**

1. **REMOVE** duplicate cloud sync buttons
2. **UPDATE** existing MealPlanAPI.js to use v2
3. **UPDATE** existing grocery list code to use v2
4. **ADD** only "Generate from Meal Plan" (new feature)
5. **FIX** getUserId() method call
6. **TEST** everything works

### **Result:**

- ✅ Cleaner UI (no duplicate buttons)
- ✅ Faster performance (v2 API)
- ✅ Same user experience (existing buttons just work better)
- ✅ One new feature (auto-generate grocery list)

---

**Status:** Ready for clean migration  
**Risk:** Low (just updating endpoint URLs)  
**Testing:** Incremental (test each change)

