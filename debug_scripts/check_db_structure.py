#!/usr/bin/env python3
"""
Check database structure and ATK Teen recipes
"""

import sqlite3
import os

def check_database():
    """Check database structure and content"""
    try:
        # Connect to database
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'hungie.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("CHECKING DATABASE STRUCTURE")
        print("=" * 50)
        
        # Check available tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print("Available tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check if we have recipe-related tables
        table_names = [table[0] for table in tables]
        
        if 'recipe_data' in table_names:
            print("\nChecking recipe_data table...")
            cursor.execute("SELECT COUNT(*) FROM recipe_data")
            count = cursor.fetchone()[0]
            print(f"Total recipes in recipe_data: {count}")
            
            # Check for ATK Teen recipes
            cursor.execute("""
                SELECT COUNT(*), source 
                FROM recipe_data 
                WHERE LOWER(source) LIKE '%teen%' 
                GROUP BY source
            """)
            teen_results = cursor.fetchall()
            
            if teen_results:
                print("\nATK Teen recipes found:")
                for count, source in teen_results:
                    print(f"  - {count} from '{source}'")
            else:
                print("\nNo ATK Teen recipes found")
                
                # Check all ATK sources
                cursor.execute("""
                    SELECT COUNT(*), source 
                    FROM recipe_data 
                    WHERE LOWER(source) LIKE '%atk%' 
                    GROUP BY source 
                    ORDER BY COUNT(*) DESC
                """)
                atk_results = cursor.fetchall()
                
                print("\nAll ATK sources:")
                for count, source in atk_results:
                    print(f"  - {count} from '{source}'")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_database()
