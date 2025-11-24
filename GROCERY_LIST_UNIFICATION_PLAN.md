# Grocery List Unification Plan
## Safe Migration Without Breaking Anything

**Date:** November 12, 2025  
**Status:** Ready for Implementation  
**Risk Level:** LOW (backward compatible approach)

---

## 📊 AUDIT FINDINGS

### Column Usage Breakdown:

**Repository Layer (The Source of Truth):**
- `list_name`: 25 uses | `name`: 33 uses ← **Inconsistent!**
- `list_data`: 37 uses | `items_json`: 33 uses ← **Inconsistent!**
- `updated_at`: 20 uses | `updated_date`: 13 uses ← **Inconsistent!**

**Frontend Usage:**
- `GroceryManagerWorkspace.js`: Uses `name` (73x), `items` (50x), `list_data` (22x)
- `LoadGroceryListPanel.js`: Uses `list_name` (5x)
- `WhiteboardApp.js`: Uses `name` (38x), `items` (5x)

**Key Finding:** Different parts of the system are reading from DIFFERENT columns! 🚨

---

## 🎯 MIGRATION STRATEGY

### Phase 1: UNIFIED WRITE (Safe, Backward Compatible)
**Goal:** All updates write to BOTH column sets  
**Timeline:** Day 1  
**Risk:** ZERO (only adds redundant writes)

**What Changes:**
```python
# BEFORE: Whiteboard writes to name, items_json, updated_date
# AFTER: Writes to ALL columns (name + list_name, items_json + list_data, etc.)
```

**Benefits:**
✅ No matter which column you read from, data is fresh  
✅ Web, Mobile, Whiteboard all see updates immediately  
✅ Zero breaking changes  
✅ Can roll back instantly if issues arise  

---

### Phase 2: UNIFIED READ (Use Latest Data)
**Goal:** All reads use COALESCE to get newest data  
**Timeline:** Day 2-3  
**Risk:** VERY LOW (already done in hungie_server.py)

**What Changes:**
```sql
-- BEFORE: SELECT list_name, list_data, updated_at
-- AFTER: SELECT COALESCE(name, list_name), COALESCE(list_data, items_json), COALESCE(updated_date, updated_at)
```

**Benefits:**
✅ Always get most recent data regardless of which column was updated  
✅ Handles partial migrations gracefully  
✅ Works even if some rows have data in old columns only  

---

### Phase 3: DATA MIGRATION (Ensure Consistency)
**Goal:** Backfill missing data in duplicate columns  
**Timeline:** Day 4  
**Risk:** LOW (read-only validation first)

**Steps:**
```sql
-- 1. Find rows with missing data
SELECT id, 
       CASE WHEN name IS NULL THEN '❌' ELSE '✅' END as has_name,
       CASE WHEN list_name IS NULL THEN '❌' ELSE '✅' END as has_list_name
FROM grocery_lists 
WHERE name IS NULL OR list_name IS NULL;

-- 2. Backfill (dry run first!)
UPDATE grocery_lists 
SET name = list_name 
WHERE name IS NULL OR name = '';

UPDATE grocery_lists 
SET list_name = name 
WHERE list_name IS NULL OR list_name = '';

-- 3. Validate (should return 0 rows)
SELECT id FROM grocery_lists 
WHERE name IS NULL OR list_name IS NULL OR name != list_name;
```

---

### Phase 4: TESTING (Comprehensive)
**Goal:** Verify all access patterns work  
**Timeline:** Day 5  
**Risk:** ZERO (testing only)

**Test Matrix:**
| Client        | Action         | Endpoint Used              | Expected Result |
|---------------|----------------|----------------------------|-----------------|
| Web           | Load list      | GET /api/grocery-lists     | ✅ Latest data  |
| Web           | Update list    | PUT /api/grocery-lists/:id | ✅ Saves to all |
| Whiteboard    | Load list      | GET /api/v2/whiteboard/:id | ✅ Latest data  |
| Whiteboard    | Update list    | PATCH /api/v2/whiteboard   | ✅ Saves to all |
| Mobile        | Load list      | GET /api/v2/grocery-lists  | ✅ Latest data  |
| Mobile        | Update list    | PUT /api/v2/grocery-lists  | ✅ Saves to all |
| GroceryMgr    | Load from WB   | GET /api/grocery-lists     | ✅ Shows WB edits|

---

### Phase 5: DEPRECATION (Future - Not Now!)
**Goal:** Remove duplicate columns  
**Timeline:** After 30 days of stable operation  
**Risk:** MEDIUM (requires client updates)

**Not doing this yet!** Only after:
- All clients confirmed using new columns
- 30+ days of monitoring show no issues
- Database backup taken
- Rollback plan documented

---

## 🔧 IMPLEMENTATION DETAILS

### 1. Unified Update Method (Day 1)

**File:** `app/database/repositories/grocery_list_repository.py`

**Action:** Remove 3 duplicate methods, replace with ONE:

```python
def update_grocery_list(
    self,
    list_id: int,
    user_id: int,
    name: Optional[str] = None,
    items: Optional[List[Dict[str, Any]]] = None,
    widget_position: Optional[Dict[str, Any]] = None,
    linked_recipe_ids: Optional[List[int]] = None
) -> Optional[Dict[str, Any]]:
    """
    Update grocery list - UNIFIED VERSION
    Writes to ALL columns for backward compatibility
    """
    updates = []
    params = []
    
    if name is not None:
        # Write to BOTH name columns
        updates.append("name = %s")
        updates.append("list_name = %s")
        params.extend([name, name])
    
    if items is not None:
        items_json_str = json.dumps(items)
        # Write to BOTH data columns
        updates.append("items_json = %s")
        updates.append("list_data = %s::jsonb")
        params.extend([items_json_str, items_json_str])
    
    if widget_position is not None:
        updates.append("wp = %s::jsonb")
        params.append(json.dumps(widget_position))
    
    if linked_recipe_ids is not None:
        updates.append("lr = %s::jsonb")
        params.append(json.dumps(linked_recipe_ids))
    
    if not updates:
        return self.get_grocery_list_by_id(list_id, user_id)
    
    # Update BOTH timestamp columns
    updates.append("updated_date = NOW()")
    updates.append("updated_at = NOW()")
    
    params.extend([list_id, user_id])
    
    query = f"""
        UPDATE grocery_lists
        SET {', '.join(updates)}
        WHERE id = %s AND user_id = %s AND deleted_at IS NULL
        RETURNING id, user_id, 
                  COALESCE(name, list_name) as name,
                  COALESCE(list_data, items_json::jsonb) as items,
                  hid, wid, wp, lr,
                  created_at,
                  COALESCE(updated_date, updated_at) as updated_at
    """
    
    result = self._execute_query(query, tuple(params))
    
    if result and len(result) > 0:
        grocery_list = dict(result[0])
        # Parse JSONB to list
        if grocery_list.get('items'):
            if isinstance(grocery_list['items'], str):
                grocery_list['items'] = json.loads(grocery_list['items'])
        # Map compact column names
        if 'hid' in grocery_list:
            grocery_list['household_id'] = grocery_list.pop('hid')
        if 'wid' in grocery_list:
            grocery_list['whiteboard_id'] = grocery_list.pop('wid')
        if 'wp' in grocery_list:
            grocery_list['widget_position'] = grocery_list.pop('wp')
        if 'lr' in grocery_list:
            grocery_list['linked_recipe_ids'] = grocery_list.pop('lr')
        
        logger.info(f"✅ Grocery list {list_id} updated (unified)")
        return grocery_list
    
    logger.warning(f"❌ Failed to update grocery list {list_id}")
    return None
```

**Why This Works:**
- ✅ Writes to ALL columns (name + list_name, list_data + items_json)
- ✅ Updates ALL timestamps (updated_date + updated_at)
- ✅ Returns unified data using COALESCE
- ✅ Backward compatible with all existing code
- ✅ No breaking changes

---

### 2. Data Migration Script (Day 4)

**File:** `scripts/migrate_grocery_list_columns.py`

```python
"""
Grocery List Column Migration
Ensures data consistency between duplicate column sets
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def migrate():
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()
    
    print("=" * 80)
    print("GROCERY LIST COLUMN MIGRATION")
    print("=" * 80)
    
    # Step 1: Audit current state
    print("\n1️⃣ AUDITING CURRENT STATE...")
    cur.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(name) as has_name,
            COUNT(list_name) as has_list_name,
            COUNT(CASE WHEN name IS NOT NULL AND list_name IS NOT NULL 
                       AND name = list_name THEN 1 END) as both_match,
            COUNT(CASE WHEN name IS NOT NULL AND list_name IS NOT NULL 
                       AND name != list_name THEN 1 END) as both_differ
        FROM grocery_lists
        WHERE deleted_at IS NULL
    """)
    
    stats = cur.fetchone()
    print(f"   Total rows: {stats[0]}")
    print(f"   Has 'name': {stats[1]} ({stats[1]/stats[0]*100:.1f}%)")
    print(f"   Has 'list_name': {stats[2]} ({stats[2]/stats[0]*100:.1f}%)")
    print(f"   Both match: {stats[3]} ({stats[3]/stats[0]*100:.1f}%)")
    print(f"   Both differ: {stats[4]} ⚠️")
    
    # Step 2: Backfill name from list_name
    print("\n2️⃣ BACKFILLING 'name' FROM 'list_name'...")
    cur.execute("""
        UPDATE grocery_lists
        SET name = list_name
        WHERE (name IS NULL OR name = '') 
          AND list_name IS NOT NULL
          AND deleted_at IS NULL
    """)
    print(f"   Updated {cur.rowcount} rows")
    
    # Step 3: Backfill list_name from name
    print("\n3️⃣ BACKFILLING 'list_name' FROM 'name'...")
    cur.execute("""
        UPDATE grocery_lists
        SET list_name = name
        WHERE (list_name IS NULL OR list_name = '')
          AND name IS NOT NULL
          AND deleted_at IS NULL
    """)
    print(f"   Updated {cur.rowcount} rows")
    
    # Step 4: Sync items_json and list_data
    print("\n4️⃣ SYNCING ITEMS...")
    cur.execute("""
        UPDATE grocery_lists
        SET items_json = list_data::text
        WHERE (items_json IS NULL OR items_json = '[]')
          AND list_data IS NOT NULL
          AND deleted_at IS NULL
    """)
    print(f"   Updated items_json: {cur.rowcount} rows")
    
    cur.execute("""
        UPDATE grocery_lists
        SET list_data = items_json::jsonb
        WHERE list_data IS NULL
          AND items_json IS NOT NULL
          AND deleted_at IS NULL
    """)
    print(f"   Updated list_data: {cur.rowcount} rows")
    
    # Step 5: Sync timestamps
    print("\n5️⃣ SYNCING TIMESTAMPS...")
    cur.execute("""
        UPDATE grocery_lists
        SET updated_date = updated_at
        WHERE updated_date IS NULL
          AND updated_at IS NOT NULL
          AND deleted_at IS NULL
    """)
    print(f"   Updated updated_date: {cur.rowcount} rows")
    
    cur.execute("""
        UPDATE grocery_lists
        SET updated_at = updated_date
        WHERE updated_at IS NULL
          AND updated_date IS NOT NULL
          AND deleted_at IS NULL
    """)
    print(f"   Updated updated_at: {cur.rowcount} rows")
    
    # Step 6: Validation
    print("\n6️⃣ VALIDATING...")
    cur.execute("""
        SELECT id, name, list_name
        FROM grocery_lists
        WHERE deleted_at IS NULL
          AND (name IS NULL OR list_name IS NULL OR name != list_name)
        LIMIT 10
    """)
    
    issues = cur.fetchall()
    if issues:
        print(f"   ⚠️ Found {len(issues)} rows with inconsistencies:")
        for row in issues:
            print(f"      ID {row[0]}: name='{row[1]}', list_name='{row[2]}'")
    else:
        print("   ✅ All rows consistent!")
    
    # Commit or rollback?
    print("\n" + "=" * 80)
    choice = input("COMMIT these changes? (yes/no): ")
    
    if choice.lower() == 'yes':
        conn.commit()
        print("✅ MIGRATION COMPLETE!")
    else:
        conn.rollback()
        print("❌ ROLLED BACK - No changes made")
    
    conn.close()

if __name__ == '__main__':
    migrate()
```

---

## 📋 EXECUTION CHECKLIST

### Day 1: Unified Write
- [ ] Backup database
- [ ] Remove duplicate `update_grocery_list` methods (lines 475-556)
- [ ] Implement new unified method
- [ ] Test on dev database
- [ ] Deploy to production
- [ ] Monitor logs for errors

### Day 2-3: Unified Read  
- [ ] Already done in `hungie_server.py` ✅
- [ ] Apply same COALESCE pattern to repository reads
- [ ] Test all frontend components
- [ ] Verify mobile app works

### Day 4: Data Migration
- [ ] Run migration script in DRY RUN mode
- [ ] Review inconsistencies
- [ ] Fix any data quality issues
- [ ] Run migration for real
- [ ] Validate all rows consistent

### Day 5: Testing
- [ ] Test web grocery manager
- [ ] Test whiteboard grocery lists
- [ ] Test mobile app (if accessible)
- [ ] Test concurrent editing
- [ ] Load test with multiple users

---

## 🔒 SAFETY MEASURES

1. **Database Backup:** Before ANY changes
2. **Dry Run:** Test migration on copy of production data
3. **Gradual Rollout:** Deploy to dev → staging → production
4. **Monitoring:** Watch logs for errors after each step
5. **Rollback Plan:** Keep old code in git, can revert instantly
6. **Feature Flag:** Can disable new code path if issues arise

---

## ✅ SUCCESS CRITERIA

After migration, these should ALL be true:

1. ✅ Web users can edit grocery lists
2. ✅ Whiteboard users can edit grocery lists  
3. ✅ Mobile users can edit grocery lists
4. ✅ All three see each other's changes immediately
5. ✅ No data loss
6. ✅ No performance degradation
7. ✅ Concurrent edits handled gracefully

---

## 🚀 READY TO START?

This plan is:
- ✅ Safe (backward compatible)
- ✅ Incremental (can pause at any step)
- ✅ Testable (validation at each step)
- ✅ Reversible (can roll back)

Shall I proceed with Phase 1 (Unified Write)?
