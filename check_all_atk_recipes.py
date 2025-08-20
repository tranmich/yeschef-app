#!/usr/bin/env python3
"""
Check all ATK recipes in the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core_systems.database_manager import DatabaseManager

def check_all_atk_recipes():
    """Check all ATK recipes in the database"""
    
    db = DatabaseManager()
    
    print("=== All ATK Recipes in Database ===")
    
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                # First check what sources we have
                cursor.execute("SELECT DISTINCT source, COUNT(*) FROM recipes GROUP BY source ORDER BY source")
                sources = cursor.fetchall()
                
                print("Recipe sources in database:")
                for source in sources:
                    print(f"  {source[1]:3d} recipes from '{source[0]}'")
                
                print("\n" + "="*60)
                
                # Get all recipes with 'ATK' in the source
                cursor.execute("""
                SELECT id, title, source, page_number, created_at
                FROM recipes 
                WHERE source LIKE '%ATK%' 
                ORDER BY created_at DESC 
                LIMIT 50
                """)
                results = cursor.fetchall()
                
                if results:
                    print(f"\nFound {len(results)} ATK recipes:")
                    for i, recipe in enumerate(results, 1):
                        print(f"{i:2d}. '{recipe[1]}' (Page {recipe[3]}) - {recipe[2]} - {recipe[4]}")
                else:
                    print("No ATK recipes found")
                    
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    check_all_atk_recipes()
