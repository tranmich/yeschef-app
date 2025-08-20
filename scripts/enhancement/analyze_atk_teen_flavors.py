#!/usr/bin/env python3
"""
🍽️ ATK Teens Flavor Analysis Script
Analyze ATK Teen recipes with the flavor profiling system
"""

import os
import sys
import sqlite3
import psycopg2
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Add core systems to path
core_systems_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'core_systems')
sys.path.insert(0, core_systems_path)

try:
    from recipe_flavor_analyzer import RecipeFlavorAnalyzer
    from recipe_intelligence_hub import RecipeIntelligenceHub
except ImportError as e:
    print(f"❌ Import error: {e}")
    print(f"Looking for modules in: {core_systems_path}")
    sys.exit(1)

def analyze_atk_teen_flavors():
    """Analyze all ATK Teen recipes with flavor profiling"""
    print("🍽️ ATK TEEN RECIPES FLAVOR ANALYSIS")
    print("=" * 60)
    
    try:
        # Connect to PostgreSQL
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            database_url = 'postgresql://postgres:udQLpljdqTYmESmntwzmwDcOlBVbqlJG@shuttle.proxy.rlwy.net:31331/railway'
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("✅ Connected to PostgreSQL database")
        
        # Find ATK Teen recipes
        cursor.execute("""
            SELECT id, title, ingredients, instructions, source 
            FROM recipes 
            WHERE source LIKE '%Teen%' 
            ORDER BY id
        """)
        
        teen_recipes = cursor.fetchall()
        
        if not teen_recipes:
            print("❌ No ATK Teen recipes found!")
            return
        
        print(f"📊 Found {len(teen_recipes)} ATK Teen recipes to analyze")
        
        # Initialize flavor analyzer
        analyzer = RecipeFlavorAnalyzer()
        
        analyzed_count = 0
        skipped_count = 0
        
        print(f"\n🔄 Starting flavor analysis...")
        
        for recipe_id, title, ingredients, instructions, source in teen_recipes:
            try:
                # Check if already analyzed
                cursor.execute("""
                    SELECT id FROM recipe_flavor_profiles 
                    WHERE recipe_id = %s
                """, (recipe_id,))
                
                if cursor.fetchone():
                    skipped_count += 1
                    continue
                
                # Analyze flavor profile
                recipe_data = {
                    'title': title,
                    'ingredients': ingredients,
                    'instructions': instructions,
                    'source': source
                }
                
                flavor_profile = analyzer.analyze_recipe(recipe_data)
                
                if flavor_profile:
                    # Convert FlavorProfile object to dictionary format for database
                    if hasattr(flavor_profile, '__dict__'):
                        # It's a FlavorProfile dataclass
                        profile_data = {
                            'flavor_categories': flavor_profile.primary_flavors + flavor_profile.secondary_flavors,
                            'dominant_flavors': flavor_profile.primary_flavors,
                            'cuisine_style': flavor_profile.cuisine_style,
                            'complexity_score': flavor_profile.complexity_score,
                            'harmony_score': flavor_profile.harmony_score,
                            'intensity_level': flavor_profile.intensity,
                            'cooking_methods': flavor_profile.cooking_methods
                        }
                    else:
                        # It's already a dictionary
                        profile_data = flavor_profile
                    # Insert flavor profile using correct column names
                    cursor.execute("""
                        INSERT INTO recipe_flavor_profiles (
                            recipe_id, primary_flavors, secondary_flavors, 
                            intensity, cooking_methods, cuisine_style,
                            complexity_score, harmony_score, created_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    """, (
                        recipe_id,
                        json.dumps(profile_data['dominant_flavors']),
                        json.dumps(profile_data['flavor_categories'][len(profile_data['dominant_flavors']):]),
                        profile_data['intensity_level'],
                        json.dumps(profile_data['cooking_methods']),
                        profile_data['cuisine_style'],
                        profile_data['complexity_score'],
                        profile_data['harmony_score']
                    ))
                    
                    analyzed_count += 1
                    
                    # Progress update
                    if analyzed_count % 10 == 0:
                        print(f"🔍 [{analyzed_count}/{len(teen_recipes)}] {title}")
                        print(f"     ✅ Analyzed - {', '.join(profile_data['dominant_flavors'])} | {profile_data['cuisine_style']} | {profile_data['complexity_score']}/10")
                    
                    # Commit every 10 recipes
                    if analyzed_count % 10 == 0:
                        conn.commit()
                
            except Exception as e:
                print(f"❌ Error analyzing recipe {recipe_id} ({title}): {e}")
                continue
        
        # Final commit
        conn.commit()
        
        print(f"\n🎉 ATK TEEN FLAVOR ANALYSIS COMPLETE!")
        print("=" * 60)
        print(f"📊 Results:")
        print(f"   Total recipes: {len(teen_recipes)}")
        print(f"   Successfully analyzed: {analyzed_count}")
        print(f"   Already had profiles: {skipped_count}")
        print(f"   Success rate: {(analyzed_count/(len(teen_recipes)-skipped_count)*100):.1f}%")
        
        # Show sample results
        if analyzed_count > 0:
            cursor.execute("""
                SELECT r.title, rfp.primary_flavors, rfp.cuisine_style, 
                       rfp.complexity_score, rfp.harmony_score
                FROM recipes r
                JOIN recipe_flavor_profiles rfp ON r.id = rfp.recipe_id
                WHERE r.source LIKE '%Teen%'
                ORDER BY rfp.created_at DESC
                LIMIT 5
            """)
            
            samples = cursor.fetchall()
            print(f"\n🍽️ Sample Teen Recipe Flavor Profiles:")
            for i, (title, flavors_json, cuisine, complexity, harmony) in enumerate(samples, 1):
                flavors = json.loads(flavors_json)
                print(f"  {i}. {title}")
                print(f"     Flavors: {', '.join(flavors)}")
                print(f"     Cuisine: {cuisine} | Complexity: {complexity}/10 | Harmony: {harmony:.2f}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error in ATK Teen analysis: {e}")

if __name__ == "__main__":
    analyze_atk_teen_flavors()
