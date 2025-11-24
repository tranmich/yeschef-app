#!/usr/bin/env python3
"""Quick script to check grocery_lists and meal_plans schema"""

import sys
sys.path.insert(0, '.')

from app.database.connection import get_db_connection
import psycopg2.extras

conn = get_db_connection()
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

print("=" * 60)
print("GROCERY_LISTS TABLE SCHEMA")
print("=" * 60)
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'grocery_lists' 
    ORDER BY ordinal_position
""")
for row in cur.fetchall():
    print(f"{row[0]}: {row[1]}")

print("\n" + "=" * 60)
print("MEAL_PLANS TABLE SCHEMA")
print("=" * 60)
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'meal_plans' 
    ORDER BY ordinal_position
""")
for row in cur.fetchall():
    print(f"{row[0]}: {row[1]}")

print("\n" + "=" * 60)
print("CHECK FOREIGN KEY CONSTRAINTS ON GROCERY_LISTS")
print("=" * 60)
cur.execute("""
    SELECT conname, confrelid::regclass as referenced_table,
           confdeltype as delete_action
    FROM pg_constraint
    WHERE conrelid = 'grocery_lists'::regclass
    AND contype = 'f'
""")
rows = cur.fetchall()
if rows:
    for row in rows:
        action_map = {'a': 'NO ACTION', 'r': 'RESTRICT', 'c': 'CASCADE', 'n': 'SET NULL', 'd': 'SET DEFAULT'}
        print(f"FK: {row[0]} -> {row[1]} (ON DELETE {action_map.get(row[2], 'UNKNOWN')})")
else:
    print("No foreign key constraints found on grocery_lists table")

print("\n" + "=" * 60)
print("GROCERY LISTS WITH DELETED WHITEBOARDS")
print("=" * 60)
cur.execute("""
    SELECT gl.id, gl.name, gl.wid, wb.deleted_at
    FROM grocery_lists gl
    LEFT JOIN wb ON gl.wid = wb.id
    WHERE gl.wid IS NOT NULL
    ORDER BY gl.wid, gl.id
""")
rows = cur.fetchall()
if rows:
    orphaned = 0
    for row in rows:
        status = "DELETED" if row[3] else "ACTIVE"
        if row[3]:
            orphaned += 1
        print(f"List ID {row[0]}: wid={row[2]} - Whiteboard {status}")
    print(f"\nTotal: {len(rows)} lists with whiteboard links, {orphaned} orphaned")
else:
    print("No grocery lists linked to whiteboards")

print("\n" + "=" * 60)
print("SAMPLE GROCERY LISTS FOR USER 11")
print("=" * 60)
cur.execute("""
    SELECT id, user_id, name, hid, wid, created_date
    FROM grocery_lists 
    WHERE user_id = 11
    ORDER BY created_date DESC
    LIMIT 10
""")
for row in cur.fetchall():
    print(f"ID: {row[0]}, User: {row[1]}, Name: {row[2]}, HID: {row[3]}, WID: {row[4]}, Created: {row[5]}")

print("\n" + "=" * 60)
print("SAMPLE MEAL PLANS FOR USER 11")
print("=" * 60)
cur.execute("""
    SELECT id, user_id, plan_name, created_date
    FROM meal_plans 
    WHERE user_id = 11
    ORDER BY created_date DESC
    LIMIT 10
""")
for row in cur.fetchall():
    print(f"ID: {row[0]}, User: {row[1]}, Name: {row[2]}, Created: {row[3]}")

print("\n" + "=" * 60)
print("ANALYSIS: SOLO VS COLLABORATIVE LISTS")
print("=" * 60)
cur.execute("""
    SELECT 
        COUNT(*) as total,
        COUNT(CASE WHEN hid IS NOT NULL AND wid IS NOT NULL THEN 1 END) as collaborative,
        COUNT(CASE WHEN hid IS NULL AND wid IS NULL THEN 1 END) as solo
    FROM grocery_lists
    WHERE user_id = 11
""")
row = cur.fetchone()
print(f"Total Lists: {row[0]}")
print(f"Collaborative (has hid/wid): {row[1]}")
print(f"Solo (no hid/wid): {row[2]}")

conn.close()
