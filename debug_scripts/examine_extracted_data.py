#!/usr/bin/env python3
"""
🔍 EXTRACTION FAILURE ANALYSIS
Examine what the extractors actually captured to understand the problems
"""

import psycopg2

def examine_extraction_failures():
    """Examine actual extracted data to understand what went wrong"""
    print("🔍 EXTRACTION FAILURE ANALYSIS")
    print("=" * 60)
    
    try:
        database_url = 'postgresql://postgres:udQLpljdqTYmESmntwzmwDcOlBVbqlJG@shuttle.proxy.rlwy.net:31331/railway'
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("📊 CURRENT DATABASE CONTENTS:")
        cursor.execute("SELECT COUNT(*) FROM recipes")
        total = cursor.fetchone()[0]
        print(f"  Total recipes: {total:,}")
        
        cursor.execute("SELECT source, COUNT(*) FROM recipes GROUP BY source ORDER BY source")
        sources = cursor.fetchall()
        for source, count in sources:
            print(f"  {source}: {count:,} recipes")
        
        print("\n🔍 SAMPLE ATK 25TH ANNIVERSARY EXTRACTIONS:")
        print("-" * 50)
        
        cursor.execute("""
            SELECT id, title, LEFT(ingredients, 150) as ingredients_sample, 
                   LEFT(instructions, 150) as instructions_sample
            FROM recipes 
            WHERE source = 'America''s Test Kitchen 25th Anniversary'
            ORDER BY id 
            LIMIT 5
        """)
        
        results = cursor.fetchall()
        for recipe_id, title, ingredients, instructions in results:
            print(f"ID {recipe_id}: \"{title}\"")
            print(f"  Ingredients: {ingredients}...")
            print(f"  Instructions: {instructions}...")
            print()
        
        print("\n🔍 SAMPLE ATK TEEN EXTRACTIONS:")
        print("-" * 50)
        
        cursor.execute("""
            SELECT id, title, LEFT(ingredients, 150) as ingredients_sample, 
                   LEFT(instructions, 150) as instructions_sample
            FROM recipes 
            WHERE source LIKE '%Teen%'
            ORDER BY id 
            LIMIT 5
        """)
        
        results = cursor.fetchall()
        for recipe_id, title, ingredients, instructions in results:
            print(f"ID {recipe_id}: \"{title}\"")
            print(f"  Ingredients: {ingredients}...")
            print(f"  Instructions: {instructions}...")
            print()
        
        print("\n🚨 ANALYZING EXTRACTION ARTIFACTS:")
        print("-" * 50)
        
        # Look at the "Before You Begin" entries specifically
        cursor.execute("""
            SELECT id, title, source, LEFT(ingredients, 200) as ingredients_sample
            FROM recipes 
            WHERE title = 'Before You Begin' OR title LIKE '%Before You Begin%'
            ORDER BY id
        """)
        
        artifacts = cursor.fetchall()
        if artifacts:
            print(f"Found {len(artifacts)} 'Before You Begin' artifacts:")
            for recipe_id, title, source, ingredients in artifacts:
                print(f"  ID {recipe_id}: \"{title}\" from {source}")
                print(f"    Ingredients: {ingredients}...")
                print()
        
        # Look at "Start Cooking!" entries
        cursor.execute("""
            SELECT id, title, source, LEFT(ingredients, 200) as ingredients_sample
            FROM recipes 
            WHERE title = 'Start Cooking!' OR title LIKE '%Start Cooking%'
            ORDER BY id
            LIMIT 5
        """)
        
        start_cooking = cursor.fetchall()
        if start_cooking:
            print(f"Found 'Start Cooking!' artifacts (showing first 5):")
            for recipe_id, title, source, ingredients in start_cooking:
                print(f"  ID {recipe_id}: \"{title}\" from {source}")
                print(f"    Ingredients: {ingredients}...")
                print()
        
        # Look at page reference artifacts
        cursor.execute("""
            SELECT id, title, source
            FROM recipes 
            WHERE title LIKE 'ATK Recipe from Page%'
            ORDER BY id
            LIMIT 5
        """)
        
        page_refs = cursor.fetchall()
        if page_refs:
            print(f"Found 'ATK Recipe from Page' artifacts (showing first 5):")
            for recipe_id, title, source in page_refs:
                print(f"  ID {recipe_id}: \"{title}\" from {source}")
        
        print("\n💡 ANALYSIS SUMMARY:")
        print("-" * 50)
        
        # Calculate artifact percentage
        cursor.execute("""
            SELECT COUNT(*) FROM recipes 
            WHERE title IN ('Start Cooking!', 'Before You Begin') 
               OR title LIKE 'ATK Recipe from Page%'
               OR title LIKE '%ajar (see photo%'
        """)
        artifact_count = cursor.fetchone()[0]
        artifact_percentage = (artifact_count / total * 100) if total > 0 else 0
        
        print(f"🚨 Artifact contamination: {artifact_count:,} out of {total:,} recipes ({artifact_percentage:.1f}%)")
        print(f"📊 Clean recipes: {total - artifact_count:,} ({100 - artifact_percentage:.1f}%)")
        
        conn.close()
        
        print("\n🔧 EXTRACTOR ANALYSIS FINDINGS:")
        print("-" * 50)
        print("1. ❌ TITLE EXTRACTION FAILURE:")
        print("   - Extractors captured PDF page headers as recipe titles")
        print("   - 'Start Cooking!' and 'Before You Begin' are instruction headers, not recipe names")
        print("   - 'ATK Recipe from Page X' are page references, not recipes")
        
        print("\n2. ❌ PAGE BOUNDARY DETECTION FAILURE:")
        print("   - Extractors didn't distinguish between recipe content and instruction headers")
        print("   - Multi-page recipes were fragmented into separate 'recipes'")
        print("   - Text extraction artifacts were treated as legitimate recipe data")
        
        print("\n3. ❌ CONTENT VALIDATION FAILURE:")
        print("   - No semantic understanding of what constitutes a recipe")
        print("   - Quantity validation was too lenient")
        print("   - No verification that 'titles' actually describe food")
        
        print("\n4. ❌ STRUCTURAL PATTERN RECOGNITION FAILURE:")
        print("   - Extractors relied on keywords without understanding context")
        print("   - No distinction between recipe sections and instructional text")
        print("   - Poor handling of cookbook formatting patterns")
        
    except Exception as e:
        print(f"❌ Error analyzing extraction data: {e}")

if __name__ == "__main__":
    examine_extraction_failures()
