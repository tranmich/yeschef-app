"""
Initialize Recipe Imports Table

Creates:
- recipe_imports: Track recipe import attempts and history
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection from environment
DATABASE_URL = os.getenv('DATABASE_URL')

def init_recipe_imports_table():
    """Initialize recipe_imports table"""
    
    conn = None
    cursor = None
    
    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("🔗 Connected to database")
        
        # ============================================================================
        # CREATE recipe_imports TABLE
        # ============================================================================
        
        print("\n📋 Creating recipe_imports table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recipe_imports (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                source_url TEXT NOT NULL,
                recipe_id INTEGER REFERENCES recipes(id) ON DELETE SET NULL,
                status VARCHAR(50) NOT NULL DEFAULT 'success',
                error_message TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_recipe_imports_user_id 
            ON recipe_imports(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_recipe_imports_status 
            ON recipe_imports(status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_recipe_imports_created_at 
            ON recipe_imports(created_at DESC)
        """)
        
        print("✅ recipe_imports table created")
        
        # ============================================================================
        # COMMIT
        # ============================================================================
        
        conn.commit()
        print("\n✅ Recipe imports table created successfully!")
        
        # ============================================================================
        # VERIFY
        # ============================================================================
        
        print("\n🔍 Verifying table...")
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'recipe_imports'
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
    print("🚀 RECIPE IMPORTS TABLE INITIALIZATION")
    print("="*70)
    
    success = init_recipe_imports_table()
    
    if success:
        print("\n" + "="*70)
        print("✅ RECIPE IMPORTS TABLE READY!")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("❌ INITIALIZATION FAILED")
        print("="*70)
        exit(1)
