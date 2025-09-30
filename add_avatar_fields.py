#!/usr/bin/env python3
"""
Add avatar fields to users table for profile customization
"""

import psycopg2
import os
from dotenv import load_dotenv

def add_avatar_fields():
    """Add avatar_background and avatar_icon fields to users table"""
    
    load_dotenv()
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ No DATABASE_URL found in environment")
        return False
    
    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name IN ('avatar_background', 'avatar_icon')
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        # Add avatar_background column if it doesn't exist
        if 'avatar_background' not in existing_columns:
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN avatar_background TEXT DEFAULT 'default'
            """)
            print("✅ Added avatar_background column")
        else:
            print("ℹ️ avatar_background column already exists")
        
        # Add avatar_icon column if it doesn't exist
        if 'avatar_icon' not in existing_columns:
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN avatar_icon TEXT DEFAULT '🍎'
            """)
            print("✅ Added avatar_icon column")
        else:
            print("ℹ️ avatar_icon column already exists")
        
        conn.commit()
        
        # Verify the changes
        cursor.execute("""
            SELECT column_name, data_type, column_default
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name IN ('avatar_background', 'avatar_icon')
            ORDER BY column_name
        """)
        
        print("\n📋 Avatar columns in users table:")
        for row in cursor.fetchall():
            print(f"  {row[0]} ({row[1]}) - Default: {row[2]}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Avatar fields migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    add_avatar_fields()