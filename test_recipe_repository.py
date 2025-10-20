"""
Test RecipeRepository
"""

from app.database.repositories.recipe_repository import RecipeRepository
from app.database.connection import init_database

print("Testing RecipeRepository...")

init_database()

recipe_repo = RecipeRepository()

# Get a user ID to test with - use user 11 who has recipes
user_id = 11
from app.database.repositories.user_repository import UserRepository
user_repo = UserRepository()
user = user_repo.find_by_id(user_id)
if not user:
    print("❌ User not found")
    exit(1)

print(f"\nTesting with user ID: {user_id} ({user['name']})")

# Test count_by_user
count = recipe_repo.count_by_user(user_id)
print(f"✅ User recipes count: {count}")

# Test find_by_user
recipes = recipe_repo.find_by_user(user_id, limit=3)
print(f"✅ Find by user (first 3): {len(recipes)} recipes")
for recipe in recipes[:3]:
    print(f"   - {recipe['title']}")

# Test find_by_id
if recipes:
    recipe = recipe_repo.find_by_id(recipes[0]['id'])
    print(f"✅ Find by ID: {recipe['title']}")

# Test get_categories
categories = recipe_repo.get_categories(user_id)
print(f"✅ User categories: {categories[:5] if len(categories) > 5 else categories}")

# Test get_flavor_profiles
flavor_profiles = recipe_repo.get_flavor_profiles(user_id)
print(f"✅ User flavor profiles: {flavor_profiles[:5] if len(flavor_profiles) > 5 else flavor_profiles}")

# Test search
if recipes:
    search_term = recipes[0]['title'].split()[0] if recipes[0]['title'] else "test"
    results = recipe_repo.search(user_id, search_term, limit=5)
    print(f"✅ Search '{search_term}': {len(results)} results")

# Test find_community_recipes
community_recipes = recipe_repo.find_community_recipes(limit=5)
print(f"✅ Community recipes: {len(community_recipes)} recipes")

# Test count_by_category
if categories:
    count = recipe_repo.count_by_category(user_id, categories[0])
    print(f"✅ Count by category '{categories[0]}': {count}")

print("\n✅ All RecipeRepository tests passed!")
