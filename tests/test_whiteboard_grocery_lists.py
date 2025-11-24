"""
Test Suite for Whiteboard Grocery List API
===========================================
Tests the grocery list endpoints integrated with whiteboards

Endpoints tested:
- POST   /api/v2/whiteboard/{wid}/grocery-lists       (create)
- GET    /api/v2/whiteboard/{wid}/grocery-lists       (list)
- PATCH  /api/v2/whiteboard/{wid}/grocery-lists/{id}  (update)
- DELETE /api/v2/whiteboard/{wid}/grocery-lists/{id}  (delete)

Author: GitHub Copilot
Date: November 4, 2025
"""

import pytest
import json
from datetime import datetime

# Test configuration
BASE_URL = "http://127.0.0.1:5000"
API_VERSION = "v2"

# Test data fixtures
@pytest.fixture
def auth_token():
    """Get valid auth token for testing"""
    # TODO: Replace with your actual test user token
    # For now, use the token from your browser's localStorage
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2MjI3ODU5OCwianRpIjoiM2Q1NGUwY2YtYWRkMC00ZDMzLThlZDctMGJhYTk0MGEwYzQyIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjExIiwibmJmIjoxNzYyMjc4NTk4LCJjc3JmIjoiNzhkZWU4YzctOTUyNC00MWRhLThlMDgtYWE0N2I1ODRiNTU4IiwiZXhwIjoxNzYyMzY0OTk4fQ.BDE3qnUx2YhAvxdwXHz5_vlVMMP4vB6waLnHmM-nvMI"

@pytest.fixture
def headers(auth_token):
    """Request headers with auth"""
    return {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }

@pytest.fixture
def test_whiteboard_id():
    """Test whiteboard ID"""
    return 3  # Replace with your test whiteboard ID

@pytest.fixture
def test_household_id():
    """Test household ID"""
    return 11  # Replace with your test household ID

@pytest.fixture
def sample_grocery_list():
    """Sample grocery list data"""
    return {
        "name": "Test Shopping List",
        "items": [
            {
                "id": "item-1",
                "ingredient": "2 cups flour",
                "quantity": "2 cups",
                "checked": False,
                "source_recipe_id": 2764
            },
            {
                "id": "item-2",
                "ingredient": "1 cup sugar",
                "quantity": "1 cup",
                "checked": False,
                "source_recipe_id": 2754
            },
            {
                "id": "item-3",
                "ingredient": "3 eggs",
                "quantity": "3",
                "checked": True,
                "source_recipe_id": 2764
            }
        ],
        "household_id": 11,
        "widget_position": {
            "x": 800,
            "y": 100,
            "size": "medium"
        },
        "linked_recipe_ids": [2764, 2754]
    }


# =====================================================
# TEST CASES
# =====================================================

class TestGroceryListCreation:
    """Test grocery list creation"""
    
    def test_create_grocery_list_success(self, requests_session, headers, test_whiteboard_id, sample_grocery_list):
        """Test creating a new grocery list on whiteboard"""
        url = f"{BASE_URL}/api/{API_VERSION}/whiteboard/{test_whiteboard_id}/grocery-lists"
        
        response = requests_session.post(url, headers=headers, json=sample_grocery_list)
        
        print(f"\n📤 POST {url}")
        print(f"📦 Request body: {json.dumps(sample_grocery_list, indent=2)}")
        print(f"📥 Status: {response.status_code}")
        print(f"📥 Response: {response.text}")
        
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        
        data = response.json()
        assert data['success'] == True
        assert 'data' in data
        assert 'id' in data['data']
        assert data['data']['name'] == sample_grocery_list['name']
        assert len(data['data']['items']) == 3
        assert data['data']['whiteboard_id'] == test_whiteboard_id
        assert data['data']['household_id'] == sample_grocery_list['household_id']
        
        # Store created ID for other tests
        pytest.created_list_id = data['data']['id']
        
        print(f"✅ Created grocery list with ID: {data['data']['id']}")
    
    def test_create_grocery_list_missing_name(self, requests_session, headers, test_whiteboard_id):
        """Test creating grocery list without name (should fail)"""
        url = f"{BASE_URL}/api/{API_VERSION}/whiteboard/{test_whiteboard_id}/grocery-lists"
        
        invalid_data = {
            "items": [{"ingredient": "test"}],
            "household_id": 11
        }
        
        response = requests_session.post(url, headers=headers, json=invalid_data)
        
        print(f"\n📤 POST {url} (missing name)")
        print(f"📥 Status: {response.status_code}")
        print(f"📥 Response: {response.text}")
        
        assert response.status_code == 400
        data = response.json()
        assert data['success'] == False
        assert 'name' in data['message'].lower()
        
        print(f"✅ Correctly rejected missing name")
    
    def test_create_grocery_list_invalid_whiteboard(self, requests_session, headers, sample_grocery_list):
        """Test creating grocery list on non-existent whiteboard"""
        url = f"{BASE_URL}/api/{API_VERSION}/whiteboard/99999/grocery-lists"
        
        response = requests_session.post(url, headers=headers, json=sample_grocery_list)
        
        print(f"\n📤 POST {url} (invalid whiteboard)")
        print(f"📥 Status: {response.status_code}")
        
        # Should either fail or succeed depending on validation
        # Document actual behavior
        print(f"📋 Response: {response.text}")


class TestGroceryListRetrieval:
    """Test grocery list retrieval"""
    
    def test_get_whiteboard_grocery_lists(self, requests_session, headers, test_whiteboard_id):
        """Test getting all grocery lists for a whiteboard"""
        url = f"{BASE_URL}/api/{API_VERSION}/whiteboard/{test_whiteboard_id}/grocery-lists"
        
        response = requests_session.get(url, headers=headers)
        
        print(f"\n📤 GET {url}")
        print(f"📥 Status: {response.status_code}")
        print(f"📥 Response: {response.text[:500]}")  # First 500 chars
        
        assert response.status_code == 200
        
        data = response.json()
        assert data['success'] == True
        assert 'data' in data
        assert 'grocery_lists' in data['data']
        assert isinstance(data['data']['grocery_lists'], list)
        assert 'count' in data['data']
        
        print(f"✅ Found {data['data']['count']} grocery lists")
        
        # Verify structure of first list if any exist
        if data['data']['count'] > 0:
            first_list = data['data']['grocery_lists'][0]
            assert 'id' in first_list
            assert 'name' in first_list
            assert 'items' in first_list
            assert 'widget_position' in first_list
            assert 'linked_recipe_ids' in first_list
            
            print(f"📋 First list: {first_list['name']} ({len(first_list['items'])} items)")


class TestGroceryListUpdate:
    """Test grocery list updates"""
    
    def test_update_grocery_list_items(self, requests_session, headers, test_whiteboard_id):
        """Test updating grocery list items"""
        # Use the created list ID from creation test
        if not hasattr(pytest, 'created_list_id'):
            pytest.skip("No list created yet")
        
        list_id = pytest.created_list_id
        url = f"{BASE_URL}/api/{API_VERSION}/whiteboard/{test_whiteboard_id}/grocery-lists/{list_id}"
        
        update_data = {
            "items": [
                {
                    "id": "item-1",
                    "ingredient": "2 cups flour",
                    "checked": True  # Changed to checked
                },
                {
                    "id": "item-2",
                    "ingredient": "1 cup sugar",
                    "checked": False
                },
                {
                    "id": "item-4",
                    "ingredient": "1 tsp vanilla",  # New item
                    "checked": False
                }
            ]
        }
        
        response = requests_session.patch(url, headers=headers, json=update_data)
        
        print(f"\n📤 PATCH {url}")
        print(f"📦 Update: {json.dumps(update_data, indent=2)}")
        print(f"📥 Status: {response.status_code}")
        print(f"📥 Response: {response.text}")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data['success'] == True
        assert len(data['data']['items']) == 3
        
        print(f"✅ Updated items successfully")
    
    def test_update_grocery_list_position(self, requests_session, headers, test_whiteboard_id):
        """Test updating widget position"""
        if not hasattr(pytest, 'created_list_id'):
            pytest.skip("No list created yet")
        
        list_id = pytest.created_list_id
        url = f"{BASE_URL}/api/{API_VERSION}/whiteboard/{test_whiteboard_id}/grocery-lists/{list_id}"
        
        update_data = {
            "widget_position": {
                "x": 1200,
                "y": 300,
                "size": "large"
            }
        }
        
        response = requests_session.patch(url, headers=headers, json=update_data)
        
        print(f"\n📤 PATCH {url}")
        print(f"📦 Update position: {json.dumps(update_data, indent=2)}")
        print(f"📥 Status: {response.status_code}")
        print(f"📥 Response: {response.text}")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data['success'] == True
        assert data['data']['widget_position']['x'] == 1200
        assert data['data']['widget_position']['y'] == 300
        assert data['data']['widget_position']['size'] == "large"
        
        print(f"✅ Updated position successfully")
    
    def test_update_grocery_list_name(self, requests_session, headers, test_whiteboard_id):
        """Test updating grocery list name"""
        if not hasattr(pytest, 'created_list_id'):
            pytest.skip("No list created yet")
        
        list_id = pytest.created_list_id
        url = f"{BASE_URL}/api/{API_VERSION}/whiteboard/{test_whiteboard_id}/grocery-lists/{list_id}"
        
        update_data = {
            "name": "Updated Shopping List Name"
        }
        
        response = requests_session.patch(url, headers=headers, json=update_data)
        
        print(f"\n📤 PATCH {url}")
        print(f"📦 Update name: {json.dumps(update_data, indent=2)}")
        print(f"📥 Status: {response.status_code}")
        print(f"📥 Response: {response.text}")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data['success'] == True
        assert data['data']['name'] == "Updated Shopping List Name"
        
        print(f"✅ Updated name successfully")


class TestGroceryListDeletion:
    """Test grocery list deletion"""
    
    def test_delete_grocery_list(self, requests_session, headers, test_whiteboard_id):
        """Test soft deleting a grocery list"""
        if not hasattr(pytest, 'created_list_id'):
            pytest.skip("No list created yet")
        
        list_id = pytest.created_list_id
        url = f"{BASE_URL}/api/{API_VERSION}/whiteboard/{test_whiteboard_id}/grocery-lists/{list_id}"
        
        response = requests_session.delete(url, headers=headers)
        
        print(f"\n📤 DELETE {url}")
        print(f"📥 Status: {response.status_code}")
        print(f"📥 Response: {response.text}")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data['success'] == True
        
        print(f"✅ Deleted grocery list successfully")
        
        # Verify it's gone
        get_url = f"{BASE_URL}/api/{API_VERSION}/whiteboard/{test_whiteboard_id}/grocery-lists"
        response = requests_session.get(get_url, headers=headers)
        data = response.json()
        
        # Should not appear in list anymore
        deleted_list = next((gl for gl in data['data']['grocery_lists'] if gl['id'] == list_id), None)
        assert deleted_list is None, "Deleted list still appears in results"
        
        print(f"✅ Verified list no longer appears in results")
    
    def test_delete_nonexistent_list(self, requests_session, headers, test_whiteboard_id):
        """Test deleting non-existent list"""
        url = f"{BASE_URL}/api/{API_VERSION}/whiteboard/{test_whiteboard_id}/grocery-lists/99999"
        
        response = requests_session.delete(url, headers=headers)
        
        print(f"\n📤 DELETE {url} (non-existent)")
        print(f"📥 Status: {response.status_code}")
        print(f"📥 Response: {response.text}")
        
        assert response.status_code == 404
        
        data = response.json()
        assert data['success'] == False
        
        print(f"✅ Correctly returned 404 for non-existent list")


class TestEdgeCases:
    """Test edge cases and data validation"""
    
    def test_empty_items_list(self, requests_session, headers, test_whiteboard_id):
        """Test creating list with empty items array"""
        url = f"{BASE_URL}/api/{API_VERSION}/whiteboard/{test_whiteboard_id}/grocery-lists"
        
        data = {
            "name": "Empty List",
            "items": [],
            "household_id": 11
        }
        
        response = requests_session.post(url, headers=headers, json=data)
        
        print(f"\n📤 POST {url} (empty items)")
        print(f"📥 Status: {response.status_code}")
        print(f"📥 Response: {response.text}")
        
        # Should succeed - empty list is valid
        assert response.status_code == 201
        
        result = response.json()
        assert result['success'] == True
        assert len(result['data']['items']) == 0
        
        print(f"✅ Empty list created successfully")
        
        # Clean up
        list_id = result['data']['id']
        delete_url = f"{BASE_URL}/api/{API_VERSION}/whiteboard/{test_whiteboard_id}/grocery-lists/{list_id}"
        requests_session.delete(delete_url, headers=headers)
    
    def test_large_items_list(self, requests_session, headers, test_whiteboard_id):
        """Test creating list with many items"""
        url = f"{BASE_URL}/api/{API_VERSION}/whiteboard/{test_whiteboard_id}/grocery-lists"
        
        # Create 50 items
        items = [
            {
                "id": f"item-{i}",
                "ingredient": f"Test ingredient {i}",
                "checked": False
            }
            for i in range(50)
        ]
        
        data = {
            "name": "Large Shopping List",
            "items": items,
            "household_id": 11
        }
        
        response = requests_session.post(url, headers=headers, json=data)
        
        print(f"\n📤 POST {url} (50 items)")
        print(f"📥 Status: {response.status_code}")
        
        assert response.status_code == 201
        
        result = response.json()
        assert result['success'] == True
        assert len(result['data']['items']) == 50
        
        print(f"✅ Large list (50 items) created successfully")
        
        # Clean up
        list_id = result['data']['id']
        delete_url = f"{BASE_URL}/api/{API_VERSION}/whiteboard/{test_whiteboard_id}/grocery-lists/{list_id}"
        requests_session.delete(delete_url, headers=headers)
    
    def test_special_characters_in_name(self, requests_session, headers, test_whiteboard_id):
        """Test name with special characters"""
        url = f"{BASE_URL}/api/{API_VERSION}/whiteboard/{test_whiteboard_id}/grocery-lists"
        
        data = {
            "name": "Mom's 🛒 Shopping List (Week #42) - 2025",
            "items": [{"ingredient": "test"}],
            "household_id": 11
        }
        
        response = requests_session.post(url, headers=headers, json=data)
        
        print(f"\n📤 POST {url} (special chars)")
        print(f"📥 Status: {response.status_code}")
        
        assert response.status_code == 201
        
        result = response.json()
        assert result['data']['name'] == data['name']
        
        print(f"✅ Special characters handled correctly")
        
        # Clean up
        list_id = result['data']['id']
        delete_url = f"{BASE_URL}/api/{API_VERSION}/whiteboard/{test_whiteboard_id}/grocery-lists/{list_id}"
        requests_session.delete(delete_url, headers=headers)


# =====================================================
# PYTEST CONFIGURATION
# =====================================================

@pytest.fixture(scope="session")
def requests_session():
    """Create a requests session for all tests"""
    import requests
    session = requests.Session()
    yield session
    session.close()


def pytest_configure(config):
    """Configure pytest"""
    print("\n" + "="*70)
    print("🧪 WHITEBOARD GROCERY LIST API TEST SUITE")
    print("="*70)
    print(f"📍 Base URL: {BASE_URL}")
    print(f"📍 API Version: {API_VERSION}")
    print(f"📍 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")


def pytest_sessionfinish(session, exitstatus):
    """Print summary after all tests"""
    print("\n" + "="*70)
    print("🧪 TEST SUITE COMPLETE")
    print("="*70)
    
    if exitstatus == 0:
        print("✅ All tests passed!")
    else:
        print(f"❌ Some tests failed (exit status: {exitstatus})")
    
    print("="*70 + "\n")
