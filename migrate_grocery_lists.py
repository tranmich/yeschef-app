"""
Check actual grocery_lists table schema and migrate if needed
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv('DATABASE_URL')

print("=" * 80)
print("CHECKING GROCERY_LISTS TABLE SCHEMA")
print("=" * 80)
print()

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Check if table exists
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'grocery_lists'
        )
    """)
    exists = cur.fetchone()['exists']
    
    if not exists:
        print("❌ grocery_lists table does NOT exist")
        print("✅ Will be created by v2 repository")
    else:
        print("✅ grocery_lists table EXISTS")
        print()
        
        # Get current columns
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'grocery_lists'
            ORDER BY ordinal_position
        """)
        columns = cur.fetchall()
        
        print("Current schema:")
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']} " +
                  f"(nullable: {col['is_nullable']}, default: {col['column_default']})")
        print()
        
        # Check for required columns
        column_names = [col['column_name'] for col in columns]
        required = ['items_json', 'name']
        missing = [col for col in required if col not in column_names]
        
        if missing:
            print(f"⚠️  Missing columns: {missing}")
            print()
            print("Applying migration...")
            
            # Add missing columns
            for col_name in missing:
                if col_name == 'items_json':
                    cur.execute("""
                        ALTER TABLE grocery_lists 
                        ADD COLUMN IF NOT EXISTS items_json TEXT NOT NULL DEFAULT '[]'
                    """)
                    print(f"  ✅ Added column: items_json")
                elif col_name == 'name':
                    cur.execute("""
                        ALTER TABLE grocery_lists 
                        ADD COLUMN IF NOT EXISTS name TEXT NOT NULL DEFAULT 'Grocery List'
                    """)
                    print(f"  ✅ Added column: name")
            
            conn.commit()
            print()
            print("✅ Migration complete!")
        else:
            print("✅ All required columns present")
    
    cur.close()
    conn.close()
    
    print()
    print("=" * 80)
    print("SCHEMA CHECK COMPLETE")
    print("=" * 80)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
