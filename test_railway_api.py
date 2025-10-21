"""
Test Friends & Households API v2 on PostgreSQL (Railway)
Tests all endpoints with real database operations
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://yeschefapp-production.up.railway.app"
API_BASE = f"{BASE_URL}/api/v2"

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(message):
    print(f"\n{Colors.BLUE}🧪 TEST: {message}{Colors.END}")

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.YELLOW}ℹ️  {message}{Colors.END}")

def print_section(title):
    print(f"\n{'='*60}")
    print(f"{Colors.BLUE}{title}{Colors.END}")
    print('='*60)

# Test state
test_data = {
    'user1_id': 10,  # Real user from database
    'user2_id': 12,  # Real user from database
    'household_id': None
}

def test_get_friends(user_id):
    """Test: Get user's friends"""
    print_test(f"Getting friends for user {user_id}")
    
    response = requests.get(f"{API_BASE}/friends/user/{user_id}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            friends = data.get('data', {}).get('friends', [])
            print_success(f"Got {len(friends)} friends")
            return True
        else:
            print_error(f"API error: {data.get('error')}")
            return False
    else:
        print_error(f"HTTP {response.status_code}")
        return False

def test_get_friend_requests(user_id):
    """Test: Get friend requests"""
    print_test(f"Getting friend requests for user {user_id}")
    
    response = requests.get(f"{API_BASE}/friends/requests/user/{user_id}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            incoming = len(data.get('data', {}).get('incoming', []))
            outgoing = len(data.get('data', {}).get('outgoing', []))
            print_success(f"Got {incoming} incoming, {outgoing} outgoing requests")
            return True
        else:
            print_error(f"API error: {data.get('error')}")
            return False
    else:
        print_error(f"HTTP {response.status_code}")
        return False

def test_friendship_status(user_id, other_user_id):
    """Test: Get friendship status"""
    print_test(f"Checking status between {user_id} and {other_user_id}")
    
    response = requests.get(
        f"{API_BASE}/friends/status",
        params={'user_id': user_id, 'other_user_id': other_user_id}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            status = data.get('data', {}).get('status')
            print_success(f"Status: {status}")
            return True
        else:
            print_error(f"API error: {data.get('error')}")
            return False
    else:
        print_error(f"HTTP {response.status_code}")
        return False

def test_get_households(user_id):
    """Test: Get user's households"""
    print_test(f"Getting households for user {user_id}")
    
    response = requests.get(f"{API_BASE}/households/user/{user_id}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            households = data.get('data', {}).get('households', [])
            print_success(f"Got {len(households)} households")
            return True
        else:
            print_error(f"API error: {data.get('error')}")
            return False
    else:
        print_error(f"HTTP {response.status_code}")
        return False

def test_create_household(user_id):
    """Test: Create household"""
    household_name = f"Test Household {int(time.time())}"
    print_test(f"Creating household '{household_name}'")
    
    payload = {
        'name': household_name,
        'created_by': user_id,
        'description': 'Test household from API v2'
    }
    
    response = requests.post(
        f"{API_BASE}/households",
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code in [200, 201]:
        data = response.json()
        if data.get('success'):
            household_id = data.get('data', {}).get('household', {}).get('id')
            print_success(f"Created! ID: {household_id}")
            test_data['household_id'] = household_id
            return True
        else:
            print_error(f"API error: {data.get('error')}")
            return False
    else:
        print_error(f"HTTP {response.status_code}")
        return False

def test_get_household_members(household_id, user_id):
    """Test: Get household members"""
    print_test(f"Getting members for household {household_id}")
    
    response = requests.get(
        f"{API_BASE}/households/{household_id}/members",
        params={'user_id': user_id}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            members = data.get('data', {}).get('members', [])
            print_success(f"Got {len(members)} members")
            return True
        else:
            print_error(f"API error: {data.get('error')}")
            return False
    else:
        print_error(f"HTTP {response.status_code}")
        return False

def run_all_tests():
    """Run all tests"""
    print_section("🚀 FRIENDS & HOUSEHOLDS API v2 TEST SUITE")
    print_info(f"Testing: {BASE_URL}")
    print_info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    passed = 0
    failed = 0
    
    # Friends API Tests
    print_section("👥 FRIENDS API TESTS")
    
    if test_get_friends(test_data['user1_id']):
        passed += 1
    else:
        failed += 1
    time.sleep(0.5)
    
    if test_get_friend_requests(test_data['user1_id']):
        passed += 1
    else:
        failed += 1
    time.sleep(0.5)
    
    if test_friendship_status(test_data['user1_id'], test_data['user2_id']):
        passed += 1
    else:
        failed += 1
    time.sleep(0.5)
    
    # Households API Tests
    print_section("🏠 HOUSEHOLDS API TESTS")
    
    if test_get_households(test_data['user1_id']):
        passed += 1
    else:
        failed += 1
    time.sleep(0.5)
    
    if test_create_household(test_data['user1_id']):
        passed += 1
    else:
        failed += 1
    time.sleep(0.5)
    
    if test_data['household_id']:
        if test_get_household_members(test_data['household_id'], test_data['user1_id']):
            passed += 1
        else:
            failed += 1
    
    # Results
    print_section("📊 TEST RESULTS")
    total = passed + failed
    print(f"\nTotal: {total}")
    print_success(f"Passed: {passed}")
    if failed > 0:
        print_error(f"Failed: {failed}")
    
    if failed == 0:
        print_success("\n🎉 ALL TESTS PASSED!")
    else:
        print_error(f"\n⚠️  {failed} test(s) failed")
    
    return failed == 0

if __name__ == '__main__':
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except Exception as e:
        print_error(f"\nError: {e}")
        exit(1)
