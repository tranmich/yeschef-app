"""
Drop duplicate whiteboard_* tables (old schema)
Keep wb* tables (compact schema)
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
conn.autocommit = True
cursor = conn.cursor()

print("\n" + "="*60)
print("DROPPING OLD WHITEBOARD TABLES")
print("="*60)

# Drop tables in correct order (respect foreign keys)
tables_to_drop = [
    'whiteboard_container_objects',
    'whiteboard_containers',
    'whiteboard_events',
    'whiteboard_objects',
    'whiteboards'
]

for table in tables_to_drop:
    try:
        print(f"\n🗑️  Dropping {table}...")
        cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
        print(f"   ✅ Dropped {table}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

# Verify they're gone
print("\n" + "="*60)
print("VERIFICATION")
print("="*60)

cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
      AND (table_name LIKE 'whiteboard%' OR table_name LIKE 'wb%')
    ORDER BY table_name
""")

remaining = cursor.fetchall()

print(f"\n✅ Remaining whiteboard tables ({len(remaining)}):")
for table in remaining:
    print(f"   - {table[0]}")

if len(remaining) == 5 and all(t[0].startswith('wb') for t in remaining):
    print("\n🎉 SUCCESS! Old tables dropped, compact schema intact")
else:
    print(f"\n⚠️  Expected 5 'wb*' tables, found {len(remaining)}")

cursor.close()
conn.close()
