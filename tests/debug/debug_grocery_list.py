import psycopg2
import psycopg2.extras
import json
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return psycopg2.connect(database_url)
    else:
        return psycopg2.connect(
            host='localhost',
            port=5432,
            database='hungie_dev',
            user='postgres',
            password='your_password'
        )

try:
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    # Get the September 8 list specifically
    cursor.execute('SELECT id, list_name, list_data FROM grocery_lists WHERE id = 9')
    result = cursor.fetchone()
    
    if result:
        print('📋 SEPTEMBER 8 LIST DETAILED ANALYSIS:')
        print('=' * 50)
        print('ID:', result['id'])
        print('Name:', result['list_name'])
        
        data = result['list_data']
        print('Data type:', type(data).__name__)
        print('Keys:', list(data.keys()))
        print()
        
        # Show each section in detail
        for section_name, items in data.items():
            if section_name == 'ingredient_count':
                print(f'{section_name}: {items}')
            elif isinstance(items, list):
                print(f'{section_name}: {len(items)} items')
                for i, item in enumerate(items):
                    print(f'  {i+1}. {item}')
            else:
                print(f'{section_name}: {items}')
        
    conn.close()
    
except Exception as e:
    print('Database error:', e)
