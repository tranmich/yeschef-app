"""
MealPlan API v2 Routes
RESTful endpoints for meal plan operations
"""

from flask import Blueprint, request, jsonify
import logging

from ...services.meal_plan_service import MealPlanService

logger = logging.getLogger(__name__)

# Create blueprint
meal_plan_bp = Blueprint('meal_plans_v2', __name__, url_prefix='/api/v2/meal-plans')

# Initialize service
meal_plan_service = MealPlanService()


@meal_plan_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'message': 'MealPlan API v2 is healthy'
    })


@meal_plan_bp.route('', methods=['POST'])
def create_meal_plan():
    """
    Create a new meal plan
    
    Request body:
    {
        "user_id": 11,
        "plan_name": "This Week",
        "week_start_date": "2025-10-20",
        "plan_data": {
            "monday": {
                "breakfast": {"recipe_id": 123, "title": "Pancakes"},
                "lunch": {"recipe_id": 456, "title": "Salad"}
            },
            ...
        }
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id', 'plan_name', 'week_start_date', 'plan_data']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Create meal plan
        meal_plan = meal_plan_service.create_meal_plan(
            user_id=data['user_id'],
            plan_name=data['plan_name'],
            week_start_date=data['week_start_date'],
            plan_data=data['plan_data']
        )
        
        if meal_plan:
            return jsonify({
                'success': True,
                'data': meal_plan,
                'message': 'Meal plan created successfully'
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create meal plan'
            }), 500
            
    except Exception as e:
        logger.error(f"Error in create_meal_plan: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@meal_plan_bp.route('/<int:plan_id>', methods=['GET'])
def get_meal_plan(plan_id):
    """
    Get meal plan by ID
    
    Query params:
    - user_id (required): User ID for authorization
    - include_recipes (optional): Include full recipe details
    """
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        include_recipes = request.args.get('include_recipes', 'false').lower() == 'true'
        
        meal_plan = meal_plan_service.get_meal_plan(
            plan_id=plan_id,
            user_id=user_id,
            include_recipes=include_recipes
        )
        
        if meal_plan:
            return jsonify({
                'success': True,
                'data': meal_plan
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Meal plan not found'
            }), 404
            
    except Exception as e:
        logger.error(f"Error in get_meal_plan: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@meal_plan_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_meal_plans(user_id):
    """
    Get all meal plans for a user
    
    Query params:
    - page (optional, default=1)
    - per_page (optional, default=20)
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Validate pagination
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 20
        
        result = meal_plan_service.get_user_meal_plans(
            user_id=user_id,
            page=page,
            per_page=per_page
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Error in get_user_meal_plans: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@meal_plan_bp.route('/user/<int:user_id>/date-range', methods=['GET'])
def get_meal_plans_by_date_range(user_id):
    """
    Get meal plans within a date range
    
    Query params:
    - start_date (required): Start date (YYYY-MM-DD)
    - end_date (required): End date (YYYY-MM-DD)
    """
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({
                'success': False,
                'error': 'start_date and end_date are required'
            }), 400
        
        meal_plans = meal_plan_service.get_meal_plans_by_date_range(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify({
            'success': True,
            'data': {
                'meal_plans': meal_plans,
                'count': len(meal_plans)
            }
        })
        
    except Exception as e:
        logger.error(f"Error in get_meal_plans_by_date_range: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@meal_plan_bp.route('/<int:plan_id>', methods=['PATCH', 'PUT'])
def update_meal_plan(plan_id):
    """
    Update meal plan
    
    Request body (all optional except user_id):
    {
        "user_id": 11,
        "plan_name": "Updated Name",
        "week_start_date": "2025-10-20",
        "plan_data": {...}
    }
    """
    try:
        data = request.get_json()
        
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        meal_plan = meal_plan_service.update_meal_plan(
            plan_id=plan_id,
            user_id=user_id,
            plan_name=data.get('plan_name'),
            week_start_date=data.get('week_start_date'),
            plan_data=data.get('plan_data')
        )
        
        if meal_plan:
            return jsonify({
                'success': True,
                'data': meal_plan,
                'message': 'Meal plan updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update meal plan or not found'
            }), 404
            
    except Exception as e:
        logger.error(f"Error in update_meal_plan: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@meal_plan_bp.route('/<int:plan_id>', methods=['DELETE'])
def delete_meal_plan(plan_id):
    """
    Delete meal plan
    
    Query params:
    - user_id (required): User ID for authorization
    """
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        success = meal_plan_service.delete_meal_plan(plan_id, user_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Meal plan deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to delete meal plan or not found'
            }), 404
            
    except Exception as e:
        logger.error(f"Error in delete_meal_plan: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@meal_plan_bp.route('/<int:plan_id>/grocery-list', methods=['GET', 'POST'])
def generate_grocery_list(plan_id):
    """
    Generate grocery list from meal plan
    🌟 THE POWER FEATURE! 🌟
    
    Combines all ingredients from all recipes in the meal plan
    
    Query params:
    - user_id (required): User ID for authorization
    """
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        grocery_list = meal_plan_service.generate_grocery_list_from_meal_plan(
            plan_id=plan_id,
            user_id=user_id
        )
        
        if grocery_list and grocery_list.get('recipe_count', 0) > 0:
            return jsonify({
                'success': True,
                'data': grocery_list,
                'message': f'Grocery list generated from {grocery_list["recipe_count"]} recipes'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No recipes found in meal plan'
            }), 404
            
    except Exception as e:
        logger.error(f"Error in generate_grocery_list: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


# Register error handlers
@meal_plan_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Resource not found'
    }), 404


@meal_plan_bp.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500
