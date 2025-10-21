"""
Add Profile Fields to Users Table

Adds profile fields:
- avatar_url: URL to user's avatar image
- bio: User biography/about text
- location: User's location
- dietary_preferences: JSON array of dietary preferences
- cooking_level: User's cooking skill level
- updated_at: Last update timestamp
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection from environment
DATABASE_URL = os.getenv('DATABASE_URL')

def add_profile_fields():
    """Add profile fields to users table"""
    
    conn = None
    cursor = None
    
    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("🔗 Connected to database")
        
        # ============================================================================
        # ADD PROFILE FIELDS
        # ============================================================================
        
        print("\n📋 Adding profile fields to users table...")
        
        # Add avatar_url
        cursor.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS avatar_url TEXT
        """)
        print("  ✅ Added avatar_url")
        
        # Add bio
        cursor.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS bio TEXT
        """)
        print("  ✅ Added bio")
        
        # Add location
        cursor.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS location VARCHAR(255)
        """)
        print("  ✅ Added location")
        
        # Add dietary_preferences
        cursor.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS dietary_preferences JSONB DEFAULT '[]'::jsonb
        """)
        print("  ✅ Added dietary_preferences")
        
        # Add cooking_level
        cursor.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS cooking_level VARCHAR(50)
        """)
        print("  ✅ Added cooking_level")
        
        # Add updated_at
        cursor.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW()
        """)
        print("  ✅ Added updated_at")
        
        # Create index on updated_at
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_updated_at 
            ON users(updated_at DESC)
        """)
        print("  ✅ Created index on updated_at")
        
        # ============================================================================
        # COMMIT
        # ============================================================================
        
        conn.commit()
        print("\n✅ Profile fields added successfully!")
        
        # ============================================================================
        # VERIFY
        # ============================================================================
        
        print("\n🔍 Verifying columns...")
        
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name IN ('avatar_url', 'bio', 'location', 'dietary_preferences', 'cooking_level', 'updated_at')
            ORDER BY column_name
        """)
        
        columns = cursor.fetchall()
        print(f"\n📊 Found {len(columns)} profile columns:")
        for col in columns:
            print(f"   ✅ {col['column_name']}: {col['data_type']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("\n🔌 Database connection closed")


if __name__ == '__main__':
    print("="*70)
    print("🚀 ADD PROFILE FIELDS TO USERS TABLE")
    print("="*70)
    
    success = add_profile_fields()
    
    if success:
        print("\n" + "="*70)
        print("✅ PROFILE FIELDS READY!")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("❌ MIGRATION FAILED")
        print("="*70)
        exit(1)
