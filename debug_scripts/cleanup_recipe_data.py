#!/usr/bin/env python3
"""
Recipe Data Cleanup Script
Fixes critical data quality issues identified in the database analysis
"""

import psycopg2
import psycopg2.extras
import json
import logging
import sys
import os
from datetime import datetime

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

def backup_problematic_recipes():
    """Create backup of recipes before cleaning"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("💾 CREATING BACKUP OF PROBLEMATIC RECIPES")
    print("="*80)
    
    try:
        # Create backup table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recipes_backup_cleanup AS 
            SELECT * FROM recipes 
            WHERE LENGTH(TRIM(ingredients)) < 20 
            OR LENGTH(TRIM(instructions)) < 20
            OR ingredients = '[]' 
            OR instructions = '[]'
        """)
        
        # Get count of backed up recipes
        cursor.execute("SELECT COUNT(*) as count FROM recipes_backup_cleanup")
        backup_count = cursor.fetchone()['count']
        
        print(f"✅ Backed up {backup_count} problematic recipes to 'recipes_backup_cleanup' table")
        
        conn.commit()
        
    except Exception as e:
        logger.error(f"❌ Error creating backup: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def fix_empty_array_recipes():
    """Fix recipes with empty arrays '[]' """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("🔧 FIXING RECIPES WITH EMPTY ARRAYS")
    print("="*80)
    
    try:
        # Find recipes with empty arrays
        cursor.execute("""
            SELECT id, title, source
            FROM recipes 
            WHERE ingredients = '[]' OR instructions = '[]'
        """)
        
        empty_recipes = cursor.fetchall()
        print(f"Found {len(empty_recipes)} recipes with empty arrays")
        
        # Option 1: Remove completely empty recipes (both ingredients and instructions empty)
        cursor.execute("""
            DELETE FROM recipes 
            WHERE ingredients = '[]' AND instructions = '[]'
        """)
        
        deleted_count = cursor.rowcount
        print(f"🗑️ Deleted {deleted_count} recipes with both empty ingredients and instructions")
        
        # Option 2: Mark remaining recipes with partial data for manual review
        cursor.execute("""
            UPDATE recipes 
            SET description = COALESCE(description, '') || ' [NEEDS_MANUAL_REVIEW: Missing data]'
            WHERE (ingredients = '[]' OR instructions = '[]')
            AND NOT (ingredients = '[]' AND instructions = '[]')
        """)
        
        marked_count = cursor.rowcount
        print(f"🏷️ Marked {marked_count} recipes with partial data for manual review")
        
        conn.commit()
        
    except Exception as e:
        logger.error(f"❌ Error fixing empty array recipes: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def fix_salt_pepper_recipes():
    """Fix recipes with only 'Salt and pepper' as ingredients"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("🧂 FIXING 'SALT AND PEPPER' RECIPES")
    print("="*80)
    
    try:
        # Find and review salt and pepper recipes
        cursor.execute("""
            SELECT id, title, ingredients, instructions, source
            FROM recipes 
            WHERE ingredients = 'Salt and pepper' OR ingredients = '1 teaspoon salt'
        """)
        
        salt_recipes = cursor.fetchall()
        print(f"Found {len(salt_recipes)} recipes with insufficient seasoning-only ingredients")
        
        for recipe in salt_recipes:
            print(f"  📝 ID {recipe['id']}: {recipe['title']}")
            print(f"      Source: {recipe['source']}")
            print(f"      Ingredients: {recipe['ingredients']}")
            print(f"      Instructions preview: {recipe['instructions'][:100]}...")
        
        # Mark these for manual review instead of deleting
        cursor.execute("""
            UPDATE recipes 
            SET description = COALESCE(description, '') || ' [NEEDS_MANUAL_REVIEW: Incomplete ingredients extraction]',
                category = COALESCE(category, 'extraction_errors')
            WHERE ingredients = 'Salt and pepper' OR ingredients = '1 teaspoon salt'
        """)
        
        marked_count = cursor.rowcount
        print(f"🏷️ Marked {marked_count} salt-and-pepper recipes for manual review")
        
        conn.commit()
        
    except Exception as e:
        logger.error(f"❌ Error fixing salt and pepper recipes: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def clean_extraction_artifacts():
    """Clean up extraction artifacts like 'INGREDIENTS', 'DIRECTIONS'"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("🧹 CLEANING EXTRACTION ARTIFACTS")
    print("="*80)
    
    try:
        # Find recipes with extraction artifacts
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM recipes 
            WHERE ingredients LIKE '%INGREDIENTS%' 
               OR ingredients LIKE '%DIRECTIONS%'
               OR instructions LIKE '%INGREDIENTS%'
               OR instructions LIKE '%DIRECTIONS%'
        """)
        
        artifact_count = cursor.fetchone()['count']
        print(f"Found {artifact_count} recipes with extraction artifacts")
        
        # Clean ingredients field
        cursor.execute("""
            UPDATE recipes 
            SET ingredients = REPLACE(
                REPLACE(
                    REPLACE(ingredients, '["INGREDIENTS", ', '['),
                    'INGREDIENTS ', ''
                ),
                '"INGREDIENTS"', ''
            )
            WHERE ingredients LIKE '%INGREDIENTS%'
        """)
        
        ingredients_cleaned = cursor.rowcount
        print(f"🧹 Cleaned {ingredients_cleaned} recipes' ingredients fields")
        
        # Clean instructions field  
        cursor.execute("""
            UPDATE recipes 
            SET instructions = REPLACE(
                REPLACE(
                    REPLACE(instructions, '["DIRECTIONS\\n', '['),
                    'DIRECTIONS\\n', ''
                ),
                '"DIRECTIONS"', ''
            )
            WHERE instructions LIKE '%DIRECTIONS%'
        """)
        
        instructions_cleaned = cursor.rowcount
        print(f"🧹 Cleaned {instructions_cleaned} recipes' instructions fields")
        
        conn.commit()
        
    except Exception as e:
        logger.error(f"❌ Error cleaning extraction artifacts: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def standardize_data_formats():
    """Standardize servings and time formats"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("📏 STANDARDIZING DATA FORMATS")
    print("="*80)
    
    try:
        # Standardize servings format
        cursor.execute("""
            UPDATE recipes 
            SET servings = CASE 
                WHEN servings LIKE 'Serves %' THEN REPLACE(servings, 'Serves ', '')
                WHEN servings LIKE '% servings' THEN REPLACE(servings, ' servings', '')
                WHEN servings LIKE '% portions' THEN REPLACE(servings, ' portions', '')
                ELSE servings
            END
            WHERE servings IS NOT NULL
        """)
        
        servings_updated = cursor.rowcount
        print(f"📏 Standardized {servings_updated} servings formats")
        
        # Standardize time format
        cursor.execute("""
            UPDATE recipes 
            SET total_time = CASE 
                WHEN total_time LIKE '% minutes' THEN REPLACE(total_time, ' minutes', ' min')
                WHEN total_time LIKE '% minute' THEN REPLACE(total_time, ' minute', ' min')
                WHEN total_time LIKE '% hours' THEN REPLACE(total_time, ' hours', ' hr')
                WHEN total_time LIKE '% hour' THEN REPLACE(total_time, ' hour', ' hr')
                ELSE total_time
            END
            WHERE total_time IS NOT NULL
        """)
        
        time_updated = cursor.rowcount
        print(f"⏱️ Standardized {time_updated} time formats")
        
        conn.commit()
        
    except Exception as e:
        logger.error(f"❌ Error standardizing data formats: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def create_quality_scores():
    """Add quality scores to recipes for easier filtering"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("📊 CREATING QUALITY SCORES")
    print("="*80)
    
    try:
        # Add quality_score column if it doesn't exist
        cursor.execute("""
            ALTER TABLE recipes 
            ADD COLUMN IF NOT EXISTS quality_score INTEGER DEFAULT 0
        """)
        
        # Calculate quality scores
        cursor.execute("""
            UPDATE recipes 
            SET quality_score = (
                CASE WHEN title IS NOT NULL AND LENGTH(TRIM(title)) > 5 THEN 1 ELSE 0 END +
                CASE WHEN ingredients IS NOT NULL AND LENGTH(TRIM(ingredients)) > 20 THEN 2 ELSE 0 END +
                CASE WHEN instructions IS NOT NULL AND LENGTH(TRIM(instructions)) > 50 THEN 2 ELSE 0 END +
                CASE WHEN servings IS NOT NULL AND servings != '' THEN 1 ELSE 0 END +
                CASE WHEN total_time IS NOT NULL AND total_time != '' THEN 1 ELSE 0 END +
                CASE WHEN category IS NOT NULL AND category != '' THEN 1 ELSE 0 END +
                CASE WHEN description IS NOT NULL AND description != '' THEN 1 ELSE 0 END
            )
        """)
        
        scored_count = cursor.rowcount
        print(f"📊 Created quality scores for {scored_count} recipes")
        
        # Show distribution
        cursor.execute("""
            SELECT quality_score, COUNT(*) as count
            FROM recipes 
            GROUP BY quality_score
            ORDER BY quality_score DESC
        """)
        
        distribution = cursor.fetchall()
        print(f"\n📈 Quality Score Distribution:")
        for score_info in distribution:
            score = score_info['quality_score']
            count = score_info['count']
            percentage = (count / scored_count) * 100
            print(f"  Score {score}: {count:>3} recipes ({percentage:5.1f}%)")
        
        conn.commit()
        
    except Exception as e:
        logger.error(f"❌ Error creating quality scores: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def generate_cleanup_report():
    """Generate final cleanup report"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("📋 CLEANUP COMPLETION REPORT")
    print("="*80)
    
    try:
        # Total recipes
        cursor.execute("SELECT COUNT(*) as total FROM recipes")
        total_recipes = cursor.fetchone()['total']
        
        # Recipes needing manual review
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM recipes 
            WHERE description LIKE '%NEEDS_MANUAL_REVIEW%'
        """)
        needs_review = cursor.fetchone()['count']
        
        # Recipes with good quality scores
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM recipes 
            WHERE quality_score >= 6
        """)
        high_quality = cursor.fetchone()['count']
        
        # Recipes with low quality scores
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM recipes 
            WHERE quality_score <= 3
        """)
        low_quality = cursor.fetchone()['count']
        
        print(f"\n📊 FINAL STATISTICS:")
        print(f"  📚 Total recipes: {total_recipes:,}")
        print(f"  ⭐ High quality (score 6+): {high_quality:,} ({(high_quality/total_recipes)*100:.1f}%)")
        print(f"  ⚠️ Needs manual review: {needs_review:,} ({(needs_review/total_recipes)*100:.1f}%)")
        print(f"  🔴 Low quality (score ≤3): {low_quality:,} ({(low_quality/total_recipes)*100:.1f}%)")
        
        print(f"\n✅ CLEANUP ACTIONS COMPLETED:")
        print(f"  🗑️ Removed recipes with completely empty data")
        print(f"  🏷️ Marked incomplete recipes for manual review")
        print(f"  🧹 Cleaned extraction artifacts from ingredients/instructions")
        print(f"  📏 Standardized servings and time formats")
        print(f"  📊 Added quality scoring system")
        
        print(f"\n🔧 NEXT STEPS RECOMMENDED:")
        print(f"  1. Review recipes marked with NEEDS_MANUAL_REVIEW")
        print(f"  2. Implement frontend fallbacks for low-quality recipes")
        print(f"  3. Add quality score filtering to search results")
        print(f"  4. Create admin interface for manual recipe editing")
        print(f"  5. Enhance recipe parsers to prevent future data quality issues")
        
    except Exception as e:
        logger.error(f"❌ Error generating cleanup report: {e}")
    finally:
        conn.close()

def main():
    """Run complete data cleanup process"""
    print("🚀 Starting comprehensive recipe data cleanup...")
    print(f"📅 Cleanup date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Run cleanup steps
        backup_problematic_recipes()
        fix_empty_array_recipes()
        fix_salt_pepper_recipes()
        clean_extraction_artifacts()
        standardize_data_formats()
        create_quality_scores()
        generate_cleanup_report()
        
        print("\n" + "="*80)
        print("✅ DATA CLEANUP COMPLETE!")
        print("="*80)
        print("\nYour recipe database has been cleaned and optimized!")
        print("Check the quality scores to filter recipes in your application.")
        
    except Exception as e:
        logger.error(f"❌ Cleanup failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
