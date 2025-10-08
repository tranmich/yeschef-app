import psycopg2

try:
    conn = psycopg2.connect('postgresql://postgres:mik0512@localhost:5432/yeschef_app')
    cursor = conn.cursor()
    
    # Count total
    cursor.execute('SELECT COUNT(*) FROM canonical_ingredients')
    count = cursor.fetchone()[0]
    print(f'Canonical ingredients count: {count}')
    
    # Get top 20
    cursor.execute('''
        SELECT canonical_name, category, COUNT(*) as cnt 
        FROM canonical_ingredients 
        GROUP BY canonical_name, category 
        ORDER BY cnt DESC 
        LIMIT 20
    ''')
    
    print('\nTop 20 canonical ingredients:')
    for row in cursor.fetchall():
        print(f'  {row[0]} ({row[1]}): {row[2]} occurrences')
    
    # Check for garlic variations
    cursor.execute('''
        SELECT DISTINCT canonical_name 
        FROM canonical_ingredients 
        WHERE canonical_name ILIKE '%garlic%'
        ORDER BY canonical_name
        LIMIT 20
    ''')
    
    print('\nGarlic variations in canonical table:')
    for row in cursor.fetchall():
        print(f'  - {row[0]}')
    
    conn.close()
    
except Exception as e:
    print(f'Error: {e}')
