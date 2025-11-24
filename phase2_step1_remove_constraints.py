"""
Phase 2 Step 1: Remove NOT NULL Constraints
============================================
Before we can stop writing to legacy columns, we need to remove their constraints
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def remove_constraints():
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()
    
    print("=" * 80)
    print("PHASE 2 STEP 1: REMOVE NOT NULL CONSTRAINTS FROM LEGACY COLUMNS")
    print("=" * 80)
    print()
    
    print("This will allow us to stop writing to legacy columns safely.")
    print()
    
    # Remove NOT NULL from list_name
    print("1. Removing NOT NULL from list_name...")
    try:
        cur.execute("""
            ALTER TABLE grocery_lists 
            ALTER COLUMN list_name DROP NOT NULL
        """)
        print("   ✅ list_name can now be NULL")
    except Exception as e:
        print(f"   ⚠️  {e}")
    
    # Remove NOT NULL from list_data  
    print("2. Removing NOT NULL from list_data...")
    try:
        cur.execute("""
            ALTER TABLE grocery_lists 
            ALTER COLUMN list_data DROP NOT NULL
        """)
        print("   ✅ list_data can now be NULL")
    except Exception as e:
        print(f"   ⚠️  {e}")
    
    # items_json might already be nullable
    print("3. Removing NOT NULL from items_json (if exists)...")
    try:
        cur.execute("""
            ALTER TABLE grocery_lists 
            ALTER COLUMN items_json DROP NOT NULL
        """)
        print("   ✅ items_json can now be NULL")
    except Exception as e:
        print(f"   ⚠️  {e}")
    
    conn.commit()
    
    print()
    print("=" * 80)
    print("✅ CONSTRAINTS REMOVED")
    print("=" * 80)
    print()
    print("Now you can:")
    print("  1. Deploy Phase 2 code (writes only to: name, list_data, updated_at)")
    print("  2. Test thoroughly")
    print("  3. Drop legacy columns when ready")
    print()
    
    conn.close()

if __name__ == '__main__':
    remove_constraints()
