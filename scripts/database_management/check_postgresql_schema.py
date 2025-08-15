#!/usr/bin/env python3
"""
Check PostgreSQL Schema vs Expected Schema
Diagnose column name mismatches causing recipe search failures
"""

import os
import psycopg2
import psycopg2.extras

def check_postgresql_schema():
    """Check what columns actually exist in PostgreSQL recipes table"""
    
    print("🔍 POSTGRESQL SCHEMA DIAGNOSTIC")
    print("=" * 50)
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        # Use Railway's known DATABASE_URL from the variables we saw
        database_url = "postgresql://postgres:udQLpljdqTYmESmntwzmwDcOlBVbqlJG@postgres.railway.internal:5432/railway"
        print("⚠️  Using hardcoded Railway DATABASE_URL for testing")
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Get recipes table schema
        print("📋 RECIPES TABLE SCHEMA:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'recipes' 
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        for col in columns:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            print(f"   {col['column_name']}: {col['data_type']} {nullable}")
        
        print(f"\n📊 Total columns in recipes table: {len(columns)}")
        
        # Check if table has any data
        print("\n🔢 RECIPE COUNT CHECK:")
        cursor.execute("SELECT COUNT(*) as count FROM recipes")
        count = cursor.fetchone()['count']
        print(f"   Total recipes in PostgreSQL: {count}")
        
        if count > 0:
            # Sample a few recipes to see structure
            print("\n📋 SAMPLE RECIPE DATA:")
            cursor.execute("SELECT * FROM recipes LIMIT 2")
            samples = cursor.fetchall()
            
            for i, recipe in enumerate(samples):
                print(f"\n   Recipe {i+1}:")
                for key, value in recipe.items():
                    if value and len(str(value)) > 50:
                        print(f"     {key}: {str(value)[:50]}...")
                    else:
                        print(f"     {key}: {value}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Schema diagnostic complete!")
        
    except Exception as e:
        print(f"❌ Error checking PostgreSQL schema: {e}")
        print(f"   Error type: {type(e).__name__}")

if __name__ == "__main__":
    check_postgresql_schema()
