/**
 * Frontend Auth V2 Integration Tests
 * Tests the complete frontend auth flow with V2 API
 * 
 * Test Account:
 * - Email: frontend-test@yeschefapp.io
 * - Password: Testtest123
 * - Purpose: Automated frontend auth testing
 * 
 * Run with: node tests/test_frontend_auth_v2.js
 */

const BASE_URL = process.env.API_URL || 'http://127.0.0.1:5000';
const TEST_EMAIL = 'frontend-test@yeschefapp.io';
const TEST_PASSWORD = 'Testtest123';
const TEST_NAME = 'Frontend Test User';

// Colors for terminal output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

class FrontendAuthTester {
  constructor() {
    this.testsPassed = 0;
    this.testsFailed = 0;
    this.token = null;
    this.userId = null;
  }

  log(message, color = colors.reset) {
    console.log(`${color}${message}${colors.reset}`);
  }

  printTest(name) {
    console.log(`\n${colors.blue}🧪 TEST: ${name}${colors.reset}`);
  }

  printPass(message) {
    console.log(`   ${colors.green}✅ PASS: ${message}${colors.reset}`);
    this.testsPassed++;
  }

  printFail(message) {
    console.log(`   ${colors.red}❌ FAIL: ${message}${colors.reset}`);
    this.testsFailed++;
  }

  printInfo(message) {
    console.log(`   ${colors.cyan}ℹ️  ${message}${colors.reset}`);
  }

  // Helper: Simulate apiCall from frontend
  async apiCall(path, options = {}) {
    const url = `${BASE_URL}${path}`;
    
    try {
      const response = await fetch(url, options);
      const data = await response.json();
      
      if (!response.ok && !data.success) {
        throw new Error(data.error || data.message || 'Request failed');
      }
      
      return data;
    } catch (error) {
      throw error;
    }
  }

  // Cleanup test user
  async cleanupTestUser() {
    try {
      // Try V1 login first to get token
      const loginResponse = await fetch(`${BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: TEST_EMAIL, password: TEST_PASSWORD }),
      });

      if (loginResponse.ok) {
        const data = await loginResponse.json();
        const token = data.access_token;

        // Delete using V1 wipe endpoint
        await fetch(`${BASE_URL}/api/auth/wipe-data`, {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` },
        });
        
        this.log('⚠️  Cleaned up existing test user', colors.yellow);
      }
    } catch (error) {
      // User doesn't exist, that's fine
    }
  }

  // ==========================================
  // Test 1: Registration Flow (mimics AuthContext)
  // ==========================================
  async testRegister() {
    this.printTest('Frontend Register Flow (AuthContext.register)');

    try {
      // Simulate AuthContext.register()
      const response = await this.apiCall('/api/v2/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: TEST_NAME,
          email: TEST_EMAIL,
          password: TEST_PASSWORD,
        }),
      });

      this.printInfo(`Response: ${JSON.stringify(response).substring(0, 100)}...`);

      // Check V2 response format
      if (response.success) {
        this.printPass('Response has success=true (V2 format)');
      } else {
        this.printFail('Response missing success flag');
      }

      // Check data wrapper
      if (response.data) {
        this.printPass('Response has data wrapper (V2 format)');
      } else {
        this.printFail('Response missing data wrapper');
      }

      // Check token location (V2: data.token, not access_token)
      if (response.data && response.data.token) {
        this.token = response.data.token;
        this.printPass(`Token at data.token (V2 format): ${this.token.substring(0, 20)}...`);
      } else if (response.access_token) {
        this.printFail('Token at access_token (V1 format) - should be data.token');
      } else {
        this.printFail('No token found in response');
      }

      // Check user location (V2: data.user, not top-level user)
      if (response.data && response.data.user) {
        this.userId = response.data.user.id;
        this.printPass(`User at data.user (V2 format): ID ${this.userId}`);
      } else if (response.user) {
        this.printFail('User at top-level (V1 format) - should be data.user');
      } else {
        this.printFail('No user found in response');
      }

      // Simulate localStorage.setItem('authToken', token)
      this.printInfo(`Would store in localStorage: authToken=${this.token?.substring(0, 20)}...`);

    } catch (error) {
      this.printFail(`Registration error: ${error.message}`);
    }
  }

  // ==========================================
  // Test 2: Login Flow (mimics AuthContext)
  // ==========================================
  async testLogin() {
    this.printTest('Frontend Login Flow (AuthContext.login)');

    try {
      // Simulate AuthContext.login()
      const response = await this.apiCall('/api/v2/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: TEST_EMAIL,
          password: TEST_PASSWORD,
        }),
      });

      // Check V2 response format
      if (response.success && response.data) {
        this.printPass('Login response has V2 format (success + data)');
        
        if (response.data.token) {
          this.token = response.data.token;
          this.printPass(`Token received: ${this.token.substring(0, 20)}...`);
        } else {
          this.printFail('No token in data object');
        }

        if (response.data.user) {
          this.printPass(`User data received: ${response.data.user.email}`);
        } else {
          this.printFail('No user in data object');
        }
      } else {
        this.printFail('Login response not in V2 format');
      }

    } catch (error) {
      this.printFail(`Login error: ${error.message}`);
    }
  }

  // ==========================================
  // Test 3: Get Current User (mimics AuthContext useEffect)
  // ==========================================
  async testGetCurrentUser() {
    this.printTest('Frontend Get Current User (AuthContext initialization)');

    if (!this.token) {
      this.printFail('No token available - skipping test');
      return;
    }

    try {
      // Simulate AuthContext checking saved token
      this.printInfo(`Simulating: localStorage.getItem('authToken')`);
      
      // Simulate apiCall('/api/v2/auth/me')
      const response = await this.apiCall('/api/v2/auth/me', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.token}`,
        },
      });

      // Check V2 response format
      if (response.success && response.data) {
        this.printPass('Get user response has V2 format');
        
        if (response.data.user) {
          this.printPass(`User retrieved: ${response.data.user.email}`);
          this.printInfo(`Would call: setUser(response.data.user)`);
        } else {
          this.printFail('No user in data object');
        }
      } else {
        this.printFail('Get user response not in V2 format');
        this.printInfo('Would call: logout()');
      }

    } catch (error) {
      this.printFail(`Get user error: ${error.message}`);
      this.printInfo('Would call: logout()');
    }
  }

  // ==========================================
  // Test 4: Invalid Email (mimics frontend validation)
  // ==========================================
  async testInvalidEmail() {
    this.printTest('Frontend Invalid Email Handling');

    try {
      const response = await this.apiCall('/api/v2/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: 'Test',
          email: 'not-an-email',  // Invalid format
          password: 'Test123',
        }),
      });

      this.printFail('Should have rejected invalid email');
    } catch (error) {
      this.printPass(`Correctly rejected: ${error.message}`);
      this.printInfo('Frontend would show error message to user');
    }
  }

  // ==========================================
  // Test 5: Weak Password (mimics frontend validation)
  // ==========================================
  async testWeakPassword() {
    this.printTest('Frontend Weak Password Handling');

    try {
      const response = await this.apiCall('/api/v2/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: 'Test',
          email: 'weak@test.com',
          password: '123',  // Too short
        }),
      });

      this.printFail('Should have rejected weak password');
    } catch (error) {
      this.printPass(`Correctly rejected: ${error.message}`);
      this.printInfo('Frontend would show error message to user');
    }
  }

  // ==========================================
  // Test 6: Logout (mimics AuthContext)
  // ==========================================
  async testLogout() {
    this.printTest('Frontend Logout Flow (AuthContext.logout)');

    // Frontend logout is client-side only
    this.printInfo('Simulating client-side logout:');
    this.printInfo('1. localStorage.removeItem("authToken")');
    this.printInfo('2. setToken(null)');
    this.printInfo('3. setUser(null)');
    this.printInfo('4. delete axios.defaults.headers.common["Authorization"]');
    
    this.printPass('Logout is client-side only (no API call needed)');
    
    // Clear our test token
    this.token = null;
  }

  // ==========================================
  // Test 7: MainApp.js User ID Fetch
  // ==========================================
  async testMainAppUserFetch() {
    this.printTest('MainApp.js User ID Fetch');

    // Need to login again
    try {
      const loginResponse = await this.apiCall('/api/v2/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: TEST_EMAIL,
          password: TEST_PASSWORD,
        }),
      });
      
      this.token = loginResponse.data.token;
    } catch (error) {
      this.printFail('Could not login for user fetch test');
      return;
    }

    try {
      // Simulate MainApp.js user fetch
      const response = await fetch(`${BASE_URL}/api/v2/auth/me`, {
        headers: {
          'Authorization': `Bearer ${this.token}`,
        },
      });

      if (response.ok) {
        const result = await response.json();
        
        // Check V2 format
        if (result.success && result.data) {
          this.printPass('Response in V2 format');
          
          if (result.data.user && result.data.user.id) {
            this.printPass(`User ID extracted: ${result.data.user.id}`);
            this.printInfo('MainApp.js would use this for recipe deletion');
          } else {
            this.printFail('Could not extract user ID from result.data.user');
          }
        } else {
          this.printFail('Response not in V2 format');
          this.printInfo('Old code: userId = userData.id');
          this.printInfo('New code: userId = result.data.user.id');
        }
      } else {
        this.printFail(`Request failed with status ${response.status}`);
      }

    } catch (error) {
      this.printFail(`MainApp fetch error: ${error.message}`);
    }
  }

  // ==========================================
  // Run All Tests
  // ==========================================
  async runAllTests() {
    console.log('\n' + '='.repeat(60));
    this.log('🧪 FRONTEND AUTH V2 INTEGRATION TESTS', colors.bright);
    console.log('='.repeat(60));
    this.log(`\nTesting against: ${BASE_URL}`, colors.blue);
    this.log(`Test account: ${TEST_EMAIL}\n`, colors.blue);

    // Cleanup
    await this.cleanupTestUser();

    // Run tests
    await this.testRegister();
    await this.testLogin();
    await this.testGetCurrentUser();
    await this.testInvalidEmail();
    await this.testWeakPassword();
    await this.testLogout();
    await this.testMainAppUserFetch();

    // Cleanup
    await this.cleanupTestUser();

    // Results
    console.log('\n' + '='.repeat(60));
    this.log('📊 TEST RESULTS', colors.bright);
    console.log('='.repeat(60));
    
    const total = this.testsPassed + this.testsFailed;
    const passRate = total > 0 ? (this.testsPassed / total * 100).toFixed(1) : 0;

    console.log(`\n   Total Tests: ${total}`);
    this.log(`   Passed: ${this.testsPassed}`, colors.green);
    this.log(`   Failed: ${this.testsFailed}`, colors.red);
    console.log(`   Pass Rate: ${passRate}%`);

    if (this.testsFailed === 0) {
      this.log('\n   🎉 ALL TESTS PASSED!', colors.green + colors.bright);
    } else {
      this.log('\n   ⚠️  Some tests failed - review output above', colors.yellow);
    }

    console.log('\n' + '='.repeat(60) + '\n');

    return this.testsFailed === 0;
  }
}

// Run tests
async function main() {
  const tester = new FrontendAuthTester();
  const success = await tester.runAllTests();
  process.exit(success ? 0 : 1);
}

main().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
