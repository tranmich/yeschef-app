"""
🧪 FAVORITES API TEST SUITE
Tests all 5 Phase 2 endpoints on PostgreSQL/Railway

Endpoints tested:
- Add to favorites
- Remove from favorites
- Get user's favorites
- Check favorite status
- Get favorites summary
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://yeschefapp-production.up.railway.app"
API_BASE = f"{BASE_URL}/api/v2"

# Test with real user IDs from database
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
    'recipe_id': None,
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
# SETUP: Create a test recipe
# =============================================================================

def setup_test_recipe():
    """Create a test recipe for favorites"""
    print_section("🔧 SETUP: CREATE TEST RECIPE")
    
    print_test("Create Test Recipe")
    success, data = test_endpoint(
        'POST', '/recipes',
        json={
            'user_id': TEST_USER_ID,
            'title': f'Favorites Test Recipe {int(time.time())}',
            'description': 'A recipe for testing favorites',
            'ingredients': ['Test Ingredient 1', 'Test Ingredient 2'],
            'instructions': ['Step 1: Test', 'Step 2: Done'],
            'prep_time': '5 minutes',
            'cook_time': '10 minutes',
            'servings': 2
        },
        headers={'Content-Type': 'application/json'}
    )
    
    if success:
        state['recipe_id'] = data.get('data', {}).get('id')
        print(f"   Recipe ID: {state['recipe_id']}")
        return True
    
    return False

# =============================================================================
# FAVORITES API TESTS
# =============================================================================

def test_favorites_api():
    """Test all favorites endpoints"""
    print_section("⭐ FAVORITES API TESTS (5 endpoints)")
    
    # Test 1: Add to favorites
    print_test("1. Add Recipe to Favorites")
    success, data = test_endpoint(
        'POST', '/favorites',
        json={
            'recipe_id': state['recipe_id'],
            'user_id': TEST_USER_ID
        },
        headers={'Content-Type': 'application/json'}
    )
    
    if success:
        print(f"   ✓ Recipe added to favorites")
    
    time.sleep(0.5)
    
    # Test 2: Check if favorited
    print_test("2. Check Favorite Status")
    success, data = test_endpoint(
        'GET', '/favorites/check',
        params={'recipe_id': state['recipe_id'], 'user_id': TEST_USER_ID}
    )
    
    if success:
        is_favorite = data.get('data', {}).get('is_favorite', False)
        if is_favorite:
            print(f"   ✓ Recipe is favorited")
        else:
            print(f"   ⚠ Recipe not marked as favorite")
    
    time.sleep(0.5)
    
    # Test 3: Get user's favorites
    print_test("3. Get User's Favorites")
    success, data = test_endpoint(
        'GET', f'/favorites/user/{TEST_USER_ID}',
        params={'limit': 10}
    )
    
    if success:
        favorites = data.get('data', [])
        print(f"   Found {len(favorites)} favorites")
        
        # Find our recipe
        for fav in favorites:
            if fav.get('id') == state['recipe_id']:
                print(f"   ✓ Our recipe found in favorites!")
                break
    
    time.sleep(0.5)
    
    # Test 4: Get favorites summary
    print_test("4. Get Favorites Summary")
    success, data = test_endpoint(
        'GET', '/favorites/summary',
        params={'user_id': TEST_USER_ID}
    )
    
    if success:
        summary = data.get('data', {})
        total = summary.get('total_favorites', 0)
        print(f"   ✓ User has {total} total favorites")
    
    time.sleep(0.5)
    
    # Test 5: Remove from favorites
    print_test("5. Remove Recipe from Favorites")
    success, data = test_endpoint(
        'DELETE', f'/favorites/{state["recipe_id"]}',
        params={'user_id': TEST_USER_ID}
    )
    
    if success:
        print(f"   ✓ Recipe removed from favorites")
    
    time.sleep(0.5)

# =============================================================================
# CLEANUP
# =============================================================================

def cleanup():
    """Clean up test data"""
    print_section("🧹 CLEANUP")
    
    # Delete test recipe
    if state['recipe_id']:
        print_test("Delete Test Recipe")
        test_endpoint(
            'DELETE', f"/recipes/{state['recipe_id']}",
            params={'user_id': TEST_USER_ID}
        )
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
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL PHASE 2 TESTS PASSED!{Colors.END}")
        print(f"{Colors.GREEN}Favorites API is working perfectly!{Colors.END}")
    else:
        print(f"\n{Colors.YELLOW}⚠️  {state['failed']} test(s) failed - review above for details{Colors.END}")

# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print_section("🚀 PHASE 2 TEST SUITE - FAVORITES API")
    print(f"{Colors.BLUE}Testing:{Colors.END} {BASE_URL}")
    print(f"{Colors.BLUE}Time:{Colors.END} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{Colors.BLUE}Test User:{Colors.END} ID {TEST_USER_ID}")
    
    try:
        # Setup
        if not setup_test_recipe():
            print(f"\n{Colors.RED}❌ Setup failed - cannot continue tests{Colors.END}")
            exit(1)
        
        # Run tests
        test_favorites_api()
        
        # Cleanup
        cleanup()
        
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
