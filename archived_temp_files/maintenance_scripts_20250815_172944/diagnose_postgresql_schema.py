#!/usr/bin/env python3
"""
Quick diagnostic to check PostgreSQL column schema
"""
import os
import sys
import psycopg2
from urllib.parse import urlparse

def check_postgresql_schema():
    """Check what columns exist in PostgreSQL recipes table"""
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("No DATABASE_URL found in environment")
        return
        
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Get column information
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'recipes'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print(f"PostgreSQL recipes table has {len(columns)} columns:")
        for col_name, data_type in columns:
            print(f"  - {col_name}: {data_type}")
            
        # Also check with PRAGMA table_info equivalent
        cursor.execute("SELECT * FROM recipes LIMIT 0;")
        col_names = [desc[0] for desc in cursor.description]
        print(f"\nColumn names from query description: {col_names}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error checking PostgreSQL schema: {e}")

if __name__ == "__main__":
    check_postgresql_schema()
