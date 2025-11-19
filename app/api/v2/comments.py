"""
Comments API (v2)
RESTful endpoints for whiteboard comments with real-time updates via Pusher
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
import logging
from datetime import datetime

from app.services.pusher_service import get_pusher_service

logger = logging.getLogger(__name__)

# Create blueprint
comments_bp = Blueprint('comments_v2', __name__, url_prefix='/api/v2/comments')


@comments_bp.route('', methods=['POST', 'OPTIONS'])
@cross_origin()
@jwt_required()
def create_comment():
    """
    Create a new comment
    
    Request body:
    {
        "whiteboard_id": 52,
        "object_type": "recipe",
        "object_id": "2755",
        "content": "This looks delicious!",
        "parent_id": null  // Optional, for threaded replies
    }
    """
    try:
        from app.database.connection import get_db_connection, return_db_connection
        from flask_jwt_extended import get_jwt_identity
        
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        whiteboard_id = data.get('whiteboard_id')
        object_type = data.get('object_type')
        object_id = data.get('object_id')
        content = data.get('content', '').strip()
        parent_id = data.get('parent_id')
        
        # Validation
        if not all([whiteboard_id, object_type, object_id, content]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400
        
        if len(content) > 5000:
            return jsonify({
                'success': False,
                'error': 'Comment too long (max 5000 characters)'
            }), 400
        
        # Insert comment
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO comments (user_id, whiteboard_id, object_type, object_id, content, parent_id, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
                RETURNING id, user_id, whiteboard_id, object_type, object_id, content, parent_id, created_at, updated_at
            """, (user_id, whiteboard_id, object_type, object_id, content, parent_id))
            
            comment = cursor.fetchone()
            conn.commit()
            
            if not comment:
                return jsonify({
                    'success': False,
                    'error': 'Failed to create comment'
                }), 500
            
            # Fetch user info for the comment
            cursor.execute("""
                SELECT id, name, email, avatar_url
                FROM users
                WHERE id = %s
            """, (user_id,))
            user = cursor.fetchone()
            
            # Format comment response
            comment_data = {
                'id': comment['id'],
                'user_id': comment['user_id'],
                'user': {
                    'id': user['id'],
                    'name': user['name'],
                    'email': user['email'],
                    'avatar_url': user.get('avatar_url'),
                } if user else None,
                'whiteboard_id': comment['whiteboard_id'],
                'object_type': comment['object_type'],
                'object_id': comment['object_id'],
                'content': comment['content'],
                'parent_id': comment['parent_id'],
                'created_at': comment['created_at'].isoformat() if comment.get('created_at') else None,
                'updated_at': comment['updated_at'].isoformat() if comment.get('updated_at') else None,
            }
            
            # Broadcast via Pusher
            pusher = get_pusher_service()
            pusher.broadcast_comment_created(whiteboard_id, comment_data)
            
            # Log activity event
            try:
                from app.utils.event_logger import EventLogger
                
                # Get household_id from whiteboard
                cursor.execute("SELECT hid FROM wb WHERE id = %s", (whiteboard_id,))
                wb = cursor.fetchone()
                
                if wb and wb['hid']:
                    EventLogger.log_event(
                        household_id=wb['hid'],
                        user_id=user_id,
                        event_type='comment.added',
                        resource_type=object_type,
                        resource_id=int(object_id),
                        event_data={
                            'whiteboard_id': whiteboard_id,
                            'comment_preview': content[:100],
                            'object_type': object_type
                        },
                        title=f"Comment on {object_type}",
                        description=f"commented on {object_type}"
                    )
            except Exception as e:
                logger.warning(f"Failed to log comment event: {e}")
            
            logger.info(f"✅ Created comment {comment['id']} on {object_type} {object_id}")
            
            return jsonify({
                'success': True,
                'comment': comment_data
            }), 201
            
        finally:
            cursor.close()
            return_db_connection(conn)
        
    except Exception as e:
        logger.error(f"❌ Error creating comment: {str(e)}")
        logger.exception("Full traceback:")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@comments_bp.route('', methods=['GET', 'OPTIONS'])
@cross_origin()
@jwt_required()
def get_comments():
    """
    Get comments for a whiteboard/object
    
    Query params:
    - whiteboard_id: Required
    - object_type: Optional (e.g., "recipe", "meal_plan")
    - object_id: Optional
    """
    try:
        from app.database.connection import get_db_connection, return_db_connection
        
        whiteboard_id = request.args.get('whiteboard_id')
        object_type = request.args.get('object_type')
        object_id = request.args.get('object_id')
        
        if not whiteboard_id:
            return jsonify({
                'success': False,
                'error': 'whiteboard_id required'
            }), 400
        
        # Build query
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            if object_type and object_id:
                # Get comments for specific object
                cursor.execute("""
                    SELECT c.id, c.user_id, c.whiteboard_id, c.object_type, c.object_id, 
                           c.content, c.parent_id, c.created_at, c.updated_at,
                           u.name, u.email, u.avatar_url
                    FROM comments c
                    LEFT JOIN users u ON c.user_id = u.id
                    WHERE c.whiteboard_id = %s 
                      AND c.object_type = %s 
                      AND c.object_id = %s
                    ORDER BY c.created_at ASC
                """, (whiteboard_id, object_type, object_id))
            else:
                # Get all comments for whiteboard
                cursor.execute("""
                    SELECT c.id, c.user_id, c.whiteboard_id, c.object_type, c.object_id, 
                           c.content, c.parent_id, c.created_at, c.updated_at,
                           u.name, u.email, u.avatar_url
                    FROM comments c
                    LEFT JOIN users u ON c.user_id = u.id
                    WHERE c.whiteboard_id = %s
                    ORDER BY c.created_at ASC
                """, (whiteboard_id,))
            
            results = cursor.fetchall()
            
            # Format comments
            comments = []
            for row in results:
                comments.append({
                    'id': row['id'],
                    'user_id': row['user_id'],
                    'user': {
                        'id': row['user_id'],
                        'name': row.get('name'),
                        'email': row.get('email'),
                        'avatar_url': row.get('avatar_url'),
                    },
                    'whiteboard_id': row['whiteboard_id'],
                    'object_type': row['object_type'],
                    'object_id': row['object_id'],
                    'content': row['content'],
                    'parent_id': row.get('parent_id'),
                    'created_at': row['created_at'].isoformat() if row.get('created_at') else None,
                    'updated_at': row['updated_at'].isoformat() if row.get('updated_at') else None,
                })
            
            logger.info(f"✅ Fetched {len(comments)} comments for whiteboard {whiteboard_id}")
            
            return jsonify({
                'success': True,
                'comments': comments
            }), 200
            
        finally:
            cursor.close()
            return_db_connection(conn)
        
    except Exception as e:
        logger.error(f"❌ Error fetching comments: {str(e)}")
        logger.exception("Full traceback:")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@comments_bp.route('/<int:comment_id>', methods=['PATCH', 'OPTIONS'])
@cross_origin()
@jwt_required()
def update_comment(comment_id):
    """Update a comment (only by the author)"""
    try:
        from core_systems.database_manager import DatabaseManager
        from flask_jwt_extended import get_jwt_identity
        
        user_id = get_jwt_identity()
        data = request.get_json()
        content = data.get('content', '').strip()
        
        if not content:
            return jsonify({
                'success': False,
                'error': 'Content required'
            }), 400
        
        db = DatabaseManager()
        
        # Check ownership
        check_query = "SELECT user_id, whiteboard_id FROM comments WHERE id = %s"
        result = db.execute_query(check_query, (comment_id,))
        
        if not result:
            return jsonify({
                'success': False,
                'error': 'Comment not found'
            }), 404
        
        if result[0]['user_id'] != int(user_id):
            return jsonify({
                'success': False,
                'error': 'Unauthorized'
            }), 403
        
        whiteboard_id = result[0]['whiteboard_id']
        
        # Update comment
        update_query = """
            UPDATE comments 
            SET content = %s, updated_at = NOW()
            WHERE id = %s
            RETURNING id, user_id, whiteboard_id, object_type, object_id, content, parent_id, created_at, updated_at
        """
        
        updated = db.execute_query(update_query, (content, comment_id))
        
        if updated:
            comment = updated[0]
            
            # Fetch user info
            user_query = "SELECT id, username, email, avatar_url FROM users WHERE id = %s"
            user_result = db.execute_query(user_query, (user_id,))
            user = user_result[0] if user_result else None
            
            comment_data = {
                'id': comment['id'],
                'user_id': comment['user_id'],
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'avatar_url': user.get('avatar_url'),
                } if user else None,
                'whiteboard_id': comment['whiteboard_id'],
                'object_type': comment['object_type'],
                'object_id': comment['object_id'],
                'content': comment['content'],
                'parent_id': comment['parent_id'],
                'created_at': comment['created_at'].isoformat() if comment['created_at'] else None,
                'updated_at': comment['updated_at'].isoformat() if comment['updated_at'] else None,
            }
            
            # Broadcast update
            pusher = get_pusher_service()
            pusher.broadcast_comment_updated(whiteboard_id, comment_data)
            
            return jsonify({
                'success': True,
                'comment': comment_data
            }), 200
        
        return jsonify({
            'success': False,
            'error': 'Failed to update comment'
        }), 500
        
    except Exception as e:
        logger.error(f"❌ Error updating comment: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@comments_bp.route('/<int:comment_id>', methods=['DELETE', 'OPTIONS'])
@cross_origin()
@jwt_required()
def delete_comment(comment_id):
    """Delete a comment (only by the author)"""
    try:
        from app.database.connection import get_db_connection, return_db_connection
        from flask_jwt_extended import get_jwt_identity
        
        user_id = int(get_jwt_identity())
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Check ownership
            cursor.execute("SELECT user_id, whiteboard_id FROM comments WHERE id = %s", (comment_id,))
            result = cursor.fetchone()
            
            if not result:
                return jsonify({
                    'success': False,
                    'error': 'Comment not found'
                }), 404
            
            if result['user_id'] != user_id:
                return jsonify({
                    'success': False,
                    'error': 'Unauthorized'
                }), 403
            
            whiteboard_id = result['whiteboard_id']
            
            # Delete comment
            cursor.execute("DELETE FROM comments WHERE id = %s", (comment_id,))
            conn.commit()
            
            # Broadcast deletion
            pusher = get_pusher_service()
            pusher.broadcast_comment_deleted(whiteboard_id, comment_id)
            
            logger.info(f"✅ Deleted comment {comment_id}")
            
            return jsonify({
                'success': True
            }), 200
            
        finally:
            cursor.close()
            return_db_connection(conn)
        
    except Exception as e:
        logger.error(f"❌ Error deleting comment: {str(e)}")
        logger.exception("Full traceback:")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@comments_bp.route('/count', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_comment_counts():
    """
    Get comment counts for multiple objects in a whiteboard
    
    Query params:
    - whiteboard_id: Required
    """
    try:
        from app.database.connection import get_db_connection, return_db_connection
        
        whiteboard_id = request.args.get('whiteboard_id')
        
        if not whiteboard_id:
            return jsonify({
                'success': False,
                'error': 'whiteboard_id required'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Get all comment counts grouped by object
            cursor.execute("""
                SELECT object_type, object_id, COUNT(*) as count
                FROM comments
                WHERE whiteboard_id = %s
                GROUP BY object_type, object_id
            """, (whiteboard_id,))
            
            results = cursor.fetchall()
            
            # Format as {object_type: {object_id: count}}
            counts = {}
            for row in results:
                object_type = row['object_type']
                object_id = row['object_id']
                count = row['count']
                
                if object_type not in counts:
                    counts[object_type] = {}
                counts[object_type][object_id] = count
            
            return jsonify({
                'success': True,
                'counts': counts
            }), 200
            
        finally:
            cursor.close()
            return_db_connection(conn)
        
    except Exception as e:
        logger.error(f"❌ Error fetching comment counts: {str(e)}")
        logger.exception("Full traceback:")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
