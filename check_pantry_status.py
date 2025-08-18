#!/usr/bin/env python3
"""
Check pantry table status
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor

def check_pantry_tables():
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    pantry_tables = ['canonical_ingredients', 'user_pantry', 'recipe_ingredients', 'ingredient_substitutions']

    try:
        for table in pantry_tables:
            try:
                cursor.execute(f'SELECT COUNT(*) as count FROM {table}')
                count = cursor.fetchone()['count']
                print(f'✅ {table}: {count} records')
                
                # Show structure
                cursor.execute(f"""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = '{table}' 
                    ORDER BY ordinal_position
                """)
                cols = cursor.fetchall()
                print(f'   Columns: {len(cols)}')
                for col in cols[:3]:  # Show first 3 columns
                    print(f'     - {col["column_name"]}: {col["data_type"]}')
                if len(cols) > 3:
                    print(f'     ... and {len(cols)-3} more')
                print()
            except Exception as e:
                print(f'❌ {table}: Does not exist or error - {str(e)[:50]}...')
                print()

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    check_pantry_tables()
