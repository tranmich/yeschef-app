"""
🧪 COMMUNITY & SHARING API TEST SUITE
Tests all 8 Phase 1 endpoints on PostgreSQL/Railway

Endpoints tested:
- Browse community recipes
- Get community recipe details
- Share recipe to community
- Unshare recipe
- Get my shares
- Check share status
- Claim recipe
- Like/Unlike recipe
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
TEST_USER2_ID = 12

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
    'shared_recipe_id': None,
    'claimed_recipe_id': None,
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
            if data.get('success') or data.get('status') == 'healthy':
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
    """Create a test recipe for community sharing"""
    print_section("🔧 SETUP: CREATE TEST RECIPE")
    
    print_test("Create Test Recipe")
    success, data = test_endpoint(
        'POST', '/recipes',
        json={
            'user_id': TEST_USER_ID,
            'title': f'Community Test Recipe {int(time.time())}',
            'description': 'A recipe for testing community features',
            'ingredients': ['Test Ingredient 1', 'Test Ingredient 2', 'Test Ingredient 3'],
            'instructions': ['Step 1: Test', 'Step 2: Test more', 'Step 3: Done'],
            'prep_time': '10 minutes',
            'cook_time': '20 minutes',
            'servings': 4
        },
        headers={'Content-Type': 'application/json'}
    )
    
    if success:
        state['recipe_id'] = data.get('data', {}).get('id')
        print(f"   Recipe ID: {state['recipe_id']}")
        return True
    
    return False

# =============================================================================
# COMMUNITY API TESTS
# =============================================================================

def test_community_api():
    """Test all community endpoints"""
    print_section("🌟 COMMUNITY & SHARING API TESTS (8 endpoints)")
    
    # Test 1: Share recipe to community
    print_test("1. Share Recipe to Community")
    success, data = test_endpoint(
        'POST', '/community/recipes',
        json={
            'recipe_id': state['recipe_id'],
            'user_id': TEST_USER_ID
        },
        headers={'Content-Type': 'application/json'}
    )
    
    time.sleep(0.5)
    
    # Test 2: Check if recipe is shared
    print_test("2. Check Share Status")
    success, data = test_endpoint(
        'GET', f"/community/check/{state['recipe_id']}",
        params={'user_id': TEST_USER_ID}
    )
    
    if success:
        is_shared = data.get('data', {}).get('is_shared', False)
        if is_shared:
            print(f"   ✓ Recipe is shared to community")
        else:
            print(f"   ⚠ Recipe not marked as shared")
    
    time.sleep(0.5)
    
    # Test 3: Browse community recipes
    print_test("3. Browse Community Recipes")
    success, data = test_endpoint(
        'GET', '/community/recipes',
        params={'user_id': TEST_USER_ID, 'limit': 10}
    )
    
    if success:
        recipes = data.get('data', [])
        print(f"   Found {len(recipes)} community recipes")
        
        # Find our recipe
        for recipe in recipes:
            if recipe.get('id') == state['recipe_id']:
                print(f"   ✓ Our recipe found in community!")
                state['shared_recipe_id'] = recipe['id']
                break
    
    time.sleep(0.5)
    
    # Test 4: Get community recipe details
    if state['shared_recipe_id']:
        print_test("4. Get Community Recipe Details")
        success, data = test_endpoint(
            'GET', f"/community/recipes/{state['shared_recipe_id']}",
            params={'user_id': TEST_USER_ID}
        )
        
        if success:
            recipe = data.get('data', {})
            print(f"   Title: {recipe.get('title', 'N/A')}")
            print(f"   Likes: {recipe.get('like_count', 0)}")
        
        time.sleep(0.5)
    
    # Test 5: Like the recipe
    print_test("5. Like Community Recipe")
    success, data = test_endpoint(
        'POST', f"/community/recipes/{state['recipe_id']}/like",
        json={'user_id': TEST_USER2_ID},  # Different user likes it
        headers={'Content-Type': 'application/json'}
    )
    
    if success:
        like_count = data.get('data', {}).get('like_count', 0)
        print(f"   ✓ Recipe now has {like_count} likes")
    
    time.sleep(0.5)
    
    # Test 6: Claim recipe (copy to own collection)
    print_test("6. Claim Community Recipe")
    success, data = test_endpoint(
        'POST', f"/community/recipes/{state['recipe_id']}/claim",
        json={'user_id': TEST_USER2_ID},  # Different user claims it
        headers={'Content-Type': 'application/json'}
    )
    
    if success:
        claimed = data.get('data', {})
        state['claimed_recipe_id'] = claimed.get('id')
        print(f"   ✓ Recipe claimed! New recipe ID: {state['claimed_recipe_id']}")
        print(f"   Title: {claimed.get('title', 'N/A')}")
    
    time.sleep(0.5)
    
    # Test 7: Get my shared recipes
    print_test("7. Get My Shared Recipes")
    success, data = test_endpoint(
        'GET', '/community/my-shares',
        params={'user_id': TEST_USER_ID}
    )
    
    if success:
        shares = data.get('data', [])
        print(f"   ✓ User has {len(shares)} shared recipes")
    
    time.sleep(0.5)
    
    # Test 8: Unlike recipe
    print_test("8. Unlike Community Recipe")
    success, data = test_endpoint(
        'DELETE', f"/community/recipes/{state['recipe_id']}/like",
        params={'user_id': TEST_USER2_ID}
    )
    
    if success:
        like_count = data.get('data', {}).get('like_count', 0)
        print(f"   ✓ Like removed. Recipe now has {like_count} likes")
    
    time.sleep(0.5)

# =============================================================================
# CLEANUP
# =============================================================================

def cleanup():
    """Clean up test data"""
    print_section("🧹 CLEANUP")
    
    # Unshare recipe
    if state['recipe_id']:
        print_test("Unshare Test Recipe")
        test_endpoint(
            'DELETE', f"/community/recipes/{state['recipe_id']}",
            params={'user_id': TEST_USER_ID}
        )
        time.sleep(0.5)
    
    # Delete original recipe
    if state['recipe_id']:
        print_test("Delete Original Recipe")
        test_endpoint(
            'DELETE', f"/recipes/{state['recipe_id']}",
            params={'user_id': TEST_USER_ID}
        )
        time.sleep(0.5)
    
    # Delete claimed recipe
    if state['claimed_recipe_id']:
        print_test("Delete Claimed Recipe")
        test_endpoint(
            'DELETE', f"/recipes/{state['claimed_recipe_id']}",
            params={'user_id': TEST_USER2_ID}
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
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL PHASE 1 TESTS PASSED!{Colors.END}")
        print(f"{Colors.GREEN}Community & Sharing API is working perfectly!{Colors.END}")
    else:
        print(f"\n{Colors.YELLOW}⚠️  {state['failed']} test(s) failed - review above for details{Colors.END}")

# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print_section("🚀 PHASE 1 TEST SUITE - COMMUNITY & SHARING API")
    print(f"{Colors.BLUE}Testing:{Colors.END} {BASE_URL}")
    print(f"{Colors.BLUE}Time:{Colors.END} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{Colors.BLUE}Test User:{Colors.END} ID {TEST_USER_ID}")
    
    try:
        # Setup
        if not setup_test_recipe():
            print(f"\n{Colors.RED}❌ Setup failed - cannot continue tests{Colors.END}")
            exit(1)
        
        # Run tests
        test_community_api()
        
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
