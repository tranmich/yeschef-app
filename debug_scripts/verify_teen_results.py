#!/usr/bin/env python3
"""Verify ATK Teen flavor analysis results"""

import psycopg2
import json

def verify_teen_results():
    try:
        database_url = 'postgresql://postgres:udQLpljdqTYmESmntwzmwDcOlBVbqlJG@shuttle.proxy.rlwy.net:31331/railway'
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("🔍 VERIFYING ATK TEEN FLAVOR ANALYSIS RESULTS")
        print("=" * 60)
        
        # Count Teen recipes with flavor profiles
        cursor.execute("""
            SELECT COUNT(*) 
            FROM recipe_flavor_profiles rfp 
            JOIN recipes r ON r.id = rfp.recipe_id 
            WHERE r.source LIKE '%Teen%'
        """)
        count = cursor.fetchone()[0]
        print(f"✅ Total ATK Teen recipes with flavor profiles: {count}")
        
        # Show some examples
        cursor.execute("""
            SELECT r.title, rfp.primary_flavors, rfp.cuisine_style, rfp.complexity_score, rfp.intensity
            FROM recipes r 
            JOIN recipe_flavor_profiles rfp ON r.id = rfp.recipe_id 
            WHERE r.source LIKE '%Teen%' 
            AND r.title NOT LIKE 'Start Cooking!%'
            AND r.title != 'PREPARE INGREDIENTS'
            ORDER BY rfp.created_at DESC
            LIMIT 10
        """)
        
        examples = cursor.fetchall()
        
        if examples:
            print(f"\n🍽️ Sample Teen Recipe Flavor Profiles:")
            for i, (title, flavors, cuisine, complexity, intensity) in enumerate(examples, 1):
                # Parse flavors (they're stored as JSON)
                try:
                    if isinstance(flavors, str):
                        flavor_list = json.loads(flavors)
                    else:
                        flavor_list = flavors
                    
                    flavor_str = ', '.join(flavor_list) if flavor_list else 'None'
                except:
                    flavor_str = str(flavors)
                
                print(f"  {i}. {title}")
                print(f"     🎨 Flavors: {flavor_str}")
                print(f"     🌍 Cuisine: {cuisine} | 📊 Complexity: {complexity}/10 | 🔥 Intensity: {intensity}")
                print()
        
        # Summary by cuisine
        cursor.execute("""
            SELECT rfp.cuisine_style, COUNT(*) as recipe_count
            FROM recipe_flavor_profiles rfp 
            JOIN recipes r ON r.id = rfp.recipe_id 
            WHERE r.source LIKE '%Teen%'
            GROUP BY rfp.cuisine_style
            ORDER BY recipe_count DESC
        """)
        
        cuisine_stats = cursor.fetchall()
        
        print(f"\n📊 Teen Recipes by Cuisine Style:")
        for cuisine, recipe_count in cuisine_stats:
            print(f"  🌍 {cuisine}: {recipe_count} recipes")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verify_teen_results()
