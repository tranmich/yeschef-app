"""
Recipe Import & Search Service
Business logic for recipe importing, searching, and recommendations
"""

from typing import Optional, Dict, Any, List
import logging
import re

from app.database.repositories.recipe_search_repository import RecipeSearchRepository
from app.database.repositories.recipe_repository import RecipeRepository

logger = logging.getLogger(__name__)


class RecipeSearchService:
    """Service for recipe search and import operations"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.repository = RecipeSearchRepository()
        self.recipe_repository = RecipeRepository()
        self._initialized = True
        
        logger.info("✅ RecipeSearchService initialized")
    
    # ============================================================================
    # ADVANCED SEARCH
    # ============================================================================
    
    def search(
        self,
        user_id: int,
        query: str = None,
        filters: Dict[str, Any] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Advanced recipe search
        
        Args:
            user_id: User ID
            query: Search term
            filters: Additional filters (category, prep_time_max, etc.)
            limit: Maximum results
            offset: Pagination offset
        
        Returns:
            Standardized response with recipes
        """
        try:
            filters = filters or {}
            
            recipes = self.repository.search_recipes(
                user_id=user_id,
                query=query,
                category=filters.get('category'),
                prep_time_max=filters.get('prep_time_max'),
                cook_time_max=filters.get('cook_time_max'),
                limit=limit,
                offset=offset
            )
            
            return {
                'success': True,
                'data': recipes,
                'query': query,
                'filters': filters,
                'pagination': {
                    'limit': limit,
                    'offset': offset,
                    'total': len(recipes)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error in search: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Search failed'
            }
    
    def get_recommendations(
        self,
        user_id: int,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get personalized recipe recommendations
        
        Args:
            user_id: User ID
            limit: Maximum results
        
        Returns:
            Standardized response with recommendations
        """
        try:
            recipes = self.repository.get_recipe_recommendations(user_id, limit)
            
            return {
                'success': True,
                'data': recipes,
                'count': len(recipes)
            }
            
        except Exception as e:
            logger.error(f"❌ Error in get_recommendations: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to get recommendations'
            }
    
    def search_by_ingredients(
        self,
        user_id: int,
        ingredients: List[str],
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Search recipes by available ingredients
        
        Args:
            user_id: User ID
            ingredients: List of ingredient names
            limit: Maximum results
        
        Returns:
            Standardized response with recipes
        """
        try:
            if not ingredients:
                return {
                    'success': False,
                    'error': 'Ingredients list is required'
                }
            
            recipes = self.repository.search_by_ingredients(user_id, ingredients, limit)
            
            return {
                'success': True,
                'data': recipes,
                'ingredients': ingredients,
                'count': len(recipes)
            }
            
        except Exception as e:
            logger.error(f"❌ Error in search_by_ingredients: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Ingredient search failed'
            }
    
    def get_popular(
        self,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get popular community recipes
        
        Args:
            limit: Maximum results
        
        Returns:
            Standardized response with popular recipes
        """
        try:
            recipes = self.repository.get_popular_recipes(limit)
            
            return {
                'success': True,
                'data': recipes,
                'count': len(recipes)
            }
            
        except Exception as e:
            logger.error(f"❌ Error in get_popular: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to get popular recipes'
            }
    
    def get_recent(
        self,
        user_id: int,
        days: int = 7,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get recent recipes
        
        Args:
            user_id: User ID
            days: Number of days to look back
            limit: Maximum results
        
        Returns:
            Standardized response with recent recipes
        """
        try:
            recipes = self.repository.get_recent_recipes(user_id, days, limit)
            
            return {
                'success': True,
                'data': recipes,
                'days': days,
                'count': len(recipes)
            }
            
        except Exception as e:
            logger.error(f"❌ Error in get_recent: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to get recent recipes'
            }
    
    # ============================================================================
    # RECIPE IMPORT
    # ============================================================================
    
    def import_from_url(
        self,
        user_id: int,
        url: str
    ) -> Dict[str, Any]:
        """
        Import recipe from URL (stub for now)
        
        Args:
            user_id: User ID
            url: Recipe URL
        
        Returns:
            Standardized response
        """
        try:
            # Validate URL
            if not url or not url.startswith('http'):
                return {
                    'success': False,
                    'error': 'Invalid URL'
                }
            
            # TODO: Implement actual scraping logic
            # For now, create a placeholder recipe
            
            recipe_data = {
                'user_id': user_id,
                'title': f'Imported Recipe from {self._extract_domain(url)}',
                'description': f'Recipe imported from {url}',
                'ingredients': ['Ingredient 1', 'Ingredient 2'],
                'instructions': ['Step 1: Import recipe', 'Step 2: Enjoy!'],
                'prep_time': '10 minutes',
                'cook_time': '20 minutes',
                'servings': 4
            }
            
            # Create recipe
            recipe = self.recipe_repository.create(recipe_data)
            
            if recipe:
                # Log import
                self.repository.log_import(
                    user_id=user_id,
                    source_url=url,
                    recipe_id=recipe['id'],
                    status='success'
                )
                
                return {
                    'success': True,
                    'data': recipe,
                    'message': 'Recipe imported successfully (placeholder)',
                    'source_url': url
                }
            
            # Log failed import
            self.repository.log_import(
                user_id=user_id,
                source_url=url,
                status='failed',
                error_message='Failed to create recipe'
            )
            
            return {
                'success': False,
                'error': 'Failed to import recipe'
            }
            
        except Exception as e:
            logger.error(f"❌ Error in import_from_url: {e}", exc_info=True)
            
            # Log error
            self.repository.log_import(
                user_id=user_id,
                source_url=url,
                status='failed',
                error_message=str(e)
            )
            
            return {
                'success': False,
                'error': 'Import failed'
            }
    
    def get_import_history(
        self,
        user_id: int,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get import history
        
        Args:
            user_id: User ID
            limit: Maximum results
        
        Returns:
            Standardized response with import records
        """
        try:
            imports = self.repository.get_import_history(user_id, limit)
            
            return {
                'success': True,
                'data': imports,
                'count': len(imports)
            }
            
        except Exception as e:
            logger.error(f"❌ Error in get_import_history: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to get import history'
            }
    
    # ============================================================================
    # BULK OPERATIONS
    # ============================================================================
    
    def bulk_delete(
        self,
        user_id: int,
        recipe_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Delete multiple recipes at once
        
        Args:
            user_id: User ID
            recipe_ids: List of recipe IDs to delete
        
        Returns:
            Standardized response
        """
        try:
            if not recipe_ids:
                return {
                    'success': False,
                    'error': 'No recipe IDs provided'
                }
            
            deleted_count = 0
            errors = []
            
            for recipe_id in recipe_ids:
                try:
                    success = self.recipe_repository.delete(recipe_id, user_id)
                    if success:
                        deleted_count += 1
                    else:
                        errors.append(f'Recipe {recipe_id} not found or not owned by user')
                except Exception as e:
                    errors.append(f'Recipe {recipe_id}: {str(e)}')
            
            return {
                'success': True,
                'deleted_count': deleted_count,
                'total_requested': len(recipe_ids),
                'errors': errors if errors else None
            }
            
        except Exception as e:
            logger.error(f"❌ Error in bulk_delete: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Bulk delete failed'
            }
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        match = re.search(r'https?://([^/]+)', url)
        return match.group(1) if match else 'unknown'
