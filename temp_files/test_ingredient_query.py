import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = 'postgresql://postgres:udQLpljdqTYmESmntwzmwDcOlBVbqlJG@shuttle.proxy.rlwy.net:31331/railway'

try:
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    
    print('Testing the cleaned ingredient query...')
    
    # Test the filtering query
    cursor.execute("""
        SELECT DISTINCT canonical_name, category 
        FROM canonical_ingredients 
        WHERE canonical_name NOT LIKE '%cup%'
        AND canonical_name NOT LIKE '%teaspoon%'
        AND canonical_name NOT LIKE '%tablespoon%'
        AND canonical_name NOT LIKE '%[%'
        AND canonical_name NOT LIKE '"%'
        AND canonical_name NOT LIKE '%{%'
        AND canonical_name NOT LIKE '½%'
        AND canonical_name NOT LIKE '¼%'
        AND canonical_name NOT LIKE '1%'
        AND canonical_name NOT LIKE '2%'
        AND canonical_name NOT LIKE '3%'
        AND canonical_name NOT LIKE '4%'
        AND canonical_name NOT LIKE '5%'
        AND LENGTH(canonical_name) < 50
        ORDER BY canonical_name
        LIMIT 30
    """)
    
    results = cursor.fetchall()
    print(f'Found {len(results)} clean ingredients:')
    for row in results:
        print(f'  {row["canonical_name"]} - {row["category"]}')
    
    # Test specific searches
    print('\n=== Testing specific ingredient searches ===')
    test_searches = ['salt', 'steak', 'pepper', 'chicken', 'onion']
    for search_term in test_searches:
        cursor.execute("""
            SELECT canonical_name, category 
            FROM canonical_ingredients 
            WHERE canonical_name ILIKE %s
            AND canonical_name NOT LIKE '%cup%'
            AND canonical_name NOT LIKE '%teaspoon%'
            AND canonical_name NOT LIKE '%tablespoon%'
            AND canonical_name NOT LIKE '%[%'
            AND canonical_name NOT LIKE '"%'
            AND LENGTH(canonical_name) < 50
            ORDER BY LENGTH(canonical_name)
        """, (f'%{search_term}%',))
        results = cursor.fetchall()
        print(f'{search_term}: Found {len(results)} clean matches')
        for row in results[:3]:  # Show first 3 matches
            print(f'  - {row["canonical_name"]} ({row["category"]})')
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f'Error: {e}')
