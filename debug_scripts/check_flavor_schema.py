#!/usr/bin/env python3
"""Check database schema for recipe_flavor_profiles table"""

import psycopg2
import os

def check_schema():
    try:
        database_url = 'postgresql://postgres:udQLpljdqTYmESmntwzmwDcOlBVbqlJG@shuttle.proxy.rlwy.net:31331/railway'
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("Checking recipe_flavor_profiles table schema...")
        
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'recipe_flavor_profiles' 
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        
        if columns:
            print("recipe_flavor_profiles table columns:")
            for col_name, data_type in columns:
                print(f"  - {col_name} ({data_type})")
        else:
            print("Table recipe_flavor_profiles not found or has no columns")
            
            # Check what tables exist
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE '%flavor%'
            """)
            
            flavor_tables = cursor.fetchall()
            print(f"\nTables with 'flavor' in name:")
            for table in flavor_tables:
                print(f"  - {table[0]}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schema()
