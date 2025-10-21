"""
Pantry Service
Business logic for pantry inventory management
"""

from typing import Optional, Dict, Any, List
import logging

from app.database.repositories.pantry_repository import PantryRepository

logger = logging.getLogger(__name__)


class PantryService:
    """Service for pantry operations"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.repository = PantryRepository()
        self._initialized = True
        
        logger.info("✅ PantryService initialized")
    
    # ============================================================================
    # PANTRY ITEMS CRUD
    # ============================================================================
    
    def get_pantry(
        self,
        user_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get all pantry items for a user
        
        Args:
            user_id: User ID
            limit: Maximum results
            offset: Pagination offset
        
        Returns:
            Standardized response with items
        """
        try:
            items = self.repository.get_user_items(user_id, limit, offset)
            
            return {
                'success': True,
                'data': items,
                'pagination': {
                    'limit': limit,
                    'offset': offset,
                    'total': len(items)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error in get_pantry: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to get pantry items'
            }
    
    def add_item(
        self,
        user_id: int,
        item_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add item to pantry
        
        Args:
            user_id: User ID
            item_data: Item data
        
        Returns:
            Standardized response
        """
        try:
            # Validate required fields
            if not item_data.get('name'):
                return {
                    'success': False,
                    'error': 'Item name is required'
                }
            
            item = self.repository.add_item(user_id, item_data)
            
            if item:
                return {
                    'success': True,
                    'data': item,
                    'message': 'Item added to pantry'
                }
            
            return {
                'success': False,
                'error': 'Failed to add item'
            }
            
        except Exception as e:
            logger.error(f"❌ Error in add_item: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to add item'
            }
    
    def update_item(
        self,
        item_id: int,
        user_id: int,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update pantry item
        
        Args:
            item_id: Item ID
            user_id: User ID
            updates: Fields to update
        
        Returns:
            Standardized response
        """
        try:
            if not updates:
                return {
                    'success': False,
                    'error': 'No updates provided'
                }
            
            item = self.repository.update_item(item_id, user_id, updates)
            
            if item:
                return {
                    'success': True,
                    'data': item,
                    'message': 'Item updated successfully'
                }
            
            return {
                'success': False,
                'error': 'Item not found or update failed'
            }
            
        except Exception as e:
            logger.error(f"❌ Error in update_item: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to update item'
            }
    
    def delete_item(
        self,
        item_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Delete pantry item
        
        Args:
            item_id: Item ID
            user_id: User ID
        
        Returns:
            Standardized response
        """
        try:
            success = self.repository.delete_item(item_id, user_id)
            
            if success:
                return {
                    'success': True,
                    'message': 'Item deleted successfully'
                }
            
            return {
                'success': False,
                'error': 'Item not found'
            }
            
        except Exception as e:
            logger.error(f"❌ Error in delete_item: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to delete item'
            }
    
    def get_item(
        self,
        item_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Get single pantry item
        
        Args:
            item_id: Item ID
            user_id: User ID
        
        Returns:
            Standardized response
        """
        try:
            item = self.repository.get_item_by_id(item_id, user_id)
            
            if item:
                return {
                    'success': True,
                    'data': item
                }
            
            return {
                'success': False,
                'error': 'Item not found'
            }
            
        except Exception as e:
            logger.error(f"❌ Error in get_item: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to get item'
            }
    
    # ============================================================================
    # PANTRY STATUS & STATS
    # ============================================================================
    
    def get_stats(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Get pantry statistics
        
        Args:
            user_id: User ID
        
        Returns:
            Standardized response with stats
        """
        try:
            stats = self.repository.get_pantry_stats(user_id)
            
            return {
                'success': True,
                'data': stats
            }
            
        except Exception as e:
            logger.error(f"❌ Error in get_stats: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to get pantry stats'
            }
    
    def search(
        self,
        user_id: int,
        search_term: str,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Search pantry items
        
        Args:
            user_id: User ID
            search_term: Search query
            limit: Maximum results
        
        Returns:
            Standardized response with matching items
        """
        try:
            if not search_term:
                return {
                    'success': False,
                    'error': 'Search term is required'
                }
            
            items = self.repository.search_items(user_id, search_term, limit)
            
            return {
                'success': True,
                'data': items,
                'query': search_term
            }
            
        except Exception as e:
            logger.error(f"❌ Error in search: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Search failed'
            }
    
    def get_by_category(
        self,
        user_id: int,
        category: str
    ) -> Dict[str, Any]:
        """
        Get pantry items by category
        
        Args:
            user_id: User ID
            category: Category name
        
        Returns:
            Standardized response with items
        """
        try:
            items = self.repository.get_items_by_category(user_id, category)
            
            return {
                'success': True,
                'data': items,
                'category': category
            }
            
        except Exception as e:
            logger.error(f"❌ Error in get_by_category: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to get items by category'
            }
    
    def clear_pantry(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Clear all pantry items for a user
        
        Args:
            user_id: User ID
        
        Returns:
            Standardized response
        """
        try:
            # Get all items
            items = self.repository.get_user_items(user_id, limit=1000)
            
            # Delete each item
            deleted_count = 0
            for item in items:
                if self.repository.delete_item(item['id'], user_id):
                    deleted_count += 1
            
            return {
                'success': True,
                'message': f'Cleared {deleted_count} items from pantry',
                'deleted_count': deleted_count
            }
            
        except Exception as e:
            logger.error(f"❌ Error in clear_pantry: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to clear pantry'
            }
