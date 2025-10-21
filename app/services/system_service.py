"""
System & Admin Service
Business logic for system monitoring, admin operations, and utilities
"""

from typing import Optional, Dict, Any, List
import logging
from datetime import datetime

from app.database.repositories.system_repository import SystemRepository

logger = logging.getLogger(__name__)


class SystemService:
    """Service for system and admin operations"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.repository = SystemRepository()
        self._initialized = True
        
        logger.info("✅ SystemService initialized")
    
    # ============================================================================
    # SYSTEM HEALTH & MONITORING
    # ============================================================================
    
    def get_health(self) -> Dict[str, Any]:
        """
        Get system health status
        
        Returns:
            Standardized response with health data
        """
        try:
            db_health = self.repository.get_database_health()
            
            return {
                'success': True,
                'data': {
                    'status': db_health.get('status', 'unknown'),
                    'timestamp': datetime.now().isoformat(),
                    'database': db_health,
                    'version': '2.0.0'
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error in get_health: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Health check failed'
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get system statistics
        
        Returns:
            Standardized response with stats
        """
        try:
            stats = self.repository.get_system_stats()
            
            return {
                'success': True,
                'data': stats
            }
            
        except Exception as e:
            logger.error(f"❌ Error in get_stats: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to get system stats'
            }
    
    def get_analytics(self) -> Dict[str, Any]:
        """
        Get system analytics
        
        Returns:
            Standardized response with analytics
        """
        try:
            categories = self.repository.get_popular_categories(limit=5)
            growth = self.repository.get_growth_stats(days=30)
            
            return {
                'success': True,
                'data': {
                    'popular_categories': categories,
                    'growth_stats': growth
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error in get_analytics: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to get analytics'
            }
    
    # ============================================================================
    # ADMIN OPERATIONS
    # ============================================================================
    
    def get_all_users(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get all users (admin operation)
        
        Args:
            limit: Maximum results
            offset: Pagination offset
        
        Returns:
            Standardized response with users
        """
        try:
            users = self.repository.get_all_users(limit, offset)
            
            return {
                'success': True,
                'data': users,
                'pagination': {
                    'limit': limit,
                    'offset': offset,
                    'total': len(users)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error in get_all_users: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to get users'
            }
    
    def get_user_activity(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Get user activity summary
        
        Args:
            user_id: User ID
        
        Returns:
            Standardized response with activity
        """
        try:
            activity = self.repository.get_user_activity(user_id)
            
            if activity:
                return {
                    'success': True,
                    'data': activity
                }
            
            return {
                'success': False,
                'error': 'User not found'
            }
            
        except Exception as e:
            logger.error(f"❌ Error in get_user_activity: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to get user activity'
            }
    
    def get_inactive_users(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get inactive users
        
        Args:
            days: Days of inactivity
        
        Returns:
            Standardized response with inactive users
        """
        try:
            users = self.repository.get_inactive_users(days)
            
            return {
                'success': True,
                'data': users,
                'days': days,
                'count': len(users)
            }
            
        except Exception as e:
            logger.error(f"❌ Error in get_inactive_users: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to get inactive users'
            }
    
    # ============================================================================
    # CLEANUP OPERATIONS
    # ============================================================================
    
    def cleanup_system(self) -> Dict[str, Any]:
        """
        Clean up orphaned data
        
        Returns:
            Standardized response with cleanup results
        """
        try:
            results = self.repository.cleanup_orphaned_data()
            
            return {
                'success': True,
                'data': results,
                'message': 'Cleanup completed'
            }
            
        except Exception as e:
            logger.error(f"❌ Error in cleanup_system: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Cleanup failed'
            }
    
    # ============================================================================
    # VOICE COMMANDS (PLACEHOLDER)
    # ============================================================================
    
    def process_voice_command(
        self,
        user_id: int,
        command: str
    ) -> Dict[str, Any]:
        """
        Process voice command (placeholder)
        
        Args:
            user_id: User ID
            command: Voice command text
        
        Returns:
            Standardized response
        """
        try:
            # Placeholder implementation
            # In production, this would integrate with speech-to-text
            # and natural language processing
            
            command_lower = command.lower()
            
            response_text = "Voice command received"
            action = "unknown"
            
            if "recipe" in command_lower:
                action = "search_recipe"
                response_text = "Searching for recipes..."
            elif "add" in command_lower:
                action = "add_item"
                response_text = "Adding item..."
            elif "list" in command_lower:
                action = "show_list"
                response_text = "Showing list..."
            
            return {
                'success': True,
                'data': {
                    'command': command,
                    'action': action,
                    'response': response_text,
                    'placeholder': True
                },
                'message': 'Voice command processed (placeholder)'
            }
            
        except Exception as e:
            logger.error(f"❌ Error in process_voice_command: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to process voice command'
            }
