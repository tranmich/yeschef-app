#!/usr/bin/env python3
"""
🍳 Community Sharing Migration Script
Adds community sharing columns to existing recipes table
"""
import os
import psycopg2
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    # Connect to database using DATABASE_URL (Railway)
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("🗄️ Adding community sharing columns to recipes table...")
        
        # Add community sharing columns
        cursor.execute('ALTER TABLE recipes ADD COLUMN IF NOT EXISTS is_community_shared BOOLEAN DEFAULT FALSE')
        cursor.execute('ALTER TABLE recipes ADD COLUMN IF NOT EXISTS shared_at TIMESTAMP NULL')
        cursor.execute('ALTER TABLE recipes ADD COLUMN IF NOT EXISTS community_title TEXT NULL')
        cursor.execute('ALTER TABLE recipes ADD COLUMN IF NOT EXISTS community_description TEXT NULL')
        cursor.execute('ALTER TABLE recipes ADD COLUMN IF NOT EXISTS community_background TEXT DEFAULT \'default\'')
        cursor.execute('ALTER TABLE recipes ADD COLUMN IF NOT EXISTS community_icon TEXT DEFAULT \'🍽️\'')
        
        print("📊 Adding performance indexes...")
        
        # Add indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_recipes_community_shared ON recipes (is_community_shared) WHERE is_community_shared = TRUE')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_recipes_shared_at ON recipes (shared_at) WHERE shared_at IS NOT NULL')
        
        conn.commit()
        print('✅ Community sharing migration completed successfully!')
        print('🎉 Your database is now ready for recipe sharing!')
        
    except Exception as e:
        print(f'❌ Migration failed: {e}')
        return False
    finally:
        if 'conn' in locals():
            conn.close()
    
    return True

if __name__ == '__main__':
    main()