#!/usr/bin/env python3
"""
🔍 Recipe Title Analysis - Finding Extraction Artifacts
=======================================================
Analyze recipe titles to identify extraction artifacts and non-recipe entries
"""

import psycopg2
import json
from collections import Counter

def analyze_recipe_titles():
    """Analyze recipe titles to find potential extraction artifacts"""
    print("🔍 RECIPE TITLE ANALYSIS - FINDING EXTRACTION ARTIFACTS")
    print("=" * 70)
    
    try:
        database_url = 'postgresql://postgres:udQLpljdqTYmESmntwzmwDcOlBVbqlJG@shuttle.proxy.rlwy.net:31331/railway'
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Find problematic titles
        print("🚨 POTENTIAL EXTRACTION ARTIFACTS")
        print("-" * 50)
        
        problematic_patterns = [
            "Before You Begin",
            "Start Cooking!",
            "PREPARE INGREDIENTS", 
            "To Finish",
            "Topping",
            "Filling",
            "Sauce",
            "Dressing"
        ]
        
        all_artifacts = []
        
        for pattern in problematic_patterns:
            cursor.execute("""
                SELECT id, title, source 
                FROM recipes 
                WHERE LOWER(title) LIKE %s
                ORDER BY id
            """, (f'%{pattern.lower()}%',))
            
            matches = cursor.fetchall()
            
            if matches:
                print(f"\n📋 '{pattern}' entries ({len(matches)} found):")
                for recipe_id, title, source in matches[:10]:  # Show first 10
                    source_short = source[:40] + "..." if len(source) > 40 else source
                    print(f"  ID {recipe_id}: {title} ({source_short})")
                
                if len(matches) > 10:
                    print(f"  ... and {len(matches) - 10} more")
                
                all_artifacts.extend(matches)
        
        # Find very short titles (likely artifacts)
        print(f"\n🔤 VERY SHORT TITLES (likely artifacts)")
        print("-" * 50)
        
        cursor.execute("""
            SELECT id, title, source 
            FROM recipes 
            WHERE LENGTH(title) <= 10
            AND title != ''
            ORDER BY LENGTH(title), title
        """)
        
        short_titles = cursor.fetchall()
        
        if short_titles:
            print(f"Found {len(short_titles)} recipes with titles ≤10 characters:")
            for recipe_id, title, source in short_titles[:15]:
                source_short = source[:30] + "..." if len(source) > 30 else source
                print(f"  ID {recipe_id}: '{title}' ({len(title)} chars) - {source_short}")
            
            if len(short_titles) > 15:
                print(f"  ... and {len(short_titles) - 15} more")
        
        # Find titles that are just numbers or weird characters
        print(f"\n🔢 NUMERIC/WEIRD TITLES")
        print("-" * 50)
        
        cursor.execute("""
            SELECT id, title, source 
            FROM recipes 
            WHERE title ~ '^[0-9\s\.\-\(\)]+$'
            OR title LIKE '%ajar (see photo%'
            OR title LIKE '%unti l skins ar e%'
            OR title LIKE '%wi thout stirring%'
            ORDER BY id
        """)
        
        weird_titles = cursor.fetchall()
        
        if weird_titles:
            print(f"Found {len(weird_titles)} recipes with numeric/weird titles:")
            for recipe_id, title, source in weird_titles:
                source_short = source[:30] + "..." if len(source) > 30 else source
                print(f"  ID {recipe_id}: '{title}' - {source_short}")
        
        # Title frequency analysis
        print(f"\n📊 TITLE FREQUENCY ANALYSIS")
        print("-" * 50)
        
        cursor.execute("""
            SELECT title, COUNT(*) as count
            FROM recipes 
            GROUP BY title
            HAVING COUNT(*) > 1
            ORDER BY count DESC, title
            LIMIT 20
        """)
        
        duplicate_titles = cursor.fetchall()
        
        if duplicate_titles:
            print("Most frequent duplicate titles:")
            for title, count in duplicate_titles:
                print(f"  '{title}': {count} times")
        
        # Source analysis for ATK books
        print(f"\n📚 ATK COOKBOOK ANALYSIS")
        print("-" * 50)
        
        # ATK Teen artifacts
        cursor.execute("""
            SELECT COUNT(*) 
            FROM recipes 
            WHERE source LIKE '%Teen%' 
            AND (title LIKE '%Start Cooking%' 
                 OR title LIKE '%Before You Begin%'
                 OR title = 'PREPARE INGREDIENTS'
                 OR title LIKE '%To Finish%')
        """)
        
        teen_artifacts = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM recipes WHERE source LIKE '%Teen%'")
        teen_total = cursor.fetchone()[0]
        
        print(f"ATK Teen Cookbook:")
        print(f"  Total entries: {teen_total}")
        print(f"  Likely artifacts: {teen_artifacts}")
        print(f"  Actual recipes: {teen_total - teen_artifacts}")
        print(f"  Artifact rate: {(teen_artifacts/teen_total*100):.1f}%")
        
        # ATK 25th artifacts
        cursor.execute("""
            SELECT COUNT(*) 
            FROM recipes 
            WHERE source = 'America''s Test Kitchen 25th Anniversary'
            AND (title LIKE '%Start Cooking%' 
                 OR title LIKE '%Before You Begin%'
                 OR title = 'PREPARE INGREDIENTS'
                 OR title LIKE '%ATK Recipe from Page%'
                 OR LENGTH(title) <= 5)
        """)
        
        atk25_artifacts = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM recipes WHERE source = 'America''s Test Kitchen 25th Anniversary'")
        atk25_total = cursor.fetchone()[0]
        
        print(f"\nATK 25th Anniversary Cookbook:")
        print(f"  Total entries: {atk25_total}")
        print(f"  Likely artifacts: {atk25_artifacts}")
        print(f"  Actual recipes: {atk25_total - atk25_artifacts}")
        print(f"  Artifact rate: {(atk25_artifacts/atk25_total*100):.1f}%")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS")
        print("-" * 50)
        
        total_artifacts = teen_artifacts + atk25_artifacts
        
        if total_artifacts > 50:
            print(f"🚨 High artifact count detected: {total_artifacts} entries")
            print("  Recommended actions:")
            print("  1. Create cleanup script to remove/flag artifacts")
            print("  2. Update extraction logic to skip instruction headers")
            print("  3. Implement better recipe title validation")
            print("  4. Consider re-extracting with improved filters")
        elif total_artifacts > 20:
            print(f"⚠️  Moderate artifact count: {total_artifacts} entries")
            print("  Consider cleanup for better data quality")
        else:
            print(f"✅ Low artifact count: {total_artifacts} entries")
            print("  Data quality is acceptable")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error analyzing titles: {e}")

if __name__ == "__main__":
    analyze_recipe_titles()
