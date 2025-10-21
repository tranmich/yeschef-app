"""
🧪 PROFILE API TEST SUITE
Tests all 6 Phase 3 endpoints on PostgreSQL/Railway

Endpoints tested:
- Get profile
- Update profile
- Upload avatar
- Get avatar
- Delete avatar
- Get profile stats
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://yeschefapp-production.up.railway.app"
API_BASE = f"{BASE_URL}/api/v2"

# Test with real user ID from database
TEST_USER_ID = 10

# Colors
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_section(title):
    print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.END}")
    print(f"{Colors.BOLD}{'='*70}{Colors.END}")

def print_test(name):
    print(f"\n{Colors.YELLOW}🧪 {name}{Colors.END}")

def print_pass():
    print(f"   {Colors.GREEN}✅ PASS{Colors.END}")

def print_fail(reason):
    print(f"   {Colors.RED}❌ FAIL: {reason}{Colors.END}")

# Test state
state = {
    'passed': 0,
    'failed': 0
}

def test_endpoint(method, path, **kwargs):
    """Generic endpoint tester"""
    url = f"{API_BASE}{path}"
    
    try:
        if method == 'GET':
            response = requests.get(url, **kwargs)
        elif method == 'POST':
            response = requests.post(url, **kwargs)
        elif method == 'PATCH':
            response = requests.patch(url, **kwargs)
        elif method == 'DELETE':
            response = requests.delete(url, **kwargs)
        
        if response.status_code in [200, 201]:
            data = response.json()
            if data.get('success'):
                state['passed'] += 1
                print_pass()
                return True, data
            else:
                state['failed'] += 1
                print_fail(f"API returned success=false: {data.get('error', 'Unknown')}")
                return False, data
        else:
            state['failed'] += 1
            print_fail(f"HTTP {response.status_code}")
            try:
                print(f"   Response: {response.json()}")
            except:
                print(f"   Response: {response.text[:200]}")
            return False, None
    except Exception as e:
        state['failed'] += 1
        print_fail(f"Exception: {str(e)[:50]}")
        return False, None

# =============================================================================
# PROFILE API TESTS
# =============================================================================

def test_profile_api():
    """Test all profile endpoints"""
    print_section("👤 PROFILE API TESTS (6 endpoints)")
    
    # Test 1: Get profile
    print_test("1. Get User Profile")
    success, data = test_endpoint(
        'GET', f'/profile/{TEST_USER_ID}'
    )
    
    if success:
        profile = data.get('data', {})
        print(f"   Name: {profile.get('name', 'N/A')}")
        print(f"   Email: {profile.get('email', 'N/A')}")
    
    time.sleep(0.5)
    
    # Test 2: Update profile
    print_test("2. Update Profile")
    success, data = test_endpoint(
        'PATCH', f'/profile/{TEST_USER_ID}',
        json={
            'bio': f'Test bio updated at {int(time.time())}',
            'location': 'Test City, Test Country',
            'cooking_level': 'intermediate'
        },
        headers={'Content-Type': 'application/json'}
    )
    
    if success:
        profile = data.get('data', {})
        print(f"   ✓ Bio: {profile.get('bio', 'N/A')[:50]}...")
        print(f"   ✓ Location: {profile.get('location', 'N/A')}")
        print(f"   ✓ Cooking Level: {profile.get('cooking_level', 'N/A')}")
    
    time.sleep(0.5)
    
    # Test 3: Upload avatar (mock base64 data)
    print_test("3. Upload Avatar")
    mock_avatar = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    
    success, data = test_endpoint(
        'POST', f'/profile/{TEST_USER_ID}/avatar',
        json={
            'avatar_data': mock_avatar,
            'filename': 'test_avatar.png'
        },
        headers={'Content-Type': 'application/json'}
    )
    
    if success:
        print(f"   ✓ Avatar uploaded successfully")
    
    time.sleep(0.5)
    
    # Test 4: Get avatar
    print_test("4. Get Avatar")
    success, data = test_endpoint(
        'GET', f'/profile/{TEST_USER_ID}/avatar'
    )
    
    if success:
        avatar_url = data.get('data', {}).get('avatar_url')
        if avatar_url:
            print(f"   ✓ Avatar URL exists ({len(avatar_url)} chars)")
        else:
            print(f"   ⚠ No avatar URL")
    
    time.sleep(0.5)
    
    # Test 5: Get profile stats
    print_test("5. Get Profile Stats")
    success, data = test_endpoint(
        'GET', f'/profile/{TEST_USER_ID}/stats'
    )
    
    if success:
        stats = data.get('data', {})
        print(f"   Recipes: {stats.get('total_recipes', 0)}")
        print(f"   Favorites: {stats.get('total_favorites', 0)}")
        print(f"   Shared: {stats.get('total_shared', 0)}")
        print(f"   Friends: {stats.get('total_friends', 0)}")
    
    time.sleep(0.5)
    
    # Test 6: Delete avatar
    print_test("6. Delete Avatar")
    success, data = test_endpoint(
        'DELETE', f'/profile/{TEST_USER_ID}/avatar'
    )
    
    if success:
        print(f"   ✓ Avatar deleted successfully")
    
    time.sleep(0.5)

# =============================================================================
# SUMMARY
# =============================================================================

def print_summary():
    """Print test summary"""
    print_section("📊 TEST SUMMARY")
    
    total = state['passed'] + state['failed']
    success_rate = (state['passed'] / total * 100) if total > 0 else 0
    
    print(f"\n{Colors.BOLD}Total Tests:{Colors.END} {total}")
    print(f"{Colors.GREEN}✅ Passed:{Colors.END} {state['passed']}")
    if state['failed'] > 0:
        print(f"{Colors.RED}❌ Failed:{Colors.END} {state['failed']}")
    print(f"\n{Colors.BOLD}Success Rate:{Colors.END} {success_rate:.1f}%")
    
    if state['failed'] == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL PHASE 3 TESTS PASSED!{Colors.END}")
        print(f"{Colors.GREEN}Profile API is working perfectly!{Colors.END}")
    else:
        print(f"\n{Colors.YELLOW}⚠️  {state['failed']} test(s) failed - review above for details{Colors.END}")

# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print_section("🚀 PHASE 3 TEST SUITE - PROFILE API")
    print(f"{Colors.BLUE}Testing:{Colors.END} {BASE_URL}")
    print(f"{Colors.BLUE}Time:{Colors.END} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{Colors.BLUE}Test User:{Colors.END} ID {TEST_USER_ID}")
    
    try:
        # Run tests
        test_profile_api()
        
        # Summary
        print_summary()
        
        # Exit code
        exit(0 if state['failed'] == 0 else 1)
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.RED}Tests interrupted by user{Colors.END}")
        exit(1)
    except Exception as e:
        print(f"\n\n{Colors.RED}Unexpected error: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        exit(1)
