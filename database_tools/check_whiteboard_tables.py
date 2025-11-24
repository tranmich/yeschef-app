import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Check tables
cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
      AND table_name LIKE 'whiteboard%'
    ORDER BY table_name
""")

tables = cur.fetchall()
if tables:
    print(f"\n✅ Found {len(tables)} whiteboard tables:")
    for table in tables:
        print(f"   - {table[0]}")
else:
    print("\n❌ No whiteboard tables found")

cur.close()
conn.close()
