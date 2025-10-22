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
                        # Don't filter by user_id - meal plans can include any recipe
                        recipe = self.recipe_repo.find_by_id(recipe_id)
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
        Supports new v2 format: plan_data = [{id, name, recipes: [...]}]
        
        Returns:
            Dict with combined ingredients
        """
        try:
            logger.info(f"🔵 Generating grocery list from meal plan {plan_id}")
            
            # Get meal plan (v2 format)
            meal_plan = self.meal_plan_repo.get_meal_plan_by_id(plan_id, user_id)
            if not meal_plan:
                logger.error(f"❌ Meal plan {plan_id} not found")
                return {'ingredients': [], 'recipe_count': 0}
            
            logger.info(f"✅ Found meal plan: {meal_plan.get('plan_name')}")
            
            # Extract plan_data (new v2 format is array of days)
            plan_data = meal_plan.get('plan_data')
            if not plan_data:
                logger.error(f"❌ No plan_data in meal plan {plan_id}")
                return {'ingredients': [], 'recipe_count': 0}
            
            logger.info(f"📊 plan_data type: {type(plan_data)}")
            
            # Handle v2 format: plan_data is array of days
            if isinstance(plan_data, list):
                logger.info(f"✅ v2 format detected: {len(plan_data)} days")
                
                # Collect all recipes from all days
                all_recipes = []
                for day in plan_data:
                    if isinstance(day, dict) and 'recipes' in day:
                        day_recipes = day.get('recipes', [])
                        logger.info(f"  Day '{day.get('name')}': {len(day_recipes)} recipes")
                        all_recipes.extend(day_recipes)
                
                logger.info(f"✅ Total recipes found: {len(all_recipes)}")
                
                # Combine ingredients from all recipes
                combined_ingredients = {}
                
                for recipe in all_recipes:
                    if not isinstance(recipe, dict):
                        continue
                    
                    # Get ingredients from recipe
                    ingredients = recipe.get('ingredients', [])
                    
                    # Parse if it's a JSON string
                    if isinstance(ingredients, str):
                        import json
                        try:
                            ingredients = json.loads(ingredients)
                        except:
                            logger.warning(f"Failed to parse ingredients for recipe {recipe.get('title')}")
                            continue
                    
                    # Add each ingredient to combined list
                    if isinstance(ingredients, list):
                        for ingredient in ingredients:
                            if isinstance(ingredient, dict):
                                name = ingredient.get('name', '').lower().strip()
                            elif isinstance(ingredient, str):
                                name = ingredient.lower().strip()
                            else:
                                continue
                            
                            if not name:
                                continue
                            
                            # Add or update ingredient
                            if name in combined_ingredients:
                                combined_ingredients[name]['count'] += 1
                            else:
                                if isinstance(ingredient, dict):
                                    combined_ingredients[name] = {
                                        'name': ingredient.get('name', name),
                                        'quantity': ingredient.get('quantity', ''),
                                        'unit': ingredient.get('unit', ''),
                                        'category': ingredient.get('category', 'Other'),
                                        'purchased': False,
                                        'count': 1
                                    }
                                else:
                                    combined_ingredients[name] = {
                                        'name': ingredient,
                                        'quantity': '',
                                        'unit': '',
                                        'category': 'Other',
                                        'purchased': False,
                                        'count': 1
                                    }
                
                # Convert to list
                ingredient_list = list(combined_ingredients.values())
                logger.info(f"✅ Generated {len(ingredient_list)} unique ingredients")
                
                return {
                    'ingredients': ingredient_list,
                    'recipe_count': len(all_recipes),
                    'total_ingredients': len(ingredient_list),
                    'meal_plan_name': meal_plan.get('plan_name'),
                    'week_start_date': meal_plan.get('week_start_date')
                }
            
            # Handle old v1 format (object with day names)
            elif isinstance(plan_data, dict):
                logger.info(f"⚠️ Old v1 format detected - not supported")
                return {'ingredients': [], 'recipe_count': 0}
            
            else:
                logger.error(f"❌ Unknown plan_data format: {type(plan_data)}")
                return {'ingredients': [], 'recipe_count': 0}
            
        except Exception as e:
            logger.error(f"Error generating grocery list from meal plan {plan_id}: {e}")
            import traceback
            traceback.print_exc()
            return {'ingredients': [], 'recipe_count': 0}
