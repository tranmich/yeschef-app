#!/usr/bin/env python3
"""
Test the friends API endpoint directly to see why friends aren't showing
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_friends_endpoint():
    """Test the friends endpoint with and without authentication"""
    print("🧪 Testing Friends API Endpoint")
    print("=" * 50)
    
    # Test without authentication first 
    print("\n1. Testing WITHOUT authentication:")
    try:
        response = requests.get(f"{BASE_URL}/api/friends/list", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test with fake authentication 
    print("\n2. Testing WITH fake token:")
    try:
        headers = {"Authorization": "Bearer fake_token"}
        response = requests.get(f"{BASE_URL}/api/friends/list", headers=headers, timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test login endpoint to see how to get a real token
    print("\n3. Testing login endpoint:")
    try:
        login_data = {
            "email": "tran.mich@gmail.com",
            "password": "test_password"  # This might not work, just testing
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data, timeout=5)
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Response: {result}")
        
        # If login successful, try friends endpoint with real token
        if response.status_code == 200 and 'token' in result:
            print("\n4. Testing friends with REAL token:")
            headers = {"Authorization": f"Bearer {result['token']}"}
            friends_response = requests.get(f"{BASE_URL}/api/friends/list", headers=headers, timeout=5)
            print(f"   Status: {friends_response.status_code}")
            friends_result = friends_response.json()
            print(f"   Friends found: {len(friends_result.get('friends', []))}")
            for friend in friends_result.get('friends', []):
                print(f"      • {friend.get('name')} ({friend.get('email')})")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Friends API Test Complete!")
    print("\nPossible issues:")
    print("1. User not logged in on web app")
    print("2. Token not being sent with requests")
    print("3. Frontend not calling the API")
    print("4. Authentication middleware issue")

if __name__ == "__main__":
    test_friends_endpoint()