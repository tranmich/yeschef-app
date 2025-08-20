#!/usr/bin/env python3
"""
Database Structure and Data Quality Analysis Script
Analyzes Railway PostgreSQL database to identify columns, data quality issues, and recipe display problems
"""

import psycopg2
import psycopg2.extras
import json
import logging
from collections import Counter
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_db_connection():
    """Get PostgreSQL database connection"""
    try:
        # Railway public URL
        database_url = "postgresql://postgres:udQLpljdqTYmESmntwzmwDcOlBVbqlJG@shuttle.proxy.rlwy.net:31331/railway"

        logger.info("🔄 Connecting to Railway PostgreSQL...")
        conn = psycopg2.connect(database_url)
        conn.cursor_factory = psycopg2.extras.RealDictCursor
        logger.info("✅ Connected to PostgreSQL database successfully")
        return conn
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise

def analyze_table_structure():
    """Analyze the structure of all tables in the database"""
    conn = get_db_connection()
    cursor = conn.cursor()

    print("\n" + "="*80)
    print("🗄️  DATABASE STRUCTURE ANALYSIS")
    print("="*80)

    try:
        # Get all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()

        print(f"\n📋 Tables found: {len(tables)}")
        for table in tables:
            print(f"  • {table['table_name']}")

        # Analyze each table structure
        for table in tables:
            table_name = table['table_name']
            print(f"\n📊 TABLE: {table_name}")
            print("-" * 60)

            # Get column information
            cursor.execute("""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    character_maximum_length
                FROM information_schema.columns 
                WHERE table_name = %s
                ORDER BY ordinal_position;
            """, (table_name,))

            columns = cursor.fetchall()

            for col in columns:
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                max_len = f"({col['character_maximum_length']})" if col['character_maximum_length'] else ""
                default = f" DEFAULT: {col['column_default']}" if col['column_default'] else ""

                print(f"  📝 {col['column_name']:<20} {col['data_type']}{max_len:<10} {nullable:<8} {default}")

            # Get row count
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            count = cursor.fetchone()['count']
            print(f"  📊 Total rows: {count:,}")

    except Exception as e:
        logger.error(f"❌ Error analyzing table structure: {e}")
    finally:
        conn.close()

def analyze_recipe_data_quality():
    """Analyze data quality issues in the recipes table"""
    conn = get_db_connection()
    cursor = conn.cursor()

    print("\n" + "="*80)
    print("🔍 RECIPE DATA QUALITY ANALYSIS")
    print("="*80)

    try:
        # Basic statistics
        cursor.execute("SELECT COUNT(*) as total FROM recipes")
        total_recipes = cursor.fetchone()['total']
        print(f"\n📊 Total recipes: {total_recipes:,}")

        # Check for empty/null critical fields
        critical_fields = ['title', 'ingredients', 'instructions']

        for field in critical_fields:
            print(f"\n🔍 ANALYZING FIELD: {field}")
            print("-" * 40)

            # Count null/empty values
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN {field} IS NULL THEN 1 END) as null_count,
                    COUNT(CASE WHEN {field} = '' THEN 1 END) as empty_count,
                    COUNT(CASE WHEN LENGTH(TRIM({field})) = 0 THEN 1 END) as whitespace_count,
                    COUNT(CASE WHEN LENGTH({field}) < 10 THEN 1 END) as too_short_count
                FROM recipes
            """)

            stats = cursor.fetchone()

            null_pct = (stats['null_count'] / total_recipes) * 100
            empty_pct = (stats['empty_count'] / total_recipes) * 100
            whitespace_pct = (stats['whitespace_count'] / total_recipes) * 100
            short_pct = (stats['too_short_count'] / total_recipes) * 100

            print(f"  • NULL values: {stats['null_count']:,} ({null_pct:.1f}%)")
            print(f"  • Empty strings: {stats['empty_count']:,} ({empty_pct:.1f}%)")
            print(f"  • Whitespace only: {stats['whitespace_count']:,} ({whitespace_pct:.1f}%)")
            print(f"  • Too short (<10 chars): {stats['too_short_count']:,} ({short_pct:.1f}%)")

            # Show examples of problematic entries
            if stats['null_count'] > 0 or stats['empty_count'] > 0 or stats['whitespace_count'] > 0:
                print(f"  \n🚨 PROBLEMATIC EXAMPLES:")
                cursor.execute(f"""
                    SELECT id, title, LEFT({field}, 50) as sample
                    FROM recipes 
                    WHERE {field} IS NULL OR {field} = '' OR LENGTH(TRIM({field})) = 0
                    LIMIT 5
                """)

                problems = cursor.fetchall()
                for problem in problems:
                    sample = problem['sample'] if problem['sample'] else '[NULL/EMPTY]'
                    print(f"    ID {problem['id']}: {problem['title'][:30]:<30} | {field}: {sample}")

        # Analyze optional fields
        optional_fields = ['description', 'category', 'servings', 'total_time', 'source', 'url']

        print(f"\n📈 OPTIONAL FIELDS COMPLETION RATES")
        print("-" * 50)

        for field in optional_fields:
            cursor.execute(f"""
                SELECT 
                    COUNT(CASE WHEN {field} IS NOT NULL AND {field} != '' AND LENGTH(TRIM({field})) > 0 THEN 1 END) as filled
                FROM recipes
            """)

            filled = cursor.fetchone()['filled']
            completion_rate = (filled / total_recipes) * 100
            print(f"  • {field:<15}: {filled:>6,} / {total_recipes:,} ({completion_rate:5.1f}%)")

        # Find recipes with the most data quality issues
        print(f"\n🚨 RECIPES WITH MULTIPLE DATA ISSUES")
        print("-" * 50)

        cursor.execute("""
            SELECT 
                id,
                title,
                CASE WHEN ingredients IS NULL OR ingredients = '' OR LENGTH(TRIM(ingredients)) = 0 THEN 1 ELSE 0 END +
                CASE WHEN instructions IS NULL OR instructions = '' OR LENGTH(TRIM(instructions)) = 0 THEN 1 ELSE 0 END +
                CASE WHEN title IS NULL OR title = '' OR LENGTH(TRIM(title)) = 0 THEN 1 ELSE 0 END as issue_count,
                CASE WHEN ingredients IS NULL OR ingredients = '' THEN 'NO_INGREDIENTS ' ELSE '' END ||
                CASE WHEN instructions IS NULL OR instructions = '' THEN 'NO_INSTRUCTIONS ' ELSE '' END ||
                CASE WHEN title IS NULL OR title = '' THEN 'NO_TITLE' ELSE '' END as issues
            FROM recipes
            WHERE 
                (ingredients IS NULL OR ingredients = '' OR LENGTH(TRIM(ingredients)) = 0) OR
                (instructions IS NULL OR instructions = '' OR LENGTH(TRIM(instructions)) = 0) OR
                (title IS NULL OR title = '' OR LENGTH(TRIM(title)) = 0)
            ORDER BY issue_count DESC, id
            LIMIT 10
        """)

        problematic_recipes = cursor.fetchall()

        if problematic_recipes:
            for recipe in problematic_recipes:
                print(f"  ID {recipe['id']:>4}: {recipe['title'][:40]:<40} | Issues: {recipe['issues']}")
        else:
            print("  ✅ No critical data quality issues found!")

    except Exception as e:
        logger.error(f"❌ Error analyzing recipe data quality: {e}")
    finally:
        conn.close()

def sample_recipe_display():
    """Sample how recipes are currently displayed"""
    conn = get_db_connection()
    cursor = conn.cursor()

    print("\n" + "="*80)
    print("👁️  RECIPE DISPLAY SAMPLING")
    print("="*80)

    try:
        # Get a few sample recipes with different data quality levels
        print("\n🔍 SAMPLING RECIPE DISPLAY QUALITY...")

        # Get recipes with complete data
        cursor.execute("""
            SELECT id, title, ingredients, instructions, servings, total_time, category
            FROM recipes 
            WHERE ingredients IS NOT NULL AND ingredients != '' 
            AND instructions IS NOT NULL AND instructions != ''
            AND LENGTH(TRIM(ingredients)) > 50
            AND LENGTH(TRIM(instructions)) > 50
            ORDER BY id
            LIMIT 3
        """)

        good_recipes = cursor.fetchall()

        print("\n✅ RECIPES WITH GOOD DATA QUALITY:")
        print("-" * 60)

        for i, recipe in enumerate(good_recipes, 1):
            print(f"\n📝 RECIPE {i} (ID: {recipe['id']}):")
            print(f"  Title: {recipe['title']}")
            print(f"  Category: {recipe['category'] or 'Not specified'}")
            print(f"  Servings: {recipe['servings'] or 'Not specified'}")
            print(f"  Time: {recipe['total_time'] or 'Not specified'}")
            print(f"  Ingredients: {recipe['ingredients'][:100]}{'...' if len(recipe['ingredients']) > 100 else ''}")
            print(f"  Instructions: {recipe['instructions'][:100]}{'...' if len(recipe['instructions']) > 100 else ''}")

        # Get recipes with poor data quality
        cursor.execute("""
            SELECT id, title, ingredients, instructions, servings, total_time, category
            FROM recipes 
            WHERE (ingredients IS NULL OR ingredients = '' OR LENGTH(TRIM(ingredients)) < 20)
            OR (instructions IS NULL OR instructions = '' OR LENGTH(TRIM(instructions)) < 20)
            ORDER BY id
            LIMIT 5
        """)

        poor_recipes = cursor.fetchall()

        if poor_recipes:
            print("\n🚨 RECIPES WITH DATA QUALITY ISSUES:")
            print("-" * 60)

            for i, recipe in enumerate(poor_recipes, 1):
                print(f"\n📝 PROBLEMATIC RECIPE {i} (ID: {recipe['id']}):")
                print(f"  Title: {recipe['title']}")
                print(f"  Category: {recipe['category'] or 'Not specified'}")
                print(f"  Servings: {recipe['servings'] or 'Not specified'}")
                print(f"  Time: {recipe['total_time'] or 'Not specified'}")

                ingredients = recipe['ingredients'] or '[MISSING]'
                instructions = recipe['instructions'] or '[MISSING]'

                print(f"  Ingredients: {ingredients[:100]}{'...' if len(ingredients) > 100 else ''}")
                print(f"  Instructions: {instructions[:100]}{'...' if len(instructions) > 100 else ''}")

                # Identify specific issues
                issues = []
                if not recipe['ingredients'] or len(recipe['ingredients'].strip()) < 20:
                    issues.append("INSUFFICIENT_INGREDIENTS")
                if not recipe['instructions'] or len(recipe['instructions'].strip()) < 20:
                    issues.append("INSUFFICIENT_INSTRUCTIONS")

                print(f"  🚨 Issues: {', '.join(issues)}")

    except Exception as e:
        logger.error(f"❌ Error sampling recipe display: {e}")
    finally:
        conn.close()

def generate_data_cleaning_recommendations():
    """Generate recommendations for data cleaning"""
    print("\n" + "="*80)
    print("💡 DATA CLEANING RECOMMENDATIONS")
    print("="*80)

    print("""
🎯 IMMEDIATE ACTIONS NEEDED:

1. 🧹 CRITICAL DATA CLEANING:
   • Remove/fix recipes with missing ingredients
   • Remove/fix recipes with missing instructions  
   • Standardize empty fields to NULL instead of empty strings
   • Set minimum content length requirements (ingredients: 20+ chars, instructions: 50+ chars)

2. 📝 DATA STANDARDIZATION:
   • Normalize servings field (some have "4", others "serves 4", etc.)
   • Standardize time formats (some use "30 min", others "30 minutes", etc.)
   • Clean up category names (standardize capitalization, remove duplicates)

3. 🔍 RECIPE EXTRACTION IMPROVEMENTS:
   • Enhance parsers to better extract ingredients lists
   • Improve instruction parsing to capture complete steps
   • Add validation during import to catch incomplete recipes
   • Implement quality scoring to flag problematic recipes

4. 🛠️ DISPLAY IMPROVEMENTS:
   • Add fallback text for missing fields
   • Implement better error handling in frontend
   • Add visual indicators for incomplete recipes
   • Create admin interface for manual recipe review

5. 📊 ONGOING MONITORING:
   • Regular data quality reports
   • User feedback collection on recipe quality
   • Automated alerts for recipes with low completion rates
   • A/B testing for different display formats
   """)

def main():
    """Run complete database analysis"""
    print("🚀 Starting comprehensive database analysis...")
    print(f"📅 Analysis date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # Run all analyses
        analyze_table_structure()
        analyze_recipe_data_quality()
        sample_recipe_display()
        generate_data_cleaning_recommendations()

        print("\n" + "="*80)
        print("✅ DATABASE ANALYSIS COMPLETE!")
        print("="*80)
        print("\nNext steps:")
        print("1. Review the data quality issues identified above")
        print("2. Run specific data cleaning scripts for critical issues")
        print("3. Implement improved recipe parsing and validation")
        print("4. Enhance frontend display for better error handling")

    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        return False

    return True

if __name__ == "__main__":
    main()
