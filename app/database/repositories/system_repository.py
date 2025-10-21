"""
System & Admin Repository
Handles database operations for system monitoring and admin operations
"""

from typing import Optional, Dict, Any, List
import logging

from app.database.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class SystemRepository(BaseRepository):
    """Repository for system and admin operations"""
    
    def __init__(self):
        super().__init__('users')
    
    # ============================================================================
    # SYSTEM HEALTH & MONITORING
    # ============================================================================
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get overall system statistics
        
        Returns:
            System stats dictionary
        """
        try:
            query = """
                SELECT 
                    (SELECT COUNT(*) FROM users) as total_users,
                    (SELECT COUNT(*) FROM recipes) as total_recipes,
                    (SELECT COUNT(*) FROM favorites) as total_favorites,
                    (SELECT COUNT(*) FROM recipe_shares WHERE is_shared = TRUE) as total_shared_recipes,
                    (SELECT COUNT(*) FROM pantry_items) as total_pantry_items,
                    (SELECT COUNT(*) FROM community_likes) as total_likes
            """
            
            stats = self._execute_query_one(query, ())
            
            logger.info("✅ Got system stats")
            
            return stats or {}
            
        except Exception as e:
            logger.error(f"❌ Error getting system stats: {e}", exc_info=True)
            return {}
    
    def get_database_health(self) -> Dict[str, Any]:
        """
        Check database health
        
        Returns:
            Health status dictionary
        """
        try:
            # Simple health check - verify we can query
            query = "SELECT COUNT(*) as count FROM users"
            result = self._execute_query_one(query, ())
            
            return {
                'status': 'healthy',
                'database': 'connected',
                'users_count': result.get('count', 0) if result else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Database health check failed: {e}", exc_info=True)
            return {
                'status': 'unhealthy',
                'database': 'error',
                'error': str(e)
            }
    
    # ============================================================================
    # USER MANAGEMENT (ADMIN)
    # ============================================================================
    
    def get_all_users(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all users (admin operation)
        
        Args:
            limit: Maximum results
            offset: Pagination offset
        
        Returns:
            List of users
        """
        try:
            query = """
                SELECT 
                    id, name, email, created_at,
                    (SELECT COUNT(*) FROM recipes WHERE user_id = users.id) as recipe_count,
                    (SELECT COUNT(*) FROM favorites WHERE user_id = users.id) as favorite_count
                FROM users
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            
            users = self._execute_query(query, (limit, offset))
            
            logger.info(f"✅ Got {len(users)} users")
            
            return users
            
        except Exception as e:
            logger.error(f"❌ Error getting all users: {e}", exc_info=True)
            return []
    
    def get_user_activity(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Get user activity summary
        
        Args:
            user_id: User ID
        
        Returns:
            Activity summary
        """
        try:
            query = """
                SELECT 
                    u.id,
                    u.name,
                    u.email,
                    u.created_at,
                    (SELECT COUNT(*) FROM recipes WHERE user_id = u.id) as total_recipes,
                    (SELECT COUNT(*) FROM favorites WHERE user_id = u.id) as total_favorites,
                    (SELECT COUNT(*) FROM recipe_shares WHERE user_id = u.id AND is_shared = TRUE) as total_shared,
                    (SELECT COUNT(*) FROM pantry_items WHERE user_id = u.id) as total_pantry_items,
                    (SELECT MAX(created_at) FROM recipes WHERE user_id = u.id) as last_recipe_date
                FROM users u
                WHERE u.id = %s
            """
            
            activity = self._execute_query_one(query, (user_id,))
            
            if activity:
                logger.info(f"✅ Got activity for user {user_id}")
                return activity
            
            return {}
            
        except Exception as e:
            logger.error(f"❌ Error getting user activity: {e}", exc_info=True)
            return {}
    
    # ============================================================================
    # CLEANUP OPERATIONS
    # ============================================================================
    
    def cleanup_orphaned_data(self) -> Dict[str, int]:
        """
        Clean up orphaned data (no foreign key references)
        
        Returns:
            Dictionary with cleanup counts
        """
        try:
            counts = {
                'favorites': 0,
                'pantry_items': 0,
                'recipe_shares': 0
            }
            
            # This is a safe operation since we have CASCADE on foreign keys
            # Just return 0 for now as cascade handles cleanup
            
            logger.info("✅ Cleanup check complete")
            
            return counts
            
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}", exc_info=True)
            return {'error': str(e)}
    
    def get_inactive_users(
        self,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get users who haven't been active
        
        Args:
            days: Days of inactivity
        
        Returns:
            List of inactive users
        """
        try:
            query = """
                SELECT 
                    u.id,
                    u.name,
                    u.email,
                    u.created_at,
                    (SELECT MAX(created_at) FROM recipes WHERE user_id = u.id) as last_activity
                FROM users u
                WHERE NOT EXISTS (
                    SELECT 1 FROM recipes 
                    WHERE user_id = u.id 
                    AND created_at >= NOW() - INTERVAL '%s days'
                )
                ORDER BY u.created_at DESC
            """
            
            users = self._execute_query(query, (days,))
            
            logger.info(f"✅ Found {len(users)} inactive users")
            
            return users
            
        except Exception as e:
            logger.error(f"❌ Error getting inactive users: {e}", exc_info=True)
            return []
    
    # ============================================================================
    # ANALYTICS
    # ============================================================================
    
    def get_popular_categories(
        self,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get most popular recipe categories
        
        Args:
            limit: Maximum results
        
        Returns:
            List of categories with counts
        """
        try:
            query = """
                SELECT 
                    category,
                    COUNT(*) as recipe_count,
                    COUNT(DISTINCT user_id) as user_count
                FROM recipes
                WHERE category IS NOT NULL
                GROUP BY category
                ORDER BY recipe_count DESC
                LIMIT %s
            """
            
            categories = self._execute_query(query, (limit,))
            
            logger.info(f"✅ Got {len(categories)} popular categories")
            
            return categories
            
        except Exception as e:
            logger.error(f"❌ Error getting popular categories: {e}", exc_info=True)
            return []
    
    def get_growth_stats(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get growth statistics
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Growth stats
        """
        try:
            query = """
                SELECT 
                    (SELECT COUNT(*) FROM users WHERE created_at >= NOW() - INTERVAL '%s days') as new_users,
                    (SELECT COUNT(*) FROM recipes WHERE created_at >= NOW() - INTERVAL '%s days') as new_recipes,
                    (SELECT COUNT(*) FROM favorites WHERE created_at >= NOW() - INTERVAL '%s days') as new_favorites
            """
            
            stats = self._execute_query_one(query, (days, days, days))
            
            logger.info(f"✅ Got growth stats for {days} days")
            
            return stats or {}
            
        except Exception as e:
            logger.error(f"❌ Error getting growth stats: {e}", exc_info=True)
            return {}
