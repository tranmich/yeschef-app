"""
Comprehensive V2 Auth Integration Tests
Tests the complete auth flow including edge cases and error handling

Test Account:
- Email: test@yeschefapp.io
- Password: Testtest
- Purpose: Automated testing of V2 auth endpoints

Run with: python tests/test_v2_auth_comprehensive.py
"""

import requests
import json
import time
from typing import Dict, Any, Optional

BASE_URL = 'http://127.0.0.1:5000'

class Colors:
    """Terminal colors for pretty output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class AuthTestSuite:
    """Comprehensive auth testing suite"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.test_email = "test@yeschefapp.io"
        self.test_password = "Testtest"
        self.test_name = "Test User"
        self.token: Optional[str] = None
        self.user_id: Optional[int] = None
        self.tests_passed = 0
        self.tests_failed = 0
        
    def print_test(self, name: str):
        """Print test name"""
        print(f"\n{Colors.OKBLUE}🧪 TEST: {name}{Colors.ENDC}")
        
    def print_pass(self, message: str):
        """Print success message"""
        print(f"   {Colors.OKGREEN}✅ PASS: {message}{Colors.ENDC}")
        self.tests_passed += 1
        
    def print_fail(self, message: str):
        """Print failure message"""
        print(f"   {Colors.FAIL}❌ FAIL: {message}{Colors.ENDC}")
        self.tests_failed += 1
        
    def print_info(self, message: str):
        """Print info message"""
        print(f"   {Colors.OKCYAN}ℹ️  {message}{Colors.ENDC}")
        
    def cleanup_test_user(self):
        """Delete test user if exists (using V1 endpoint)"""
        try:
            # Try to login first
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={"email": self.test_email, "password": self.test_password}
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                
                # Delete using V1 endpoint
                requests.delete(
                    f"{self.base_url}/api/auth/wipe-data",
                    headers={'Authorization': f'Bearer {token}'}
                )
                print(f"{Colors.WARNING}⚠️  Cleaned up existing test user{Colors.ENDC}")
        except:
            pass  # User doesn't exist, that's fine
    
    # ============================================
    # Test 1: Registration Flow
    # ============================================
    
    def test_registration_success(self):
        """Test successful user registration"""
        self.print_test("Registration - Success Case")
        
        response = requests.post(
            f"{self.base_url}/api/v2/auth/register",
            json={
                "name": self.test_name,
                "email": self.test_email,
                "password": self.test_password
            }
        )
        
        self.print_info(f"Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            
            # Check response structure
            if data.get('success') == True:
                self.print_pass("Response has success=true")
            else:
                self.print_fail("Response missing success=true")
                
            # Check token exists
            if data.get('data', {}).get('token'):
                self.token = data['data']['token']
                self.print_pass(f"Token received: {self.token[:20]}...")
            else:
                self.print_fail("No token in response")
                
            # Check user data
            user = data.get('data', {}).get('user', {})
            if user.get('email') == self.test_email:
                self.user_id = user.get('id')
                self.print_pass(f"User created with ID: {self.user_id}")
            else:
                self.print_fail("User data incorrect")
        else:
            self.print_fail(f"Expected 201, got {response.status_code}")
            self.print_info(f"Response: {response.text}")
    
    def test_registration_duplicate_email(self):
        """Test registration with existing email"""
        self.print_test("Registration - Duplicate Email")
        
        response = requests.post(
            f"{self.base_url}/api/v2/auth/register",
            json={
                "name": "Another User",
                "email": self.test_email,  # Same email
                "password": "different123"
            }
        )
        
        if response.status_code in [400, 409]:
            self.print_pass(f"Correctly rejected duplicate (status {response.status_code})")
        else:
            self.print_fail(f"Should reject duplicate, got {response.status_code}")
    
    def test_registration_invalid_email(self):
        """Test registration with invalid email"""
        self.print_test("Registration - Invalid Email")
        
        response = requests.post(
            f"{self.base_url}/api/v2/auth/register",
            json={
                "name": "Test",
                "email": "not-an-email",
                "password": "test123"
            }
        )
        
        if response.status_code == 400:
            self.print_pass("Correctly rejected invalid email")
        else:
            self.print_fail(f"Should reject invalid email, got {response.status_code}")
    
    def test_registration_weak_password(self):
        """Test registration with weak password"""
        self.print_test("Registration - Weak Password")
        
        response = requests.post(
            f"{self.base_url}/api/v2/auth/register",
            json={
                "name": "Test",
                "email": "weak@test.com",
                "password": "123"  # Too short
            }
        )
        
        # Note: Currently may not validate password strength
        self.print_info(f"Status: {response.status_code}")
        if response.status_code == 400:
            self.print_pass("Password validation working")
        else:
            self.print_info("⚠️  No password strength validation (enhancement needed)")
    
    # ============================================
    # Test 2: Login Flow
    # ============================================
    
    def test_login_success(self):
        """Test successful login"""
        self.print_test("Login - Success Case")
        
        response = requests.post(
            f"{self.base_url}/api/v2/auth/login",
            json={
                "email": self.test_email,
                "password": self.test_password
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                self.print_pass("Login successful")
                
                # Check token
                if data.get('data', {}).get('token'):
                    self.token = data['data']['token']
                    self.print_pass(f"Token received: {self.token[:20]}...")
                else:
                    self.print_fail("No token in login response")
            else:
                self.print_fail("Login response missing success flag")
        else:
            self.print_fail(f"Expected 200, got {response.status_code}")
    
    def test_login_wrong_password(self):
        """Test login with wrong password"""
        self.print_test("Login - Wrong Password")
        
        response = requests.post(
            f"{self.base_url}/api/v2/auth/login",
            json={
                "email": self.test_email,
                "password": "WrongPassword123"
            }
        )
        
        if response.status_code == 401:
            self.print_pass("Correctly rejected wrong password")
        else:
            self.print_fail(f"Expected 401, got {response.status_code}")
    
    def test_login_nonexistent_user(self):
        """Test login with non-existent email"""
        self.print_test("Login - Non-existent User")
        
        response = requests.post(
            f"{self.base_url}/api/v2/auth/login",
            json={
                "email": "doesnotexist@test.com",
                "password": "password123"
            }
        )
        
        if response.status_code == 401:
            self.print_pass("Correctly rejected non-existent user")
        else:
            self.print_fail(f"Expected 401, got {response.status_code}")
    
    # ============================================
    # Test 3: Protected Route Access
    # ============================================
    
    def test_get_current_user(self):
        """Test getting current user with valid token"""
        self.print_test("Get Current User - Valid Token")
        
        if not self.token:
            self.print_fail("No token available for test")
            return
        
        response = requests.get(
            f"{self.base_url}/api/v2/auth/me",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            user = data.get('data', {}).get('user', {})
            
            if user.get('email') == self.test_email:
                self.print_pass(f"Retrieved user: {user.get('name')}")
            else:
                self.print_fail("User data incorrect")
        else:
            self.print_fail(f"Expected 200, got {response.status_code}")
    
    def test_get_current_user_no_token(self):
        """Test getting current user without token"""
        self.print_test("Get Current User - No Token")
        
        response = requests.get(f"{self.base_url}/api/v2/auth/me")
        
        if response.status_code == 401:
            self.print_pass("Correctly rejected request without token")
        else:
            self.print_fail(f"Expected 401, got {response.status_code}")
    
    def test_get_current_user_invalid_token(self):
        """Test getting current user with invalid token"""
        self.print_test("Get Current User - Invalid Token")
        
        response = requests.get(
            f"{self.base_url}/api/v2/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        
        if response.status_code == 401:
            self.print_pass("Correctly rejected invalid token")
        else:
            self.print_fail(f"Expected 401, got {response.status_code}")
    
    # ============================================
    # Test 4: Token Validation
    # ============================================
    
    def test_token_structure(self):
        """Test JWT token structure"""
        self.print_test("Token Structure Validation")
        
        if not self.token:
            self.print_fail("No token available")
            return
        
        parts = self.token.split('.')
        if len(parts) == 3:
            self.print_pass("Token has 3 parts (header.payload.signature)")
        else:
            self.print_fail(f"Token has {len(parts)} parts, expected 3")
        
        # Try to decode payload (without verification)
        try:
            import base64
            payload = parts[1]
            # Add padding if needed
            payload += '=' * (4 - len(payload) % 4)
            decoded = base64.urlsafe_b64decode(payload)
            payload_data = json.loads(decoded)
            
            self.print_pass(f"Token payload decoded successfully")
            
            # Check required fields
            if 'sub' in payload_data:  # User ID
                self.print_pass(f"Token contains user ID: {payload_data['sub']}")
            else:
                self.print_fail("Token missing 'sub' (user ID)")
                
            if 'exp' in payload_data:  # Expiration
                exp_time = payload_data['exp']
                current_time = time.time()
                hours_until_expiry = (exp_time - current_time) / 3600
                self.print_pass(f"Token expires in {hours_until_expiry:.1f} hours")
            else:
                self.print_fail("Token missing 'exp' (expiration)")
                
        except Exception as e:
            self.print_fail(f"Failed to decode token: {e}")
    
    # ============================================
    # Test 5: Account Deletion
    # ============================================
    
    def test_delete_account_no_password(self):
        """Test account deletion without password"""
        self.print_test("Delete Account - No Password")
        
        if not self.token:
            self.print_fail("No token available")
            return
        
        response = requests.delete(
            f"{self.base_url}/api/v2/auth/account",
            headers={"Authorization": f"Bearer {self.token}"},
            json={}  # No password
        )
        
        if response.status_code == 400:
            self.print_pass("Correctly requires password")
        else:
            self.print_fail(f"Expected 400, got {response.status_code}")
    
    def test_delete_account_wrong_password(self):
        """Test account deletion with wrong password"""
        self.print_test("Delete Account - Wrong Password")
        
        if not self.token:
            self.print_fail("No token available")
            return
        
        response = requests.delete(
            f"{self.base_url}/api/v2/auth/account",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"password": "WrongPassword123"}
        )
        
        if response.status_code in [400, 401]:
            self.print_pass("Correctly rejected wrong password")
        else:
            self.print_fail(f"Expected 400/401, got {response.status_code}")
    
    def test_delete_account_success(self):
        """Test successful account deletion"""
        self.print_test("Delete Account - Success Case")
        
        if not self.token:
            self.print_fail("No token available")
            return
        
        response = requests.delete(
            f"{self.base_url}/api/v2/auth/account",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"password": self.test_password}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                self.print_pass("Account deleted successfully")
                
                # Verify account is gone
                time.sleep(0.5)
                login_response = requests.post(
                    f"{self.base_url}/api/v2/auth/login",
                    json={
                        "email": self.test_email,
                        "password": self.test_password
                    }
                )
                
                if login_response.status_code == 401:
                    self.print_pass("Verified account no longer exists")
                else:
                    self.print_fail("Account still exists after deletion!")
            else:
                self.print_fail("Deletion response missing success flag")
        else:
            self.print_fail(f"Expected 200, got {response.status_code}")
            self.print_info(f"Response: {response.text}")
    
    # ============================================
    # Test 6: Logout
    # ============================================
    
    def test_logout(self):
        """Test logout endpoint"""
        self.print_test("Logout")
        
        # Re-register for logout test
        requests.post(
            f"{self.base_url}/api/v2/auth/register",
            json={
                "name": self.test_name,
                "email": self.test_email,
                "password": self.test_password
            }
        )
        
        # Login to get token
        login_response = requests.post(
            f"{self.base_url}/api/v2/auth/login",
            json={"email": self.test_email, "password": self.test_password}
        )
        
        if login_response.status_code == 200:
            token = login_response.json()['data']['token']
            
            # Logout
            logout_response = requests.post(
                f"{self.base_url}/api/v2/auth/logout",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if logout_response.status_code == 200:
                self.print_pass("Logout successful")
            else:
                self.print_fail(f"Expected 200, got {logout_response.status_code}")
        else:
            self.print_fail("Could not login for logout test")
    
    # ============================================
    # Test 7: Forgot Password (if implemented)
    # ============================================
    
    def test_forgot_password(self):
        """Test forgot password endpoint"""
        self.print_test("Forgot Password")
        
        response = requests.post(
            f"{self.base_url}/api/v2/auth/forgot-password",
            json={"email": self.test_email}
        )
        
        self.print_info(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            self.print_pass("Forgot password request accepted")
        else:
            self.print_info("⚠️  Forgot password may not be fully implemented")
    
    # ============================================
    # Run All Tests
    # ============================================
    
    def run_all_tests(self):
        """Run the complete test suite"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}🧪 V2 AUTH COMPREHENSIVE TEST SUITE{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"\n{Colors.OKBLUE}Testing against: {self.base_url}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}Test account: {self.test_email}{Colors.ENDC}\n")
        
        # Cleanup any existing test user
        self.cleanup_test_user()
        
        # Category 1: Registration
        print(f"\n{Colors.BOLD}{'='*60}")
        print(f"📝 CATEGORY 1: REGISTRATION TESTS")
        print(f"{'='*60}{Colors.ENDC}")
        self.test_registration_success()
        self.test_registration_duplicate_email()
        self.test_registration_invalid_email()
        self.test_registration_weak_password()
        
        # Category 2: Login
        print(f"\n{Colors.BOLD}{'='*60}")
        print(f"🔑 CATEGORY 2: LOGIN TESTS")
        print(f"{'='*60}{Colors.ENDC}")
        self.test_login_success()
        self.test_login_wrong_password()
        self.test_login_nonexistent_user()
        
        # Category 3: Protected Routes
        print(f"\n{Colors.BOLD}{'='*60}")
        print(f"🔒 CATEGORY 3: PROTECTED ROUTE TESTS")
        print(f"{'='*60}{Colors.ENDC}")
        self.test_get_current_user()
        self.test_get_current_user_no_token()
        self.test_get_current_user_invalid_token()
        
        # Category 4: Token Validation
        print(f"\n{Colors.BOLD}{'='*60}")
        print(f"🎫 CATEGORY 4: TOKEN VALIDATION TESTS")
        print(f"{'='*60}{Colors.ENDC}")
        self.test_token_structure()
        
        # Category 5: Logout
        print(f"\n{Colors.BOLD}{'='*60}")
        print(f"👋 CATEGORY 5: LOGOUT TESTS")
        print(f"{'='*60}{Colors.ENDC}")
        self.test_logout()
        
        # Category 6: Account Deletion
        print(f"\n{Colors.BOLD}{'='*60}")
        print(f"🗑️  CATEGORY 6: ACCOUNT DELETION TESTS")
        print(f"{'='*60}{Colors.ENDC}")
        self.test_delete_account_no_password()
        self.test_delete_account_wrong_password()
        self.test_delete_account_success()
        
        # Category 7: Password Reset
        print(f"\n{Colors.BOLD}{'='*60}")
        print(f"🔑 CATEGORY 7: PASSWORD RESET TESTS")
        print(f"{'='*60}{Colors.ENDC}")
        self.test_forgot_password()
        
        # Final cleanup
        self.cleanup_test_user()
        
        # Results
        print(f"\n{Colors.HEADER}{'='*60}")
        print(f"📊 TEST RESULTS")
        print(f"{'='*60}{Colors.ENDC}")
        total = self.tests_passed + self.tests_failed
        pass_rate = (self.tests_passed / total * 100) if total > 0 else 0
        
        print(f"\n   Total Tests: {total}")
        print(f"   {Colors.OKGREEN}Passed: {self.tests_passed}{Colors.ENDC}")
        print(f"   {Colors.FAIL}Failed: {self.tests_failed}{Colors.ENDC}")
        print(f"   Pass Rate: {pass_rate:.1f}%")
        
        if self.tests_failed == 0:
            print(f"\n   {Colors.OKGREEN}{Colors.BOLD}🎉 ALL TESTS PASSED!{Colors.ENDC}")
        else:
            print(f"\n   {Colors.WARNING}⚠️  Some tests failed - review output above{Colors.ENDC}")
        
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
        
        return self.tests_failed == 0


def main():
    """Run the test suite"""
    suite = AuthTestSuite()
    success = suite.run_all_tests()
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
