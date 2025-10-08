#!/usr/bin/env python3
import sqlite3
import os

def check_database_tables():
    """Check what tables exist in the database"""
    db_path = os.path.join(os.path.dirname(__file__), 'hungie.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("📋 Tables in database:")
    for table in tables:
        print(f"  - {table[0]}")
        
        # Get schema for each table
        cursor.execute(f"PRAGMA table_info({table[0]})")
        columns = cursor.fetchall()
        for col in columns:
            print(f"    {col[1]} ({col[2]})")
        print()
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_database_tables()