"""
Activity Feed API Routes (V2)
==============================
RESTful endpoints for household activity feed and notifications

Endpoints:
- GET  /api/v2/activity/feed - Get global activity feed (all households)
- GET  /api/v2/households/{id}/activity - Get household-specific activity
- POST /api/v2/activity/mark-read - Mark events as read

Author: GitHub Copilot
Date: November 10, 2025
"""

from flask import Blueprint, request, jsonify
import logging
import psycopg2.extras
from datetime import datetime, timedelta

from app.database.connection import get_db_connection, return_db_connection
from app.api.v2.whiteboards import jwt_required_v2, handle_errors
from app.utils.event_logger import EventLogger

logger = logging.getLogger(__name__)

# Create blueprint
activity_bp = Blueprint('activity_v2', __name__, url_prefix='/api/v2/activity')


@activity_bp.route('/feed', methods=['GET'])
@jwt_required_v2
@handle_errors
def get_global_activity_feed():
    """
    Get global activity feed across all user's households
    
    GET /api/v2/activity/feed?limit=50&offset=0&event_types=recipe,comment
    
    Query Parameters:
    - limit: Number of events to return (default: 50, max: 100)
    - offset: Pagination offset (default: 0)
    - event_types: Comma-separated list of event types to filter
    - since: ISO timestamp to get events after this time
    
    Returns: Paginated list of activity events with user and household info
    """
    user_id = request.user_id
    
    # Parse query parameters
    limit = min(int(request.args.get('limit', 50)), 100)
    offset = int(request.args.get('offset', 0))
    event_types_param = request.args.get('event_types')
    since_param = request.args.get('since')
    
    logger.info(f"User {user_id} fetching global activity feed (limit={limit}, offset={offset})")
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        # Build WHERE clause
        where_clauses = []
        params = [user_id]
        
        # Filter by event types if provided
        if event_types_param:
            event_types = [t.strip() for t in event_types_param.split(',')]
            where_clauses.append(f"af.event_type = ANY(%s)")
            params.append(event_types)
        
        # Filter by time if provided
        if since_param:
            where_clauses.append("af.created_at > %s")
            params.append(since_param)
        
        where_clause = "AND " + " AND ".join(where_clauses) if where_clauses else ""
        
        # Get events from all user's households
        params_with_pagination = params + [limit, offset]
        cursor.execute(f"""
            SELECT 
                af.id,
                af.household_id,
                af.user_id,
                af.event_type,
                af.resource_type,
                af.reference_id,
                af.title,
                af.description,
                af.event_data,
                af.created_at,
                af.is_read,
                h.name as household_name,
                u.name as user_name,
                u.email as user_email
            FROM activity_feed af
            INNER JOIN household_members hm ON af.household_id = hm.household_id
            INNER JOIN households h ON af.household_id = h.id
            INNER JOIN users u ON af.user_id = u.id
            WHERE hm.user_id = %s
            {where_clause}
            ORDER BY af.created_at DESC
            LIMIT %s OFFSET %s
        """, tuple(params_with_pagination))
        
        events = cursor.fetchall()
        
        # Get total count for pagination
        cursor.execute(f"""
            SELECT COUNT(*) as total
            FROM activity_feed af
            INNER JOIN household_members hm ON af.household_id = hm.household_id
            WHERE hm.user_id = %s
            {where_clause}
        """, tuple(params))
        
        total = cursor.fetchone()['total']
        
        # Get unread count
        cursor.execute("""
            SELECT COUNT(*) as unread
            FROM activity_feed af
            INNER JOIN household_members hm ON af.household_id = hm.household_id
            WHERE hm.user_id = %s AND af.is_read = FALSE
        """, (user_id,))
        
        unread_count = cursor.fetchone()['unread']
        
        # Format events with time_ago
        formatted_events = []
        for event in events:
            event_dict = dict(event)
            # Add human-readable time
            event_dict['time_ago'] = _format_time_ago(event['created_at'])
            formatted_events.append(event_dict)
        
        return jsonify({
            'success': True,
            'events': formatted_events,
            'pagination': {
                'total': total,
                'limit': limit,
                'offset': offset,
                'has_more': (offset + limit) < total
            },
            'unread_count': unread_count
        }), 200
        
    finally:
        cursor.close()
        return_db_connection(conn)


@activity_bp.route('/households/<int:household_id>', methods=['GET'])
@jwt_required_v2
@handle_errors
def get_household_activity(household_id):
    """
    Get activity feed for a specific household
    
    GET /api/v2/activity/households/11?limit=30&offset=0
    
    Query Parameters:
    - limit: Number of events (default: 30, max: 100)
    - offset: Pagination offset (default: 0)
    - event_types: Filter by event types
    
    Returns: Household-specific activity events
    """
    user_id = request.user_id
    
    limit = min(int(request.args.get('limit', 30)), 100)
    offset = int(request.args.get('offset', 0))
    event_types_param = request.args.get('event_types')
    
    logger.info(f"User {user_id} fetching activity for household {household_id}")
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        # Verify user has access to household
        cursor.execute("""
            SELECT 1 FROM household_members 
            WHERE household_id = %s AND user_id = %s
        """, (household_id, user_id))
        
        if not cursor.fetchone():
            return jsonify({
                'success': False,
                'error': 'FORBIDDEN',
                'message': 'Access denied to this household'
            }), 403
        
        # Build query
        where_clauses = [f"af.household_id = {household_id}"]
        params = []
        
        if event_types_param:
            event_types = [t.strip() for t in event_types_param.split(',')]
            where_clauses.append("af.event_type = ANY(%s)")
            params.append(event_types)
        
        where_clause = " AND ".join(where_clauses)
        params_with_pagination = params + [limit, offset]
        
        # Get events
        cursor.execute(f"""
            SELECT 
                af.id,
                af.household_id,
                af.user_id,
                af.event_type,
                af.resource_type,
                af.reference_id,
                af.title,
                af.description,
                af.event_data,
                af.created_at,
                af.is_read,
                u.name as user_name,
                u.email as user_email
            FROM activity_feed af
            INNER JOIN users u ON af.user_id = u.id
            WHERE {where_clause}
            ORDER BY af.created_at DESC
            LIMIT %s OFFSET %s
        """, tuple(params_with_pagination))
        
        events = cursor.fetchall()
        
        # Get total and unread counts
        cursor.execute(f"""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN is_read = FALSE THEN 1 ELSE 0 END) as unread
            FROM activity_feed af
            WHERE {where_clause}
        """, tuple(params))
        
        counts = cursor.fetchone()
        
        # Format events
        formatted_events = []
        for event in events:
            event_dict = dict(event)
            event_dict['time_ago'] = _format_time_ago(event['created_at'])
            formatted_events.append(event_dict)
        
        return jsonify({
            'success': True,
            'household_id': household_id,
            'events': formatted_events,
            'pagination': {
                'total': counts['total'],
                'limit': limit,
                'offset': offset,
                'has_more': (offset + limit) < counts['total']
            },
            'unread_count': counts['unread'] or 0
        }), 200
        
    finally:
        cursor.close()
        return_db_connection(conn)


@activity_bp.route('/mark-read', methods=['POST'])
@jwt_required_v2
@handle_errors
def mark_events_read():
    """
    Mark activity events as read
    
    POST /api/v2/activity/mark-read
    Body: {
        "event_ids": [123, 124, 125]
    }
    
    Returns: Number of events marked as read
    """
    user_id = request.user_id
    data = request.get_json()
    
    event_ids = data.get('event_ids', [])
    
    if not event_ids or not isinstance(event_ids, list):
        return jsonify({
            'success': False,
            'error': 'INVALID_REQUEST',
            'message': 'event_ids must be a non-empty array'
        }), 400
    
    logger.info(f"User {user_id} marking {len(event_ids)} events as read")
    
    count = EventLogger.mark_events_read(event_ids, user_id)
    
    return jsonify({
        'success': True,
        'marked_read': count,
        'message': f'Marked {count} events as read'
    }), 200


def _format_time_ago(timestamp):
    """Format timestamp as human-readable 'time ago' string"""
    if not timestamp:
        return 'unknown'
    
    now = datetime.utcnow()
    if timestamp.tzinfo is not None:
        timestamp = timestamp.replace(tzinfo=None)
    
    diff = now - timestamp
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return 'just now'
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f'{minutes} minute{"s" if minutes != 1 else ""} ago'
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f'{hours} hour{"s" if hours != 1 else ""} ago'
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f'{days} day{"s" if days != 1 else ""} ago'
    else:
        weeks = int(seconds / 604800)
        return f'{weeks} week{"s" if weeks != 1 else ""} ago'
