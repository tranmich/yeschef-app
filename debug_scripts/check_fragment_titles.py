#!/usr/bin/env python3
"""
Quick script to check fragment title extraction issues
"""

import sqlite3
import sys
import os

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_fragment_titles():
    """Check recent ATK extractions for fragment titles"""
    try:
        conn = sqlite3.connect('hungie.db')
        cursor = conn.cursor()
        
        # Get recent ATK 25th extractions
        cursor.execute('''
            SELECT title, source, ingredients, instructions 
            FROM recipes 
            WHERE source LIKE "%ATK 25th%" 
            ORDER BY id DESC 
            LIMIT 15
        ''')
        
        results = cursor.fetchall()
        print(f"Found {len(results)} recent ATK 25th extractions:")
        print("=" * 60)
        
        fragments = []
        proper_recipes = []
        
        for i, (title, source, ingredients, instructions) in enumerate(results, 1):
            print(f"\n{i}. Title: '{title}'")
            print(f"   Source: {source}")
            print(f"   Ingredients length: {len(ingredients) if ingredients else 0}")
            print(f"   Instructions length: {len(instructions) if instructions else 0}")
            
            # Check for fragment patterns
            is_fragment = False
            
            # Check for obvious fragments
            if (len(title) < 10 or 
                title.lower() in ['soup', 'salad', 'sauce', 'dressing'] or
                any(word in title.lower() for word in ['cup', 'tablespoon', 'teaspoon', 'pound', 'ounce']) or
                title.count(' ') > 8 or  # Too many words (likely a sentence fragment)
                not title[0].isupper() or  # Doesn't start with capital
                title.endswith('.') or title.endswith(',') or  # Fragment ending
                any(char in title for char in ['(', ')', '[', ']']) or  # Contains brackets
                title.startswith('•') or title.startswith('-')):  # List item
                is_fragment = True
                fragments.append((title, source))
            else:
                proper_recipes.append((title, source))
                
            print(f"   Fragment: {'YES' if is_fragment else 'NO'}")
        
        print(f"\n\nSUMMARY:")
        print(f"Proper recipes: {len(proper_recipes)}")
        print(f"Fragments: {len(fragments)}")
        
        if fragments:
            print(f"\nFragment examples:")
            for title, source in fragments[:5]:
                print(f"  - '{title}'")
                
        conn.close()
        return len(proper_recipes), len(fragments)
        
    except Exception as e:
        print(f"Error checking database: {e}")
        return 0, 0

if __name__ == "__main__":
    proper, fragments = check_fragment_titles()
    print(f"\nResult: {proper} proper recipes, {fragments} fragments detected")
