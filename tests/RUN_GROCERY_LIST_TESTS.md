# Grocery List API Test Suite

## 🚀 Quick Start

### 1. Install pytest (if not already installed)
```powershell
pip install pytest requests
```

### 2. Make sure your server is running
```powershell
python hungie_server.py
```

### 3. Update test configuration

Edit `test_whiteboard_grocery_lists.py` and update:

```python
@pytest.fixture
def auth_token():
    # Get your token from browser localStorage or login response
    return "YOUR_AUTH_TOKEN_HERE"

@pytest.fixture
def test_whiteboard_id():
    return 3  # Your test whiteboard ID

@pytest.fixture
def test_household_id():
    return 11  # Your household ID
```

### 4. Run the tests

**Run all tests:**
```powershell
cd tests
pytest test_whiteboard_grocery_lists.py -v
```

**Run specific test class:**
```powershell
pytest test_whiteboard_grocery_lists.py::TestGroceryListCreation -v
```

**Run with detailed output:**
```powershell
pytest test_whiteboard_grocery_lists.py -v -s
```

## 📋 Test Coverage

### ✅ Creation Tests
- Create grocery list with full data
- Reject missing required fields
- Handle invalid whiteboard IDs

### ✅ Retrieval Tests
- Get all grocery lists for whiteboard
- Verify data structure

### ✅ Update Tests
- Update items (check/uncheck)
- Update widget position
- Update name

### ✅ Deletion Tests
- Soft delete grocery list
- Verify deletion
- Handle non-existent lists

### ✅ Edge Cases
- Empty items list
- Large lists (50+ items)
- Special characters in names
- Unicode/emoji support

## 📊 Expected Output

```
🧪 WHITEBOARD GROCERY LIST API TEST SUITE
======================================================================
📍 Base URL: http://127.0.0.1:5000
📍 API Version: v2
📍 Time: 2025-11-04 14:00:00
======================================================================

tests/test_whiteboard_grocery_lists.py::TestGroceryListCreation::test_create_grocery_list_success 
📤 POST http://127.0.0.1:5000/api/v2/whiteboard/3/grocery-lists
📥 Status: 201
✅ Created grocery list with ID: 42
PASSED

tests/test_whiteboard_grocery_lists.py::TestGroceryListCreation::test_create_grocery_list_missing_name
📤 POST http://127.0.0.1:5000/api/v2/whiteboard/3/grocery-lists (missing name)
📥 Status: 400
✅ Correctly rejected missing name
PASSED

...

======================================================================
🧪 TEST SUITE COMPLETE
======================================================================
✅ All tests passed!
======================================================================
```

## 🐛 Troubleshooting

### Authentication Error (401)
- Update your `auth_token` fixture with a valid token
- Get token from browser localStorage: `localStorage.getItem('authToken')`

### Whiteboard Not Found (404)
- Verify `test_whiteboard_id` exists in your database
- Create a test whiteboard in the UI first

### Connection Refused
- Make sure `hungie_server.py` is running
- Check server is on `http://127.0.0.1:5000`

### Import Errors
```powershell
pip install pytest requests
```

## 🎯 Next Steps

After tests pass:
1. ✅ Backend API is working correctly
2. ✅ Database schema is correct
3. ✅ Ready to test frontend integration manually
4. ✅ Safe to add WebSocket features

## 📝 Notes

- Tests run in order and share state (created_list_id)
- Tests clean up after themselves (delete test data)
- Safe to run multiple times
- Can run against local or Railway database (update BASE_URL)
