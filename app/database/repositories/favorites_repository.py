"""
Favorites Repository
Handles all database operations for recipe favorites/bookmarks
"""

from typing import Optional, Dict, Any, List
import logging

from app.database.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class FavoritesRepository(BaseRepository):
    """Repository for recipe favorites"""
    
    def __init__(self):
        super().__init__('favorites')
    
    # ============================================================================
    # FAVORITES OPERATIONS
    # ============================================================================
    
    def add_favorite(
        self,
        recipe_id: int,
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Add a recipe to user's favorites
        
        Args:
            recipe_id: Recipe ID
            user_id: User ID
        
        Returns:
            Favorite record or None
        """
        try:
            query = """
                INSERT INTO favorites 
                (user_id, recipe_id, created_at)
                VALUES (%s, %s, NOW())
                ON CONFLICT (user_id, recipe_id) DO NOTHING
                RETURNING *
            """
            
            favorite = self._execute_insert(query, (user_id, recipe_id))
            
            if favorite:
                logger.info(f"✅ User {user_id} added recipe {recipe_id} to favorites")
            
            return favorite
            
        except Exception as e:
            logger.error(f"❌ Error adding favorite: {e}", exc_info=True)
            return None
    
    def remove_favorite(
        self,
        recipe_id: int,
        user_id: int
    ) -> bool:
        """
        Remove a recipe from user's favorites
        
        Args:
            recipe_id: Recipe ID
            user_id: User ID
        
        Returns:
            True if successful
        """
        try:
            query = """
                DELETE FROM favorites 
                WHERE user_id = %s AND recipe_id = %s
                RETURNING id
            """
            
            result = self._execute_insert(query, (user_id, recipe_id))
            
            if result:
                logger.info(f"✅ User {user_id} removed recipe {recipe_id} from favorites")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error removing favorite: {e}", exc_info=True)
            return False
    
    def get_user_favorites(
        self,
        user_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all favorite recipes for a user
        
        Args:
            user_id: User ID
            limit: Maximum results
            offset: Pagination offset
        
        Returns:
            List of favorite recipes with details
        """
        try:
            query = """
                SELECT 
                    r.*,
                    f.created_at as favorited_at,
                    f.id as favorite_id
                FROM favorites f
                JOIN recipes r ON f.recipe_id = r.id
                WHERE f.user_id = %s
                ORDER BY f.created_at DESC
                LIMIT %s OFFSET %s
            """
            
            favorites = self._execute_query(query, (user_id, limit, offset))
            
            logger.info(f"✅ Got {len(favorites)} favorites for user {user_id}")
            
            return favorites
            
        except Exception as e:
            logger.error(f"❌ Error getting favorites: {e}", exc_info=True)
            return []
    
    def check_is_favorite(
        self,
        recipe_id: int,
        user_id: int
    ) -> bool:
        """
        Check if a recipe is in user's favorites
        
        Args:
            recipe_id: Recipe ID
            user_id: User ID
        
        Returns:
            True if favorited
        """
        try:
            query = """
                SELECT id FROM favorites 
                WHERE user_id = %s AND recipe_id = %s
            """
            
            result = self._execute_query_one(query, (user_id, recipe_id))
            return result is not None
            
        except Exception as e:
            logger.error(f"❌ Error checking favorite: {e}", exc_info=True)
            return False
    
    def get_favorites_summary(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Get favorites summary/stats for a user
        
        Args:
            user_id: User ID
        
        Returns:
            Summary dictionary with stats
        """
        try:
            query = """
                SELECT 
                    COUNT(*) as total_favorites,
                    COUNT(DISTINCT r.user_id) as unique_authors,
                    MIN(f.created_at) as first_favorite_date,
                    MAX(f.created_at) as last_favorite_date
                FROM favorites f
                JOIN recipes r ON f.recipe_id = r.id
                WHERE f.user_id = %s
            """
            
            summary = self._execute_query_one(query, (user_id,))
            
            if summary:
                logger.info(f"✅ Got favorites summary for user {user_id}")
                return summary
            
            return {
                'total_favorites': 0,
                'unique_authors': 0,
                'first_favorite_date': None,
                'last_favorite_date': None
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting favorites summary: {e}", exc_info=True)
            return {
                'total_favorites': 0,
                'unique_authors': 0,
                'first_favorite_date': None,
                'last_favorite_date': None
            }
    
    def get_favorites_count(
        self,
        user_id: int
    ) -> int:
        """
        Get count of user's favorites
        
        Args:
            user_id: User ID
        
        Returns:
            Number of favorites
        """
        try:
            query = """
                SELECT COUNT(*) as count
                FROM favorites 
                WHERE user_id = %s
            """
            
            result = self._execute_query_one(query, (user_id,))
            return result['count'] if result else 0
            
        except Exception as e:
            logger.error(f"❌ Error getting favorites count: {e}", exc_info=True)
            return 0
