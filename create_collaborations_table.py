#!/usr/bin/env python3
"""
Create collaborations table for meal plan and grocery list sharing
"""

import sqlite3
import os

def get_db_connection():
    """Get SQLite database connection"""
    db_path = os.path.join(os.path.dirname(__file__), 'hungie.db')
    return sqlite3.connect(db_path)

def create_collaborations_table():
    """Create the collaborations table"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Create collaborations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collaborations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resource_type TEXT NOT NULL CHECK (resource_type IN ('meal_plan', 'grocery_list')),
                resource_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                invited_by INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                permission_level TEXT NOT NULL DEFAULT 'editor' CHECK (permission_level IN ('viewer', 'editor')),
                status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'removed')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
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
        
        # Check if owner_user_id column exists in meal_plans
        cursor.execute("PRAGMA table_info(meal_plans)")
        meal_plans_columns = [row[1] for row in cursor.fetchall()]
        
        if 'owner_user_id' not in meal_plans_columns:
            cursor.execute("""
                ALTER TABLE meal_plans 
                ADD COLUMN owner_user_id INTEGER REFERENCES users(id);
            """)
            
            # Update existing records to set owner (assuming user_id is the owner)
            cursor.execute("""
                UPDATE meal_plans SET owner_user_id = user_id 
                WHERE owner_user_id IS NULL AND user_id IS NOT NULL;
            """)
        
        # Check if owner_user_id column exists in grocery_lists
        cursor.execute("PRAGMA table_info(grocery_lists)")
        grocery_lists_columns = [row[1] for row in cursor.fetchall()]
        
        if 'owner_user_id' not in grocery_lists_columns:
            cursor.execute("""
                ALTER TABLE grocery_lists 
                ADD COLUMN owner_user_id INTEGER REFERENCES users(id);
            """)
            
            # Update existing records to set owner (assuming user_id is the owner)
            cursor.execute("""
                UPDATE grocery_lists SET owner_user_id = user_id 
                WHERE owner_user_id IS NULL AND user_id IS NOT NULL;
            """)
        
        conn.commit()
        print("✅ Collaborations table created successfully!")
        print("✅ Indexes created successfully!")
        print("✅ Owner columns added/updated successfully!")
        
    except Exception as e:
        print(f"❌ Error creating collaborations table: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_collaborations_table()