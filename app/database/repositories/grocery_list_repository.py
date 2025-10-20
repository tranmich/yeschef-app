"""
GroceryList Repository
Handles all database operations for grocery lists
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import logging

from .base_repository import BaseRepository

logger = logging.getLogger(__name__)


class GroceryListRepository(BaseRepository):
    """Repository for grocery list data access"""
    
    def __init__(self):
        super().__init__('grocery_lists')
        self.ensure_table_exists()
    
    def ensure_table_exists(self):
        """Create grocery_lists table if it doesn't exist"""
        # Create table if not exists
        create_query = """
            CREATE TABLE IF NOT EXISTS grocery_lists (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                items_json TEXT NOT NULL,
                meal_plan_id INTEGER,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        if self._execute_ddl(create_query, ()):
            logger.info("✅ Grocery lists table ensured")
        else:
            logger.error("❌ Error ensuring grocery_lists table")
        
        # Add name column if it doesn't exist (for existing tables from old schema)
        alter_query = """
            DO $$ 
            BEGIN 
                BEGIN
                    ALTER TABLE grocery_lists ADD COLUMN name TEXT DEFAULT 'My Grocery List';
                EXCEPTION
                    WHEN duplicate_column THEN 
                        -- Column already exists, do nothing
                        NULL;
                END;
            END $$;
        """
        if self._execute_ddl(alter_query, ()):
            logger.info("✅ Grocery lists 'name' column migration complete")
        else:
            logger.warning("⚠️ Could not run name column migration")
    
    # CREATE
    def create_grocery_list(
        self,
        user_id: int,
        name: str,
        items: List[Dict[str, Any]],
        meal_plan_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new grocery list
        
        Args:
            user_id: User ID
            name: Name of the list
            items: List of grocery items
            meal_plan_id: Optional meal plan ID this was generated from
        
        Returns:
            Created grocery list dict or None
        """
        try:
            items_json = json.dumps(items)
            logger.info(f"Creating grocery list: user={user_id}, name={name}, items_count={len(items)}")
            
            # If name is provided, include it; otherwise let database use DEFAULT
            if name:
                query = """
                    INSERT INTO grocery_lists 
                    (user_id, name, items_json, meal_plan_id, created_date, updated_date)
                    VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    RETURNING id, user_id, name, items_json, meal_plan_id,
                              created_date, updated_date
                """
                params = (user_id, name, items_json, meal_plan_id)
            else:
                query = """
                    INSERT INTO grocery_lists 
                    (user_id, items_json, meal_plan_id, created_date, updated_date)
                    VALUES (%s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    RETURNING id, user_id, COALESCE(name, 'My Grocery List') as name, items_json, meal_plan_id,
                              created_date, updated_date
                """
                params = (user_id, items_json, meal_plan_id)
            
            grocery_list = self._execute_insert(query, params)
            
            if grocery_list:
                logger.info(f"Grocery list created successfully: id={grocery_list['id']}")
                # Parse JSON back to list
                if grocery_list.get('items_json'):
                    grocery_list['items'] = json.loads(grocery_list['items_json'])
                    del grocery_list['items_json']
                return grocery_list
            else:
                logger.error("Grocery list creation returned None")
                return None
                
        except Exception as e:
            logger.error(f"Error in create_grocery_list: {e}", exc_info=True)
            return None
    
    # READ
    def get_grocery_list_by_id(self, list_id: int, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Get grocery list by ID"""
        query = """
            SELECT id, user_id, name, items_json, meal_plan_id,
                   created_date, updated_date
            FROM grocery_lists
            WHERE id = %s
        """
        params = [list_id]
        
        # Optionally filter by user_id for security
        if user_id is not None:
            query += " AND user_id = %s"
            params.append(user_id)
        
        result = self._execute_query(query, tuple(params))
        
        if result:
            grocery_list = dict(result[0])
            # Parse JSON
            if grocery_list.get('items_json'):
                grocery_list['items'] = json.loads(grocery_list['items_json'])
                del grocery_list['items_json']
            return grocery_list
        return None
    
    def get_user_grocery_lists(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get all grocery lists for a user"""
        query = """
            SELECT id, user_id, name, items_json, meal_plan_id,
                   created_date, updated_date
            FROM grocery_lists
            WHERE user_id = %s
            ORDER BY created_date DESC
            LIMIT %s OFFSET %s
        """
        
        result = self._execute_query(query, (user_id, limit, offset))
        
        if result:
            grocery_lists = []
            for row in result:
                grocery_list = dict(row)
                # Parse JSON
                if grocery_list.get('items_json'):
                    grocery_list['items'] = json.loads(grocery_list['items_json'])
                    del grocery_list['items_json']
                grocery_lists.append(grocery_list)
            return grocery_lists
        return []
    
    def count_user_grocery_lists(self, user_id: int) -> int:
        """Count total grocery lists for user"""
        query = "SELECT COUNT(*) as count FROM grocery_lists WHERE user_id = %s"
        result = self._execute_query(query, (user_id,))
        return result[0]['count'] if result else 0
    
    def get_grocery_lists_by_meal_plan(self, meal_plan_id: int, user_id: int) -> List[Dict[str, Any]]:
        """Get all grocery lists generated from a specific meal plan"""
        query = """
            SELECT id, user_id, name, items_json, meal_plan_id,
                   created_date, updated_date
            FROM grocery_lists
            WHERE meal_plan_id = %s AND user_id = %s
            ORDER BY created_date DESC
        """
        
        result = self._execute_query(query, (meal_plan_id, user_id))
        
        if result:
            grocery_lists = []
            for row in result:
                grocery_list = dict(row)
                if grocery_list.get('items_json'):
                    grocery_list['items'] = json.loads(grocery_list['items_json'])
                    del grocery_list['items_json']
                grocery_lists.append(grocery_list)
            return grocery_lists
        return []
    
    # UPDATE
    def update_grocery_list(
        self,
        list_id: int,
        user_id: int,
        name: Optional[str] = None,
        items: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[Dict[str, Any]]:
        """Update grocery list"""
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = %s")
            params.append(name)
        
        if items is not None:
            updates.append("items_json = %s")
            params.append(json.dumps(items))
        
        if not updates:
            return self.get_grocery_list_by_id(list_id, user_id)
        
        updates.append("updated_date = CURRENT_TIMESTAMP")
        
        query = f"""
            UPDATE grocery_lists
            SET {', '.join(updates)}
            WHERE id = %s AND user_id = %s
            RETURNING id, user_id, name, items_json, meal_plan_id,
                      created_date, updated_date
        """
        
        params.extend([list_id, user_id])
        grocery_list = self._execute_update(query, tuple(params))
        
        if grocery_list:
            if grocery_list.get('items_json'):
                grocery_list['items'] = json.loads(grocery_list['items_json'])
                del grocery_list['items_json']
            return grocery_list
        return None
    
    def mark_item_purchased(
        self,
        list_id: int,
        user_id: int,
        item_index: int,
        purchased: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Mark a specific item as purchased/unpurchased"""
        grocery_list = self.get_grocery_list_by_id(list_id, user_id)
        if not grocery_list or 'items' not in grocery_list:
            return None
        
        items = grocery_list['items']
        if 0 <= item_index < len(items):
            items[item_index]['purchased'] = purchased
            return self.update_grocery_list(list_id, user_id, items=items)
        
        return None
    
    def clear_purchased_items(self, list_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Remove all purchased items from the list"""
        grocery_list = self.get_grocery_list_by_id(list_id, user_id)
        if not grocery_list or 'items' not in grocery_list:
            return None
        
        # Filter out purchased items
        items = grocery_list['items']
        unpurchased_items = [item for item in items if not item.get('purchased', False)]
        
        return self.update_grocery_list(list_id, user_id, items=unpurchased_items)
    
    # DELETE
    def delete_grocery_list(self, list_id: int, user_id: int) -> bool:
        """Delete grocery list"""
        query = "DELETE FROM grocery_lists WHERE id = %s AND user_id = %s"
        rows_deleted = self._execute_delete(query, (list_id, user_id))
        return rows_deleted > 0
    
    # HELPER METHODS
    def get_list_stats(self, list_id: int, user_id: int) -> Dict[str, Any]:
        """Get statistics about a grocery list"""
        grocery_list = self.get_grocery_list_by_id(list_id, user_id)
        if not grocery_list or 'items' not in grocery_list:
            return {}
        
        items = grocery_list['items']
        total_items = len(items)
        purchased_items = sum(1 for item in items if item.get('purchased', False))
        
        return {
            'total_items': total_items,
            'purchased_items': purchased_items,
            'remaining_items': total_items - purchased_items,
            'completion_percentage': (purchased_items / total_items * 100) if total_items > 0 else 0
        }
