"""
GroceryList API v2 Routes
RESTful endpoints for grocery list operations
"""

from flask import Blueprint, request, jsonify
import logging

from ...services.grocery_list_service import GroceryListService

logger = logging.getLogger(__name__)

# Create blueprint
grocery_list_bp = Blueprint('grocery_lists_v2', __name__, url_prefix='/api/v2/grocery-lists')

# Initialize service
grocery_list_service = GroceryListService()


@grocery_list_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'message': 'GroceryList API v2 is healthy'
    })


@grocery_list_bp.route('', methods=['POST'])
def create_grocery_list():
    """
    Create a new grocery list
    
    Request body:
    {
        "user_id": 11,
        "name": "Weekly Shopping",
        "items": [
            {"name": "Milk", "quantity": "1", "unit": "gallon", "category": "Dairy"},
            {"name": "Bread", "quantity": "2", "unit": "loaves", "category": "Bakery"}
        ]
    }
    """
    try:
        data = request.get_json()
        
        logger.info(f"📝 Creating grocery list: {data.get('name')} for user {data.get('user_id')}")
        
        # Validate required fields
        required_fields = ['user_id', 'name', 'items']
        for field in required_fields:
            if field not in data:
                logger.warning(f"Missing required field: {field}")
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Create grocery list
        grocery_list = grocery_list_service.create_grocery_list(
            user_id=data['user_id'],
            name=data['name'],
            items=data['items'],
            meal_plan_id=data.get('meal_plan_id')
        )
        
        if grocery_list:
            logger.info(f"✅ Created grocery list {grocery_list['id']}: {grocery_list['name']}")
            return jsonify({
                'success': True,
                'data': grocery_list,
                'message': 'Grocery list created successfully'
            }), 201
        else:
            logger.error("Failed to create grocery list")
            return jsonify({
                'success': False,
                'error': 'Failed to create grocery list'
            }), 500
            
    except Exception as e:
        logger.error(f"Error in create_grocery_list: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@grocery_list_bp.route('/from-meal-plan/<int:meal_plan_id>', methods=['POST'])
def create_from_meal_plan(meal_plan_id):
    """
    Create grocery list from meal plan
    🌟 THE POWER FEATURE! 🌟
    
    Query params:
    - user_id (required): User ID
    
    Request body (optional):
    {
        "name": "Custom List Name"
    }
    """
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        # Get optional request body (don't fail if empty)
        try:
            data = request.get_json(silent=True) or {}
        except:
            data = {}
        
        list_name = data.get('name')
        
        grocery_list = grocery_list_service.create_from_meal_plan(
            meal_plan_id=meal_plan_id,
            user_id=user_id,
            list_name=list_name
        )
        
        if grocery_list:
            return jsonify({
                'success': True,
                'data': grocery_list,
                'message': f'Grocery list created from meal plan with {grocery_list["stats"]["total_items"]} items'
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create grocery list from meal plan'
            }), 404
            
    except Exception as e:
        logger.error(f"Error in create_from_meal_plan: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@grocery_list_bp.route('/<int:list_id>', methods=['GET'])
def get_grocery_list(list_id):
    """
    Get grocery list by ID
    
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
        
        grocery_list = grocery_list_service.get_grocery_list(list_id, user_id)
        
        if grocery_list:
            return jsonify({
                'success': True,
                'data': grocery_list
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Grocery list not found'
            }), 404
            
    except Exception as e:
        logger.error(f"Error in get_grocery_list: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@grocery_list_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_grocery_lists(user_id):
    """
    Get all grocery lists for a user
    
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
        
        result = grocery_list_service.get_user_grocery_lists(
            user_id=user_id,
            page=page,
            per_page=per_page
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Error in get_user_grocery_lists: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@grocery_list_bp.route('/<int:list_id>', methods=['PATCH', 'PUT'])
def update_grocery_list(list_id):
    """
    Update grocery list
    
    Request body (all optional except user_id):
    {
        "user_id": 11,
        "name": "Updated Name",
        "items": [...]
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
        
        grocery_list = grocery_list_service.update_grocery_list(
            list_id=list_id,
            user_id=user_id,
            name=data.get('name'),
            items=data.get('items')
        )
        
        if grocery_list:
            return jsonify({
                'success': True,
                'data': grocery_list,
                'message': 'Grocery list updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update grocery list or not found'
            }), 404
            
    except Exception as e:
        logger.error(f"Error in update_grocery_list: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@grocery_list_bp.route('/<int:list_id>/items', methods=['POST'])
def add_item(list_id):
    """
    Add item to grocery list
    
    Request body:
    {
        "user_id": 11,
        "item": {
            "name": "Apples",
            "quantity": "6",
            "unit": "",
            "category": "Produce"
        }
    }
    """
    try:
        data = request.get_json()
        
        user_id = data.get('user_id')
        item = data.get('item')
        
        if not user_id or not item:
            return jsonify({
                'success': False,
                'error': 'user_id and item are required'
            }), 400
        
        grocery_list = grocery_list_service.add_item(list_id, user_id, item)
        
        if grocery_list:
            return jsonify({
                'success': True,
                'data': grocery_list,
                'message': 'Item added successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to add item'
            }), 404
            
    except Exception as e:
        logger.error(f"Error in add_item: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@grocery_list_bp.route('/<int:list_id>/items/<int:item_index>', methods=['DELETE'])
def remove_item(list_id, item_index):
    """
    Remove item from grocery list
    
    Query params:
    - user_id (required): User ID
    """
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        grocery_list = grocery_list_service.remove_item(list_id, user_id, item_index)
        
        if grocery_list:
            return jsonify({
                'success': True,
                'data': grocery_list,
                'message': 'Item removed successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to remove item or not found'
            }), 404
            
    except Exception as e:
        logger.error(f"Error in remove_item: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@grocery_list_bp.route('/<int:list_id>/items/<int:item_index>/purchase', methods=['POST', 'PATCH'])
def mark_item_purchased(list_id, item_index):
    """
    Mark item as purchased/unpurchased
    
    Request body:
    {
        "user_id": 11,
        "purchased": true
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
        
        purchased = data.get('purchased', True)
        
        grocery_list = grocery_list_service.mark_item_purchased(
            list_id=list_id,
            user_id=user_id,
            item_index=item_index,
            purchased=purchased
        )
        
        if grocery_list:
            return jsonify({
                'success': True,
                'data': grocery_list,
                'message': f'Item marked as {"purchased" if purchased else "not purchased"}'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update item'
            }), 404
            
    except Exception as e:
        logger.error(f"Error in mark_item_purchased: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@grocery_list_bp.route('/<int:list_id>/clear-purchased', methods=['POST'])
def clear_purchased_items(list_id):
    """
    Remove all purchased items from list
    
    Query params:
    - user_id (required): User ID
    """
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        grocery_list = grocery_list_service.clear_purchased_items(list_id, user_id)
        
        if grocery_list:
            return jsonify({
                'success': True,
                'data': grocery_list,
                'message': 'Purchased items cleared successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to clear purchased items'
            }), 404
            
    except Exception as e:
        logger.error(f"Error in clear_purchased_items: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@grocery_list_bp.route('/<int:list_id>', methods=['DELETE'])
def delete_grocery_list(list_id):
    """
    Delete grocery list
    
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
        
        success = grocery_list_service.delete_grocery_list(list_id, user_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Grocery list deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to delete grocery list or not found'
            }), 404
            
    except Exception as e:
        logger.error(f"Error in delete_grocery_list: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


# Register error handlers
@grocery_list_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Resource not found'
    }), 404


@grocery_list_bp.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500
