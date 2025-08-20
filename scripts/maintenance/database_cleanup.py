#!/usr/bin/env python3
"""
🧹 DATABASE CLEANUP - Remove Contaminated ATK Data
==================================================

Remove all ATK 25th Anniversary and ATK Teen data from hungie.db
to prepare for clean re-extraction with intelligence engine.
"""

import sqlite3
import os
from datetime import datetime

def analyze_current_database():
    """Analyze current database contents"""
    print("🔍 ANALYZING CURRENT DATABASE")
    print("=" * 50)
    
    if not os.path.exists('hungie.db'):
        print("❌ hungie.db not found!")
        return False
    
    conn = sqlite3.connect('hungie.db')
    cursor = conn.cursor()
    
    try:
        # Check if recipes table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='recipes'")
        if not cursor.fetchone():
            print("❌ No recipes table found!")
            return False
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM recipes")
        total_recipes = cursor.fetchone()[0]
        print(f"📊 Total recipes in database: {total_recipes}")
        
        # Get count by source
        cursor.execute("SELECT source, COUNT(*) FROM recipes GROUP BY source ORDER BY COUNT(*) DESC")
        sources = cursor.fetchall()
        
        print(f"\n📚 SOURCES BREAKDOWN:")
        atk_25th_count = 0
        atk_teen_count = 0
        other_count = 0
        
        for source, count in sources:
            print(f"  {source}: {count} recipes")
            if "25th Anniversary" in source:
                atk_25th_count = count
            elif "Teen" in source:
                atk_teen_count = count
            else:
                other_count += count
        
        print(f"\n🎯 CLEANUP TARGET:")
        print(f"  ATK 25th Anniversary: {atk_25th_count} recipes (REMOVE)")
        print(f"  ATK Teen: {atk_teen_count} recipes (REMOVE)")
        print(f"  Other sources: {other_count} recipes (KEEP)")
        
        cleanup_count = atk_25th_count + atk_teen_count
        remaining_count = total_recipes - cleanup_count
        
        print(f"\n📈 AFTER CLEANUP:")
        print(f"  Will remove: {cleanup_count} recipes")
        print(f"  Will remain: {remaining_count} recipes")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        conn.close()
        return False

def backup_database():
    """Create backup before cleanup"""
    print(f"\n💾 CREATING BACKUP")
    print("-" * 30)
    
    if not os.path.exists('hungie.db'):
        print("❌ No database to backup!")
        return False
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"hungie_backup_before_cleanup_{timestamp}.db"
    
    try:
        # Copy database file
        import shutil
        shutil.copy2('hungie.db', backup_name)
        print(f"✅ Backup created: {backup_name}")
        return True
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False

def cleanup_atk_data():
    """Remove ATK 25th Anniversary and Teen data"""
    print(f"\n🧹 CLEANING UP ATK DATA")
    print("-" * 30)
    
    conn = sqlite3.connect('hungie.db')
    cursor = conn.cursor()
    
    try:
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
        
        print(f"🎯 Will remove {removal_count} recipes")
        
        # Remove ATK data
        cursor.execute("""
            DELETE FROM recipes 
            WHERE source LIKE '%25th Anniversary%' OR source LIKE '%Teen%'
        """)
        
        removed_count = cursor.rowcount
        conn.commit()
        
        # Verify cleanup
        cursor.execute("SELECT COUNT(*) FROM recipes")
        remaining_count = cursor.fetchone()[0]
        
        print(f"✅ Successfully removed {removed_count} recipes")
        print(f"📊 Remaining recipes: {remaining_count}")
        
        # Show remaining sources
        cursor.execute("SELECT source, COUNT(*) FROM recipes GROUP BY source")
        remaining_sources = cursor.fetchall()
        
        if remaining_sources:
            print(f"\n📚 REMAINING SOURCES:")
            for source, count in remaining_sources:
                print(f"  {source}: {count} recipes")
        else:
            print("\n📚 No recipes remaining in database")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Cleanup failed: {e}")
        conn.rollback()
        conn.close()
        return False

def main():
    """Main cleanup process"""
    print("🧹 HUNGIE.DB CLEANUP PROCESS")
    print("=" * 60)
    
    # Step 1: Analyze current state
    if not analyze_current_database():
        print("❌ Database analysis failed!")
        return
    
    # Step 2: Confirm cleanup
    print(f"\n⚠️  CONFIRMATION REQUIRED")
    print("This will permanently remove all ATK 25th Anniversary and Teen data!")
    confirm = input("Continue with cleanup? (y/N): ").lower().strip()
    
    if confirm != 'y':
        print("❌ Cleanup cancelled by user")
        return
    
    # Step 3: Create backup
    if not backup_database():
        print("❌ Backup failed! Aborting cleanup for safety.")
        return
    
    # Step 4: Perform cleanup
    if cleanup_atk_data():
        print(f"\n✅ DATABASE CLEANUP COMPLETE!")
        print("Ready for clean re-extraction with intelligence engine.")
    else:
        print(f"\n❌ CLEANUP FAILED!")
        print("Database backup is available for restoration.")

if __name__ == "__main__":
    main()
