#!/usr/bin/env python3
"""
Analyze why we're getting such low extraction rates
"""

import sys
import os

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_systems.database_manager import DatabaseManager

def analyze_extraction_results():
    """Analyze the current extraction results and see what we got"""
    
    db = DatabaseManager()
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all ATK 25th recipes
            cursor.execute("""
                SELECT title, category, ingredients, instructions, page_number
                FROM recipes 
                WHERE source LIKE %s 
                ORDER BY page_number
            """, ('%ATK 25th%',))
            
            results = cursor.fetchall()
            
            print(f"🔍 CURRENT ATK 25TH EXTRACTION RESULTS")
            print("=" * 60)
            print(f"Total recipes found: {len(results)}")
            
            for i, (title, category, ingredients, instructions, page_num) in enumerate(results, 1):
                print(f"\n{i}. Page {page_num}: '{title}'")
                print(f"   Category: {category}")
                print(f"   Ingredients preview: {ingredients[:100] if ingredients else 'None'}...")
                print(f"   Instructions preview: {instructions[:100] if instructions else 'None'}...")
                
                # Check for issues
                issues = []
                if len(title) > 60:
                    issues.append("LONG_TITLE")
                if not title[0].isupper():
                    issues.append("NO_CAPITAL")
                if any(word in title.lower() for word in ['place', 'bake', 'heat', 'transfer']):
                    issues.append("INSTRUCTION_WORDS")
                if ' br ' in title or ' o ' in title or ' wir ' in title:
                    issues.append("BROKEN_WORDS")
                    
                if issues:
                    print(f"   ⚠️ Issues: {', '.join(issues)}")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_extraction_results()
