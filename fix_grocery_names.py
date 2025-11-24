"""
Fix Grocery List Names - Use Most Descriptive Name
==================================================
When names differ, use the one that's NOT the default value
"""

import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()

def fix_names():
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    print("=" * 80)
    print("FIXING GROCERY LIST NAMES")
    print("=" * 80)
    
    # Find rows where names differ
    print("\n🔍 Finding rows where name != list_name...")
    cur.execute("""
        SELECT id, name, list_name,
               COALESCE(updated_date, updated_at) as last_updated
        FROM grocery_lists
        WHERE deleted_at IS NULL
          AND name != list_name
        ORDER BY last_updated DESC
    """)
    
    differing_rows = cur.fetchall()
    print(f"Found {len(differing_rows)} rows with differing names\n")
    
    if len(differing_rows) == 0:
        print("✅ All names already synchronized!")
        conn.close()
        return
    
    # Strategy: Use list_name if it's not default, otherwise use name
    print("🔧 FIXING STRATEGY:")
    print("   • If list_name has custom value → copy to name")
    print("   • If both are custom → use whichever was updated most recently\n")
    
    fixed_count = 0
    for row in differing_rows:
        list_id = row['id']
        name = row['name']
        list_name = row['list_name']
        
        # Determine which is the "real" name
        if list_name and list_name not in ['My Grocery List', 'Grocery List', '']:
            # list_name has custom value, use it
            chosen_name = list_name
            print(f"  ID {list_id:3d}: Using list_name='{list_name}' (custom)")
        elif name and name not in ['My Grocery List', 'Grocery List', '']:
            # name has custom value, use it
            chosen_name = name
            print(f"  ID {list_id:3d}: Using name='{name}' (custom)")
        else:
            # Both are defaults or one is empty, use whichever is not default
            chosen_name = list_name if list_name != 'My Grocery List' else name
            print(f"  ID {list_id:3d}: Using '{chosen_name}' (both defaults)")
        
        # Update both columns to chosen name
        cur.execute("""
            UPDATE grocery_lists
            SET name = %s, list_name = %s
            WHERE id = %s
        """, (chosen_name, chosen_name, list_id))
        fixed_count += 1
    
    print(f"\n✅ Fixed {fixed_count} rows")
    
    # Validate
    print("\n🔍 VALIDATING...")
    cur.execute("""
        SELECT COUNT(*) as mismatched
        FROM grocery_lists
        WHERE deleted_at IS NULL
          AND name != list_name
    """)
    remaining = cur.fetchone()['mismatched']
    
    if remaining == 0:
        print("   🎉 ALL NAMES NOW SYNCHRONIZED!")
        print("\n✅ COMMITTING CHANGES...")
        conn.commit()
        print("🎉 DONE!")
    else:
        print(f"   ⚠️  {remaining} rows still mismatched")
        choice = input("\nCommit anyway? (yes/no): ")
        if choice.lower() == 'yes':
            conn.commit()
            print("✅ Changes committed")
        else:
            conn.rollback()
            print("❌ Rolled back")
    
    conn.close()

if __name__ == '__main__':
    fix_names()
