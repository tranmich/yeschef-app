"""
Pantry Repository
Handles all database operations for pantry inventory management
"""

from typing import Optional, Dict, Any, List
import logging

from app.database.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class PantryRepository(BaseRepository):
    """Repository for pantry items"""
    
    def __init__(self):
        super().__init__('pantry_items')
    
    # ============================================================================
    # PANTRY ITEMS CRUD
    # ============================================================================
    
    def get_user_items(
        self,
        user_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all pantry items for a user
        
        Args:
            user_id: User ID
            limit: Maximum results
            offset: Pagination offset
        
        Returns:
            List of pantry items
        """
        try:
            query = """
                SELECT *
                FROM pantry_items
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            
            items = self._execute_query(query, (user_id, limit, offset))
            
            logger.info(f"✅ Got {len(items)} pantry items for user {user_id}")
            
            return items
            
        except Exception as e:
            logger.error(f"❌ Error getting pantry items: {e}", exc_info=True)
            return []
    
    def add_item(
        self,
        user_id: int,
        item_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Add item to pantry
        
        Args:
            user_id: User ID
            item_data: Item data (name, quantity, unit, category, etc.)
        
        Returns:
            Created item or None
        """
        try:
            query = """
                INSERT INTO pantry_items 
                (user_id, name, quantity, unit, category, expiry_date, notes, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                RETURNING *
            """
            
            params = (
                user_id,
                item_data.get('name'),
                item_data.get('quantity', 1),
                item_data.get('unit', 'unit'),
                item_data.get('category', 'other'),
                item_data.get('expiry_date'),
                item_data.get('notes', '')
            )
            
            item = self._execute_insert(query, params)
            
            if item:
                logger.info(f"✅ Added pantry item: {item['name']} for user {user_id}")
            
            return item
            
        except Exception as e:
            logger.error(f"❌ Error adding pantry item: {e}", exc_info=True)
            return None
    
    def update_item(
        self,
        item_id: int,
        user_id: int,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update pantry item
        
        Args:
            item_id: Item ID
            user_id: User ID (for authorization)
            updates: Fields to update
        
        Returns:
            Updated item or None
        """
        try:
            # Build SET clause
            set_clauses = []
            params = []
            
            allowed_fields = ['name', 'quantity', 'unit', 'category', 'expiry_date', 'notes']
            
            for field, value in updates.items():
                if field in allowed_fields:
                    set_clauses.append(f"{field} = %s")
                    params.append(value)
            
            if not set_clauses:
                return self.get_item_by_id(item_id, user_id)
            
            params.extend([item_id, user_id])
            
            query = f"""
                UPDATE pantry_items 
                SET {', '.join(set_clauses)}
                WHERE id = %s AND user_id = %s
                RETURNING *
            """
            
            item = self._execute_insert(query, tuple(params))
            
            if item:
                logger.info(f"✅ Updated pantry item {item_id}")
            
            return item
            
        except Exception as e:
            logger.error(f"❌ Error updating pantry item: {e}", exc_info=True)
            return None
    
    def delete_item(
        self,
        item_id: int,
        user_id: int
    ) -> bool:
        """
        Delete pantry item
        
        Args:
            item_id: Item ID
            user_id: User ID (for authorization)
        
        Returns:
            True if successful
        """
        try:
            query = """
                DELETE FROM pantry_items 
                WHERE id = %s AND user_id = %s
                RETURNING id
            """
            
            result = self._execute_insert(query, (item_id, user_id))
            
            if result:
                logger.info(f"✅ Deleted pantry item {item_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error deleting pantry item: {e}", exc_info=True)
            return False
    
    def get_item_by_id(
        self,
        item_id: int,
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get pantry item by ID
        
        Args:
            item_id: Item ID
            user_id: User ID (for authorization)
        
        Returns:
            Item or None
        """
        try:
            query = """
                SELECT *
                FROM pantry_items
                WHERE id = %s AND user_id = %s
            """
            
            return self._execute_query_one(query, (item_id, user_id))
            
        except Exception as e:
            logger.error(f"❌ Error getting pantry item: {e}", exc_info=True)
            return None
    
    # ============================================================================
    # PANTRY STATUS & STATS
    # ============================================================================
    
    def get_pantry_stats(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Get pantry statistics
        
        Args:
            user_id: User ID
        
        Returns:
            Statistics dictionary
        """
        try:
            query = """
                SELECT 
                    COUNT(*) as total_items,
                    COUNT(DISTINCT category) as total_categories,
                    COUNT(CASE WHEN expiry_date IS NOT NULL AND expiry_date < NOW() THEN 1 END) as expired_items,
                    COUNT(CASE WHEN expiry_date IS NOT NULL AND expiry_date BETWEEN NOW() AND NOW() + INTERVAL '7 days' THEN 1 END) as expiring_soon
                FROM pantry_items
                WHERE user_id = %s
            """
            
            stats = self._execute_query_one(query, (user_id,))
            
            if stats:
                logger.info(f"✅ Got pantry stats for user {user_id}")
                return stats
            
            return {
                'total_items': 0,
                'total_categories': 0,
                'expired_items': 0,
                'expiring_soon': 0
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting pantry stats: {e}", exc_info=True)
            return {
                'total_items': 0,
                'total_categories': 0,
                'expired_items': 0,
                'expiring_soon': 0
            }
    
    def search_items(
        self,
        user_id: int,
        search_term: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search pantry items by name
        
        Args:
            user_id: User ID
            search_term: Search query
            limit: Maximum results
        
        Returns:
            List of matching items
        """
        try:
            query = """
                SELECT *
                FROM pantry_items
                WHERE user_id = %s AND name ILIKE %s
                ORDER BY name
                LIMIT %s
            """
            
            items = self._execute_query(query, (user_id, f'%{search_term}%', limit))
            
            logger.info(f"✅ Found {len(items)} items matching '{search_term}'")
            
            return items
            
        except Exception as e:
            logger.error(f"❌ Error searching pantry items: {e}", exc_info=True)
            return []
    
    def get_items_by_category(
        self,
        user_id: int,
        category: str
    ) -> List[Dict[str, Any]]:
        """
        Get pantry items by category
        
        Args:
            user_id: User ID
            category: Category name
        
        Returns:
            List of items in category
        """
        try:
            query = """
                SELECT *
                FROM pantry_items
                WHERE user_id = %s AND category = %s
                ORDER BY name
            """
            
            items = self._execute_query(query, (user_id, category))
            
            logger.info(f"✅ Got {len(items)} items in category '{category}'")
            
            return items
            
        except Exception as e:
            logger.error(f"❌ Error getting items by category: {e}", exc_info=True)
            return []
