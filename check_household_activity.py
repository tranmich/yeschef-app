from app.database.connection import get_db_connection, return_db_connection
import psycopg2.extras

conn = get_db_connection()
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

# Check if activity_feed table exists and has data
print("=" * 60)
print("CHECKING ACTIVITY FEED FOR HOUSEHOLD 19")
print("=" * 60)

cur.execute("""
    SELECT COUNT(*) as count 
    FROM activity_feed 
    WHERE household_id = 19
""")
result = cur.fetchone()
print(f"\nTotal activities for household 19: {result['count']}")

# Get some sample activities
cur.execute("""
    SELECT 
        af.id,
        af.event_type,
        af.resource_type,
        af.title,
        af.description,
        af.created_at,
        u.name as user_name
    FROM activity_feed af
    LEFT JOIN users u ON af.user_id = u.id
    WHERE af.household_id = 19
    ORDER BY af.created_at DESC
    LIMIT 10
""")

activities = cur.fetchall()
print(f"\nSample activities:")
for act in activities:
    print(f"  - {act['event_type']}: {act['title']} by {act['user_name']} at {act['created_at']}")

# Check comments in household 19
print("\n" + "=" * 60)
print("CHECKING COMMENTS FOR HOUSEHOLD 19")
print("=" * 60)

cur.execute("""
    SELECT COUNT(*) as count
    FROM wbc
    WHERE household_id = 19
""")
result = cur.fetchone()
print(f"\nTotal comments for household 19: {result['count']}")

# Get sample comments
cur.execute("""
    SELECT 
        wbc.id,
        wbc.comment_text,
        wbc.created_at,
        u.name as user_name,
        wbo.object_type,
        wbo.reference_id
    FROM wbc
    LEFT JOIN users u ON wbc.user_id = u.id
    LEFT JOIN wbo ON wbc.wbo_id = wbo.id
    WHERE wbc.household_id = 19
    ORDER BY wbc.created_at DESC
    LIMIT 10
""")

comments = cur.fetchall()
print(f"\nSample comments:")
for com in comments:
    print(f"  - {com['user_name']}: '{com['comment_text'][:50]}...' on {com['object_type']}#{com['reference_id']} at {com['created_at']}")

cur.close()
return_db_connection(conn)
