"""
Test the whiteboard query to see what columns are returned
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cursor = conn.cursor()

# Test the exact query from get_household_whiteboards
cursor.execute("""
    SELECT 
        id,
        hid,
        n,
        d,
        tt,
        cs,
        ca,
        ua,
        laa,
        cby,
        (SELECT COUNT(*) FROM wbo WHERE wid = wb.id AND deleted_at IS NULL) as object_count
    FROM wb
    WHERE hid = %s
      AND deleted_at IS NULL
    ORDER BY laa DESC
""", (11,))

rows = cursor.fetchall()

print(f"\n✅ Query returned {len(rows)} rows")
print(f"📊 Cursor description (columns):")
for i, desc in enumerate(cursor.description):
    print(f"   [{i}] {desc[0]} ({desc[1]})")

if rows:
    print(f"\n📋 First row has {len(rows[0])} values:")
    for i, val in enumerate(rows[0]):
        print(f"   [{i}] = {val} (type: {type(val).__name__})")
else:
    print("\n⚠️  No rows returned")

cursor.close()
conn.close()
