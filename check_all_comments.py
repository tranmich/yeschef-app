from app.database.connection import get_db_connection, return_db_connection
import psycopg2.extras

conn = get_db_connection()
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

# Check for ANY comments
print("=" * 60)
print("ALL COMMENTS IN DATABASE")
print("=" * 60)

cur.execute("SELECT COUNT(*) as count FROM wbc WHERE deleted_at IS NULL")
result = cur.fetchone()
print(f"\nTotal comments (not deleted): {result['count']}")

# Get sample comments with their whiteboard info
cur.execute("""
    SELECT 
        wbc.id as comment_id,
        wbc.txt as comment_text,
        wbc.ca as created_at,
        u.name as user_name,
        wbo.object_type,
        wbo.reference_id,
        wb.hid as household_id,
        wb.id as whiteboard_id
    FROM wbc
    INNER JOIN wbo ON wbc.oid = wbo.id
    INNER JOIN wb ON wbo.wid = wb.id
    LEFT JOIN users u ON wbc.uid = u.id
    WHERE wbc.deleted_at IS NULL
    ORDER BY wbc.ca DESC
    LIMIT 20
""")

comments = cur.fetchall()
print(f"\nSample comments across all households:")
for com in comments:
    text = com['comment_text'][:50] if com['comment_text'] else 'N/A'
    print(f"  HH#{com['household_id']}: {com['user_name']} on {com['object_type']}#{com['reference_id']}")
    print(f"    '{text}...' at {com['created_at']}")

# Now check household 19 specifically
print("\n" + "=" * 60)
print("COMMENTS FOR HOUSEHOLD 19")
print("=" * 60)

cur.execute("""
    SELECT COUNT(*) as count
    FROM wbc
    INNER JOIN wbo ON wbc.oid = wbo.id
    INNER JOIN wb ON wbo.wid = wb.id
    WHERE wb.hid = 19 AND wbc.deleted_at IS NULL
""")
result = cur.fetchone()
print(f"\nTotal comments for household 19: {result['count']}")

cur.close()
return_db_connection(conn)
