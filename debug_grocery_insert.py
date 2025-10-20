"""Quick test to debug grocery list INSERT issue"""
import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import json

DATABASE_URL = os.getenv('DATABASE_URL')

print("=" * 80)
print("DEBUGGING GROCERY LIST INSERT")
print("=" * 80)
print()

try:
    # Connect to database
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Test 1: Check if table exists
    print("TEST 1: Check if grocery_lists table exists...")
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema='public' AND table_name='grocery_lists'
    """)
    result = cur.fetchone()
    if result:
        print(f"✅ Table exists: {result['table_name']}")
    else:
        print("❌ Table does NOT exist!")
        print("Creating table now...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS grocery_lists (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                items_json TEXT NOT NULL,
                meal_plan_id INTEGER,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("✅ Table created!")
    print()
    
    # Test 2: Check table schema
    print("TEST 2: Check table schema...")
    cur.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'grocery_lists'
        ORDER BY ordinal_position
    """)
    columns = cur.fetchall()
    for col in columns:
        print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
    print()
    
    # Test 3: Try a simple INSERT
    print("TEST 3: Try simple INSERT...")
    test_items = [{"name": "Test Item", "quantity": "1", "unit": "pc", "category": "Test", "purchased": False}]
    items_json = json.dumps(test_items)
    
    try:
        cur.execute("""
            INSERT INTO grocery_lists 
            (user_id, name, items_json, meal_plan_id, created_date, updated_date)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING id, user_id, name, items_json, meal_plan_id, created_date, updated_date
        """, (11, "Debug Test", items_json, None))
        
        result = cur.fetchone()
        conn.commit()
        
        print(f"✅ INSERT successful! ID: {result['id']}")
        print(f"   Name: {result['name']}")
        print(f"   Items: {result['items_json']}")
        
        # Clean up test data
        cur.execute("DELETE FROM grocery_lists WHERE id = %s", (result['id'],))
        conn.commit()
        print("✅ Test data cleaned up")
        
    except Exception as e:
        print(f"❌ INSERT failed: {e}")
        conn.rollback()
    
    print()
    print("=" * 80)
    print("DIAGNOSIS COMPLETE")
    print("=" * 80)
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
