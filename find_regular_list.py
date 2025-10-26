#!/usr/bin/env python3
"""Search for Regular List grocery list"""

from app.database.connection import get_db_connection
import psycopg2.extras

conn = get_db_connection()
cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# Search for all grocery lists to see what's there
cursor.execute("""
    SELECT id, user_id, list_name, created_at, updated_at
    FROM grocery_lists 
    ORDER BY created_at DESC
    LIMIT 20
""")

results = cursor.fetchall()

print('\n📋 All Grocery Lists (last 20):')
print('-' * 80)

if results:
    for row in results:
        print(f'  ID: {row["id"]:<5} User ID: {row["user_id"]:<5} Name: "{row["list_name"]}"')
        print(f'          Created: {row["created_at"]}')
        print()
else:
    print('  No lists found!')

print(f'Total: {len(results)} list(s) found')

# Now search for "My Grocery List" pattern
cursor.execute("""
    SELECT id, user_id, list_name, created_at
    FROM grocery_lists 
    WHERE list_name ILIKE %s
    ORDER BY created_at DESC
""", ('%My Grocery%',))

my_list_results = cursor.fetchall()
if my_list_results:
    print('\n🔍 Lists containing "My Grocery":')
    print('-' * 80)
    for row in my_list_results:
        print(f'  ID: {row["id"]:<5} User ID: {row["user_id"]:<5} Name: "{row["list_name"]}"')
        print(f'          Created: {row["created_at"]}')
        print()


cursor.close()
conn.close()
