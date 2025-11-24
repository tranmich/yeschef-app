from app.database.connection import get_db_connection, return_db_connection
import psycopg2.extras

conn = get_db_connection()
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

user_id = 11
limit = 50
offset = 0

# Test the updated query with deleted whiteboard filtering
query = """
    SELECT DISTINCT gl.id, gl.user_id, gl.list_name, gl.list_data, gl.hid, gl.wid, gl.created_at, gl.updated_at
    FROM grocery_lists gl
    LEFT JOIN household_members hm ON gl.hid = hm.household_id
    LEFT JOIN wb ON gl.wid = wb.id
    WHERE (gl.user_id = %s OR (gl.hid IS NOT NULL AND hm.user_id = %s))
      AND gl.deleted_at IS NULL
      AND (gl.wid IS NULL OR wb.deleted_at IS NULL)
    ORDER BY gl.created_at DESC
    LIMIT %s OFFSET %s
"""

print("Executing updated query with deleted whiteboard filtering...")
cur.execute(query, (user_id, user_id, limit, offset))

lists = cur.fetchall()
print(f'\n✅ Grocery lists returned: {len(lists)}\n')

for gl in lists:
    wb_status = f"WB:{gl['wid']}" if gl['wid'] else "No WB"
    hh_status = f"HH:{gl['hid']}" if gl['hid'] else "Solo"
    print(f'  ID={gl["id"]}, user={gl["user_id"]}, name={gl["list_name"][:30]}, {wb_status}, {hh_status}')

cur.close()
return_db_connection(conn)
