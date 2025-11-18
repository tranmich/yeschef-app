"""
Authentication API Routes (v2)
RESTful endpoints for authentication operations
Uses AuthService for business logic
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import logging
import jwt
import os
import hashlib

from app.services.auth_service import get_auth_service

logger = logging.getLogger(__name__)

# Create blueprint
auth_bp = Blueprint('auth_v2', __name__, url_prefix='/api/v2/auth')


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


# Helper function to get JWT secret
def get_jwt_secret():
    """Get JWT secret key (same logic as auth_system.py)"""
    jwt_secret = os.getenv('JWT_SECRET_KEY')
    if not jwt_secret:
        database_url = os.getenv('DATABASE_URL', '')
        if database_url:
            jwt_secret = hashlib.sha256(database_url.encode()).hexdigest()
        else:
            jwt_secret = 'dev-secret-key-for-local-testing-only'
    return jwt_secret


# Helper decorator for JWT authentication
def jwt_required_v2(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'error': 'Missing or invalid Authorization header',
                'code': 'UNAUTHORIZED'
            }), 401
        
        token = auth_header.split(' ')[1]
        
        try:
            # Decode JWT token
            jwt_secret = get_jwt_secret()
            payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
            user_id = payload.get('sub')
            
            if not user_id:
                return jsonify({
                    'success': False,
                    'error': 'Invalid token',
                    'code': 'INVALID_TOKEN'
                }), 401
            
            # Add user_id to request context
            request.user_id = user_id
            
            return f(*args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'error': 'Token has expired',
                'code': 'TOKEN_EXPIRED'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'error': 'Invalid token',
                'code': 'INVALID_TOKEN'
            }), 401
    
    return decorated_function


# POST /api/v2/auth/register
@auth_bp.route('/register', methods=['POST'])
@handle_errors
def register():
    """
    Register a new user
    
    Example:
        POST /api/v2/auth/register
        {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "securepassword123"
        }
        
    Response:
        {
            "success": true,
            "data": {
                "user": {
                    "id": 123,
                    "name": "John Doe",
                    "email": "john@example.com"
                },
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            },
            "message": "User registered successfully"
        }
    """
    auth_service = get_auth_service()
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'error': 'No data provided',
            'code': 'VALIDATION_ERROR'
        }), 400
    
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    result = auth_service.register_user(name, email, password)
    
    if result['success']:
        return jsonify(result), 201  # 201 Created
    else:
        status_code = 400
        if result.get('code') == 'EMAIL_EXISTS':
            status_code = 409  # 409 Conflict
        return jsonify(result), status_code


# POST /api/v2/auth/login
@auth_bp.route('/login', methods=['POST'])
@handle_errors
def login():
    """
    Authenticate user with email and password
    
    Example:
        POST /api/v2/auth/login
        {
            "email": "john@example.com",
            "password": "securepassword123"
        }
        
    Response:
        {
            "success": true,
            "data": {
                "user": {
                    "id": 123,
                    "name": "John Doe",
                    "email": "john@example.com"
                },
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            },
            "message": "Login successful"
        }
    """
    auth_service = get_auth_service()
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'error': 'No data provided',
            'code': 'VALIDATION_ERROR'
        }), 400
    
    email = data.get('email')
    password = data.get('password')
    
    result = auth_service.login_user(email, password)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 401  # 401 Unauthorized


# POST /api/v2/auth/logout
@auth_bp.route('/logout', methods=['POST'])
@handle_errors
def logout():
    """
    Logout user (client-side token removal)
    
    Note: JWT tokens are stateless, so logout is handled client-side
    by removing the token. This endpoint logs the event for monitoring.
    
    Example:
        POST /api/v2/auth/logout
        Authorization: Bearer <token>
        
    Response:
        {
            "success": true,
            "message": "Logged out successfully"
        }
    """
    # Try to get user info for logging
    try:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            jwt_secret = get_jwt_secret()
            payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
            user_id = payload.get('sub')
            logger.info(f"✅ User logged out: ID {user_id}")
    except:
        # Don't fail logout if token is invalid
        logger.info("✅ Logout called (token invalid or missing)")
    
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    }), 200


# GET /api/v2/auth/me
@auth_bp.route('/me', methods=['GET'])
@jwt_required_v2
@handle_errors
def get_me():
    """
    Get current user information
    
    Example:
        GET /api/v2/auth/me
        Authorization: Bearer <token>
        
    Response:
        {
            "success": true,
            "data": {
                "user": {
                    "id": 123,
                    "name": "John Doe",
                    "email": "john@example.com",
                    "avatar_emoji": "👨‍🍳",
                    "created_at": "2025-01-15 10:30:00"
                }
            },
            "message": "User retrieved successfully"
        }
    """
    auth_service = get_auth_service()
    user_id = request.user_id  # Set by jwt_required_v2 decorator
    
    result = auth_service.get_current_user(user_id)
    
    if result['success']:
        return jsonify(result), 200
    else:
        status_code = 404 if result.get('code') == 'NOT_FOUND' else 400
        return jsonify(result), status_code


# POST /api/v2/auth/forgot-password
@auth_bp.route('/forgot-password', methods=['POST'])
@handle_errors
def forgot_password():
    """
    Request password reset email
    
    Example:
        POST /api/v2/auth/forgot-password
        {
            "email": "john@example.com"
        }
        
    Response:
        {
            "success": true,
            "message": "If an account exists with this email, a password reset link has been sent"
        }
    """
    auth_service = get_auth_service()
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'error': 'No data provided',
            'code': 'VALIDATION_ERROR'
        }), 400
    
    email = data.get('email')
    
    result = auth_service.request_password_reset(email)
    
    # Always return 200 for security (don't reveal if email exists)
    return jsonify(result), 200


# POST /api/v2/auth/reset-password
@auth_bp.route('/reset-password', methods=['POST'])
@handle_errors
def reset_password():
    """
    Reset password using reset token
    
    Example:
        POST /api/v2/auth/reset-password
        {
            "token": "reset_token_here",
            "password": "newpassword123"
        }
        
    Response:
        {
            "success": true,
            "message": "Password reset successfully"
        }
    """
    auth_service = get_auth_service()
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'error': 'No data provided',
            'code': 'VALIDATION_ERROR'
        }), 400
    
    token = data.get('token')
    password = data.get('password')
    
    result = auth_service.reset_password(token, password)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 400


# DELETE /api/v2/auth/account
@auth_bp.route('/account', methods=['DELETE'])
@jwt_required_v2
@handle_errors
def delete_account():
    """
    Delete user account (requires password confirmation)
    
    Example:
        DELETE /api/v2/auth/account
        Authorization: Bearer <token>
        {
            "password": "currentpassword"
        }
        
    Response:
        {
            "success": true,
            "message": "Account deleted successfully"
        }
    """
    auth_service = get_auth_service()
    user_id = request.user_id  # Set by jwt_required_v2 decorator
    data = request.get_json()
    
    if not data or not data.get('password'):
        return jsonify({
            'success': False,
            'error': 'Password is required for account deletion',
            'code': 'VALIDATION_ERROR'
        }), 400
    
    password = data.get('password')
    
    result = auth_service.delete_account(user_id, password)
    
    if result['success']:
        return jsonify(result), 200
    else:
        status_code = 401 if result.get('code') == 'INVALID_CREDENTIALS' else 400
        return jsonify(result), status_code


# GET /api/v2/auth/status
@auth_bp.route('/status', methods=['GET'])
@handle_errors
def auth_status():
    """
    Check authentication system status
    
    Example:
        GET /api/v2/auth/status
        
    Response:
        {
            "success": true,
            "data": {
                "status": "operational",
                "version": "2.0"
            }
        }
    """
    return jsonify({
        'success': True,
        'data': {
            'status': 'operational',
            'version': '2.0',
            'endpoints': [
                'POST /api/v2/auth/register',
                'POST /api/v2/auth/login',
                'POST /api/v2/auth/logout',
                'GET /api/v2/auth/me',
                'POST /api/v2/auth/forgot-password',
                'POST /api/v2/auth/reset-password',
                'DELETE /api/v2/auth/account'
            ]
        }
    }), 200


# OAuth endpoints (future implementation)

# GET /api/v2/auth/google
@auth_bp.route('/google', methods=['GET'])
@handle_errors
def google_auth():
    """
    Initiate Google OAuth flow
    
    Note: This is a placeholder for future OAuth integration
    """
    return jsonify({
        'success': False,
        'error': 'Google OAuth integration coming soon',
        'code': 'NOT_IMPLEMENTED'
    }), 501  # 501 Not Implemented


# GET /api/v2/auth/google/callback
@auth_bp.route('/google/callback', methods=['GET'])
@handle_errors
def google_auth_callback():
    """
    Handle Google OAuth callback
    
    Note: This is a placeholder for future OAuth integration
    """
    return jsonify({
        'success': False,
        'error': 'Google OAuth integration coming soon',
        'code': 'NOT_IMPLEMENTED'
    }), 501  # 501 Not Implemented
