#!/usr/bin/env python3
"""
Check for ATK Teen recipes in the database
"""

import sqlite3
import sys
import os

def check_teen_recipes():
    """Check for ATK Teen recipes"""
    try:
        # Connect to database
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'hungie.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("CHECKING FOR ATK TEEN RECIPES")
        print("=" * 50)

        # Check for recipes with "teen" in source
        cursor.execute("""
            SELECT COUNT(*), source 
            FROM recipes 
            WHERE LOWER(source) LIKE '%teen%' 
            GROUP BY source
            ORDER BY COUNT(*) DESC
        """)

        teen_sources = cursor.fetchall()

        if teen_sources:
            print("Found ATK Teen Recipe Sources:")
            total_teen = 0
            for count, source in teen_sources:
                print(f"  - {count} recipes from '{source}'")
                total_teen += count

            print(f"\nTotal ATK Teen recipes: {total_teen}")

            # Get sample recipes
            cursor.execute("""
                SELECT id, title, source 
                FROM recipes 
                WHERE LOWER(source) LIKE '%teen%' 
                LIMIT 5
            """)

            samples = cursor.fetchall()
            print("\nSample ATK Teen recipes:")
            for recipe_id, title, source in samples:
                print(f"  [{recipe_id}] {title} ({source})")

        else:
            print("No ATK Teen recipes found in database")

            # Check for other ATK sources
            cursor.execute("""
                SELECT COUNT(*), source 
                FROM recipes 
                WHERE LOWER(source) LIKE '%atk%' 
                GROUP BY source
                ORDER BY COUNT(*) DESC
            """)

            atk_sources = cursor.fetchall()
            print("\nAll ATK sources found:")
            for count, source in atk_sources:
                print(f"  - {count} recipes from '{source}'")

        conn.close()

    except Exception as e:
        print(f"Error checking teen recipes: {e}")

if __name__ == "__main__":
    check_teen_recipes()
