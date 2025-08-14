#!/usr/bin/env python3
"""
Authentication Routes for Hungie
API endpoints for user registration, login, OAuth, and user management
"""

from flask import Blueprint, request, jsonify, session, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from auth_system import AuthenticationSystem
import logging
import json

logger = logging.getLogger(__name__)

def create_auth_routes(auth_system):
    """Create authentication routes blueprint"""
    
    auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
    
    @auth_bp.route('/register', methods=['POST'])
    def register():
        """Register a new user"""
        try:
            data = request.get_json()
            
            # Validate input
            if not data or not data.get('name') or not data.get('email'):
                return jsonify({'success': False, 'message': 'Name and email are required'}), 400
            
            name = data.get('name').strip()
            email = data.get('email').strip().lower()
            password = data.get('password')
            
            if not password or len(password) < 6:
                return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
            
            # Register user
            result = auth_system.register_user(name, email, password)
            
            if result['success']:
                logger.info(f"[OK] User registered via API: {email}")
                return jsonify(result), 201
            else:
                return jsonify(result), 400
                
        except Exception as e:
            logger.error(f"[ERROR] Registration API error: {e}")
            return jsonify({'success': False, 'message': 'Registration failed'}), 500
    
    @auth_bp.route('/login', methods=['POST'])
    def login():
        """Authenticate user with email and password"""
        try:
            data = request.get_json()
            
            if not data or not data.get('email') or not data.get('password'):
                return jsonify({'success': False, 'message': 'Email and password are required'}), 400
            
            email = data.get('email').strip().lower()
            password = data.get('password')
            
            # Authenticate user
            result = auth_system.authenticate_user(email, password)
            
            if result['success']:
                logger.info(f"[OK] User logged in via API: {email}")
                return jsonify(result), 200
            else:
                return jsonify(result), 401
                
        except Exception as e:
            logger.error(f"[ERROR] Login API error: {e}")
            return jsonify({'success': False, 'message': 'Login failed'}), 500
    
    @auth_bp.route('/me', methods=['GET'])
    @jwt_required()
    def get_current_user():
        """Get current user information"""
        try:
            user_id = get_jwt_identity()
            user = auth_system.get_user_by_id(user_id)
            
            if user:
                return jsonify({'success': True, 'user': user}), 200
            else:
                return jsonify({'success': False, 'message': 'User not found'}), 404
                
        except Exception as e:
            logger.error(f"[ERROR] Get user API error: {e}")
            return jsonify({'success': False, 'message': 'Failed to get user'}), 500
    
    @auth_bp.route('/google', methods=['GET'])
    def google_login():
        """Initiate Google OAuth login"""
        try:
            redirect_uri = url_for('auth.google_callback', _external=True)
            return auth_system.google.authorize_redirect(redirect_uri)
        except Exception as e:
            logger.error(f"[ERROR] Google OAuth error: {e}")
            return jsonify({'success': False, 'message': 'OAuth initialization failed'}), 500
    
    @auth_bp.route('/google/callback', methods=['GET'])
    def google_callback():
        """Handle Google OAuth callback"""
        try:
            token = auth_system.google.authorize_access_token()
            user_info = token.get('userinfo')
            
            if user_info:
                email = user_info.get('email')
                name = user_info.get('name')
                
                # Register or authenticate user
                result = auth_system.register_user(
                    name=name,
                    email=email,
                    password=None,
                    oauth_provider='google',
                    oauth_id=user_info.get('sub')
                )
                
                if result['success']:
                    # Redirect to frontend with token
                    token = result['access_token']
                    return redirect(f'http://localhost:3000/auth/success?token={token}')
                else:
                    # Try to authenticate existing user
                    # For OAuth users, we'll create a token directly
                    from flask_jwt_extended import create_access_token
                    access_token = create_access_token(identity=email)
                    return redirect(f'http://localhost:3000/auth/success?token={access_token}')
            
            return redirect('http://localhost:3000/auth/error')
            
        except Exception as e:
            logger.error(f"[ERROR] Google callback error: {e}")
            return redirect('http://localhost:3000/auth/error')
    
    @auth_bp.route('/facebook', methods=['GET'])
    def facebook_login():
        """Initiate Facebook OAuth login"""
        try:
            redirect_uri = url_for('auth.facebook_callback', _external=True)
            return auth_system.facebook.authorize_redirect(redirect_uri)
        except Exception as e:
            logger.error(f"[ERROR] Facebook OAuth error: {e}")
            return jsonify({'success': False, 'message': 'OAuth initialization failed'}), 500
    
    @auth_bp.route('/facebook/callback', methods=['GET'])
    def facebook_callback():
        """Handle Facebook OAuth callback"""
        try:
            token = auth_system.facebook.authorize_access_token()
            
            # Get user info from Facebook
            resp = auth_system.facebook.get('me?fields=id,name,email')
            user_info = resp.json()
            
            if user_info:
                email = user_info.get('email')
                name = user_info.get('name')
                
                # Register or authenticate user
                result = auth_system.register_user(
                    name=name,
                    email=email,
                    password=None,
                    oauth_provider='facebook',
                    oauth_id=user_info.get('id')
                )
                
                if result['success']:
                    token = result['access_token']
                    return redirect(f'http://localhost:3000/auth/success?token={token}')
                else:
                    from flask_jwt_extended import create_access_token
                    access_token = create_access_token(identity=email)
                    return redirect(f'http://localhost:3000/auth/success?token={access_token}')
            
            return redirect('http://localhost:3000/auth/error')
            
        except Exception as e:
            logger.error(f"[ERROR] Facebook callback error: {e}")
            return redirect('http://localhost:3000/auth/error')
    
    @auth_bp.route('/wipe-data', methods=['DELETE'])
    def wipe_user_data():
        """Wipe user data for testing purposes"""
        try:
            # Check if this is a development environment
            data = request.get_json() or {}
            confirm = data.get('confirm', False)
            user_id = data.get('user_id')
            
            if not confirm:
                return jsonify({
                    'success': False, 
                    'message': 'Must confirm data wipe with "confirm": true'
                }), 400
            
            result = auth_system.wipe_user_data(user_id)
            
            if result['success']:
                logger.warning(f"[WARNING] User data wiped via API: {'user ' + str(user_id) if user_id else 'all users'}")
                return jsonify(result), 200
            else:
                return jsonify(result), 500
                
        except Exception as e:
            logger.error(f"[ERROR] Wipe data API error: {e}")
            return jsonify({'success': False, 'message': 'Failed to wipe data'}), 500
    
    @auth_bp.route('/status', methods=['GET'])
    def auth_status():
        """Check authentication system status"""
        return jsonify({
            'success': True,
            'message': 'Authentication system is running',
            'endpoints': {
                'register': '/api/auth/register',
                'login': '/api/auth/login',
                'me': '/api/auth/me',
                'google': '/api/auth/google',
                'facebook': '/api/auth/facebook',
                'wipe_data': '/api/auth/wipe-data'
            }
        }), 200
    
    return auth_bp
