#!/usr/bin/env python3
"""
🔍 Database Source Checker
==========================
"""

import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()

def check_database_sources():
    try:
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            db_url = "postgresql://postgres:bBPQiSOwjkCnYdydFUcQKXeiFGFdIsgh@junction.proxy.rlwy.net:40067/railway"
        
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        print("🔍 CHECKING DATABASE SOURCES")
        print("=" * 40)
        
        # Get distinct sources
        cursor.execute("SELECT DISTINCT source, COUNT(*) FROM recipes GROUP BY source ORDER BY COUNT(*) DESC")
        sources = cursor.fetchall()
        
        print("Recipe sources:")
        for source, count in sources:
            print(f"  {source}: {count:,} recipes")
        
        # Check for ATK patterns
        cursor.execute("""
            SELECT DISTINCT source FROM recipes 
            WHERE source ILIKE '%atk%' OR source ILIKE '%america%' OR source ILIKE '%test%' OR source ILIKE '%kitchen%'
            ORDER BY source
        """)
        atk_sources = cursor.fetchall()
        
        if atk_sources:
            print(f"\n🍳 ATK-related sources:")
            for source in atk_sources:
                print(f"  {source[0]}")
        
        # Get sample recent recipes
        cursor.execute("SELECT id, title, source FROM recipes ORDER BY id DESC LIMIT 5")
        recent = cursor.fetchall()
        
        print(f"\n📝 Recent recipes:")
        for recipe_id, title, source in recent:
            print(f"  {recipe_id}: {title[:40]}... ({source})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_database_sources()
