import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = 'postgresql://postgres:udQLpljdqTYmESmntwzmwDcOlBVbqlJG@shuttle.proxy.rlwy.net:31331/railway'

try:
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    
    print('Adding clean ingredient names to canonical_ingredients...')
    
    # List of clean, common ingredients without measurements
    clean_ingredients = [
        ('salt', 'spice'),
        ('pepper', 'spice'),
        ('black pepper', 'spice'),
        ('white pepper', 'spice'),
        ('steak', 'protein'),
        ('beef steak', 'protein'),
        ('sirloin steak', 'protein'),
        ('ribeye steak', 'protein'),
        ('chicken breast', 'protein'),
        ('chicken', 'protein'),
        ('chicken thighs', 'protein'),
        ('ground beef', 'protein'),
        ('ground turkey', 'protein'),
        ('pork chops', 'protein'),
        ('bacon', 'protein'),
        ('salmon', 'protein'),
        ('tuna', 'protein'),
        ('shrimp', 'protein'),
        ('eggs', 'protein'),
        ('onion', 'produce'),
        ('red onion', 'produce'),
        ('yellow onion', 'produce'),
        ('garlic', 'produce'),
        ('tomato', 'produce'),
        ('tomatoes', 'produce'),
        ('cherry tomatoes', 'produce'),
        ('bell pepper', 'produce'),
        ('red pepper', 'produce'),
        ('green pepper', 'produce'),
        ('jalapeño', 'produce'),
        ('carrot', 'produce'),
        ('celery', 'produce'),
        ('potato', 'produce'),
        ('sweet potato', 'produce'),
        ('broccoli', 'produce'),
        ('spinach', 'produce'),
        ('lettuce', 'produce'),
        ('kale', 'produce'),
        ('cabbage', 'produce'),
        ('avocado', 'produce'),
        ('corn', 'produce'),
        ('peas', 'produce'),
        ('green beans', 'produce'),
        ('mushrooms', 'produce'),
        ('button mushrooms', 'produce'),
        ('shiitake mushrooms', 'produce'),
        ('lemon', 'produce'),
        ('lime', 'produce'),
        ('orange', 'produce'),
        ('apple', 'produce'),
        ('banana', 'produce'),
        ('olive oil', 'cooking'),
        ('vegetable oil', 'cooking'),
        ('canola oil', 'cooking'),
        ('coconut oil', 'cooking'),
        ('butter', 'dairy'),
        ('unsalted butter', 'dairy'),
        ('milk', 'dairy'),
        ('heavy cream', 'dairy'),
        ('sour cream', 'dairy'),
        ('yogurt', 'dairy'),
        ('greek yogurt', 'dairy'),
        ('cheese', 'dairy'),
        ('cheddar cheese', 'dairy'),
        ('mozzarella cheese', 'dairy'),
        ('parmesan cheese', 'dairy'),
        ('swiss cheese', 'dairy'),
        ('feta cheese', 'dairy'),
        ('cream cheese', 'dairy'),
        ('flour', 'grain'),
        ('all-purpose flour', 'grain'),
        ('whole wheat flour', 'grain'),
        ('bread flour', 'grain'),
        ('rice', 'grain'),
        ('brown rice', 'grain'),
        ('white rice', 'grain'),
        ('pasta', 'grain'),
        ('spaghetti', 'grain'),
        ('penne', 'grain'),
        ('bread', 'grain'),
        ('whole wheat bread', 'grain'),
        ('oats', 'grain'),
        ('quinoa', 'grain'),
        ('sugar', 'baking'),
        ('brown sugar', 'baking'),
        ('powdered sugar', 'baking'),
        ('honey', 'baking'),
        ('maple syrup', 'baking'),
        ('vanilla extract', 'baking'),
        ('baking powder', 'baking'),
        ('baking soda', 'baking'),
        ('yeast', 'baking'),
        ('cinnamon', 'spice'),
        ('paprika', 'spice'),
        ('cumin', 'spice'),
        ('chili powder', 'spice'),
        ('oregano', 'herb'),
        ('basil', 'herb'),
        ('thyme', 'herb'),
        ('rosemary', 'herb'),
        ('parsley', 'herb'),
        ('cilantro', 'herb'),
        ('dill', 'herb'),
        ('sage', 'herb'),
        ('bay leaves', 'herb'),
        ('red wine', 'cooking'),
        ('white wine', 'cooking'),
        ('beer', 'cooking'),
        ('vinegar', 'cooking'),
        ('balsamic vinegar', 'cooking'),
        ('apple cider vinegar', 'cooking'),
        ('soy sauce', 'cooking'),
        ('worcestershire sauce', 'cooking'),
        ('hot sauce', 'cooking'),
        ('ketchup', 'cooking'),
        ('mustard', 'cooking'),
        ('dijon mustard', 'cooking'),
        ('mayonnaise', 'cooking'),
        ('sriracha', 'cooking'),
        ('chicken broth', 'cooking'),
        ('beef broth', 'cooking'),
        ('vegetable broth', 'cooking'),
        ('coconut milk', 'cooking'),
        ('black beans', 'protein'),
        ('kidney beans', 'protein'),
        ('chickpeas', 'protein'),
        ('lentils', 'protein'),
        ('tofu', 'protein'),
        ('nuts', 'other'),
        ('almonds', 'other'),
        ('walnuts', 'other'),
        ('pecans', 'other'),
        ('peanuts', 'other'),
        ('pine nuts', 'other'),
    ]
    
    # Insert clean ingredients (skip if already exists)
    added_count = 0
    for ingredient, category in clean_ingredients:
        try:
            cursor.execute('''
                INSERT INTO canonical_ingredients (canonical_name, category) 
                VALUES (%s, %s) 
                ON CONFLICT (canonical_name) DO NOTHING
            ''', (ingredient, category))
            if cursor.rowcount > 0:
                added_count += 1
        except Exception as e:
            print(f"Error adding {ingredient}: {e}")
    
    conn.commit()
    print(f'Added {added_count} new clean ingredients')
    
    # Get final count
    cursor.execute('SELECT COUNT(*) as total FROM canonical_ingredients')
    total = cursor.fetchone()['total']
    print(f'Total ingredients now: {total}')
    
    # Test our specific searches
    print('\n=== Testing searches ===')
    test_searches = ['salt', 'steak', 'pepper', 'chicken', 'onion']
    for search_term in test_searches:
        cursor.execute('''
            SELECT canonical_name, category 
            FROM canonical_ingredients 
            WHERE canonical_name ILIKE %s
            ORDER BY canonical_name
        ''', (f'%{search_term}%',))
        results = cursor.fetchall()
        print(f'{search_term}: Found {len(results)} matches')
        for row in results[:3]:  # Show first 3 matches
            print(f'  - {row["canonical_name"]} ({row["category"]})')
    
    cursor.close()
    conn.close()
    print('\nDatabase update complete!')
    
except Exception as e:
    print(f'Error: {e}')
