#!/usr/bin/env python3
"""
Debug friends visibility issue
Check what friends data exists and why it's not showing up in web app
"""

import sqlite3
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Get database connection based on environment"""
    database_url = os.getenv('DATABASE_URL')
    
    if database_url and database_url.startswith('postgresql'):
        # PostgreSQL connection
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        return conn, 'postgresql'
    else:
        # SQLite connection
        db_path = os.getenv('DATABASE_PATH', 'hungie.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn, 'sqlite'

def debug_friends_data():
    """Debug friends data and table structure"""
    
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    
    print("🔍 DEBUGGING FRIENDS VISIBILITY ISSUE")
    print("=" * 60)
    
    # First, let's see what tables exist with 'friend' in the name
    print("\n📋 Tables containing 'friend':")
    try:
        if db_type == 'postgresql':
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name ILIKE '%friend%'
                ORDER BY table_name
            """)
        else:
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name LIKE '%friend%'
                ORDER BY name
            """)
        
        tables = cursor.fetchall()
        for table in tables:
            table_name = table[0] if db_type == 'postgresql' else table['name']
            print(f"   • {table_name}")
            
    except Exception as e:
        print(f"   ❌ Error listing tables: {e}")
    
    # Check users table to understand user structure
    print("\n👤 Users in database:")
    try:
        cursor.execute("SELECT id, name, email FROM users ORDER BY id LIMIT 10")
        users = cursor.fetchall()
        for user in users:
            if db_type == 'postgresql':
                print(f"   • ID: {user[0]}, Name: {user[1]}, Email: {user[2]}")
            else:
                print(f"   • ID: {user['id']}, Name: {user['name']}, Email: {user['email']}")
    except Exception as e:
        print(f"   ❌ Error reading users: {e}")
    
    # Now let's check different possible friends table structures
    friends_tables_to_check = ['friends', 'friendships', 'friend_requests', 'user_friends']
    
    for table_name in friends_tables_to_check:
        print(f"\n🔍 Checking table: {table_name}")
        try:
            # First check if table exists and get its structure
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
            columns = [desc[0] for desc in cursor.description]
            print(f"   📊 Columns: {', '.join(columns)}")
            
            # Get all data from the table
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            print(f"   📈 Total rows: {len(rows)}")
            
            if rows:
                print("   📄 Sample data:")
                for i, row in enumerate(rows[:5]):  # Show first 5 rows
                    if db_type == 'postgresql':
                        row_data = dict(zip(columns, row))
                    else:
                        row_data = dict(row)
                    print(f"      Row {i+1}: {row_data}")
                    
        except Exception as e:
            if "no such table" in str(e).lower() or "does not exist" in str(e).lower():
                print(f"   ⚪ Table doesn't exist")
            else:
                print(f"   ❌ Error: {e}")
    
    # Check what the backend friends endpoint is actually looking for
    print(f"\n🔍 Checking what the backend friends endpoint expects:")
    print("   The /api/friends/list endpoint looks for:")
    print("   • Table: 'friendships'")
    print("   • Joins with users table on friend_id")
    print("   • Expects columns: user_id, friend_id, status, created_at, updated_at")
    
    # Check if we need to migrate existing friends data
    print(f"\n🔄 Migration needed?")
    try:
        # Check if there's a 'friends' table with data but no 'friendships' table
        cursor.execute("SELECT COUNT(*) FROM friends")
        friends_count = cursor.fetchone()[0] if db_type == 'sqlite' else cursor.fetchone()[0]
        
        try:
            cursor.execute("SELECT COUNT(*) FROM friendships") 
            friendships_count = cursor.fetchone()[0] if db_type == 'sqlite' else cursor.fetchone()[0]
        except:
            friendships_count = 0
            print("   ❗ 'friendships' table doesn't exist or is empty")
        
        print(f"   • 'friends' table has {friends_count} rows")
        print(f"   • 'friendships' table has {friendships_count} rows")
        
        if friends_count > 0 and friendships_count == 0:
            print("   🚨 MIGRATION NEEDED: Data exists in 'friends' but not 'friendships'")
        
    except Exception as e:
        print(f"   ❌ Error checking migration: {e}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("🎯 Debug complete!")

if __name__ == "__main__":
    debug_friends_data()