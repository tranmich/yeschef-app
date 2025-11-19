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
        """Create grocery_lists table if it doesn't exist, migrate legacy schema"""
        # Create table if not exists
        create_query = """
            CREATE TABLE IF NOT EXISTS grocery_lists (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                items_json TEXT NOT NULL DEFAULT '[]',
                name TEXT NOT NULL DEFAULT 'Grocery List',
                meal_plan_id INTEGER,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        if self._execute_ddl(create_query, ()):
            logger.info("✅ Grocery lists table ensured")
        else:
            logger.error("❌ Error ensuring grocery_lists table")
        
        # Migrate legacy schema - add columns if they don't exist
        migrations = [
            "ALTER TABLE grocery_lists ADD COLUMN IF NOT EXISTS items_json TEXT NOT NULL DEFAULT '[]'",
            "ALTER TABLE grocery_lists ADD COLUMN IF NOT EXISTS name TEXT NOT NULL DEFAULT 'Grocery List'",
            "ALTER TABLE grocery_lists ADD COLUMN IF NOT EXISTS meal_plan_id INTEGER",
            "ALTER TABLE grocery_lists ADD COLUMN IF NOT EXISTS created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "ALTER TABLE grocery_lists ADD COLUMN IF NOT EXISTS updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            # New whiteboard integration columns (matching wb table pattern)
            "ALTER TABLE grocery_lists ADD COLUMN IF NOT EXISTS hid INTEGER", # household_id (like wb.hid)
            "ALTER TABLE grocery_lists ADD COLUMN IF NOT EXISTS wid INTEGER", # whiteboard_id (like wbo.wid)
            "ALTER TABLE grocery_lists ADD COLUMN IF NOT EXISTS wp JSONB", # widget_position {x, y, size}
            "ALTER TABLE grocery_lists ADD COLUMN IF NOT EXISTS lr JSONB", # linked_recipes [recipe_ids]
            "ALTER TABLE grocery_lists ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP", # soft delete (like wb.deleted_at)
            # Indexes for performance
            "CREATE INDEX IF NOT EXISTS idx_grocery_lists_user_id ON grocery_lists(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_grocery_lists_hid ON grocery_lists(hid)",
            "CREATE INDEX IF NOT EXISTS idx_grocery_lists_wid ON grocery_lists(wid)",
            "CREATE INDEX IF NOT EXISTS idx_grocery_lists_deleted ON grocery_lists(deleted_at)"
        ]
        
        for migration in migrations:
            try:
                if self._execute_ddl(migration, ()):
                    logger.info(f"✅ Migration: {migration[:60]}...")
            except Exception as e:
                logger.warning(f"⚠️ Migration skipped (may already exist): {str(e)[:60]}")
        
        logger.info("✅ Grocery lists schema migrations complete")
    
    # CREATE
    def create_grocery_list(
        self,
        user_id: int,
        name: str,
        items: List[Dict[str, Any]],
        meal_plan_id: Optional[int] = None,
        household_id: Optional[int] = None,
        whiteboard_id: Optional[int] = None,
        widget_position: Optional[Dict[str, Any]] = None,
        linked_recipe_ids: Optional[List[int]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new grocery list (supports both legacy and whiteboard modes)
        
        Args:
            user_id: User ID
            name: Name of the list
            items: List of grocery items
            meal_plan_id: Optional meal plan ID
            household_id: Optional household ID (for whiteboard lists)
            whiteboard_id: Optional whiteboard ID (for whiteboard lists)
            widget_position: Optional widget position {x, y, size}
            linked_recipe_ids: Optional list of linked recipe IDs
        
        Returns:
            Created grocery list dict or None
        """
        try:
            items_data = json.dumps(items)
            logger.info(f"🔵 PHASE 2 CREATE: user={user_id}, name={name}, items_count={len(items)}, whiteboard={whiteboard_id}")
            
            # PHASE 2: Clean schema - single columns only!
            query = """
                INSERT INTO grocery_lists 
                (user_id, name, list_data, recipe_ids, meal_plan_id, 
                 hid, wid, wp, lr, created_at, updated_at)
                VALUES (%s, %s, %s::jsonb, %s, %s, %s, %s, %s::jsonb, %s::jsonb, NOW(), NOW())
                RETURNING id, user_id, name, list_data as items,
                          meal_plan_id, hid, wid, wp, lr, 
                          created_at, updated_at
            """
            
            wp_json = json.dumps(widget_position) if widget_position else None
            lr_json = json.dumps(linked_recipe_ids) if linked_recipe_ids else None
            recipe_ids_array = linked_recipe_ids if linked_recipe_ids else []
            
            # PHASE 2: Single column set only
            params = (user_id, name, items_data, recipe_ids_array, meal_plan_id, household_id, whiteboard_id, wp_json, lr_json)
            
            grocery_list = self._execute_insert(query, params)
            
            if grocery_list:
                logger.info(f"✅ Grocery list created (Phase 2 clean schema): id={grocery_list['id']}")
                # Parse JSONB fields
                if grocery_list.get('items'):
                    if isinstance(grocery_list['items'], str):
                        grocery_list['items'] = json.loads(grocery_list['items'])
                
                if grocery_list.get('wp'):
                    grocery_list['widget_position'] = grocery_list.pop('wp') if isinstance(grocery_list['wp'], dict) else json.loads(grocery_list.pop('wp'))
                
                if grocery_list.get('lr'):
                    grocery_list['linked_recipe_ids'] = grocery_list.pop('lr') if isinstance(grocery_list['lr'], list) else json.loads(grocery_list.pop('lr'))
                
                # Map compact column names to readable names
                if 'hid' in grocery_list:
                    grocery_list['household_id'] = grocery_list.pop('hid')
                if 'wid' in grocery_list:
                    grocery_list['whiteboard_id'] = grocery_list.pop('wid')
                
                return grocery_list
            else:
                logger.error("❌ Grocery list creation returned None")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error in create_grocery_list: {e}", exc_info=True)
            return None
    
    # READ
    def get_grocery_list_by_id(self, list_id: int, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Get grocery list by ID"""
        query = """
            SELECT id, user_id, name, list_data as items, hid, wid, wp, lr, created_at, updated_at
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
            # Parse JSONB items
            if grocery_list.get('items'):
                if isinstance(grocery_list['items'], str):
                    grocery_list['items'] = json.loads(grocery_list['items'])
            # Map compact columns
            if 'hid' in grocery_list:
                grocery_list['household_id'] = grocery_list.pop('hid')
            if 'wid' in grocery_list:
                grocery_list['whiteboard_id'] = grocery_list.pop('wid')
            if 'wp' in grocery_list:
                grocery_list['widget_position'] = grocery_list.pop('wp')
            if 'lr' in grocery_list:
                grocery_list['linked_recipe_ids'] = grocery_list.pop('lr')
            return grocery_list
        return None
    
    def get_user_grocery_lists(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all grocery lists accessible by a user
        Includes both:
        - Personal lists (user_id matches and not linked to deleted whiteboards)
        - Household collaborative lists (user is member of household and whiteboard not deleted)
        """
        query = """
            SELECT DISTINCT gl.id, gl.user_id, gl.name, gl.list_data as items, gl.hid, gl.wid, gl.created_at, gl.updated_at
            FROM grocery_lists gl
            LEFT JOIN household_members hm ON gl.hid = hm.household_id
            LEFT JOIN wb ON gl.wid = wb.id
            WHERE (gl.user_id = %s OR (gl.hid IS NOT NULL AND hm.user_id = %s))
              AND gl.deleted_at IS NULL
              AND (gl.wid IS NULL OR wb.deleted_at IS NULL)
            ORDER BY gl.updated_at DESC
            LIMIT %s OFFSET %s
        """
        
        logger.info(f"🔍 Fetching grocery lists for user {user_id}, limit={limit}, offset={offset}")
        result = self._execute_query(query, (user_id, user_id, limit, offset))
        logger.info(f"📊 Query returned {len(result) if result else 0} lists")
        
        if result:
            grocery_lists = []
            for row in result:
                grocery_list = dict(row)
                
                # Parse items (already aliased as 'items' in query, but might be JSONB)
                if grocery_list.get('items'):
                    if isinstance(grocery_list['items'], str):
                        try:
                            grocery_list['items'] = json.loads(grocery_list['items'])
                        except (json.JSONDecodeError, TypeError):
                            logger.warning(f"Failed to parse items for list {grocery_list.get('id')}, using empty array")
                            grocery_list['items'] = []
                    elif not isinstance(grocery_list['items'], list):
                        grocery_list['items'] = []
                else:
                    grocery_list['items'] = []
                
                # Map compact column names to standard (keep standard format)
                if 'hid' in grocery_list:
                    grocery_list['household_id'] = grocery_list['hid']
                    del grocery_list['hid']
                if 'wid' in grocery_list:
                    grocery_list['whiteboard_id'] = grocery_list['wid']
                    del grocery_list['wid']
                
                # Keep standard timestamp names (created_at, updated_at)
                # No conversion needed - already standard!
                grocery_lists.append(grocery_list)
            return grocery_lists
        return []
    
    def count_user_grocery_lists(self, user_id: int) -> int:
        """
        Count total grocery lists accessible by user
        Includes both personal and household lists, excluding deleted whiteboards
        """
        query = """
            SELECT COUNT(DISTINCT gl.id) as count 
            FROM grocery_lists gl
            LEFT JOIN household_members hm ON gl.hid = hm.household_id
            LEFT JOIN wb ON gl.wid = wb.id
            WHERE (gl.user_id = %s OR (gl.hid IS NOT NULL AND hm.user_id = %s))
              AND gl.deleted_at IS NULL
              AND (gl.wid IS NULL OR wb.deleted_at IS NULL)
        """
        result = self._execute_query(query, (user_id, user_id))
        return result[0]['count'] if result else 0
    
    def get_grocery_lists_by_meal_plan(self, meal_plan_id: int, user_id: int) -> List[Dict[str, Any]]:
        """Get all grocery lists generated from a specific meal plan"""
        query = """
            SELECT id, user_id, list_name, items_json, meal_plan_id,
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
                # Map list_name to name for API consistency
                if 'list_name' in grocery_list:
                    grocery_list['name'] = grocery_list['list_name']
                    del grocery_list['list_name']
                if grocery_list.get('items_json'):
                    grocery_list['items'] = json.loads(grocery_list['items_json'])
                    del grocery_list['items_json']
                grocery_lists.append(grocery_list)
            return grocery_lists
        return []
    
    def get_grocery_lists_by_whiteboard(self, whiteboard_id: int, user_id: int) -> List[Dict[str, Any]]:
        """Get all grocery lists for a specific whiteboard (Phase 2: clean schema)"""
        query = """
            SELECT id, user_id, name, list_data as items, meal_plan_id, hid, wid, wp, lr,
                   created_at, updated_at
            FROM grocery_lists
            WHERE wid = %s AND user_id = %s AND deleted_at IS NULL
            ORDER BY updated_at DESC
        """
        
        result = self._execute_query(query, (whiteboard_id, user_id))
        
        if result:
            grocery_lists = []
            for row in result:
                grocery_list = dict(row)
                # Parse JSONB fields
                if grocery_list.get('items'):
                    if isinstance(grocery_list['items'], str):
                        grocery_list['items'] = json.loads(grocery_list['items'])
                if grocery_list.get('wp'):
                    grocery_list['widget_position'] = grocery_list['wp'] if isinstance(grocery_list['wp'], dict) else json.loads(grocery_list['wp'])
                    logger.info(f"  📍 Loaded widget_position for list {grocery_list.get('id')}: {grocery_list['widget_position']}")
                    del grocery_list['wp']
                if grocery_list.get('lr'):
                    grocery_list['linked_recipe_ids'] = grocery_list['lr'] if isinstance(grocery_list['lr'], list) else json.loads(grocery_list['lr'])
                    del grocery_list['lr']
                # Map compact names
                if 'hid' in grocery_list:
                    grocery_list['household_id'] = grocery_list['hid']
                    del grocery_list['hid']
                if 'wid' in grocery_list:
                    grocery_list['whiteboard_id'] = grocery_list['wid']
                    del grocery_list['wid']
                grocery_lists.append(grocery_list)
            return grocery_lists
        return []
    
    # UPDATE
    def update_grocery_list(
        self,
        list_id: int,
        user_id: int,
        name: Optional[str] = None,
        items: Optional[List[Dict[str, Any]]] = None,
        widget_position: Optional[Dict[str, Any]] = None,
        linked_recipe_ids: Optional[List[int]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        UNIFIED UPDATE METHOD - Writes to ALL columns for backward compatibility
        
        Phase 2: All systems use clean schema:
        - name (single source)
        - list_data (JSONB, single source)
        - updated_at (single source)
        """
        updates = []
        params = []
        
        logger.info(f"🔵 PHASE 2 UPDATE: list_id={list_id}, user_id={user_id}")
        
        if name is not None:
            updates.append("name = %s")
            params.append(name)
            logger.info(f"  📝 Updating name: {name}")
        
        if items is not None:
            items_json_str = json.dumps(items)
            updates.append("list_data = %s::jsonb")
            params.append(items_json_str)
            logger.info(f"  📦 Updating items: {len(items)} items")
        
        if widget_position is not None:
            updates.append("wp = %s::jsonb")
            params.append(json.dumps(widget_position))
            logger.info(f"  📐 Updating widget_position: {widget_position}")
        
        if linked_recipe_ids is not None:
            updates.append("lr = %s::jsonb")
            params.append(json.dumps(linked_recipe_ids))
            logger.info(f"  🔗 Updating linked_recipes: {linked_recipe_ids}")
        
        if not updates:
            logger.warning("  ⚠️ No fields to update")
            return self.get_grocery_list_by_id(list_id, user_id)
        
        # Update timestamp
        updates.append("updated_at = NOW()")
        
        params.extend([list_id, user_id, user_id])
        
        # Allow household members to edit collaborative lists
        query = f"""
            UPDATE grocery_lists gl
            SET {', '.join(updates)}
            WHERE gl.id = %s 
              AND gl.deleted_at IS NULL
              AND (
                  gl.user_id = %s  -- User is owner
                  OR EXISTS (      -- OR user is household member
                      SELECT 1 FROM household_members hm
                      WHERE hm.household_id = gl.hid
                        AND hm.user_id = %s
                  )
              )
            RETURNING id, user_id, name, list_data as items,
                      hid, wid, wp, lr, created_at, updated_at
        """
        
        logger.info(f"  🔍 Executing Phase 2 update with {len(params)} params")
        
        # CRITICAL FIX: Use _execute_update (with transaction/commit) not _execute_query!
        result = self._execute_update(query, tuple(params))
        
        if result:
            grocery_list = dict(result)
            
            # Parse JSONB fields
            if grocery_list.get('items'):
                if isinstance(grocery_list['items'], str):
                    grocery_list['items'] = json.loads(grocery_list['items'])
            
            if grocery_list.get('wp'):
                grocery_list['widget_position'] = grocery_list.pop('wp') if isinstance(grocery_list['wp'], dict) else json.loads(grocery_list.pop('wp'))
            
            if grocery_list.get('lr'):
                grocery_list['linked_recipe_ids'] = grocery_list.pop('lr') if isinstance(grocery_list['lr'], list) else json.loads(grocery_list.pop('lr'))
            
            # Map compact column names to readable names
            if 'hid' in grocery_list:
                grocery_list['household_id'] = grocery_list.pop('hid')
            if 'wid' in grocery_list:
                grocery_list['whiteboard_id'] = grocery_list.pop('wid')
            
            logger.info(f"✅ Grocery list {list_id} updated successfully (unified)")
            return grocery_list
        
        logger.error(f"❌ Update failed - list {list_id} not found or unauthorized")
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
