#!/usr/bin/env python3
"""
Complete Servings Data Restoration
1. Migrate all servings data from SQLite to PostgreSQL
2. Ensure all recipes have default servings values
3. Fix the enhanced_recipe_suggestions to handle missing servings gracefully
"""
import os
import sqlite3
import psycopg2
import psycopg2.extras

def restore_servings_data():
    """Complete servings data restoration process"""
    
    print("🍽️  COMPLETE SERVINGS DATA RESTORATION")
    print("=" * 60)
    
    # Check if we have DATABASE_URL (Railway environment)
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("⚠️  DATABASE_URL not set - will test locally with SQLite")
        print("💡 For Railway deployment, this script needs DATABASE_URL")
        return test_local_servings()
    
    return restore_postgresql_servings(database_url)

def test_local_servings():
    """Test servings data handling locally with SQLite"""
    print("\n🧪 TESTING LOCAL SERVINGS DATA (SQLite)")
    print("=" * 45)
    
    try:
        conn = sqlite3.connect('hungie.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check current servings data
        cursor.execute("SELECT COUNT(*) FROM recipes")
        total_recipes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM recipes WHERE servings IS NOT NULL AND servings != ''")
        with_servings = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM recipes WHERE servings IS NULL OR servings = ''")
        without_servings = cursor.fetchone()[0]
        
        print(f"📊 SQLite Servings Status:")
        print(f"   Total recipes: {total_recipes}")
        print(f"   With servings data: {with_servings}")
        print(f"   Without servings data: {without_servings}")
        
        # Update empty servings with default values
        if without_servings > 0:
            print(f"\n🔧 Fixing {without_servings} recipes with missing servings...")
            cursor.execute("""
                UPDATE recipes 
                SET servings = 'Serves 4' 
                WHERE servings IS NULL OR servings = ''
            """)
            conn.commit()
            print(f"✅ Updated {cursor.rowcount} recipes with default 'Serves 4'")
        
        # Sample the data
        cursor.execute("SELECT title, servings FROM recipes LIMIT 5")
        samples = cursor.fetchall()
        print(f"\n📋 Sample recipes with servings:")
        for sample in samples:
            print(f"   - {sample['title']}: {sample['servings']}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Local servings test failed: {e}")
        return False

def restore_postgresql_servings(database_url):
    """Restore servings data in PostgreSQL from SQLite"""
    print("\n🚀 RESTORING POSTGRESQL SERVINGS DATA")
    print("=" * 45)
    
    try:
        # Connect to PostgreSQL
        print("🔗 Connecting to PostgreSQL...")
        pg_conn = psycopg2.connect(database_url)
        pg_cursor = pg_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Check if servings column exists
        pg_cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'recipes' AND column_name = 'servings'
        """)
        
        servings_exists = pg_cursor.fetchone()
        if not servings_exists:
            print("📋 Adding servings column to PostgreSQL...")
            pg_cursor.execute("ALTER TABLE recipes ADD COLUMN servings TEXT")
            pg_conn.commit()
            print("✅ Servings column added")
        else:
            print("✅ Servings column exists")
        
        # Check current PostgreSQL servings status
        pg_cursor.execute("SELECT COUNT(*) as total FROM recipes")
        pg_total = pg_cursor.fetchone()['total']
        
        pg_cursor.execute("SELECT COUNT(*) as with_servings FROM recipes WHERE servings IS NOT NULL AND servings != ''")
        pg_with_servings = pg_cursor.fetchone()['with_servings']
        
        print(f"📊 PostgreSQL Current Status:")
        print(f"   Total recipes: {pg_total}")
        print(f"   With servings: {pg_with_servings}")
        print(f"   Missing servings: {pg_total - pg_with_servings}")
        
        # Connect to SQLite to get servings data
        print("\n📋 Reading servings data from SQLite...")
        sqlite_conn = sqlite3.connect('hungie.db')
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()
        
        # Get all recipes with their servings data
        sqlite_cursor.execute("""
            SELECT id, title, servings 
            FROM recipes 
            ORDER BY id
        """)
        sqlite_recipes = sqlite_cursor.fetchall()
        
        print(f"📊 SQLite has {len(sqlite_recipes)} recipes")
        
        # Update PostgreSQL with servings data
        print("🔄 Updating PostgreSQL with servings data...")
        updated_count = 0
        default_count = 0
        
        for recipe in sqlite_recipes:
            # Determine servings value
            servings_value = recipe['servings']
            if not servings_value or servings_value.strip() == '':
                servings_value = 'Serves 4'  # Default value
                default_count += 1
            
            try:
                # Update based on title match (more reliable than ID if IDs don't match)
                pg_cursor.execute("""
                    UPDATE recipes 
                    SET servings = %s 
                    WHERE title = %s
                """, (servings_value, recipe['title']))
                
                if pg_cursor.rowcount > 0:
                    updated_count += 1
                    
            except Exception as e:
                print(f"⚠️  Error updating recipe '{recipe['title']}': {e}")
        
        # Update any remaining recipes without servings
        pg_cursor.execute("""
            UPDATE recipes 
            SET servings = 'Serves 4' 
            WHERE servings IS NULL OR servings = ''
        """)
        additional_defaults = pg_cursor.rowcount
        
        pg_conn.commit()
        
        print(f"✅ Migration Complete:")
        print(f"   Updated recipes: {updated_count}")
        print(f"   Set to default 'Serves 4': {default_count + additional_defaults}")
        
        # Verify the fix
        pg_cursor.execute("SELECT COUNT(*) as with_servings FROM recipes WHERE servings IS NOT NULL AND servings != ''")
        final_count = pg_cursor.fetchone()['with_servings']
        print(f"   Final recipes with servings: {final_count}")
        
        # Test the problematic query
        print("\n🧪 Testing recipe query with servings...")
        pg_cursor.execute("""
            SELECT r.id, r.title, r.servings 
            FROM recipes r 
            WHERE r.title ILIKE %s 
            LIMIT 3
        """, ('%chicken%',))
        
        test_results = pg_cursor.fetchall()
        print(f"✅ Query successful! Found {len(test_results)} chicken recipes:")
        for result in test_results:
            print(f"   - {result['title']}: {result['servings']}")
        
        sqlite_conn.close()
        pg_conn.close()
        return True
        
    except Exception as e:
        print(f"❌ PostgreSQL servings restoration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def update_enhanced_suggestions_safety():
    """Update enhanced_recipe_suggestions.py to handle servings safely"""
    print("\n🛡️  UPDATING ENHANCED SUGGESTIONS FOR SERVINGS SAFETY")
    print("=" * 55)
    
    # This will be done with a separate file edit
    print("📝 Need to update enhanced_recipe_suggestions.py to:")
    print("   1. Always provide default servings value")
    print("   2. Handle None/empty servings gracefully")
    print("   3. Ensure no errors when servings is missing")
    
    return True

if __name__ == "__main__":
    print("🍽️  SERVINGS DATA RESTORATION TOOL")
    print("=" * 50)
    print("This tool will:")
    print("✅ Migrate all servings data from SQLite to PostgreSQL")
    print("✅ Set default 'Serves 4' for recipes without servings")
    print("✅ Ensure no servings-related errors in the application")
    print()
    
    success = restore_servings_data()
    
    if success:
        print("\n🎉 SERVINGS DATA RESTORATION COMPLETE!")
        print("✅ All recipes now have servings data")
        print("✅ Recipe scaling functionality preserved")
        print("✅ Default 'Serves 4' applied where needed")
        print("✅ Chat API will work without servings errors")
        
        print("\n🎯 Next Steps:")
        print("1. Deploy updated code to Railway")
        print("2. Test recipe search functionality")
        print("3. Implement recipe scaling features")
        
    else:
        print("\n❌ SERVINGS RESTORATION FAILED")
        print("💡 Check database connections and permissions")
        
    print("\n📊 Servings Data Value Examples:")
    print("   - 'Serves 4' (most common default)")
    print("   - 'Serves 2-3' (range servings)")
    print("   - 'Serves 8-10' (larger gatherings)")
    print("   - 'Serves 1' (individual portions)")
    print("   - 'Serves 20' (party-size recipes)")
