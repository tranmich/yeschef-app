import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

print("=== GROCERY_LISTS TABLE SCHEMA ===\n")
cur.execute("""
    SELECT column_name, data_type, is_nullable, column_default
    FROM information_schema.columns 
    WHERE table_name = 'grocery_lists' 
    ORDER BY ordinal_position
""")

for row in cur.fetchall():
    print(f"{row[0]:20} {row[1]:15} Nullable: {row[2]:3} Default: {row[3] or 'None'}")

print("\n=== SAMPLE DATA FROM WHITEBOARD GROCERY LISTS ===\n")
cur.execute("""
    SELECT id, user_id, list_name, name, 
           LENGTH(list_data::text) as list_data_len,
           LENGTH(items_json) as items_json_len,
           wid, hid, created_at, updated_at,
           updated_date
    FROM grocery_lists 
    WHERE wid IS NOT NULL
    ORDER BY updated_at DESC NULLS LAST, updated_date DESC NULLS LAST
    LIMIT 5
""")

for row in cur.fetchall():
    print(f"ID: {row[0]}, User: {row[1]}")
    print(f"  list_name: {row[2]}")
    print(f"  name: {row[3]}")
    print(f"  list_data length: {row[4]}")
    print(f"  items_json length: {row[5]}")
    print(f"  Whiteboard: {row[6]}, Household: {row[7]}")
    print(f"  created_at: {row[8]}")
    print(f"  updated_at: {row[9]}")
    print(f"  updated_date: {row[10]}")
    print()

conn.close()
