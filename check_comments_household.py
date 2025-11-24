from app.database.connection import get_db_connection, return_db_connection
import psycopg2.extras

conn = get_db_connection()
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

# Check wbc table structure
print("=" * 60)
print("WBC TABLE STRUCTURE")
print("=" * 60)

cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'wbc' 
    ORDER BY ordinal_position
""")
cols = cur.fetchall()
for col in cols:
    print(f"  {col['column_name']}: {col['data_type']}")

# Check for comments with whiteboard objects in household 19
print("\n" + "=" * 60)
print("COMMENTS IN HOUSEHOLD 19 (VIA WHITEBOARD OBJECTS)")
print("=" * 60)

cur.execute("""
    SELECT COUNT(*) as count
    FROM wbc
    INNER JOIN wbo ON wbc.wbo_id = wbo.id
    INNER JOIN wb ON wbo.wid = wb.id
    WHERE wb.hid = 19
""")
result = cur.fetchone()
print(f"\nTotal comments: {result['count']}")

# Get sample
cur.execute("""
    SELECT 
        wbc.id,
        wbc.comment_text,
        wbc.created_at,
        u.name as user_name,
        wbo.object_type,
        wbo.reference_id,
        wb.hid as household_id
    FROM wbc
    INNER JOIN wbo ON wbc.wbo_id = wbo.id
    INNER JOIN wb ON wbo.wid = wb.id
    LEFT JOIN users u ON wbc.user_id = u.id
    WHERE wb.hid = 19
    ORDER BY wbc.created_at DESC
    LIMIT 10
""")

comments = cur.fetchall()
print(f"\nSample comments:")
for com in comments:
    print(f"  - {com['user_name']}: '{com['comment_text'][:50]}...' on {com['object_type']}#{com['reference_id']} at {com['created_at']}")

cur.close()
return_db_connection(conn)
