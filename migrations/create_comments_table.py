"""
Database migration: Create comments table
Run this to add comments support to whiteboards
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def migrate():
    """Create comments table"""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    try:
        # Create comments table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                whiteboard_id INTEGER NOT NULL,  -- References wb table
                object_type VARCHAR(50) NOT NULL,  -- 'recipe', 'meal_plan', 'grocery_list', etc.
                object_id VARCHAR(100) NOT NULL,   -- The ID of the object being commented on
                content TEXT NOT NULL,
                parent_id INTEGER REFERENCES comments(id) ON DELETE CASCADE,  -- For threaded replies
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create indexes for performance
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_comments_whiteboard 
            ON comments(whiteboard_id);
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_comments_object 
            ON comments(whiteboard_id, object_type, object_id);
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_comments_user 
            ON comments(user_id);
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_comments_parent 
            ON comments(parent_id);
        """)
        
        conn.commit()
        print("✅ Comments table created successfully!")
        print("✅ Indexes created successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    migrate()
