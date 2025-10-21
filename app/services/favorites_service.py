"""
Favorites Service
Business logic for recipe favorites/bookmarks
"""

from typing import Optional, Dict, Any, List
import logging

from app.database.repositories.favorites_repository import FavoritesRepository
from app.database.repositories.recipe_repository import RecipeRepository

logger = logging.getLogger(__name__)


class FavoritesService:
    """Service for favorites operations"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.repository = FavoritesRepository()
        self.recipes_repository = RecipeRepository()
        self._initialized = True
        
        logger.info("✅ FavoritesService initialized")
    
    # ============================================================================
    # FAVORITES OPERATIONS
    # ============================================================================
    
    def add_to_favorites(
        self,
        recipe_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Add a recipe to user's favorites
        
        Args:
            recipe_id: Recipe ID
            user_id: User ID
        
        Returns:
            Standardized response
        """
        try:
            # Verify recipe exists
            recipe = self.recipes_repository.find_by_id(recipe_id)
            
            if not recipe:
                return {
                    'success': False,
                    'error': 'Recipe not found'
                }
            
            # Add to favorites
            favorite = self.repository.add_favorite(recipe_id, user_id)
            
            if favorite:
                return {
                    'success': True,
                    'data': {
                        'favorite_id': favorite['id'],
                        'recipe_id': recipe_id,
                        'recipe_title': recipe.get('title'),
                        'created_at': favorite['created_at']
                    },
                    'message': 'Recipe added to favorites'
                }
            
            return {
                'success': False,
                'error': 'Recipe already in favorites or failed to add'
            }
            
        except Exception as e:
            logger.error(f"❌ Error in add_to_favorites: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to add to favorites'
            }
    
    def remove_from_favorites(
        self,
        recipe_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Remove a recipe from user's favorites
        
        Args:
            recipe_id: Recipe ID
            user_id: User ID
        
        Returns:
            Standardized response
        """
        try:
            success = self.repository.remove_favorite(recipe_id, user_id)
            
            if success:
                return {
                    'success': True,
                    'message': 'Recipe removed from favorites'
                }
            
            return {
                'success': False,
                'error': 'Recipe not in favorites'
            }
            
        except Exception as e:
            logger.error(f"❌ Error in remove_from_favorites: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to remove from favorites'
            }
    
    def get_favorites(
        self,
        user_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get all favorite recipes for a user
        
        Args:
            user_id: User ID
            limit: Maximum results
            offset: Pagination offset
        
        Returns:
            Standardized response with recipes
        """
        try:
            favorites = self.repository.get_user_favorites(user_id, limit, offset)
            
            return {
                'success': True,
                'data': favorites,
                'pagination': {
                    'limit': limit,
                    'offset': offset,
                    'total': len(favorites)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error in get_favorites: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to get favorites'
            }
    
    def check_favorite(
        self,
        recipe_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Check if a recipe is in user's favorites
        
        Args:
            recipe_id: Recipe ID
            user_id: User ID
        
        Returns:
            Standardized response with status
        """
        try:
            is_favorite = self.repository.check_is_favorite(recipe_id, user_id)
            
            return {
                'success': True,
                'data': {
                    'recipe_id': recipe_id,
                    'is_favorite': is_favorite
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error in check_favorite: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to check favorite status'
            }
    
    def get_summary(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Get favorites summary/stats for a user
        
        Args:
            user_id: User ID
        
        Returns:
            Standardized response with summary
        """
        try:
            summary = self.repository.get_favorites_summary(user_id)
            
            return {
                'success': True,
                'data': summary
            }
            
        except Exception as e:
            logger.error(f"❌ Error in get_summary: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to get favorites summary'
            }
