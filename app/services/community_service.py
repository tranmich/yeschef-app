"""
Community Service
Business logic for community recipe sharing
"""

from typing import Optional, Dict, Any, List
import logging

from app.database.repositories.community_repository import CommunityRepository
from app.database.repositories.recipe_repository import RecipeRepository

logger = logging.getLogger(__name__)


class CommunityService:
    """Service for community recipe sharing operations"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.repository = CommunityRepository()
        self.recipes_repository = RecipeRepository()
        self._initialized = True
        
        logger.info("✅ CommunityService initialized")
    
    # ============================================================================
    # COMMUNITY RECIPES
    # ============================================================================
    
    def get_community_recipes(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
        filters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Get all community recipes
        
        Args:
            user_id: Requesting user ID
            limit: Maximum results
            offset: Pagination offset
            filters: Optional filters
        
        Returns:
            Standardized response with recipes
        """
        try:
            recipes = self.repository.get_community_recipes(limit, offset, filters)
            
            # Add liked status for user
            for recipe in recipes:
                recipe['is_liked_by_user'] = self.repository.check_user_liked(
                    recipe['id'], 
                    user_id
                )
            
            return {
                'success': True,
                'data': recipes,
                'pagination': {
                    'limit': limit,
                    'offset': offset,
                    'total': len(recipes)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error in get_community_recipes: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to get community recipes'
            }
    
    def get_community_recipe(
        self,
        recipe_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Get a specific community recipe with full details
        
        Args:
            recipe_id: Recipe ID
            user_id: Requesting user ID
        
        Returns:
            Standardized response with recipe
        """
        try:
            # Get recipe details
            recipe = self.recipes_repository.find_by_id(recipe_id)
            
            if not recipe:
                return {
                    'success': False,
                    'error': 'Recipe not found'
                }
            
            # Check if shared
            share_info = self.repository.get_recipe_share_info(recipe_id)
            
            if not share_info:
                return {
                    'success': False,
                    'error': 'Recipe not shared to community'
                }
            
            # Add community info
            recipe['share_info'] = share_info
            recipe['like_count'] = self.repository.get_recipe_likes_count(recipe_id)
            recipe['is_liked_by_user'] = self.repository.check_user_liked(recipe_id, user_id)
            
            return {
                'success': True,
                'data': recipe
            }
            
        except Exception as e:
            logger.error(f"❌ Error in get_community_recipe: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to get community recipe'
            }
    
    # ============================================================================
    # SHARING OPERATIONS
    # ============================================================================
    
    def share_recipe(
        self,
        recipe_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Share a recipe to the community
        
        Args:
            recipe_id: Recipe ID to share
            user_id: User ID sharing
        
        Returns:
            Standardized response
        """
        try:
            # Verify user owns the recipe
            recipe = self.recipes_repository.find_by_id(recipe_id)
            
            if not recipe:
                return {
                    'success': False,
                    'error': 'Recipe not found'
                }
            
            if recipe['user_id'] != user_id:
                return {
                    'success': False,
                    'error': 'You can only share your own recipes'
                }
            
            # Share to community
            share = self.repository.share_recipe_to_community(recipe_id, user_id)
            
            if share:
                return {
                    'success': True,
                    'data': share,
                    'message': 'Recipe shared to community successfully'
                }
            
            return {
                'success': False,
                'error': 'Failed to share recipe'
            }
            
        except Exception as e:
            logger.error(f"❌ Error in share_recipe: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to share recipe'
            }
    
    def unshare_recipe(
        self,
        recipe_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Remove a recipe from the community
        
        Args:
            recipe_id: Recipe ID
            user_id: User ID (must be owner)
        
        Returns:
            Standardized response
        """
        try:
            # Verify ownership
            recipe = self.recipes_repository.find_by_id(recipe_id)
            
            if not recipe:
                return {
                    'success': False,
                    'error': 'Recipe not found'
                }
            
            if recipe['user_id'] != user_id:
                return {
                    'success': False,
                    'error': 'You can only unshare your own recipes'
                }
            
            # Unshare
            success = self.repository.unshare_recipe_from_community(recipe_id, user_id)
            
            if success:
                return {
                    'success': True,
                    'message': 'Recipe removed from community'
                }
            
            return {
                'success': False,
                'error': 'Failed to unshare recipe'
            }
            
        except Exception as e:
            logger.error(f"❌ Error in unshare_recipe: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to unshare recipe'
            }
    
    def get_my_shares(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Get all recipes shared by a user
        
        Args:
            user_id: User ID
        
        Returns:
            Standardized response with recipes
        """
        try:
            recipes = self.repository.get_user_shared_recipes(user_id)
            
            return {
                'success': True,
                'data': recipes,
                'total': len(recipes)
            }
            
        except Exception as e:
            logger.error(f"❌ Error in get_my_shares: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to get shared recipes'
            }
    
    def check_shared(
        self,
        recipe_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Check if a recipe is shared to community
        
        Args:
            recipe_id: Recipe ID
            user_id: User ID
        
        Returns:
            Standardized response with status
        """
        try:
            is_shared = self.repository.check_recipe_shared(recipe_id, user_id)
            
            return {
                'success': True,
                'data': {
                    'recipe_id': recipe_id,
                    'is_shared': is_shared
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error in check_shared: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to check share status'
            }
    
    # ============================================================================
    # RECIPE CLAIMING (Copy community recipe to own collection)
    # ============================================================================
    
    def claim_recipe(
        self,
        recipe_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Claim a community recipe (copy to own collection)
        
        Args:
            recipe_id: Community recipe ID
            user_id: User claiming the recipe
        
        Returns:
            Standardized response with new recipe
        """
        try:
            # Get community recipe
            recipe = self.recipes_repository.find_by_id(recipe_id)
            
            if not recipe:
                return {
                    'success': False,
                    'error': 'Recipe not found'
                }
            
            # Verify it's shared
            if not self.repository.check_recipe_shared(recipe_id, recipe['user_id']):
                return {
                    'success': False,
                    'error': 'Recipe is not shared to community'
                }
            
            # Create a copy for the user
            new_recipe_data = {
                'user_id': user_id,
                'title': f"{recipe['title']} (from community)",
                'description': recipe.get('description', ''),
                'ingredients': recipe.get('ingredients', []),
                'instructions': recipe.get('instructions', []),
                'prep_time': recipe.get('prep_time'),
                'cook_time': recipe.get('cook_time'),
                'servings': recipe.get('servings'),
                'image_url': recipe.get('image_url'),
                'original_recipe_id': recipe_id
            }
            
            new_recipe = self.recipes_repository.create_recipe(new_recipe_data)
            
            if new_recipe:
                return {
                    'success': True,
                    'data': new_recipe,
                    'message': 'Recipe claimed successfully'
                }
            
            return {
                'success': False,
                'error': 'Failed to claim recipe'
            }
            
        except Exception as e:
            logger.error(f"❌ Error in claim_recipe: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to claim recipe'
            }
    
    # ============================================================================
    # LIKES
    # ============================================================================
    
    def like_recipe(
        self,
        recipe_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Like a community recipe
        
        Args:
            recipe_id: Recipe ID
            user_id: User ID
        
        Returns:
            Standardized response
        """
        try:
            like = self.repository.add_like(recipe_id, user_id)
            
            if like:
                like_count = self.repository.get_recipe_likes_count(recipe_id)
                return {
                    'success': True,
                    'data': {
                        'recipe_id': recipe_id,
                        'liked': True,
                        'like_count': like_count
                    },
                    'message': 'Recipe liked'
                }
            
            return {
                'success': False,
                'error': 'Recipe already liked or not found'
            }
            
        except Exception as e:
            logger.error(f"❌ Error in like_recipe: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to like recipe'
            }
    
    def unlike_recipe(
        self,
        recipe_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Unlike a community recipe
        
        Args:
            recipe_id: Recipe ID
            user_id: User ID
        
        Returns:
            Standardized response
        """
        try:
            success = self.repository.remove_like(recipe_id, user_id)
            
            if success:
                like_count = self.repository.get_recipe_likes_count(recipe_id)
                return {
                    'success': True,
                    'data': {
                        'recipe_id': recipe_id,
                        'liked': False,
                        'like_count': like_count
                    },
                    'message': 'Recipe unliked'
                }
            
            return {
                'success': False,
                'error': 'Like not found'
            }
            
        except Exception as e:
            logger.error(f"❌ Error in unlike_recipe: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to unlike recipe'
            }
