"""
System & Admin API v2 Routes
RESTful endpoints for system monitoring, admin operations, and utilities
"""

from flask import Blueprint, request, jsonify
import logging

from app.services.system_service import SystemService

logger = logging.getLogger(__name__)

# Create blueprint
system_bp = Blueprint('system_v2', __name__, url_prefix='/api/v2/system')

# Initialize service
system_service = SystemService()


@system_bp.route('/health', methods=['GET'])
def health_check():
    """
    System health check endpoint
    
    Returns system status and database connectivity
    """
    try:
        result = system_service.get_health()
        
        if result['success']:
            return jsonify(result), 200
        
        return jsonify(result), 503
        
    except Exception as e:
        logger.error(f"Error in health_check: {e}")
        return jsonify({
            'success': False,
            'error': 'Health check failed'
        }), 503


@system_bp.route('/stats', methods=['GET'])
def get_system_stats():
    """
    Get system statistics
    
    Returns counts for users, recipes, favorites, etc.
    """
    try:
        result = system_service.get_stats()
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in get_system_stats: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@system_bp.route('/analytics', methods=['GET'])
def get_analytics():
    """
    Get system analytics
    
    Returns popular categories and growth stats
    """
    try:
        result = system_service.get_analytics()
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in get_analytics: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@system_bp.route('/cleanup', methods=['POST'])
def cleanup_system():
    """
    Clean up orphaned data
    
    Admin operation to clean up database
    """
    try:
        result = system_service.cleanup_system()
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in cleanup_system: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


# ============================================================================
# ADMIN OPERATIONS
# ============================================================================

@system_bp.route('/admin/users', methods=['GET'])
def get_all_users():
    """
    Get all users (admin operation)
    
    Query params:
    - limit (optional): Results limit (default: 100)
    - offset (optional): Pagination offset (default: 0)
    """
    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        result = system_service.get_all_users(limit=limit, offset=offset)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in get_all_users: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@system_bp.route('/admin/users/<int:user_id>/activity', methods=['GET'])
def get_user_activity(user_id):
    """
    Get user activity summary (admin operation)
    
    Path params:
    - user_id: User ID
    """
    try:
        result = system_service.get_user_activity(user_id=user_id)
        
        if result['success']:
            return jsonify(result), 200
        
        return jsonify(result), 404
        
    except Exception as e:
        logger.error(f"Error in get_user_activity: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@system_bp.route('/admin/users/inactive', methods=['GET'])
def get_inactive_users():
    """
    Get inactive users (admin operation)
    
    Query params:
    - days (optional): Days of inactivity (default: 30)
    """
    try:
        days = request.args.get('days', 30, type=int)
        
        result = system_service.get_inactive_users(days=days)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in get_inactive_users: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


# ============================================================================
# VOICE COMMANDS
# ============================================================================

@system_bp.route('/voice/command', methods=['POST'])
def process_voice_command():
    """
    Process voice command (placeholder)
    
    Request body:
    {
        "user_id": 10,
        "command": "Find me a pasta recipe"
    }
    """
    try:
        data = request.get_json()
        
        user_id = data.get('user_id')
        command = data.get('command')
        
        if not user_id or not command:
            return jsonify({
                'success': False,
                'error': 'user_id and command are required'
            }), 400
        
        result = system_service.process_voice_command(
            user_id=user_id,
            command=command
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in process_voice_command: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


# Register error handlers
@system_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Resource not found'
    }), 404


@system_bp.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500
