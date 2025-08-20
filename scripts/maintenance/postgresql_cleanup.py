#!/usr/bin/env python3
"""
🧹 POSTGRESQL CLEANUP - Remove Contaminated ATK Data
=====================================================

Remove all ATK 25th Anniversary and ATK Teen data from PostgreSQL
to prepare for clean re-extraction with intelligence engine.
"""

import psycopg2
from datetime import datetime

def analyze_current_database():
    """Analyze current PostgreSQL database contents"""
    print("🔍 ANALYZING CURRENT POSTGRESQL DATABASE")
    print("=" * 60)
    
    try:
        database_url = 'postgresql://postgres:udQLpljdqTYmESmntwzmwDcOlBVbqlJG@shuttle.proxy.rlwy.net:31331/railway'
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM recipes")
        total_recipes = cursor.fetchone()[0]
        print(f"📊 Total recipes in database: {total_recipes:,}")
        
        # Get count by source
        cursor.execute("SELECT source, COUNT(*) FROM recipes GROUP BY source ORDER BY COUNT(*) DESC")
        sources = cursor.fetchall()
        
        print(f"\n📚 SOURCES BREAKDOWN:")
        atk_25th_count = 0
        atk_teen_count = 0
        other_count = 0
        
        for source, count in sources:
            print(f"  {source}: {count:,} recipes")
            if "25th Anniversary" in source:
                atk_25th_count = count
            elif "Teen" in source:
                atk_teen_count = count
            else:
                other_count += count
        
        print(f"\n🎯 CLEANUP TARGET:")
        print(f"  ATK 25th Anniversary: {atk_25th_count:,} recipes (REMOVE)")
        print(f"  ATK Teen: {atk_teen_count:,} recipes (REMOVE)")
        print(f"  Other sources: {other_count:,} recipes (KEEP)")
        
        cleanup_count = atk_25th_count + atk_teen_count
        remaining_count = total_recipes - cleanup_count
        
        print(f"\n📈 AFTER CLEANUP:")
        print(f"  Will remove: {cleanup_count:,} recipes")
        print(f"  Will remain: {remaining_count:,} recipes")
        
        conn.close()
        return True, cleanup_count, remaining_count
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False, 0, 0

def backup_database():
    """Create backup table before cleanup"""
    print(f"\n💾 CREATING BACKUP TABLE")
    print("-" * 40)
    
    try:
        database_url = 'postgresql://postgres:udQLpljdqTYmESmntwzmwDcOlBVbqlJG@shuttle.proxy.rlwy.net:31331/railway'
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_table = f"recipes_backup_before_cleanup_{timestamp}"
        
        # Create backup table with all current data
        cursor.execute(f"""
            CREATE TABLE {backup_table} AS 
            SELECT * FROM recipes
        """)
        
        # Get backup count
        cursor.execute(f"SELECT COUNT(*) FROM {backup_table}")
        backup_count = cursor.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        print(f"✅ Backup table created: {backup_table}")
        print(f"📊 Backed up {backup_count:,} recipes")
        return True, backup_table
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False, None

def cleanup_atk_data():
    """Remove ATK 25th Anniversary and Teen data"""
    print(f"\n🧹 CLEANING UP ATK DATA")
    print("-" * 40)
    
    try:
        database_url = 'postgresql://postgres:udQLpljdqTYmESmntwzmwDcOlBVbqlJG@shuttle.proxy.rlwy.net:31331/railway'
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Count what we're about to remove
        cursor.execute("""
            SELECT COUNT(*) FROM recipes 
            WHERE source LIKE '%25th Anniversary%' OR source LIKE '%Teen%'
        """)
        removal_count = cursor.fetchone()[0]
        
        if removal_count == 0:
            print("ℹ️  No ATK data found to remove")
            conn.close()
            return True
        
        print(f"🎯 Will remove {removal_count:,} recipes")
        
        # Also remove associated flavor profiles
        cursor.execute("""
            SELECT COUNT(*) FROM recipe_flavor_profiles rfp
            JOIN recipes r ON rfp.recipe_id = r.id
            WHERE r.source LIKE '%25th Anniversary%' OR r.source LIKE '%Teen%'
        """)
        flavor_removal_count = cursor.fetchone()[0]
        
        if flavor_removal_count > 0:
            print(f"🎯 Will also remove {flavor_removal_count:,} flavor profiles")
            
            # Remove flavor profiles first (foreign key constraint)
            cursor.execute("""
                DELETE FROM recipe_flavor_profiles 
                WHERE recipe_id IN (
                    SELECT id FROM recipes 
                    WHERE source LIKE '%25th Anniversary%' OR source LIKE '%Teen%'
                )
            """)
            print(f"✅ Removed {cursor.rowcount:,} flavor profiles")
        
        # Remove ATK recipes
        cursor.execute("""
            DELETE FROM recipes 
            WHERE source LIKE '%25th Anniversary%' OR source LIKE '%Teen%'
        """)
        
        removed_count = cursor.rowcount
        conn.commit()
        
        # Verify cleanup
        cursor.execute("SELECT COUNT(*) FROM recipes")
        remaining_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM recipe_flavor_profiles")
        remaining_flavors = cursor.fetchone()[0]
        
        print(f"✅ Successfully removed {removed_count:,} recipes")
        print(f"📊 Remaining recipes: {remaining_count:,}")
        print(f"📊 Remaining flavor profiles: {remaining_flavors:,}")
        
        # Show remaining sources
        cursor.execute("SELECT source, COUNT(*) FROM recipes GROUP BY source ORDER BY COUNT(*) DESC")
        remaining_sources = cursor.fetchall()
        
        if remaining_sources:
            print(f"\n📚 REMAINING SOURCES:")
            for source, count in remaining_sources:
                print(f"  {source}: {count:,} recipes")
        else:
            print("\n📚 No recipes remaining in database")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        try:
            conn.rollback()
            conn.close()
        except:
            pass
        return False

def main():
    """Main cleanup process"""
    print("🧹 POSTGRESQL CLEANUP PROCESS")
    print("=" * 70)
    
    # Step 1: Analyze current state
    success, cleanup_count, remaining_count = analyze_current_database()
    if not success:
        print("❌ Database analysis failed!")
        return
    
    if cleanup_count == 0:
        print("\n✅ No ATK data found to clean up!")
        return
    
    # Step 2: Confirm cleanup
    print(f"\n⚠️  CONFIRMATION REQUIRED")
    print(f"This will permanently remove {cleanup_count:,} ATK recipes!")
    print(f"Database will have {remaining_count:,} recipes remaining.")
    confirm = input("Continue with cleanup? (y/N): ").lower().strip()
    
    if confirm != 'y':
        print("❌ Cleanup cancelled by user")
        return
    
    # Step 3: Create backup
    backup_success, backup_table = backup_database()
    if not backup_success:
        print("❌ Backup failed! Aborting cleanup for safety.")
        return
    
    # Step 4: Perform cleanup
    if cleanup_atk_data():
        print(f"\n✅ POSTGRESQL CLEANUP COMPLETE!")
        print(f"🛡️  Data backed up in table: {backup_table}")
        print("🚀 Ready for clean re-extraction with intelligence engine.")
    else:
        print(f"\n❌ CLEANUP FAILED!")
        print(f"🛡️  Database backup is available in: {backup_table}")

if __name__ == "__main__":
    main()
