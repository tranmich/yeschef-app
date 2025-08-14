#!/usr/bin/env python3
"""
Recipe Migration Script: SQLite to PostgreSQL
Migrates all recipes from local hungie.db to Railway PostgreSQL database
"""

import sqlite3
import psycopg2
import psycopg2.extras
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_sqlite_connection():
    """Connect to local SQLite database"""
    try:
        conn = sqlite3.connect('hungie.db')
        conn.row_factory = sqlite3.Row
        logger.info("✅ Connected to SQLite database")
        return conn
    except Exception as e:
        logger.error(f"❌ SQLite connection error: {e}")
        raise

def get_postgresql_connection():
    """Connect to Railway PostgreSQL database"""
    try:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            # Try to get from Railway variables (for local testing)
            import subprocess
            try:
                result = subprocess.run(['railway', 'variables'], capture_output=True, text=True)
                # This is a fallback - in production DATABASE_URL should be available
                logger.warning("DATABASE_URL not found in environment variables")
                return None
            except:
                logger.error("Cannot connect to PostgreSQL - DATABASE_URL not available")
                return None
        
        conn = psycopg2.connect(database_url)
        conn.cursor_factory = psycopg2.extras.RealDictCursor
        logger.info("✅ Connected to PostgreSQL database")
        return conn
    except Exception as e:
        logger.error(f"❌ PostgreSQL connection error: {e}")
        return None

def get_recipes_from_sqlite():
    """Fetch all recipes from SQLite database"""
    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM recipes ORDER BY id")
        recipes = cursor.fetchall()
        
        conn.close()
        logger.info(f"📊 Found {len(recipes)} recipes in SQLite database")
        return recipes
    except Exception as e:
        logger.error(f"❌ Error reading from SQLite: {e}")
        return []

def insert_recipe_to_postgresql(conn, recipe):
    """Insert a single recipe into PostgreSQL"""
    try:
        cursor = conn.cursor()
        
        # Convert SQLite row to dictionary
        recipe_data = dict(recipe)
        
        # Map SQLite fields to PostgreSQL fields
        # SQLite has: id, book_id, title, page_number, servings, hands_on_time, total_time, 
        #             ingredients, instructions, description, url, date_saved, why_this_works, category, chapter, chapter_number
        # PostgreSQL expects: title, description, ingredients, instructions, image_url, source, category, flavor_profile, created_at
        
        # Create a description combining available fields
        description_parts = []
        if recipe_data.get('description'):
            description_parts.append(recipe_data['description'])
        if recipe_data.get('why_this_works'):
            description_parts.append(f"Why this works: {recipe_data['why_this_works']}")
        if recipe_data.get('servings'):
            description_parts.append(f"Servings: {recipe_data['servings']}")
        if recipe_data.get('total_time'):
            description_parts.append(f"Total time: {recipe_data['total_time']}")
        
        combined_description = " | ".join(description_parts) if description_parts else None
        
        # Create source information
        source_parts = []
        if recipe_data.get('book_id'):
            source_parts.append(f"Book ID: {recipe_data['book_id']}")
        if recipe_data.get('chapter'):
            source_parts.append(f"Chapter: {recipe_data['chapter']}")
        if recipe_data.get('page_number'):
            source_parts.append(f"Page: {recipe_data['page_number']}")
        
        source = " | ".join(source_parts) if source_parts else "Recipe Collection"
        
        # Insert recipe (excluding id since PostgreSQL uses SERIAL)
        cursor.execute("""
            INSERT INTO recipes (title, description, ingredients, instructions, image_url, source, category, flavor_profile, created_at)
            VALUES (%(title)s, %(description)s, %(ingredients)s, %(instructions)s, %(image_url)s, %(source)s, %(category)s, %(flavor_profile)s, %(created_at)s)
            RETURNING id
        """, {
            'title': recipe_data.get('title'),
            'description': combined_description,
            'ingredients': recipe_data.get('ingredients'),
            'instructions': recipe_data.get('instructions'),
            'image_url': recipe_data.get('url'),  # Use URL as image_url
            'source': source,
            'category': recipe_data.get('category'),
            'flavor_profile': None,  # Will be populated later by AI analysis
            'created_at': recipe_data.get('date_saved')
        })
        
        new_id = cursor.fetchone()[0]
        logger.debug(f"✅ Inserted recipe: {recipe_data.get('title')} (new ID: {new_id})")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error inserting recipe '{recipe.get('title', 'Unknown')}': {e}")
        return False

def migrate_recipes():
    """Main migration function"""
    logger.info("🚀 Starting recipe migration from SQLite to PostgreSQL")
    
    # Get recipes from SQLite
    recipes = get_recipes_from_sqlite()
    if not recipes:
        logger.warning("⚠️ No recipes found in SQLite database")
        return
    
    # Connect to PostgreSQL
    pg_conn = get_postgresql_connection()
    if not pg_conn:
        logger.error("❌ Cannot connect to PostgreSQL database")
        return
    
    try:
        # Migrate recipes
        success_count = 0
        error_count = 0
        
        for recipe in recipes:
            if insert_recipe_to_postgresql(pg_conn, recipe):
                success_count += 1
            else:
                error_count += 1
        
        # Commit all changes
        pg_conn.commit()
        logger.info(f"✅ Migration completed! {success_count} recipes migrated successfully, {error_count} errors")
        
        # Verify migration
        cursor = pg_conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM recipes")
        total_recipes = cursor.fetchone()[0]
        logger.info(f"📊 PostgreSQL database now contains {total_recipes} recipes")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        pg_conn.rollback()
    
    finally:
        pg_conn.close()

if __name__ == "__main__":
    migrate_recipes()
