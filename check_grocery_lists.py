from app.database.connection import get_db_connection, return_db_connection
import psycopg2.extras

conn = get_db_connection()
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

# Check grocery lists
cur.execute("""
    SELECT id, user_id, list_name, hid 
    FROM grocery_lists 
    WHERE user_id = 11 OR hid IN (2, 11, 16, 19) 
    LIMIT 10
""")

lists = cur.fetchall()
print(f'\nGrocery lists for user 11: {len(lists)}\n')

for gl in lists:
    print(f'  ID={gl["id"]}, user={gl["user_id"]}, name={gl["list_name"]}, hid={gl["hid"]}')

cur.close()
return_db_connection(conn)
