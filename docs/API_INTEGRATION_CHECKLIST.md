# API Integration Checklist
**Use this before adding any new whiteboard feature**

## Pre-Implementation Questions

### 1. Database Schema
- [ ] Does the table exist? Which columns?
- [ ] Are there indexes for performance?
- [ ] What are the foreign key relationships?
- [ ] Check: `SELECT * FROM information_schema.columns WHERE table_name = 'YOUR_TABLE';`

### 2. Backend API Endpoints
- [ ] Do endpoints exist? (V1 or V2?)
- [ ] Are they stubs or fully implemented?
- [ ] What request/response format do they use?
- [ ] Test with curl: `curl -X POST http://localhost:5000/api/endpoint -H "Authorization: Bearer TOKEN"`

### 3. Frontend Integration Points
- [ ] What API service file handles this? (`whiteboardAPI.js`, `api.js`, etc.)
- [ ] What state management is used? (React state, context, etc.)
- [ ] How does the widget save/load?

### 4. Testing Strategy
- [ ] Unit tests for repository?
- [ ] API endpoint tests?
- [ ] Integration test for save/load cycle?

---

## Implementation Checklist

### Phase 1: Verify Infrastructure
```bash
# 1. Check database schema
psql $DATABASE_URL -c "\d+ YOUR_TABLE"

# 2. Test existing endpoints
curl -X GET http://localhost:5000/api/v2/whiteboard/3
curl -X POST http://localhost:5000/api/v2/whiteboard/3/o -d '{"type":"test"}'

# 3. Search for stubs
grep -r "_stub" app/api/v2/
```

### Phase 2: Document API Contract
Create/update: `docs/api/ENDPOINT_NAME.md`
```markdown
## POST /api/v2/whiteboard/:wid/objects

### Request Body
{
  "type": "mp",
  "entity_type": "meal_plan",
  "entity_id": 123,
  "position": [x, y, w, h, z]
}

### Response
{
  "success": true,
  "data": {
    "id": 1,
    "mid": 123,
    ...
  }
}

### Database Mapping
- entity_type="meal_plan" → mid column
- entity_type="recipe" → rid column
- entity_type="grocery_list" → gid column
```

### Phase 3: Implement with Tests
1. Write failing test first
2. Implement endpoint
3. Test save/load cycle manually
4. Document any gotchas

### Phase 4: Validate Integration
- [ ] Create widget in frontend
- [ ] Save (Ctrl+S)
- [ ] Refresh page
- [ ] Verify widget loads in same position
- [ ] Check browser console for errors
- [ ] Check Flask logs for errors

---

## Common Pitfalls

### ❌ Problem: "Cannot read properties of undefined"
**Cause:** Response format mismatch
**Fix:** Check actual API response vs what frontend expects
```javascript
// Expected:
result.data.id

// Actual:
result.plan_id
```

### ❌ Problem: "Column X does not exist"
**Cause:** Using wrong column names
**Fix:** Check actual schema with `\d+ table_name`

### ❌ Problem: Widget saves but doesn't reload at correct position
**Cause:** Update endpoint is a stub OR position not being updated
**Fix:** 
1. Check if endpoint has `_stub: true` in response
2. Verify database actually updated: `SELECT p FROM wbo WHERE id=X;`
3. Implement real update endpoint if stub
4. Test full cycle: Move → Save → Refresh → Verify position

### ❌ Problem: CORS or 404 errors
**Cause:** Wrong endpoint path (V1 vs V2)
**Fix:** Check routes: `flask routes | grep endpoint_name`

---

## Quick Reference: Whiteboard Schema

### Tables
- `wb` - Whiteboards (id, hid, n, d, tt, cs)
- `wbo` - Whiteboard Objects (id, wid, t, rid, gid, mid, p, c, tags)
- `recipes` - Recipes (id, title, ingredients)
- `grocery_lists` - Grocery Lists (id, name, items, hid, wid, wp)
- `meal_plans` - Meal Plans (id, plan_name, plan_data_json)

### Column Naming Conventions
- Shortened names: `n`=name, `d`=description, `p`=position, `t`=type
- References: `rid`=recipe_id, `gid`=grocery_list_id, `mid`=meal_plan_id
- Audit: `cby`=created_by, `ca`=created_at, `ua`=updated_at

---

## Example: Adding a New Widget Type

### Step 1: Database
```sql
-- Check if table exists
SELECT * FROM information_schema.tables WHERE table_name = 'your_entity';

-- Check wbo supports it
ALTER TABLE wbo ADD COLUMN your_id INTEGER REFERENCES your_entity(id);
```

### Step 2: Backend
```python
# app/api/v2/whiteboards.py - create_object
your_id = entity_id if entity_type == 'your_entity' else None

INSERT INTO wbo (wid, t, your_id, p, ...)
```

### Step 3: Frontend
```javascript
// Save
await whiteboardAPI.createObject(whiteboardId, {
  type: 'ye',  // your entity type code
  entity_type: 'your_entity',
  entity_id: yourEntityId,
  position: {x, y, width, height, z}
});

// Load
const objects = whiteboard.objects.filter(obj => 
  obj.type === 'ye' || obj.your_id
);
```

### Step 4: Test
```bash
# Create
curl -X POST http://localhost:5000/api/v2/whiteboard/3/o \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"type":"ye","entity_type":"your_entity","entity_id":1,"position":[0,0,300,400,0]}'

# Verify
psql $DATABASE_URL -c "SELECT * FROM wbo WHERE wid=3 AND your_id=1;"
```

---

## Lessons Learned

### From Grocery Lists ✅
- Pre-existing infrastructure = smooth integration
- Repository pattern with tests = reliable
- Clear column mappings (hid, wid, wp) = no confusion

### From Meal Plans ⚠️
- Stubs hide integration issues until too late
- Mixed V1/V2 APIs cause endpoint confusion
- Schema assumptions without verification = runtime errors
- No integration tests = discovering issues in production

### Best Practices Going Forward
1. **Always check schema first** - Don't assume columns exist
2. **Test endpoints with curl** - Verify they work before frontend integration
3. **Document as you go** - API contracts in `docs/api/`
4. **Write integration tests** - Full save/load cycles
5. **Use consistent patterns** - V2 APIs only, avoid mixing V1
6. **Remove stubs immediately** - Or clearly mark them as blockers
