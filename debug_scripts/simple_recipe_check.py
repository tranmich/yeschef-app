#!/usr/bin/env python3
"""
Simple recipe count check
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_systems.database_manager import DatabaseManager

def main():
    try:
        db_manager = DatabaseManager()
        
        print("DATABASE RECIPE CHECK")
        print("=" * 30)

        with db_manager.get_connection() as conn:
            cursor = conn.cursor()

            # Total count
            cursor.execute("SELECT COUNT(*) FROM recipes")
            result = cursor.fetchone()
            total = result[0] if result else 0
            print(f"Total recipes: {total}")

            # Sources
            cursor.execute("SELECT source, COUNT(*) FROM recipes GROUP BY source ORDER BY COUNT(*) DESC LIMIT 5")
            results = cursor.fetchall()
            
            print(f"\nTop sources:")
            for source, count in results:
                source_short = source[:50] + "..." if len(source) > 50 else source
                print(f"  {count} recipes - {source_short}")
                
            # Recent recipes
            cursor.execute("SELECT title, source FROM recipes ORDER BY id DESC LIMIT 5")
            recent = cursor.fetchall()
            
            print(f"\nMost recent recipes:")
            for title, source in recent:
                title_short = title[:40] + "..." if len(title) > 40 else title
                print(f"  '{title_short}' from {source}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
