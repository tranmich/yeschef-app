# 🧪 Database Migration Testing Guide

**Date:** November 3, 2025  
**Phase:** 1 - Foundation  
**Migration Files:**
- Forward: `20251103_create_whiteboard_tables.sql`
- Rollback: `20251103_rollback_whiteboard_tables.sql`

---

## ⚠️ **BEFORE YOU RUN**

### **Prerequisites:**
- [ ] PostgreSQL database running
- [ ] Database connection string in `.env` file
- [ ] `households` table exists (with data for user_id 11)
- [ ] `users` table exists (with user_id 11: tran.mich@gmail.com)
- [ ] `recipes`, `grocery_lists`, `meal_plans` tables exist
- [ ] Backup of database created (optional but recommended)

---

## 🚀 **STEP 1: RUN MIGRATION (LOCAL TEST)**

### **Option A: Using psql (Recommended)**

```powershell
# Navigate to project directory
cd "d:\Mik\Downloads\Me Hungie"

# Run migration
psql -d yeschef_dev -f migrations/20251103_create_whiteboard_tables.sql
```

**Expected Output:**
```
BEGIN
CREATE TABLE
CREATE INDEX
...
NOTICE:  ✅ Migration successful: All 5 tables created
NOTICE:     - wb (whiteboards)
NOTICE:     - wbo (whiteboard_objects)
NOTICE:     - wbc (whiteboard_comments)
NOTICE:     - wbco (whiteboard_collaborators)
NOTICE:     - wbe (whiteboard_events)
INSERT 0 1
...
COMMIT
```

### **Option B: Using Python script**

```python
# test_migration.py
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cursor = conn.cursor()

# Read migration file
with open('migrations/20251103_create_whiteboard_tables.sql', 'r') as f:
    migration_sql = f.read()

# Execute
cursor.execute(migration_sql)
conn.commit()

print("✅ Migration successful!")
cursor.close()
conn.close()
```

---

## ✅ **STEP 2: VERIFY TABLES EXIST**

```sql
-- Check all tables created
SELECT table_name, 
       pg_size_pretty(pg_total_relation_size(quote_ident(table_name)::regclass)) AS size
FROM information_schema.tables
WHERE table_name IN ('wb', 'wbo', 'wbc', 'wbco', 'wbe')
  AND table_schema = 'public'
ORDER BY table_name;
```

**Expected Output:**
```
 table_name |  size   
------------+---------
 wb         | 16 kB
 wbe        | 16 kB
 wbo        | 16 kB
 wbc        | 8 kB
 wbco       | 8 kB
(5 rows)
```

---

## 🧪 **STEP 3: TEST BASIC OPERATIONS**

### **Test 1: Check test whiteboard created**

```sql
SELECT id, n, d, cby, ca 
FROM wb 
WHERE n = 'Test Whiteboard - Phase 1';
```

**Expected:** 1 row with user_id 11 as creator

---

### **Test 2: Check collaborator added**

```sql
SELECT wid, uid, rl, un 
FROM wbco 
WHERE uid = 11;
```

**Expected:** 1 row with role 'admin'

---

### **Test 3: Check event logged**

```sql
SELECT id, wid, et, uid, ed, ca 
FROM wbe 
WHERE et = 'whiteboard_created'
ORDER BY ca DESC 
LIMIT 1;
```

**Expected:** 1 row with event_type 'whiteboard_created'

---

### **Test 4: Test insert whiteboard object**

```sql
-- Insert a recipe block (linking to existing recipe)
INSERT INTO wbo (wid, t, rid, p, tags, cby)
VALUES (
    (SELECT id FROM wb WHERE n = 'Test Whiteboard - Phase 1'),
    'rc',  -- recipe card
    2577,  -- Existing recipe ID (adjust if needed)
    '[100, 150, 300, 400, 1]'::jsonb,  -- [x, y, width, height, z-index]
    ARRAY['test', 'phase1'],
    11
)
RETURNING id, wid, t, rid, p;
```

**Expected:** New object created with ID

---

### **Test 5: Test soft delete**

```sql
-- Soft delete the test whiteboard
UPDATE wb 
SET deleted_at = NOW(), deleted_by = 11
WHERE n = 'Test Whiteboard - Phase 1';

-- Verify it's in trash
SELECT id, n, deleted_at, deleted_by,
       EXTRACT(DAY FROM NOW() - deleted_at) as days_in_trash
FROM wb 
WHERE deleted_at IS NOT NULL;
```

**Expected:** Whiteboard marked as deleted, shows in trash

---

### **Test 6: Test restore**

```sql
-- Restore from trash
UPDATE wb 
SET deleted_at = NULL, deleted_by = NULL
WHERE n = 'Test Whiteboard - Phase 1';

-- Verify it's active again
SELECT id, n, deleted_at 
FROM wb 
WHERE n = 'Test Whiteboard - Phase 1';
```

**Expected:** deleted_at is NULL (active)

---

### **Test 7: Test triggers (auto-update timestamps)**

```sql
-- Update whiteboard name
UPDATE wb 
SET n = 'Test Whiteboard - Phase 1 (Updated)'
WHERE n = 'Test Whiteboard - Phase 1';

-- Check updated_at changed
SELECT n, ca, ua, ua > ca as timestamp_updated 
FROM wb 
WHERE n LIKE 'Test Whiteboard%';
```

**Expected:** ua > ca (updated_at is newer than created_at)

---

### **Test 8: Test cleanup function**

```sql
-- Manually set deleted_at to 15 days ago
UPDATE wb 
SET deleted_at = NOW() - INTERVAL '15 days'
WHERE n LIKE 'Test Whiteboard%';

-- Run cleanup
SELECT schedule_permanent_delete();

-- Verify permanently deleted
SELECT COUNT(*) 
FROM wb 
WHERE n LIKE 'Test Whiteboard%';
```

**Expected:** 0 rows (permanently deleted after 14 days)

---

## 📊 **STEP 4: PERFORMANCE TESTS**

### **Test index usage:**

```sql
EXPLAIN ANALYZE
SELECT * FROM wb WHERE hid = 1 AND deleted_at IS NULL;
```

**Expected:** Should use `idx_wb_hid` index

---

### **Test JSONB GIN index:**

```sql
EXPLAIN ANALYZE
SELECT * FROM wbo WHERE p @> '[100, 150]'::jsonb;
```

**Expected:** Should use `idx_wbo_p` GIN index

---

## 🔄 **STEP 5: TEST ROLLBACK**

```powershell
# Run rollback script
psql -d yeschef_dev -f migrations/20251103_rollback_whiteboard_tables.sql
```

**Expected Output:**
```
BEGIN
WARNING:  ⚠️  Found X active whiteboards
WARNING:  ⚠️  This rollback will PERMANENTLY delete all whiteboard data
WARNING:  ⚠️  Press Ctrl+C to cancel, or wait 5 seconds to continue...
NOTICE:  ✅ Dropped 4 functions
NOTICE:  ✅ Dropped wbe (whiteboard_events)
...
NOTICE:  ✅ Rollback successful: All whiteboard tables removed
COMMIT
```

---

### **Verify rollback:**

```sql
SELECT COUNT(*) 
FROM information_schema.tables
WHERE table_name IN ('wb', 'wbo', 'wbc', 'wbco', 'wbe')
  AND table_schema = 'public';
```

**Expected:** 0 (all tables removed)

---

## 🎯 **STEP 6: RE-RUN MIGRATION (FINAL TEST)**

```powershell
# Run migration again (to keep tables)
psql -d yeschef_dev -f migrations/20251103_create_whiteboard_tables.sql
```

**Expected:** All tables recreated successfully

---

## ✅ **SUCCESS CRITERIA**

**Migration is successful if:**
- [ ] All 5 tables created (wb, wbo, wbc, wbco, wbe)
- [ ] 14 indexes created
- [ ] 4 functions created
- [ ] 5 triggers created
- [ ] Test whiteboard inserted for user_id 11
- [ ] Soft delete works (14-day retention)
- [ ] Restore works (deleted_at set to NULL)
- [ ] Triggers update timestamps automatically
- [ ] Cleanup function deletes items >14 days
- [ ] Rollback removes all tables cleanly
- [ ] Re-migration works without errors

---

## 🐛 **TROUBLESHOOTING**

### **Error: relation "households" does not exist**
```sql
-- Check if households table exists
SELECT * FROM households LIMIT 1;

-- If not, you need to create it first or adjust the FK constraint
```

---

### **Error: user_id 11 not found**
```sql
-- Check if user exists
SELECT id, name, email FROM users WHERE id = 11;

-- If not, adjust the seed data to use a different user_id
```

---

### **Error: recipe_id 2577 does not exist**
```sql
-- Find an existing recipe ID
SELECT id, title FROM recipes LIMIT 5;

-- Use one of those IDs in Test 4
```

---

## 📝 **NEXT STEPS AFTER SUCCESSFUL MIGRATION**

1. ✅ **Document migration date** in changelog
2. ✅ **Commit migration files** to git
3. ✅ **Create API blueprint** (Phase 1, Week 2)
4. ✅ **Set up frontend page structure** (Phase 1, Week 3)
5. ✅ **Implement CRUD endpoints** (Phase 1, Week 3)

---

## 🚨 **EMERGENCY ROLLBACK**

If something goes wrong in production:

```powershell
# Immediate rollback
psql -d $DATABASE_URL -f migrations/20251103_rollback_whiteboard_tables.sql
```

**Note:** This will permanently delete all whiteboard data!

---

**Need help?** Check migration logs or contact dev team.
