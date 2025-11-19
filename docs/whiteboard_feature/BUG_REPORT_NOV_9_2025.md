# 🐛 Whiteboard Bug Report

**Date:** November 9, 2025  
**Reporter:** User  
**Priority:** High  
**Status:** 🔍 Investigated (Not Fixed)

---

## **Bug #1: Recipe Tags Not Persisting** 🏷️

### **Issue:**
Users can add tags to recipe cards on the whiteboard, but after refreshing the page, the tags disappear.

### **Root Cause:**
The backend **saves** tags correctly to the database (confirmed in `bulk_update_objects` function), but when **loading** the whiteboard, the SELECT query doesn't include the `tags` column.

### **Location:**
**File:** `app/api/v2/whiteboards.py`  
**Function:** `get_whiteboard(wid)`  
**Line:** ~379

### **Current Code:**
```python
cursor.execute("""
    SELECT 
        wbo.id,
        wbo.t,
        wbo.rid,
        wbo.gid,
        wbo.mid,
        wbo.p,
        wbo.c,
        wbo.s,
        wbo.ca,
        wbo.cby,
        -- MISSING: wbo.tags ❌
        u.name as created_by_name,
        u.email as created_by_email
    FROM wbo
    LEFT JOIN users u ON wbo.cby = u.id
    WHERE wbo.wid = %s AND wbo.deleted_at IS NULL
    ORDER BY (wbo.p->>4)::int ASC, wbo.id ASC
""", (wid,))
```

### **Fix Required:**
Add `wbo.tags` to the SELECT statement and include it in the response object.

```python
cursor.execute("""
    SELECT 
        wbo.id,
        wbo.t,
        wbo.rid,
        wbo.gid,
        wbo.mid,
        wbo.p,
        wbo.c,
        wbo.s,
        wbo.tags,  -- ✅ ADD THIS
        wbo.ca,
        wbo.cby,
        u.name as created_by_name,
        u.email as created_by_email
    FROM wbo
    LEFT JOIN users u ON wbo.cby = u.id
    WHERE wbo.wid = %s AND wbo.deleted_at IS NULL
    ORDER BY (wbo.p->>4)::int ASC, wbo.id ASC
""", (wid,))
```

And in the objects loop (~line 430):
```python
objects.append({
    'id': obj_row['id'],
    'type': obj_row['t'],
    'object_type': obj_row['t'],
    'entity_type': entity_type,
    'entity_id': entity_id,
    'position': { ... },
    'content': obj_row.get('c'),
    'style': obj_row.get('s'),
    'tags': obj_row.get('tags') or [],  -- ✅ ADD THIS
    'created_at': obj_row['ca'].isoformat() if obj_row.get('ca') else None,
    'created_by': obj_row['cby'],
    'created_by_name': obj_row.get('created_by_name'),
    'created_by_email': obj_row.get('created_by_email')
})
```

### **Testing:**
1. Add tags to a recipe card
2. Save whiteboard (triggers `handleSave()`)
3. Refresh page
4. ✅ Tags should persist

---

## **Bug #2: Note & Grocery List Titles Not Persisting** 📝

### **Issue:**
When users rename a NoteBlock or GroceryList, the new name doesn't persist after page refresh.

### **Root Cause:**
The `wbo` (whiteboard_objects) table doesn't have a dedicated `name` column. The schema design uses:
- `c` (content) - JSONB field for storing object content
- No separate `name` field

However, the frontend is sending `name` as a **separate field** in the PATCH request, which the backend ignores.

### **Location:**

**Frontend:** `frontend/src/pages/WhiteboardApp.js` (lines ~693)  
**Backend:** `app/api/v2/whiteboards.py` - `update_object(wid, oid)` function

### **Current Frontend Code (NoteBlock onSave):**
```javascript
await apiCall(`/api/v2/whiteboard/${whiteboardId}/o/${obj.id}`, {
  method: 'PATCH',
  body: JSON.stringify({
    name: noteData.name,  // ❌ Sent separately (ignored by backend)
    content: {
      type: 'note',
      html: noteData.content,
      backgroundColor: noteData.backgroundColor,
      fontSize: noteData.fontSize
    }
  })
});
```

### **Current Backend Code:**
```python
if 'content' in data:
    update_fields.append('c = %s::jsonb')
    update_values.append(json.dumps(data['content']))
    # ❌ No handling for 'name' field
```

### **Fix Required:**

**Option 1: Store name inside content JSONB (Recommended)**

**Frontend change:** Include name inside content object
```javascript
await apiCall(`/api/v2/whiteboard/${whiteboardId}/o/${obj.id}`, {
  method: 'PATCH',
  body: JSON.stringify({
    content: {
      type: 'note',
      name: noteData.name,  // ✅ Include in content
      html: noteData.content,
      backgroundColor: noteData.backgroundColor,
      fontSize: noteData.fontSize
    }
  })
});
```

**Backend:** No changes needed (content is already saved as JSONB)

**Option 2: Add name column to wbo table (Not Recommended - requires migration)**

Add migration to add `n` column (name) to `wbo` table and update all save/load logic.

### **Files to Update:**

1. **NoteBlock onSave handler** (`WhiteboardApp.js` line ~690)
2. **NoteBlock load logic** (`WhiteboardApp.js` line ~660) - Extract name from content
3. **GroceryList save handler** (if using same pattern)
4. **MealPlan save handler** (if using same pattern)

### **Testing:**
1. Create a note block
2. Rename it to "Test Note"
3. Save (auto-save triggers on blur)
4. Refresh page
5. ✅ Name should be "Test Note" not "Note"

---

## **Bug #3: Remove Connection Lines Feature** 🔗

### **Issue:**
User wants to remove the connection lines feature (edges between nodes) as it's not relevant anymore.

### **Location:**
- **Frontend:** `frontend/src/pages/WhiteboardApp.js`
- **Components:** Any edge-related rendering

### **Fix Required:**

1. **Remove edge state and handlers:**
```javascript
// Remove these:
const [edges, setEdges] = useState([]);
const onEdgesChange = useCallback(...);
const onConnect = useCallback(...);
```

2. **Remove edge controls from ReactFlow:**
```javascript
<ReactFlow
  nodes={filteredNodes}
  // edges={edges}  // ❌ Remove this line
  onNodesChange={onNodesChange}
  // onEdgesChange={onEdgesChange}  // ❌ Remove
  // onConnect={onConnect}  // ❌ Remove
  ...
>
  {/* Remove: <Background />, <MiniMap /> if not needed */}
</ReactFlow>
```

3. **Remove edge-related UI:**
- Remove "Add Connection" buttons
- Remove edge styling
- Remove edge validation
- Remove edge save/load logic

### **Files to Update:**
- `frontend/src/pages/WhiteboardApp.js`
- `frontend/src/pages/WhiteboardApp.css` (remove edge styles)

### **Testing:**
1. Open whiteboard
2. ✅ No connection lines visible
3. ✅ No ability to create connections
4. Try to drag nodes
5. ✅ Works normally without edges

---

## **Bug #4: Household Presence Not Updating** 👥

### **Issue:**
The household presence bar at the bottom doesn't show which users are currently online/active on the whiteboard.

### **Symptoms:**
- Presence bar shows all household members but doesn't distinguish online/offline
- No real-time updates when users join/leave
- Console may show Pusher auth errors

### **Investigation Findings:**

**1. Pusher is configured correctly:**
- ✅ `pusher.js` has authorizer
- ✅ Backend has `/api/v2/pusher/auth` endpoint
- ✅ Auth endpoint returns user data correctly

**2. HouseholdPresence component subscribes correctly:**
- ✅ Subscribes to `presence-household-${householdId}` channel
- ✅ Binds to `pusher:member_added`, `pusher:member_removed`, `pusher:subscription_succeeded`

**3. Potential Issues:**

### **Issue A: Pusher auth endpoint might not be reachable**
**Check:** Look at browser console for fetch errors to `/api/v2/pusher/auth`

**Location:** `frontend/src/utils/pusher.js` line ~27
```javascript
fetch('/api/v2/pusher/auth', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': `Bearer ${token}`
  },
  body: `socket_id=${socketId}&channel_name=${channel.name}`
})
```

**Potential Fix:** Ensure API URL is correct (might need full URL in production)
```javascript
const API_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000';
fetch(`${API_URL}/api/v2/pusher/auth`, {
  ...
})
```

### **Issue B: Pusher key/cluster mismatch**
**Check:** Verify environment variables match backend

**Frontend:** `frontend/src/utils/pusher.js`
```javascript
const PUSHER_KEY = process.env.REACT_APP_PUSHER_KEY || '60bca4fc1079dbf0900d';
const PUSHER_CLUSTER = process.env.REACT_APP_PUSHER_CLUSTER || 'us2';
```

**Backend:** Check `app/services/pusher_service.py`
- Ensure `PUSHER_KEY`, `PUSHER_SECRET`, `PUSHER_CLUSTER` match

### **Issue C: User dictionary access error**
**Location:** `app/api/v2/pusher_auth.py` line ~45

Current code assumes cursor returns dict:
```python
cursor.execute(...)
user = cursor.fetchone()  # May return tuple, not dict!

user_data = {
    'id': user['id'],  # ❌ May fail if tuple
    'name': user['name'],
    ...
}
```

**Fix:** Ensure cursor is RealDictCursor:
```python
cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
```

Or access by index if tuple:
```python
user = cursor.fetchone()
user_data = {
    'id': user[0],
    'name': user[1],
    'email': user[2],
    'avatar_url': user[3]
}
```

### **Debugging Steps:**

1. **Check browser console:**
   - Look for Pusher auth errors
   - Check if `✅ Presence subscription succeeded!` appears
   - Check if member events fire

2. **Check backend logs:**
   - Look for `/api/v2/pusher/auth` requests
   - Check for any Python errors during auth

3. **Test Pusher dashboard:**
   - Go to Pusher.com dashboard
   - Check "Debug Console"
   - See if presence channel is being created
   - Check if users are joining

4. **Test manually:**
   - Open whiteboard in two different browsers
   - Both should authenticate
   - Should see both users in presence bar

### **Files to Check:**
- `frontend/src/utils/pusher.js` - Pusher client config
- `frontend/src/components/whiteboard/HouseholdPresence.js` - UI component
- `app/api/v2/pusher_auth.py` - Backend auth endpoint
- `app/services/pusher_service.py` - Pusher initialization

### **Expected Behavior:**
1. User opens whiteboard
2. Pusher connects and authenticates
3. User joins `presence-household-${householdId}` channel
4. HouseholdPresence component receives member list
5. Updates `onlineMembers` state
6. Shows green dot next to online members
7. Real-time updates when other users join/leave

---

## **Summary**

| Bug | Severity | Estimated Fix Time | Status |
|-----|----------|-------------------|--------|
| #1: Tags not persisting | 🔴 High | 15 min | Ready to fix |
| #2: Titles not persisting | 🔴 High | 30 min | Ready to fix |
| #3: Remove connection lines | 🟡 Medium | 20 min | Ready to fix |
| #4: Presence not updating | 🟠 High | 30-60 min | Needs debugging |

**Total Estimated Time:** 1.5 - 2 hours

---

## **Recommended Fix Order:**

1. **Bug #1 (Tags)** - Quickest win, one-line fix
2. **Bug #3 (Lines)** - Simple removal, no debugging needed
3. **Bug #2 (Titles)** - Requires frontend + backend coordination
4. **Bug #4 (Presence)** - Requires debugging, may take longer

---

**Document Version:** 1.0  
**Last Updated:** November 9, 2025  
**Next Steps:** User to prioritize which bugs to fix first
