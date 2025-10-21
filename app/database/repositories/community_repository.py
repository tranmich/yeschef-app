"""
Community Repository
Handles all database operations for community recipe sharing
"""

from typing import Optional, Dict, Any, List
import logging

from app.database.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class CommunityRepository(BaseRepository):
    """Repository for community recipe shares and interactions"""
    
    def __init__(self):
        super().__init__('recipe_shares')
    
    # ============================================================================
    # RECIPE SHARING OPERATIONS
    # ============================================================================
    
    def get_community_recipes(
        self,
        limit: int = 50,
        offset: int = 0,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all shared community recipes
        
        Args:
            limit: Maximum number of recipes to return
            offset: Number of recipes to skip
            filters: Optional filters (category, search, etc.)
        
        Returns:
            List of community recipe dictionaries
        """
        try:
            query = """
                SELECT 
                    r.id,
                    r.title,
                    r.description,
                    r.prep_time,
                    r.cook_time,
                    r.servings,
                    r.image_url,
                    r.created_at,
                    u.id as shared_by_user_id,
                    u.name as shared_by_name,
                    u.email as shared_by_email,
                    rs.shared_at,
                    COUNT(DISTINCT cl.id) as like_count
                FROM recipes r
                JOIN recipe_shares rs ON r.id = rs.recipe_id
                JOIN users u ON rs.user_id = u.id
                LEFT JOIN community_likes cl ON r.id = cl.recipe_id
                WHERE rs.is_shared = TRUE
                GROUP BY r.id, r.title, r.description, r.prep_time, r.cook_time,
                         r.servings, r.image_url, r.created_at, u.id, u.name,
                         u.email, rs.shared_at
                ORDER BY rs.shared_at DESC
                LIMIT %s OFFSET %s
            """
            
            recipes = self._execute_query(query, (limit, offset))
            
            logger.info(f"✅ Got {len(recipes)} community recipes")
            
            return recipes
            
        except Exception as e:
            logger.error(f"❌ Error getting community recipes: {e}", exc_info=True)
            return []
    
    def share_recipe_to_community(
        self,
        recipe_id: int,
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Share a recipe to the community
        
        Args:
            recipe_id: Recipe ID to share
            user_id: User ID sharing the recipe
        
        Returns:
            Share record or None
        """
        try:
            # Check if already shared
            check_query = """
                SELECT id FROM recipe_shares 
                WHERE recipe_id = %s AND user_id = %s
            """
            existing = self._execute_query_one(check_query, (recipe_id, user_id))
            
            if existing:
                # Update existing share
                query = """
                    UPDATE recipe_shares 
                    SET is_shared = TRUE, shared_at = NOW()
                    WHERE recipe_id = %s AND user_id = %s
                    RETURNING *
                """
            else:
                # Create new share
                query = """
                    INSERT INTO recipe_shares 
                    (recipe_id, user_id, is_shared, shared_at)
                    VALUES (%s, %s, TRUE, NOW())
                    RETURNING *
                """
            
            share = self._execute_insert(query, (recipe_id, user_id))
            
            logger.info(f"✅ Recipe {recipe_id} shared to community by user {user_id}")
            
            return share
            
        except Exception as e:
            logger.error(f"❌ Error sharing recipe: {e}", exc_info=True)
            return None
    
    def unshare_recipe_from_community(
        self,
        recipe_id: int,
        user_id: int
    ) -> bool:
        """
        Remove a recipe from community
        
        Args:
            recipe_id: Recipe ID
            user_id: User ID (must be owner)
        
        Returns:
            True if successful
        """
        try:
            query = """
                UPDATE recipe_shares 
                SET is_shared = FALSE
                WHERE recipe_id = %s AND user_id = %s
                RETURNING id
            """
            
            result = self._execute_insert(query, (recipe_id, user_id))
            
            if result:
                logger.info(f"✅ Recipe {recipe_id} unshared from community")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error unsharing recipe: {e}", exc_info=True)
            return False
    
    def get_recipe_share_info(
        self,
        recipe_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get share information for a recipe
        
        Args:
            recipe_id: Recipe ID
        
        Returns:
            Share info or None
        """
        try:
            query = """
                SELECT 
                    rs.*,
                    u.name as shared_by_name,
                    COUNT(DISTINCT cl.id) as like_count
                FROM recipe_shares rs
                JOIN users u ON rs.user_id = u.id
                LEFT JOIN community_likes cl ON rs.recipe_id = cl.recipe_id
                WHERE rs.recipe_id = %s AND rs.is_shared = TRUE
                GROUP BY rs.id, rs.recipe_id, rs.user_id, rs.is_shared, rs.shared_at, u.name
            """
            
            return self._execute_query_one(query, (recipe_id,))
            
        except Exception as e:
            logger.error(f"❌ Error getting share info: {e}", exc_info=True)
            return None
    
    def check_recipe_shared(
        self,
        recipe_id: int,
        user_id: int
    ) -> bool:
        """
        Check if a recipe is shared by a user
        
        Args:
            recipe_id: Recipe ID
            user_id: User ID
        
        Returns:
            True if shared
        """
        try:
            query = """
                SELECT id FROM recipe_shares 
                WHERE recipe_id = %s AND user_id = %s AND is_shared = TRUE
            """
            
            result = self._execute_query_one(query, (recipe_id, user_id))
            return result is not None
            
        except Exception as e:
            logger.error(f"❌ Error checking if shared: {e}", exc_info=True)
            return False
    
    def get_user_shared_recipes(
        self,
        user_id: int
    ) -> List[Dict[str, Any]]:
        """
        Get all recipes shared by a user
        
        Args:
            user_id: User ID
        
        Returns:
            List of shared recipes
        """
        try:
            query = """
                SELECT 
                    r.*,
                    rs.shared_at,
                    COUNT(DISTINCT cl.id) as like_count
                FROM recipes r
                JOIN recipe_shares rs ON r.id = rs.recipe_id
                LEFT JOIN community_likes cl ON r.id = cl.recipe_id
                WHERE rs.user_id = %s AND rs.is_shared = TRUE
                GROUP BY r.id, rs.shared_at
                ORDER BY rs.shared_at DESC
            """
            
            recipes = self._execute_query(query, (user_id,))
            
            logger.info(f"✅ Got {len(recipes)} shared recipes for user {user_id}")
            
            return recipes
            
        except Exception as e:
            logger.error(f"❌ Error getting user shared recipes: {e}", exc_info=True)
            return []
    
    # ============================================================================
    # COMMUNITY LIKES OPERATIONS
    # ============================================================================
    
    def add_like(
        self,
        recipe_id: int,
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Add a like to a community recipe
        
        Args:
            recipe_id: Recipe ID
            user_id: User ID
        
        Returns:
            Like record or None
        """
        try:
            query = """
                INSERT INTO community_likes 
                (recipe_id, user_id, created_at)
                VALUES (%s, %s, NOW())
                ON CONFLICT (recipe_id, user_id) DO NOTHING
                RETURNING *
            """
            
            like = self._execute_insert(query, (recipe_id, user_id))
            
            if like:
                logger.info(f"✅ User {user_id} liked recipe {recipe_id}")
            
            return like
            
        except Exception as e:
            logger.error(f"❌ Error adding like: {e}", exc_info=True)
            return None
    
    def remove_like(
        self,
        recipe_id: int,
        user_id: int
    ) -> bool:
        """
        Remove a like from a community recipe
        
        Args:
            recipe_id: Recipe ID
            user_id: User ID
        
        Returns:
            True if successful
        """
        try:
            query = """
                DELETE FROM community_likes 
                WHERE recipe_id = %s AND user_id = %s
                RETURNING id
            """
            
            result = self._execute_insert(query, (recipe_id, user_id))
            
            if result:
                logger.info(f"✅ User {user_id} unliked recipe {recipe_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error removing like: {e}", exc_info=True)
            return False
    
    def check_user_liked(
        self,
        recipe_id: int,
        user_id: int
    ) -> bool:
        """
        Check if user has liked a recipe
        
        Args:
            recipe_id: Recipe ID
            user_id: User ID
        
        Returns:
            True if liked
        """
        try:
            query = """
                SELECT id FROM community_likes 
                WHERE recipe_id = %s AND user_id = %s
            """
            
            result = self._execute_query_one(query, (recipe_id, user_id))
            return result is not None
            
        except Exception as e:
            logger.error(f"❌ Error checking if liked: {e}", exc_info=True)
            return False
    
    def get_recipe_likes_count(
        self,
        recipe_id: int
    ) -> int:
        """
        Get number of likes for a recipe
        
        Args:
            recipe_id: Recipe ID
        
        Returns:
            Like count
        """
        try:
            query = """
                SELECT COUNT(*) as count
                FROM community_likes 
                WHERE recipe_id = %s
            """
            
            result = self._execute_query_one(query, (recipe_id,))
            return result['count'] if result else 0
            
        except Exception as e:
            logger.error(f"❌ Error getting likes count: {e}", exc_info=True)
            return 0
