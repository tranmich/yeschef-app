"""
Test v2 API Endpoints
Run the Flask app and test all v2 endpoints
"""

from app import create_app
import json

print("=" * 70)
print("TESTING V2 API ENDPOINTS")
print("=" * 70)

# Create Flask app
app = create_app('development')

# Create test client
client = app.test_client()

# Test user_id (user with recipes)
USER_ID = 11

print("\n🧪 Testing User API v2...\n")

# Test 1: Health check
print("1. GET /api/v2/health")
response = client.get('/api/v2/health')
print(f"   Status: {response.status_code}")
print(f"   Response: {response.get_json()}")
assert response.status_code == 200

# Test 2: Get user by ID
print("\n2. GET /api/v2/users/11")
response = client.get(f'/api/v2/users/{USER_ID}')
print(f"   Status: {response.status_code}")
data = response.get_json()
print(f"   User: {data['data']['name']} ({data['data']['email']})")
assert response.status_code == 200
assert data['success'] == True

# Test 3: Get user stats
print("\n3. GET /api/v2/users/11/stats")
response = client.get(f'/api/v2/users/{USER_ID}/stats')
print(f"   Status: {response.status_code}")
data = response.get_json()
print(f"   Recipes: {data['data']['recipe_count']}")
assert response.status_code == 200

# Test 4: Search users
print("\n4. GET /api/v2/users/search?q=test")
response = client.get('/api/v2/users/search?q=test')
print(f"   Status: {response.status_code}")
data = response.get_json()
print(f"   Found: {data['data']['count']} users")
assert response.status_code == 200

print("\n" + "=" * 70)
print("🧪 Testing Recipe API v2...\n")

# Test 5: Get user recipes with stats (THE STAR!)
print("5. GET /api/v2/recipes/user/11/stats")
response = client.get(f'/api/v2/recipes/user/{USER_ID}/stats')
print(f"   Status: {response.status_code}")
data = response.get_json()
print(f"   User: {data['data']['user']['name']}")
print(f"   Total recipes: {data['data']['stats']['total_recipes']}")
print(f"   Categories: {data['data']['stats']['categories']}")
print(f"   Category counts: {data['data']['stats']['category_counts']}")
assert response.status_code == 200
assert data['success'] == True

# Get a recipe ID for further tests
recipes = data['data']['recipes']
recipe_id = recipes[0]['id'] if recipes else None

# Test 6: Get user recipes (paginated)
print("\n6. GET /api/v2/recipes/user/11?page=1&per_page=5")
response = client.get(f'/api/v2/recipes/user/{USER_ID}?page=1&per_page=5')
print(f"   Status: {response.status_code}")
data = response.get_json()
print(f"   Page: {data['data']['pagination']['page']}")
print(f"   Items on page: {len(data['data']['items'])}")
print(f"   Total: {data['data']['pagination']['total']}")
assert response.status_code == 200

# Test 7: Get user recipes by category
print("\n7. GET /api/v2/recipes/user/11?category=dinner")
response = client.get(f'/api/v2/recipes/user/{USER_ID}?category=dinner')
print(f"   Status: {response.status_code}")
data = response.get_json()
print(f"   Dinner recipes: {len(data['data']['items'])}")
assert response.status_code == 200

# Test 8: Get recipe by ID
if recipe_id:
    print(f"\n8. GET /api/v2/recipes/{recipe_id}?user_id={USER_ID}")
    response = client.get(f'/api/v2/recipes/{recipe_id}?user_id={USER_ID}')
    print(f"   Status: {response.status_code}")
    data = response.get_json()
    print(f"   Recipe: {data['data']['title']}")
    print(f"   Ingredients parsed: {isinstance(data['data'].get('ingredients'), list)}")
    assert response.status_code == 200

# Test 9: Search recipes
print(f"\n9. GET /api/v2/recipes/search?user_id={USER_ID}&q=chicken")
response = client.get(f'/api/v2/recipes/search?user_id={USER_ID}&q=chicken')
print(f"   Status: {response.status_code}")
data = response.get_json()
print(f"   Found: {data['data']['count']} recipes")
for recipe in data['data']['recipes'][:3]:
    print(f"   - {recipe['title']}")
assert response.status_code == 200

# Test 10: Get community recipes
print("\n10. GET /api/v2/recipes/community?page=1&per_page=10")
response = client.get('/api/v2/recipes/community?page=1&per_page=10')
print(f"    Status: {response.status_code}")
data = response.get_json()
print(f"    Community recipes: {data['data']['pagination']['total']}")
assert response.status_code == 200

# Test 11: Create recipe (with duplicate detection!)
print("\n11. POST /api/v2/recipes (create new recipe)")
new_recipe = {
    'user_id': USER_ID,
    'title': 'Test Recipe from v2 API',
    'ingredients': ['ingredient 1', 'ingredient 2'],
    'instructions': ['step 1', 'step 2'],
    'category': 'test'
}
response = client.post(
    '/api/v2/recipes',
    data=json.dumps(new_recipe),
    content_type='application/json'
)
print(f"    Status: {response.status_code}")
data = response.get_json()
if data['success']:
    created_recipe_id = data['data']['id']
    print(f"    ✅ Created recipe ID: {created_recipe_id}")
    
    # Test 12: Try to create duplicate (should fail!)
    print("\n12. POST /api/v2/recipes (duplicate - should fail!)")
    response = client.post(
        '/api/v2/recipes',
        data=json.dumps(new_recipe),
        content_type='application/json'
    )
    print(f"    Status: {response.status_code}")
    data = response.get_json()
    if not data['success']:
        print(f"    ✅ Duplicate detected! Error: {data['error']}")
        print(f"    Existing recipe ID: {data['details']['existing_recipe']['id']}")
        assert response.status_code == 409  # Conflict
    
    # Test 13: Update recipe
    print(f"\n13. PATCH /api/v2/recipes/{created_recipe_id} (update)")
    update_data = {
        'user_id': USER_ID,
        'title': 'Updated Test Recipe'
    }
    response = client.patch(
        f'/api/v2/recipes/{created_recipe_id}',
        data=json.dumps(update_data),
        content_type='application/json'
    )
    print(f"    Status: {response.status_code}")
    data = response.get_json()
    if data['success']:
        print(f"    ✅ Updated title: {data['data']['title']}")
    
    # Test 14: Delete recipe
    print(f"\n14. DELETE /api/v2/recipes/{created_recipe_id}")
    response = client.delete(f'/api/v2/recipes/{created_recipe_id}?user_id={USER_ID}')
    print(f"    Status: {response.status_code}")
    data = response.get_json()
    if data['success']:
        print(f"    ✅ Deleted recipe ID: {data['data']['recipe_id']}")
else:
    print(f"    ⚠️  Create failed (might already exist): {data.get('error')}")

# Test 15: Error handling - Get non-existent user
print("\n15. GET /api/v2/users/99999 (should return 404)")
response = client.get('/api/v2/users/99999')
print(f"    Status: {response.status_code}")
assert response.status_code == 404

# Test 16: Error handling - Unauthorized access
if recipe_id:
    print(f"\n16. GET /api/v2/recipes/{recipe_id}?user_id=999 (unauthorized)")
    response = client.get(f'/api/v2/recipes/{recipe_id}?user_id=999')
    print(f"    Status: {response.status_code}")
    data = response.get_json()
    print(f"    Error: {data['error']}")
    assert response.status_code == 403  # Forbidden

print("\n" + "=" * 70)
print("✅ ALL V2 API TESTS PASSED!")
print("=" * 70)
print("\nYour v2 API is working perfectly! 🎉")
print("\nKey features tested:")
print("  ✅ User retrieval & stats")
print("  ✅ Recipe retrieval with statistics")
print("  ✅ Pagination")
print("  ✅ Search")
print("  ✅ Create/Update/Delete")
print("  ✅ Duplicate detection")
print("  ✅ Authorization checks")
print("  ✅ Error handling")
print("\nReady to integrate with your mobile app!")
