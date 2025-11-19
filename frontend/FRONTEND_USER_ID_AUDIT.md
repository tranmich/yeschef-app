# Frontend `user_id` Audit Report

**Date:** November 19, 2025  
**Purpose:** Identify all API calls that may be missing `user_id` parameter

---

## 🎯 **Critical Components to Check:**

### **1. GroceryManagerWorkspace.js** ✅ FIXED
- **Issue:** Missing `user_id` in POST/PUT grocery list save
- **Status:** Fixed in commit `20ab191`
- **Location:** Line ~999

### **2. MealPlannerView.js** ⚠️ NEEDS CHECK
**API Calls to Verify:**
- `POST /api/v2/meal-plans` - Creating meal plans
- `PUT /api/v2/meal-plans/:id` - Updating meal plans
- `DELETE /api/v2/meal-plans/:id` - Deleting meal plans

**Search Pattern:**
```javascript
fetch(`${getApiUrl()}/api/v2/meal-plans
```

### **3. MainApp.js** ⚠️ NEEDS CHECK
**API Calls to Verify:**
- Recipe creation/edit/delete operations
- Any direct fetch calls bypassing api.js utilities

**Known Issues:**
- `createRecipeV2()` should include user_id in recipe data
- Check if `onRecipeEdit` properly passes user_id

### **4. PantryManager.js** ⚠️ NEEDS CHECK
**API Calls to Verify:**
- `POST /api/v2/pantry` - Adding pantry items
- `DELETE /api/v2/pantry/:id` - Removing items
- `PUT /api/v2/pantry/:id` - Updating items

### **5. CommunityBrowserNew.js** ⚠️ NEEDS CHECK
**API Calls to Verify:**
- `POST /api/v2/community/recipes` - Sharing recipes
- `POST /api/v2/community/recipes/:id/like` - Liking recipes
- `POST /api/v2/community/recipes/:id/claim` - Claiming recipes

### **6. ActivityFeed.js** ⚠️ NEEDS CHECK
**API Calls to Verify:**
- `POST /api/v2/activity/mark-read` - Marking notifications read
- Should include `user_id` in request body

### **7. FriendsView.js** ⚠️ NEEDS CHECK
**API Calls to Verify:**
- `POST /api/v2/friends/request` - Sending friend requests
- `POST /api/v2/friends/request/:id/accept` - Accepting requests
- `DELETE /api/v2/friends/:id` - Removing friends

### **8. WhiteboardApp.js** ⚠️ NEEDS CHECK
**API Calls to Verify:**
- Whiteboard create/update/delete
- Recipe adding to whiteboard
- Meal plan operations
- Grocery list operations

**Note:** Whiteboards may pass user_id through different mechanisms

---

## 🔍 **How to Audit Each Component:**

### **Step 1: Search for Direct Fetch Calls**
```bash
# In PowerShell:
Get-ChildItem -Path src/components -Filter ComponentName.js | 
  Select-String -Pattern "fetch\(" -Context 0,10
```

### **Step 2: Check for JSON.stringify Bodies**
Look for patterns like:
```javascript
body: JSON.stringify({
    // Check if user_id is included
})
```

### **Step 3: Verify Against Backend Requirements**
- Check backend route decorators for `@jwt_required_v2`
- Check if route extracts `user_id` from request body or token
- Some routes get user_id from JWT token automatically

---

## 📋 **Backend API Requirements:**

### **Routes That REQUIRE user_id in Body:**
1. `POST /api/v2/recipes` - ✅ Requires user_id
2. `POST /api/v2/meal-plans` - ✅ Requires user_id
3. `POST /api/v2/grocery-lists` - ✅ Requires user_id (FIXED)
4. `PUT /api/v2/grocery-lists/:id` - ✅ Requires user_id (FIXED)
5. `POST /api/v2/pantry` - ⚠️ Check backend
6. `POST /api/v2/community/recipes` - ⚠️ Check backend
7. `POST /api/v2/friends/request` - ⚠️ Check backend

### **Routes That Get user_id from JWT:**
Some routes use `@jwt_required_v2` decorator and extract user_id from token:
- Look for `request.user_id` in backend code
- These don't need user_id in body

---

## 🛠️ **Recommended Fix Pattern:**

### **Before (Missing user_id):**
```javascript
const response = await fetch(url, {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        name: 'My Item',
        data: itemData
    })
});
```

### **After (With user_id):**
```javascript
const response = await fetch(url, {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        user_id: currentUser?.id,  // ✅ Added
        name: 'My Item',
        data: itemData
    })
});
```

---

## 🎯 **Next Steps:**

1. **Run Component-Specific Audits:**
   - Check each component listed above
   - Search for fetch/POST/PUT/PATCH patterns
   - Verify user_id is included where needed

2. **Test in Production:**
   - Try each feature after login
   - Watch browser console for 400 errors
   - Look for "user_id is required" messages

3. **Create Automated Test:**
   - Script to test all user operations
   - Verify no 400 errors occur
   - Check data persists correctly

4. **Backend Verification:**
   - Review backend route handlers
   - Document which routes extract user_id from JWT
   - Document which routes require it in body

---

## 📊 **Priority Order:**

### **HIGH PRIORITY** (User-facing features):
1. ✅ GroceryManagerWorkspace - FIXED
2. ⚠️ MainApp (recipe operations)
3. ⚠️ MealPlannerView
4. ⚠️ PantryManager

### **MEDIUM PRIORITY** (Social features):
5. ⚠️ CommunityBrowserNew
6. ⚠️ FriendsView
7. ⚠️ ActivityFeed

### **LOW PRIORITY** (Advanced features):
8. ⚠️ WhiteboardApp (complex, test thoroughly)

---

## 🔧 **Bulk Fix Strategy:**

**Option A: Fix individually as bugs are found** (Current approach)
- Pros: Targeted, lower risk
- Cons: Slower, users hit errors

**Option B: Systematic audit and fix all at once** (Recommended)
- Pros: Comprehensive, prevents future bugs
- Cons: More upfront work, higher testing burden

**Recommendation:** Do Option B for HIGH PRIORITY components now, Option A for others.

---

## ✅ **Completed Fixes:**

1. `GroceryManagerWorkspace.js` - Added user_id to save operations (Commit: `20ab191`)

---

## 🚧 **Pending Fixes:**

Run these commands to find specific issues:

```powershell
# Check MealPlannerView
Get-Content src/components/MealPlannerView.js | Select-String -Pattern "fetch.*meal-plans" -Context 5

# Check MainApp  
Get-Content src/pages/MainApp.js | Select-String -Pattern "fetch.*recipes" -Context 5

# Check PantryManager
Get-Content src/components/PantryManager.js | Select-String -Pattern "fetch.*pantry" -Context 5
```

---

**Would you like me to audit a specific component in detail?**
