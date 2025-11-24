"""
Token Handling V2 Test Suite
Tests that V2 API correctly handles tokens in requests and responses

Test Account:
- Email: token-test@yeschefapp.io
- Password: Testtest123
- Purpose: Automated token handling V2 testing

Run with: python tests/test_token_handling_v2.py
"""

import requests
import json
import jwt
import time
from datetime import datetime, timedelta

BASE_URL = 'http://127.0.0.1:5000'
TEST_EMAIL = 'token-test@yeschefapp.io'
TEST_PASSWORD = 'Testtest123'
TEST_NAME = 'Token Test User'

class Colors:
    """Terminal colors"""
    RESET = '\033[0m'
    BRIGHT = '\033[1m'
    GREEN = '\033[32m'
    RED = '\033[31m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    CYAN = '\033[36m'

class TokenHandlingTester:
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.token = None
        self.user_id = None
        
    def log(self, message, color=Colors.RESET):
        print(f"{color}{message}{Colors.RESET}")
        
    def print_test(self, name):
        print(f"\n{Colors.BLUE}🧪 TEST: {name}{Colors.RESET}")
        
    def print_pass(self, message):
        print(f"   {Colors.GREEN}✅ PASS: {message}{Colors.RESET}")
        self.tests_passed += 1
        
    def print_fail(self, message):
        print(f"   {Colors.RED}❌ FAIL: {message}{Colors.RESET}")
        self.tests_failed += 1
        
    def print_info(self, message):
        print(f"   {Colors.CYAN}ℹ️  {message}{Colors.RESET}")
        
    # ==========================================
    # Setup
    # ==========================================
    def setup_user(self):
        """Create test user"""
        self.log("\n🔧 SETUP: Creating test user...", Colors.YELLOW)
        
        try:
            response = requests.post(
                f'{BASE_URL}/api/v2/auth/register',
                json={
                    'name': TEST_NAME,
                    'email': TEST_EMAIL,
                    'password': TEST_PASSWORD
                }
            )
            
            if response.status_code == 201:
                data = response.json()
                self.token = data['data']['token']
                self.user_id = data['data']['user']['id']
                self.log(f"✅ User created: ID {self.user_id}", Colors.GREEN)
                return True
        except:
            pass
        
        # Try to login if already exists
        response = requests.post(
            f'{BASE_URL}/api/v2/auth/login',
            json={
                'email': TEST_EMAIL,
                'password': TEST_PASSWORD
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data['data']['token']
            self.user_id = data['data']['user']['id']
            self.log(f"✅ User logged in: ID {self.user_id}", Colors.GREEN)
            return True
        
        self.log("❌ Could not setup test user", Colors.RED)
        return False
    
    def cleanup_user(self):
        """Delete test user"""
        if self.token:
            try:
                requests.delete(
                    f'{BASE_URL}/api/v2/auth/account',
                    headers={'Authorization': f'Bearer {self.token}'},
                    json={'password': TEST_PASSWORD}
                )
                self.log("\n⚠️  Test user cleaned up", Colors.YELLOW)
            except:
                pass
    
    # ==========================================
    # Test 1: Token Format in Registration
    # ==========================================
    def test_registration_token_format(self):
        self.print_test('Registration Token Format (V2)')
        
        # Use a unique email for this test
        unique_email = f'token-format-test-{int(time.time())}@yeschefapp.io'
        
        try:
            response = requests.post(
                f'{BASE_URL}/api/v2/auth/register',
                json={
                    'name': 'Format Test',
                    'email': unique_email,
                    'password': TEST_PASSWORD
                }
            )
            
            self.print_info(f"Status: {response.status_code}")
            
            if response.status_code == 201:
                data = response.json()
                
                # Check V2 response structure
                if data.get('success'):
                    self.print_pass('Response has success=true')
                else:
                    self.print_fail('Missing success flag')
                
                if data.get('data'):
                    self.print_pass('Response has data wrapper')
                    
                    # Check token location (V2: data.token, not access_token)
                    if 'token' in data['data']:
                        token = data['data']['token']
                        self.print_pass(f'Token in data.token (V2 format): {token[:20]}...')
                        
                        # Validate JWT format
                        if self.validate_jwt_format(token):
                            self.print_pass('Token is valid JWT format')
                        else:
                            self.print_fail('Token is not valid JWT')
                    else:
                        self.print_fail('Token not in data.token')
                    
                    # Ensure old V1 format is NOT used
                    if 'access_token' not in data['data']:
                        self.print_pass('Old V1 access_token not present (good!)')
                    else:
                        self.print_fail('Found V1 access_token (should not exist in V2)')
                else:
                    self.print_fail('Missing data wrapper')
                
                # Cleanup
                if data.get('data', {}).get('token'):
                    requests.delete(
                        f'{BASE_URL}/api/v2/auth/account',
                        headers={'Authorization': f'Bearer {data["data"]["token"]}'},
                        json={'password': TEST_PASSWORD}
                    )
            else:
                self.print_fail(f'Wrong status code: {response.status_code}')
        except Exception as e:
            self.print_fail(f'Exception: {str(e)}')
    
    # ==========================================
    # Test 2: Token Format in Login
    # ==========================================
    def test_login_token_format(self):
        self.print_test('Login Token Format (V2)')
        
        try:
            response = requests.post(
                f'{BASE_URL}/api/v2/auth/login',
                json={
                    'email': TEST_EMAIL,
                    'password': TEST_PASSWORD
                }
            )
            
            self.print_info(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and data.get('data'):
                    self.print_pass('V2 response format correct')
                    
                    # Check token location
                    if 'token' in data['data']:
                        token = data['data']['token']
                        self.print_pass(f'Token in data.token: {token[:20]}...')
                        
                        # Validate JWT
                        if self.validate_jwt_format(token):
                            self.print_pass('Token is valid JWT')
                            
                            # Decode and check contents
                            payload = self.decode_jwt(token)
                            if payload:
                                if 'user_id' in payload:
                                    self.print_pass(f'Token contains user_id: {payload["user_id"]}')
                                if 'exp' in payload:
                                    exp_time = datetime.fromtimestamp(payload['exp'])
                                    hours_until_expiry = (exp_time - datetime.now()).total_seconds() / 3600
                                    self.print_pass(f'Token expires in {hours_until_expiry:.1f} hours')
                        else:
                            self.print_fail('Token is not valid JWT')
                    else:
                        self.print_fail('Token not in data.token')
                else:
                    self.print_fail('Wrong V2 format')
            else:
                self.print_fail(f'Wrong status code: {response.status_code}')
        except Exception as e:
            self.print_fail(f'Exception: {str(e)}')
    
    # ==========================================
    # Test 3: Token in Authorization Header
    # ==========================================
    def test_token_in_auth_header(self):
        self.print_test('Token in Authorization Header')
        
        if not self.token:
            self.print_fail('No token available')
            return
        
        try:
            # Test with correct format: Bearer <token>
            response = requests.get(
                f'{BASE_URL}/api/v2/auth/me',
                headers={'Authorization': f'Bearer {self.token}'}
            )
            
            self.print_info(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.print_pass('Token accepted in Authorization header')
                    self.print_pass(f'User authenticated: {data["data"]["user"]["email"]}')
                else:
                    self.print_fail('Request failed despite correct token')
            else:
                self.print_fail(f'Token rejected: {response.status_code}')
        except Exception as e:
            self.print_fail(f'Exception: {str(e)}')
    
    # ==========================================
    # Test 4: Missing Token Rejection
    # ==========================================
    def test_missing_token_rejection(self):
        self.print_test('Missing Token Rejection')
        
        try:
            # Try protected endpoint without token
            response = requests.get(
                f'{BASE_URL}/api/v2/auth/me'
                # No Authorization header
            )
            
            self.print_info(f"Status: {response.status_code}")
            
            if response.status_code == 401:
                self.print_pass('Request correctly rejected (401 Unauthorized)')
                
                data = response.json()
                if not data.get('success'):
                    self.print_pass('Response has success=false')
                if data.get('error'):
                    self.print_pass(f'Error message provided: {data["error"]}')
            else:
                self.print_fail(f'Wrong status code: {response.status_code} (expected 401)')
        except Exception as e:
            self.print_fail(f'Exception: {str(e)}')
    
    # ==========================================
    # Test 5: Invalid Token Rejection
    # ==========================================
    def test_invalid_token_rejection(self):
        self.print_test('Invalid Token Rejection')
        
        try:
            # Try with invalid token
            response = requests.get(
                f'{BASE_URL}/api/v2/auth/me',
                headers={'Authorization': 'Bearer invalid_token_12345'}
            )
            
            self.print_info(f"Status: {response.status_code}")
            
            if response.status_code == 401:
                self.print_pass('Invalid token correctly rejected (401)')
                
                data = response.json()
                if not data.get('success'):
                    self.print_pass('Response has success=false')
            else:
                self.print_fail(f'Wrong status code: {response.status_code} (expected 401)')
        except Exception as e:
            self.print_fail(f'Exception: {str(e)}')
    
    # ==========================================
    # Test 6: Token Works Across Endpoints
    # ==========================================
    def test_token_across_endpoints(self):
        self.print_test('Token Works Across Multiple Endpoints')
        
        if not self.token or not self.user_id:
            self.print_fail('No token available')
            return
        
        endpoints = [
            ('GET', f'/api/v2/auth/me', None),
            ('GET', f'/api/v2/recipes/user/{self.user_id}', None),
            ('GET', f'/api/v2/profile/{self.user_id}', None),
            ('GET', f'/api/v2/profile/{self.user_id}/stats', None),
        ]
        
        for method, endpoint, body in endpoints:
            try:
                if method == 'GET':
                    response = requests.get(
                        f'{BASE_URL}{endpoint}',
                        headers={'Authorization': f'Bearer {self.token}'}
                    )
                else:
                    response = requests.request(
                        method,
                        f'{BASE_URL}{endpoint}',
                        headers={
                            'Authorization': f'Bearer {self.token}',
                            'Content-Type': 'application/json'
                        },
                        json=body
                    )
                
                if response.status_code in [200, 201]:
                    self.print_pass(f'{method} {endpoint} - Token accepted')
                else:
                    self.print_fail(f'{method} {endpoint} - Failed ({response.status_code})')
            except Exception as e:
                self.print_fail(f'{method} {endpoint} - Exception: {str(e)}')
    
    # ==========================================
    # Helper Methods
    # ==========================================
    def validate_jwt_format(self, token):
        """Check if token is valid JWT format"""
        try:
            parts = token.split('.')
            return len(parts) == 3
        except:
            return False
    
    def decode_jwt(self, token):
        """Decode JWT without verification (for testing)"""
        try:
            # Decode without verification to inspect contents
            payload = jwt.decode(token, options={"verify_signature": False})
            return payload
        except:
            return None
    
    # ==========================================
    # Run All Tests
    # ==========================================
    def run_all_tests(self):
        print('\n' + '='*60)
        self.log('🧪 TOKEN HANDLING V2 TEST SUITE', Colors.BRIGHT)
        print('='*60)
        self.log(f'\nTesting against: {BASE_URL}', Colors.BLUE)
        self.log(f'Test account: {TEST_EMAIL}\n', Colors.BLUE)
        
        # Setup
        if not self.setup_user():
            self.log('❌ Could not setup test user - aborting', Colors.RED)
            return False
        
        # Run tests
        self.test_registration_token_format()
        self.test_login_token_format()
        self.test_token_in_auth_header()
        self.test_missing_token_rejection()
        self.test_invalid_token_rejection()
        self.test_token_across_endpoints()
        
        # Cleanup
        self.cleanup_user()
        
        # Results
        print('\n' + '='*60)
        self.log('📊 TEST RESULTS', Colors.BRIGHT)
        print('='*60)
        
        total = self.tests_passed + self.tests_failed
        pass_rate = (self.tests_passed / total * 100) if total > 0 else 0
        
        print(f'\n   Total Tests: {total}')
        self.log(f'   Passed: {self.tests_passed}', Colors.GREEN)
        self.log(f'   Failed: {self.tests_failed}', Colors.RED)
        print(f'   Pass Rate: {pass_rate:.1f}%')
        
        if self.tests_failed == 0:
            self.log('\n   🎉 ALL TOKEN TESTS PASSED!', Colors.GREEN + Colors.BRIGHT)
        else:
            self.log('\n   ⚠️  Some tests failed - review output above', Colors.YELLOW)
        
        print('\n' + '='*60 + '\n')
        
        return self.tests_failed == 0

# Run tests
if __name__ == '__main__':
    tester = TokenHandlingTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)
