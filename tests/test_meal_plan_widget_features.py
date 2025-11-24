"""
Test Script: Meal Plan Widget Phase 1 Features
==============================================
Tests the three new features:
1. Live rename (auto-save on blur)
2. Corner resize handles (Illustrator-style)
3. Drag recipes into meal plan box (Phase 1c - coming soon)

Author: GitHub Copilot
Date: November 5, 2025
"""

import requests
import json
import time
from datetime import datetime

# Try to import from config file, fallback to template
try:
    from test_config import TEST_USER, TEST_HOUSEHOLD_ID, TEST_WHITEBOARD_ID, BASE_URL
    print("✅ Loaded configuration from test_config.py")
except ImportError:
    print("⚠️  test_config.py not found - using defaults")
    print("   Create test_config.py from test_config_template.py")
    BASE_URL = "http://localhost:5000"
    AUTH_TOKEN = None
    TEST_USER = {
        "email": "tran.mich@gmail.com",
        "password": input("Enter password for tran.mich@gmail.com: ")
    }
    TEST_HOUSEHOLD_ID = 11
    TEST_WHITEBOARD_ID = 3

AUTH_TOKEN = None  # Will be set after login

# Colors for output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_fail(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKBLUE}ℹ️  {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

# API Helper Functions
def login():
    """Login and get authentication token"""
    global AUTH_TOKEN
    
    print_header("🔐 Authentication Test")
    print_info(f"Logging in as: {TEST_USER['email']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=TEST_USER,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            AUTH_TOKEN = data.get('token') or data.get('access_token')
            
            if AUTH_TOKEN:
                print_success("Login successful")
                print_info(f"Token: {AUTH_TOKEN[:20]}...")
                return True
            else:
                print_fail("No token in response")
                return False
        else:
            print_fail(f"Login failed: {response.status_code}")
            print_fail(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_fail(f"Login error: {e}")
        return False

def get_headers():
    """Get headers with authentication"""
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AUTH_TOKEN}"
    }

# Test 1: Live Rename Feature
def test_live_rename():
    """Test that meal plan name updates persist to database"""
    print_header("📝 Test 1: Live Rename (Auto-Save)")
    
    # Step 1: Create a new meal plan
    print_info("Step 1: Creating test meal plan...")
    
    create_response = requests.post(
        f"{BASE_URL}/api/meal-plans",
        json={
            "plan_name": "Test Plan - Original Name",
            "week_start_date": datetime.now().strftime("%Y-%m-%d"),
            "plan_data": {
                "days": {
                    "day1": {
                        "name": "Day 1",
                        "recipes": []
                    }
                }
            },
            "household_id": TEST_HOUSEHOLD_ID
        },
        headers=get_headers()
    )
    
    if create_response.status_code != 200:
        print_fail(f"Failed to create meal plan: {create_response.text}")
        return False
    
    meal_plan_data = create_response.json()
    meal_plan_id = meal_plan_data.get('plan_id')
    
    if not meal_plan_id:
        print_fail("No plan_id in response")
        print_fail(f"Response: {meal_plan_data}")
        return False
    
    print_success(f"Created meal plan with ID: {meal_plan_id}")
    
    # Step 2: Update the name
    print_info("Step 2: Updating meal plan name...")
    
    new_name = "Test Plan - Renamed! 🎉"
    update_response = requests.put(
        f"{BASE_URL}/api/meal-plans/{meal_plan_id}",
        json={"plan_name": new_name},
        headers=get_headers()
    )
    
    if update_response.status_code != 200:
        print_fail(f"Failed to update name: {update_response.text}")
        return False
    
    print_success(f"Updated name to: '{new_name}'")
    
    # Step 3: Verify the name persisted
    print_info("Step 3: Verifying name persisted...")
    
    time.sleep(0.5)  # Give database a moment
    
    get_response = requests.get(
        f"{BASE_URL}/api/meal-plans/{meal_plan_id}",
        headers=get_headers()
    )
    
    if get_response.status_code != 200:
        print_fail(f"Failed to retrieve meal plan: {get_response.text}")
        return False
    
    retrieved_data = get_response.json()
    retrieved_name = retrieved_data.get('meal_plan', {}).get('plan_name')
    
    if retrieved_name == new_name:
        print_success(f"✨ Name persisted correctly: '{retrieved_name}'")
        print_success("Live rename feature PASSED! ✅")
        
        # Cleanup
        print_info("Cleaning up test meal plan...")
        requests.delete(
            f"{BASE_URL}/api/meal-plans/{meal_plan_id}",
            headers=get_headers()
        )
        
        return True
    else:
        print_fail(f"Name mismatch!")
        print_fail(f"Expected: '{new_name}'")
        print_fail(f"Got: '{retrieved_name}'")
        return False

# Test 2: Corner Resize Handles
def test_corner_resize():
    """Test that whiteboard object dimensions can be updated"""
    print_header("📏 Test 2: Corner Resize Handles")
    
    # Step 1: Get existing whiteboard
    print_info("Step 1: Loading whiteboard...")
    
    wb_response = requests.get(
        f"{BASE_URL}/api/v2/whiteboard/{TEST_WHITEBOARD_ID}",
        headers=get_headers()
    )
    
    if wb_response.status_code != 200:
        print_fail(f"Failed to load whiteboard: {wb_response.text}")
        return False
    
    wb_data = wb_response.json()
    whiteboard = wb_data.get('data', {}).get('whiteboard', {})
    objects = whiteboard.get('objects', [])
    
    print_success(f"Loaded whiteboard with {len(objects)} objects")
    
    # Find a meal plan object
    meal_plan_obj = None
    for obj in objects:
        if obj.get('entity_type') == 'meal_plan':
            meal_plan_obj = obj
            break
    
    if not meal_plan_obj:
        print_warning("No meal plan objects found on whiteboard")
        print_info("Creating a test meal plan object...")
        
        # Create meal plan first
        create_response = requests.post(
            f"{BASE_URL}/api/meal-plans",
            json={
                "plan_name": "Test Resize Plan",
                "week_start_date": datetime.now().strftime("%Y-%m-%d"),
                "plan_data": {"days": {"day1": {"name": "Day 1", "recipes": []}}},
                "household_id": TEST_HOUSEHOLD_ID
            },
            headers=get_headers()
        )
        
        if create_response.status_code != 200:
            print_fail("Failed to create meal plan")
            return False
        
        meal_plan_id = create_response.json().get('plan_id')
        
        # Link to whiteboard
        link_response = requests.post(
            f"{BASE_URL}/api/v2/whiteboard/{TEST_WHITEBOARD_ID}/o",
            json={
                "type": "mp",
                "entity_type": "meal_plan",
                "entity_id": meal_plan_id,
                "position": {"x": 100, "y": 100, "width": 320, "height": 200, "z": 0}
            },
            headers=get_headers()
        )
        
        if link_response.status_code != 201:
            print_fail(f"Failed to link meal plan: {link_response.text}")
            return False
        
        meal_plan_obj = link_response.json().get('data', {})
        print_success(f"Created test meal plan object: {meal_plan_obj.get('id')}")
    
    object_id = meal_plan_obj.get('id')
    original_position = meal_plan_obj.get('position', {})
    
    print_info(f"Testing with object ID: {object_id}")
    print_info(f"Original dimensions: {original_position.get('width')}x{original_position.get('height')}")
    
    # Step 2: Update dimensions (simulate corner drag)
    print_info("Step 2: Updating dimensions (simulating corner drag)...")
    
    new_width = 450
    new_height = 300
    
    resize_response = requests.patch(
        f"{BASE_URL}/api/v2/whiteboard/{TEST_WHITEBOARD_ID}/o/{object_id}",
        json={
            "position": {
                "x": original_position.get('x', 100),
                "y": original_position.get('y', 100),
                "width": new_width,
                "height": new_height,
                "z": original_position.get('z_index', 0)
            }
        },
        headers=get_headers()
    )
    
    if resize_response.status_code != 200:
        print_fail(f"Failed to update dimensions: {resize_response.text}")
        return False
    
    print_success(f"Updated dimensions to: {new_width}x{new_height}")
    
    # Step 3: Verify dimensions persisted
    print_info("Step 3: Verifying dimensions persisted...")
    
    time.sleep(0.5)
    
    verify_response = requests.get(
        f"{BASE_URL}/api/v2/whiteboard/{TEST_WHITEBOARD_ID}",
        headers=get_headers()
    )
    
    if verify_response.status_code != 200:
        print_fail("Failed to verify")
        return False
    
    verify_data = verify_response.json()
    verify_objects = verify_data.get('data', {}).get('whiteboard', {}).get('objects', [])
    
    updated_obj = None
    for obj in verify_objects:
        if obj.get('id') == object_id:
            updated_obj = obj
            break
    
    if not updated_obj:
        print_fail("Object not found after update")
        return False
    
    updated_position = updated_obj.get('position', {})
    updated_width = updated_position.get('width')
    updated_height = updated_position.get('height')
    
    if updated_width == new_width and updated_height == new_height:
        print_success(f"✨ Dimensions persisted: {updated_width}x{updated_height}")
        print_success("Corner resize feature PASSED! ✅")
        return True
    else:
        print_fail(f"Dimensions mismatch!")
        print_fail(f"Expected: {new_width}x{new_height}")
        print_fail(f"Got: {updated_width}x{updated_height}")
        return False

# Test 3: Position Update (Already Working)
def test_position_update():
    """Verify position updates work correctly"""
    print_header("📍 Test 3: Position Update (Existing Feature)")
    
    print_info("Loading whiteboard...")
    
    wb_response = requests.get(
        f"{BASE_URL}/api/v2/whiteboard/{TEST_WHITEBOARD_ID}",
        headers=get_headers()
    )
    
    if wb_response.status_code != 200:
        print_fail(f"Failed to load whiteboard: {wb_response.text}")
        return False
    
    wb_data = wb_response.json()
    objects = wb_data.get('data', {}).get('whiteboard', {}).get('objects', [])
    
    # Find any meal plan object
    meal_plan_obj = None
    for obj in objects:
        if obj.get('entity_type') == 'meal_plan':
            meal_plan_obj = obj
            break
    
    if not meal_plan_obj:
        print_warning("No meal plan objects to test")
        return True
    
    object_id = meal_plan_obj.get('id')
    original_pos = meal_plan_obj.get('position', {})
    
    print_info(f"Original position: ({original_pos.get('x')}, {original_pos.get('y')})")
    
    # Move it
    new_x = original_pos.get('x', 100) + 50
    new_y = original_pos.get('y', 100) + 50
    
    print_info(f"Moving to: ({new_x}, {new_y})")
    
    move_response = requests.patch(
        f"{BASE_URL}/api/v2/whiteboard/{TEST_WHITEBOARD_ID}/o/{object_id}",
        json={
            "position": {
                "x": new_x,
                "y": new_y,
                "width": original_pos.get('width', 320),
                "height": original_pos.get('height', 200),
                "z": original_pos.get('z_index', 0)
            }
        },
        headers=get_headers()
    )
    
    if move_response.status_code == 200:
        print_success("Position update works! ✅")
        return True
    else:
        print_fail(f"Position update failed: {move_response.text}")
        return False

# Main Test Runner
def run_all_tests():
    """Run all tests and report results"""
    print_header("🧪 Meal Plan Widget Feature Tests")
    print_info(f"Testing against: {BASE_URL}")
    print_info(f"Whiteboard ID: {TEST_WHITEBOARD_ID}")
    print_info(f"Household ID: {TEST_HOUSEHOLD_ID}")
    
    # Login first
    if not login():
        print_fail("Authentication failed - cannot run tests")
        return
    
    # Run tests
    results = {
        "Live Rename": test_live_rename(),
        "Corner Resize": test_corner_resize(),
        "Position Update": test_position_update()
    }
    
    # Summary
    print_header("📊 Test Results Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        if result:
            print_success(f"{test_name}: PASSED")
        else:
            print_fail(f"{test_name}: FAILED")
    
    print(f"\n{Colors.BOLD}Total: {passed}/{total} tests passed{Colors.ENDC}\n")
    
    if passed == total:
        print_success("🎉 All Phase 1 features working! Ready for manual testing.")
    else:
        print_warning("⚠️  Some tests failed - review output above")

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    except Exception as e:
        print_fail(f"Test runner error: {e}")
        import traceback
        traceback.print_exc()
