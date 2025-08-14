import sqlite3

# Test searching for our new recipes directly in the database
conn = sqlite3.connect('hungie.db')
cursor = conn.cursor()

# Search for "Overnight Oats" recipe
cursor.execute("SELECT id, title, url FROM recipes WHERE title LIKE '%Overnight Oats%'")
results = cursor.fetchall()

if results:
    print("Found Overnight Oats recipe:")
    for recipe_id, title, url in results:
        print(f"  ID: {recipe_id}")
        print(f"  Title: {title}")
        print(f"  URL: {url}")
        
        # Get ingredients for this recipe
        cursor.execute("""
            SELECT i.name 
            FROM ingredients i 
            JOIN recipe_ingredients ri ON i.id = ri.ingredient_id 
            WHERE ri.recipe_id = ?
            LIMIT 5
        """, (recipe_id,))
        ingredients = cursor.fetchall()
        print(f"  First 5 ingredients: {[ing[0] for ing in ingredients]}")
        
        # Get instructions
        cursor.execute("SELECT instruction FROM instructions WHERE recipe_id = ? ORDER BY step_number LIMIT 3", (recipe_id,))
        instructions = cursor.fetchall()
        print(f"  First 3 instructions: {[inst[0][:100] + '...' if len(inst[0]) > 100 else inst[0] for inst in instructions]}")
else:
    print("No Overnight Oats recipe found")

conn.close()
