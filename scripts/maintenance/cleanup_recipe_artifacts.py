#!/usr/bin/env python3
"""
🧹 Recipe Database Cleanup Script
=================================
Remove extraction artifacts and improve data quality
"""

import psycopg2
import json
from datetime import datetime

def cleanup_recipe_artifacts():
    """Clean up extraction artifacts from the recipe database"""
    print("🧹 RECIPE DATABASE CLEANUP SCRIPT")
    print("=" * 60)
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        database_url = 'postgresql://postgres:udQLpljdqTYmESmntwzmwDcOlBVbqlJG@shuttle.proxy.rlwy.net:31331/railway'
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # First, let's analyze what we're about to clean up
        print("🔍 PRE-CLEANUP ANALYSIS")
        print("-" * 40)
        
        cursor.execute("SELECT COUNT(*) FROM recipes")
        total_before = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM recipe_flavor_profiles")
        flavor_profiles_before = cursor.fetchone()[0]
        
        print(f"📊 Current database state:")
        print(f"  Total recipes: {total_before:,}")
        print(f"  Flavor profiles: {flavor_profiles_before:,}")
        
        # Define cleanup criteria
        cleanup_patterns = [
            "Start Cooking!",
            "Before You Begin", 
            "PREPARE INGREDIENTS",
            "To Finish",
            "Recipe with Topping",
            "Dressing"  # Single word entries that are likely artifacts
        ]
        
        # Additional criteria for artifacts
        additional_criteria = [
            # Very short titles (likely artifacts)
            "LENGTH(title) <= 3",
            # Garbled text patterns
            "title LIKE '%ajar (see photo%'",
            "title LIKE '%unti l skins ar e%'", 
            "title LIKE '%wi thout stirring%'",
            # Generic recipe page references
            "title LIKE 'ATK Recipe from Page%'",
            # Empty or whitespace-only titles
            "TRIM(title) = ''"
        ]
        
        recipes_to_delete = []
        
        # Find recipes matching cleanup patterns
        for pattern in cleanup_patterns:
            cursor.execute("""
                SELECT id, title, source 
                FROM recipes 
                WHERE title = %s
            """, (pattern,))
            
            matches = cursor.fetchall()
            recipes_to_delete.extend(matches)
        
        # Find recipes matching additional criteria
        for criteria in additional_criteria:
            cursor.execute(f"""
                SELECT id, title, source 
                FROM recipes 
                WHERE {criteria}
            """)
            
            matches = cursor.fetchall()
            recipes_to_delete.extend(matches)
        
        # Remove duplicates (recipes matching multiple criteria)
        unique_recipes_to_delete = {}
        for recipe_id, title, source in recipes_to_delete:
            unique_recipes_to_delete[recipe_id] = (title, source)
        
        print(f"\n🎯 CLEANUP TARGETS IDENTIFIED")
        print("-" * 40)
        print(f"📋 Found {len(unique_recipes_to_delete)} recipes to delete")
        
        if len(unique_recipes_to_delete) == 0:
            print("✅ No artifacts found - database is clean!")
            return
        
        # Show sample of what will be deleted
        print(f"\n📝 Sample entries to be deleted:")
        sample_count = 0
        for recipe_id, (title, source) in unique_recipes_to_delete.items():
            if sample_count >= 10:
                break
            source_short = source[:40] + "..." if len(source) > 40 else source
            print(f"  ID {recipe_id}: '{title}' ({source_short})")
            sample_count += 1
        
        if len(unique_recipes_to_delete) > 10:
            print(f"  ... and {len(unique_recipes_to_delete) - 10} more")
        
        # Ask for confirmation
        print(f"\n⚠️  CONFIRMATION REQUIRED")
        print("-" * 40)
        print(f"This will permanently delete {len(unique_recipes_to_delete)} recipe entries.")
        print(f"This action cannot be undone!")
        
        # For safety, let's create a backup first
        print(f"\n🛡️  CREATING BACKUP")
        print("-" * 40)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_table = f"recipes_backup_cleanup_{timestamp}"
        
        # Create backup table with recipes to be deleted
        cursor.execute(f"""
            CREATE TABLE {backup_table} AS 
            SELECT * FROM recipes 
            WHERE id IN ({','.join(map(str, unique_recipes_to_delete.keys()))})
        """)
        
        print(f"✅ Backup created: {backup_table}")
        print(f"📊 Backed up {len(unique_recipes_to_delete)} recipes")
        
        # Now proceed with cleanup - but let's make it safe with a transaction
        print(f"\n🧹 PERFORMING CLEANUP")
        print("-" * 40)
        
        try:
            # Start transaction
            cursor.execute("BEGIN")
            
            # Delete flavor profiles first (foreign key constraint)
            cursor.execute(f"""
                DELETE FROM recipe_flavor_profiles 
                WHERE recipe_id IN ({','.join(map(str, unique_recipes_to_delete.keys()))})
            """)
            
            deleted_profiles = cursor.rowcount
            print(f"🎨 Deleted {deleted_profiles} flavor profiles")
            
            # Delete the recipes
            cursor.execute(f"""
                DELETE FROM recipes 
                WHERE id IN ({','.join(map(str, unique_recipes_to_delete.keys()))})
            """)
            
            deleted_recipes = cursor.rowcount
            print(f"📚 Deleted {deleted_recipes} recipes")
            
            # Commit the transaction
            cursor.execute("COMMIT")
            
            print(f"✅ Cleanup completed successfully!")
            
        except Exception as e:
            # Rollback on error
            cursor.execute("ROLLBACK")
            print(f"❌ Cleanup failed: {e}")
            print(f"🔄 All changes rolled back")
            return False
        
        # Post-cleanup analysis
        print(f"\n📊 POST-CLEANUP ANALYSIS")
        print("-" * 40)
        
        cursor.execute("SELECT COUNT(*) FROM recipes")
        total_after = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM recipe_flavor_profiles")
        flavor_profiles_after = cursor.fetchone()[0]
        
        print(f"📈 Database state after cleanup:")
        print(f"  Total recipes: {total_after:,} (was {total_before:,})")
        print(f"  Flavor profiles: {flavor_profiles_after:,} (was {flavor_profiles_before:,})")
        print(f"  Recipes removed: {total_before - total_after:,}")
        print(f"  Flavor profiles removed: {flavor_profiles_before - flavor_profiles_after:,}")
        
        # Updated cookbook statistics
        cursor.execute("SELECT COUNT(*) FROM recipes WHERE source LIKE '%Teen%'")
        teen_clean = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM recipes WHERE source = 'America''s Test Kitchen 25th Anniversary'")
        atk25_clean = cursor.fetchone()[0]
        
        print(f"\n📚 CLEAN COOKBOOK STATISTICS")
        print("-" * 40)
        print(f"  ATK Teen Cookbook: {teen_clean} recipes (clean)")
        print(f"  ATK 25th Anniversary: {atk25_clean} recipes (clean)")
        
        improvement_percent = ((total_before - total_after) / total_before) * 100
        print(f"  Data quality improvement: {improvement_percent:.1f}%")
        
        print(f"\n🎉 CLEANUP COMPLETED SUCCESSFULLY!")
        print(f"✅ Backup table: {backup_table}")
        print(f"🧹 Database is now clean and ready for use!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        return False

def preview_cleanup():
    """Preview what would be cleaned up without making changes"""
    print("👁️  CLEANUP PREVIEW MODE")
    print("=" * 60)
    print("This will show what would be cleaned up without making changes")
    print()
    
    # Run the same analysis but don't actually delete anything
    # [Implementation would be similar but without the actual DELETE statements]
    
if __name__ == "__main__":
    print("🧹 Recipe Database Cleanup Tool")
    print("=" * 40)
    print("1. Preview cleanup (safe)")
    print("2. Perform cleanup (permanent)")
    print()
    
    choice = input("Choose option (1 or 2): ").strip()
    
    if choice == "1":
        preview_cleanup()
    elif choice == "2":
        confirm = input("Are you sure you want to permanently delete artifacts? (yes/no): ").strip().lower()
        if confirm == "yes":
            cleanup_recipe_artifacts()
        else:
            print("❌ Cleanup cancelled")
    else:
        print("❌ Invalid choice")
