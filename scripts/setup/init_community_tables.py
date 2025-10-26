"""
Initialize Community Tables for Community Recipe Sharing

Creates:
- recipe_shares: Track which recipes are shared to community
- community_likes: Track likes on community recipes
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection from environment
DATABASE_URL = os.getenv('DATABASE_URL')

def init_community_tables():
    """Initialize community tables"""
    
    conn = None
    cursor = None
    
    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("🔗 Connected to database")
        
        # ============================================================================
        # 1. CREATE recipe_shares TABLE
        # ============================================================================
        
        print("\n📋 Creating recipe_shares table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recipe_shares (
                id SERIAL PRIMARY KEY,
                recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                is_shared BOOLEAN DEFAULT TRUE,
                shared_at TIMESTAMP DEFAULT NOW(),
                created_at TIMESTAMP DEFAULT NOW(),
                UNIQUE(recipe_id, user_id)
            )
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_recipe_shares_recipe_id 
            ON recipe_shares(recipe_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_recipe_shares_user_id 
            ON recipe_shares(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_recipe_shares_is_shared 
            ON recipe_shares(is_shared)
        """)
        
        print("✅ recipe_shares table created")
        
        # ============================================================================
        # 2. CREATE community_likes TABLE
        # ============================================================================
        
        print("\n📋 Creating community_likes table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS community_likes (
                id SERIAL PRIMARY KEY,
                recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT NOW(),
                UNIQUE(recipe_id, user_id)
            )
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_community_likes_recipe_id 
            ON community_likes(recipe_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_community_likes_user_id 
            ON community_likes(user_id)
        """)
        
        print("✅ community_likes table created")
        
        # ============================================================================
        # COMMIT
        # ============================================================================
        
        conn.commit()
        print("\n✅ All community tables created successfully!")
        
        # ============================================================================
        # VERIFY
        # ============================================================================
        
        print("\n🔍 Verifying tables...")
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('recipe_shares', 'community_likes')
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print(f"\n📊 Found {len(tables)} tables:")
        for table in tables:
            print(f"   ✅ {table['table_name']}")
        
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
    print("🚀 COMMUNITY TABLES INITIALIZATION")
    print("="*70)
    
    success = init_community_tables()
    
    if success:
        print("\n" + "="*70)
        print("✅ COMMUNITY TABLES READY!")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("❌ INITIALIZATION FAILED")
        print("="*70)
        exit(1)
