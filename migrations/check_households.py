"""
Quick script to check households table structure
"""
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'), sslmode='require', cursor_factory=psycopg2.extras.RealDictCursor)
cursor = conn.cursor()

# Check households table structure
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'households'
    ORDER BY ordinal_position;
""")

print("\n📊 HOUSEHOLDS TABLE STRUCTURE:")
print("-" * 40)
for col in cursor.fetchall():
    print(f"  {col['column_name']:20s} | {col['data_type']}")
print("-" * 40)

# Check if we have any households for user 11
cursor.execute("SELECT * FROM households LIMIT 3;")
households = cursor.fetchall()

print("\n📋 SAMPLE HOUSEHOLDS:")
print("-" * 40)
for h in households:
    print(f"  ID: {h.get('id')}, Name: {h.get('name', 'N/A')}")
print("-" * 40)

cursor.close()
conn.close()
