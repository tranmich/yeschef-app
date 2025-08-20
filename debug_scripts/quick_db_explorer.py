#!/usr/bin/env python3
"""
Quick database explorer for ATK recipes
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_systems.database_manager import DatabaseManager

def explore_atk_recipes():
    """Explore what's actually in the database"""
    db_manager = DatabaseManager()
    
    print("🔍 EXPLORING ATK RECIPES DATABASE")
    print("=" * 50)
    
    # Get sample titles
    query = """
    SELECT title, page_number, category, 
           LENGTH(ingredients) as ing_len,
           LENGTH(instructions) as inst_len,
           servings, total_time
    FROM recipes 
    WHERE source = 'The Complete Cookbook for Teen - America''s Test Kitchen Kids'
    ORDER BY page_number
    LIMIT 15
    """
    
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            recipes = cursor.fetchall()
            
            print(f"\nFound {len(recipes)} sample recipes:")
            for recipe in recipes:
                print(f"📄 Page {recipe['page_number']}: '{recipe['title']}'")
                print(f"   Category: {recipe.get('category', 'N/A')}")
                print(f"   Content: {recipe['ing_len']} chars ingredients, {recipe['inst_len']} chars instructions")
                print(f"   Servings: {recipe.get('servings', 'N/A')} | Time: {recipe.get('total_time', 'N/A')}")
                print()
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    explore_atk_recipes()
