#!/usr/bin/env python3
"""
Check what friends-related tables exist in the database
and compare with what the API is querying
"""

import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

def check_database_tables():
    """Check what tables exist in the database"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return
    
    conn = psycopg2.connect(database_url)
    conn.autocommit = True
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    print("🔍 Checking PostgreSQL Database Tables")
    print("=" * 60)
    
    # Get all table names
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)
    
    all_tables = [row['table_name'] for row in cursor.fetchall()]
    
    print(f"\n📋 All tables ({len(all_tables)}):")
    for table in all_tables:
        print(f"   • {table}")
    
    # Check for friend-related tables
    print("\n\n👥 Friend-related tables:")
    friend_tables = [t for t in all_tables if 'friend' in t.lower()]
    
    if not friend_tables:
        print("   ❌ No friend-related tables found!")
    else:
        for table in friend_tables:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            count = cursor.fetchone()['count']
            print(f"   ✅ {table} ({count} records)")
            
            # Show structure
            cursor.execute(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{table}'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            print(f"      Columns: {', '.join([c['column_name'] for c in columns])}")
    
    # Check what the mobile app might be using - look for 'friends' singular
    print("\n\n🔍 Checking 'friends' table (mobile app might use this):")
    if 'friends' in all_tables:
        cursor.execute("SELECT COUNT(*) as count FROM friends")
        count = cursor.fetchone()['count']
        print(f"   ✅ 'friends' table exists ({count} records)")
        
        # Show structure
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'friends'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        print(f"   Columns: {', '.join([c['column_name'] for c in columns])}")
        
        # Show sample data
        cursor.execute("SELECT * FROM friends LIMIT 5")
        friends_data = cursor.fetchall()
        if friends_data:
            print(f"\n   Sample data:")
            for friend in friends_data:
                print(f"      {dict(friend)}")
    else:
        print("   ❌ 'friends' table does NOT exist")
    
    # Check for user 11's friends in whatever table exists
    print("\n\n👤 Looking for User ID 11's friends:")
    
    # Try different possible table names
    possible_tables = ['friends', 'friendships', 'friend_requests']
    
    for table in possible_tables:
        if table in all_tables:
            print(f"\n   Checking '{table}' table:")
            
            # Try different column name patterns
            try:
                cursor.execute(f"""
                    SELECT * FROM {table} 
                    WHERE user_id = 11 OR friend_user_id = 11 OR friend_id = 11
                    LIMIT 10
                """)
                results = cursor.fetchall()
                if results:
                    print(f"      ✅ Found {len(results)} records:")
                    for row in results:
                        print(f"         {dict(row)}")
                else:
                    print(f"      No records found for user 11")
            except Exception as e:
                print(f"      Error querying: {e}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ Database inspection complete!")

if __name__ == "__main__":
    check_database_tables()
