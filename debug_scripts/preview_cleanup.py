#!/usr/bin/env python3
"""
🔍 Recipe Cleanup Preview - Safe Analysis
=========================================
Identify artifacts without making any changes
"""

import psycopg2
import json
from collections import defaultdict

def preview_cleanup_detailed():
    """Detailed preview of what would be cleaned up"""
    print("🔍 DETAILED CLEANUP PREVIEW")
    print("=" * 60)
    print("🛡️  SAFE MODE - No changes will be made")
    print()
    
    try:
        database_url = 'postgresql://postgres:udQLpljdqTYmESmntwzmwDcOlBVbqlJG@shuttle.proxy.rlwy.net:31331/railway'
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Categories of artifacts to identify
        artifact_categories = {
            'instruction_headers': [
                "Start Cooking!",
                "Before You Begin", 
                "PREPARE INGREDIENTS",
                "To Finish"
            ],
            'single_word_artifacts': [
                "Dressing",
                "Topping",
                "Filling", 
                "Sauce"  # Only single word, not part of recipe names
            ],
            'very_short_titles': [],  # Will be populated by query
            'garbled_text': [
                "ajar (see photo",
                "unti l skins ar e",
                "wi thout stirring"
            ],
            'page_references': [
                "ATK Recipe from Page"
            ]
        }
        
        artifacts_found = defaultdict(list)
        
        # Find instruction header artifacts
        for header in artifact_categories['instruction_headers']:
            cursor.execute("""
                SELECT id, title, source 
                FROM recipes 
                WHERE title = %s
                ORDER BY id
            """, (header,))
            
            matches = cursor.fetchall()
            artifacts_found['instruction_headers'].extend(matches)
        
        # Find single-word artifacts (but be careful about legitimate single-word recipes)
        for word in artifact_categories['single_word_artifacts']:
            cursor.execute("""
                SELECT id, title, source 
                FROM recipes 
                WHERE title = %s
                ORDER BY id
            """, (word,))
            
            matches = cursor.fetchall()
            artifacts_found['single_word_artifacts'].extend(matches)
        
        # Find very short titles (likely artifacts)
        cursor.execute("""
            SELECT id, title, source 
            FROM recipes 
            WHERE LENGTH(title) <= 3
            OR (LENGTH(title) <= 10 AND title ~ '^[A-Z]+$')
            ORDER BY LENGTH(title), title
        """)
        
        short_titles = cursor.fetchall()
        artifacts_found['very_short_titles'] = short_titles
        
        # Find garbled text
        for pattern in artifact_categories['garbled_text']:
            cursor.execute("""
                SELECT id, title, source 
                FROM recipes 
                WHERE title LIKE %s
                ORDER BY id
            """, (f'%{pattern}%',))
            
            matches = cursor.fetchall()
            artifacts_found['garbled_text'].extend(matches)
        
        # Find page reference artifacts
        cursor.execute("""
            SELECT id, title, source 
            FROM recipes 
            WHERE title LIKE 'ATK Recipe from Page%'
            ORDER BY id
        """)
        
        page_refs = cursor.fetchall()
        artifacts_found['page_references'] = page_refs
        
        # Display findings
        total_artifacts = 0
        
        for category, items in artifacts_found.items():
            if items:
                print(f"📋 {category.upper().replace('_', ' ')} ({len(items)} found)")
                print("-" * 50)
                
                # Group by source for better analysis
                by_source = defaultdict(list)
                for recipe_id, title, source in items:
                    by_source[source].append((recipe_id, title))
                
                for source, recipes in by_source.items():
                    source_short = source[:50] + "..." if len(source) > 50 else source
                    print(f"  📚 {source_short} ({len(recipes)} entries):")
                    
                    for recipe_id, title in recipes[:5]:  # Show first 5
                        print(f"    ID {recipe_id}: '{title}'")
                    
                    if len(recipes) > 5:
                        print(f"    ... and {len(recipes) - 5} more")
                    print()
                
                total_artifacts += len(items)
        
        # Cookbook quality analysis
        print(f"📊 COOKBOOK QUALITY ANALYSIS")
        print("-" * 50)
        
        # ATK Teen analysis
        cursor.execute("SELECT COUNT(*) FROM recipes WHERE source LIKE '%Teen%'")
        teen_total = cursor.fetchone()[0]
        
        teen_artifacts = len([item for item in artifacts_found['instruction_headers'] 
                            if any('Teen' in item[2] for item in [item])])
        teen_artifacts += len([item for item in artifacts_found['single_word_artifacts'] 
                             if any('Teen' in item[2] for item in [item])])
        teen_artifacts += len([item for item in artifacts_found['garbled_text'] 
                             if any('Teen' in item[2] for item in [item])])
        
        print(f"🍽️  ATK Teen Cookbook:")
        print(f"   Total entries: {teen_total}")
        print(f"   Identified artifacts: {teen_artifacts}")
        print(f"   Clean recipes: {teen_total - teen_artifacts}")
        print(f"   Quality score: {((teen_total - teen_artifacts) / teen_total * 100):.1f}%")
        
        # ATK 25th analysis
        cursor.execute("SELECT COUNT(*) FROM recipes WHERE source = 'America''s Test Kitchen 25th Anniversary'")
        atk25_total = cursor.fetchone()[0]
        
        atk25_artifacts = len([item for item in artifacts_found['page_references']]) 
        atk25_artifacts += len([item for item in artifacts_found['very_short_titles'] 
                              if any('25th' in item[2] for item in [item])])
        
        print(f"\n📘 ATK 25th Anniversary:")
        print(f"   Total entries: {atk25_total}")
        print(f"   Identified artifacts: {atk25_artifacts}")
        print(f"   Clean recipes: {atk25_total - atk25_artifacts}")
        print(f"   Quality score: {((atk25_total - atk25_artifacts) / atk25_total * 100):.1f}%")
        
        # Impact analysis
        print(f"\n💫 CLEANUP IMPACT ANALYSIS")
        print("-" * 50)
        
        cursor.execute("SELECT COUNT(*) FROM recipes")
        total_recipes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM recipe_flavor_profiles")
        total_flavor_profiles = cursor.fetchone()[0]
        
        # Calculate how many flavor profiles would be affected
        all_artifact_ids = set()
        for category_items in artifacts_found.values():
            for recipe_id, _, _ in category_items:
                all_artifact_ids.add(recipe_id)
        
        if all_artifact_ids:
            cursor.execute(f"""
                SELECT COUNT(*) FROM recipe_flavor_profiles 
                WHERE recipe_id IN ({','.join(map(str, all_artifact_ids))})
            """)
            affected_profiles = cursor.fetchone()[0]
        else:
            affected_profiles = 0
        
        print(f"📊 Current database:")
        print(f"   Total recipes: {total_recipes:,}")
        print(f"   Total flavor profiles: {total_flavor_profiles:,}")
        print()
        print(f"🧹 After cleanup would have:")
        print(f"   Recipes: {total_recipes - total_artifacts:,} (-{total_artifacts})")
        print(f"   Flavor profiles: {total_flavor_profiles - affected_profiles:,} (-{affected_profiles})")
        print(f"   Quality improvement: {(total_artifacts / total_recipes * 100):.1f}%")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS")
        print("-" * 50)
        
        if total_artifacts > 100:
            print("🚨 HIGH artifact contamination detected!")
            print("   Immediate cleanup recommended")
            print("   Consider re-extraction with improved filters")
        elif total_artifacts > 50:
            print("⚠️  MODERATE artifact contamination")
            print("   Cleanup recommended for better data quality")
        else:
            print("✅ LOW artifact contamination")
            print("   Optional cleanup for perfectionist data quality")
        
        print(f"\n🛡️  Next steps:")
        print(f"   1. Review this analysis carefully")
        print(f"   2. Run the full cleanup script if satisfied")
        print(f"   3. Backup will be created automatically before cleanup")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")

if __name__ == "__main__":
    preview_cleanup_detailed()
