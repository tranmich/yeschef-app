"""
User API Routes (v2)
RESTful endpoints for user operations
Uses UserService for business logic
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import logging

from app.services.user_service import get_user_service

logger = logging.getLogger(__name__)

# Create blueprint
user_bp = Blueprint('user_v2', __name__, url_prefix='/api/v2/users')


# Helper decorator for error handling
def handle_errors(f):
    """Decorator to handle errors consistently"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Internal server error'
            }), 500
    return decorated_function


# GET /api/v2/users/<user_id>
@user_bp.route('/<int:user_id>', methods=['GET'])
@handle_errors
def get_user(user_id):
    """
    Get user by ID
    
    Example:
        GET /api/v2/users/11
        
    Response:
        {
            "success": true,
            "data": {
                "id": 11,
                "name": "YesChef",
                "email": "test@example.com",
                "avatar_emoji": "👨‍🍳"
            }
        }
    """
    user_service = get_user_service()
    result = user_service.get_user_by_id(user_id)
    
    if result['success']:
        return jsonify(result), 200
    else:
        status_code = 404 if result.get('error_code') == 'NOT_FOUND' else 400
        return jsonify(result), status_code


# GET /api/v2/users/email/<email>
@user_bp.route('/email/<email>', methods=['GET'])
@handle_errors
def get_user_by_email(email):
    """
    Get user by email
    
    Example:
        GET /api/v2/users/email/test@example.com
        
    Response:
        {
            "success": true,
            "data": {...}
        }
    """
    user_service = get_user_service()
    result = user_service.get_user_by_email(email)
    
    if result['success']:
        return jsonify(result), 200
    else:
        status_code = 404 if result.get('error_code') == 'NOT_FOUND' else 400
        return jsonify(result), status_code


# POST /api/v2/users
@user_bp.route('', methods=['POST'])
@handle_errors
def create_user():
    """
    Create new user
    
    Example:
        POST /api/v2/users
        {
            "email": "newuser@example.com",
            "name": "New User",
            "password_hash": "hashed_password"
        }
        
    Response:
        {
            "success": true,
            "data": {...},
            "message": "User created successfully"
        }
    """
    user_service = get_user_service()
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'error': 'No data provided'
        }), 400
    
    result = user_service.create_user(data)
    
    if result['success']:
        return jsonify(result), 201  # 201 Created
    else:
        status_code = 400
        if result.get('error_code') == 'EMAIL_EXISTS':
            status_code = 409  # 409 Conflict
        return jsonify(result), status_code


# PATCH /api/v2/users/<user_id>
@user_bp.route('/<int:user_id>', methods=['PATCH'])
@handle_errors
def update_user(user_id):
    """
    Update user
    
    Example:
        PATCH /api/v2/users/11
        {
            "name": "Updated Name",
            "avatar_emoji": "🎨"
        }
        
    Response:
        {
            "success": true,
            "data": {...},
            "message": "User updated successfully"
        }
    """
    user_service = get_user_service()
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'error': 'No data provided'
        }), 400
    
    result = user_service.update_user(user_id, data)
    
    if result['success']:
        return jsonify(result), 200
    else:
        status_code = 404 if result.get('error_code') == 'NOT_FOUND' else 400
        return jsonify(result), status_code


# PATCH /api/v2/users/<user_id>/profile
@user_bp.route('/<int:user_id>/profile', methods=['PATCH'])
@handle_errors
def update_profile(user_id):
    """
    Update user profile (avatar)
    
    Example:
        PATCH /api/v2/users/11/profile
        {
            "avatar_emoji": "👨‍🍳",
            "avatar_background_color": "#FF5733"
        }
        
    Response:
        {
            "success": true,
            "data": {...},
            "message": "Profile updated successfully"
        }
    """
    user_service = get_user_service()
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'error': 'No data provided'
        }), 400
    
    result = user_service.update_profile(
        user_id,
        avatar_emoji=data.get('avatar_emoji'),
        avatar_background_color=data.get('avatar_background_color')
    )
    
    if result['success']:
        return jsonify(result), 200
    else:
        status_code = 404 if result.get('error_code') == 'NOT_FOUND' else 400
        return jsonify(result), status_code


# GET /api/v2/users/search?q=<search_term>
@user_bp.route('/search', methods=['GET'])
@handle_errors
def search_users():
    """
    Search users by name or email
    
    Example:
        GET /api/v2/users/search?q=john&limit=10
        
    Response:
        {
            "success": true,
            "data": {
                "users": [...],
                "count": 5
            }
        }
    """
    user_service = get_user_service()
    
    search_term = request.args.get('q', '')
    limit = request.args.get('limit', 50, type=int)
    
    if not search_term:
        return jsonify({
            'success': False,
            'error': 'Search term required (q parameter)'
        }), 400
    
    result = user_service.search_users(search_term, limit=limit)
    
    return jsonify(result), 200


# GET /api/v2/users/<user_id>/stats
@user_bp.route('/<int:user_id>/stats', methods=['GET'])
@handle_errors
def get_user_stats(user_id):
    """
    Get user statistics
    
    Example:
        GET /api/v2/users/11/stats
        
    Response:
        {
            "success": true,
            "data": {
                "user_id": 11,
                "name": "YesChef",
                "email": "test@example.com",
                "recipe_count": 37,
                "member_since": "2025-08-14 18:48:27"
            }
        }
    """
    user_service = get_user_service()
    result = user_service.get_user_stats(user_id)
    
    if result['success']:
        return jsonify(result), 200
    else:
        status_code = 404 if result.get('error_code') == 'NOT_FOUND' else 400
        return jsonify(result), status_code


@user_bp.route('/batch', methods=['POST'])
@handle_errors
def get_users_batch():
    """
    Get multiple users by IDs (for Liveblocks user resolution)
    
    Request body:
    {
        "user_ids": [1, 2, 3]
    }
    
    Returns:
    {
        "success": true,
        "users": [...]
    }
    """
    data = request.get_json()
    user_ids = data.get('user_ids', [])
    
    if not user_ids:
        return jsonify({
            'success': False,
            'error': 'user_ids required'
        }), 400
    
    user_service = get_user_service()
    users = []
    
    for user_id in user_ids:
        try:
            uid = int(user_id) if isinstance(user_id, str) else user_id
            result = user_service.get_user(uid)
            
            if result['success']:
                user = result['data']
                users.append({
                    'id': user['id'],
                    'username': user.get('username', f'User {user["id"]}'),
                    'email': user.get('email', ''),
                    'avatar_url': user.get('avatar_url'),
                    'avatar_emoji': user.get('avatar_emoji'),
                    'avatar_background_color': user.get('avatar_background_color'),
                })
            else:
                # User not found - add placeholder
                users.append({
                    'id': uid,
                    'username': f'User {uid}',
                    'email': '',
                    'avatar_url': None,
                })
        except Exception as e:
            logger.error(f"Error fetching user {user_id}: {str(e)}")
            users.append({
                'id': user_id,
                'username': f'User {user_id}',
                'email': '',
                'avatar_url': None,
            })
    
    logger.info(f"✅ Fetched batch of {len(users)} users")
    
    return jsonify({
        'success': True,
        'users': users
    }), 200
