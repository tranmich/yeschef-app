# Whiteboard Guest Access Troubleshooting Guide

**Date:** November 19, 2025  
**Purpose:** Diagnose and fix household member access to shared whiteboards

---

## 🔍 **Information Needed for Troubleshooting:**

### **1. User Information**
```javascript
// From browser console (both users):
console.log('Current User:', {
  id: currentUser?.id,
  email: currentUser?.email,
  name: currentUser?.name
});

// Example Output:
// Guest: {id: 13, email: 'test1@gmail.com', name: 'test1'}
// Owner: {id: 11, email: 'tran.mich@gmail.com', name: 'YesChef'}
```

### **2. Household Membership**
```javascript
// Check household members
fetch('https://yeschefapp-production.up.railway.app/api/v2/households/11', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
  }
})
.then(r => r.json())
.then(d => console.log('Household Members:', d));

// Expected Output:
{
  success: true,
  data: {
    id: 11,
    name: "Test Household",
    members: [
      {user_id: 11, role: 'owner', email: 'tran.mich@gmail.com'},
      {user_id: 13, role: 'member', email: 'test1@gmail.com'}
    ]
  }
}
```

### **3. Whiteboard Access Check**
```javascript
// Check whiteboard details
fetch('https://yeschefapp-production.up.railway.app/api/v2/whiteboard/53', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
  }
})
.then(r => r.json())
.then(d => console.log('Whiteboard Access:', d));

// Expected Output:
{
  success: true,
  data: {
    id: 53,
    name: "Household Test",
    household_id: 11,  // ✅ Must match user's household
    objects: [...]
  }
}
```

### **4. Recipe Access (Household Context)**
```javascript
// Test household-aware recipe access
const whiteboardId = 53;
const recipeId = 2609;

fetch(`https://yeschefapp-production.up.railway.app/api/v2/whiteboard/${whiteboardId}/recipes/${recipeId}`, {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
  }
})
.then(r => r.json())
.then(d => console.log('Recipe Access:', d));

// Expected Output (Success):
{
  success: true,
  data: {
    id: 2609,
    title: "Chicken Soup",
    user_id: 11,  // Different user, same household
    author_name: "tran.mich@gmail.com"
  }
}

// Expected Output (Failure):
{
  success: false,
  error: "RECIPE_NOT_FOUND",
  message: "Recipe not found or not shared in this household"
}
```

### **5. Network Requests (Browser Console)**
```javascript
// Watch network tab for these patterns:

// ❌ BAD (old endpoint - user ownership check):
GET /api/v2/recipes/2609?user_id=13  → 404 Not Found

// ✅ GOOD (new endpoint - household check):
GET /api/v2/whiteboard/53/recipes/2609  → 200 OK
```

---

## 🏗️ **Access Flow Architecture:**

### **Step-by-Step Access Chain:**

```
1. User Login
   ↓
2. JWT Token Generated (contains user_id)
   ↓
3. User Navigates to Household
   ↓
4. Check: User in household_members table?
   ├─ NO → 403 Forbidden (not a member)
   └─ YES → Continue
   ↓
5. User Opens Whiteboard
   ↓
6. Check: Whiteboard.household_id matches user's household?
   ├─ NO → 403 Forbidden (wrong household)
   └─ YES → Continue
   ↓
7. Whiteboard Loads Objects (recipes, meal plans, notes)
   ↓
8. For Each Recipe Card:
   ├─ Check: Recipe owner in same household?
   │  ├─ NO → Skip (not shared)
   │  └─ YES → Load recipe data
   ↓
9. For Each Meal Plan:
   ├─ Check: Meal plan owner in same household?
   │  ├─ NO → Skip (not shared)
   │  └─ YES → Load meal plan data
   ↓
10. Display Whiteboard with Accessible Objects
```

---

## 🧪 **Diagnostic Checklist:**

### **Phase 1: Authentication**
- [ ] User can login successfully
- [ ] JWT token stored in localStorage
- [ ] Token not expired (check `exp` claim)
- [ ] User ID extracted from token correctly

**Test:**
```javascript
const token = localStorage.getItem('authToken');
const payload = JSON.parse(atob(token.split('.')[1]));
console.log('Token Payload:', payload);
// Should show: {sub: 13, email: 'test1@gmail.com', exp: ...}
```

### **Phase 2: Household Membership**
- [ ] User is in household_members table
- [ ] Correct household_id (should match whiteboard)
- [ ] Role is 'owner', 'member', or 'viewer'

**Test:**
```sql
-- Run on Railway PostgreSQL
SELECT * FROM household_members 
WHERE user_id = 13 AND household_id = 11;

-- Expected: 1 row with role
```

### **Phase 3: Whiteboard Access**
- [ ] Whiteboard exists (not soft-deleted)
- [ ] Whiteboard.household_id matches user's household
- [ ] GET /api/v2/whiteboard/{wid} returns 200

**Test:**
```javascript
// Should return whiteboard data, not 403
fetch('/api/v2/whiteboard/53', {headers: {Authorization: `Bearer ${token}`}})
```

### **Phase 4: Recipe Access (Household Context)**
- [ ] Recipe owner is in same household as guest
- [ ] Using household-aware endpoint (not direct recipe API)
- [ ] GET /api/v2/whiteboard/{wid}/recipes/{rid} returns 200

**Test:**
```javascript
// Old way (will fail):
fetch('/api/v2/recipes/2609?user_id=13')  // ❌ 404

// New way (should work):
fetch('/api/v2/whiteboard/53/recipes/2609')  // ✅ 200
```

### **Phase 5: Frontend Integration**
- [ ] WhiteboardApp.js uses whiteboardAPI.getWhiteboardRecipe()
- [ ] Not using direct api.get('/api/v2/recipes/...')
- [ ] Whiteboard ID passed to all data loading functions

---

## 🔴 **Common Failure Patterns:**

### **Pattern 1: Frontend Not Updated**
**Symptom:**
```
⚠️ Recipe 2609 not found, skipping
GET /api/v2/recipes/2609?user_id=13  404 (Not Found)
```

**Cause:** Frontend still using old direct recipe endpoint

**Fix:** Update WhiteboardApp.js to use household-aware endpoints:
```javascript
// ❌ OLD
const recipe = await api.get(`/api/v2/recipes/${recipeId}`);

// ✅ NEW
const recipe = await whiteboardAPI.getWhiteboardRecipe(whiteboardId, recipeId);
```

---

### **Pattern 2: User Not in Household**
**Symptom:**
```
GET /api/v2/whiteboard/53  403 (Forbidden)
Whiteboard not found or access denied
```

**Cause:** User not in household_members table

**Fix:** Add user to household:
```sql
INSERT INTO household_members (household_id, user_id, role)
VALUES (11, 13, 'member');
```

---

### **Pattern 3: Recipe Owner Not in Household**
**Symptom:**
```
GET /api/v2/whiteboard/53/recipes/2609  404 (Not Found)
Recipe not found or not shared in this household
```

**Cause:** Recipe owner (user_id=11) not in same household as guest

**Fix:** Verify recipe owner is household member:
```sql
-- Check recipe owner
SELECT user_id FROM recipes WHERE id = 2609;  -- Returns: 11

-- Check if owner in household
SELECT * FROM household_members 
WHERE user_id = 11 AND household_id = 11;  -- Must exist
```

---

### **Pattern 4: Wrong Household ID**
**Symptom:**
```
Whiteboard loads but shows no recipes/meal plans
All household-aware API calls return 404
```

**Cause:** Whiteboard.household_id doesn't match user's household

**Fix:** Update whiteboard's household:
```sql
UPDATE wb SET hid = 11 WHERE id = 53;
```

---

## 📊 **Backend Logging for Debugging:**

### **Add Debug Logging to whiteboards.py:**

```python
@whiteboard_bp.route('/<int:wid>/recipes/<int:recipe_id>', methods=['GET'])
@jwt_required_v2
@handle_errors
def get_whiteboard_recipe(wid, recipe_id):
    user_id = request.user_id
    
    logger.info(f"🔍 Recipe access attempt - User: {user_id}, Whiteboard: {wid}, Recipe: {recipe_id}")
    
    # Check whiteboard access
    cursor.execute("""...""")
    whiteboard = cursor.fetchone()
    
    if not whiteboard:
        logger.warning(f"❌ User {user_id} denied access to whiteboard {wid}")
        return jsonify({...}), 403
    
    household_id = whiteboard['household_id']
    logger.info(f"✅ User {user_id} has access to household {household_id}")
    
    # Check recipe
    cursor.execute("""...""")
    recipe = cursor.fetchone()
    
    if not recipe:
        logger.warning(f"❌ Recipe {recipe_id} not found in household {household_id}")
        return jsonify({...}), 404
    
    logger.info(f"✅ User {user_id} accessed recipe {recipe_id} (owner: {recipe['user_id']})")
    return jsonify({...}), 200
```

**Expected Logs (Success):**
```
🔍 Recipe access attempt - User: 13, Whiteboard: 53, Recipe: 2609
✅ User 13 has access to household 11
✅ User 13 accessed recipe 2609 (owner: 11)
```

**Expected Logs (Failure):**
```
🔍 Recipe access attempt - User: 13, Whiteboard: 53, Recipe: 2609
❌ User 13 denied access to whiteboard 53
```

---

## 🛠️ **Quick Diagnostic Commands:**

### **Run These in Railway PostgreSQL:**

```sql
-- 1. Check user's households
SELECT 
  h.id as household_id,
  h.name as household_name,
  hm.role,
  hm.joined_at
FROM household_members hm
JOIN households h ON hm.household_id = h.id
WHERE hm.user_id = 13;  -- Guest user

-- 2. Check whiteboard ownership
SELECT 
  wb.id,
  wb.n as name,
  wb.hid as household_id,
  h.name as household_name,
  wb.cby as created_by
FROM wb
JOIN households h ON wb.hid = h.id
WHERE wb.id = 53;

-- 3. Check recipe ownership and household membership
SELECT 
  r.id as recipe_id,
  r.title,
  r.user_id as owner_id,
  u.email as owner_email,
  hm.household_id
FROM recipes r
JOIN users u ON r.user_id = u.id
LEFT JOIN household_members hm ON r.user_id = hm.user_id
WHERE r.id = 2609;

-- 4. Check if both users in same household
SELECT 
  hm1.user_id as user1_id,
  u1.email as user1_email,
  hm2.user_id as user2_id,
  u2.email as user2_email,
  hm1.household_id
FROM household_members hm1
JOIN household_members hm2 ON hm1.household_id = hm2.household_id
JOIN users u1 ON hm1.user_id = u1.id
JOIN users u2 ON hm2.user_id = u2.id
WHERE hm1.user_id = 11  -- Owner
  AND hm2.user_id = 13  -- Guest
  AND hm1.household_id = 11;
```

---

## ✅ **Success Verification:**

After fixes are applied, test with these commands in browser console:

```javascript
// 1. Verify authentication
console.log('Auth Token:', localStorage.getItem('authToken') ? 'Present' : 'Missing');

// 2. Verify household access
const testHousehold = async () => {
  const response = await fetch('/api/v2/households/11', {
    headers: {Authorization: `Bearer ${localStorage.getItem('authToken')}`}
  });
  console.log('Household Access:', await response.json());
};
testHousehold();

// 3. Verify whiteboard access
const testWhiteboard = async () => {
  const response = await fetch('/api/v2/whiteboard/53', {
    headers: {Authorization: `Bearer ${localStorage.getItem('authToken')}`}
  });
  console.log('Whiteboard Access:', await response.json());
};
testWhiteboard();

// 4. Verify recipe access (household context)
const testRecipe = async () => {
  const response = await fetch('/api/v2/whiteboard/53/recipes/2609', {
    headers: {Authorization: `Bearer ${localStorage.getItem('authToken')}`}
  });
  console.log('Recipe Access:', await response.json());
};
testRecipe();
```

All four should return `{success: true, data: {...}}` ✅

---

## 📋 **Troubleshooting Workflow:**

```
START: Guest reports "can't see recipes"
  ↓
1. Get user info (id, email, household_id)
  ↓
2. Check household_members table
  ├─ Not member? → Add to household
  └─ Is member? → Continue
  ↓
3. Check whiteboard.household_id matches
  ├─ No match? → Update whiteboard household
  └─ Matches? → Continue
  ↓
4. Check recipe owner in same household
  ├─ Not in household? → Add owner to household
  └─ In household? → Continue
  ↓
5. Check frontend using correct endpoints
  ├─ Using old endpoints? → Update WhiteboardApp.js
  └─ Using new endpoints? → Continue
  ↓
6. Check network tab for 200 responses
  ├─ Still 404? → Check backend logs
  └─ Returns 200? → SUCCESS! ✅
```

---

**With this guide, you can diagnose guest access issues in under 5 minutes!** 🎯
