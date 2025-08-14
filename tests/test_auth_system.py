#!/usr/bin/env python3
"""
Quick test of our authentication endpoints
"""
import requests
import json

def test_auth_endpoints():
    base_url = "http://127.0.0.1:5000/api/auth"
    
    print("🧪 Testing Authentication Endpoints")
    print("=" * 50)
    
    # Test status endpoint
    try:
        response = requests.get(f"{base_url}/status")
        print(f"✅ Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"📝 Response: {json.dumps(data, indent=2)}")
        print()
    except Exception as e:
        print(f"❌ Status test failed: {e}")
        print()
    
    # Test user registration
    try:
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        response = requests.post(f"{base_url}/register", json=user_data)
        print(f"✅ Registration: {response.status_code}")
        if response.status_code in [200, 201, 400]:  # 400 might be "user exists"
            data = response.json()
            print(f"📝 Response: {json.dumps(data, indent=2)}")
        print()
    except Exception as e:
        print(f"❌ Registration test failed: {e}")
        print()
    
    # Test login
    try:
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        response = requests.post(f"{base_url}/login", json=login_data)
        print(f"✅ Login: {response.status_code}")
        if response.status_code in [200, 401]:
            data = response.json()
            print(f"📝 Response: {json.dumps(data, indent=2)}")
            
            # If login successful, test protected endpoint
            if response.status_code == 200 and 'access_token' in data:
                token = data['access_token']
                headers = {'Authorization': f'Bearer {token}'}
                
                me_response = requests.get(f"{base_url}/me", headers=headers)
                print(f"✅ Protected endpoint (/me): {me_response.status_code}")
                if me_response.status_code == 200:
                    me_data = me_response.json()
                    print(f"📝 User data: {json.dumps(me_data, indent=2)}")
        print()
    except Exception as e:
        print(f"❌ Login test failed: {e}")
        print()

if __name__ == "__main__":
    test_auth_endpoints()
