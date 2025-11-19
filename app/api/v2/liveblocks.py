"""
Liveblocks Integration API (v2)
Authentication and configuration for Liveblocks real-time collaboration
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import logging
import jwt
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Create blueprint
liveblocks_bp = Blueprint('liveblocks_v2', __name__, url_prefix='/api/v2/liveblocks')


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


# Helper function to get Liveblocks secret
def get_liveblocks_secret():
    """Get Liveblocks secret key from environment"""
    secret = os.getenv('LIVEBLOCKS_SECRET_KEY')
    if not secret:
        logger.warning("LIVEBLOCKS_SECRET_KEY not set in environment! Using development key.")
        return 'dev-liveblocks-secret-for-local-testing-only'
    return secret


# Helper function to get user initials
def get_user_initials(name):
    """Extract initials from user's name"""
    if not name:
        return "?"
    
    # Split name and take first letter of each word
    parts = name.strip().split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[1][0]}".upper()
    elif len(parts) == 1:
        # Single name - use first two letters
        return name[:2].upper() if len(name) >= 2 else name[0].upper()
    return "?"


# Helper function to assign user color
def assign_user_color(user_id):
    """Assign a consistent color to a user based on their ID"""
    # Predefined color palette (mint shades + complementary colors)
    colors = [
        "#7FD4C1",  # Medium mint
        "#4FB69A",  # Dark mint
        "#9FDFCD",  # Light mint  
        "#5BC0A3",  # Teal mint
        "#FF9B9B",  # Soft coral (complement)
        "#FFB84D",  # Soft orange (complement)
        "#9B9BFF",  # Soft purple (complement)
        "#FFB6D9",  # Soft pink (complement)
    ]
    
    # Use user_id to consistently pick a color
    color_index = user_id % len(colors)
    return colors[color_index]


@liveblocks_bp.route('/auth', methods=['OPTIONS'])
def auth_options():
    """Handle CORS preflight for auth endpoint"""
    response = jsonify({'status': 'ok'})
    response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response, 200


@liveblocks_bp.route('/auth', methods=['POST'])
@handle_errors
def authenticate():
    """
    Generate Liveblocks authentication token
    
    Expected request body (from Liveblocks client):
    {
        "room": "whiteboard-123"  // Room ID to access
    }
    
    Expected headers:
    Authorization: Bearer <YesChef JWT token>
    
    Returns:
    {
        "token": "<Liveblocks JWT token>"
    }
    """
    
    # 1. Get YesChef JWT token from request headers
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        logger.warning("Missing or invalid Authorization header")
        return jsonify({
            'success': False,
            'error': 'Missing authentication token'
        }), 401
    
    yeschef_token = auth_header.split(' ')[1]
    
    # 2. Verify YesChef JWT token and extract user info
    try:
        # Decode YesChef token (use same secret as auth_system.py)
        import hashlib
        database_url = os.getenv('DATABASE_URL', '')
        jwt_secret = os.getenv('JWT_SECRET_KEY') or hashlib.sha256(database_url.encode()).hexdigest()
        
        user_data = jwt.decode(yeschef_token, jwt_secret, algorithms=['HS256'])
        # YesChef uses 'sub' (subject) for user ID, not 'user_id'
        user_id = user_data.get('sub')
        
        if not user_id:
            logger.warning(f"JWT token missing 'sub' claim. Token data: {user_data}")
            return jsonify({
                'success': False,
                'error': 'Invalid token'
            }), 401
        
        # Convert to integer
        user_id = int(user_id)
            
    except jwt.ExpiredSignatureError:
        logger.warning("Expired JWT token")
        return jsonify({
            'success': False,
            'error': 'Token expired'
        }), 401
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Invalid token'
        }), 401
    
    # 3. Get room ID from request body (sent by Liveblocks client)
    data = request.get_json() or {}
    room_id = data.get('room')
    
    if not room_id:
        logger.warning("Missing room parameter in request")
        return jsonify({
            'success': False,
            'error': 'Missing room parameter'
        }), 400
    
    # 4. Fetch user details from database
    try:
        from app.services.user_service import UserService
        user_service = UserService()
        user = user_service.get_user_by_id(user_id)
        
        if not user:
            logger.warning(f"User {user_id} not found")
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Extract user info
        user_name = user.get('username') or user.get('email', 'Unknown User')
        user_email = user.get('email', '')
        
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {str(e)}")
        # Fallback to basic info if DB query fails
        user_name = f"User {user_id}"
        user_email = ""
    
    # 5. Generate initials and color
    initials = get_user_initials(user_name)
    color = assign_user_color(user_id)
    
    # 6. Get Liveblocks token via their REST API
    # We can't create JWTs ourselves - we need to call Liveblocks!
    # Reference: https://liveblocks.io/docs/api-reference/rest-api-endpoints#post-authorize-access-token
    liveblocks_secret = get_liveblocks_secret()
    
    logger.info(f"🔑 Using Liveblocks secret: {liveblocks_secret[:10]}...{liveblocks_secret[-10:]}")
    
    # Prepare the request to Liveblocks REST API
    import requests
    
    liveblocks_api_url = "https://api.liveblocks.io/v2/authorize-access-token"
    
    # Payload for Liveblocks API
    payload = {
        "userId": str(user_id),
        "permissions": {
            room_id: ["room:write"]
        }
    }
    
    headers = {
        "Authorization": f"Bearer {liveblocks_secret}",
        "Content-Type": "application/json"
    }
    
    logger.info(f"� Requesting token from Liveblocks API for user {user_id}, room {room_id}")
    
    try:
        response = requests.post(liveblocks_api_url, json=payload, headers=headers)
        response.raise_for_status()
        
        liveblocks_data = response.json()
        liveblocks_token = liveblocks_data.get('token')
        
        if not liveblocks_token:
            logger.error(f"❌ No token in Liveblocks response: {liveblocks_data}")
            return jsonify({
                'success': False,
                'error': 'Failed to get token from Liveblocks'
            }), 500
        
        logger.info(f"✅ Got Liveblocks token for user {user_id}, room {room_id}")
        logger.info(f"   Token (first 50 chars): {liveblocks_token[:50]}...")
        
        # 7. Return the token
        return jsonify({
            'token': liveblocks_token
        }), 200
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Liveblocks API error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Liveblocks API error: {str(e)}'
        }), 500


@liveblocks_bp.route('/webhook', methods=['POST'])
@handle_errors
def webhook():
    """
    Handle Liveblocks webhooks (optional - for future features)
    
    Webhooks can notify us when:
    - Comments are created
    - Users join/leave rooms
    - Storage is updated
    
    For now, this is a placeholder for future enhancements.
    """
    data = request.get_json() or {}
    event_type = data.get('type')
    
    logger.info(f"Received Liveblocks webhook: {event_type}")
    
    # TODO: Handle specific webhook events
    # - commentCreated: Send email notifications
    # - storageUpdated: Track activity
    # - userJoined: Log analytics
    
    return jsonify({
        'success': True,
        'message': 'Webhook received'
    }), 200
