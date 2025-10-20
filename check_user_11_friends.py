#!/usr/bin/env python3
"""
Check User 11's friends in the friendships table
"""

import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

def check_user_friends():
    """Check what friends user 11 has"""
    database_url = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(database_url)
    conn.autocommit = True
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    print("🔍 Checking User 11's Friends")
    print("=" * 60)
    
    # Check friendships table structure
    print("\n📋 Friendships table structure:")
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'friendships'
        ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()
    for col in columns:
        print(f"   • {col['column_name']}: {col['data_type']}")
    
    # Get all friendships for user 11
    print("\n\n👥 All friendships involving User 11:")
    cursor.execute("""
        SELECT * FROM friendships 
        WHERE user_id = 11 OR friend_id = 11
    """)
    friendships = cursor.fetchall()
    
    if friendships:
        print(f"   Found {len(friendships)} friendship records:")
        for friendship in friendships:
            print(f"      {dict(friendship)}")
    else:
        print("   ❌ No friendships found for user 11")
    
    # Get user details for the friends
    if friendships:
        print("\n\n📇 Friend Details:")
        friend_ids = set()
        for f in friendships:
            if f['user_id'] == 11:
                friend_ids.add(f['friend_id'])
            else:
                friend_ids.add(f['user_id'])
        
        for friend_id in friend_ids:
            cursor.execute("""
                SELECT id, name, email, created_at 
                FROM users 
                WHERE id = %s
            """, (friend_id,))
            user = cursor.fetchone()
            if user:
                print(f"   Friend ID {friend_id}:")
                print(f"      Name: {user['name']}")
                print(f"      Email: {user['email']}")
                print(f"      Joined: {user['created_at']}")
    
    # Check what the API endpoint is querying
    print("\n\n🔍 What the API endpoint queries:")
    print("   Looking at hungie_server.py line ~5870...")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    check_user_friends()
