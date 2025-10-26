"""
GroceryList Service
Business logic for grocery list operations
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from .base_service import BaseService
from ..database.repositories.grocery_list_repository import GroceryListRepository
from ..database.repositories.meal_plan_repository import MealPlanRepository

logger = logging.getLogger(__name__)


class GroceryListService(BaseService):
    """Service for grocery list business logic"""
    
    def __init__(self):
        super().__init__()
        self.grocery_list_repo = GroceryListRepository()
        self.meal_plan_repo = MealPlanRepository()
    
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
            items: List of items [{name, quantity, unit, category, purchased}, ...]
            meal_plan_id: Optional meal plan ID
        
        Returns:
            Created grocery list with stats
        """
        try:
            # Ensure each item has required structure
            formatted_items = []
            for item in items:
                formatted_item = {
                    'name': item.get('name', ''),
                    'quantity': item.get('quantity', ''),
                    'unit': item.get('unit', ''),
                    'category': item.get('category', 'Other'),
                    'purchased': item.get('purchased', False)
                }
                formatted_items.append(formatted_item)
            
            # Create grocery list
            grocery_list = self.grocery_list_repo.create_grocery_list(
                user_id=user_id,
                name=name,
                items=formatted_items,
                meal_plan_id=meal_plan_id
            )
            
            if grocery_list:
                # Add stats - skip this if it fails
                try:
                    stats = self.grocery_list_repo.get_list_stats(grocery_list['id'], user_id)
                    grocery_list['stats'] = stats
                except Exception as e:
                    logger.error(f"Failed to get stats, using defaults: {e}")
                    grocery_list['stats'] = {
                        'total_items': len(formatted_items),
                        'purchased_items': 0,
                        'remaining_items': len(formatted_items),
                        'completion_percentage': 0
                    }
                logger.info(f"Created grocery list {grocery_list['id']} for user {user_id}")
            
            return grocery_list
            
        except Exception as e:
            logger.error(f"Error creating grocery list: {e}")
            return None
    
    def create_from_meal_plan(
        self,
        meal_plan_id: int,
        user_id: int,
        list_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create grocery list from meal plan
        Uses MealPlanService logic to generate ingredients
        
        Args:
            meal_plan_id: Meal plan ID
            user_id: User ID
            list_name: Optional custom name
        
        Returns:
            Created grocery list
        """
        try:
            logger.info(f"🔵 create_from_meal_plan: meal_plan={meal_plan_id}, user={user_id}")
            
            # Import here to avoid circular dependency
            from .meal_plan_service import MealPlanService
            
            meal_plan_service = MealPlanService()
            
            # Generate ingredients from meal plan
            logger.info(f"🔵 Generating ingredients from meal plan {meal_plan_id}...")
            grocery_data = meal_plan_service.generate_grocery_list_from_meal_plan(
                plan_id=meal_plan_id,
                user_id=user_id
            )
            
            if not grocery_data or not grocery_data.get('ingredients'):
                logger.error(f"❌ No ingredients found in meal plan {meal_plan_id}")
                return None
            
            logger.info(f"✅ Generated {len(grocery_data['ingredients'])} ingredients")
            
            # Create name if not provided
            if not list_name:
                meal_plan_name = grocery_data.get('meal_plan_name', 'Meal Plan')
                list_name = f"Grocery List - {meal_plan_name}"
            
            logger.info(f"🔵 Creating grocery list: '{list_name}'")
            
            # Create grocery list
            result = self.create_grocery_list(
                user_id=user_id,
                name=list_name,
                items=grocery_data['ingredients'],
                meal_plan_id=meal_plan_id
            )
            
            if result:
                logger.info(f"✅ Grocery list created successfully: ID={result.get('id')}")
            else:
                logger.error(f"❌ create_grocery_list returned None!")
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating grocery list from meal plan {meal_plan_id}: {e}")
            return None
    
    def get_grocery_list(self, list_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Get grocery list by ID with stats"""
        try:
            grocery_list = self.grocery_list_repo.get_grocery_list_by_id(list_id, user_id)
            
            if grocery_list:
                # Add stats
                stats = self.grocery_list_repo.get_list_stats(list_id, user_id)
                grocery_list['stats'] = stats
            
            return grocery_list
                
        except Exception as e:
            logger.error(f"Error getting grocery list {list_id}: {e}")
            return None
    
    def get_user_grocery_lists(
        self,
        user_id: int,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Get user's grocery lists with pagination
        
        Returns:
            Dict with grocery lists, pagination info, and stats
        """
        try:
            offset = (page - 1) * per_page
            
            # Get grocery lists
            grocery_lists = self.grocery_list_repo.get_user_grocery_lists(
                user_id=user_id,
                limit=per_page,
                offset=offset
            )
            
            # Add stats to each list
            for grocery_list in grocery_lists:
                stats = self.grocery_list_repo.get_list_stats(grocery_list['id'], user_id)
                grocery_list['stats'] = stats
            
            # Get total count
            total = self.grocery_list_repo.count_user_grocery_lists(user_id)
            
            # Calculate pagination
            total_pages = (total + per_page - 1) // per_page
            has_next = page < total_pages
            has_prev = page > 1
            
            return {
                'grocery_lists': grocery_lists,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'total_pages': total_pages,
                    'has_next': has_next,
                    'has_prev': has_prev
                },
                'stats': {
                    'total_lists': total
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting user grocery lists: {e}")
            return {
                'grocery_lists': [],
                'pagination': {},
                'stats': {}
            }
    
    def update_grocery_list(
        self,
        list_id: int,
        user_id: int,
        name: Optional[str] = None,
        items: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[Dict[str, Any]]:
        """Update grocery list"""
        try:
            logger.info(f"🔄 Service: Updating list {list_id} for user {user_id}")
            logger.info(f"📝 Service: name={name}, items_count={len(items) if items else 'None'}")
            
            grocery_list = self.grocery_list_repo.update_grocery_list(
                list_id=list_id,
                user_id=user_id,
                name=name,
                items=items
            )
            
            if grocery_list:
                logger.info(f"✅ Service: List updated successfully")
                # Add stats
                stats = self.grocery_list_repo.get_list_stats(list_id, user_id)
                grocery_list['stats'] = stats
            else:
                logger.error(f"❌ Service: Repository returned None for list {list_id}")
            
            return grocery_list
            
        except Exception as e:
            logger.error(f"Error updating grocery list {list_id}: {e}", exc_info=True)
            return None
    
    def add_item(
        self,
        list_id: int,
        user_id: int,
        item: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Add a single item to grocery list"""
        try:
            grocery_list = self.grocery_list_repo.get_grocery_list_by_id(list_id, user_id)
            if not grocery_list:
                return None
            
            items = grocery_list.get('items', [])
            items.append({
                'name': item.get('name', ''),
                'quantity': item.get('quantity', ''),
                'unit': item.get('unit', ''),
                'category': item.get('category', 'Other'),
                'purchased': False
            })
            
            return self.update_grocery_list(list_id, user_id, items=items)
            
        except Exception as e:
            logger.error(f"Error adding item to list {list_id}: {e}")
            return None
    
    def remove_item(
        self,
        list_id: int,
        user_id: int,
        item_index: int
    ) -> Optional[Dict[str, Any]]:
        """Remove item from grocery list"""
        try:
            grocery_list = self.grocery_list_repo.get_grocery_list_by_id(list_id, user_id)
            if not grocery_list:
                return None
            
            items = grocery_list.get('items', [])
            if 0 <= item_index < len(items):
                items.pop(item_index)
                return self.update_grocery_list(list_id, user_id, items=items)
            
            return None
            
        except Exception as e:
            logger.error(f"Error removing item from list {list_id}: {e}")
            return None
    
    def mark_item_purchased(
        self,
        list_id: int,
        user_id: int,
        item_index: int,
        purchased: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Mark item as purchased/unpurchased"""
        try:
            grocery_list = self.grocery_list_repo.mark_item_purchased(
                list_id=list_id,
                user_id=user_id,
                item_index=item_index,
                purchased=purchased
            )
            
            if grocery_list:
                # Add stats
                stats = self.grocery_list_repo.get_list_stats(list_id, user_id)
                grocery_list['stats'] = stats
            
            return grocery_list
            
        except Exception as e:
            logger.error(f"Error marking item in list {list_id}: {e}")
            return None
    
    def clear_purchased_items(self, list_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Remove all purchased items"""
        try:
            grocery_list = self.grocery_list_repo.clear_purchased_items(list_id, user_id)
            
            if grocery_list:
                # Add stats
                stats = self.grocery_list_repo.get_list_stats(list_id, user_id)
                grocery_list['stats'] = stats
                logger.info(f"Cleared purchased items from list {list_id}")
            
            return grocery_list
            
        except Exception as e:
            logger.error(f"Error clearing purchased items from list {list_id}: {e}")
            return None
    
    def delete_grocery_list(self, list_id: int, user_id: int) -> bool:
        """Delete grocery list"""
        try:
            success = self.grocery_list_repo.delete_grocery_list(list_id, user_id)
            if success:
                logger.info(f"Deleted grocery list {list_id} for user {user_id}")
            return success
        except Exception as e:
            logger.error(f"Error deleting grocery list {list_id}: {e}")
            return False
