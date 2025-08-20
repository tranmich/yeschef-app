#!/usr/bin/env python3
"""
Check for all ATK recipes in the database
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_systems.database_manager import DatabaseManager

def check_atk_recipes():
    """Check for all ATK recipes"""
    try:
        db_manager = DatabaseManager()
        
        print("CHECKING FOR ALL ATK RECIPES")
        print("=" * 50)

        with db_manager.get_connection() as conn:
            cursor = conn.cursor()

            # Check for all ATK sources
            cursor.execute("""
                SELECT COUNT(*), source 
                FROM recipes 
                WHERE LOWER(source) LIKE '%atk%' OR LOWER(source) LIKE '%america''s test kitchen%'
                GROUP BY source
                ORDER BY COUNT(*) DESC
            """)

            atk_sources = cursor.fetchall()

            if atk_sources:
                print("Found ATK Recipe Sources:")
                total_atk = 0
                for count, source in atk_sources:
                    print(f"  - {count} recipes from '{source}'")
                    total_atk += count

                print(f"\nTotal ATK recipes: {total_atk}")

                # Get sample recipes from each source
                for count, source in atk_sources:
                    print(f"\nSample recipes from '{source}':")
                    cursor.execute("""
                        SELECT id, title 
                        FROM recipes 
                        WHERE source = %s
                        ORDER BY created_at DESC
                        LIMIT 5
                    """, (source,))

                    samples = cursor.fetchall()
                    for recipe_id, title in samples:
                        print(f"  [{recipe_id}] {title}")

            else:
                print("No ATK recipes found in database")

                # Check total recipes
                cursor.execute("SELECT COUNT(*) FROM recipes")
                total_count = cursor.fetchone()[0]
                print(f"Total recipes in database: {total_count}")

    except Exception as e:
        print(f"Error checking ATK recipes: {e}")

if __name__ == "__main__":
    check_atk_recipes()
