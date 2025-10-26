import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cursor = conn.cursor()

print("📊 Checking households table...")
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'households' 
    ORDER BY ordinal_position
""")

cols = cursor.fetchall()
if cols:
    print("\n✅ Households table columns:")
    for c in cols:
        print(f"  - {c[0]}: {c[1]}")
else:
    print("\n❌ Households table does not exist!")

cursor.close()
conn.close()
