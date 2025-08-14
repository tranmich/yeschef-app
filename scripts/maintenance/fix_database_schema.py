#!/usr/bin/env python3
"""
Database Schema Checker and Fixer
"""

import sqlite3
import os

def check_database_schema():
    """Check the current database schema"""
    
    db_path = 'hungie.db'
    if not os.path.exists(db_path):
        print("Database doesn't exist yet")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("Database Tables:")
    print("=" * 40)
    
    for table in tables:
        table_name = table[0]
        print(f"\nTable: {table_name}")
        
        # Get table structure
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        for col in columns:
            print(f"  {col[1]} {col[2]} {'NOT NULL' if col[3] else ''} {'PRIMARY KEY' if col[5] else ''}")
    
    conn.close()

def fix_user_preferences_table():
    """Drop and recreate user_preferences table with correct schema"""
    
    db_path = 'hungie.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Fixing user_preferences table...")
    
    # Drop existing table
    cursor.execute('DROP TABLE IF EXISTS user_preferences')
    
    # Recreate with correct schema
    cursor.execute('''
        CREATE TABLE user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            dietary_restrictions TEXT, -- JSON array
            allergies TEXT, -- JSON array  
            caloric_needs INTEGER,
            nutritional_goals TEXT, -- JSON object
            preferred_cuisines TEXT, -- JSON array
            cooking_skill_level TEXT DEFAULT 'beginner',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✓ user_preferences table fixed")

if __name__ == "__main__":
    print("Checking database schema...")
    check_database_schema()
    
    print("\nFixing schema issues...")
    fix_user_preferences_table()
    
    print("\nRechecking schema...")
    check_database_schema()
