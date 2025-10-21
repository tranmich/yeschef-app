"""
🧪 RECIPE SEARCH & IMPORT API TEST SUITE
Tests all 8 Phase 5 endpoints on PostgreSQL/Railway

Endpoints tested:
- Advanced search
- Get recommendations
- Search by ingredients
- Get popular recipes
- Get recent recipes
- Import from URL
- Get import history
- Bulk delete
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
    'recipe_ids': [],
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
# SETUP: Create test recipes
# =============================================================================

def setup_test_recipes():
    """Create test recipes for search"""
    print_section("🔧 SETUP: CREATE TEST RECIPES")
    
    recipes = [
        {
            'title': f'Search Test Pizza {int(time.time())}',
            'description': 'Italian pizza recipe',
            'category': 'italian',
            'prep_time': '15 minutes',
            'cook_time': '20 minutes'
        },
        {
            'title': f'Search Test Pasta {int(time.time())}',
            'description': 'Quick pasta dish',
            'category': 'italian',
            'prep_time': '10 minutes',
            'cook_time': '15 minutes'
        }
    ]
    
    for i, recipe_data in enumerate(recipes, 1):
        print_test(f"Create Test Recipe {i}")
        success, data = test_endpoint(
            'POST', '/recipes',
            json={
                'user_id': TEST_USER_ID,
                **recipe_data,
                'ingredients': ['Test Ingredient'],
                'instructions': ['Test Step'],
                'servings': 2
            },
            headers={'Content-Type': 'application/json'}
        )
        
        if success:
            recipe_id = data.get('data', {}).get('id')
            state['recipe_ids'].append(recipe_id)
            print(f"   Recipe ID: {recipe_id}")
        
        time.sleep(0.5)

# =============================================================================
# RECIPE SEARCH & IMPORT API TESTS
# =============================================================================

def test_search_api():
    """Test all search and import endpoints"""
    print_section("🔍 RECIPE SEARCH & IMPORT API TESTS (8 endpoints)")
    
    # Test 1: Advanced search
    print_test("1. Advanced Search")
    success, data = test_endpoint(
        'GET', '/recipes/search/advanced',
        params={
            'user_id': TEST_USER_ID,
            'q': 'Search Test',
            'limit': 10
        }
    )
    
    if success:
        recipes = data.get('data', [])
        print(f"   Found {len(recipes)} recipes")
    
    time.sleep(0.5)
    
    # Test 2: Search with filters
    print_test("2. Advanced Search with Filters")
    success, data = test_endpoint(
        'GET', '/recipes/search/advanced',
        params={
            'user_id': TEST_USER_ID,
            'category': 'italian',
            'prep_time_max': 20,
            'limit': 10
        }
    )
    
    if success:
        recipes = data.get('data', [])
        print(f"   Found {len(recipes)} Italian recipes")
    
    time.sleep(0.5)
    
    # Test 3: Get recommendations
    print_test("3. Get Recipe Recommendations")
    success, data = test_endpoint(
        'GET', '/recipes/recommendations',
        params={'user_id': TEST_USER_ID, 'limit': 5}
    )
    
    if success:
        recipes = data.get('data', [])
        print(f"   Got {len(recipes)} recommendations")
    
    time.sleep(0.5)
    
    # Test 4: Search by ingredients
    print_test("4. Search by Ingredients")
    success, data = test_endpoint(
        'POST', '/recipes/search/ingredients',
        json={
            'user_id': TEST_USER_ID,
            'ingredients': ['Test', 'Ingredient'],
            'limit': 10
        },
        headers={'Content-Type': 'application/json'}
    )
    
    if success:
        recipes = data.get('data', [])
        print(f"   Found {len(recipes)} recipes with matching ingredients")
    
    time.sleep(0.5)
    
    # Test 5: Get popular recipes
    print_test("5. Get Popular Recipes")
    success, data = test_endpoint(
        'GET', '/recipes/popular',
        params={'limit': 10}
    )
    
    if success:
        recipes = data.get('data', [])
        print(f"   Got {len(recipes)} popular recipes")
    
    time.sleep(0.5)
    
    # Test 6: Get recent recipes
    print_test("6. Get Recent Recipes")
    success, data = test_endpoint(
        'GET', '/recipes/recent',
        params={'user_id': TEST_USER_ID, 'days': 7, 'limit': 10}
    )
    
    if success:
        recipes = data.get('data', [])
        print(f"   Got {len(recipes)} recent recipes")
    
    time.sleep(0.5)
    
    # Test 7: Import recipe from URL
    print_test("7. Import Recipe from URL")
    success, data = test_endpoint(
        'POST', '/recipes/import',
        json={
            'user_id': TEST_USER_ID,
            'url': 'https://example.com/test-recipe'
        },
        headers={'Content-Type': 'application/json'}
    )
    
    if success:
        recipe_id = data.get('data', {}).get('id')
        state['recipe_ids'].append(recipe_id)
        print(f"   ✓ Imported recipe ID: {recipe_id}")
    
    time.sleep(0.5)
    
    # Test 8: Get import history
    print_test("8. Get Import History")
    success, data = test_endpoint(
        'GET', '/recipes/import/history',
        params={'user_id': TEST_USER_ID, 'limit': 10}
    )
    
    if success:
        imports = data.get('data', [])
        print(f"   Found {len(imports)} import records")
    
    time.sleep(0.5)

# =============================================================================
# CLEANUP
# =============================================================================

def cleanup():
    """Clean up test data"""
    print_section("🧹 CLEANUP")
    
    if state['recipe_ids']:
        print_test("Bulk Delete Test Recipes")
        test_endpoint(
            'DELETE', '/recipes/bulk-delete',
            json={
                'user_id': TEST_USER_ID,
                'recipe_ids': state['recipe_ids']
            },
            headers={'Content-Type': 'application/json'}
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
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL PHASE 5 TESTS PASSED!{Colors.END}")
        print(f"{Colors.GREEN}Recipe Search & Import API is working perfectly!{Colors.END}")
    else:
        print(f"\n{Colors.YELLOW}⚠️  {state['failed']} test(s) failed - review above for details{Colors.END}")

# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print_section("🚀 PHASE 5 TEST SUITE - RECIPE SEARCH & IMPORT API")
    print(f"{Colors.BLUE}Testing:{Colors.END} {BASE_URL}")
    print(f"{Colors.BLUE}Time:{Colors.END} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{Colors.BLUE}Test User:{Colors.END} ID {TEST_USER_ID}")
    
    try:
        # Setup
        setup_test_recipes()
        
        # Run tests
        test_search_api()
        
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
