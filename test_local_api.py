"""
🧪 LOCAL TEST - Friends & Households API v2
Test against local server (http://localhost:5000)
This will verify the code works before Railway deployment
"""

import requests
import json
import time
from datetime import datetime

# Configuration - LOCAL SERVER
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api/v2"

print("=" * 70)
print("🧪 TESTING LOCALLY (localhost:5000)")
print("=" * 70)
print(f"Make sure hungie_server.py is running!")
print()

# Quick health check
try:
    response = requests.get(f"{API_BASE}/health", timeout=2)
    if response.status_code == 200:
        print("✅ Server is running!")
        print()
    else:
        print("⚠️  Server responded but with error")
        print()
except:
    print("❌ ERROR: Server is not running!")
    print("   Please start the server with: python hungie_server.py")
    print()
    exit(1)

# Test data
test_data = {
    'user1_id': 1,
    'user2_id': 2,
    'household_id': None
}

passed = 0
failed = 0

def test_endpoint(name, method, url, **kwargs):
    """Generic endpoint tester"""
    global passed, failed
    
    print(f"🧪 {name}...")
    try:
        if method == 'GET':
            response = requests.get(url, **kwargs)
        elif method == 'POST':
            response = requests.post(url, **kwargs)
        elif method == 'PUT':
            response = requests.put(url, **kwargs)
        elif method == 'DELETE':
            response = requests.delete(url, **kwargs)
        
        if response.status_code in [200, 201]:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ PASS - {response.status_code}")
                passed += 1
                return True, data
            else:
                print(f"   ❌ FAIL - API Error: {data.get('error')}")
                failed += 1
                return False, data
        else:
            print(f"   ❌ FAIL - HTTP {response.status_code}")
            failed += 1
            return False, None
    except Exception as e:
        print(f"   ❌ FAIL - Exception: {e}")
        failed += 1
        return False, None

# Run tests
print("=" * 70)
print("👥 FRIENDS API TESTS")
print("=" * 70)

test_endpoint(
    "Get friends for user 1",
    "GET",
    f"{API_BASE}/friends/user/{test_data['user1_id']}"
)

test_endpoint(
    "Get friend requests for user 1",
    "GET",
    f"{API_BASE}/friends/requests/user/{test_data['user1_id']}"
)

test_endpoint(
    "Check friendship status",
    "GET",
    f"{API_BASE}/friends/status",
    params={'user_id': test_data['user1_id'], 'other_user_id': test_data['user2_id']}
)

print()
print("=" * 70)
print("🏠 HOUSEHOLDS API TESTS")
print("=" * 70)

test_endpoint(
    "Get households for user 1",
    "GET",
    f"{API_BASE}/households/user/{test_data['user1_id']}"
)

success, data = test_endpoint(
    "Create household",
    "POST",
    f"{API_BASE}/households",
    json={
        'name': f'Test Household {int(time.time())}',
        'created_by': test_data['user1_id'],
        'description': 'Test household from local test'
    },
    headers={'Content-Type': 'application/json'}
)

if success and data:
    household_id = data.get('data', {}).get('household', {}).get('id')
    if household_id:
        test_data['household_id'] = household_id
        test_endpoint(
            f"Get household {household_id} members",
            "GET",
            f"{API_BASE}/households/{household_id}/members",
            params={'user_id': test_data['user1_id']}
        )

# Results
print()
print("=" * 70)
print("📊 RESULTS")
print("=" * 70)
total = passed + failed
print(f"Total Tests: {total}")
print(f"✅ Passed: {passed}")
print(f"❌ Failed: {failed}")
print()

if failed == 0:
    print("🎉 ALL TESTS PASSED! Code is ready for Railway deployment!")
else:
    print(f"⚠️  {failed} test(s) failed - needs fixing")

print("=" * 70)
