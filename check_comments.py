from app.database.connection import get_db_connection, return_db_connection
import psycopg2.extras

conn = get_db_connection()
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

cur.execute("""
    SELECT id, whiteboard_id, object_type, object_id, content 
    FROM comments 
    WHERE whiteboard_id = 53 
    LIMIT 10
""")

rows = cur.fetchall()
print(f'\nComments in whiteboard 53: {len(rows)}\n')

for r in rows:
    obj_id = r['object_id']
    content_preview = r['content'][:40] if r['content'] else 'empty'
    print(f'  ID={r["id"]}, Type={r["object_type"]}, ObjID={obj_id}, Text={content_preview}...')

cur.close()
return_db_connection(conn)
