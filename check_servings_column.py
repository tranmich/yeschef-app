#!/usr/bin/env python3
"""
Check PostgreSQL Servings Column Status
Investigate why servings column appears to be missing
"""
import os
import psycopg2
import psycopg2.extras

def check_postgresql_servings():
    """Check if servings column actually exists in PostgreSQL"""
    
    # Use Railway DATABASE_URL if available, or hardcoded for testing
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not set - testing locally")
        return
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        print("🔍 POSTGRESQL SERVINGS COLUMN INVESTIGATION")
        print("=" * 50)
        
        # Check if recipes table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'recipes'
            );
        """)
        table_exists = cursor.fetchone()[0]
        print(f"Recipes table exists: {table_exists}")
        
        if table_exists:
            # Check table schema
            cursor.execute("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'recipes' 
                ORDER BY ordinal_position
            """)
            
            columns = cursor.fetchall()
            print(f"\nPostgreSQL recipes table has {len(columns)} columns:")
            
            servings_found = False
            for col in columns:
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                print(f"  - {col['column_name']}: {col['data_type']} {nullable}")
                if col['column_name'] == 'servings':
                    servings_found = True
            
            print(f"\n🎯 Servings column found: {servings_found}")
            
            # If servings column exists, check data
            if servings_found:
                cursor.execute("SELECT COUNT(*) as total FROM recipes")
                total_recipes = cursor.fetchone()['total']
                
                cursor.execute("SELECT COUNT(*) as with_servings FROM recipes WHERE servings IS NOT NULL AND servings != ''")
                with_servings = cursor.fetchone()['with_servings']
                
                print(f"\n📊 Recipe Data:")
                print(f"  Total recipes: {total_recipes}")
                print(f"  Recipes with servings data: {with_servings}")
                
                # Sample servings data
                cursor.execute("SELECT servings FROM recipes WHERE servings IS NOT NULL AND servings != '' LIMIT 5")
                samples = cursor.fetchall()
                print(f"\n📋 Sample servings data:")
                for sample in samples:
                    print(f"  - '{sample['servings']}'")
            
            # Test the problematic query
            print(f"\n🧪 Testing problematic query:")
            try:
                cursor.execute("SELECT r.id, r.title, r.servings FROM recipes r LIMIT 3")
                results = cursor.fetchall()
                print("✅ Query with servings column works!")
                for result in results:
                    print(f"  - {result['title']}: {result['servings']}")
            except Exception as e:
                print(f"❌ Query with servings failed: {e}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")

if __name__ == "__main__":
    check_postgresql_servings()
