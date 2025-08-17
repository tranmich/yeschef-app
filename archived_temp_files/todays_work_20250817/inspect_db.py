#!/usr/bin/env python3
"""
Direct PostgreSQL connection to check actual recipe count
Uses the public DATABASE_URL to bypass the application layer
"""
import psycopg2
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_postgres_directly():
    # Use the public DATABASE_URL from Railway
    database_url = "postgresql://postgres:udQLpljdqTYmESmntwzmwDcOlBVbqlJG@shuttle.proxy.rlwy.net:31331/railway"
    
    print("🔍 DIRECT POSTGRESQL CONNECTION CHECK")
    print("=" * 50)
    
    try:
        # Connect directly to PostgreSQL
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("✅ Connected to PostgreSQL database")
        
        # Check total recipe count
        cursor.execute("SELECT COUNT(*) FROM recipes")
        total_count = cursor.fetchone()[0]
        print(f"📊 Total recipes in PostgreSQL: {total_count}")
        
        # Check if intelligence columns exist
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'recipes' 
            AND column_name IN ('meal_role', 'is_easy', 'time_min')
        """)
        intelligence_columns = cursor.fetchall()
        print(f"🧠 Intelligence columns found: {len(intelligence_columns)}")
        for col in intelligence_columns:
            print(f"   • {col[0]}")
        
        # Check recipes with intelligence data
        if intelligence_columns:
            cursor.execute("SELECT COUNT(*) FROM recipes WHERE meal_role IS NOT NULL")
            classified_count = cursor.fetchone()[0]
            print(f"� Recipes with intelligence data: {classified_count}")
            
            # Show sample data
            cursor.execute("""
                SELECT id, title, meal_role, is_easy, time_min 
                FROM recipes 
                WHERE meal_role IS NOT NULL 
                LIMIT 5
            """)
            samples = cursor.fetchall()
            print(f"\n� Sample classified recipes:")
            for recipe in samples:
                print(f"   ID {recipe[0]}: {recipe[1][:40]}... | {recipe[2]} | Easy: {recipe[3]} | Time: {recipe[4]}min")
        
        # Check first few recipe IDs to understand the data
        cursor.execute("SELECT id, title FROM recipes ORDER BY id LIMIT 10")
        first_recipes = cursor.fetchall()
        print(f"\n🔢 First 10 recipe IDs:")
        for recipe in first_recipes:
            print(f"   ID {recipe[0]}: {recipe[1][:50]}...")
            
        # Check last few recipe IDs
        cursor.execute("SELECT id, title FROM recipes ORDER BY id DESC LIMIT 5")
        last_recipes = cursor.fetchall()
        print(f"\n🔢 Last 5 recipe IDs:")
        for recipe in last_recipes:
            print(f"   ID {recipe[0]}: {recipe[1][:50]}...")
        
        conn.close()
        
        return total_count
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return None

if __name__ == "__main__":
    count = check_postgres_directly()
    
    if count is not None:
        if count >= 700:
            print(f"\n🎉 SUCCESS! Found {count} recipes in PostgreSQL")
            print("✅ The database migration was successful")
            print("✅ Intelligence migration should process all recipes")
        elif count == 100:
            print(f"\n⚠️  Only {count} recipes found - migration may be incomplete")
        else:
            print(f"\n🤔 Found {count} recipes - unexpected count")
