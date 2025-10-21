"""
🧪 SYSTEM & ADMIN API TEST SUITE
Tests all 8 Phase 6 endpoints on PostgreSQL/Railway

Endpoints tested:
- System health check
- System stats
- System analytics
- System cleanup
- Get all users (admin)
- Get user activity (admin)
- Get inactive users (admin)
- Process voice command (placeholder)
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
        
        if response.status_code in [200, 201, 503]:  # 503 is ok for health checks
            data = response.json()
            # System health can return success=False if unhealthy, that's ok
            if data.get('success') or (response.status_code == 503 and 'status' in data.get('data', {})):
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
# SYSTEM & ADMIN API TESTS
# =============================================================================

def test_system_api():
    """Test all system and admin endpoints"""
    print_section("⚙️ SYSTEM & ADMIN API TESTS (8 endpoints)")
    
    # Test 1: Health check
    print_test("1. System Health Check")
    success, data = test_endpoint('GET', '/system/health')
    
    if success:
        status = data.get('data', {}).get('status', 'unknown')
        print(f"   System status: {status}")
    
    time.sleep(0.5)
    
    # Test 2: System stats
    print_test("2. Get System Stats")
    success, data = test_endpoint('GET', '/system/stats')
    
    if success:
        stats = data.get('data', {})
        print(f"   Total users: {stats.get('total_users', 0)}")
        print(f"   Total recipes: {stats.get('total_recipes', 0)}")
        print(f"   Total favorites: {stats.get('total_favorites', 0)}")
    
    time.sleep(0.5)
    
    # Test 3: System analytics
    print_test("3. Get System Analytics")
    success, data = test_endpoint('GET', '/system/analytics')
    
    if success:
        analytics = data.get('data', {})
        categories = analytics.get('popular_categories', [])
        print(f"   Popular categories: {len(categories)}")
    
    time.sleep(0.5)
    
    # Test 4: System cleanup
    print_test("4. System Cleanup")
    success, data = test_endpoint('POST', '/system/cleanup')
    
    if success:
        print(f"   ✓ Cleanup completed")
    
    time.sleep(0.5)
    
    # Test 5: Get all users (admin)
    print_test("5. Get All Users (Admin)")
    success, data = test_endpoint(
        'GET', '/system/admin/users',
        params={'limit': 10}
    )
    
    if success:
        users = data.get('data', [])
        print(f"   Found {len(users)} users")
    
    time.sleep(0.5)
    
    # Test 6: Get user activity (admin)
    print_test("6. Get User Activity (Admin)")
    success, data = test_endpoint(
        'GET', f'/system/admin/users/{TEST_USER_ID}/activity'
    )
    
    if success:
        activity = data.get('data', {})
        print(f"   User: {activity.get('name', 'N/A')}")
        print(f"   Recipes: {activity.get('total_recipes', 0)}")
        print(f"   Favorites: {activity.get('total_favorites', 0)}")
    
    time.sleep(0.5)
    
    # Test 7: Get inactive users (admin)
    print_test("7. Get Inactive Users (Admin)")
    success, data = test_endpoint(
        'GET', '/system/admin/users/inactive',
        params={'days': 30}
    )
    
    if success:
        inactive = data.get('data', [])
        print(f"   Found {len(inactive)} inactive users")
    
    time.sleep(0.5)
    
    # Test 8: Process voice command (placeholder)
    print_test("8. Process Voice Command (Placeholder)")
    success, data = test_endpoint(
        'POST', '/system/voice/command',
        json={
            'user_id': TEST_USER_ID,
            'command': 'Find me a pasta recipe'
        },
        headers={'Content-Type': 'application/json'}
    )
    
    if success:
        response_text = data.get('data', {}).get('response', '')
        print(f"   ✓ Response: {response_text}")
    
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
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL PHASE 6 TESTS PASSED!{Colors.END}")
        print(f"{Colors.GREEN}System & Admin API is working perfectly!{Colors.END}")
        print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}🏆 REFACTORING 100% COMPLETE! 🏆{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}{'='*70}{Colors.END}")
    else:
        print(f"\n{Colors.YELLOW}⚠️  {state['failed']} test(s) failed - review above for details{Colors.END}")

# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print_section("🚀 PHASE 6 TEST SUITE - SYSTEM & ADMIN API")
    print(f"{Colors.BLUE}Testing:{Colors.END} {BASE_URL}")
    print(f"{Colors.BLUE}Time:{Colors.END} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{Colors.BLUE}Test User:{Colors.END} ID {TEST_USER_ID}")
    
    try:
        # Run tests
        test_system_api()
        
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
