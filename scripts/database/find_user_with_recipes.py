from app.database.connection import init_database, get_db_connection, return_db_connection

init_database()
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute('SELECT user_id, COUNT(*) as cnt FROM recipes WHERE user_id IS NOT NULL GROUP BY user_id ORDER BY cnt DESC LIMIT 1')
result = cursor.fetchone()
if result:
    print(f"User {result['user_id']} has {result['cnt']} recipes")
else:
    print("No users with recipes found")
return_db_connection(conn)
