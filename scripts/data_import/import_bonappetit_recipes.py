import json
import sqlite3
import hashlib
from datetime import datetime

def import_bonappetit_recipes():
    """Import BonAppetitePersonal recipe collections into hungie.db"""
    
    # Recipe files to import
    files = [
        'data/session_breakfast_59recipes_2025-08-06T11-28.json',
        'data/session_sides_16recipes_2025-08-06T18-08.json', 
        'data/session_vegetarian_33recipes_2025-08-06T17-49.json'
    ]
    
    # Connect to database
    conn = sqlite3.connect('hungie.db')
    cursor = conn.cursor()
    
    total_imported = 0
    
    for file_path in files:
        print(f"\nProcessing {file_path}...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Get recipes from the recipes section
            recipes = data.get('recipes', [])
            print(f"Found {len(recipes)} recipes in file")
            
            for recipe in recipes:
                try:
                    # Generate a unique ID for this recipe using URL hash
                    recipe_id = hashlib.md5(recipe['metadata']['url'].encode()).hexdigest()
                    
                    # Check if recipe already exists
                    cursor.execute("SELECT id FROM recipes WHERE url = ?", (recipe['metadata']['url'],))
                    if cursor.fetchone():
                        print(f"  Skipping duplicate: {recipe['name']}")
                        continue
                    
                    # Insert recipe into recipes table
                    cursor.execute("""
                        INSERT INTO recipes (
                            id, book_id, title, page_number, servings, hands_on_time, 
                            total_time, ingredients, instructions, description, url, date_saved
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        recipe_id,                              # id
                        None,                                   # book_id (not applicable)
                        recipe['name'],                         # title
                        None,                                   # page_number (not applicable)
                        None,                                   # servings (not in this data)
                        None,                                   # hands_on_time (not in this data)
                        None,                                   # total_time (not in this data)
                        json.dumps([ing['ingredient'] for ing in recipe.get('ingredients', [])]),  # ingredients as JSON
                        json.dumps([inst['text'] for inst in recipe.get('instructions', [])]),     # instructions as JSON
                        recipe.get('description', ''),         # description
                        recipe['metadata']['url'],              # url
                        recipe['metadata']['date_saved']        # date_saved
                    ))
                    
                    # Insert ingredients into ingredients table (if not exists) and recipe_ingredients
                    for idx, ingredient_data in enumerate(recipe.get('ingredients', [])):
                        ingredient_text = ingredient_data['ingredient']
                        
                        # Check if ingredient exists
                        cursor.execute("SELECT id FROM ingredients WHERE name = ?", (ingredient_text,))
                        ingredient_row = cursor.fetchone()
                        
                        if not ingredient_row:
                            # Insert new ingredient
                            cursor.execute("""
                                INSERT INTO ingredients (name, normalized_name, category) 
                                VALUES (?, ?, ?)
                            """, (ingredient_text, ingredient_text.lower(), None))
                            ingredient_id = cursor.lastrowid
                        else:
                            ingredient_id = ingredient_row[0]
                        
                        # Insert into recipe_ingredients
                        cursor.execute("""
                            INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, preparation)
                            VALUES (?, ?, ?, ?, ?)
                        """, (recipe_id, ingredient_id, None, None, None))
                    
                    # Insert instructions into instructions table
                    for instruction_data in recipe.get('instructions', []):
                        cursor.execute("""
                            INSERT INTO instructions (recipe_id, step_number, instruction)
                            VALUES (?, ?, ?)
                        """, (recipe_id, instruction_data['step'], instruction_data['text']))
                    
                    # Handle categories
                    for category_name in recipe.get('categories', []):
                        # Check if category exists
                        cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
                        category_row = cursor.fetchone()
                        
                        if not category_row:
                            # Insert new category
                            cursor.execute("INSERT INTO categories (name) VALUES (?)", (category_name,))
                            category_id = cursor.lastrowid
                        else:
                            category_id = category_row[0]
                        
                        # Link recipe to category
                        cursor.execute("""
                            INSERT OR IGNORE INTO recipe_categories (recipe_id, category_id)
                            VALUES (?, ?)
                        """, (recipe_id, category_id))
                    
                    total_imported += 1
                    print(f"  ✓ Imported: {recipe['name']}")
                    
                except Exception as e:
                    print(f"  ✗ Error importing {recipe.get('name', 'Unknown')}: {e}")
                    continue
        
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue
    
    # Commit all changes
    conn.commit()
    conn.close()
    
    print(f"\n✅ Import complete! {total_imported} recipes imported successfully.")

if __name__ == "__main__":
    import_bonappetit_recipes()
