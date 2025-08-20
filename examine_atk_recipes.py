#!/usr/bin/env python3
"""
Examine the recently extracted ATK recipes to understand the quality issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core_systems.database_manager import DatabaseManager

def examine_atk_recipes():
    """Examine the ATK 25th recipes"""
    
    db = DatabaseManager()
    
    print("=== Examining ATK 25th Anniversary Recipes ===")
    
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                SELECT id, title, page_number, 
                       LEFT(ingredients, 200) as ingredients_preview,
                       LEFT(instructions, 200) as instructions_preview
                FROM recipes 
                WHERE source = 'America''s Test Kitchen 25th Anniversary'
                ORDER BY id DESC 
                LIMIT 10
                """)
                results = cursor.fetchall()
                
                if results:
                    print(f"Found {len(results)} recent recipes. Examining first 10:")
                    print()
                    
                    for i, recipe in enumerate(results, 1):
                        print(f"{i}. RECIPE ID {recipe[0]} - Page {recipe[2]}")
                        print(f"   Title: '{recipe[1]}'")
                        print(f"   Ingredients: {recipe[3]}...")
                        print(f"   Instructions: {recipe[4]}...")
                        print()
                        
                        # Quick quality assessment
                        title = recipe[1]
                        if (len(title) < 20 and 
                            not any(word in title.lower() for word in ['recipe', 'with', 'and', 'chicken', 'beef', 'pasta', 'salad']) and
                            title.lower() not in ['soup', 'salad', 'sauce']):
                            quality = "✅ Looks good"
                        else:
                            quality = "⚠️ Suspicious"
                            
                        print(f"   Quality: {quality}")
                        print("   " + "="*60)
                        print()
                        
                else:
                    print("No ATK 25th recipes found")
                    
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    examine_atk_recipes()
