import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = 'postgresql://postgres:udQLpljdqTYmESmntwzmwDcOlBVbqlJG@shuttle.proxy.rlwy.net:31331/railway'

try:
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    
    print('=== Checking canonical_ingredients table ===')
    cursor.execute('SELECT COUNT(*) as total FROM canonical_ingredients')
    total = cursor.fetchone()['total']
    print(f'Total ingredients: {total}')
    
    print('\n=== Sample data (first 20) ===')
    cursor.execute('SELECT canonical_name, category FROM canonical_ingredients ORDER BY canonical_name LIMIT 20')
    for row in cursor.fetchall():
        print(f'{row["canonical_name"]} - {row["category"]}')
    
    print('\n=== Searching for salt, steak, pepper ===')
    cursor.execute("""
        SELECT canonical_name, category 
        FROM canonical_ingredients 
        WHERE canonical_name ILIKE %s OR canonical_name ILIKE %s OR canonical_name ILIKE %s
    """, ('%salt%', '%steak%', '%pepper%'))
    results = cursor.fetchall()
    print(f'Found {len(results)} matches:')
    for row in results:
        print(f'  {row["canonical_name"]} - {row["category"]}')
    
    print('\n=== Checking for measurement issues ===')
    cursor.execute("""
        SELECT canonical_name, category 
        FROM canonical_ingredients 
        WHERE canonical_name LIKE '%cup%' OR canonical_name LIKE '%tablespoon%' OR canonical_name LIKE '%teaspoon%'
        ORDER BY canonical_name 
        LIMIT 10
    """)
    measurement_results = cursor.fetchall()
    print(f'Found {len(measurement_results)} ingredients with measurements:')
    for row in measurement_results:
        print(f'  {row["canonical_name"]} - {row["category"]}')
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f'Error: {e}')
