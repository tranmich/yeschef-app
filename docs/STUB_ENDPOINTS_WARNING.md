# ⚠️ STUB ENDPOINTS - CRITICAL WARNING
**A stub endpoint will lie to you and break your feature!**

---

## What is a Stub?

A **stub endpoint** returns fake success responses without actually doing anything in the database.

**Example Stub:**
```python
@app.route('/api/v2/whiteboard/<int:wid>/o/<int:oid>', methods=['PATCH'])
def update_object(wid, oid):
    # TODO Phase 2: Implement object update
    return jsonify({
        'success': True,
        'data': {
            'id': oid,
            '_stub': True  # ← WARNING FLAG!
        }
    }), 200
```

**What happens:**
1. ✅ Frontend calls endpoint
2. ✅ Gets `{success: true}` response
3. ❌ **Nothing persists to database**
4. ❌ Data lost on page refresh
5. 😱 **Wasted hours debugging "why won't it save?!"**

---

## Real-World Impact: Meal Plan Position Bug

### The Problem
Meal plan widgets would:
- ✅ Save positions: `{x: 1397, y: -1856}`
- ❌ Load at: `{x: 0, y: 0}` (spawn point)
- ⏱️ **Wasted 30+ minutes debugging**

### The Cause
```javascript
// Frontend: Move widget and save
await whiteboardAPI.updateObject(whiteboardId, objectId, {
  position: {x: 1397, y: -1856}
});
// ✅ Returns {success: true}
// ❌ BUT database still has {x: 0, y: 0}!
```

### The Root Issue
Backend `update_object` was a **STUB** - returned success without updating!

```python
# Backend (STUB - BAD!)
def update_object(wid, oid):
    return jsonify({'success': True, 'data': {'_stub': True}})
    # ↑ No database UPDATE!
```

### The Fix
Implement the actual database update:

```python
# Backend (REAL - GOOD!)
def update_object(wid, oid):
    data = request.get_json()
    
    cursor.execute("""
        UPDATE wbo
        SET p = %s::jsonb, ua = CURRENT_TIMESTAMP
        WHERE id = %s
    """, (json.dumps(position), oid))
    
    conn.commit()  # ← Actually persist!
    
    return jsonify({'success': True, 'data': {...}})
```

---

## How to Detect Stubs

### 1. Check Response for `_stub` Flag
```javascript
const response = await api.updateObject(id, data);
if (response.data._stub) {
  console.error('⚠️ WARNING: This endpoint is a stub!');
}
```

### 2. Look for TODO Comments in Backend
```python
# Red flags:
# TODO Phase 2: Implement
# Phase 1: Stub implementation
# return fake data
```

### 3. Check Endpoint List
See `docs/WHITEBOARD_SCHEMA_REFERENCE.md` for stub status

### 4. Test Full Save/Load Cycle
```javascript
// Don't just test save:
await api.save(data);
// ✅ Success!

// Test RELOAD too:
const loaded = await api.load();
// ❌ Data missing? → STUB!
```

### 5. Query Database Directly
```sql
-- After "successful" save, check if data actually exists:
SELECT * FROM wbo WHERE id = 123;

-- If position is still (0,0), endpoint is a stub!
```

---

## List of Known Stubs (As of Nov 5, 2025)

### ✅ IMPLEMENTED (No Longer Stubs)
- `POST /api/v2/whiteboard/:wid/o` - Create object ✅
- `PATCH /api/v2/whiteboard/:wid/o/:oid` - Update object ✅
- `DELETE /api/v2/whiteboard/:wid/o/:oid` - Delete object ✅
- `POST /api/v2/whiteboard/:wid/o/bulk` - Bulk update ✅

### ⚠️ STILL STUBS (Do Not Use!)
- `PATCH /api/v2/whiteboard/:wid` - Update whiteboard metadata
- `POST /api/v2/whiteboard/:wid/o/:oid/link` - Link object to entity
- `POST /api/v2/whiteboard/:wid/o/:oid/sync` - Sync from source
- `POST /api/v2/whiteboard/:wid/o/from-r/:rid` - Create from recipe
- `GET /api/v2/whiteboard/o/:oid/cm` - Get comments
- `POST /api/v2/whiteboard/o/:oid/cm` - Add comment
- `PATCH /api/v2/whiteboard/cm/:cid` - Update comment
- `DELETE /api/v2/whiteboard/cm/:cid` - Delete comment
- `POST /api/v2/whiteboard/cm/:cid/rx` - Add reaction
- `GET /api/v2/whiteboard/:wid/co` - Get collaborators
- `POST /api/v2/whiteboard/:wid/pr` - Update presence
- `GET /api/v2/whiteboard/:wid/h` - Get history
- `POST /api/v2/whiteboard/:wid/restore` - Restore version
- `GET /api/v2/whiteboard/templates` - Get templates
- `POST /api/v2/whiteboard/:wid/dup` - Duplicate whiteboard
- `GET /api/v2/whiteboard/:wid/export` - Export whiteboard

---

## Before Using ANY Endpoint

### Pre-Flight Checklist:
```bash
# 1. Check if endpoint is implemented
grep -r "_stub" app/api/v2/whiteboards.py | grep "your_endpoint"

# 2. Test with curl to see actual response
curl -X POST http://localhost:5000/api/endpoint \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"test": "data"}'

# 3. Check response for _stub flag
# If you see "_stub": true → DO NOT USE!

# 4. Verify database changes
psql $DATABASE_URL -c "SELECT * FROM your_table WHERE id=123;"
```

### If It's a Stub:
1. ❌ **Do NOT build features on top of it**
2. ✅ **Implement the real endpoint first**
3. ✅ **Test database persistence**
4. ✅ **Update stub status in docs**

---

## Cost of Ignoring Stubs

### Time Wasted (Meal Plan Example):
- 30 min: "Why isn't position saving?"
- 15 min: Adding debug logs
- 10 min: Checking frontend save logic
- 5 min: Testing different positions
- 10 min: Reading backend code
- **Total: 70 minutes debugging a stub** 😱

### Proper Approach:
- 5 min: Check if endpoint is stub
- 45 min: Implement real endpoint
- 5 min: Test and verify
- **Total: 55 minutes with working code** ✅

**Net savings: 15 minutes + working feature!**

---

## Implementation Checklist

When implementing a stub endpoint:

```python
# 1. Remove stub response
# ❌ Before:
return jsonify({'success': True, 'data': {'_stub': True}})

# ✅ After: Real implementation
cursor.execute("UPDATE table SET column = %s WHERE id = %s", (value, id))
conn.commit()
return jsonify({'success': True, 'data': {...}})

# 2. Add database operations
# - INSERT for create
# - UPDATE for update
# - DELETE for delete
# - SELECT to verify

# 3. Test with actual data
curl -X PATCH http://localhost:5000/api/endpoint \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"real": "data"}'

# 4. Verify database changed
psql $DATABASE_URL -c "SELECT * FROM table WHERE id=X;"

# 5. Update documentation
# Mark endpoint as ✅ in WHITEBOARD_SCHEMA_REFERENCE.md

# 6. Test full cycle
# Create → Update → Load → Verify
```

---

## Key Lessons

### 1. Success Response ≠ Data Persisted
A `200 OK` doesn't mean anything was saved!

### 2. Always Test Load, Not Just Save
```javascript
// Not enough:
await save(); // ✅

// Complete test:
await save();
await reload();
assert(data matches); // ← This catches stubs!
```

### 3. Stubs Block Features
Don't build on stubs - implement them first!

### 4. Check Twice, Code Once
5 minutes verifying endpoint status saves hours debugging.

### 5. Trust Database, Not Logs
```bash
# Frontend says "saved"?
# Backend says "success"?
# Check the source of truth:
SELECT * FROM wbo WHERE id = 123;
```

---

## Documentation Updates

When you implement a stub:

1. **Update `WHITEBOARD_SCHEMA_REFERENCE.md`:**
   ```markdown
   | PATCH | `/:wid/o/:oid` | Update object | ✅ **FIXED!** |
   ```

2. **Update this file:**
   Move endpoint from "STILL STUBS" → "IMPLEMENTED"

3. **Add to `MEAL_PLAN_INTEGRATION_LESSONS.md`:**
   Document the issue and solution

---

## Quick Reference

```bash
# Find all stubs in codebase:
grep -r "_stub.*True" app/

# Find TODO comments (potential stubs):
grep -r "TODO Phase" app/

# Test if endpoint persists:
curl -X POST endpoint && psql -c "SELECT * FROM table;"

# Before using ANY endpoint:
1. Check docs/WHITEBOARD_SCHEMA_REFERENCE.md
2. Test with curl
3. Verify database changes
4. If stub → implement first!
```

---

## Bottom Line

**A stub is a landmine waiting to explode.** 💣

It will:
- ✅ Return success (fake)
- ❌ Not persist data (real problem)
- ⏱️ Waste hours debugging (guaranteed)

**Check for stubs BEFORE building features, not after!**

---

**Last Updated:** November 5, 2025 (After Issue #10)  
**Status:** 2 critical stubs implemented (create_object, update_object)  
**Remaining Stubs:** 16 (see list above)
