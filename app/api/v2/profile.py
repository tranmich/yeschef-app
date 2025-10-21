"""
Profile API v2 Routes
RESTful endpoints for user profile management
"""

from flask import Blueprint, request, jsonify
import logging

from app.services.profile_service import ProfileService

logger = logging.getLogger(__name__)

# Create blueprint
profile_bp = Blueprint('profile_v2', __name__, url_prefix='/api/v2/profile')

# Initialize service
profile_service = ProfileService()


@profile_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Profile API"""
    return jsonify({
        'success': True,
        'message': 'Profile API v2 is healthy',
        'version': '1.0.0'
    })


# ============================================================================
# PROFILE OPERATIONS
# ============================================================================

@profile_bp.route('/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    """
    Get user profile
    
    Path params:
    - user_id: User ID
    """
    try:
        result = profile_service.get_profile(user_id=user_id)
        
        if result['success']:
            return jsonify(result), 200
        
        return jsonify(result), 404
        
    except Exception as e:
        logger.error(f"Error in get_profile: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@profile_bp.route('/<int:user_id>', methods=['PATCH'])
def update_profile(user_id):
    """
    Update user profile
    
    Path params:
    - user_id: User ID
    
    Request body:
    {
        "name": "New Name",
        "bio": "My bio",
        "location": "City, Country",
        "dietary_preferences": ["vegetarian"],
        "cooking_level": "intermediate"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        result = profile_service.update_profile(
            user_id=user_id,
            updates=data
        )
        
        if result['success']:
            return jsonify(result), 200
        
        return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Error in update_profile: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


# ============================================================================
# AVATAR OPERATIONS
# ============================================================================

@profile_bp.route('/<int:user_id>/avatar', methods=['POST'])
def upload_avatar(user_id):
    """
    Upload user avatar
    
    Path params:
    - user_id: User ID
    
    Request body:
    {
        "avatar_data": "data:image/png;base64,iVBORw0KG...",
        "filename": "avatar.png"
    }
    """
    try:
        data = request.get_json()
        
        avatar_data = data.get('avatar_data')
        filename = data.get('filename')
        
        if not avatar_data:
            return jsonify({
                'success': False,
                'error': 'avatar_data is required'
            }), 400
        
        result = profile_service.upload_avatar(
            user_id=user_id,
            avatar_data=avatar_data,
            filename=filename
        )
        
        if result['success']:
            return jsonify(result), 201
        
        return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Error in upload_avatar: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@profile_bp.route('/<int:user_id>/avatar', methods=['GET'])
def get_avatar(user_id):
    """
    Get user avatar URL
    
    Path params:
    - user_id: User ID
    """
    try:
        result = profile_service.get_avatar(user_id=user_id)
        
        if result['success']:
            return jsonify(result), 200
        
        return jsonify(result), 404
        
    except Exception as e:
        logger.error(f"Error in get_avatar: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@profile_bp.route('/<int:user_id>/avatar', methods=['DELETE'])
def delete_avatar(user_id):
    """
    Delete user avatar
    
    Path params:
    - user_id: User ID
    """
    try:
        result = profile_service.delete_avatar(user_id=user_id)
        
        if result['success']:
            return jsonify(result), 200
        
        return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Error in delete_avatar: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


# ============================================================================
# PROFILE STATS
# ============================================================================

@profile_bp.route('/<int:user_id>/stats', methods=['GET'])
def get_profile_stats(user_id):
    """
    Get profile statistics
    
    Path params:
    - user_id: User ID
    """
    try:
        result = profile_service.get_stats(user_id=user_id)
        
        if result['success']:
            return jsonify(result), 200
        
        return jsonify(result), 404
        
    except Exception as e:
        logger.error(f"Error in get_profile_stats: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


# Register error handlers
@profile_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Resource not found'
    }), 404


@profile_bp.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500
