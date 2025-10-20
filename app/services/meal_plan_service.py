"""
MealPlan Service
Business logic for meal plan operations
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from .base_service import BaseService
from ..database.repositories.meal_plan_repository import MealPlanRepository
from ..database.repositories.recipe_repository import RecipeRepository

logger = logging.getLogger(__name__)


class MealPlanService(BaseService):
    """Service for meal plan business logic"""
    
    def __init__(self):
        super().__init__()
        self.meal_plan_repo = MealPlanRepository()
        self.recipe_repo = RecipeRepository()
    
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
            plan_data: Meal plan data structure
        
        Returns:
            Created meal plan with details
        """
        try:
            # Validate date format
            try:
                datetime.strptime(week_start_date, '%Y-%m-%d')
            except ValueError:
                logger.error(f"Invalid date format: {week_start_date}")
                return None
            
            # Create meal plan
            meal_plan = self.meal_plan_repo.create_meal_plan(
                user_id=user_id,
                plan_name=plan_name,
                week_start_date=week_start_date,
                plan_data=plan_data
            )
            
            if meal_plan:
                logger.info(f"Created meal plan {meal_plan['id']} for user {user_id}")
            
            return meal_plan
            
        except Exception as e:
            logger.error(f"Error creating meal plan: {e}")
            return None
    
    def get_meal_plan(self, plan_id: int, user_id: int, include_recipes: bool = False) -> Optional[Dict[str, Any]]:
        """
        Get meal plan by ID
        
        Args:
            plan_id: Meal plan ID
            user_id: User ID (for authorization)
            include_recipes: Whether to include full recipe details
        
        Returns:
            Meal plan dict or None
        """
        try:
            if include_recipes:
                meal_plan = self.meal_plan_repo.get_meal_plan_with_recipes(plan_id, user_id)
                
                # Fetch full recipe details
                if meal_plan and 'recipe_ids' in meal_plan:
                    recipes = []
                    for recipe_id in meal_plan['recipe_ids']:
                        recipe = self.recipe_repo.get_recipe_by_id(recipe_id, user_id)
                        if recipe:
                            recipes.append(recipe)
                    meal_plan['recipes'] = recipes
                
                return meal_plan
            else:
                return self.meal_plan_repo.get_meal_plan_by_id(plan_id, user_id)
                
        except Exception as e:
            logger.error(f"Error getting meal plan {plan_id}: {e}")
            return None
    
    def get_user_meal_plans(
        self,
        user_id: int,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Get user's meal plans with pagination
        
        Returns:
            Dict with meal plans, pagination info, and stats
        """
        try:
            offset = (page - 1) * per_page
            
            # Get meal plans
            meal_plans = self.meal_plan_repo.get_user_meal_plans(
                user_id=user_id,
                limit=per_page,
                offset=offset
            )
            
            # Get total count
            total = self.meal_plan_repo.count_user_meal_plans(user_id)
            
            # Calculate pagination
            total_pages = (total + per_page - 1) // per_page
            has_next = page < total_pages
            has_prev = page > 1
            
            return {
                'meal_plans': meal_plans,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'total_pages': total_pages,
                    'has_next': has_next,
                    'has_prev': has_prev
                },
                'stats': {
                    'total_meal_plans': total
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting user meal plans: {e}")
            return {
                'meal_plans': [],
                'pagination': {},
                'stats': {}
            }
    
    def get_meal_plans_by_date_range(
        self,
        user_id: int,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """Get meal plans within date range"""
        try:
            return self.meal_plan_repo.get_meal_plans_by_date_range(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date
            )
        except Exception as e:
            logger.error(f"Error getting meal plans by date range: {e}")
            return []
    
    def update_meal_plan(
        self,
        plan_id: int,
        user_id: int,
        plan_name: Optional[str] = None,
        week_start_date: Optional[str] = None,
        plan_data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Update meal plan"""
        try:
            # Validate date if provided
            if week_start_date:
                try:
                    datetime.strptime(week_start_date, '%Y-%m-%d')
                except ValueError:
                    logger.error(f"Invalid date format: {week_start_date}")
                    return None
            
            return self.meal_plan_repo.update_meal_plan(
                plan_id=plan_id,
                user_id=user_id,
                plan_name=plan_name,
                week_start_date=week_start_date,
                plan_data=plan_data
            )
            
        except Exception as e:
            logger.error(f"Error updating meal plan {plan_id}: {e}")
            return None
    
    def delete_meal_plan(self, plan_id: int, user_id: int) -> bool:
        """Delete meal plan"""
        try:
            success = self.meal_plan_repo.delete_meal_plan(plan_id, user_id)
            if success:
                logger.info(f"Deleted meal plan {plan_id} for user {user_id}")
            return success
        except Exception as e:
            logger.error(f"Error deleting meal plan {plan_id}: {e}")
            return False
    
    def generate_grocery_list_from_meal_plan(
        self,
        plan_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Generate a grocery list from a meal plan
        Combines all ingredients from all recipes in the plan
        
        Returns:
            Dict with combined ingredients
        """
        try:
            # Get meal plan with recipes
            meal_plan = self.get_meal_plan(plan_id, user_id, include_recipes=True)
            if not meal_plan or 'recipes' not in meal_plan:
                return {'ingredients': [], 'recipe_count': 0}
            
            # Combine all ingredients
            combined_ingredients = {}
            
            for recipe in meal_plan['recipes']:
                if 'ingredients' not in recipe:
                    continue
                
                # Parse ingredients if it's a JSON string
                ingredients = recipe['ingredients']
                if isinstance(ingredients, str):
                    import json
                    try:
                        ingredients = json.loads(ingredients)
                    except:
                        continue
                
                # Add ingredients to combined list
                if isinstance(ingredients, list):
                    for ingredient in ingredients:
                        if isinstance(ingredient, dict):
                            name = ingredient.get('name', '').lower()
                            if name:
                                if name in combined_ingredients:
                                    # TODO: Smart quantity combination
                                    combined_ingredients[name]['count'] += 1
                                else:
                                    combined_ingredients[name] = {
                                        'name': ingredient.get('name'),
                                        'quantity': ingredient.get('quantity', ''),
                                        'unit': ingredient.get('unit', ''),
                                        'count': 1  # How many recipes use this
                                    }
                        elif isinstance(ingredient, str):
                            name = ingredient.lower()
                            if name in combined_ingredients:
                                combined_ingredients[name]['count'] += 1
                            else:
                                combined_ingredients[name] = {
                                    'name': ingredient,
                                    'quantity': '',
                                    'unit': '',
                                    'count': 1
                                }
            
            # Convert to list
            ingredient_list = list(combined_ingredients.values())
            
            return {
                'ingredients': ingredient_list,
                'recipe_count': len(meal_plan['recipes']),
                'total_ingredients': len(ingredient_list),
                'meal_plan_name': meal_plan.get('plan_name'),
                'week_start_date': meal_plan.get('week_start_date')
            }
            
        except Exception as e:
            logger.error(f"Error generating grocery list from meal plan {plan_id}: {e}")
            return {'ingredients': [], 'recipe_count': 0}
