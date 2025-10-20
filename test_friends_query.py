#!/usr/bin/env python3
"""
Test the /api/friends/list endpoint to see what it returns
"""

import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

def test_friends_query():
    """Test the exact query the API uses"""
    database_url = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    user_id = 11  # YesChef admin
    
    print("🧪 Testing Friends API Query")
    print("=" * 60)
    print(f"User ID: {user_id}\n")
    
    # Run the exact query from the API
    query = """
        SELECT 
            u.id, u.name, u.email,
            f.created_at as friend_since,
            f.updated_at as last_activity
        FROM friendships f
        JOIN users u ON f.friend_id = u.id
        WHERE f.user_id = %s AND f.status = 'accepted'
        ORDER BY u.name
    """
    
    print("📝 Running query:")
    print(query)
    print(f"   Parameters: user_id = {user_id}")
    
    cursor.execute(query, (user_id,))
    friends = cursor.fetchall()
    
    print(f"\n✅ Query returned {len(friends)} friends:")
    
    if friends:
        for friend in friends:
            print(f"\n   Friend #{friend['id']}:")
            print(f"      Name: {friend['name']}")
            print(f"      Email: {friend['email']}")
            print(f"      Friends Since: {friend['friend_since']}")
            print(f"      Last Activity: {friend['last_activity']}")
    else:
        print("\n   ❌ No friends returned by query!")
        print("\n   🔍 Let's check why...")
        
        # Check if friendships exist but don't match the query
        cursor.execute("""
            SELECT * FROM friendships 
            WHERE user_id = %s OR friend_id = %s
        """, (user_id, user_id))
        
        all_friendships = cursor.fetchall()
        print(f"\n   Total friendships involving user {user_id}: {len(all_friendships)}")
        for f in all_friendships:
            print(f"      {dict(f)}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    
    return len(friends)

if __name__ == "__main__":
    count = test_friends_query()
    
    if count == 0:
        print("\n⚠️  PROBLEM FOUND!")
        print("   The query returns 0 friends even though friendships exist.")
        print("   This means the web app won't show any friends.")
        print("\n💡 Possible causes:")
        print("   1. The query only looks for WHERE user_id = 11")
        print("   2. But friendships are bidirectional (both user_id and friend_id)")
        print("   3. Need to query BOTH directions!")
    else:
        print(f"\n✅ Query works! Should return {count} friends to web app.")
