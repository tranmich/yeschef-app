"""
Pusher Authentication API
Handles Pusher channel authentication for presence channels
"""

import os
import logging
import hashlib
import jwt
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from app.services.pusher_service import get_pusher_service
from functools import wraps

logger = logging.getLogger(__name__)

pusher_auth_bp = Blueprint('pusher_auth', __name__, url_prefix='/api/v2/pusher')


# Get JWT secret (same as whiteboards.py)
def get_jwt_secret():
    jwt_secret = os.getenv('JWT_SECRET_KEY')
    if not jwt_secret:
        database_url = os.getenv('DATABASE_URL', '')
        if database_url:
            jwt_secret = hashlib.sha256(database_url.encode()).hexdigest()
        else:
            jwt_secret = 'dev-secret-key-for-local-testing-only'
    return jwt_secret


# Custom JWT decorator that works with your dual JWT system
def jwt_required_v2(f):
    """Custom JWT authentication decorator for API v2"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'error': 'Missing or invalid Authorization header'
            }), 401
        
        token = auth_header.split(' ')[1]
        
        try:
            jwt_secret = get_jwt_secret()
            payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
            user_id = payload.get('sub')
            
            if not user_id:
                return jsonify({
                    'success': False,
                    'error': 'Invalid token payload'
                }), 401
            
            # Store user_id in request for the route
            request.user_id = int(user_id)
            
            return f(*args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'error': 'Token has expired'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'error': 'Invalid token'
            }), 401
    
    return decorated_function


@pusher_auth_bp.route('/auth', methods=['POST', 'OPTIONS'])
@cross_origin()
def authenticate_pusher():
    """
    Authenticate Pusher presence channel
    Required for presence channels to show who's online
    """
    # Handle OPTIONS preflight request
    if request.method == 'OPTIONS':
        return jsonify({'success': True}), 200
    
    # Verify JWT token for POST requests
    auth_header = request.headers.get('Authorization')
    
    logger.info(f"🔐 Pusher auth request - Full Authorization header: '{auth_header}'")
    logger.info(f"🔐 All headers: {dict(request.headers)}")
    
    if not auth_header or not auth_header.startswith('Bearer '):
        logger.warning(f"❌ Missing or invalid Authorization header: {auth_header}")
        return jsonify({
            'success': False,
            'error': 'Missing or invalid Authorization header'
        }), 401
    
    token = auth_header.split(' ')[1]
    logger.info(f"🔐 Token extracted, length: {len(token)}, first 20 chars: {token[:20]}...")
    
    try:
        jwt_secret = get_jwt_secret()
        payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
        user_id = payload.get('sub')
        
        logger.info(f"✅ Token decoded, user_id from payload: {user_id}")
        
        if not user_id:
            logger.warning("❌ No user_id in token payload")
            return jsonify({
                'success': False,
                'error': 'Invalid token payload'
            }), 401
        
        user_id = int(user_id)
        logger.info(f"✅ Authenticating user {user_id} for Pusher")
        
    except jwt.ExpiredSignatureError as e:
        logger.warning(f"❌ Token expired: {e}")
        return jsonify({
            'success': False,
            'error': 'Token has expired'
        }), 401
    except jwt.InvalidTokenError as e:
        logger.warning(f"❌ Invalid token: {e}")
        return jsonify({
            'success': False,
            'error': 'Invalid token'
        }), 401
    except Exception as e:
        logger.error(f"❌ Unexpected error decoding token: {e}")
        return jsonify({
            'success': False,
            'error': 'Token verification failed'
        }), 401
    
    try:
        # Get channel name and socket ID from request
        socket_id = request.form.get('socket_id')
        channel_name = request.form.get('channel_name')
        
        if not socket_id or not channel_name:
            return jsonify({
                'success': False,
                'error': 'Missing socket_id or channel_name'
            }), 400
        
        # Get user info from database
        from app.database.connection import get_db_connection, return_db_connection
        import psycopg2.extras
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)  # Use RealDictCursor
        
        try:
            cursor.execute("""
                SELECT id, name, email, avatar_url
                FROM users
                WHERE id = %s
            """, (user_id,))
            user = cursor.fetchone()
            
            if not user:
                return jsonify({
                    'success': False,
                    'error': 'User not found'
                }), 404
            
            # Prepare user data for presence channel
            user_data = {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'avatar_url': user.get('avatar_url')
            }
            
            # Authenticate with Pusher
            pusher = get_pusher_service()
            auth = pusher.pusher.authenticate(
                channel=channel_name,
                socket_id=socket_id,
                custom_data={
                    'user_id': user['id'],
                    'user_info': user_data
                }
            )
            
            logger.info(f"✅ Authenticated user {user_id} for channel {channel_name}")
            
            return jsonify(auth)
            
        finally:
            cursor.close()
            return_db_connection(conn)
        
    except Exception as e:
        logger.error(f"❌ Error authenticating Pusher: {str(e)}")
        logger.exception("Full traceback:")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
