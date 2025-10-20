"""
MealPlan Repository
Handles all database operations for meal plans
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import logging

from .base_repository import BaseRepository

logger = logging.getLogger(__name__)


class MealPlanRepository(BaseRepository):
    """Repository for meal plan data access"""
    
    def __init__(self):
        super().__init__('meal_plans')
    
    # CREATE
    def create_meal_plan(
        self,
        user_id: int,
        plan_name: str,
        week_start_date: str,
        plan_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new meal plan
        
        Args:
            user_id: User ID
            plan_name: Name of the meal plan
            week_start_date: Start date (YYYY-MM-DD)
            plan_data: Meal plan data (days, meals, recipes)
        
        Returns:
            Created meal plan dict or None
        """
        query = """
            INSERT INTO meal_plans 
            (user_id, plan_name, week_start_date, plan_data_json, created_date, updated_date)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING id, user_id, plan_name, week_start_date, plan_data_json, 
                      created_date, updated_date
        """
        
        plan_data_json = json.dumps(plan_data)
        meal_plan = self._execute_insert(query, (user_id, plan_name, week_start_date, plan_data_json))
        
        if meal_plan:
            # Parse JSON back to dict
            if meal_plan.get('plan_data_json'):
                meal_plan['plan_data'] = json.loads(meal_plan['plan_data_json'])
                del meal_plan['plan_data_json']
            return meal_plan
        return None
    
    # READ
    def get_meal_plan_by_id(self, plan_id: int, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Get meal plan by ID"""
        query = """
            SELECT id, user_id, plan_name, week_start_date, plan_data_json,
                   created_date, updated_date
            FROM meal_plans
            WHERE id = %s
        """
        params = [plan_id]
        
        # Optionally filter by user_id for security
        if user_id is not None:
            query += " AND user_id = %s"
            params.append(user_id)
        
        result = self.execute_query(query, tuple(params))
        
        if result:
            meal_plan = dict(result[0])
            # Parse JSON
            if meal_plan.get('plan_data_json'):
                meal_plan['plan_data'] = json.loads(meal_plan['plan_data_json'])
                del meal_plan['plan_data_json']
            return meal_plan
        return None
    
    def get_user_meal_plans(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get all meal plans for a user"""
        query = """
            SELECT id, user_id, plan_name, week_start_date, plan_data_json,
                   created_date, updated_date
            FROM meal_plans
            WHERE user_id = %s
            ORDER BY week_start_date DESC, created_date DESC
            LIMIT %s OFFSET %s
        """
        
        result = self.execute_query(query, (user_id, limit, offset))
        
        if result:
            meal_plans = []
            for row in result:
                meal_plan = dict(row)
                # Parse JSON
                if meal_plan.get('plan_data_json'):
                    meal_plan['plan_data'] = json.loads(meal_plan['plan_data_json'])
                    del meal_plan['plan_data_json']
                meal_plans.append(meal_plan)
            return meal_plans
        return []
    
    def get_meal_plans_by_date_range(
        self,
        user_id: int,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """Get meal plans within a date range"""
        query = """
            SELECT id, user_id, plan_name, week_start_date, plan_data_json,
                   created_date, updated_date
            FROM meal_plans
            WHERE user_id = %s 
              AND week_start_date >= %s 
              AND week_start_date <= %s
            ORDER BY week_start_date ASC
        """
        
        result = self.execute_query(query, (user_id, start_date, end_date))
        
        if result:
            meal_plans = []
            for row in result:
                meal_plan = dict(row)
                if meal_plan.get('plan_data_json'):
                    meal_plan['plan_data'] = json.loads(meal_plan['plan_data_json'])
                    del meal_plan['plan_data_json']
                meal_plans.append(meal_plan)
            return meal_plans
        return []
    
    def count_user_meal_plans(self, user_id: int) -> int:
        """Count total meal plans for user"""
        query = "SELECT COUNT(*) as count FROM meal_plans WHERE user_id = %s"
        result = self.execute_query(query, (user_id,))
        return result[0]['count'] if result else 0
    
    # UPDATE
    def update_meal_plan(
        self,
        plan_id: int,
        user_id: int,
        plan_name: Optional[str] = None,
        week_start_date: Optional[str] = None,
        plan_data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Update meal plan"""
        updates = []
        params = []
        
        if plan_name is not None:
            updates.append("plan_name = %s")
            params.append(plan_name)
        
        if week_start_date is not None:
            updates.append("week_start_date = %s")
            params.append(week_start_date)
        
        if plan_data is not None:
            updates.append("plan_data_json = %s")
            params.append(json.dumps(plan_data))
        
        if not updates:
            return self.get_meal_plan_by_id(plan_id, user_id)
        
        updates.append("updated_date = CURRENT_TIMESTAMP")
        
        query = f"""
            UPDATE meal_plans
            SET {', '.join(updates)}
            WHERE id = %s AND user_id = %s
            RETURNING id, user_id, plan_name, week_start_date, plan_data_json,
                      created_date, updated_date
        """
        
        params.extend([plan_id, user_id])
        result = self.execute_query(query, tuple(params))
        
        if result:
            meal_plan = dict(result[0])
            if meal_plan.get('plan_data_json'):
                meal_plan['plan_data'] = json.loads(meal_plan['plan_data_json'])
                del meal_plan['plan_data_json']
            return meal_plan
        return None
    
    # DELETE
    def delete_meal_plan(self, plan_id: int, user_id: int) -> bool:
        """Delete meal plan"""
        query = "DELETE FROM meal_plans WHERE id = %s AND user_id = %s"
        result = self.execute_query(query, (plan_id, user_id))
        return result is not None
    
    # HELPER METHODS
    def get_recipes_in_meal_plan(self, plan_id: int, user_id: int) -> List[int]:
        """
        Extract all recipe IDs from a meal plan
        
        Returns:
            List of recipe IDs used in the meal plan
        """
        meal_plan = self.get_meal_plan_by_id(plan_id, user_id)
        if not meal_plan or 'plan_data' not in meal_plan:
            return []
        
        recipe_ids = set()
        plan_data = meal_plan['plan_data']
        
        # Extract recipe IDs from plan data
        # Assuming structure: {"monday": {"breakfast": {"recipe_id": 123}, ...}, ...}
        for day, meals in plan_data.items():
            if isinstance(meals, dict):
                for meal_type, meal_info in meals.items():
                    if isinstance(meal_info, dict) and 'recipe_id' in meal_info:
                        recipe_ids.add(meal_info['recipe_id'])
        
        return list(recipe_ids)
    
    def get_meal_plan_with_recipes(self, plan_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get meal plan with full recipe details
        This will need RecipeRepository to fetch recipe details
        """
        meal_plan = self.get_meal_plan_by_id(plan_id, user_id)
        if not meal_plan:
            return None
        
        recipe_ids = self.get_recipes_in_meal_plan(plan_id, user_id)
        meal_plan['recipe_ids'] = recipe_ids
        meal_plan['recipe_count'] = len(recipe_ids)
        
        return meal_plan
