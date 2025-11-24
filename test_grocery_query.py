from app.database.connection import get_db_connection, return_db_connection
import psycopg2.extras

conn = get_db_connection()
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

user_id = 11
limit = 50
offset = 0

# Test the exact query from the repository
query = """
    SELECT DISTINCT gl.id, gl.user_id, gl.list_name, gl.list_data, gl.hid, gl.wid, gl.created_at, gl.updated_at
    FROM grocery_lists gl
    LEFT JOIN household_members hm ON gl.hid = hm.household_id
    WHERE gl.user_id = %s 
       OR (gl.hid IS NOT NULL AND hm.user_id = %s)
    ORDER BY gl.created_at DESC
    LIMIT %s OFFSET %s
"""

print("Executing query with user_id=11...")
cur.execute(query, (user_id, user_id, limit, offset))

lists = cur.fetchall()
print(f'\nGrocery lists returned: {len(lists)}\n')

for gl in lists:
    print(f'  ID={gl["id"]}, user={gl["user_id"]}, name={gl["list_name"]}, hid={gl["hid"]}')

cur.close()
return_db_connection(conn)
