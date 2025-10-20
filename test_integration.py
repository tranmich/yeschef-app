"""
Test v2 API integration with hungie_server.py
Verifies that v2 routes work alongside old routes
"""

import sys
import requests
import time

print("=" * 70)
print("TESTING V2 API INTEGRATION")
print("=" * 70)

# Test with local server
BASE_URL = "http://localhost:5000"

def test_endpoint(method, endpoint, description, expected_status=200):
    """Test an endpoint and return success/failure"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n{description}")
    print(f"  {method} {endpoint}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json={}, timeout=5)
        else:
            print(f"  ❌ Unsupported method: {method}")
            return False
        
        print(f"  Status: {response.status_code}")
        
        if response.status_code == expected_status or response.status_code == 200:
            print(f"  ✅ Success!")
            return True
        else:
            print(f"  ⚠️ Expected {expected_status}, got {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"  ❌ Cannot connect to server!")
        print(f"  Please start hungie_server.py first:")
        print(f"  python hungie_server.py")
        return None
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

# Wait a moment for server to be ready
print("\nChecking if server is running...")
time.sleep(1)

# Test old endpoints (should still work!)
print("\n" + "=" * 70)
print("TESTING OLD ENDPOINTS (Should still work!)")
print("=" * 70)

old_tests = []
old_tests.append(test_endpoint("GET", "/api/direct-test", "1. Old direct test endpoint"))

# Test v2 endpoints (new!)
print("\n" + "=" * 70)
print("TESTING NEW V2 ENDPOINTS")
print("=" * 70)

v2_tests = []
v2_tests.append(test_endpoint("GET", "/api/v2/health", "1. V2 Health check"))
v2_tests.append(test_endpoint("GET", "/api/v2/users/11", "2. Get user by ID"))
v2_tests.append(test_endpoint("GET", "/api/v2/users/11/stats", "3. Get user stats"))
v2_tests.append(test_endpoint("GET", "/api/v2/recipes/user/11/stats", "4. Get recipes with stats (THE STAR!)"))
v2_tests.append(test_endpoint("GET", "/api/v2/recipes/user/11?page=1&per_page=5", "5. Get paginated recipes"))
v2_tests.append(test_endpoint("GET", "/api/v2/recipes/search?user_id=11&q=chicken", "6. Search recipes"))

# Check if any test couldn't connect
if None in old_tests or None in v2_tests:
    print("\n" + "=" * 70)
    print("❌ SERVER NOT RUNNING")
    print("=" * 70)
    print("\nPlease start the server first:")
    print("  cd \"d:\\Mik\\Downloads\\Me Hungie\"")
    print("  python hungie_server.py")
    print("\nThen run this test again:")
    print("  python test_integration.py")
    sys.exit(1)

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

old_passed = sum(1 for x in old_tests if x == True)
old_total = len(old_tests)

v2_passed = sum(1 for x in v2_tests if x == True)
v2_total = len(v2_tests)

print(f"\nOld endpoints: {old_passed}/{old_total} passed")
print(f"V2 endpoints:  {v2_passed}/{v2_total} passed")

if old_passed == old_total and v2_passed == v2_total:
    print("\n✅ ALL TESTS PASSED!")
    print("\nBoth old and new endpoints are working!")
    print("Your v2 API is ready to deploy! 🚀")
    sys.exit(0)
else:
    print("\n⚠️ Some tests failed")
    print("Check the errors above for details")
    sys.exit(1)
