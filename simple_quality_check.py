#!/usr/bin/env python3
"""
Simple check of ATK recipe quality
"""

import psycopg2
import os

def check_atk_quality():
    """Simple quality check"""
    
    # Get database URL from environment or use Railway
    database_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:gOdHhLYpvyXMQEqeAdPnJHlnoBsrNHXz@junction.proxy.rlwy.net:14408/railway')
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("=== ATK Recipe Quality Check ===")
        
        cursor.execute("""
        SELECT title, page_number 
        FROM recipes 
        WHERE source = 'America''s Test Kitchen 25th Anniversary'
        ORDER BY id DESC 
        LIMIT 15
        """)
        
        recipes = cursor.fetchall()
        
        good = 0
        bad = 0
        
        for title, page in recipes:
            # Simple quality heuristics
            if (len(title) > 50 or  # Very long
                title.startswith(('½', '¼', '¾', '1', '2', '3')) or  # Starts with numbers
                any(word in title.lower() for word in ['cup', 'teaspoon', 'tablespoon', 'ounce']) or  # Has measurements
                title.lower() in ['soup', 'salad'] or  # Generic
                title.endswith(('.', ',', ';'))):  # Ends with punctuation
                print(f"❌ Page {page}: '{title}'")
                bad += 1
            else:
                print(f"✅ Page {page}: '{title}'")
                good += 1
        
        print(f"\n📊 Quality Summary:")
        print(f"✅ Good recipes: {good}")
        print(f"❌ Problematic recipes: {bad}")
        print(f"📈 Success rate: {good/(good+bad)*100:.1f}%")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_atk_quality()
