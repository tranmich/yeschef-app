"""
WebSocket Service
=================
Real-time communication infrastructure for YesChef

Features:
- Grocery list updates (live sync)
- Chat messages (future)
- Comments on recipes/whiteboards (future)
- Notifications (future)
- Collaborative editing (future)

Architecture:
- Rooms organized by household_id
- Event-driven communication
- Scalable for multiple features

Author: GitHub Copilot
Date: November 4, 2025
"""

from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
from flask import request
from functools import wraps
import logging
import jwt
import os

logger = logging.getLogger(__name__)

# Global SocketIO instance (initialized in hungie_server.py)
socketio = None

def init_socketio(app):
    """
    Initialize SocketIO with Flask app
    
    Args:
        app: Flask application instance
    """
    global socketio
    socketio = SocketIO(
        app,
        cors_allowed_origins="*",  # Adjust for production
        async_mode='threading',     # Use threading for Flask
        logger=True,
        engineio_logger=True
    )
    
    logger.info("✅ WebSocket service initialized")
    return socketio


# =====================================================
# AUTHENTICATION DECORATOR
# =====================================================

def authenticated_socket(f):
    """
    Decorator to verify JWT token for socket events
    Similar to @jwt_required for REST endpoints
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from handshake auth
        from flask import request
        token = request.args.get('token')
        
        if not token:
            logger.warning("🔐 Socket connection without token")
            return {'success': False, 'error': 'Authentication required'}
        
        try:
            # Verify JWT token
            jwt_secret = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
            payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
            user_id = int(payload.get('sub'))
            
            # Add user_id to kwargs
            kwargs['user_id'] = user_id
            return f(*args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            logger.warning("🔐 Expired token in socket connection")
            return {'success': False, 'error': 'Token expired'}
        except jwt.InvalidTokenError:
            logger.warning("🔐 Invalid token in socket connection")
            return {'success': False, 'error': 'Invalid token'}
        except Exception as e:
            logger.error(f"🔐 Socket auth error: {e}")
            return {'success': False, 'error': 'Authentication failed'}
    
    return decorated_function


# =====================================================
# ROOM MANAGEMENT
# =====================================================

def get_household_room(household_id):
    """Get room name for household"""
    return f"household_{household_id}"

def get_whiteboard_room(whiteboard_id):
    """Get room name for whiteboard (for future collaborative editing)"""
    return f"whiteboard_{whiteboard_id}"

def get_user_room(user_id):
    """Get room name for user-specific notifications"""
    return f"user_{user_id}"


# =====================================================
# CONNECTION HANDLERS
# =====================================================

@socketio.on('connect')
def handle_connect():
    """Handle new WebSocket connection"""
    logger.info(f"🔌 New WebSocket connection: {request.sid}")
    emit('connected', {
        'success': True,
        'message': 'Connected to YesChef real-time server',
        'features': ['grocery_lists', 'chat', 'comments', 'notifications']
    })


@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    logger.info(f"🔌 WebSocket disconnected: {request.sid}")


# =====================================================
# ROOM JOIN/LEAVE
# =====================================================

@socketio.on('join_household')
@authenticated_socket
def handle_join_household(data, user_id=None):
    """
    Join household room for real-time updates
    
    Args:
        data: {'household_id': 11}
        user_id: From auth decorator
    """
    household_id = data.get('household_id')
    
    if not household_id:
        return {'success': False, 'error': 'household_id required'}
    
    # TODO: Verify user is member of household
    
    room = get_household_room(household_id)
    join_room(room)
    
    logger.info(f"👤 User {user_id} joined household room: {room}")
    
    return {
        'success': True,
        'room': room,
        'household_id': household_id
    }


@socketio.on('leave_household')
@authenticated_socket
def handle_leave_household(data, user_id=None):
    """Leave household room"""
    household_id = data.get('household_id')
    
    if not household_id:
        return {'success': False, 'error': 'household_id required'}
    
    room = get_household_room(household_id)
    leave_room(room)
    
    logger.info(f"👤 User {user_id} left household room: {room}")
    
    return {'success': True}


# =====================================================
# GROCERY LIST EVENTS
# =====================================================

@socketio.on('grocery_list_updated')
@authenticated_socket
def handle_grocery_list_updated(data, user_id=None):
    """
    Broadcast grocery list update to household
    
    Args:
        data: {
            'household_id': 11,
            'list_id': 123,
            'action': 'item_added' | 'item_checked' | 'item_removed',
            'item': {...},
            'updated_by': user_id
        }
    """
    household_id = data.get('household_id')
    
    if not household_id:
        return {'success': False, 'error': 'household_id required'}
    
    room = get_household_room(household_id)
    
    # Broadcast to all household members
    emit('grocery_list_update', {
        'list_id': data.get('list_id'),
        'action': data.get('action'),
        'item': data.get('item'),
        'updated_by': user_id,
        'timestamp': data.get('timestamp')
    }, room=room, include_self=False)  # Don't send to sender
    
    logger.info(f"📝 Grocery list update broadcast to {room}")
    
    return {'success': True}


@socketio.on('item_checked')
@authenticated_socket
def handle_item_checked(data, user_id=None):
    """
    Broadcast item check/uncheck
    
    Args:
        data: {
            'household_id': 11,
            'list_id': 123,
            'item_id': 456,
            'checked': true/false
        }
    """
    household_id = data.get('household_id')
    room = get_household_room(household_id)
    
    emit('item_check_update', {
        'list_id': data.get('list_id'),
        'item_id': data.get('item_id'),
        'checked': data.get('checked'),
        'updated_by': user_id
    }, room=room, include_self=False)
    
    return {'success': True}


@socketio.on('item_transferred')
@authenticated_socket
def handle_item_transferred(data, user_id=None):
    """
    Broadcast item transfer between lists
    
    Args:
        data: {
            'household_id': 11,
            'from_list_id': 123,
            'to_list_id': 456,
            'item': {...}
        }
    """
    household_id = data.get('household_id')
    room = get_household_room(household_id)
    
    emit('item_transfer_update', {
        'from_list_id': data.get('from_list_id'),
        'to_list_id': data.get('to_list_id'),
        'item': data.get('item'),
        'updated_by': user_id
    }, room=room, include_self=False)
    
    return {'success': True}


# =====================================================
# FUTURE: CHAT EVENTS (Placeholder)
# =====================================================

@socketio.on('chat_message')
@authenticated_socket
def handle_chat_message(data, user_id=None):
    """
    Send chat message to household
    
    Args:
        data: {
            'household_id': 11,
            'message': 'Can you pick up milk?',
            'thread_id': optional
        }
    """
    # TODO: Implement chat feature
    logger.info(f"💬 Chat message from user {user_id}: {data.get('message')}")
    return {'success': True, 'message': 'Chat feature coming soon!'}


# =====================================================
# FUTURE: COMMENT EVENTS (Placeholder)
# =====================================================

@socketio.on('comment_added')
@authenticated_socket
def handle_comment_added(data, user_id=None):
    """
    Add comment to recipe/whiteboard
    
    Args:
        data: {
            'entity_type': 'recipe' | 'whiteboard',
            'entity_id': 123,
            'comment': 'This recipe is amazing!'
        }
    """
    # TODO: Implement comments feature
    logger.info(f"💬 Comment from user {user_id}: {data.get('comment')}")
    return {'success': True, 'message': 'Comments feature coming soon!'}


# =====================================================
# UTILITY FUNCTIONS
# =====================================================

def broadcast_to_household(household_id, event, data):
    """
    Utility to broadcast event to household from REST API
    
    Usage:
        from app.services.websocket_service import broadcast_to_household
        broadcast_to_household(11, 'grocery_list_update', {...})
    """
    if socketio:
        room = get_household_room(household_id)
        socketio.emit(event, data, room=room)
        logger.info(f"📡 Broadcast {event} to household {household_id}")
    else:
        logger.warning("⚠️ SocketIO not initialized, cannot broadcast")


def broadcast_to_user(user_id, event, data):
    """
    Broadcast to specific user
    
    For notifications, direct messages, etc.
    """
    if socketio:
        room = get_user_room(user_id)
        socketio.emit(event, data, room=room)
        logger.info(f"📡 Broadcast {event} to user {user_id}")
