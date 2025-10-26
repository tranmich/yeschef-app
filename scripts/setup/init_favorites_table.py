"""
Initialize Favorites Table

Creates:
- favorites: Track user's favorite/bookmarked recipes
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection from environment
DATABASE_URL = os.getenv('DATABASE_URL')

def init_favorites_table():
    """Initialize favorites table"""
    
    conn = None
    cursor = None
    
    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("🔗 Connected to database")
        
        # ============================================================================
        # CREATE favorites TABLE
        # ============================================================================
        
        print("\n📋 Creating favorites table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT NOW(),
                UNIQUE(user_id, recipe_id)
            )
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_favorites_user_id 
            ON favorites(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_favorites_recipe_id 
            ON favorites(recipe_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_favorites_created_at 
            ON favorites(created_at DESC)
        """)
        
        print("✅ favorites table created")
        
        # ============================================================================
        # COMMIT
        # ============================================================================
        
        conn.commit()
        print("\n✅ Favorites table created successfully!")
        
        # ============================================================================
        # VERIFY
        # ============================================================================
        
        print("\n🔍 Verifying table...")
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'favorites'
        """)
        
        table = cursor.fetchone()
        if table:
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
    print("🚀 FAVORITES TABLE INITIALIZATION")
    print("="*70)
    
    success = init_favorites_table()
    
    if success:
        print("\n" + "="*70)
        print("✅ FAVORITES TABLE READY!")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("❌ INITIALIZATION FAILED")
        print("="*70)
        exit(1)
