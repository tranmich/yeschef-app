"""
Community API v2 Routes
RESTful endpoints for community recipe sharing
"""

from flask import Blueprint, request, jsonify
import logging

from app.services.community_service import CommunityService

logger = logging.getLogger(__name__)

# Create blueprint
community_bp = Blueprint('community_v2', __name__, url_prefix='/api/v2/community')

# Initialize service
community_service = CommunityService()


@community_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'message': 'Community API v2 is healthy'
    })


# ============================================================================
# COMMUNITY RECIPES BROWSING
# ============================================================================

@community_bp.route('/recipes', methods=['GET'])
def get_community_recipes():
    """
    Get all community recipes
    
    Query params:
    - user_id (required): User ID for liked status
    - limit (optional): Results limit (default: 50)
    - offset (optional): Pagination offset (default: 0)
    """
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        result = community_service.get_community_recipes(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        if result['success']:
            return jsonify(result), 200
        
        return jsonify(result), 404
        
    except Exception as e:
        logger.error(f"Error in get_community_recipes: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@community_bp.route('/recipes/<int:recipe_id>', methods=['GET'])
def get_community_recipe(recipe_id):
    """
    Get a specific community recipe with full details
    
    Query params:
    - user_id (required): User ID for liked status
    """
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        result = community_service.get_community_recipe(
            recipe_id=recipe_id,
            user_id=user_id
        )
        
        if result['success']:
            return jsonify(result), 200
        
        return jsonify(result), 404
        
    except Exception as e:
        logger.error(f"Error in get_community_recipe: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


# ============================================================================
# SHARING OPERATIONS
# ============================================================================

@community_bp.route('/recipes', methods=['POST'])
def share_recipe():
    """
    Share a recipe to the community
    
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
        
        result = community_service.share_recipe(
            recipe_id=recipe_id,
            user_id=user_id
        )
        
        if result['success']:
            return jsonify(result), 201
        
        return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Error in share_recipe: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@community_bp.route('/recipes/<int:recipe_id>', methods=['DELETE'])
def unshare_recipe(recipe_id):
    """
    Remove a recipe from the community
    
    Query params:
    - user_id (required): User ID (must be owner)
    """
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        result = community_service.unshare_recipe(
            recipe_id=recipe_id,
            user_id=user_id
        )
        
        if result['success']:
            return jsonify(result), 200
        
        return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Error in unshare_recipe: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@community_bp.route('/my-shares', methods=['GET'])
def get_my_shares():
    """
    Get all recipes shared by the user
    
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
        
        result = community_service.get_my_shares(user_id=user_id)
        
        if result['success']:
            return jsonify(result), 200
        
        return jsonify(result), 404
        
    except Exception as e:
        logger.error(f"Error in get_my_shares: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@community_bp.route('/check/<int:recipe_id>', methods=['GET'])
def check_shared(recipe_id):
    """
    Check if a recipe is shared to community
    
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
        
        result = community_service.check_shared(
            recipe_id=recipe_id,
            user_id=user_id
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in check_shared: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


# ============================================================================
# RECIPE CLAIMING
# ============================================================================

@community_bp.route('/recipes/<int:recipe_id>/claim', methods=['POST'])
def claim_recipe(recipe_id):
    """
    Claim a community recipe (copy to own collection)
    
    Request body:
    {
        "user_id": 10
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
        
        result = community_service.claim_recipe(
            recipe_id=recipe_id,
            user_id=user_id
        )
        
        if result['success']:
            return jsonify(result), 201
        
        return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Error in claim_recipe: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


# ============================================================================
# LIKES
# ============================================================================

@community_bp.route('/recipes/<int:recipe_id>/like', methods=['POST'])
def like_recipe(recipe_id):
    """
    Like a community recipe
    
    Request body:
    {
        "user_id": 10
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
        
        result = community_service.like_recipe(
            recipe_id=recipe_id,
            user_id=user_id
        )
        
        if result['success']:
            return jsonify(result), 201
        
        return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Error in like_recipe: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@community_bp.route('/recipes/<int:recipe_id>/like', methods=['DELETE'])
def unlike_recipe(recipe_id):
    """
    Unlike a community recipe
    
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
        
        result = community_service.unlike_recipe(
            recipe_id=recipe_id,
            user_id=user_id
        )
        
        if result['success']:
            return jsonify(result), 200
        
        return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Error in unlike_recipe: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


# Register error handlers
@community_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Resource not found'
    }), 404


@community_bp.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500
