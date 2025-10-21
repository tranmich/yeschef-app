"""
Pantry API v2 Routes
RESTful endpoints for pantry inventory management
"""

from flask import Blueprint, request, jsonify
import logging

from app.services.pantry_service import PantryService

logger = logging.getLogger(__name__)

# Create blueprint
pantry_bp = Blueprint('pantry_v2', __name__, url_prefix='/api/v2/pantry')

# Initialize service
pantry_service = PantryService()


@pantry_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Pantry API"""
    return jsonify({
        'success': True,
        'message': 'Pantry API v2 is healthy',
        'version': '1.0.0'
    })


# ============================================================================
# PANTRY ITEMS CRUD
# ============================================================================

@pantry_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_pantry(user_id):
    """
    Get all pantry items for a user
    
    Query params:
    - limit (optional): Results limit (default: 100)
    - offset (optional): Pagination offset (default: 0)
    """
    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        result = pantry_service.get_pantry(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        if result['success']:
            return jsonify(result), 200
        
        return jsonify(result), 404
        
    except Exception as e:
        logger.error(f"Error in get_user_pantry: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@pantry_bp.route('', methods=['POST'])
def add_pantry_item():
    """
    Add item to pantry
    
    Request body:
    {
        "user_id": 10,
        "name": "Tomatoes",
        "quantity": 5,
        "unit": "count",
        "category": "vegetables",
        "expiry_date": "2025-10-30",
        "notes": "From farmer's market"
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
        
        result = pantry_service.add_item(
            user_id=user_id,
            item_data=data
        )
        
        if result['success']:
            return jsonify(result), 201
        
        return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Error in add_pantry_item: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@pantry_bp.route('/<int:item_id>', methods=['GET'])
def get_pantry_item(item_id):
    """
    Get single pantry item
    
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
        
        result = pantry_service.get_item(
            item_id=item_id,
            user_id=user_id
        )
        
        if result['success']:
            return jsonify(result), 200
        
        return jsonify(result), 404
        
    except Exception as e:
        logger.error(f"Error in get_pantry_item: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@pantry_bp.route('/<int:item_id>', methods=['PATCH'])
def update_pantry_item(item_id):
    """
    Update pantry item
    
    Query params:
    - user_id (required): User ID
    
    Request body:
    {
        "quantity": 3,
        "notes": "Updated note"
    }
    """
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        result = pantry_service.update_item(
            item_id=item_id,
            user_id=user_id,
            updates=data
        )
        
        if result['success']:
            return jsonify(result), 200
        
        return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Error in update_pantry_item: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@pantry_bp.route('/<int:item_id>', methods=['DELETE'])
def delete_pantry_item(item_id):
    """
    Delete pantry item
    
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
        
        result = pantry_service.delete_item(
            item_id=item_id,
            user_id=user_id
        )
        
        if result['success']:
            return jsonify(result), 200
        
        return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Error in delete_pantry_item: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


# ============================================================================
# PANTRY STATUS & SEARCH
# ============================================================================

@pantry_bp.route('/stats', methods=['GET'])
def get_pantry_stats():
    """
    Get pantry statistics
    
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
        
        result = pantry_service.get_stats(user_id=user_id)
        
        if result['success']:
            return jsonify(result), 200
        
        return jsonify(result), 404
        
    except Exception as e:
        logger.error(f"Error in get_pantry_stats: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@pantry_bp.route('/search', methods=['GET'])
def search_pantry():
    """
    Search pantry items
    
    Query params:
    - user_id (required): User ID
    - q (required): Search term
    - limit (optional): Results limit (default: 50)
    """
    try:
        user_id = request.args.get('user_id', type=int)
        search_term = request.args.get('q', '')
        limit = request.args.get('limit', 50, type=int)
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        result = pantry_service.search(
            user_id=user_id,
            search_term=search_term,
            limit=limit
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in search_pantry: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@pantry_bp.route('/category/<category>', methods=['GET'])
def get_by_category(category):
    """
    Get pantry items by category
    
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
        
        result = pantry_service.get_by_category(
            user_id=user_id,
            category=category
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in get_by_category: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@pantry_bp.route('/clear', methods=['DELETE'])
def clear_pantry():
    """
    Clear all pantry items
    
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
        
        result = pantry_service.clear_pantry(user_id=user_id)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in clear_pantry: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


# Register error handlers
@pantry_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Resource not found'
    }), 404


@pantry_bp.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500
