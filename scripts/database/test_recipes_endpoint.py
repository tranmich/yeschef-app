"""
Test the /api/user/recipes endpoint directly to see what it returns
"""

import requests
import json

# Test without authentication
print("=" * 80)
print("🧪 TESTING /api/user/recipes ENDPOINT")
print("=" * 80)

API_URL = "http://localhost:5000"  # Update if different

print(f"\n1️⃣ Testing WITHOUT authentication...")
try:
    response = requests.get(f"{API_URL}/api/user/recipes")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:200]}...")
except Exception as e:
    print(f"   ❌ Error: {e}")

print(f"\n2️⃣ Testing WITH authentication (Bearer token)...")
print(f"   You need to:")
print(f"   1. Log into the web frontend")
print(f"   2. Open browser console (F12)")
print(f"   3. Type: localStorage.getItem('authToken')")
print(f"   4. Copy the token")
print(f"   5. Run this script with the token as argument")
print(f"\n   Example: python scripts/database/test_recipes_endpoint.py YOUR_TOKEN_HERE")

import sys
if len(sys.argv) > 1:
    token = sys.argv[1]
    print(f"\n   Using token: {token[:20]}...")
    
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        response = requests.get(f"{API_URL}/api/user/recipes", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success!")
            print(f"   Recipe count: {len(data.get('data', []))}")
            print(f"   Admin access: {data.get('admin_access', False)}")
            if data.get('data'):
                print(f"   First recipe: {data['data'][0].get('title', 'No title')}")
        else:
            print(f"   ❌ Failed: {response.text[:500]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n" + "=" * 80)
