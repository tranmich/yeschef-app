from app.services.community_service import CommunityService
from app.database.repositories.recipe_repository import RecipeRepository

# Check if recipe exists and who owns it
recipe_repo = RecipeRepository()
recipe = recipe_repo.get_recipe_by_id(2702)
print(f'Recipe found: {recipe is not None}')
if recipe:
    print(f'Recipe ID: {recipe.get("id")}')
    print(f'Recipe user_id: {recipe.get("user_id")}')
    print(f'Recipe title: {recipe.get("title")}')

# Try to share
service = CommunityService()
result = service.share_recipe(recipe_id=2702, user_id=10)
print(f'\nShare result: {result}')
