#!/usr/bin/env python3
"""
Check SQLite Database Content
Quick script to inspect the hungie.db database structure and content
"""

import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def inspect_database():
    """Inspect the SQLite database"""
    try:
        conn = sqlite3.connect('hungie.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        logger.info(f"📊 Tables found: {[table[0] for table in tables]}")
        
        # Check recipes table
        if any(table[0] == 'recipes' for table in tables):
            cursor.execute("PRAGMA table_info(recipes)")
            columns = cursor.fetchall()
            logger.info(f"📝 Recipes table columns: {[col[1] for col in columns]}")
            
            # Count recipes
            cursor.execute("SELECT COUNT(*) FROM recipes")
            count = cursor.fetchone()[0]
            logger.info(f"🍽️ Total recipes: {count}")
            
            # Show sample recipes
            cursor.execute("SELECT title, source, category FROM recipes LIMIT 5")
            samples = cursor.fetchall()
            logger.info("📖 Sample recipes:")
            for i, recipe in enumerate(samples, 1):
                logger.info(f"  {i}. {recipe[0]} (Source: {recipe[1]}, Category: {recipe[2]})")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"❌ Database inspection error: {e}")

if __name__ == "__main__":
    inspect_database()
