"""
Friends API Routes (v2)
RESTful endpoints for friends and friend requests management
"""

from flask import Blueprint, request, jsonify
import logging

from app.services.friends_service import get_friends_service

logger = logging.getLogger(__name__)

# Create blueprint
friends_bp = Blueprint('friends', __name__, url_prefix='/api/v2')

# Get service instance
friends_service = get_friends_service()


@friends_bp.route('/friends/user/<int:user_id>', methods=['GET'])
def get_user_friends(user_id):
    """
    Get all friends for a user
    
    Path Parameters:
        user_id: User ID
    
    Response:
        {
            "success": true,
            "data": {
                "friends": [
                    {
                        "friendship_id": 1,
                        "friend_id": 2,
                        "friend_name": "John Doe",
                        "friend_email": "john@example.com",
                        "friend_since": "2025-01-15T10:30:00",
                        "status": "accepted"
                    }
                ],
                "count": 1
            }
        }
    """
    try:
        result = friends_service.get_friends(user_id)
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in get_user_friends: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@friends_bp.route('/friends/requests/user/<int:user_id>', methods=['GET'])
def get_friend_requests(user_id):
    """
    Get all friend requests for a user (incoming and outgoing)
    
    Path Parameters:
        user_id: User ID
    
    Response:
        {
            "success": true,
            "data": {
                "requests": [...],
                "incoming": [...],
                "outgoing": [...],
                "incoming_count": 2,
                "outgoing_count": 1
            }
        }
    """
    try:
        result = friends_service.get_friend_requests(user_id)
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in get_friend_requests: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@friends_bp.route('/friends/request', methods=['POST'])
def send_friend_request():
    """
    Send a friend request by email
    
    Request Body:
        {
            "requester_id": 1,
            "recipient_email": "friend@example.com",
            "message": "Let's be friends!"  // optional
        }
    
    Response:
        {
            "success": true,
            "data": {
                "id": 1,
                "requester_id": 1,
                "recipient_id": 2,
                "message": "Let's be friends!",
                "status": "pending",
                "created_at": "2025-10-21T12:00:00"
            },
            "message": "Friend request sent to John Doe"
        }
    """
    try:
        data = request.get_json()
        
        # Debug logging
        logger.info(f"Friend request received. Payload: {data}")
        
        # Validate required fields
        requester_id = data.get('requester_id')
        recipient_email = data.get('recipient_email')
        
        logger.info(f"Parsed: requester_id={requester_id}, recipient_email={recipient_email}")
        
        if not requester_id:
            logger.warning(f"Missing requester_id in payload: {data}")
            return jsonify({
                'success': False,
                'error': 'requester_id is required'
            }), 400
        
        if not recipient_email:
            logger.warning(f"Missing recipient_email in payload: {data}")
            return jsonify({
                'success': False,
                'error': 'recipient_email is required'
            }), 400
        
        # Optional message
        message = data.get('message')
        
        # Send request
        result = friends_service.send_friend_request(
            requester_id=requester_id,
            recipient_email=recipient_email,
            message=message
        )
        
        status_code = 201 if result.get('success') else 400
        
        if not result.get('success'):
            logger.warning(f"Friend request failed: {result.get('error')}")
        else:
            logger.info(f"Friend request sent successfully to {recipient_email}")
        
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in send_friend_request: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@friends_bp.route('/friends/request/<int:request_id>/accept', methods=['POST'])
def accept_friend_request(request_id):
    """
    Accept a friend request
    
    Path Parameters:
        request_id: Request ID to accept
    
    Request Body:
        {
            "user_id": 2  // User accepting (must be recipient)
        }
    
    Response:
        {
            "success": true,
            "data": {
                "request": {...},
                "friendship": {...}
            },
            "message": "You are now friends with John Doe"
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
        
        result = friends_service.accept_friend_request(request_id, user_id)
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in accept_friend_request: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@friends_bp.route('/friends/request/<int:request_id>/decline', methods=['POST'])
def decline_friend_request(request_id):
    """
    Decline a friend request
    
    Path Parameters:
        request_id: Request ID to decline
    
    Request Body:
        {
            "user_id": 2  // User declining (must be recipient)
        }
    
    Response:
        {
            "success": true,
            "data": {...},
            "message": "Friend request declined"
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
        
        result = friends_service.decline_friend_request(request_id, user_id)
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in decline_friend_request: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@friends_bp.route('/friends/<int:friend_id>', methods=['DELETE'])
def remove_friend(friend_id):
    """
    Remove a friend (unfriend)
    
    Path Parameters:
        friend_id: Friend user ID to remove
    
    Query Parameters:
        user_id: User ID removing the friend
    
    Response:
        {
            "success": true,
            "message": "Friend removed successfully"
        }
    """
    try:
        user_id = request.args.get('user_id', type=int)
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        result = friends_service.remove_friend(user_id, friend_id)
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in remove_friend: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@friends_bp.route('/friends/status', methods=['GET'])
def get_friendship_status():
    """
    Get friendship status between two users
    
    Query Parameters:
        user_id: First user ID
        other_user_id: Second user ID
    
    Response:
        {
            "success": true,
            "data": {
                "user_id": 1,
                "other_user_id": 2,
                "status": "friends"  // or "request_sent", "request_received", "none"
            }
        }
    """
    try:
        user_id = request.args.get('user_id', type=int)
        other_user_id = request.args.get('other_user_id', type=int)
        
        if not user_id or not other_user_id:
            return jsonify({
                'success': False,
                'error': 'user_id and other_user_id are required'
            }), 400
        
        result = friends_service.get_friendship_status(user_id, other_user_id)
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in get_friendship_status: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
