"""
Initialize Pantry Table

Creates:
- pantry_items: Track user's pantry inventory
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection from environment
DATABASE_URL = os.getenv('DATABASE_URL')

def init_pantry_table():
    """Initialize pantry_items table"""
    
    conn = None
    cursor = None
    
    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("🔗 Connected to database")
        
        # ============================================================================
        # CREATE pantry_items TABLE
        # ============================================================================
        
        print("\n📋 Creating pantry_items table...")
        
        # Drop table if it exists (for clean migration)
        cursor.execute("DROP TABLE IF EXISTS pantry_items CASCADE")
        
        cursor.execute("""
            CREATE TABLE pantry_items (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                name VARCHAR(255) NOT NULL,
                quantity DECIMAL(10, 2) DEFAULT 1,
                unit VARCHAR(50) DEFAULT 'unit',
                category VARCHAR(100) DEFAULT 'other',
                expiry_date DATE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_pantry_user_id 
            ON pantry_items(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_pantry_category 
            ON pantry_items(category)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_pantry_expiry 
            ON pantry_items(expiry_date)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_pantry_name 
            ON pantry_items(name)
        """)
        
        print("✅ pantry_items table created")
        
        # ============================================================================
        # COMMIT
        # ============================================================================
        
        conn.commit()
        print("\n✅ Pantry table created successfully!")
        
        # ============================================================================
        # VERIFY
        # ============================================================================
        
        print("\n🔍 Verifying table...")
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'pantry_items'
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
    print("🚀 PANTRY TABLE INITIALIZATION")
    print("="*70)
    
    success = init_pantry_table()
    
    if success:
        print("\n" + "="*70)
        print("✅ PANTRY TABLE READY!")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("❌ INITIALIZATION FAILED")
        print("="*70)
        exit(1)
