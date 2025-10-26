"""
Initialize Social Features Database Tables
Run this to create friends, households, and related tables
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Get DATABASE_URL
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ DATABASE_URL not found in environment!")
    exit(1)

print(f"🔄 Connecting to PostgreSQL...")
print(f"📍 URL: {DATABASE_URL[:50]}...")

try:
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("✅ Connected!")
    print()
    print("=" * 70)
    print("Creating Social Features Tables...")
    print("=" * 70)
    
    # 1. Friend Requests Table
    print("\n1. Creating friend_requests table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS friend_requests (
            id SERIAL PRIMARY KEY,
            requester_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            recipient_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            message TEXT,
            status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'declined')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(requester_id, recipient_id)
        )
    """)
    print("   ✅ friend_requests table created")
    
    # 2. Friendships Table
    print("\n2. Creating friendships table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS friendships (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            friend_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            status VARCHAR(20) DEFAULT 'accepted' CHECK (status IN ('accepted', 'blocked')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, friend_id)
        )
    """)
    print("   ✅ friendships table created")
    
    # 3. Households Table
    print("\n3. Creating households table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS households (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            created_by INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("   ✅ households table created")
    
    # 4. Household Members Table
    print("\n4. Creating household_members table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS household_members (
            id SERIAL PRIMARY KEY,
            household_id INTEGER NOT NULL REFERENCES households(id) ON DELETE CASCADE,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            role VARCHAR(50) DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'member')),
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(household_id, user_id)
        )
    """)
    print("   ✅ household_members table created")
    
    # 5. Create indexes
    print("\n5. Creating indexes...")
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_friend_requests_recipient ON friend_requests(recipient_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_friendships_user ON friendships(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_friendships_friend ON friendships(friend_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_households_created_by ON households(created_by)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_household_members_household ON household_members(household_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_household_members_user ON household_members(user_id)")
        print("   ✅ Indexes created")
    except Exception as e:
        print(f"   ⚠️ Index creation warning (may already exist): {e}")
    
    print()
    print("=" * 70)
    print("🎉 ALL SOCIAL TABLES CREATED SUCCESSFULLY!")
    print("=" * 70)
    print()
    print("Tables created:")
    print("  ✅ friend_requests")
    print("  ✅ friendships")
    print("  ✅ households")
    print("  ✅ household_members")
    print()
    print("🚀 Ready for Friends & Households API testing!")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
