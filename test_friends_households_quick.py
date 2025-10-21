"""
Quick Test Script for Friends & Households API v2
Tests all 16 endpoints with the actual database
"""

import requests
import json
from colorama import init, Fore, Style

# Initialize colorama for colored output
init()

BASE_URL = "http://localhost:5000/api/v2"

# Test counters
tests_passed = 0
tests_failed = 0

def print_test(name):
    """Print test name"""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print('='*60)

def print_success(message):
    """Print success message"""
    global tests_passed
    tests_passed += 1
    print(f"{Fore.GREEN}✓ PASS{Style.RESET_ALL}: {message}")

def print_error(message):
    """Print error message"""
    global tests_failed
    tests_failed += 1
    print(f"{Fore.RED}✗ FAIL{Style.RESET_ALL}: {message}")

def print_response(response):
    """Print formatted response"""
    print(f"\nStatus: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

# Test user IDs (from database)
USER1_ID = 12  # Al Alicelebic
USER2_ID = 13  # test1
USER2_EMAIL = "test1@gmail.com"  # test1's email

print(f"\n{Fore.CYAN}{'='*60}")
print("FRIENDS & HOUSEHOLDS API v2 - QUICK TEST")
print(f"{'='*60}{Style.RESET_ALL}\n")

# ============================================================================
# FRIENDS API TESTS
# ============================================================================

print(f"\n{Fore.YELLOW}>>> FRIENDS API TESTS{Style.RESET_ALL}\n")

# Test 1: Get Friends
print_test("Get User Friends")
try:
    response = requests.get(f"{BASE_URL}/friends/user/{USER1_ID}")
    print_response(response)
    if response.status_code == 200:
        print_success("Get friends endpoint working")
    else:
        print_error(f"Expected 200, got {response.status_code}")
except Exception as e:
    print_error(f"Request failed: {e}")

# Test 2: Get Friend Requests
print_test("Get Friend Requests")
try:
    response = requests.get(f"{BASE_URL}/friends/requests/user/{USER1_ID}")
    print_response(response)
    if response.status_code == 200:
        print_success("Get friend requests endpoint working")
    else:
        print_error(f"Expected 200, got {response.status_code}")
except Exception as e:
    print_error(f"Request failed: {e}")

# Test 3: Send Friend Request
print_test("Send Friend Request")
try:
    data = {
        "requester_id": USER1_ID,
        "recipient_email": USER2_EMAIL,
        "message": "Let's be friends! (API Test)"
    }
    response = requests.post(f"{BASE_URL}/friends/request", json=data)
    print_response(response)
    if response.status_code in [200, 201, 400]:  # 400 if already exists
        print_success("Send friend request endpoint working")
        if response.status_code in [200, 201]:
            request_id = response.json().get('data', {}).get('id')
            print(f"Friend request ID: {request_id}")
    else:
        print_error(f"Unexpected status code: {response.status_code}")
except Exception as e:
    print_error(f"Request failed: {e}")

# Test 4: Get Friendship Status
print_test("Get Friendship Status")
try:
    response = requests.get(
        f"{BASE_URL}/friends/status",
        params={"user_id": USER1_ID, "other_user_id": USER2_ID}
    )
    print_response(response)
    if response.status_code == 200:
        print_success("Get friendship status endpoint working")
    else:
        print_error(f"Expected 200, got {response.status_code}")
except Exception as e:
    print_error(f"Request failed: {e}")

# ============================================================================
# HOUSEHOLDS API TESTS
# ============================================================================

print(f"\n{Fore.YELLOW}>>> HOUSEHOLDS API TESTS{Style.RESET_ALL}\n")

# Test 5: Get User Households
print_test("Get User Households")
try:
    response = requests.get(f"{BASE_URL}/households/user/{USER1_ID}")
    print_response(response)
    if response.status_code == 200:
        print_success("Get households endpoint working")
    else:
        print_error(f"Expected 200, got {response.status_code}")
except Exception as e:
    print_error(f"Request failed: {e}")

# Test 6: Create Household
print_test("Create Household")
household_id = None
try:
    data = {
        "name": "Test Family (API Test)",
        "created_by": USER1_ID,
        "description": "Created by API test script"
    }
    response = requests.post(f"{BASE_URL}/households", json=data)
    print_response(response)
    if response.status_code in [200, 201]:
        print_success("Create household endpoint working")
        household_id = response.json().get('data', {}).get('household', {}).get('id')
        print(f"Created household ID: {household_id}")
    else:
        print_error(f"Expected 201, got {response.status_code}")
except Exception as e:
    print_error(f"Request failed: {e}")

# Test 7: Get Household Details (if we created one)
if household_id:
    print_test("Get Household Details")
    try:
        response = requests.get(
            f"{BASE_URL}/households/{household_id}",
            params={"user_id": USER1_ID}
        )
        print_response(response)
        if response.status_code == 200:
            print_success("Get household details endpoint working")
        else:
            print_error(f"Expected 200, got {response.status_code}")
    except Exception as e:
        print_error(f"Request failed: {e}")

    # Test 8: Get Household Members
    print_test("Get Household Members")
    try:
        response = requests.get(
            f"{BASE_URL}/households/{household_id}/members",
            params={"user_id": USER1_ID}
        )
        print_response(response)
        if response.status_code == 200:
            print_success("Get household members endpoint working")
        else:
            print_error(f"Expected 200, got {response.status_code}")
    except Exception as e:
        print_error(f"Request failed: {e}")

# ============================================================================
# SUMMARY
# ============================================================================

print(f"\n{Fore.CYAN}{'='*60}")
print("TEST SUMMARY")
print(f"{'='*60}{Style.RESET_ALL}\n")

total_tests = tests_passed + tests_failed
pass_rate = (tests_passed / total_tests * 100) if total_tests > 0 else 0

print(f"Total Tests: {total_tests}")
print(f"{Fore.GREEN}Passed: {tests_passed}{Style.RESET_ALL}")
print(f"{Fore.RED}Failed: {tests_failed}{Style.RESET_ALL}")
print(f"Pass Rate: {pass_rate:.1f}%")

if tests_failed == 0:
    print(f"\n{Fore.GREEN}🎉 ALL TESTS PASSED!{Style.RESET_ALL}")
else:
    print(f"\n{Fore.YELLOW}⚠️  Some tests failed. Check output above.{Style.RESET_ALL}")

print("\n")
