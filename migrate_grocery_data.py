"""
Grocery List Data Migration - Backfill Duplicate Columns
=========================================================
Ensures data consistency between legacy and whiteboard column sets

Run this ONCE after deploying unified update method
"""

import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()

def migrate():
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    print("=" * 80)
    print("GROCERY LIST DATA MIGRATION - AGGRESSIVE MODE")
    print("=" * 80)
    
    # Step 1: Audit current state
    print("\n📊 STEP 1: AUDITING CURRENT STATE...")
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
    print(f"   Total active lists: {stats['total']}")
    print(f"   Has 'name': {stats['has_name']} ({stats['has_name']/max(stats['total'],1)*100:.1f}%)")
    print(f"   Has 'list_name': {stats['has_list_name']} ({stats['has_list_name']/max(stats['total'],1)*100:.1f}%)")
    print(f"   Both columns match: {stats['both_match']} ({stats['both_match']/max(stats['total'],1)*100:.1f}%)")
    if stats['both_differ'] > 0:
        print(f"   ⚠️  Both differ: {stats['both_differ']} (will use most recent)")
    
    # Step 2: Backfill name from list_name (for older lists)
    print("\n🔄 STEP 2: BACKFILLING 'name' FROM 'list_name'...")
    cur.execute("""
        UPDATE grocery_lists
        SET name = list_name
        WHERE (name IS NULL OR name = '') 
          AND list_name IS NOT NULL
          AND deleted_at IS NULL
    """)
    count1 = cur.rowcount
    print(f"   ✅ Updated {count1} rows")
    
    # Step 3: Backfill list_name from name (for whiteboard-created lists)
    print("\n🔄 STEP 3: BACKFILLING 'list_name' FROM 'name'...")
    cur.execute("""
        UPDATE grocery_lists
        SET list_name = name
        WHERE (list_name IS NULL OR list_name = '')
          AND name IS NOT NULL
          AND deleted_at IS NULL
    """)
    count2 = cur.rowcount
    print(f"   ✅ Updated {count2} rows")
    
    # Step 4: Sync items_json and list_data
    print("\n🔄 STEP 4: SYNCING ITEMS DATA...")
    
    # items_json → list_data
    cur.execute("""
        UPDATE grocery_lists
        SET list_data = items_json::jsonb
        WHERE (list_data IS NULL OR list_data::text = '{}')
          AND items_json IS NOT NULL
          AND items_json != '[]'
          AND deleted_at IS NULL
    """)
    count3 = cur.rowcount
    print(f"   ✅ Copied items_json → list_data: {count3} rows")
    
    # list_data → items_json
    cur.execute("""
        UPDATE grocery_lists
        SET items_json = list_data::text
        WHERE (items_json IS NULL OR items_json = '[]')
          AND list_data IS NOT NULL
          AND list_data::text != '{}'
          AND deleted_at IS NULL
    """)
    count4 = cur.rowcount
    print(f"   ✅ Copied list_data → items_json: {count4} rows")
    
    # Step 5: Sync timestamps
    print("\n🔄 STEP 5: SYNCING TIMESTAMPS...")
    
    cur.execute("""
        UPDATE grocery_lists
        SET updated_date = updated_at
        WHERE updated_date IS NULL
          AND updated_at IS NOT NULL
          AND deleted_at IS NULL
    """)
    count5 = cur.rowcount
    print(f"   ✅ Copied updated_at → updated_date: {count5} rows")
    
    cur.execute("""
        UPDATE grocery_lists
        SET updated_at = updated_date
        WHERE updated_at IS NULL
          AND updated_date IS NOT NULL
          AND deleted_at IS NULL
    """)
    count6 = cur.rowcount
    print(f"   ✅ Copied updated_date → updated_at: {count6} rows")
    
    cur.execute("""
        UPDATE grocery_lists
        SET created_date = created_at
        WHERE created_date IS NULL
          AND created_at IS NOT NULL
          AND deleted_at IS NULL
    """)
    count7 = cur.rowcount
    print(f"   ✅ Copied created_at → created_date: {count7} rows")
    
    cur.execute("""
        UPDATE grocery_lists
        SET created_at = created_date
        WHERE created_at IS NULL
          AND created_date IS NOT NULL
          AND deleted_at IS NULL
    """)
    count8 = cur.rowcount
    print(f"   ✅ Copied created_date → created_at: {count8} rows")
    
    # Step 6: Final validation
    print("\n✅ STEP 6: VALIDATION...")
    cur.execute("""
        SELECT COUNT(*) as total FROM grocery_lists WHERE deleted_at IS NULL
    """)
    total_after = cur.fetchone()['total']
    
    cur.execute("""
        SELECT COUNT(*) as synced 
        FROM grocery_lists
        WHERE deleted_at IS NULL
          AND name IS NOT NULL 
          AND list_name IS NOT NULL
          AND name = list_name
          AND list_data IS NOT NULL
          AND items_json IS NOT NULL
    """)
    synced = cur.fetchone()['synced']
    
    print(f"   Total active lists: {total_after}")
    print(f"   Fully synced: {synced} ({synced/max(total_after,1)*100:.1f}%)")
    
    # Check for remaining issues
    cur.execute("""
        SELECT id, name, list_name, 
               CASE WHEN name IS NULL THEN '❌' ELSE '✅' END as has_name,
               CASE WHEN list_name IS NULL THEN '❌' ELSE '✅' END as has_list_name,
               CASE WHEN name != list_name THEN '⚠️ DIFFER' ELSE '✅' END as match_status
        FROM grocery_lists
        WHERE deleted_at IS NULL
          AND (name IS NULL OR list_name IS NULL OR name != list_name)
        LIMIT 10
    """)
    
    issues = cur.fetchall()
    if issues:
        print(f"\n   ⚠️  Found {len(issues)} rows with remaining inconsistencies:")
        for row in issues:
            print(f"      ID {row['id']:3d}: name={row['has_name']} list_name={row['has_list_name']} {row['match_status']}")
            print(f"           name='{row['name']}' vs list_name='{row['list_name']}'")
    else:
        print("   🎉 ALL ROWS FULLY SYNCHRONIZED!")
    
    # Summary
    print("\n" + "=" * 80)
    print("MIGRATION SUMMARY")
    print("=" * 80)
    total_changes = count1 + count2 + count3 + count4 + count5 + count6 + count7 + count8
    print(f"Total rows modified: {total_changes}")
    print(f"Success rate: {synced}/{total_after} ({synced/max(total_after,1)*100:.1f}%)")
    
    if total_changes > 0 or len(issues) == 0:
        print("\n✅ COMMITTING CHANGES...")
        conn.commit()
        print("🎉 MIGRATION COMPLETE!")
    else:
        print("\n⚠️  No changes made (data already synced)")
        conn.rollback()
    
    conn.close()

if __name__ == '__main__':
    print("\n⚡ AGGRESSIVE MODE: Running migration immediately\n")
    migrate()
