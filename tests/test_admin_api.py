#!/usr/bin/env python3
"""
Test Admin API Endpoint
Test if the admin user detection is working on the backend
"""

import requests
import json

def test_admin_api():
    """Test admin API functionality"""
    base_url = "http://localhost:5000"
    
    print("🧪 TESTING ADMIN API FUNCTIONALITY")
    print("="*50)
    
    print("\n📝 MANUAL TEST INSTRUCTIONS:")
    print("1. Login to the app with tran.mich@gmail.com")
    print("2. Open browser Developer Tools (F12)")
    print("3. Go to Application/Storage → Local Storage")
    print("4. Copy the 'authToken' value")
    print("5. Run this test with the token")
    
    # Get token from user
    token = input("\n🔑 Paste your authToken here: ").strip()
    
    if not token:
        print("❌ No token provided")
        return False
    
    print(f"\n🔍 Testing with token: {token[:20]}...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Test the user recipes endpoint
        print("\n📊 Testing /api/user/recipes...")
        response = requests.get(f"{base_url}/api/user/recipes", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Response:")
            print(f"   Success: {data.get('success')}")
            print(f"   Admin Access: {data.get('admin_access')}")
            print(f"   Recipe Count: {data.get('count')}")
            print(f"   Message: {data.get('message')}")
            
            if data.get('admin_access'):
                print(f"🔧 ADMIN DETECTED! Should see all recipes in database")
            else:
                print(f"👤 Regular user detected")
                print(f"⚠️ If you logged in with tran.mich@gmail.com, this is a problem")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    return True

if __name__ == "__main__":
    test_admin_api()
