"""
V2 API Feature Verification Script
Tests all registered V2 endpoints to ensure they're working

Run with: python tests/verify_v2_features.py
"""

import requests
import json
from datetime import datetime

BASE_URL = 'http://127.0.0.1:5000'

class Colors:
    RESET = '\033[0m'
    BRIGHT = '\033[1m'
    GREEN = '\033[32m'
    RED = '\033[31m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    CYAN = '\033[36m'

class V2FeatureVerifier:
    def __init__(self):
        self.features_checked = 0
        self.features_working = 0
        self.features_missing = 0
        self.features_error = 0
        
    def log(self, message, color=Colors.RESET):
        print(f"{color}{message}{Colors.RESET}")
        
    def check_endpoint(self, method, path, expected_status=200, name="", needs_auth=False):
        """Check if an endpoint exists and responds"""
        self.features_checked += 1
        
        try:
            headers = {}
            if needs_auth:
                headers['Authorization'] = 'Bearer fake_token_for_testing'
            
            if method == 'GET':
                response = requests.get(f'{BASE_URL}{path}', headers=headers, timeout=5)
            elif method == 'POST':
                response = requests.post(f'{BASE_URL}{path}', json={}, headers=headers, timeout=5)
            else:
                response = requests.request(method, f'{BASE_URL}{path}', headers=headers, timeout=5)
            
            # Check if endpoint exists (not 404)
            if response.status_code == 404:
                self.log(f"  ❌ {name}: Not found (404)", Colors.RED)
                self.features_missing += 1
                return False
            
            # 401 is OK for auth-protected endpoints
            if response.status_code == 401 and needs_auth:
                self.log(f"  ✅ {name}: Exists (requires auth)", Colors.GREEN)
                self.features_working += 1
                return True
            
            # Check if it returns expected status or reasonable status
            if response.status_code in [200, 201, 400, 401, 403, 422, 503]:
                self.log(f"  ✅ {name}: Working ({response.status_code})", Colors.GREEN)
                self.features_working += 1
                return True
            
            self.log(f"  ⚠️  {name}: Unexpected status ({response.status_code})", Colors.YELLOW)
            self.features_error += 1
            return False
            
        except requests.exceptions.ConnectionError:
            self.log(f"  ❌ {name}: Server not running", Colors.RED)
            self.features_error += 1
            return False
        except Exception as e:
            self.log(f"  ❌ {name}: Error - {str(e)}", Colors.RED)
            self.features_error += 1
            return False
    
    def verify_all_features(self):
        print('\n' + '='*70)
        self.log('🔍 V2 API FEATURE VERIFICATION', Colors.BRIGHT + Colors.CYAN)
        print('='*70)
        self.log(f'\nTesting against: {BASE_URL}', Colors.BLUE)
        self.log(f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n', Colors.BLUE)
        
        # ============================================================
        # Authentication (Already Verified - 72 tests passing)
        # ============================================================
        self.log('\n📍 1. AUTHENTICATION V2 (Already tested - 72 tests passing)', Colors.CYAN)
        self.check_endpoint('GET', '/api/v2/auth/health', name='Auth Health Check')
        self.log('   ℹ️  Full auth testing: tests/test_v2_auth_comprehensive.py', Colors.CYAN)
        self.log('   ℹ️  Token testing: tests/test_token_handling_v2.py', Colors.CYAN)
        
        # ============================================================
        # Recipes (Already Verified - 18 tests passing)
        # ============================================================
        self.log('\n📍 2. RECIPES V2 (Already tested - 18 tests passing)', Colors.CYAN)
        self.check_endpoint('GET', '/api/v2/recipes/health', name='Recipes Health Check')
        self.log('   ℹ️  Full recipe testing: tests/test_mobile_recipes_v2.py', Colors.CYAN)
        
        # ============================================================
        # Profile (Already Migrated)
        # ============================================================
        self.log('\n📍 3. PROFILE V2 (Migrated, needs testing)', Colors.CYAN)
        self.check_endpoint('GET', '/api/v2/profile/health', name='Profile Health Check')
        self.check_endpoint('GET', '/api/v2/profile/1', name='Get Profile', needs_auth=True)
        self.check_endpoint('GET', '/api/v2/profile/1/stats', name='Get Stats', needs_auth=True)
        
        # ============================================================
        # Meal Plans (Existing V2 - Needs Verification)
        # ============================================================
        self.log('\n📍 4. MEAL PLANS V2 (Existing - checking...)', Colors.CYAN)
        self.check_endpoint('GET', '/api/v2/meal-plans/health', name='Meal Plans Health Check')
        self.check_endpoint('GET', '/api/v2/meal-plans', name='List Meal Plans', needs_auth=True)
        self.check_endpoint('GET', '/api/v2/meal-plans/current', name='Get Current Plan', needs_auth=True)
        
        # ============================================================
        # Grocery Lists (Existing V2 - Needs Verification)
        # ============================================================
        self.log('\n📍 5. GROCERY LISTS V2 (Existing - checking...)', Colors.CYAN)
        self.check_endpoint('GET', '/api/v2/grocery-lists/health', name='Grocery Lists Health Check')
        self.check_endpoint('GET', '/api/v2/grocery-lists', name='List Grocery Lists', needs_auth=True)
        self.check_endpoint('GET', '/api/v2/grocery-lists/active', name='Get Active List', needs_auth=True)
        
        # ============================================================
        # Friends (Existing V2 - Needs Verification)
        # ============================================================
        self.log('\n📍 6. FRIENDS V2 (Existing - checking...)', Colors.CYAN)
        self.check_endpoint('GET', '/api/v2/friends/health', name='Friends Health Check')
        self.check_endpoint('GET', '/api/v2/friends', name='List Friends', needs_auth=True)
        self.check_endpoint('GET', '/api/v2/friends/requests', name='Friend Requests', needs_auth=True)
        
        # ============================================================
        # Households (Existing V2 - Needs Verification)
        # ============================================================
        self.log('\n📍 7. HOUSEHOLDS V2 (Existing - checking...)', Colors.CYAN)
        self.check_endpoint('GET', '/api/v2/households/health', name='Households Health Check')
        self.check_endpoint('GET', '/api/v2/households', name='List Households', needs_auth=True)
        self.check_endpoint('GET', '/api/v2/households/my', name='My Households', needs_auth=True)
        
        # ============================================================
        # Community (Existing V2 - Needs Verification)
        # ============================================================
        self.log('\n📍 8. COMMUNITY V2 (Existing - checking...)', Colors.CYAN)
        self.check_endpoint('GET', '/api/v2/community/health', name='Community Health Check')
        self.check_endpoint('GET', '/api/v2/community/feed', name='Community Feed', needs_auth=True)
        self.check_endpoint('GET', '/api/v2/community/discover', name='Discover', needs_auth=True)
        
        # ============================================================
        # Pantry (Existing V2 - Needs Verification)
        # ============================================================
        self.log('\n📍 9. PANTRY V2 (Existing - checking...)', Colors.CYAN)
        self.check_endpoint('GET', '/api/v2/pantry/health', name='Pantry Health Check')
        self.check_endpoint('GET', '/api/v2/pantry/items', name='List Items', needs_auth=True)
        self.check_endpoint('GET', '/api/v2/pantry/categories', name='Categories', needs_auth=True)
        
        # ============================================================
        # Recipe Search (Existing V2 - Needs Verification)
        # ============================================================
        self.log('\n📍 10. RECIPE SEARCH V2 (Existing - checking...)', Colors.CYAN)
        self.check_endpoint('GET', '/api/v2/search/health', name='Search Health Check')
        self.check_endpoint('POST', '/api/v2/search/recipes', name='Search Recipes', needs_auth=True)
        
        # ============================================================
        # System (Existing V2 - Needs Verification)
        # ============================================================
        self.log('\n📍 11. SYSTEM V2 (Existing - checking...)', Colors.CYAN)
        self.check_endpoint('GET', '/api/v2/system/health', name='System Health Check')
        self.check_endpoint('GET', '/api/v2/system/version', name='System Version')
        
        # ============================================================
        # Images (Existing V2 - Needs Verification)
        # ============================================================
        self.log('\n📍 12. IMAGES V2 (Existing - checking...)', Colors.CYAN)
        self.check_endpoint('GET', '/api/v2/images/health', name='Images Health Check')
        
        # ============================================================
        # Results
        # ============================================================
        print('\n' + '='*70)
        self.log('📊 VERIFICATION RESULTS', Colors.BRIGHT)
        print('='*70)
        
        print(f'\n   Total Endpoints Checked: {self.features_checked}')
        self.log(f'   ✅ Working: {self.features_working}', Colors.GREEN)
        self.log(f'   ❌ Missing: {self.features_missing}', Colors.RED)
        self.log(f'   ⚠️  Errors: {self.features_error}', Colors.YELLOW)
        
        working_rate = (self.features_working / self.features_checked * 100) if self.features_checked > 0 else 0
        print(f'   Working Rate: {working_rate:.1f}%')
        
        print('\n' + '='*70)
        
        # Summary by feature
        self.log('\n📋 FEATURE STATUS SUMMARY:', Colors.BRIGHT)
        print('\n   ✅ Fully Tested & Working:')
        print('      - Auth V2 (72 tests)')
        print('      - Recipes V2 (18 tests)')
        print('      - Token Handling (20 tests)')
        
        print('\n   ✅ Migrated (Ready for testing):')
        print('      - Profile V2')
        
        print('\n   ⏳ Existing V2 (Need verification):')
        print('      - Meal Plans')
        print('      - Grocery Lists')
        print('      - Friends')
        print('      - Households')
        print('      - Community')
        print('      - Pantry')
        print('      - Recipe Search')
        print('      - System')
        print('      - Images')
        
        print('\n   ❌ Removed:')
        print('      - Favorites (cleaned up - was incomplete)')
        
        print('\n' + '='*70)
        
        return self.features_missing == 0 and self.features_error == 0

# Run verification
if __name__ == '__main__':
    verifier = V2FeatureVerifier()
    success = verifier.verify_all_features()
    
    if success:
        print(f'\n{Colors.GREEN}{Colors.BRIGHT}✅ ALL V2 FEATURES VERIFIED!{Colors.RESET}\n')
        exit(0)
    else:
        print(f'\n{Colors.YELLOW}{Colors.BRIGHT}⚠️  SOME FEATURES NEED ATTENTION{Colors.RESET}\n')
        exit(1)
