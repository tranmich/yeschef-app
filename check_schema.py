#!/usr/bin/env python3
"""
Quick script to check the actual PostgreSQL schema for recipes table
"""

import psycopg2
import psycopg2.extras
import os
from urllib.parse import urlparse

def get_db_connection():
    """Get PostgreSQL connection using Railway URL"""
    # Use the same connection string as hungie_server.py
    public_database_url = "postgresql://postgres:udQLpljdqTYmESmntwzmwDcOlBVbqlJG@shuttle.proxy.rlwy.net:31331/railway"
    
    return psycopg2.connect(public_database_url)

def check_recipes_schema():
    """Check the actual schema of the recipes table"""
    try:
        conn = get_db_connection()
        if not conn:
            return
            
        cursor = conn.cursor()
        
        # Get column information for recipes table
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'recipes'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        
        print("📊 RECIPES TABLE SCHEMA:")
        print("=" * 50)
        for col in columns:
            col_name, data_type, nullable, default = col
            print(f"  {col_name:<20} | {data_type:<15} | {'NULL' if nullable == 'YES' else 'NOT NULL':<8} | {default or ''}")
        
        print("\n" + "=" * 50)
        print(f"✅ Found {len(columns)} columns in recipes table")
        
        # Check if difficulty column exists
        difficulty_exists = any(col[0] == 'difficulty' for col in columns)
        print(f"🔍 'difficulty' column exists: {'✅ YES' if difficulty_exists else '❌ NO'}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking schema: {e}")

if __name__ == "__main__":
    check_recipes_schema()
