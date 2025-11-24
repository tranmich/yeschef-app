"""
Recipe Service  
Business logic for recipe operations
Coordinates RecipeRepository and UserRepository with validation, duplicate detection
"""

from typing import Dict, Any, Optional, List
import logging
import json

from app.services.base_service import BaseService
from app.database.repositories.recipe_repository import get_recipe_repository
from app.database.repositories.user_repository import get_user_repository

logger = logging.getLogger(__name__)


class RecipeService(BaseService):
    """Service for recipe business logic"""
    
    def __init__(self):
        super().__init__()
        self.recipe_repo = get_recipe_repository()
        self.user_repo = get_user_repository()
    
    # Recipe retrieval
    
    def get_recipe_by_id(self, recipe_id: int, user_id: int = None) -> Dict[str, Any]:
        """
        Get recipe by ID
        
        Args:
            recipe_id: Recipe ID
            user_id: User ID (for authorization check)
        
        Returns:
            Success response with recipe data or error response
        """
        try:
            recipe = self.recipe_repo.find_by_id(recipe_id)
            
            if not recipe:
                return self.error_response('Recipe not found', code='NOT_FOUND')
            
            # Authorization check (if user_id provided)
            if user_id and recipe['user_id'] != user_id:
                # Allow if recipe is community-shared
                if not recipe.get('is_community_shared'):
                    return self.error_response(
                        'Not authorized to view this recipe',
                        code='UNAUTHORIZED'
                    )
            
            # Parse JSON fields
            recipe = self._parse_recipe_json(recipe)
            
            return self.success_response(recipe)
            
        except Exception as e:
            self.log_error(f"Error getting recipe {recipe_id}", exception=e)
            return self.error_response('Failed to get recipe')
    
    def get_user_recipes(self, user_id: int, category: str = None,
                        page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Get all recipes for a user with pagination
        
        Args:
            user_id: User ID
            category: Optional category filter
            page: Page number
            per_page: Items per page
        
        Returns:
            Success response with paginated recipes
        """
        try:
            # Verify user exists
            user = self.user_repo.find_by_id(user_id)
            if not user:
                return self.error_response('User not found', code='NOT_FOUND')
            
            # Get recipes
            if category:
                recipes = self.recipe_repo.find_by_category(user_id, category, limit=1000)
            else:
                recipes = self.recipe_repo.find_by_user(user_id, limit=1000)
            
            # Parse JSON fields
            recipes = [self._parse_recipe_json(r) for r in recipes]
            
            # Paginate
            result = self.paginate(recipes, page, per_page)
            
            # Add metadata
            result['user'] = {
                'id': user['id'],
                'name': user['name']
            }
            result['total_recipes'] = len(recipes)
            
            return self.success_response(result)
            
        except Exception as e:
            self.log_error(f"Error getting recipes for user {user_id}", exception=e)
            return self.error_response('Failed to get recipes')
    
    def get_user_recipes_with_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Get user's recipes WITH statistics (categories, counts, etc.)
        This is a SERVICE-level operation that coordinates multiple repositories!
        
        Args:
            user_id: User ID
        
        Returns:
            Success response with recipes and statistics
        """
        try:
            # Verify user exists
            user = self.user_repo.find_by_id(user_id)
            if not user:
                return self.error_response('User not found', code='NOT_FOUND')
            
            # Get recipes
            recipes = self.recipe_repo.find_by_user(user_id, limit=1000)
            recipes = [self._parse_recipe_json(r) for r in recipes]
            
            # Get statistics
            categories = self.recipe_repo.get_categories(user_id)
            flavor_profiles = self.recipe_repo.get_flavor_profiles(user_id)
            
            # Calculate category counts
            category_counts = {}
            for category in categories:
                count = self.recipe_repo.count_by_category(user_id, category)
                category_counts[category] = count
            
            stats = {
                'total_recipes': len(recipes),
                'categories': categories,
                'category_counts': category_counts,
                'flavor_profiles': flavor_profiles,
                'recent_recipes': recipes[:5] if recipes else []
            }
            
            return self.success_response({
                'user': {
                    'id': user['id'],
                    'name': user['name'],
                    'email': user['email']
                },
                'recipes': recipes,
                'stats': stats
            })
            
        except Exception as e:
            self.log_error(f"Error getting recipes with stats for user {user_id}", exception=e)
            return self.error_response('Failed to get recipes')
    
    # Recipe creation
    
    def create_recipe(self, user_id: int, recipe_data: Dict[str, Any],
                     check_duplicates: bool = True) -> Dict[str, Any]:
        """
        Create new recipe with validation and duplicate detection
        
        Args:
            user_id: User ID
            recipe_data: Recipe data
            check_duplicates: Whether to check for recent duplicates
        
        Returns:
            Success response with created recipe or error response
        """
        try:
            # Verify user exists
            user = self.user_repo.find_by_id(user_id)
            if not user:
                return self.error_response('User not found', code='NOT_FOUND')
            
            # Validate required fields
            error = self.validate_required_fields(recipe_data, ['title'])
            if error:
                return self.error_response(error, code='VALIDATION_ERROR')
            
            # Add user_id to recipe data
            recipe_data['user_id'] = user_id
            
            # Check for duplicates (if enabled)
            if check_duplicates:
                duplicate = self.recipe_repo.find_recent_similar(
                    user_id,
                    recipe_data['title'],
                    within_minutes=5
                )
                
                if duplicate:
                    self.log_warning(f"Duplicate recipe detected: {recipe_data['title']}")
                    return self.error_response(
                        'You just created a recipe with this title 5 minutes ago',
                        code='DUPLICATE',
                        details={'existing_recipe': self._parse_recipe_json(duplicate)}
                    )
            
            # Create recipe
            recipe = self.recipe_repo.create(recipe_data)
            
            if not recipe:
                return self.error_response('Failed to create recipe')
            
            self.log_info(f"Created recipe: {recipe['title']} (ID: {recipe['id']}) for user {user_id}")
            
            recipe = self._parse_recipe_json(recipe)
            
            return self.success_response(
                recipe,
                message='Recipe created successfully'
            )
            
        except ValueError as e:
            return self.error_response(str(e), code='VALIDATION_ERROR')
        except Exception as e:
            self.log_error("Error creating recipe", exception=e)
            return self.error_response('Failed to create recipe')
    
    # Recipe updates
    
    def update_recipe(self, recipe_id: int, user_id: int,
                     updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update recipe with authorization
        
        Args:
            recipe_id: Recipe ID
            user_id: User ID (for authorization)
            updates: Fields to update
        
        Returns:
            Success response with updated recipe or error response
        """
        try:
            # Verify ownership
            recipe = self.recipe_repo.find_by_id(recipe_id)
            if not recipe:
                return self.error_response('Recipe not found', code='NOT_FOUND')
            
            if recipe['user_id'] != user_id:
                return self.error_response(
                    'Not authorized to update this recipe',
                    code='UNAUTHORIZED'
                )
            
            # Update recipe
            updated = self.recipe_repo.update(recipe_id, updates)
            
            if not updated:
                return self.error_response('Failed to update recipe')
            
            self.log_info(f"Updated recipe: {updated['title']} (ID: {recipe_id})")
            
            updated = self._parse_recipe_json(updated)
            
            return self.success_response(
                updated,
                message='Recipe updated successfully'
            )
            
        except Exception as e:
            self.log_error(f"Error updating recipe {recipe_id}", exception=e)
            return self.error_response('Failed to update recipe')
    
    def share_to_community(self, recipe_id: int, user_id: int) -> Dict[str, Any]:
        """
        Share recipe to community
        
        Args:
            recipe_id: Recipe ID
            user_id: User ID (for authorization)
        
        Returns:
            Success response or error response
        """
        try:
            recipe = self.recipe_repo.share_to_community(recipe_id, user_id)
            
            if not recipe:
                return self.error_response('Failed to share recipe')
            
            self.log_info(f"Shared recipe to community: {recipe['title']} (ID: {recipe_id})")
            
            recipe = self._parse_recipe_json(recipe)
            
            return self.success_response(
                recipe,
                message='Recipe shared to community'
            )
            
        except ValueError as e:
            return self.error_response(str(e), code='UNAUTHORIZED')
        except Exception as e:
            self.log_error(f"Error sharing recipe {recipe_id}", exception=e)
            return self.error_response('Failed to share recipe')
    
    def unshare_from_community(self, recipe_id: int, user_id: int) -> Dict[str, Any]:
        """
        Unshare recipe from community
        
        Args:
            recipe_id: Recipe ID
            user_id: User ID (for authorization)
        
        Returns:
            Success response or error response
        """
        try:
            recipe = self.recipe_repo.unshare_from_community(recipe_id, user_id)
            
            if not recipe:
                return self.error_response('Failed to unshare recipe')
            
            self.log_info(f"Unshared recipe from community: {recipe['title']} (ID: {recipe_id})")
            
            recipe = self._parse_recipe_json(recipe)
            
            return self.success_response(
                recipe,
                message='Recipe removed from community'
            )
            
        except ValueError as e:
            return self.error_response(str(e), code='UNAUTHORIZED')
        except Exception as e:
            self.log_error(f"Error unsharing recipe {recipe_id}", exception=e)
            return self.error_response('Failed to unshare recipe')
    
    # Recipe deletion
    
    def delete_recipe(self, recipe_id: int, user_id: int) -> Dict[str, Any]:
        """
        Delete recipe with authorization
        
        Args:
            recipe_id: Recipe ID
            user_id: User ID (for authorization)
        
        Returns:
            Success response or error response
        """
        try:
            success = self.recipe_repo.delete(recipe_id, user_id)
            
            if success:
                self.log_info(f"Deleted recipe ID: {recipe_id} for user {user_id}")
                return self.success_response(
                    {'recipe_id': recipe_id},
                    message='Recipe deleted successfully'
                )
            else:
                return self.error_response('Recipe not found', code='NOT_FOUND')
                
        except ValueError as e:
            return self.error_response(str(e), code='UNAUTHORIZED')
        except Exception as e:
            self.log_error(f"Error deleting recipe {recipe_id}", exception=e)
            return self.error_response('Failed to delete recipe')
    
    # Search
    
    def search_recipes(self, user_id: int, search_term: str,
                      limit: int = 50) -> Dict[str, Any]:
        """
        Search user's recipes
        
        Args:
            user_id: User ID
            search_term: Search term
            limit: Maximum results
        
        Returns:
            Success response with search results
        """
        try:
            recipes = self.recipe_repo.search_all_fields(user_id, search_term, limit)
            recipes = [self._parse_recipe_json(r) for r in recipes]
            
            return self.success_response({
                'recipes': recipes,
                'count': len(recipes),
                'search_term': search_term
            })
            
        except Exception as e:
            self.log_error(f"Error searching recipes: {search_term}", exception=e)
            return self.error_response('Failed to search recipes')
    
    def get_community_recipes(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Get community-shared recipes
        
        Args:
            page: Page number
            per_page: Items per page
        
        Returns:
            Success response with paginated community recipes
        """
        try:
            recipes = self.recipe_repo.find_community_recipes(limit=1000)
            recipes = [self._parse_recipe_json(r) for r in recipes]
            
            result = self.paginate(recipes, page, per_page)
            
            return self.success_response(result)
            
        except Exception as e:
            self.log_error("Error getting community recipes", exception=e)
            return self.error_response('Failed to get community recipes')
    
    def get_recipes_batch(self, recipe_ids: List[int], user_id: int = None) -> Dict[str, Any]:
        """
        Get multiple recipes by IDs in a single batch request (solves N+1 query problem)
        
        Args:
            recipe_ids: List of recipe IDs to fetch
            user_id: Optional user ID for authorization check
        
        Returns:
            Success response with list of recipes
        """
        try:
            if not recipe_ids:
                return self.success_response({
                    'recipes': [],
                    'found_count': 0,
                    'requested_count': 0
                })
            
            # Fetch all recipes in single query
            recipes = self.recipe_repo.find_by_ids(recipe_ids)
            
            # Filter by authorization if user_id provided
            if user_id:
                authorized_recipes = []
                for recipe in recipes:
                    # User owns recipe OR recipe is community-shared
                    if recipe['user_id'] == user_id or recipe.get('is_community_shared'):
                        authorized_recipes.append(recipe)
                recipes = authorized_recipes
            
            # Parse JSON fields for all recipes
            recipes = [self._parse_recipe_json(r) for r in recipes]
            
            return self.success_response({
                'recipes': recipes,
                'found_count': len(recipes),
                'requested_count': len(recipe_ids)
            })
            
        except Exception as e:
            self.log_error(f"Error getting recipes batch (count: {len(recipe_ids)})", exception=e)
            return self.error_response('Failed to get recipes batch')
    
    # Helper methods
    
    def _parse_recipe_json(self, recipe: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse JSON string fields (ingredients, instructions) to Python objects
        
        Args:
            recipe: Recipe dictionary
        
        Returns:
            Recipe with parsed JSON fields
        """
        # Parse ingredients if it's a JSON string
        if 'ingredients' in recipe and isinstance(recipe['ingredients'], str):
            try:
                recipe['ingredients'] = json.loads(recipe['ingredients'])
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Parse instructions if it's a JSON string
        if 'instructions' in recipe and isinstance(recipe['instructions'], str):
            try:
                recipe['instructions'] = json.loads(recipe['instructions'])
            except (json.JSONDecodeError, TypeError):
                pass
        
        return recipe


# Global instance
_recipe_service: Optional[RecipeService] = None


def get_recipe_service() -> RecipeService:
    """Get global RecipeService instance"""
    global _recipe_service
    if _recipe_service is None:
        _recipe_service = RecipeService()
    return _recipe_service
