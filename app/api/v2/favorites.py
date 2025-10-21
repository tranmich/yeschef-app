"""
Favorites API v2 Routes
RESTful endpoints for recipe favorites/bookmarks
"""

from flask import Blueprint, request, jsonify
import logging

from app.services.favorites_service import FavoritesService

logger = logging.getLogger(__name__)

# Create blueprint
favorites_bp = Blueprint('favorites_v2', __name__, url_prefix='/api/v2/favorites')

# Initialize service
favorites_service = FavoritesService()


@favorites_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Favorites API"""
    return jsonify({
        'success': True,
        'message': 'Favorites API v2 is healthy',
        'version': '1.0.0'
    })


# ============================================================================
# FAVORITES OPERATIONS
# ============================================================================

@favorites_bp.route('', methods=['POST'])
def add_favorite():
    """
    Add a recipe to favorites
    
    Request body:
    {
        "recipe_id": 123,
        "user_id": 10
    }
    """
    try:
        data = request.get_json()
        
        recipe_id = data.get('recipe_id')
        user_id = data.get('user_id')
        
        if not recipe_id or not user_id:
            return jsonify({
                'success': False,
                'error': 'recipe_id and user_id are required'
            }), 400
        
        result = favorites_service.add_to_favorites(
            recipe_id=recipe_id,
            user_id=user_id
        )
        
        if result['success']:
            return jsonify(result), 201
        
        return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Error in add_favorite: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@favorites_bp.route('/<int:recipe_id>', methods=['DELETE'])
def remove_favorite(recipe_id):
    """
    Remove a recipe from favorites
    
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
        
        result = favorites_service.remove_from_favorites(
            recipe_id=recipe_id,
            user_id=user_id
        )
        
        if result['success']:
            return jsonify(result), 200
        
        return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Error in remove_favorite: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@favorites_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_favorites(user_id):
    """
    Get all favorite recipes for a user
    
    Query params:
    - limit (optional): Results limit (default: 100)
    - offset (optional): Pagination offset (default: 0)
    """
    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        result = favorites_service.get_favorites(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        if result['success']:
            return jsonify(result), 200
        
        return jsonify(result), 404
        
    except Exception as e:
        logger.error(f"Error in get_user_favorites: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@favorites_bp.route('/check', methods=['GET'])
def check_favorite():
    """
    Check if a recipe is in user's favorites
    
    Query params:
    - recipe_id (required): Recipe ID
    - user_id (required): User ID
    """
    try:
        recipe_id = request.args.get('recipe_id', type=int)
        user_id = request.args.get('user_id', type=int)
        
        if not recipe_id or not user_id:
            return jsonify({
                'success': False,
                'error': 'recipe_id and user_id are required'
            }), 400
        
        result = favorites_service.check_favorite(
            recipe_id=recipe_id,
            user_id=user_id
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in check_favorite: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@favorites_bp.route('/summary', methods=['GET'])
def get_favorites_summary():
    """
    Get favorites summary/stats for a user
    
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
        
        result = favorites_service.get_summary(user_id=user_id)
        
        if result['success']:
            return jsonify(result), 200
        
        return jsonify(result), 404
        
    except Exception as e:
        logger.error(f"Error in get_favorites_summary: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


# Register error handlers
@favorites_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Resource not found'
    }), 404


@favorites_bp.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500
