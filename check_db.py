#!/usr/bin/env python3
"""
Check database contents and migrate to PostgreSQL
"""
import sqlite3
import os

def check_sqlite_db(db_path):
    """Check SQLite database contents"""
    if not os.path.exists(db_path):
        print(f"Database {db_path} does not exist")
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables in {db_path}: {tables}")
        
        if ('recipes',) in tables:
            cursor.execute("SELECT COUNT(*) FROM recipes;")
            count = cursor.fetchone()[0]
            print(f"Recipe count: {count}")
            
            if count > 0:
                # Get sample recipes
                cursor.execute("SELECT title, source FROM recipes LIMIT 5;")
                samples = cursor.fetchall()
                print(f"Sample recipes: {samples}")
                return conn
        
        conn.close()
        return None
        
    except Exception as e:
        print(f"Error checking {db_path}: {e}")
        return None

# Check available databases
databases = ['test.db', 'scripts/book_parsing/recipe_books.db']

for db in databases:
    print(f"\n=== Checking {db} ===")
    conn = check_sqlite_db(db)
    if conn:
        conn.close()
