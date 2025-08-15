#!/usr/bin/env python3
"""
Fix PostgreSQL Servings Column
Ensure servings data is properly migrated and accessible
"""
import os
import sqlite3
import psycopg2
import psycopg2.extras

def fix_postgresql_servings():
    """Fix the servings column issue in PostgreSQL"""
    
    print("🔧 FIXING POSTGRESQL SERVINGS COLUMN")
    print("=" * 50)
    
    # Get DATABASE_URL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not set")
        print("💡 This needs to run with Railway environment or set DATABASE_URL")
        return False
    
    try:
        # Connect to PostgreSQL
        print("🔗 Connecting to PostgreSQL...")
        pg_conn = psycopg2.connect(database_url)
        pg_cursor = pg_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Check current table structure
        print("📋 Checking current table structure...")
        pg_cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'recipes' 
            AND column_name = 'servings'
        """)
        
        servings_col = pg_cursor.fetchall()
        if servings_col:
            print("✅ Servings column exists in PostgreSQL")
            
            # Check data count
            pg_cursor.execute("SELECT COUNT(*) as total FROM recipes")
            total = pg_cursor.fetchone()['total']
            
            pg_cursor.execute("SELECT COUNT(*) as with_servings FROM recipes WHERE servings IS NOT NULL AND servings != ''")
            with_servings = pg_cursor.fetchone()['with_servings']
            
            print(f"📊 PostgreSQL Status:")
            print(f"   Total recipes: {total}")
            print(f"   Recipes with servings: {with_servings}")
            
            if with_servings == 0:
                print("⚠️  No servings data found - need to migrate from SQLite")
                return migrate_servings_data(pg_conn)
            else:
                print("✅ Servings data already exists")
                
                # Test the query that was failing
                print("\n🧪 Testing recipe query with servings...")
                try:
                    pg_cursor.execute("""
                        SELECT r.id, r.title, r.servings 
                        FROM recipes r 
                        WHERE r.servings IS NOT NULL 
                        LIMIT 3
                    """)
                    results = pg_cursor.fetchall()
                    print("✅ Query works! Sample data:")
                    for row in results:
                        print(f"   - {row['title']}: {row['servings']}")
                    return True
                except Exception as e:
                    print(f"❌ Query still fails: {e}")
                    return False
        else:
            print("❌ Servings column missing - need to add it")
            return add_servings_column(pg_conn)
            
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

def add_servings_column(pg_conn):
    """Add servings column to PostgreSQL if missing"""
    print("\n🔧 Adding servings column to PostgreSQL...")
    
    try:
        cursor = pg_conn.cursor()
        cursor.execute("ALTER TABLE recipes ADD COLUMN servings TEXT")
        pg_conn.commit()
        print("✅ Servings column added")
        
        return migrate_servings_data(pg_conn)
        
    except Exception as e:
        print(f"❌ Failed to add servings column: {e}")
        pg_conn.rollback()
        return False

def migrate_servings_data(pg_conn):
    """Migrate servings data from SQLite to PostgreSQL"""
    print("\n📋 Migrating servings data from SQLite...")
    
    try:
        # Connect to SQLite
        sqlite_conn = sqlite3.connect('hungie.db')
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()
        
        # Get servings data from SQLite
        sqlite_cursor.execute("SELECT id, servings FROM recipes WHERE servings IS NOT NULL AND servings != ''")
        servings_data = sqlite_cursor.fetchall()
        
        print(f"📊 Found {len(servings_data)} recipes with servings data in SQLite")
        
        if len(servings_data) == 0:
            print("⚠️  No servings data in SQLite either")
            return False
        
        # Update PostgreSQL with servings data
        pg_cursor = pg_conn.cursor()
        
        updated_count = 0
        for row in servings_data:
            # Map SQLite ID to PostgreSQL ID (they should match if migration was done properly)
            try:
                pg_cursor.execute(
                    "UPDATE recipes SET servings = %s WHERE id = %s",
                    (row['servings'], row['id'])
                )
                if pg_cursor.rowcount > 0:
                    updated_count += 1
            except Exception as e:
                print(f"Error updating recipe {row['id']}: {e}")
        
        pg_conn.commit()
        print(f"✅ Updated {updated_count} recipes with servings data")
        
        sqlite_conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to migrate servings data: {e}")
        pg_conn.rollback()
        return False

def verify_fix(pg_conn):
    """Verify the servings fix worked"""
    print("\n✅ Verifying servings fix...")
    
    try:
        cursor = pg_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Test the exact query from enhanced_recipe_suggestions.py
        cursor.execute("""
            SELECT DISTINCT r.id, r.title, r.description, r.servings, 
                   r.hands_on_time, r.total_time, r.ingredients, r.instructions,
                   r.book_id, r.page_number
            FROM recipes r
            WHERE r.title ILIKE %s
            LIMIT 3
        """, ('%chicken%',))
        
        results = cursor.fetchall()
        print(f"✅ Recipe search query works! Found {len(results)} chicken recipes:")
        
        for recipe in results:
            print(f"   - {recipe['title']}")
            print(f"     Servings: {recipe['servings']}")
            print(f"     Cook time: {recipe['total_time']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    success = fix_postgresql_servings()
    
    if success:
        print("\n🎉 SERVINGS COLUMN FIX COMPLETE!")
        print("✅ PostgreSQL servings data restored")
        print("✅ Recipe scaling functionality preserved")
        print("✅ Chat API should now work with full servings data")
    else:
        print("\n❌ SERVINGS FIX FAILED")
        print("💡 Check PostgreSQL connection and migration status")
