"""
Check all whiteboard-related tables in the database
Shows exactly what exists and detects duplicates
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

print("\n" + "="*60)
print("WHITEBOARD TABLE AUDIT")
print("="*60)

# Check for all possible whiteboard table names
table_patterns = [
    'whiteboard%',  # Our current naming
    'wb%',          # Compact naming from attachment
]

all_tables = []

for pattern in table_patterns:
    cur.execute("""
        SELECT table_name, 
               (SELECT COUNT(*) FROM information_schema.columns 
                WHERE table_name = t.table_name) as column_count
        FROM information_schema.tables t
        WHERE table_schema = 'public' 
          AND table_name LIKE %s
        ORDER BY table_name
    """, (pattern,))
    
    tables = cur.fetchall()
    all_tables.extend(tables)

# Remove duplicates
all_tables = list(set(all_tables))
all_tables.sort()

if all_tables:
    print(f"\n✅ Found {len(all_tables)} whiteboard-related tables:\n")
    for table, col_count in all_tables:
        print(f"   📋 {table:30s} ({col_count} columns)")
        
        # Get sample row count
        try:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            row_count = cur.fetchone()[0]
            print(f"      └─ {row_count} rows")
        except:
            print(f"      └─ (could not count rows)")
    
    # Check for duplicates
    table_names = [t[0] for t in all_tables]
    
    # Check if we have both old and new naming
    has_whiteboard = any('whiteboard_' in t for t in table_names)
    has_wb = any(t.startswith('wb') and len(t) <= 4 for t in table_names)
    
    if has_whiteboard and has_wb:
        print("\n⚠️  WARNING: DUPLICATE TABLE NAMING DETECTED!")
        print("   You have both 'whiteboard_*' and 'wb*' tables")
        print("   This suggests migration ran twice with different schemas")
        print("\n   Recommendation: Drop one set and keep the other")
    else:
        print("\n✅ No duplicate naming conflicts detected")
        
else:
    print("\n❌ No whiteboard tables found in database")
    print("   Migration has not been run yet")

# Show indexes
print("\n" + "="*60)
print("WHITEBOARD INDEXES")
print("="*60)

cur.execute("""
    SELECT tablename, indexname 
    FROM pg_indexes 
    WHERE schemaname = 'public' 
      AND (tablename LIKE 'whiteboard%' OR tablename LIKE 'wb%')
    ORDER BY tablename, indexname
""")

indexes = cur.fetchall()
if indexes:
    current_table = None
    for table, index in indexes:
        if table != current_table:
            print(f"\n📋 {table}:")
            current_table = table
        print(f"   └─ {index}")
else:
    print("\n❌ No indexes found")

# Show triggers
print("\n" + "="*60)
print("WHITEBOARD TRIGGERS")
print("="*60)

cur.execute("""
    SELECT event_object_table, trigger_name
    FROM information_schema.triggers
    WHERE trigger_schema = 'public'
      AND (event_object_table LIKE 'whiteboard%' OR event_object_table LIKE 'wb%')
    ORDER BY event_object_table, trigger_name
""")

triggers = cur.fetchall()
if triggers:
    current_table = None
    for table, trigger in triggers:
        if table != current_table:
            print(f"\n📋 {table}:")
            current_table = table
        print(f"   └─ {trigger}")
else:
    print("\n❌ No triggers found")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Tables:   {len(all_tables)}")
print(f"Indexes:  {len(indexes)}")
print(f"Triggers: {len(triggers)}")

if len(all_tables) == 5 and not (has_whiteboard and has_wb):
    print("\n✅ Database schema looks good!")
    print("   All expected tables present, no duplicates")
elif len(all_tables) > 5:
    print("\n⚠️  More tables than expected - check for duplicates")
elif len(all_tables) < 5:
    print("\n⚠️  Missing some tables - migration may be incomplete")

print("\n" + "="*60)

cur.close()
conn.close()
