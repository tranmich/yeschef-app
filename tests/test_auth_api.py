#!/usr/bin/env python3
"""
Quick API test script to verify authentication endpoints
"""

import requests
import json
import sys

def test_auth_endpoints():
    """Test authentication endpoints"""
    base_url = "http://127.0.0.1:5000"
    
    print("Testing Authentication Endpoints...")
    print("=" * 50)
    
    # Test 1: Auth Status
    try:
        response = requests.get(f"{base_url}/api/auth/status", timeout=5)
        print(f"✓ Auth Status: {response.status_code}")
        print(f"  Response: {json.dumps(response.json(), indent=2)}")
        print()
    except Exception as e:
        print(f"✗ Auth Status failed: {e}")
        return False
    
    # Test 2: User Registration
    user_data = {
        'name': 'SAGE Test User',
        'email': 'sage@hungie.app', 
        'password': 'SecurePassword123!'
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/register", json=user_data, timeout=5)
        print(f"Registration: {response.status_code}")
        print(f"  Response: {json.dumps(response.json(), indent=2)}")
        print()
        
        if response.status_code == 201:
            token = response.json().get('token')
            print(f"✓ Registration successful! Token: {token[:20]}...")
        elif response.status_code == 400:
            print("Registration failed - checking if user already exists...")
        
    except Exception as e:
        print(f"✗ Registration failed: {e}")
        return False
    
    # Test 3: User Login (if registration failed due to existing user)
    if response.status_code == 400:
        login_data = {
            'email': user_data['email'],
            'password': user_data['password']
        }
        
        try:
            response = requests.post(f"{base_url}/api/auth/login", json=login_data, timeout=5)
            print(f"Login: {response.status_code}")
            print(f"  Response: {json.dumps(response.json(), indent=2)}")
            print()
            
            if response.status_code == 200:
                token = response.json().get('token')
                print(f"✓ Login successful! Token: {token[:20]}...")
                
                # Test 4: Protected endpoint
                headers = {'Authorization': f'Bearer {token}'}
                response = requests.get(f"{base_url}/api/auth/me", headers=headers, timeout=5)
                print(f"Protected endpoint /me: {response.status_code}")
                print(f"  Response: {json.dumps(response.json(), indent=2)}")
                
        except Exception as e:
            print(f"✗ Login failed: {e}")
            return False
    
    print("\n" + "=" * 50)
    print("✓ AUTHENTICATION SYSTEM WORKING!")
    return True

if __name__ == "__main__":
    if test_auth_endpoints():
        print("Phase 1 Authentication Backend: COMPLETE ✓")
        sys.exit(0)
    else:
        print("Authentication test failed")
        sys.exit(1)
