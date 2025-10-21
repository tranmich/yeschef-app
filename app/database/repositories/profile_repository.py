"""
Profile Repository
Handles all database operations for user profiles
"""

from typing import Optional, Dict, Any
import logging

from app.database.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class ProfileRepository(BaseRepository):
    """Repository for user profile operations"""
    
    def __init__(self):
        super().__init__('users')
    
    # ============================================================================
    # PROFILE OPERATIONS
    # ============================================================================
    
    def get_profile(
        self,
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get user profile
        
        Args:
            user_id: User ID
        
        Returns:
            User profile dictionary or None
        """
        try:
            query = """
                SELECT 
                    id,
                    name,
                    email,
                    avatar_url,
                    bio,
                    location,
                    dietary_preferences,
                    cooking_level,
                    created_at,
                    updated_at
                FROM users
                WHERE id = %s
            """
            
            profile = self._execute_query_one(query, (user_id,))
            
            if profile:
                logger.info(f"✅ Got profile for user {user_id}")
            
            return profile
            
        except Exception as e:
            logger.error(f"❌ Error getting profile: {e}", exc_info=True)
            return None
    
    def update_profile(
        self,
        user_id: int,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update user profile
        
        Args:
            user_id: User ID
            updates: Dictionary of fields to update
        
        Returns:
            Updated profile or None
        """
        try:
            # Build SET clause dynamically
            set_clauses = []
            params = []
            
            allowed_fields = ['name', 'bio', 'location', 'dietary_preferences', 'cooking_level', 'avatar_url']
            
            for field, value in updates.items():
                if field in allowed_fields:
                    set_clauses.append(f"{field} = %s")
                    params.append(value)
            
            if not set_clauses:
                logger.warning("No valid fields to update")
                return self.get_profile(user_id)
            
            # Add updated_at
            set_clauses.append("updated_at = NOW()")
            params.append(user_id)
            
            query = f"""
                UPDATE users 
                SET {', '.join(set_clauses)}
                WHERE id = %s
                RETURNING 
                    id, name, email, avatar_url, bio, location,
                    dietary_preferences, cooking_level, created_at, updated_at
            """
            
            profile = self._execute_insert(query, tuple(params))
            
            if profile:
                logger.info(f"✅ Updated profile for user {user_id}")
            
            return profile
            
        except Exception as e:
            logger.error(f"❌ Error updating profile: {e}", exc_info=True)
            return None
    
    def update_avatar(
        self,
        user_id: int,
        avatar_url: str
    ) -> Optional[Dict[str, Any]]:
        """
        Update user avatar URL
        
        Args:
            user_id: User ID
            avatar_url: Avatar image URL
        
        Returns:
            Updated profile or None
        """
        try:
            query = """
                UPDATE users 
                SET avatar_url = %s, updated_at = NOW()
                WHERE id = %s
                RETURNING 
                    id, name, email, avatar_url, bio, location,
                    dietary_preferences, cooking_level, created_at, updated_at
            """
            
            profile = self._execute_insert(query, (avatar_url, user_id))
            
            if profile:
                logger.info(f"✅ Updated avatar for user {user_id}")
            
            return profile
            
        except Exception as e:
            logger.error(f"❌ Error updating avatar: {e}", exc_info=True)
            return None
    
    def delete_avatar(
        self,
        user_id: int
    ) -> bool:
        """
        Delete user avatar (set to NULL)
        
        Args:
            user_id: User ID
        
        Returns:
            True if successful
        """
        try:
            query = """
                UPDATE users 
                SET avatar_url = NULL, updated_at = NOW()
                WHERE id = %s
                RETURNING id
            """
            
            result = self._execute_insert(query, (user_id,))
            
            if result:
                logger.info(f"✅ Deleted avatar for user {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error deleting avatar: {e}", exc_info=True)
            return False
    
    def get_profile_stats(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Get profile statistics
        
        Args:
            user_id: User ID
        
        Returns:
            Statistics dictionary
        """
        try:
            query = """
                SELECT 
                    (SELECT COUNT(*) FROM recipes WHERE user_id = %s) as total_recipes,
                    (SELECT COUNT(*) FROM favorites WHERE user_id = %s) as total_favorites,
                    (SELECT COUNT(*) FROM recipe_shares WHERE user_id = %s AND is_shared = TRUE) as total_shared,
                    (SELECT COUNT(*) FROM friends WHERE user_id = %s OR friend_id = %s) as total_friends
            """
            
            stats = self._execute_query_one(query, (user_id, user_id, user_id, user_id, user_id))
            
            if stats:
                logger.info(f"✅ Got stats for user {user_id}")
                return stats
            
            return {
                'total_recipes': 0,
                'total_favorites': 0,
                'total_shared': 0,
                'total_friends': 0
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting profile stats: {e}", exc_info=True)
            return {
                'total_recipes': 0,
                'total_favorites': 0,
                'total_shared': 0,
                'total_friends': 0
            }
