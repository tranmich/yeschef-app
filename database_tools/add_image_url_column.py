"""
Database Migration: Add image_url column to recipes table
Created: 2025-10-29
Purpose: Store optimized local image paths for recipe photos
"""

import os
import sys
import psycopg2
import logging
from pathlib import Path

# Add parent directory to path to import from project
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_env():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        logger.info("✅ Loaded environment variables from .env")
    else:
        logger.warning("⚠️ .env file not found")

def run_migration():
    """Add image_url column to recipes table if it doesn't exist"""
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("❌ DATABASE_URL environment variable not set")
        return False
    
    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        logger.info("🔄 Checking if image_url column exists...")
        
        # Check if column already exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='recipes' AND column_name='image_url'
        """)
        
        if cursor.fetchone():
            logger.info("✅ image_url column already exists, skipping migration")
            conn.close()
            return True
        
        logger.info("📝 Adding image_url column to recipes table...")
        
        # Add the column
        cursor.execute("""
            ALTER TABLE recipes 
            ADD COLUMN image_url TEXT
        """)
        
        conn.commit()
        logger.info("✅ Successfully added image_url column")
        
        # Verify it was added
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name='recipes' AND column_name='image_url'
        """)
        
        result = cursor.fetchone()
        if result:
            logger.info(f"✅ Verified: image_url column exists with type {result[1]}")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("DATABASE MIGRATION: Add image_url column")
    print("="*60 + "\n")
    
    load_env()  # Load .env first
    success = run_migration()
    
    if success:
        print("\n✅ Migration completed successfully!\n")
    else:
        print("\n❌ Migration failed. Check logs for details.\n")
