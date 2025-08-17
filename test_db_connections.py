#!/usr/bin/env python3
"""
Test both database URLs to see which one works for YesChefapp service
"""
import psycopg2

def test_database_connections():
    print("🔍 TESTING DATABASE CONNECTIONS")
    print("=" * 40)
    
    # Test 1: Internal Railway URL (what YesChefapp is using)
    internal_url = "postgresql://postgres:udQLpljdqTYmESmntwzmwDcOlBVbqlJG@postgres.railway.internal:5432/railway"
    print("\n📡 Test 1: Internal Railway URL")
    try:
        conn = psycopg2.connect(internal_url)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM recipes")
        count = cursor.fetchone()[0]
        print(f"   ✅ SUCCESS: {count} recipes found via internal URL")
        conn.close()
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
    
    # Test 2: Public Railway URL (what worked for us)
    public_url = "postgresql://postgres:udQLpljdqTYmESmntwzmwDcOlBVbqlJG@shuttle.proxy.rlwy.net:31331/railway"
    print("\n🌍 Test 2: Public Railway URL")
    try:
        conn = psycopg2.connect(public_url)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM recipes")
        count = cursor.fetchone()[0]
        print(f"   ✅ SUCCESS: {count} recipes found via public URL")
        conn.close()
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
    
    print("\n💡 RECOMMENDATION:")
    print("If internal URL fails but public URL works, YesChefapp service")
    print("needs to use the public DATABASE_URL instead of internal one.")

if __name__ == "__main__":
    test_database_connections()
