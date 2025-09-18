#!/usr/bin/env python3
"""
Create collaborations table in PostgreSQL
"""

import psycopg2
import psycopg2.extras
import logging

logger = logging.getLogger(__name__)

def get_db_connection():
    """Get PostgreSQL database connection"""
    public_database_url = "postgresql://postgres:udQLpljdqTYmESmntwzmwDcOlBVbqlJG@shuttle.proxy.rlwy.net:31331/railway"
    
    try:
        print("🔄 Connecting to PostgreSQL...")
        conn = psycopg2.connect(public_database_url)
        conn.cursor_factory = psycopg2.extras.RealDictCursor
        print("✅ Connected to PostgreSQL database successfully")
        return conn
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        raise Exception(f"Database connection failed: {str(e)}")

def create_collaborations_table():
    """Create the collaborations table in PostgreSQL"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Create collaborations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collaborations (
                id SERIAL PRIMARY KEY,
                resource_type VARCHAR(20) NOT NULL CHECK (resource_type IN ('meal_plan', 'grocery_list')),
                resource_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                invited_by INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                permission_level VARCHAR(10) NOT NULL DEFAULT 'editor' CHECK (permission_level IN ('viewer', 'editor')),
                status VARCHAR(10) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'removed')),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                
                -- Ensure unique collaboration per user per resource
                UNIQUE(resource_type, resource_id, user_id)
            );
        """)
        
        # Create indexes for better performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_collaborations_user_resource 
            ON collaborations(user_id, resource_type, status);
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_collaborations_resource 
            ON collaborations(resource_type, resource_id, status);
        """)
        
        conn.commit()
        print("✅ Collaborations table created successfully in PostgreSQL!")
        print("✅ Indexes created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating collaborations table: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_collaborations_table()