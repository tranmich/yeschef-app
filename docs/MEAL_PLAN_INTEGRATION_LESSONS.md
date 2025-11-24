# Meal Plan Integration - Lessons Learned
**Date:** November 5, 2025  
**Feature:** Meal plan day box widgets on whiteboard  
**Status:** ✅ Resolved after multiple iterations

---

## What We Built
Draggable meal plan "day boxes" on the whiteboard canvas that:
- Display day name and recipe count
- Can be renamed by clicking
- Generate grocery lists from contained recipes
- Persist position and data across page refreshes

---

## Issues Encountered & Solutions

### Issue 1: API Endpoint Mismatch
**Problem:** Frontend calling `/api/user/meal-plans` but endpoint is `/api/meal-plans`  
**Symptom:** `404 Not Found` or CORS errors  
**Root Cause:** Mixed V1/V2 API patterns, unclear documentation  
**Solution:**
```javascript
// ❌ Wrong
await apiCall('/api/user/meal-plans', {...})

// ✅ Correct
await apiCall('/api/meal-plans', {...})
```
**Lesson:** Always verify endpoint paths with `flask routes | grep meal` before frontend integration

---

### Issue 2: Response Format Mismatch
**Problem:** `Cannot read properties of undefined (reading 'id')`  
**Symptom:** JavaScript errors on save  
**Root Cause:** Expected `result.data.id` but API returns `result.plan_id`  
**Solution:**
```javascript
// ❌ Wrong assumption
const newId = result.data.id || result.data.meal_plan?.id;

// ✅ Check actual response
const newId = result.plan_id;  // From API: {success: true, plan_id: 123}
```
**Lesson:** Test API endpoints with curl first to see actual response format

---

### Issue 3: Stub Endpoint Returning Fake Data
**Problem:** `createObject` was a stub returning `{id: 1001, _stub: true}`  
**Symptom:** Widget saves successfully but doesn't persist to database  
**Root Cause:** Phased API development left critical endpoint unimplemented  
**Solution:** Implemented full `create_object` endpoint with actual database INSERT
```python
# Before: Stub
return jsonify({'success': True, 'data': {'id': 1001, '_stub': True}}), 201

# After: Real implementation
cursor.execute("""
    INSERT INTO wbo (wid, t, rid, gid, mid, p, ...)
    VALUES (%s, %s, %s, %s, %s, %s::jsonb, ...)
    RETURNING id, ...
""", (...))
```
**Lesson:** Identify and remove stubs BEFORE building dependent features

---

### Issue 4: Schema Column Name Mismatch  
**Problem:** `column "et" of relation "wbo" does not exist`  
**Symptom:** 500 Internal Server Error on save  
**Root Cause:** Assumed frontend naming (`entity_type`) matched database columns  
**Solution:** Checked actual schema and used correct abbreviated columns
```sql
-- ❌ Wrong assumption
INSERT INTO wbo (wid, t, et, eid, ...)  -- entity_type, entity_id

-- ✅ Actual schema
INSERT INTO wbo (wid, t, rid, gid, mid, ...)  -- recipe_id, grocery_list_id, meal_plan_id
```
**Lesson:** ALWAYS check schema with `\d+ table_name` before writing queries

---

### Issue 5: Array Constraint Violation
**Problem:** `cannot get array length of a non-array`  
**Symptom:** 500 error on INSERT  
**Root Cause:** CHECK constraint requires position to be 5-element array  
**Solution:** Validate and default position array
```python
# ❌ Wrong - didn't validate
position = data.get('position')
INSERT INTO wbo (..., p, ...) VALUES (..., %s::jsonb, ...)

# ✅ Correct - validate and default
position = data.get('position', [0, 0, 300, 400, 0])
if not isinstance(position, list) or len(position) != 5:
    position = [0, 0, 300, 400, 0]
```
**Lesson:** Check table constraints with `\d+ table_name` and validate inputs

---

### Issue 6: Infinite Render Loop
**Problem:** Widget re-rendering hundreds of times per second  
**Symptom:** Browser freezes, console spam  
**Root Cause:** `onPositionChange` callback in dependency array triggering re-renders  
**Solution:** Only call position callback on mouseUp, not mousemove
```javascript
// ❌ Wrong - triggers on every pixel movement
const handleMouseMove = (e) => {
  const newPos = calculatePosition(e);
  setPosition(newPos);
  onPositionChange(newPos);  // ← Triggers parent re-render
};

// ✅ Correct - only notify on drag end
const handleMouseUp = (e) => {
  setIsDragging(false);
  onPositionChange(canvasPosition);  // ← Only once
};
```
**Lesson:** Be careful with callbacks in React effect dependencies

---

### Issue 7: V1 API Response Format Mismatch
**Problem:** `Meal plan 170 not found` even though API returned success  
**Symptom:** Widget saves but doesn't reload after page refresh  
**Root Cause:** V1 API returns `{success: true, meal_plan: {...}}` not `{success: true, data: {...}}`  
**Solution:** Access response fields correctly based on V1 format
```javascript
// ❌ Wrong - assumed V2 response format
if (response.success && response.data) {
  mealPlanDataMap[planId] = response.data.meal_plan || response.data;
}

// ✅ Correct - V1 returns meal_plan directly on response
if (response.success) {
  mealPlanDataMap[planId] = response.meal_plan;  // V1 format
}
```
**Lesson:** V1 and V2 APIs have different response formats - check actual endpoint version

---

### Issue 8: Backend Field Name Mismatch (object_type vs type)
**Problem:** Widget not finding meal plan objects on load, position not loading  
**Symptom:** Debug shows `undefined meal_plan 170` instead of `mp meal_plan 170`  
**Root Cause:** Backend returns `object_type` but frontend checked for `type`  
**Solution:** Use correct field name from backend response
```javascript
// ❌ Wrong - backend doesn't return 'type'
const mealPlanObjects = objects.filter(obj => obj.type === 'mp');

// ✅ Correct - backend returns 'object_type'
const mealPlanObjects = objects.filter(obj => obj.object_type === 'mp');
```
**Backend Response Structure:**
```javascript
{
  id: 456,
  object_type: 'mp',        // ← not 'type'
  entity_type: 'meal_plan',
  entity_id: 170,
  position: {               // ← already an object with x, y
    x: 100,
    y: 200,
    width: 320,
    height: 200,
    z_index: 0
  }
}
```
**Lesson:** Always log actual API responses during development - don't assume field names

---

### Issue 9: Updating Existing Meal Plans
**Problem:** `Cannot read properties of undefined (reading 'plan_data')`  
**Symptom:** Updates fail when trying to modify position  
**Root Cause:** Trying to access `currentPlan.data.plan_data` but V1 returns `currentPlan.meal_plan.meal_data`  
**Solution:** Use correct V1 response structure consistently
```javascript
// ❌ Wrong - assumed V2 nested structure
const existingPlanData = currentPlan.data.plan_data;

// ✅ Correct - V1 returns meal_plan directly
const existingPlanData = currentPlan.meal_plan.meal_data;
```
**Lesson:** Be consistent with response format - if using V1 for GET, expect V1 format everywhere

---

### Issue 10: Update Object Position Not Persisting
**Problem:** Widgets save but reload at (0, 0) instead of moved position  
**Symptom:** 
- Save: `📍 position: {x: 1397.39, y: -1856.79}`
- Load: `📍 position: {x: 0, y: 0}` ❌
**Root Cause:** `update_object` endpoint was a STUB - returned fake success but didn't update database  
**Solution:** Implement real `update_object` endpoint with actual database UPDATE

**The Problem:**
```python
# Before: Stub returned fake success
@whiteboard_bp.route('/<int:wid>/o/<int:oid>', methods=['PATCH'])
def update_object(wid, oid):
    # TODO Phase 2: Implement object update
    return jsonify({
        'success': True,
        'data': {'_stub': True}  # ← Fake success!
    }), 200
```

**Frontend thought it succeeded, but database never updated!**

**The Fix:**
```python
# After: Real implementation updates database
@whiteboard_bp.route('/<int:wid>/o/<int:oid>', methods=['PATCH'])
def update_object(wid, oid):
    data = request.get_json()
    
    # Convert position object to array for JSONB storage
    if isinstance(data['position'], dict):
        pos_array = [
            data['position']['x'],
            data['position']['y'],
            data['position'].get('width', 300),
            data['position'].get('height', 400),
            data['position'].get('z', 0)
        ]
    
    # Actually update the database
    cursor.execute("""
        UPDATE wbo
        SET p = %s::jsonb, ua = CURRENT_TIMESTAMP
        WHERE id = %s
        RETURNING id, p as position
    """, (json.dumps(pos_array), oid))
    
    conn.commit()  # ← Critical! Actually persist changes
```

**Result After Fix:**
- Save: `📍 position: {x: 1397.39, y: -1856.79}` ✅
- Load: `📍 position: {x: 1397.39, y: -1856.79}` ✅ **MATCHES!**

**Lesson:** ALWAYS verify stubs are implemented before relying on them. A successful API response doesn't mean data was persisted!

**How to Detect Stub Issues:**
1. Check for `_stub: true` in response
2. Look for `TODO Phase X` comments in backend
3. Test full save/load cycle - don't trust save alone
4. Query database directly: `SELECT * FROM wbo WHERE id=X;`

---

## What Worked Well

### ✅ Grocery Lists Integration
- Pre-existing full implementation (not stubs)
- Clear repository pattern with tests
- Documented column additions (`hid`, `wid`, `wp`, `lr`)
- Smooth integration in ~30 minutes

### ✅ Test Suite
- Comprehensive test coverage (8 tests)
- Caught schema mismatches early
- Provided confidence in repository layer

---

## Process Improvements Implemented

### 1. API Integration Checklist
Created `docs/API_INTEGRATION_CHECKLIST.md` with:
- Pre-implementation verification steps
- Database schema check commands
- Endpoint testing with curl
- Common pitfall solutions

### 2. Schema Reference Document
Created `docs/WHITEBOARD_SCHEMA_REFERENCE.md` with:
- Complete table schemas
- Column naming conventions
- Frontend ↔ Backend mapping examples
- Common queries

### 3. Testing Strategy
```bash
# Before writing any code:
1. Check schema: \d+ table_name
2. Test endpoint: curl -X POST http://localhost:5000/api/endpoint
3. Verify response format
4. Check for stubs: grep -r "_stub" app/api/
```

---

## Recommended Workflow for Future Features

### Phase 1: Discovery (15 min)
```bash
# 1. Verify database schema
psql $DATABASE_URL -c "\d+ your_table"

# 2. Test existing endpoints
curl -X GET http://localhost:5000/api/v2/whiteboard/3
curl -X POST http://localhost:5000/api/v2/whiteboard/3/o -d '{"type":"test"}'

# 3. Check for stubs
grep -r "_stub" app/api/v2/ | grep -i "your_feature"

# 4. Review similar working feature (e.g., grocery lists)
```

### Phase 2: Documentation (10 min)
```markdown
# Create: docs/api/YOUR_FEATURE.md

## Endpoint
POST /api/v2/whiteboard/:wid/objects

## Request (from curl test)
{...actual format...}

## Response (from curl test)
{...actual format...}

## Database Mapping
- Frontend field → Database column
- position object → p jsonb array
```

### Phase 3: Implementation (30-60 min)
1. Backend endpoint (if stub)
2. Frontend integration
3. Test save/load cycle manually

### Phase 4: Testing (15 min)
1. Unit tests for repository
2. Manual save/load test
3. Page refresh test
4. Browser console check
5. Flask logs check

**Total Time: ~90 min** (vs 3+ hours debugging)

---

## Key Takeaways

### 🎯 Always Verify Before Assuming
- ❌ Don't assume column names match variable names
- ❌ Don't assume endpoints exist just because frontend calls them
- ❌ Don't assume stubs work like real implementations
- ✅ Check schema, test endpoints, verify responses

### 📚 Documentation Prevents Rework
- Each hour spent documenting saves 3+ hours debugging
- Schema reference + API contracts = faster development
- Checklists catch issues before they become blockers

### 🧪 Test End-to-End Early
- Unit tests alone aren't enough
- Full save → refresh → load cycle catches integration issues
- curl tests catch API contract mismatches

### 🏗️ Infrastructure Matters
- Fully implemented features integrate smoothly (grocery lists)
- Stubs block progress (whiteboard objects)
- Complete one feature before starting the next

---

## Success Metrics

### Before Process Improvements:
- ⏱️ Time to integrate meal plans: **4.5 hours** (including Issue #10)
- 🐛 Issues discovered: **10 major bugs**
- 🔄 Iterations needed: **20+ code changes**
- 😓 Frustration level: High

### After Process Improvements:
- ⏱️ **Expected** time for next feature: **~90 minutes**
- 🐛 **Expected** issues: **1-2 minor** (caught early with checklist)
- 🔄 **Expected** iterations: **2-3**
- 😊 **Expected** confidence: High
- 🎯 **New rule:** Check for stubs BEFORE building!

### Final Result:
- ✅ **Meal plans fully working!**
- ✅ **Save:** 2/2 meal plans persisting to database
- ✅ **Load:** Widgets restore at exact positions (no drift!)
- ✅ **Update:** Position changes persist perfectly
- ✅ **Refresh:** Survives page reloads
- 📊 **Position accuracy:** {x: 1397.39, y: -1856.79} → {x: 1397.39, y: -1856.79} (0.00% error)
- 🎉 **Mission Accomplished!**

---

## Action Items for Next Feature

- [ ] Read `API_INTEGRATION_CHECKLIST.md` BEFORE starting
- [ ] Verify schema with `\d+ table_name`
- [ ] Test endpoint with curl FIRST
- [ ] Document API contract in `docs/api/`
- [ ] Check for stubs and implement if needed
- [ ] Write integration test
- [ ] Test full save/load cycle before committing

---

## Resources Created
1. `docs/API_INTEGRATION_CHECKLIST.md` - Step-by-step feature integration guide
2. `docs/WHITEBOARD_SCHEMA_REFERENCE.md` - Complete schema documentation
3. `tests/test_whiteboard_meal_plans.py` - Comprehensive test suite (8 tests passing)
4. This document - Lessons learned and process improvements

---

**Bottom Line:** We now have the documentation and process to prevent these issues. Use the checklist for every new feature, and integration should be smooth! 🚀
