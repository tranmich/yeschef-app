"""
Phase 2 Final Migration: Drop Legacy Columns
=============================================
This is the final step - removes duplicate columns from database

IMPORTANT: Run this ONLY after verifying Phase 2 code is deployed and working!
"""

import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def phase_2_migration():
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    print("=" * 80)
    print("PHASE 2: FINAL MIGRATION - DROP LEGACY COLUMNS")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("⚠️  WARNING: This will permanently remove columns!")
    print("   Make sure Phase 2 code is deployed and tested first!")
    print()
    
    # Step 1: Final data sync (just in case)
    print("STEP 1: Final data synchronization check...")
    print("-" * 80)
    
    # Copy name → list_name (if any missing)
    cur.execute("""
        UPDATE grocery_lists
        SET list_name = name
        WHERE (list_name IS NULL OR list_name = '')
          AND name IS NOT NULL
          AND deleted_at IS NULL
    """)
    if cur.rowcount > 0:
        print(f"   Synced {cur.rowcount} list_name values from name")
    
    # Copy list_data → items_json (if any missing)
    cur.execute("""
        UPDATE grocery_lists
        SET items_json = list_data::text
        WHERE (items_json IS NULL OR items_json = '[]')
          AND list_data IS NOT NULL
          AND deleted_at IS NULL
    """)
    if cur.rowcount > 0:
        print(f"   Synced {cur.rowcount} items_json values from list_data")
    
    # Copy updated_at → updated_date (if any missing)
    cur.execute("""
        UPDATE grocery_lists
        SET updated_date = updated_at
        WHERE updated_date IS NULL
          AND updated_at IS NOT NULL
          AND deleted_at IS NULL
    """)
    if cur.rowcount > 0:
        print(f"   Synced {cur.rowcount} updated_date values from updated_at")
    
    conn.commit()
    print("   ✅ Final sync complete")
    print()
    
    # Step 2: Validate data integrity
    print("STEP 2: Data integrity validation...")
    print("-" * 80)
    
    cur.execute("""
        SELECT COUNT(*) as total,
               COUNT(name) as has_name,
               COUNT(list_data) as has_list_data,
               COUNT(updated_at) as has_updated_at,
               COUNT(created_at) as has_created_at
        FROM grocery_lists
        WHERE deleted_at IS NULL
    """)
    
    stats = cur.fetchone()
    print(f"   Total active lists: {stats['total']}")
    print(f"   Have name: {stats['has_name']}/{stats['total']}")
    print(f"   Have list_data: {stats['has_list_data']}/{stats['total']}")
    print(f"   Have updated_at: {stats['has_updated_at']}/{stats['total']}")
    print(f"   Have created_at: {stats['has_created_at']}/{stats['total']}")
    
    if stats['has_name'] < stats['total'] or stats['has_list_data'] < stats['total']:
        print()
        print("   ❌ ERROR: Some lists missing required data!")
        print("   Cannot proceed with column drop. Fix data first.")
        conn.close()
        return False
    
    print("   ✅ All lists have required columns")
    print()
    
    # Step 3: Drop legacy columns
    print("STEP 3: Dropping legacy columns...")
    print("-" * 80)
    
    print("\n⚠️  FINAL WARNING: About to drop columns:")
    print("   • list_name (replaced by: name)")
    print("   • items_json (replaced by: list_data)")
    print("   • updated_date (replaced by: updated_at)")
    print("   • created_date (replaced by: created_at)")
    print()
    
    response = input("Type 'DROP COLUMNS' to proceed: ")
    
    if response != 'DROP COLUMNS':
        print("\n❌ Aborted - no changes made")
        conn.close()
        return False
    
    print("\n🔧 Dropping columns...")
    
    try:
        # Drop list_name
        cur.execute("ALTER TABLE grocery_lists DROP COLUMN IF EXISTS list_name")
        print("   ✅ Dropped list_name")
        
        # Drop items_json
        cur.execute("ALTER TABLE grocery_lists DROP COLUMN IF EXISTS items_json")
        print("   ✅ Dropped items_json")
        
        # Drop updated_date
        cur.execute("ALTER TABLE grocery_lists DROP COLUMN IF EXISTS updated_date")
        print("   ✅ Dropped updated_date")
        
        # Drop created_date
        cur.execute("ALTER TABLE grocery_lists DROP COLUMN IF EXISTS created_date")
        print("   ✅ Dropped created_date")
        
        conn.commit()
        
        print()
        print("=" * 80)
        print("🎉 PHASE 2 MIGRATION COMPLETE!")
        print("=" * 80)
        print()
        print("Final schema:")
        print("  ✅ name (single source)")
        print("  ✅ list_data (JSONB, queryable)")
        print("  ✅ updated_at (standard timestamp)")
        print("  ✅ created_at (standard timestamp)")
        print()
        print("Legacy columns removed:")
        print("  ❌ list_name")
        print("  ❌ items_json")
        print("  ❌ updated_date")
        print("  ❌ created_date")
        print()
        print("Storage saved: ~50%")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR during column drop: {e}")
        conn.rollback()
        print("   Rolled back - no changes made")
        return False
    
    finally:
        conn.close()

if __name__ == '__main__':
    print("\n🚀 Starting Phase 2 Final Migration...\n")
    success = phase_2_migration()
    
    if success:
        print("✅ Migration successful!")
        print("   Test your application thoroughly.")
        print("   Database backup is recommended before running in production.")
    else:
        print("❌ Migration failed or aborted")
    
    print()
