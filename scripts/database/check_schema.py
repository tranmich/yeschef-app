#!/usr/bin/env python3
"""Quick script to check friend_requests table schema"""

from app.database.connection import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()
import psycopg2.extras
cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

cursor.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns 
    WHERE table_name = 'households' 
    ORDER BY ordinal_position
""")

print("\n📋 households table columns:")
print("-" * 50)
rows = cursor.fetchall()
if not rows:
    print("  No columns found!")
else:
    for row in rows:
        print(f"  {row[0]:<20} {row[1]:<15}")

# Also check household_members
cursor.execute("""
    SELECT column_name, data_type
    FROM information_schema.columns 
    WHERE table_name = 'household_members' 
    ORDER BY ordinal_position
""")

print("\n📋 household_members table columns:")
print("-" * 50)
rows = cursor.fetchall()
if not rows:
    print("  No columns found!")
else:
    for row in rows:
        print(f"  {row[0]:<20} {row[1]:<15}")

cursor.close()
conn.close()
