"""
🧪 PANTRY API TEST SUITE
Tests all 10 Phase 4 endpoints on PostgreSQL/Railway

Endpoints tested:
- Get user pantry
- Add item
- Get single item
- Update item
- Delete item
- Get pantry stats
- Search items
- Get by category
- Clear pantry
"""

import requests
import json
import time
from datetime import datetime, timedelta

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
    'item_ids': [],
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
# PANTRY API TESTS
# =============================================================================

def test_pantry_api():
    """Test all pantry endpoints"""
    print_section("🥫 PANTRY API TESTS (10 endpoints)")
    
    # Test 1: Add items to pantry
    print_test("1. Add Pantry Items")
    
    # Add item 1
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    success, data = test_endpoint(
        'POST', '/pantry',
        json={
            'user_id': TEST_USER_ID,
            'name': 'Tomatoes',
            'quantity': 5,
            'unit': 'count',
            'category': 'vegetables',
            'expiry_date': tomorrow,
            'notes': 'From test'
        },
        headers={'Content-Type': 'application/json'}
    )
    
    if success:
        item_id = data.get('data', {}).get('id')
        state['item_ids'].append(item_id)
        print(f"   ✓ Added item ID: {item_id}")
    
    time.sleep(0.5)
    
    # Add item 2
    print_test("2. Add Second Item")
    success, data = test_endpoint(
        'POST', '/pantry',
        json={
            'user_id': TEST_USER_ID,
            'name': 'Onions',
            'quantity': 3,
            'unit': 'count',
            'category': 'vegetables',
            'notes': 'Test item 2'
        },
        headers={'Content-Type': 'application/json'}
    )
    
    if success:
        item_id = data.get('data', {}).get('id')
        state['item_ids'].append(item_id)
        print(f"   ✓ Added item ID: {item_id}")
    
    time.sleep(0.5)
    
    # Test 3: Get user pantry
    print_test("3. Get User Pantry")
    success, data = test_endpoint(
        'GET', f'/pantry/user/{TEST_USER_ID}',
        params={'limit': 10}
    )
    
    if success:
        items = data.get('data', [])
        print(f"   Found {len(items)} pantry items")
    
    time.sleep(0.5)
    
    # Test 4: Get single item
    if state['item_ids']:
        print_test("4. Get Single Pantry Item")
        success, data = test_endpoint(
            'GET', f'/pantry/{state["item_ids"][0]}',
            params={'user_id': TEST_USER_ID}
        )
        
        if success:
            item = data.get('data', {})
            print(f"   Item: {item.get('name')} ({item.get('quantity')} {item.get('unit')})")
        
        time.sleep(0.5)
    
    # Test 5: Update item
    if state['item_ids']:
        print_test("5. Update Pantry Item")
        success, data = test_endpoint(
            'PATCH', f'/pantry/{state["item_ids"][0]}',
            params={'user_id': TEST_USER_ID},
            json={'quantity': 10, 'notes': 'Updated quantity'},
            headers={'Content-Type': 'application/json'}
        )
        
        if success:
            item = data.get('data', {})
            print(f"   ✓ Updated quantity to {item.get('quantity')}")
        
        time.sleep(0.5)
    
    # Test 6: Get pantry stats
    print_test("6. Get Pantry Stats")
    success, data = test_endpoint(
        'GET', '/pantry/stats',
        params={'user_id': TEST_USER_ID}
    )
    
    if success:
        stats = data.get('data', {})
        print(f"   Total items: {stats.get('total_items', 0)}")
        print(f"   Categories: {stats.get('total_categories', 0)}")
        print(f"   Expiring soon: {stats.get('expiring_soon', 0)}")
    
    time.sleep(0.5)
    
    # Test 7: Search items
    print_test("7. Search Pantry Items")
    success, data = test_endpoint(
        'GET', '/pantry/search',
        params={'user_id': TEST_USER_ID, 'q': 'Tomato'}
    )
    
    if success:
        items = data.get('data', [])
        print(f"   Found {len(items)} matching items")
    
    time.sleep(0.5)
    
    # Test 8: Get by category
    print_test("8. Get Items by Category")
    success, data = test_endpoint(
        'GET', '/pantry/category/vegetables',
        params={'user_id': TEST_USER_ID}
    )
    
    if success:
        items = data.get('data', [])
        print(f"   Found {len(items)} vegetables")
    
    time.sleep(0.5)
    
    # Test 9: Delete single item
    if len(state['item_ids']) > 1:
        print_test("9. Delete Pantry Item")
        success, data = test_endpoint(
            'DELETE', f'/pantry/{state["item_ids"][0]}',
            params={'user_id': TEST_USER_ID}
        )
        
        if success:
            print(f"   ✓ Item deleted")
        
        time.sleep(0.5)
    
    # Test 10: Clear pantry
    print_test("10. Clear Pantry")
    success, data = test_endpoint(
        'DELETE', '/pantry/clear',
        params={'user_id': TEST_USER_ID}
    )
    
    if success:
        deleted_count = data.get('deleted_count', 0)
        print(f"   ✓ Cleared {deleted_count} items")
    
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
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL PHASE 4 TESTS PASSED!{Colors.END}")
        print(f"{Colors.GREEN}Pantry API is working perfectly!{Colors.END}")
    else:
        print(f"\n{Colors.YELLOW}⚠️  {state['failed']} test(s) failed - review above for details{Colors.END}")

# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print_section("🚀 PHASE 4 TEST SUITE - PANTRY API")
    print(f"{Colors.BLUE}Testing:{Colors.END} {BASE_URL}")
    print(f"{Colors.BLUE}Time:{Colors.END} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{Colors.BLUE}Test User:{Colors.END} ID {TEST_USER_ID}")
    
    try:
        # Run tests
        test_pantry_api()
        
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
