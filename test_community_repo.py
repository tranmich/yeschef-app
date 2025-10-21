from app.database.repositories.community_repository import CommunityRepository

repo = CommunityRepository()

# Share recipe 2703
print("Sharing recipe 2703...")
result = repo.share_recipe_to_community(2703, 10)
print(f'Share result: {result}')

# Check if shared
print("\nChecking if shared...")
is_shared = repo.check_recipe_shared(2703, 10)
print(f'Is shared: {is_shared}')

# Get shared recipes
print("\nGetting community recipes...")
recipes = repo.get_community_recipes(limit=10)
print(f'Community recipes count: {len(recipes)}')
for r in recipes:
    print(f'  - Recipe {r.get("id")}: {r.get("title")}')
