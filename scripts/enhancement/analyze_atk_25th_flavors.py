#!/usr/bin/env python3
"""
🎨 ATK 25th Anniversary Flavor Profile Generator
==============================================

Specifically analyzes the 1000+ ATK 25th Anniversary recipes we just extracted
and generates comprehensive flavor profiles for each.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'core_systems'))

from recipe_flavor_analyzer import RecipeFlavorAnalyzer
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

def analyze_atk_25th_recipes():
    """Analyze all ATK 25th Anniversary recipes for flavor profiles"""
    print("🎨 ATK 25TH ANNIVERSARY FLAVOR ANALYSIS")
    print("=" * 60)
    
    analyzer = RecipeFlavorAnalyzer()
    
    try:
        # Connect to database
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            db_url = "postgresql://postgres:bBPQiSOwjkCnYdydFUcQKXeiFGFdIsgh@junction.proxy.rlwy.net:40067/railway"
        
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Find ATK 25th Anniversary recipes without flavor profiles
        cursor.execute("""
            SELECT r.id, r.title, r.ingredients, r.instructions, r.source, r.category
            FROM recipes r
            LEFT JOIN recipe_flavor_profiles fp ON r.id = fp.recipe_id
            WHERE fp.recipe_id IS NULL
            AND r.source = %s
            AND r.ingredients IS NOT NULL
            ORDER BY r.id
        """, ("America's Test Kitchen 25th Anniversary",))
        
        recipes = cursor.fetchall()
        
        print(f"📊 Found {len(recipes)} ATK 25th Anniversary recipes to analyze")
        
        if len(recipes) == 0:
            print("ℹ️ No ATK 25th Anniversary recipes found without flavor profiles")
            return
        
        processed = 0
        errors = 0
        sample_profiles = []
        
        for i, recipe in enumerate(recipes, 1):
            try:
                print(f"\n🔍 [{i}/{len(recipes)}] {recipe['title'][:60]}...")
                
                # Analyze recipe
                flavor_profile = analyzer.analyze_recipe(dict(recipe))
                
                # Save to database
                if analyzer.save_flavor_profile(flavor_profile):
                    processed += 1
                    
                    # Collect first 5 for sample output
                    if len(sample_profiles) < 5:
                        sample_profiles.append({
                            'title': recipe['title'],
                            'primary_flavors': flavor_profile.primary_flavors,
                            'cuisine_style': flavor_profile.cuisine_style,
                            'intensity': flavor_profile.intensity,
                            'complexity_score': flavor_profile.complexity_score,
                            'harmony_score': flavor_profile.harmony_score
                        })
                    
                    print(f"     ✅ Analyzed - {', '.join(flavor_profile.primary_flavors)} | {flavor_profile.cuisine_style} | {flavor_profile.complexity_score}/10")
                else:
                    print(f"     ❌ Failed to save")
                    errors += 1
                
                # Progress updates every 50 recipes
                if i % 50 == 0:
                    success_rate = (processed / i) * 100
                    print(f"\n📈 Progress: {i}/{len(recipes)} ({success_rate:.1f}% success)")
                
            except Exception as e:
                print(f"     ❌ Error: {e}")
                errors += 1
                continue
        
        # Final results
        print(f"\n🎉 ATK 25TH ANNIVERSARY ANALYSIS COMPLETE!")
        print("=" * 60)
        print(f"📊 Results:")
        print(f"   Total recipes: {len(recipes):,}")
        print(f"   Successfully analyzed: {processed:,}")
        print(f"   Errors: {errors}")
        print(f"   Success rate: {(processed/len(recipes)*100):.1f}%")
        
        # Show sample profiles
        if sample_profiles:
            print(f"\n🍽️ Sample Flavor Profiles:")
            for i, profile in enumerate(sample_profiles, 1):
                print(f"  {i}. {profile['title'][:40]}...")
                print(f"     Flavors: {', '.join(profile['primary_flavors'])}")
                print(f"     Cuisine: {profile['cuisine_style']} | Intensity: {profile['intensity']}")
                print(f"     Complexity: {profile['complexity_score']}/10 | Harmony: {profile['harmony_score']:.2f}")
        
        # Update database statistics
        cursor.execute("""
            SELECT COUNT(*) FROM recipe_flavor_profiles rfp
            JOIN recipes r ON rfp.recipe_id = r.id
            WHERE r.source = 'ATK 25th Anniversary'
        """)
        
        total_atk_profiles = cursor.fetchone()[0]
        print(f"\n📊 Database Update:")
        print(f"   ATK recipes with flavor profiles: {total_atk_profiles:,}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error in ATK analysis: {e}")

if __name__ == "__main__":
    analyze_atk_25th_recipes()
