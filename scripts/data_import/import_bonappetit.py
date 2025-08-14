import sqlite3
import json
import hashlib
from datetime import datetime

def generate_id(text):
    """Generate a consistent hash ID for text"""
    return hashlib.md5(text.encode()).hexdigest()

def import_bonappetit_collection():
    # Read the latest BonAppétit session collection
    with open('data/session_dinner_100recipes_2025-08-01T17-47.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Found {data['sessionInfo']['recipesCollected']} recipes to import")
    
    # Connect to database
    conn = sqlite3.connect('hungie.db')
    cursor = conn.cursor()
    
    # Create BonAppétit category if it doesn't exist
    bonappetit_category_id = generate_id('bonappetit')
    cursor.execute('''
        INSERT OR IGNORE INTO categories (id, name) 
        VALUES (?, ?)
    ''', (bonappetit_category_id, 'bonappetit'))
    
    imported_count = 0
    skipped_count = 0
    
    for recipe in data['recipes']:
        try:
            # Generate recipe ID from name or URL
            recipe_id = generate_id(recipe['name'] + recipe['metadata']['url'])
            
            # Check if recipe already exists
            cursor.execute('SELECT id FROM recipes WHERE id = ?', (recipe_id,))
            if cursor.fetchone():
                print(f"Skipping duplicate: {recipe['name']}")
                skipped_count += 1
                continue
            
            # Extract timing information (if available)
            prep_time = ''
            cook_time = ''
            total_time = ''
            servings = None
            
            # Insert recipe
            cursor.execute('''
                INSERT INTO recipes (
                    id, name, description, prep_time, cook_time, 
                    total_time, servings, url, date_saved
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                recipe_id,
                recipe['name'],
                recipe.get('description', ''),
                prep_time,
                cook_time,
                total_time,
                servings,
                recipe['metadata']['url'],
                recipe['metadata']['date_saved']
            ))
            
            # Add to BonAppétit category
            cursor.execute('''
                INSERT INTO recipe_categories (recipe_id, category_id)
                VALUES (?, ?)
            ''', (recipe_id, bonappetit_category_id))
            
            # Process ingredients
            for ingredient_data in recipe.get('ingredients', []):
                ingredient_text = ingredient_data.get('text', ingredient_data.get('original', ''))
                
                # Skip malformed ingredients (like HTML content)
                if '<' in ingredient_text or len(ingredient_text) > 500:
                    continue
                
                ingredient_id = generate_id(ingredient_text)
                
                # Insert ingredient if not exists
                cursor.execute('''
                    INSERT OR IGNORE INTO ingredients (id, name)
                    VALUES (?, ?)
                ''', (ingredient_id, ingredient_text))
                
                # Link ingredient to recipe
                cursor.execute('''
                    INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit)
                    VALUES (?, ?, ?, ?)
                ''', (recipe_id, ingredient_id, '', ''))
            
            # Process instructions
            for instruction in recipe.get('instructions', []):
                step_number = instruction.get('step', 0)
                instruction_text = instruction.get('text', '')
                
                cursor.execute('''
                    INSERT INTO instructions (recipe_id, step_number, instruction)
                    VALUES (?, ?, ?)
                ''', (recipe_id, step_number, instruction_text))
            
            imported_count += 1
            print(f"Imported: {recipe['name']}")
            
        except Exception as e:
            print(f"Error importing {recipe.get('name', 'Unknown')}: {e}")
            continue
    
    # Commit changes
    conn.commit()
    
    # Print summary
    print(f"\n--- Import Summary ---")
    print(f"Total recipes in collection: {data['sessionInfo']['recipesCollected']}")
    print(f"Successfully imported: {imported_count}")
    print(f"Skipped (duplicates): {skipped_count}")
    print(f"Failed: {data['sessionInfo']['recipesCollected'] - imported_count - skipped_count}")
    
    # Show updated database stats
    cursor.execute('SELECT COUNT(*) FROM recipes')
    total_recipes = cursor.fetchone()[0]
    print(f"Total recipes in database: {total_recipes}")
    
    cursor.execute('''
        SELECT COUNT(*) FROM recipes r 
        JOIN recipe_categories rc ON r.id = rc.recipe_id
        JOIN categories c ON rc.category_id = c.id
        WHERE c.name = 'bonappetit'
    ''')
    bonappetit_count = cursor.fetchone()[0]
    print(f"BonAppétit recipes in database: {bonappetit_count}")
    
    conn.close()

if __name__ == "__main__":
    import_bonappetit_collection()
