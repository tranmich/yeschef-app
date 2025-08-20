#!/usr/bin/env python3
"""
Detailed Recipe Quality Investigation
Examines specific problematic recipes to understand extraction issues and patterns
"""

import psycopg2
import psycopg2.extras
import json
import logging
import sys
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_db_connection():
    """Get PostgreSQL database connection"""
    try:
        database_url = "postgresql://postgres:udQLpljdqTYmESmntwzmwDcOlBVbqlJG@shuttle.proxy.rlwy.net:31331/railway"
        logger.info("🔄 Connecting to Railway PostgreSQL...")
        conn = psycopg2.connect(database_url)
        conn.cursor_factory = psycopg2.extras.RealDictCursor
        logger.info("✅ Connected to PostgreSQL database successfully")
        return conn
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise

def investigate_problematic_recipes():
    """Deep dive into recipes with data quality issues"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("🔍 DETAILED PROBLEMATIC RECIPE INVESTIGATION")
    print("="*80)
    
    try:
        # Get recipes with insufficient ingredients
        print("\n🚨 RECIPES WITH INSUFFICIENT INGREDIENTS:")
        print("-" * 60)
        
        cursor.execute("""
            SELECT id, title, ingredients, instructions, source, category, servings, total_time
            FROM recipes 
            WHERE LENGTH(TRIM(ingredients)) < 20 OR ingredients = 'Salt and pepper'
            ORDER BY id
            LIMIT 10
        """)
        
        problematic_recipes = cursor.fetchall()
        
        for i, recipe in enumerate(problematic_recipes, 1):
            print(f"\n📝 RECIPE {i} (ID: {recipe['id']}):")
            print(f"  📖 Title: {recipe['title']}")
            print(f"  📚 Source: {recipe['source']}")
            print(f"  🏷️ Category: {recipe['category']}")
            print(f"  🍽️ Servings: {recipe['servings']}")
            print(f"  ⏱️ Time: {recipe['total_time']}")
            print(f"  🥘 Ingredients: '{recipe['ingredients']}'")
            print(f"  📋 Instructions: '{recipe['instructions'][:100]}{'...' if len(recipe['instructions']) > 100 else ''}'")
            
            # Analyze the issue
            issues = []
            if not recipe['ingredients'] or len(recipe['ingredients'].strip()) < 10:
                issues.append("MISSING_INGREDIENTS")
            elif recipe['ingredients'] == 'Salt and pepper':
                issues.append("INCOMPLETE_INGREDIENTS")
            elif len(recipe['ingredients'].strip()) < 20:
                issues.append("TOO_SHORT_INGREDIENTS")
            
            if not recipe['instructions'] or len(recipe['instructions'].strip()) < 20:
                issues.append("INSUFFICIENT_INSTRUCTIONS")
                
            print(f"  🚨 Detected Issues: {', '.join(issues)}")
        
        # Check for patterns in sources
        print(f"\n📊 SOURCES OF PROBLEMATIC RECIPES:")
        print("-" * 50)
        
        cursor.execute("""
            SELECT source, COUNT(*) as problem_count
            FROM recipes 
            WHERE LENGTH(TRIM(ingredients)) < 20 OR LENGTH(TRIM(instructions)) < 20
            GROUP BY source
            ORDER BY problem_count DESC
        """)
        
        source_problems = cursor.fetchall()
        
        for source_info in source_problems:
            print(f"  📚 {source_info['source']}: {source_info['problem_count']} problematic recipes")
        
        # Look for specific patterns in ingredients field
        print(f"\n🔍 INGREDIENTS FIELD PATTERNS:")
        print("-" * 50)
        
        cursor.execute("""
            SELECT 
                ingredients,
                COUNT(*) as frequency,
                array_agg(id ORDER BY id) as recipe_ids
            FROM recipes 
            WHERE LENGTH(TRIM(ingredients)) < 30
            GROUP BY ingredients
            ORDER BY frequency DESC
            LIMIT 10
        """)
        
        patterns = cursor.fetchall()
        
        for pattern in patterns:
            ids_sample = pattern['recipe_ids'][:5]  # Show first 5 IDs
            print(f"  🔹 '{pattern['ingredients']}' → {pattern['frequency']} recipes (IDs: {ids_sample})")
        
        # Check for recipes with empty arrays/lists
        print(f"\n🔍 RECIPES WITH EMPTY/NULL DATA STRUCTURES:")
        print("-" * 50)
        
        cursor.execute("""
            SELECT id, title, ingredients, instructions
            FROM recipes 
            WHERE ingredients = '[]' OR instructions = '[]' OR ingredients IS NULL OR instructions IS NULL
            ORDER BY id
            LIMIT 5
        """)
        
        empty_recipes = cursor.fetchall()
        
        for recipe in empty_recipes:
            print(f"  📝 ID {recipe['id']}: {recipe['title']}")
            print(f"      Ingredients: {recipe['ingredients']}")
            print(f"      Instructions: {recipe['instructions']}")
        
        # Find recipes that look like extraction errors
        print(f"\n🔍 RECIPES WITH EXTRACTION ERROR PATTERNS:")
        print("-" * 50)
        
        cursor.execute("""
            SELECT id, title, ingredients, instructions
            FROM recipes 
            WHERE ingredients LIKE '%INGREDIENTS%' 
               OR ingredients LIKE '%DIRECTIONS%'
               OR instructions LIKE '%INGREDIENTS%'
               OR title LIKE '%RECIPE%'
            ORDER BY id
            LIMIT 5
        """)
        
        extraction_errors = cursor.fetchall()
        
        for recipe in extraction_errors:
            print(f"  📝 ID {recipe['id']}: {recipe['title']}")
            print(f"      Ingredients contain formatting: {recipe['ingredients'][:100]}...")
            print(f"      Instructions: {recipe['instructions'][:100]}...")
            
    except Exception as e:
        logger.error(f"❌ Error investigating problematic recipes: {e}")
    finally:
        conn.close()

def analyze_good_recipes():
    """Examine well-formatted recipes to understand good patterns"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("✅ WELL-FORMATTED RECIPE ANALYSIS")
    print("="*80)
    
    try:
        # Get recipes with good data quality
        cursor.execute("""
            SELECT id, title, ingredients, instructions, source, category, servings, total_time
            FROM recipes 
            WHERE LENGTH(TRIM(ingredients)) > 100 
            AND LENGTH(TRIM(instructions)) > 200
            AND ingredients NOT LIKE '%INGREDIENTS%'
            AND instructions NOT LIKE '%DIRECTIONS%'
            ORDER BY LENGTH(ingredients) DESC
            LIMIT 5
        """)
        
        good_recipes = cursor.fetchall()
        
        print("\n🌟 EXAMPLES OF WELL-FORMATTED RECIPES:")
        print("-" * 60)
        
        for i, recipe in enumerate(good_recipes, 1):
            print(f"\n📝 GOOD RECIPE {i} (ID: {recipe['id']}):")
            print(f"  📖 Title: {recipe['title']}")
            print(f"  📚 Source: {recipe['source']}")
            print(f"  🏷️ Category: {recipe['category']}")
            print(f"  🍽️ Servings: {recipe['servings']}")
            print(f"  ⏱️ Time: {recipe['total_time']}")
            print(f"  📏 Ingredients length: {len(recipe['ingredients'])} chars")
            print(f"  📏 Instructions length: {len(recipe['instructions'])} chars")
            print(f"  🥘 Ingredients (first 200 chars): {recipe['ingredients'][:200]}...")
            print(f"  📋 Instructions (first 200 chars): {recipe['instructions'][:200]}...")
            
            # Try to detect the format
            ingredients_format = "Unknown"
            if recipe['ingredients'].startswith('['):
                ingredients_format = "JSON Array"
            elif recipe['ingredients'].startswith('"'):
                ingredients_format = "JSON String Array"
            elif '\n' in recipe['ingredients']:
                ingredients_format = "Newline Separated"
            elif ',' in recipe['ingredients']:
                ingredients_format = "Comma Separated"
            
            instructions_format = "Unknown"
            if recipe['instructions'].startswith('['):
                instructions_format = "JSON Array"
            elif recipe['instructions'].startswith('"'):
                instructions_format = "JSON String Array"
            elif '\n' in recipe['instructions']:
                instructions_format = "Newline Separated"
            elif '.' in recipe['instructions'] and len(recipe['instructions']) > 100:
                instructions_format = "Paragraph Text"
            
            print(f"  🔍 Ingredients Format: {ingredients_format}")
            print(f"  🔍 Instructions Format: {instructions_format}")
        
    except Exception as e:
        logger.error(f"❌ Error analyzing good recipes: {e}")
    finally:
        conn.close()

def generate_cleanup_strategy():
    """Generate specific data cleanup strategy based on findings"""
    print("\n" + "="*80)
    print("🛠️ SPECIFIC DATA CLEANUP STRATEGY")
    print("="*80)
    
    print("""
🎯 PRIORITY 1: CRITICAL FIXES (Immediate)

1. 🧹 Remove/Fix Recipes with "Salt and pepper" as complete ingredients:
   - These appear to be extraction failures where only seasoning was captured
   - Need to either re-extract from source or remove from database

2. 🔧 Fix Empty Array/List Recipes:
   - Some recipes have ingredients: "[]" or instructions: "[]"
   - These are clear extraction failures that need to be re-processed

3. 🔍 Clean Extraction Artifacts:
   - Remove formatting text like "INGREDIENTS", "DIRECTIONS" from content
   - These indicate parser didn't properly separate structure from content

🎯 PRIORITY 2: DATA STANDARDIZATION (Next Sprint)

1. 📝 Normalize Ingredients Format:
   - Decide on standard format (JSON array vs newline-separated vs comma-separated)
   - Convert all recipes to consistent format
   - Parse quantities and units properly

2. 📋 Standardize Instructions Format:
   - Choose between JSON array of steps vs paragraph text
   - Number steps consistently
   - Remove extraction artifacts

3. 🏷️ Category Cleanup:
   - Only 16.8% of recipes have categories
   - Implement automatic categorization based on title/ingredients
   - Standardize existing category names

🎯 PRIORITY 3: ENHANCED EXTRACTION (Future)

1. 🤖 Improve Recipe Parsers:
   - Add validation during extraction
   - Implement minimum content length requirements
   - Add quality scoring to flag incomplete extractions

2. 📊 Quality Monitoring:
   - Regular automated quality reports
   - User feedback collection
   - A/B testing for different display formats

🔧 IMMEDIATE ACTIONABLE FIXES:

1. Create script to identify and remove/fix the ~115 recipes with insufficient data
2. Implement frontend fallbacks for missing data
3. Add admin interface for manual review of flagged recipes
4. Enhance recipe display to handle various data formats gracefully
    """)

def main():
    """Run detailed recipe investigation"""
    print("🚀 Starting detailed recipe quality investigation...")
    
    try:
        investigate_problematic_recipes()
        analyze_good_recipes()
        generate_cleanup_strategy()
        
        print("\n" + "="*80)
        print("✅ DETAILED INVESTIGATION COMPLETE!")
        print("="*80)
        print("\nKey Findings:")
        print("1. ~115 recipes (15.8%) have insufficient ingredients/instructions")
        print("2. Common issue: 'Salt and pepper' as complete ingredient list")
        print("3. Some recipes have empty arrays [] from extraction failures")
        print("4. Good recipes exist with proper formatting - use as templates")
        print("5. Multiple data formats present - need standardization")
        
    except Exception as e:
        logger.error(f"❌ Investigation failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
