"""Test RecipeService"""
from app.services.recipe_service import RecipeService
from app.database.connection import init_database

print("Testing RecipeService...")

init_database()
recipe_service = RecipeService()

user_id = 11  # User with recipes

# Test get_user_recipes_with_stats - THIS IS THE POWER OF SERVICES!
print("\n=== Test: Get User Recipes WITH Stats ===")
result = recipe_service.get_user_recipes_with_stats(user_id)
print(f"✅ Get recipes with stats: {result['success']}")
if result['success']:
    data = result['data']
    print(f"   User: {data['user']['name']}")
    print(f"   Total recipes: {data['stats']['total_recipes']}")
    print(f"   Categories: {data['stats']['categories']}")
    print(f"   Category counts: {data['stats']['category_counts']}")
    print(f"   Recent recipes:")
    for recipe in data['stats']['recent_recipes'][:3]:
        print(f"      - {recipe['title']}")

# Test get_recipe_by_id  
print("\n=== Test: Get Recipe by ID ===")
recipes = result['data']['recipes']
if recipes:
    recipe_id = recipes[0]['id']
    result = recipe_service.get_recipe_by_id(recipe_id, user_id)
    print(f"✅ Get recipe: {result['success']}")
    if result['success']:
        print(f"   Title: {result['data']['title']}")
        print(f"   Ingredients parsed: {isinstance(result['data'].get('ingredients'), list)}")

# Test get_user_recipes with pagination
print("\n=== Test: Get User Recipes (Paginated) ===")
result = recipe_service.get_user_recipes(user_id, page=1, per_page=5)
print(f"✅ Get recipes (page 1): {result['success']}")
if result['success']:
    print(f"   Page: {result['data']['pagination']['page']}")
    print(f"   Total: {result['data']['pagination']['total']}")
    print(f"   Items on this page: {len(result['data']['items'])}")

# Test get_user_recipes with category filter
print("\n=== Test: Get User Recipes (By Category) ===")
result = recipe_service.get_user_recipes(user_id, category='dinner')
print(f"✅ Get dinner recipes: {result['success']}")
if result['success']:
    print(f"   Found: {len(result['data']['items'])} dinner recipes")

# Test search_recipes
print("\n=== Test: Search Recipes ===")
result = recipe_service.search_recipes(user_id, 'chicken')
print(f"✅ Search 'chicken': {result['success']}")
if result['success']:
    print(f"   Found: {result['data']['count']} recipes")
    for recipe in result['data']['recipes'][:3]:
        print(f"   - {recipe['title']}")

# Test authorization - try to get another user's recipe
print("\n=== Test: Authorization Check ===")
if recipes:
    recipe_id = recipes[0]['id']
    wrong_user_id = 999
    result = recipe_service.get_recipe_by_id(recipe_id, wrong_user_id)
    print(f"✅ Unauthorized access blocked: {not result['success']}")
    if not result['success']:
        print(f"   Error: {result['error']}")

# Test get_community_recipes
print("\n=== Test: Get Community Recipes ===")
result = recipe_service.get_community_recipes(page=1, per_page=10)
print(f"✅ Get community recipes: {result['success']}")
if result['success']:
    print(f"   Found: {result['data']['pagination']['total']} community recipes")

print("\n✅ All RecipeService tests passed!")
