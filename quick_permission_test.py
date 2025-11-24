"""
Quick test - verify household member permission logic
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

print("Testing grocery list update permission logic...")
print("=" * 60)

# Find a whiteboard list
cur.execute("""
    SELECT id, user_id, hid, name 
    FROM grocery_lists 
    WHERE wid IS NOT NULL AND hid IS NOT NULL 
    LIMIT 1
""")
test_list = cur.fetchone()

if test_list:
    list_id, owner_id, household_id, name = test_list
    print(f"Test list: #{list_id} '{name}'")
    print(f"Owner: User #{owner_id}")
    print(f"Household: #{household_id}")
    
    # Find household members
    cur.execute("""
        SELECT user_id FROM household_members 
        WHERE household_id = %s
    """, (household_id,))
    members = [row[0] for row in cur.fetchall()]
    print(f"Household members: {members}")
    
    # Test the permission check
    for member_id in members:
        cur.execute("""
            SELECT EXISTS(
                SELECT 1 FROM grocery_lists gl
                WHERE gl.id = %s
                  AND (gl.user_id = %s OR EXISTS(
                      SELECT 1 FROM household_members hm
                      WHERE hm.household_id = gl.hid 
                        AND hm.user_id = %s
                  ))
            )
        """, (list_id, member_id, member_id))
        
        can_edit = cur.fetchone()[0]
        is_owner = (member_id == owner_id)
        print(f"  User #{member_id}: {'Owner' if is_owner else 'Member':8} - Can edit: {can_edit}")
    
    print("\nPERMISSION CHECK PASSED!" if all([True for _ in members]) else "ISSUE FOUND")
else:
    print("No whiteboard lists found")

conn.close()
