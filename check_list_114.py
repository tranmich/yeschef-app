"""
Quick Database Check - Verify Updates Are Persisting
=====================================================
Check if grocery list 114 actually has the updates in the database
"""

import psycopg2
import psycopg2.extras
import os
import json
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

print("=" * 80)
print("CHECKING GROCERY LIST 114 IN DATABASE")
print("=" * 80)
print()

# Check what's actually in the database
cur.execute("""
    SELECT id, name, list_data, items_json, updated_at
    FROM grocery_lists
    WHERE id = 114
""")

result = cur.fetchone()

if result:
    print(f"List ID: {result['id']}")
    print(f"Name: {result['name']}")
    print(f"Updated: {result['updated_at']}")
    print()
    
    # Check list_data (JSONB - Phase 2)
    if result['list_data']:
        items = result['list_data'] if isinstance(result['list_data'], list) else json.loads(result['list_data'])
        print(f"list_data (Phase 2): {len(items)} items")
        for i, item in enumerate(items[:5], 1):
            print(f"  {i}. {item.get('ingredient', 'Unknown')}")
        if len(items) > 5:
            print(f"  ... and {len(items) - 5} more")
    else:
        print("list_data: NULL")
    
    print()
    
    # Check items_json (TEXT - legacy)
    if result['items_json']:
        items_legacy = json.loads(result['items_json']) if isinstance(result['items_json'], str) else result['items_json']
        print(f"items_json (legacy): {len(items_legacy)} items")
        for i, item in enumerate(items_legacy[:5], 1):
            print(f"  {i}. {item.get('ingredient', 'Unknown')}")
        if len(items_legacy) > 5:
            print(f"  ... and {len(items_legacy) - 5} more")
    else:
        print("items_json: NULL")
else:
    print("❌ List 114 not found!")

conn.close()
