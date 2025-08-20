#!/usr/bin/env python3
"""
Check the quality of recently extracted ATK 25th recipes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core_systems.database_manager import DatabaseManager

def check_recent_atk_recipes():
    """Check the recently extracted ATK 25th recipes"""
    
    db = DatabaseManager()
    
    print("=== Recently Extracted ATK 25th Anniversary Recipes ===")
    
    # Get the most recent ATK 25th recipes
    query = """
    SELECT id, title, source, page_number, 
           LEFT(ingredients, 100) as ingredients_preview,
           LEFT(instructions, 100) as instructions_preview,
           created_at
    FROM recipes 
    WHERE source LIKE '%ATK 25th%' 
    ORDER BY created_at DESC 
    LIMIT 30
    """
    
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
    except Exception as e:
        print(f"Database error: {e}")
        return
    
    if results:
        print(f"Found {len(results)} recent ATK 25th recipes:")
        print()
        
        for i, recipe in enumerate(results, 1):
            print(f"{i:2d}. '{recipe['title']}' (Page {recipe['page_number']})")
            print(f"    Ingredients: {recipe['ingredients_preview']}...")
            print(f"    Instructions: {recipe['instructions_preview']}...")
            print(f"    Created: {recipe['created_at']}")
            print()
            
        # Check for suspicious titles (likely fragments)
        suspicious_titles = []
        good_titles = []
        
        for recipe in results:
            title = recipe['title']
            # Check for common signs of incomplete extraction
            if (len(title) > 50 or  # Very long titles
                title.startswith(('½', '¼', '¾', '1', '2', '3', '4', '5', '6', '7', '8', '9')) or  # Starts with measurements
                'cup' in title.lower() or 'teaspoon' in title.lower() or 'tablespoon' in title.lower() or  # Contains measurements
                title.endswith(('.', ',', ';')) or  # Ends with punctuation (incomplete sentence)
                'plus' in title.lower() or 'add' in title.lower() or  # Instruction fragments
                len(title.split()) > 10):  # Very long titles
                suspicious_titles.append(title)
            else:
                good_titles.append(title)
        
        print(f"\n=== Quality Analysis ===")
        print(f"✅ Good titles: {len(good_titles)}")
        print(f"⚠️ Suspicious titles: {len(suspicious_titles)}")
        
        if suspicious_titles:
            print("\n⚠️ Suspicious titles (likely fragments):")
            for title in suspicious_titles:
                print(f"  - '{title}'")
        
        if good_titles:
            print("\n✅ Good titles:")
            for title in good_titles:
                print(f"  - '{title}'")
                
    else:
        print("No recent ATK 25th recipes found")

if __name__ == "__main__":
    check_recent_atk_recipes()
