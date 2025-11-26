"""
Whiteboard API Routes (V2)
============================
RESTful endpoints for collaborative whiteboard operations

Phase 1: Foundation (Week 2)
- 24 endpoint stubs created
- Authentication required
- Consistent V2 response format

Author: GitHub Copilot
Date: November 3, 2025
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import logging
import jwt
import json
import os
import hashlib
from datetime import datetime
import psycopg2.extras

from app.database.connection import get_db_connection, return_db_connection
from app.utils.event_logger import EventLogger

logger = logging.getLogger(__name__)

# Create blueprint
whiteboard_bp = Blueprint('whiteboard_v2', __name__, url_prefix='/api/v2/whiteboard')


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def get_jwt_secret():
    """Get JWT secret key (consistent with auth.py)"""
    jwt_secret = os.getenv('JWT_SECRET_KEY')
    if not jwt_secret:
        database_url = os.getenv('DATABASE_URL', '')
        if database_url:
            jwt_secret = hashlib.sha256(database_url.encode()).hexdigest()
        else:
            jwt_secret = 'dev-secret-key-for-local-testing-only'
    return jwt_secret


def jwt_required_v2(f):
    """
    Decorator to require valid JWT token
    Adds request.user_id to request context
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'error': 'UNAUTHORIZED',
                'message': 'Missing or invalid Authorization header'
            }), 401
        
        token = auth_header.split(' ')[1]
        
        try:
            jwt_secret = get_jwt_secret()
            payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
            user_id = payload.get('sub')
            
            if not user_id:
                return jsonify({
                    'success': False,
                    'error': 'INVALID_TOKEN',
                    'message': 'Invalid token payload'
                }), 401
            
            # Add user_id to request context
            request.user_id = user_id
            
            return f(*args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'error': 'TOKEN_EXPIRED',
                'message': 'Token has expired'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'error': 'INVALID_TOKEN',
                'message': 'Invalid token'
            }), 401
    
    return decorated_function


def handle_errors(f):
    """Decorator to handle errors consistently"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}", exc_info=True)
            return jsonify({
                'success': False,
                'error': 'SERVER_ERROR',
                'message': 'Internal server error'
            }), 500
    return decorated_function


# =====================================================
# WHITEBOARD CRUD ENDPOINTS (5)
# =====================================================

@whiteboard_bp.route('/h/<int:hid>', methods=['GET'])
@jwt_required_v2
@handle_errors
def get_household_whiteboards(hid):
    """
    Get all whiteboards for household
    
    GET /api/v2/whiteboard/h/1
    Returns: List of whiteboards for household 1
    
    Phase 1 Week 4: Real database implementation with compact schema (wb)
    """
    user_id = request.user_id
    
    logger.info(f"User {user_id} requesting whiteboards for household {hid}")
    
    # Get database connection
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        # Query whiteboards for household (not deleted) - using compact schema
        cursor.execute("""
            SELECT 
                id,
                hid,
                n,
                d,
                tt,
                cs,
                ca,
                ua,
                laa,
                cby,
                (SELECT COUNT(*) FROM wbo WHERE wid = wb.id AND deleted_at IS NULL) as object_count
            FROM wb
            WHERE hid = %s
              AND deleted_at IS NULL
            ORDER BY laa DESC
        """, (hid,))
        
        rows = cursor.fetchall()
        
        # Convert to dict list
        whiteboards = []
        for row in rows:
            # Parse canvas settings from JSONB
            try:
                canvas_data = row['cs'] if row.get('cs') else {}
            except (KeyError, IndexError, TypeError):
                canvas_data = {}
            
            viewport = canvas_data.get('vp', [0, 0, 1.0]) if isinstance(canvas_data, dict) else [0, 0, 1.0]
            
            whiteboards.append({
                'id': row['id'],
                'household_id': row['hid'],
                'name': row['n'],
                'description': row['d'],
                'template_type': row['tt'],
                'canvas_width': 3000,  # Default for now
                'canvas_height': 2000,  # Default for now
                'zoom_level': float(viewport[2]) if isinstance(viewport, list) and len(viewport) > 2 else 1.0,
                'created_at': row['ca'].isoformat() if row.get('ca') else None,
                'updated_at': row['ua'].isoformat() if row.get('ua') else None,
                'last_activity_at': row['laa'].isoformat() if row.get('laa') else None,
                'created_by': row['cby'],
                'object_count': row['object_count']
            })
        
        logger.info(f"Found {len(whiteboards)} whiteboards for household {hid}")
        
        return jsonify({
            'success': True,
            'data': {
                'whiteboards': whiteboards,
                'household_id': hid,
                'count': len(whiteboards)
            }
        }), 200
        
    finally:
        cursor.close()
        return_db_connection(conn)


@whiteboard_bp.route('', methods=['POST'], strict_slashes=False)
@jwt_required_v2
@handle_errors
def create_whiteboard():
    """
    Create new whiteboard
    
    POST /api/v2/whiteboard
    Body: {household_id, name, description, template_type}
    Returns: Created whiteboard object
    
    Phase 1 Week 4: Real database implementation with compact schema (wb)
    """
    user_id = request.user_id
    data = request.get_json()
    
    logger.info(f"User {user_id} creating whiteboard: {data.get('name')}")
    
    # Validate required fields
    if not data.get('household_id'):
        return jsonify({
            'success': False,
            'error': 'VALIDATION_ERROR',
            'message': 'household_id is required'
        }), 400
    
    if not data.get('name'):
        return jsonify({
            'success': False,
            'error': 'VALIDATION_ERROR',
            'message': 'name is required'
        }), 400
    
    # Get database connection
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        # Insert new whiteboard using compact schema
        cursor.execute("""
            INSERT INTO wb (
                hid,
                n,
                d,
                tt,
                cby
            ) VALUES (%s, %s, %s, %s, %s)
            RETURNING 
                id,
                hid,
                n,
                d,
                tt,
                cs,
                ca,
                ua,
                laa,
                cby
        """, (
            data.get('household_id'),
            data.get('name'),
            data.get('description'),
            data.get('template_type', 'freeform'),
            user_id
        ))
        
        row = cursor.fetchone()
        conn.commit()
        
        # Parse canvas settings
        try:
            canvas_data = row['cs'] if row.get('cs') else {}
        except (KeyError, TypeError, AttributeError):
            canvas_data = {}
            
        viewport = canvas_data.get('vp', [0, 0, 1.0]) if isinstance(canvas_data, dict) else [0, 0, 1.0]
        
        # Build response using column names (not indices)
        whiteboard = {
            'id': row['id'],
            'household_id': row['hid'],
            'name': row['n'],
            'description': row['d'],
            'template_type': row['tt'],
            'canvas_width': 3000,
            'canvas_height': 2000,
            'zoom_level': float(viewport[2]) if isinstance(viewport, list) and len(viewport) > 2 else 1.0,
            'created_at': row['ca'].isoformat() if row.get('ca') else None,
            'updated_at': row['ua'].isoformat() if row.get('ua') else None,
            'last_activity_at': row['laa'].isoformat() if row.get('laa') else None,
            'created_by': row['cby'],
            'object_count': 0
        }
        
        logger.info(f"Created whiteboard {whiteboard['id']}: {whiteboard['name']}")
        
        # Log activity event
        try:
            from app.utils.event_logger import EventLogger
            EventLogger.log_event(
                household_id=row['hid'],
                user_id=user_id,
                event_type='whiteboard.created',
                resource_type='whiteboard',
                resource_id=whiteboard['id'],
                event_data={
                    'whiteboard_name': whiteboard['name'],
                    'description': whiteboard.get('description'),
                    'template_type': whiteboard.get('template_type')
                },
                title=whiteboard['name']
            )
        except Exception as e:
            logger.warning(f"Failed to log whiteboard creation event: {e}")
        
        return jsonify({
            'success': True,
            'data': {
                'whiteboard': whiteboard
            }
        }), 201
        
    finally:
        cursor.close()
        return_db_connection(conn)


@whiteboard_bp.route('/<int:wid>', methods=['GET'])
@jwt_required_v2
@handle_errors
def get_whiteboard(wid):
    """
    Get whiteboard details with objects
    
    GET /api/v2/whiteboard/123
    Returns: Whiteboard metadata + objects array
    
    Phase 1 Week 4: Real database implementation with compact schema (wb/wbo)
    """
    user_id = request.user_id
    
    logger.info(f"User {user_id} requesting whiteboard {wid}")
    
    # Get database connection
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        # Get whiteboard metadata using compact schema
        cursor.execute("""
            SELECT 
                id,
                hid,
                n,
                d,
                tt,
                cs,
                ca,
                ua,
                laa,
                cby
            FROM wb
            WHERE id = %s AND deleted_at IS NULL
        """, (wid,))
        
        row = cursor.fetchone()
        
        if not row:
            return jsonify({
                'success': False,
                'error': 'NOT_FOUND',
                'message': f'Whiteboard {wid} not found'
            }), 404
        
        # Parse canvas settings
        canvas_data = row.get('cs') or {}
        viewport = canvas_data.get('vp', [0, 0, 1.0]) if isinstance(canvas_data, dict) else [0, 0, 1.0]
        
        # Build whiteboard object
        whiteboard = {
            'id': row['id'],
            'household_id': row['hid'],
            'name': row['n'],
            'description': row['d'],
            'template_type': row['tt'],
            'canvas_width': 3000,
            'canvas_height': 2000,
            'zoom_level': float(viewport[2]) if isinstance(viewport, list) and len(viewport) > 2 else 1.0,
            'created_at': row['ca'].isoformat() if row.get('ca') else None,
            'updated_at': row['ua'].isoformat() if row.get('ua') else None,
            'last_activity_at': row['laa'].isoformat() if row.get('laa') else None,
            'created_by': row['cby']
        }
        
        # Get all objects for this whiteboard using compact schema
        cursor.execute("""
            SELECT 
                wbo.id,
                wbo.t,
                wbo.rid,
                wbo.gid,
                wbo.mid,
                wbo.p,
                wbo.c,
                wbo.s,
                wbo.tags,
                wbo.ca,
                wbo.cby,
                u.name as created_by_name,
                u.email as created_by_email
            FROM wbo
            LEFT JOIN users u ON wbo.cby = u.id
            WHERE wbo.wid = %s AND wbo.deleted_at IS NULL
            ORDER BY (wbo.p->>4)::int ASC, wbo.id ASC
        """, (wid,))
        
        objects = []
        for obj_row in cursor.fetchall():
            # Determine entity_type and entity_id from compact columns
            entity_type = None
            entity_id = None
            if obj_row.get('rid'):
                entity_type = 'recipe'
                entity_id = obj_row['rid']
            elif obj_row.get('gid'):
                entity_type = 'grocery_list'
                entity_id = obj_row['gid']
            elif obj_row.get('mid'):
                entity_type = 'meal_plan'
                entity_id = obj_row['mid']
            
            # Parse position JSONB array
            pos = obj_row.get('p') or [0, 0, 300, 400, 0]
            
            objects.append({
                'id': obj_row['id'],
                'type': obj_row['t'],  # Database type: 'rc', 'note', 'list', 'container', etc.
                'object_type': obj_row['t'],  # Alias for backward compatibility
                'entity_type': entity_type,
                'entity_id': entity_id,
                'position': {
                    'x': float(pos[0]) if len(pos) > 0 else 0,
                    'y': float(pos[1]) if len(pos) > 1 else 0,
                    'width': float(pos[2]) if len(pos) > 2 else 300,
                    'height': float(pos[3]) if len(pos) > 3 else 400,
                    'z_index': int(pos[4]) if len(pos) > 4 else 0
                },
                'content': obj_row.get('c'),
                'style': obj_row.get('s'),
                'tags': obj_row.get('tags') or [],
                'created_at': obj_row['ca'].isoformat() if obj_row.get('ca') else None,
                'created_by': obj_row['cby'],
                'created_by_name': obj_row.get('created_by_name'),
                'created_by_email': obj_row.get('created_by_email')
            })
        
        whiteboard['objects'] = objects
        whiteboard['object_count'] = len(objects)
        
        logger.info(f"Loaded whiteboard {wid} with {len(objects)} objects")
        
        return jsonify({
            'success': True,
            'data': {
                'whiteboard': whiteboard
            }
        }), 200
        
    finally:
        cursor.close()
        return_db_connection(conn)


@whiteboard_bp.route('/<int:wid>', methods=['PATCH'])
@jwt_required_v2
@handle_errors
def update_whiteboard(wid):
    """
    Update whiteboard metadata
    
    PATCH /api/v2/whiteboard/123
    Body: {name, description, canvas_settings}
    Returns: Updated whiteboard object
    
    Phase 1: Stub implementation
    """
    user_id = request.user_id
    data = request.get_json()
    
    logger.info(f"User {user_id} updating whiteboard {wid}")
    
    # TODO Phase 1 Week 3: Implement database update
    return jsonify({
        'success': True,
        'data': {
            'whiteboard': {
                'id': wid,
                'updated_at': datetime.utcnow().isoformat(),
                '_stub': True
            }
        }
    }), 200


@whiteboard_bp.route('/<int:wid>', methods=['DELETE'])
@jwt_required_v2
@handle_errors
def delete_whiteboard(wid):
    """
    Soft delete whiteboard
    
    DELETE /api/v2/whiteboard/123
    Returns: Success with trash retention info
    """
    user_id = request.user_id
    
    logger.info(f"User {user_id} deleting whiteboard {wid}")
    
    # Get database connection
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        # Check whiteboard exists and user has access
        cursor.execute("""
            SELECT wb.id, wb.hid
            FROM wb
            WHERE wb.id = %s AND wb.deleted_at IS NULL
        """, (wid,))
        
        whiteboard = cursor.fetchone()
        
        if not whiteboard:
            return jsonify({
                'success': False,
                'error': 'NOT_FOUND',
                'message': 'Whiteboard not found'
            }), 404
        
        # Soft delete the whiteboard
        cursor.execute("""
            UPDATE wb
            SET deleted_at = NOW(),
                ua = NOW(),
                deleted_by = %s
            WHERE id = %s
        """, (user_id, wid))
        
        # CASCADE DELETE: Also soft delete related grocery lists
        cursor.execute("""
            UPDATE grocery_lists
            SET deleted_at = NOW()
            WHERE wid = %s AND deleted_at IS NULL
        """, (wid,))
        
        deleted_lists_count = cursor.rowcount
        
        # CASCADE DELETE: Also delete related meal plan containers (whiteboard objects)
        # Note: Meal plans in meal_plans table don't have wid, only whiteboard objects do
        cursor.execute("""
            UPDATE wbo
            SET deleted_at = NOW(),
                deleted_by = %s
            WHERE wid = %s AND deleted_at IS NULL
        """, (user_id, wid))
        
        deleted_objects_count = cursor.rowcount
        
        conn.commit()
        
        logger.info(f"Whiteboard {wid} soft deleted by user {user_id}")
        logger.info(f"CASCADE: Deleted {deleted_lists_count} grocery lists")
        logger.info(f"CASCADE: Deleted {deleted_objects_count} whiteboard objects")
        
        # Log activity event
        try:
            from app.utils.event_logger import EventLogger
            # Get whiteboard name before it's deleted
            cursor.execute("SELECT n FROM wb WHERE id = %s", (wid,))
            wb_row = cursor.fetchone()
            whiteboard_name = wb_row['n'] if wb_row else f"Whiteboard #{wid}"
            
            EventLogger.log_event(
                household_id=whiteboard['hid'],
                user_id=user_id,
                event_type='whiteboard.deleted',
                resource_type='whiteboard',
                resource_id=wid,
                event_data={
                    'whiteboard_name': whiteboard_name,
                    'deleted_objects_count': deleted_objects_count,
                    'deleted_lists_count': deleted_lists_count
                },
                title=whiteboard_name
            )
        except Exception as e:
            logger.warning(f"Failed to log whiteboard deletion event: {e}")
        
        return jsonify({
            'success': True,
            'data': {
                'message': 'Whiteboard moved to trash',
                'whiteboard_id': wid,
                'deleted_at': datetime.utcnow().isoformat(),
                'cascade_deleted': {
                    'grocery_lists': deleted_lists_count,
                    'objects': deleted_objects_count
                }
            }
        }), 200
        
    finally:
        cursor.close()
        return_db_connection(conn)


# =====================================================
# OBJECT MANAGEMENT ENDPOINTS (7)
# =====================================================

@whiteboard_bp.route('/<int:wid>/o', methods=['POST'])
@jwt_required_v2
@handle_errors
def create_object(wid):
    """
    Create object on whiteboard
    
    POST /api/v2/whiteboard/123/o
    Body: {type, entity_type?, entity_id?, position, content?, tags?}
    Returns: Created object
    """
    user_id = request.user_id
    data = request.get_json()
    
    logger.info(f"User {user_id} creating object on whiteboard {wid}")
    logger.info(f"Object data: {data}")
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        # Verify whiteboard exists and user has access
        cursor.execute("""
            SELECT wb.id, wb.hid
            FROM wb
            JOIN household_members hm ON wb.hid = hm.household_id
            WHERE wb.id = %s AND hm.user_id = %s AND wb.deleted_at IS NULL
        """, (wid, user_id))
        
        whiteboard = cursor.fetchone()
        if not whiteboard:
            return jsonify({'success': False, 'error': 'Whiteboard not found or access denied'}), 404
        
        # Extract object data
        obj_type = data.get('type', 'rc')  # Default to recipe card (matches DB constraint)
        entity_type = data.get('entity_type')
        entity_id = data.get('entity_id')
        position = data.get('position', [0, 0, 300, 400, 0])
        content = data.get('content', {})
        tags = data.get('tags') or []
        
        # Ensure position is a list of 5 elements
        if not isinstance(position, list) or len(position) != 5:
            position = [0, 0, 300, 400, 0]
        
        # Map entity_type to proper column
        rid = entity_id if entity_type == 'recipe' else None
        gid = entity_id if entity_type == 'grocery_list' else None
        mid = entity_id if entity_type == 'meal_plan' else None
        
        # Insert object
        cursor.execute("""
            INSERT INTO wbo (wid, t, rid, gid, mid, p, c, tags, cby, ca, ua)
            VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING id, wid, t as type, rid, gid, mid, p as position, c as content, tags, ca as created_at
        """, (wid, obj_type, rid, gid, mid, json.dumps(position), json.dumps(content), tags, user_id))
        
        obj = cursor.fetchone()
        conn.commit()
        
        logger.info(f"✅ Created object {obj['id']} on whiteboard {wid}")
        
        # Log activity event based on object type
        try:
            from app.utils.event_logger import EventLogger
            
            # Get whiteboard name
            cursor.execute("SELECT n FROM wb WHERE id = %s", (wid,))
            wb_row = cursor.fetchone()
            whiteboard_name = wb_row['n'] if wb_row else f"Whiteboard #{wid}"
            
            event_data = {
                'whiteboard_id': wid,
                'whiteboard_name': whiteboard_name,
                'object_id': obj['id']
            }
            
            # Determine event type and get resource details
            if obj['rid']:  # Recipe added
                cursor.execute("SELECT title FROM recipes WHERE id = %s", (obj['rid'],))
                recipe = cursor.fetchone()
                recipe_title = recipe['title'] if recipe else f"Recipe #{obj['rid']}"
                
                event_data['recipe_title'] = recipe_title
                event_data['recipe_id'] = obj['rid']
                
                EventLogger.log_event(
                    household_id=whiteboard['hid'],
                    user_id=user_id,
                    event_type='whiteboard.recipe_added',
                    resource_type='recipe',
                    resource_id=obj['rid'],
                    event_data=event_data,
                    title=recipe_title
                )
            elif obj_type == 'note':  # Note added (database stores as 'note', not 'nt')
                note_preview = content.get('html', '')[:100] if isinstance(content, dict) else ''
                event_data['note_preview'] = note_preview
                
                EventLogger.log_event(
                    household_id=whiteboard['hid'],
                    user_id=user_id,
                    event_type='whiteboard.note_added',
                    resource_type='note',
                    resource_id=obj['id'],
                    event_data=event_data,
                    title=f"Note on {whiteboard_name}",
                    description=f"added a note to the whiteboard"
                )
            elif obj['gid']:  # Grocery list added
                cursor.execute("SELECT name FROM grocery_lists WHERE id = %s", (obj['gid'],))
                gl = cursor.fetchone()
                list_name = gl['name'] if gl else f"List #{obj['gid']}"
                
                event_data['list_name'] = list_name
                
                EventLogger.log_event(
                    household_id=whiteboard['hid'],
                    user_id=user_id,
                    event_type='whiteboard.grocery_added',
                    resource_type='grocery_list',
                    resource_id=obj['gid'],
                    event_data=event_data,
                    title=list_name
                )
            elif obj['mid']:  # Meal plan added
                cursor.execute("SELECT name FROM meal_plans WHERE id = %s", (obj['mid'],))
                mp = cursor.fetchone()
                plan_name = mp['name'] if mp else f"Meal Plan #{obj['mid']}"
                
                event_data['plan_name'] = plan_name
                
                EventLogger.log_event(
                    household_id=whiteboard['hid'],
                    user_id=user_id,
                    event_type='whiteboard.mealplan_added',
                    resource_type='meal_plan',
                    resource_id=obj['mid'],
                    event_data=event_data,
                    title=plan_name
                )
        except Exception as e:
            logger.warning(f"Failed to log object creation event: {e}")
        
        # Build response with entity_type for consistency
        entity_type_response = None
        entity_id_response = None
        
        if obj['rid']:
            entity_type_response = 'recipe'
            entity_id_response = obj['rid']
        elif obj['gid']:
            entity_type_response = 'grocery_list'
            entity_id_response = obj['gid']
        elif obj['mid']:
            entity_type_response = 'meal_plan'
            entity_id_response = obj['mid']
        
        return jsonify({
            'success': True,
            'data': {
                'id': obj['id'],
                'whiteboard_id': obj['wid'],
                'type': obj['type'],
                'entity_type': entity_type_response,
                'entity_id': entity_id_response,
                'rid': obj['rid'],
                'gid': obj['gid'],
                'mid': obj['mid'],
                'position': obj['position'],
                'content': obj['content'],
                'tags': obj['tags'],
                'created_at': obj['created_at'].isoformat() if obj.get('created_at') else None
            }
        }), 201
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating object: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cursor.close()
        return_db_connection(conn)


@whiteboard_bp.route('/<int:wid>/o/<int:oid>', methods=['PATCH'])
@jwt_required_v2
@handle_errors
def update_object(wid, oid):
    """
    Update object (position, style, tags, content)
    
    PATCH /api/v2/whiteboard/123/o/1001
    Body: {position?, style?, tags?, content?}
    Returns: Updated object
    """
    user_id = request.user_id
    data = request.get_json()
    
    logger.info(f"User {user_id} updating object {oid} on whiteboard {wid}")
    logger.info(f"Update data: {data}")
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        # Verify object exists and user has access
        cursor.execute("""
            SELECT wbo.id, wbo.wid, wb.hid
            FROM wbo
            JOIN wb ON wbo.wid = wb.id
            JOIN household_members hm ON wb.hid = hm.household_id
            WHERE wbo.id = %s AND wbo.wid = %s AND hm.user_id = %s AND wbo.deleted_at IS NULL
        """, (oid, wid, user_id))
        
        obj = cursor.fetchone()
        if not obj:
            return jsonify({'success': False, 'error': 'Object not found or access denied'}), 404
        
        # Build UPDATE query dynamically based on provided fields
        update_fields = []
        update_values = []
        
        if 'position' in data:
            position = data['position']
            # Convert object to array if needed
            if isinstance(position, dict):
                pos_array = [
                    position.get('x', 0),
                    position.get('y', 0),
                    position.get('width', 300),
                    position.get('height', 400),
                    position.get('z', 0) or position.get('z_index', 0)
                ]
            else:
                pos_array = position
            update_fields.append('p = %s::jsonb')
            update_values.append(json.dumps(pos_array))
        
        if 'style' in data:
            update_fields.append('s = %s::jsonb')
            update_values.append(json.dumps(data['style']))
        
        if 'tags' in data:
            update_fields.append('tags = %s')
            update_values.append(data['tags'] or [])
        
        if 'content' in data:
            update_fields.append('c = %s::jsonb')
            update_values.append(json.dumps(data['content']))
        
        if not update_fields:
            return jsonify({'success': False, 'error': 'No fields to update'}), 400
        
        # Always update ua (updated_at)
        update_fields.append('ua = CURRENT_TIMESTAMP')
        
        # Execute update
        update_query = f"""
            UPDATE wbo
            SET {', '.join(update_fields)}
            WHERE id = %s
            RETURNING id, wid, t as type, rid, gid, mid, p as position, s as style, tags, c as content, ua as updated_at
        """
        
        update_values.append(oid)
        cursor.execute(update_query, update_values)
        
        updated_obj = cursor.fetchone()
        conn.commit()
        
        logger.info(f"✅ Updated object {oid} on whiteboard {wid}")
        
        # Note: Removed event logging for updates to avoid spam from auto-save
        # Only log creation and deletion events
        
        # Build response with entity_type for consistency
        entity_type_response = None
        entity_id_response = None
        
        if updated_obj['rid']:
            entity_type_response = 'recipe'
            entity_id_response = updated_obj['rid']
        elif updated_obj['gid']:
            entity_type_response = 'grocery_list'
            entity_id_response = updated_obj['gid']
        elif updated_obj['mid']:
            entity_type_response = 'meal_plan'
            entity_id_response = updated_obj['mid']
        
        return jsonify({
            'success': True,
            'data': {
                'id': updated_obj['id'],
                'whiteboard_id': updated_obj['wid'],
                'type': updated_obj['type'],
                'entity_type': entity_type_response,
                'entity_id': entity_id_response,
                'position': updated_obj['position'],
                'style': updated_obj['style'],
                'tags': updated_obj['tags'],
                'content': updated_obj['content'],
                'updated_at': updated_obj['updated_at'].isoformat() if updated_obj.get('updated_at') else None
            }
        }), 200
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error updating object: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cursor.close()
        return_db_connection(conn)


@whiteboard_bp.route('/<int:wid>/o/<int:oid>', methods=['DELETE'])
@jwt_required_v2
@handle_errors
def delete_object(wid, oid):
    """
    Delete object from whiteboard (soft delete)
    
    DELETE /api/v2/whiteboard/123/o/1001
    Returns: Success confirmation
    
    Phase 2: Full implementation - soft delete object
    """
    user_id = request.user_id
    
    logger.info(f"User {user_id} deleting object {oid} from whiteboard {wid}")
    
    # Get database connection
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        # Get object info before deleting for event logging
        cursor.execute("""
            SELECT wbo.id, wbo.t, wbo.rid, wbo.gid, wbo.mid, wb.hid, wb.n as whiteboard_name
            FROM wbo
            JOIN wb ON wbo.wid = wb.id
            WHERE wbo.id = %s AND wbo.wid = %s AND wbo.deleted_at IS NULL
        """, (oid, wid))
        
        obj = cursor.fetchone()
        
        if not obj:
            return jsonify({
                'success': False,
                'error': 'NOT_FOUND',
                'message': f'Object {oid} not found on whiteboard {wid}'
            }), 404
        
        # Soft delete the object
        cursor.execute("""
            UPDATE wbo
            SET deleted_at = CURRENT_TIMESTAMP
            WHERE id = %s AND wid = %s AND deleted_at IS NULL
            RETURNING id
        """, (oid, wid))
        
        deleted = cursor.fetchone()
        
        # Update whiteboard's last_activity_at
        cursor.execute("""
            UPDATE wb
            SET laa = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (wid,))
        
        conn.commit()
        
        logger.info(f"Deleted object {oid} from whiteboard {wid}")
        
        # Log activity event
        try:
            object_type = obj['t']
            object_description = f"{object_type} object"
            event_type_map = {
                'rc': 'whiteboard.recipe_removed',
                'nt': 'whiteboard.note_deleted',
                'gl': 'whiteboard.grocery_deleted',
                'mp': 'whiteboard.mealplan_deleted'
            }
            event_type = event_type_map.get(object_type, 'whiteboard.object_deleted')
            
            # Get more detailed description
            if obj['rid']:
                # Get recipe title
                cursor.execute("SELECT title FROM recipes WHERE id = %s", (obj['rid'],))
                recipe = cursor.fetchone()
                object_description = recipe['title'] if recipe else f"recipe #{obj['rid']}"
            elif obj['gid']:
                object_description = f"grocery list #{obj['gid']}"
            elif obj['mid']:
                object_description = f"meal plan #{obj['mid']}"
            
            EventLogger.log_event(
                household_id=obj['hid'],
                user_id=user_id,
                event_type=event_type,
                resource_type=object_type,
                resource_id=oid,
                event_data={
                    'whiteboard_id': wid,
                    'whiteboard_name': obj['whiteboard_name'],
                    'resource_title': object_description
                },
                title=object_description,
                description=f"removed {object_description} from the whiteboard"
            )
        except Exception as e:
            logger.warning(f"Failed to log object deletion event: {e}")
        
        return jsonify({
            'success': True,
            'data': {
                'message': 'Object deleted',
                'object_id': oid
            }
        }), 200
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error deleting object: {str(e)}", exc_info=True)
        raise
    finally:
        cursor.close()
        return_db_connection(conn)


@whiteboard_bp.route('/<int:wid>/o/bulk', methods=['PATCH'])
@jwt_required_v2
@handle_errors
def bulk_update_objects(wid):
    """
    Bulk update/insert object positions (drag multiple)
    
    PATCH /api/v2/whiteboard/123/o/bulk
    Body: {objects: [{recipe_id, position}, ...]}
    Returns: Success confirmation with created/updated counts
    
    Phase 2: Full implementation - upserts objects with positions
    """
    user_id = request.user_id
    data = request.get_json()
    objects = data.get('objects', [])
    
    if not objects:
        return jsonify({
            'success': False,
            'error': 'VALIDATION_ERROR',
            'message': 'objects array is required'
        }), 400
    
    logger.info(f"User {user_id} bulk saving {len(objects)} objects on whiteboard {wid}")
    
    # Get database connection
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        # Get whiteboard info for household_id
        cursor.execute("""
            SELECT hid FROM wb WHERE id = %s
        """, (wid,))
        whiteboard = cursor.fetchone()
        
        if not whiteboard:
            return jsonify({
                'success': False,
                'error': 'NOT_FOUND',
                'message': 'Whiteboard not found'
            }), 404
        
        household_id = whiteboard['hid']
        
        created_count = 0
        updated_count = 0
        new_recipe_ids = []  # Track newly added recipes for event logging
        tagged_recipes = []  # Track recipes that had tags added/changed
        
        # Process each object
        for obj in objects:
            object_id = obj.get('object_id')  # Get object_id if provided
            recipe_id = obj.get('recipe_id')
            position = obj.get('position', {})
            tags = obj.get('tags', [])  # Get tags array
            
            if not recipe_id:
                continue  # Skip objects without recipe_id
            
            # Build position JSONB array: [x, y, width, height, z_index]
            pos_array = [
                float(position.get('x', 0)),
                float(position.get('y', 0)),
                float(position.get('width', 300)),
                float(position.get('height', 400)),
                int(position.get('z', 0))
            ]
            
            # Check if object already exists (prefer object_id, fallback to rid match)
            if object_id:
                cursor.execute("""
                    SELECT id, tags FROM wbo
                    WHERE id = %s AND wid = %s AND deleted_at IS NULL
                """, (object_id, wid))
            else:
                cursor.execute("""
                    SELECT id, tags FROM wbo
                    WHERE wid = %s AND rid = %s AND deleted_at IS NULL
                """, (wid, recipe_id))
            
            existing = cursor.fetchone()
            
            if existing:
                # Check if tags changed
                existing_tags = existing['tags'] or []
                if set(tags) != set(existing_tags) and tags:  # Only if tags were added/changed
                    tagged_recipes.append(recipe_id)
                
                # Update existing object position and tags
                cursor.execute("""
                    UPDATE wbo
                    SET p = %s::jsonb,
                        tags = %s,
                        ua = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (
                    psycopg2.extras.Json(pos_array),
                    tags,
                    existing['id']
                ))
                updated_count += 1
                logger.debug(f"Updated object {existing['id']} for recipe {recipe_id}")
            else:
                # Insert new object with tags
                cursor.execute("""
                    INSERT INTO wbo (
                        wid,
                        t,
                        rid,
                        p,
                        tags,
                        cby
                    ) VALUES (%s, %s, %s, %s::jsonb, %s, %s)
                    RETURNING id
                """, (
                    wid,
                    'rc',  # recipe card type
                    recipe_id,
                    psycopg2.extras.Json(pos_array),
                    tags,
                    user_id
                ))
                new_object = cursor.fetchone()
                created_count += 1
                new_recipe_ids.append(recipe_id)  # Track for event logging
                logger.debug(f"Created new object {new_object['id']} for recipe {recipe_id}")
        
        # Update whiteboard's last_activity_at
        cursor.execute("""
            UPDATE wb
            SET laa = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (wid,))
        
        # Commit all changes
        conn.commit()
        
        logger.info(f"Bulk save complete: {created_count} created, {updated_count} updated")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error in bulk_update_objects: {str(e)}", exc_info=True)
        raise
    finally:
        cursor.close()
        return_db_connection(conn)
    
    # Log activity events for newly added recipes (after connection is closed)
    if new_recipe_ids and household_id:
        for recipe_id in new_recipe_ids:
            try:
                # Get recipe title for event - use new connection
                event_conn = get_db_connection()
                event_cursor = event_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                
                event_cursor.execute("""
                    SELECT title FROM recipes WHERE id = %s
                """, (recipe_id,))
                recipe = event_cursor.fetchone()
                recipe_title = recipe['title'] if recipe else f"Recipe #{recipe_id}"
                
                event_cursor.close()
                return_db_connection(event_conn)
                
                # Log event
                EventLogger.log_event(
                    household_id=household_id,
                    user_id=int(user_id),
                    event_type='whiteboard.recipe_added',
                    resource_type='recipe',
                    resource_id=recipe_id,
                    event_data={
                        'recipe_title': recipe_title,
                        'whiteboard_id': wid
                    },
                    title=recipe_title,
                    description=f"added {recipe_title} to the whiteboard"
                )
                logger.info(f"📝 Logged activity event for recipe {recipe_id}")
            except Exception as e:
                logger.warning(f"Failed to log activity event for recipe {recipe_id}: {e}")
    
    # Log activity events for tagged recipes
    if tagged_recipes and household_id:
        for recipe_id in tagged_recipes:
            try:
                # Get recipe title for event - use new connection
                event_conn = get_db_connection()
                event_cursor = event_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                
                event_cursor.execute("""
                    SELECT title FROM recipes WHERE id = %s
                """, (recipe_id,))
                recipe = event_cursor.fetchone()
                recipe_title = recipe['title'] if recipe else f"Recipe #{recipe_id}"
                
                event_cursor.close()
                return_db_connection(event_conn)
                
                # Log event
                EventLogger.log_event(
                    household_id=household_id,
                    user_id=int(user_id),
                    event_type='whiteboard.recipe_tagged',
                    resource_type='recipe',
                    resource_id=recipe_id,
                    event_data={
                        'recipe_title': recipe_title,
                        'whiteboard_id': wid
                    },
                    title=recipe_title,
                    description=f"tagged {recipe_title} in the whiteboard"
                )
                logger.info(f"🏷️ Logged tag event for recipe {recipe_id}")
            except Exception as e:
                logger.warning(f"Failed to log tag event for recipe {recipe_id}: {e}")
    
    return jsonify({
        'success': True,
        'data': {
            'created_count': created_count,
            'updated_count': updated_count,
            'total_processed': created_count + updated_count,
            'whiteboard_id': wid
        }
    }), 200


@whiteboard_bp.route('/<int:wid>/o/<int:oid>/link', methods=['POST'])
@jwt_required_v2
@handle_errors
def link_object_to_entity(wid, oid):
    """
    Link object to recipe/grocery/meal plan
    
    POST /api/v2/whiteboard/123/o/1001/link
    Body: {entity_type: 'recipe', entity_id: 2577}
    Returns: Updated object with link
    
    Phase 1: Stub implementation
    """
    user_id = request.user_id
    data = request.get_json()
    
    logger.info(f"User {user_id} linking object {oid} to {data.get('entity_type')} {data.get('entity_id')}")
    
    # TODO Phase 3: Implement entity linking
    return jsonify({
        'success': True,
        'data': {
            'object': {
                'id': oid,
                'entity_type': data.get('entity_type'),
                'entity_id': data.get('entity_id'),
                '_stub': True
            }
        }
    }), 200


@whiteboard_bp.route('/<int:wid>/o/<int:oid>/sync', methods=['POST'])
@jwt_required_v2
@handle_errors
def sync_object_from_source(wid, oid):
    """
    Sync object data from linked entity
    
    POST /api/v2/whiteboard/123/o/1001/sync
    Returns: Updated object with fresh data
    
    Phase 1: Stub implementation
    """
    user_id = request.user_id
    
    logger.info(f"User {user_id} syncing object {oid} from source")
    
    # TODO Phase 3: Implement sync from source entity
    return jsonify({
        'success': True,
        'data': {
            'object': {
                'id': oid,
                'synced_at': datetime.utcnow().isoformat(),
                '_stub': True
            }
        }
    }), 200


@whiteboard_bp.route('/<int:wid>/o/from-r/<int:rid>', methods=['POST'])
@jwt_required_v2
@handle_errors
def create_object_from_recipe(wid, rid):
    """
    Create recipe card from existing recipe
    
    POST /api/v2/whiteboard/123/o/from-r/2577
    Body: {position: [x, y, w, h, z]}
    Returns: Created recipe card object
    
    Phase 1: Stub implementation
    """
    user_id = request.user_id
    data = request.get_json()
    
    logger.info(f"User {user_id} creating recipe card from recipe {rid}")
    
    # TODO Phase 2: Implement recipe card creation
    return jsonify({
        'success': True,
        'data': {
            'object': {
                'id': 1002,
                'type': 'rc',
                'recipe_id': rid,
                'position': data.get('position', [100, 100, 300, 400, 1]),
                '_stub': True
            }
        }
    }), 201


# =====================================================
# COMMENT ENDPOINTS (5)
# =====================================================

@whiteboard_bp.route('/o/<int:oid>/cm', methods=['GET'])
@jwt_required_v2
@handle_errors
def get_comments(oid):
    """
    Get comments for whiteboard object
    
    GET /api/v2/whiteboard/o/1001/cm
    Returns: Threaded comments array with user info
    """
    user_id = request.user_id
    
    logger.info(f"User {user_id} fetching comments for object {oid}")
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        # Verify object exists and user has access
        cursor.execute("""
            SELECT wbo.id, wbo.wid, wb.hid
            FROM wbo
            JOIN wb ON wbo.wid = wb.id
            JOIN household_members hm ON wb.hid = hm.household_id
            WHERE wbo.id = %s AND hm.user_id = %s
        """, (oid, user_id))
        
        obj = cursor.fetchone()
        if not obj:
            return jsonify({
                'success': False,
                'error': 'Object not found or access denied'
            }), 404
        
        # Get comments with user info
        cursor.execute("""
            SELECT 
                wbc.id,
                wbc.oid,
                wbc.uid,
                wbc.txt,
                wbc.pid,
                wbc.td,
                wbc.rx,
                wbc.ca,
                wbc.ua,
                u.name,
                u.email
            FROM wbc
            LEFT JOIN users u ON wbc.uid = u.id
            WHERE wbc.oid = %s
            ORDER BY wbc.ca ASC
        """, (oid,))
        
        comments = cursor.fetchall()
        
        # Format comments
        formatted_comments = []
        for c in comments:
            formatted_comments.append({
                'id': c['id'],
                'object_id': c['oid'],
                'user_id': c['uid'],
                'user_name': c['name'] or 'Unknown',
                'un': c['name'] or 'Unknown',  # Alias for mobile
                'text': c['txt'],
                'txt': c['txt'],  # Alias for mobile
                'parent_id': c['pid'],
                'thread_depth': c['td'],
                'td': c['td'],  # Alias for mobile
                'reactions': c['rx'] or {},
                'rx': c['rx'] or {},  # Alias for mobile
                'created_at': c['ca'].isoformat() if c['ca'] else None,
                'ca': c['ca'].isoformat() if c['ca'] else None,  # Alias
                'updated_at': c['ua'].isoformat() if c['ua'] else None,
            })
        
        logger.info(f"✅ Fetched {len(formatted_comments)} comments for object {oid}")
        
        return jsonify({
            'success': True,
            'comments': formatted_comments,
            'count': len(formatted_comments)
        }), 200
        
    finally:
        cursor.close()
        return_db_connection(conn)


@whiteboard_bp.route('/o/<int:oid>/cm', methods=['POST'])
@jwt_required_v2
@handle_errors
def add_comment(oid):
    """
    Add comment to whiteboard object
    
    POST /api/v2/whiteboard/o/1001/cm
    Body: {text, parent_id?}
    Returns: Created comment with user info
    """
    user_id = request.user_id
    data = request.get_json()
    
    text = data.get('text', '').strip()
    parent_id = data.get('parent_id')
    
    if not text:
        return jsonify({
            'success': False,
            'error': 'Comment text is required'
        }), 400
    
    logger.info(f"User {user_id} adding comment to object {oid}")
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        # Verify object exists and user has access
        cursor.execute("""
            SELECT wbo.id, wbo.wid, wb.hid
            FROM wbo
            JOIN wb ON wbo.wid = wb.id
            JOIN household_members hm ON wb.hid = hm.household_id
            WHERE wbo.id = %s AND hm.user_id = %s
        """, (oid, user_id))
        
        obj = cursor.fetchone()
        if not obj:
            return jsonify({
                'success': False,
                'error': 'Object not found or access denied'
            }), 404
        
        # Calculate thread depth if replying
        thread_depth = 0
        if parent_id:
            cursor.execute("SELECT td FROM wbc WHERE id = %s", (parent_id,))
            parent = cursor.fetchone()
            if parent:
                thread_depth = parent['td'] + 1
        
        # Insert comment
        cursor.execute("""
            INSERT INTO wbc (oid, uid, txt, pid, td)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, oid, uid, txt, pid, td, rx, ca, ua
        """, (oid, user_id, text, parent_id, thread_depth))
        
        comment = cursor.fetchone()
        conn.commit()
        
        # Get user info
        cursor.execute("""
            SELECT id, name, email
            FROM users
            WHERE id = %s
        """, (user_id,))
        
        user = cursor.fetchone()
        
        # Format response
        comment_data = {
            'id': comment['id'],
            'object_id': comment['oid'],
            'user_id': comment['uid'],
            'user_name': user['name'] if user else 'Unknown',
            'text': comment['txt'],
            'txt': comment['txt'],  # Also include 'txt' for mobile compatibility
            'parent_id': comment['pid'],
            'thread_depth': comment['td'],
            'td': comment['td'],  # Also include 'td' for mobile compatibility
            'reactions': comment['rx'] or {},
            'rx': comment['rx'] or {},  # Also include 'rx' for mobile compatibility
            'created_at': comment['ca'].isoformat() if comment['ca'] else None,
            'ca': comment['ca'].isoformat() if comment['ca'] else None,
            'updated_at': comment['ua'].isoformat() if comment['ua'] else None,
        }
        
        logger.info(f"✅ Created comment {comment['id']} on object {oid}")
        
        # TODO: Broadcast via Pusher
        
        return jsonify({
            'success': True,
            'comment': comment_data
        }), 201
        
    finally:
        cursor.close()
        return_db_connection(conn)


@whiteboard_bp.route('/cm/<int:cid>', methods=['PATCH'])
@jwt_required_v2
@handle_errors
def update_comment(cid):
    """
    Update comment text
    
    PATCH /api/v2/whiteboard/cm/5001
    Body: {text}
    Returns: Updated comment
    
    Phase 1: Stub implementation
    """
    user_id = request.user_id
    data = request.get_json()
    
    logger.info(f"User {user_id} updating comment {cid}")
    
    # TODO Phase 4: Implement comment update
    return jsonify({
        'success': True,
        'data': {
            'comment': {
                'id': cid,
                'text': data.get('text'),
                'updated_at': datetime.utcnow().isoformat(),
                '_stub': True
            }
        }
    }), 200


@whiteboard_bp.route('/cm/<int:cid>', methods=['DELETE'])
@jwt_required_v2
@handle_errors
def delete_comment(cid):
    """
    Delete comment
    
    DELETE /api/v2/whiteboard/cm/5001
    Returns: Success confirmation
    
    Phase 1: Stub implementation
    """
    user_id = request.user_id
    
    logger.info(f"User {user_id} deleting comment {cid}")
    
    # TODO Phase 4: Implement comment deletion
    return jsonify({
        'success': True,
        'data': {
            'message': 'Comment deleted',
            'comment_id': cid,
            '_stub': True
        }
    }), 200


@whiteboard_bp.route('/cm/<int:cid>/rx', methods=['POST'])
@jwt_required_v2
@handle_errors
def add_reaction(cid):
    """
    Add or remove reaction to comment
    
    POST /api/v2/whiteboard/cm/5001/rx
    Body: {emoji: '👍'}
    Returns: Updated comment with reactions
    """
    user_id = request.user_id
    data = request.get_json()
    
    emoji = data.get('emoji', '').strip()
    if not emoji:
        return jsonify({
            'success': False,
            'error': 'Emoji is required'
        }), 400
    
    logger.info(f"User {user_id} adding reaction {emoji} to comment {cid}")
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        # Get current comment and verify access
        cursor.execute("""
            SELECT wbc.*, wbo.wid, wb.hid
            FROM wbc
            JOIN wbo ON wbc.oid = wbo.id
            JOIN wb ON wbo.wid = wb.id
            JOIN household_members hm ON wb.hid = hm.household_id
            WHERE wbc.id = %s AND hm.user_id = %s
        """, (cid, user_id))
        
        comment = cursor.fetchone()
        if not comment:
            return jsonify({
                'success': False,
                'error': 'Comment not found or access denied'
            }), 404
        
        # Get current reactions
        reactions = comment['rx'] or {}
        
        # Toggle reaction (add if not present, remove if present)
        if emoji in reactions:
            user_list = reactions[emoji]
            if user_id in user_list:
                # Remove reaction
                user_list.remove(user_id)
                if not user_list:
                    del reactions[emoji]
            else:
                # Add reaction
                user_list.append(user_id)
        else:
            # New emoji reaction
            reactions[emoji] = [user_id]
        
        # Update comment
        cursor.execute("""
            UPDATE wbc
            SET rx = %s, ua = NOW()
            WHERE id = %s
            RETURNING id, oid, uid, txt, pid, td, rx, ca, ua
        """, (json.dumps(reactions), cid))
        
        updated_comment = cursor.fetchone()
        conn.commit()
        
        # Get user info
        cursor.execute("SELECT name FROM users WHERE id = %s", (updated_comment['uid'],))
        user = cursor.fetchone()
        
        # Format response
        comment_data = {
            'id': updated_comment['id'],
            'object_id': updated_comment['oid'],
            'user_id': updated_comment['uid'],
            'user_name': user['name'] if user else 'Unknown',
            'text': updated_comment['txt'],
            'txt': updated_comment['txt'],
            'parent_id': updated_comment['pid'],
            'thread_depth': updated_comment['td'],
            'td': updated_comment['td'],
            'reactions': updated_comment['rx'] or {},
            'rx': updated_comment['rx'] or {},
            'created_at': updated_comment['ca'].isoformat() if updated_comment['ca'] else None,
            'ca': updated_comment['ca'].isoformat() if updated_comment['ca'] else None,
            'updated_at': updated_comment['ua'].isoformat() if updated_comment['ua'] else None,
        }
        
        logger.info(f"✅ Updated reactions on comment {cid}")
        
        return jsonify({
            'success': True,
            'comment': comment_data
        }), 200
        
    finally:
        cursor.close()
        return_db_connection(conn)


# =====================================================
# COLLABORATION ENDPOINTS (4)
# =====================================================

@whiteboard_bp.route('/<int:wid>/co', methods=['GET'])
@jwt_required_v2
@handle_errors
def get_collaborators(wid):
    """
    Get active collaborators on whiteboard
    
    GET /api/v2/whiteboard/123/co
    Returns: List of active users with presence
    
    Phase 1: Stub implementation
    """
    user_id = request.user_id
    
    logger.info(f"User {user_id} fetching collaborators for whiteboard {wid}")
    
    # TODO Phase 3: Implement collaborator fetching
    return jsonify({
        'success': True,
        'data': {
            'collaborators': [],
            'whiteboard_id': wid,
            '_stub': True
        }
    }), 200


@whiteboard_bp.route('/<int:wid>/pr', methods=['POST'])
@jwt_required_v2
@handle_errors
def update_presence(wid):
    """
    Update user presence on whiteboard
    
    POST /api/v2/whiteboard/123/pr
    Body: {is_active, current_object_id?, activity_status?}
    Returns: Updated presence
    
    Phase 1: Stub implementation
    """
    user_id = request.user_id
    data = request.get_json()
    
    logger.info(f"User {user_id} updating presence on whiteboard {wid}")
    
    # TODO Phase 3: Implement presence updates
    return jsonify({
        'success': True,
        'data': {
            'user_id': user_id,
            'whiteboard_id': wid,
            'is_active': data.get('is_active', True),
            '_stub': True
        }
    }), 200


@whiteboard_bp.route('/<int:wid>/h', methods=['GET'])
@jwt_required_v2
@handle_errors
def get_history(wid):
    """
    Get activity history for whiteboard
    
    GET /api/v2/whiteboard/123/h?limit=20
    Returns: Event log (chronological)
    
    Phase 1: Stub implementation
    """
    user_id = request.user_id
    limit = request.args.get('limit', 20, type=int)
    
    logger.info(f"User {user_id} fetching history for whiteboard {wid}")
    
    # TODO Phase 3: Implement event log fetching
    return jsonify({
        'success': True,
        'data': {
            'events': [],
            'whiteboard_id': wid,
            'limit': limit,
            '_stub': True
        }
    }), 200


@whiteboard_bp.route('/<int:wid>/restore', methods=['POST'])
@jwt_required_v2
@handle_errors
def restore_whiteboard(wid):
    """
    Restore whiteboard from trash
    
    POST /api/v2/whiteboard/123/restore
    Returns: Restored whiteboard
    
    Phase 1: Stub implementation
    """
    user_id = request.user_id
    
    logger.info(f"User {user_id} restoring whiteboard {wid} from trash")
    
    # TODO Phase 1 Week 3: Implement restore
    return jsonify({
        'success': True,
        'data': {
            'whiteboard': {
                'id': wid,
                'restored_at': datetime.utcnow().isoformat(),
                'restored_by': user_id,
                '_stub': True
            }
        }
    }), 200


# =====================================================
# UTILITY ENDPOINTS (3)
# =====================================================

@whiteboard_bp.route('/tpl', methods=['GET'])
@jwt_required_v2
@handle_errors
def get_templates():
    """
    Get whiteboard templates
    
    GET /api/v2/whiteboard/tpl
    Returns: List of available templates
    
    Phase 1: Stub implementation
    """
    user_id = request.user_id
    
    logger.info(f"User {user_id} fetching whiteboard templates")
    
    # TODO Phase 5: Implement template system
    return jsonify({
        'success': True,
        'data': {
            'templates': [
                {
                    'id': 'weekly_planner',
                    'name': 'Weekly Meal Planner',
                    'description': '7-day meal planning grid',
                    '_stub': True
                },
                {
                    'id': 'party_board',
                    'name': 'Party Planning',
                    'description': 'Organize recipes and shopping for events',
                    '_stub': True
                },
                {
                    'id': 'meal_prep',
                    'name': 'Meal Prep Session',
                    'description': 'Batch cooking organization',
                    '_stub': True
                }
            ]
        }
    }), 200


@whiteboard_bp.route('/<int:wid>/dup', methods=['POST'])
@jwt_required_v2
@handle_errors
def duplicate_whiteboard(wid):
    """
    Duplicate whiteboard with all objects
    
    POST /api/v2/whiteboard/123/dup
    Body: {name?, household_id?}
    Returns: Duplicated whiteboard
    
    Phase 1: Stub implementation
    """
    user_id = request.user_id
    data = request.get_json()
    
    logger.info(f"User {user_id} duplicating whiteboard {wid}")
    
    # TODO Phase 5: Implement duplication
    return jsonify({
        'success': True,
        'data': {
            'original_id': wid,
            'duplicate_id': 998,
            'name': data.get('name', 'Copy of Whiteboard'),
            '_stub': True
        }
    }), 201


@whiteboard_bp.route('/<int:wid>/exp', methods=['GET'])
@jwt_required_v2
@handle_errors
def export_whiteboard(wid):
    """
    Export whiteboard as JSON
    
    GET /api/v2/whiteboard/123/exp
    Returns: Complete whiteboard data for export
    
    Phase 1: Stub implementation
    """
    user_id = request.user_id
    
    logger.info(f"User {user_id} exporting whiteboard {wid}")
    
    # TODO Phase 5: Implement export
    return jsonify({
        'success': True,
        'data': {
            'whiteboard_id': wid,
            'export_format': 'json',
            'exported_at': datetime.utcnow().isoformat(),
            '_stub': True
        }
    }), 200


# =====================================================
# HEALTH CHECK
# =====================================================

@whiteboard_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint (no auth required)
    
    GET /api/v2/whiteboard/health
    Returns: Service status
    """
    return jsonify({
        'success': True,
        'data': {
            'service': 'whiteboard',
            'status': 'healthy',
            'version': 'v2',
            'phase': 1,
            'endpoints_registered': 25,
            'timestamp': datetime.utcnow().isoformat()
        }
    }), 200


# =====================================================
# GROCERY LIST ENDPOINTS (Whiteboard Integration)
# =====================================================

@whiteboard_bp.route('/<int:wid>/grocery-lists', methods=['GET'])
@jwt_required_v2
@handle_errors
def get_whiteboard_grocery_lists(wid):
    """
    Get all grocery lists for a whiteboard
    
    GET /api/v2/whiteboard/123/grocery-lists
    Returns: List of grocery lists on this whiteboard
    """
    user_id = request.user_id
    
    logger.info(f"User {user_id} requesting grocery lists for whiteboard {wid}")
    
    # Import here to avoid circular dependency
    from app.database.repositories.grocery_list_repository import GroceryListRepository
    
    grocery_repo = GroceryListRepository()
    grocery_lists = grocery_repo.get_grocery_lists_by_whiteboard(wid, user_id)
    
    return jsonify({
        'success': True,
        'data': {
            'whiteboard_id': wid,
            'grocery_lists': grocery_lists,
            'count': len(grocery_lists)
        }
    }), 200


@whiteboard_bp.route('/<int:wid>/grocery-lists', methods=['POST'])
@jwt_required_v2
@handle_errors
def create_whiteboard_grocery_list(wid):
    """
    Create a new grocery list on whiteboard
    
    POST /api/v2/whiteboard/123/grocery-lists
    Body: {
        name: str,
        items: [{ingredient, checked, ...}],
        household_id: int,
        widget_position: {x, y, size},
        linked_recipe_ids: [int]
    }
    Returns: Created grocery list
    """
    user_id = request.user_id
    data = request.get_json()
    
    logger.info(f"User {user_id} creating grocery list on whiteboard {wid}")
    logger.info(f"📦 Data received: name={data.get('name')}, items_count={len(data.get('items', []))}, household_id={data.get('household_id')}")
    
    # Validate required fields
    if not data.get('name'):
        return jsonify({
            'success': False,
            'error': 'MISSING_FIELDS',
            'message': 'name is required'
        }), 400
    
    if 'items' not in data:
        return jsonify({
            'success': False,
            'error': 'MISSING_FIELDS',
            'message': 'items field is required (can be empty array)'
        }), 400
    
    # Import here to avoid circular dependency
    from app.database.repositories.grocery_list_repository import GroceryListRepository
    
    grocery_repo = GroceryListRepository()
    grocery_list = grocery_repo.create_grocery_list(
        user_id=user_id,
        name=data['name'],
        items=data['items'],
        household_id=data.get('household_id'),
        whiteboard_id=wid,
        widget_position=data.get('widget_position'),
        linked_recipe_ids=data.get('linked_recipe_ids')
    )
    
    if grocery_list:
        logger.info(f"✅ Grocery list created: id={grocery_list['id']}")
        return jsonify({
            'success': True,
            'data': grocery_list
        }), 201
    else:
        return jsonify({
            'success': False,
            'error': 'CREATE_FAILED',
            'message': 'Failed to create grocery list'
        }), 500


@whiteboard_bp.route('/<int:wid>/grocery-lists/<int:list_id>', methods=['PATCH'])
@jwt_required_v2
@handle_errors
def update_whiteboard_grocery_list(wid, list_id):
    """
    Update a grocery list on whiteboard
    
    PATCH /api/v2/whiteboard/123/grocery-lists/456
    Body: {
        name?: str,
        items?: [{ingredient, checked, ...}],
        widget_position?: {x, y, size},
        linked_recipe_ids?: [int]
    }
    Returns: Updated grocery list
    """
    user_id = request.user_id
    data = request.get_json()
    
    logger.info(f"User {user_id} updating grocery list {list_id} on whiteboard {wid}")
    
    # Import here to avoid circular dependency
    from app.database.repositories.grocery_list_repository import GroceryListRepository
    
    grocery_repo = GroceryListRepository()
    grocery_list = grocery_repo.update_grocery_list(
        list_id=list_id,
        user_id=user_id,
        name=data.get('name'),
        items=data.get('items'),
        widget_position=data.get('widget_position'),
        linked_recipe_ids=data.get('linked_recipe_ids')
    )
    
    if grocery_list:
        logger.info(f"✅ Grocery list updated: id={list_id}")
        return jsonify({
            'success': True,
            'data': grocery_list
        }), 200
    else:
        return jsonify({
            'success': False,
            'error': 'UPDATE_FAILED',
            'message': 'Failed to update grocery list or not found'
        }), 404


@whiteboard_bp.route('/<int:wid>/grocery-lists/<int:list_id>', methods=['DELETE'])
@jwt_required_v2
@handle_errors
def delete_whiteboard_grocery_list(wid, list_id):
    """
    Delete (soft delete) a grocery list from whiteboard
    
    DELETE /api/v2/whiteboard/123/grocery-lists/456
    Returns: Success message
    """
    user_id = request.user_id
    
    logger.info(f"User {user_id} deleting grocery list {list_id} from whiteboard {wid}")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Soft delete by setting deleted_at
        cursor.execute("""
            UPDATE grocery_lists
            SET deleted_at = NOW()
            WHERE id = %s AND user_id = %s AND wid = %s
            RETURNING id
        """, (list_id, user_id, wid))
        
        result = cursor.fetchone()
        conn.commit()
        
        if result:
            logger.info(f"✅ Grocery list deleted: id={list_id}")
            return jsonify({
                'success': True,
                'message': 'Grocery list deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'NOT_FOUND',
                'message': 'Grocery list not found or unauthorized'
            }), 404
            
    finally:
        cursor.close()
        return_db_connection(conn)


# =====================================================
# WHITEBOARD OBJECT LINK ENDPOINTS (For Mobile Integration)
# =====================================================

@whiteboard_bp.route('/recipes/<int:recipe_id>/whiteboard-object', methods=['GET'])
@jwt_required_v2
@handle_errors
def get_recipe_whiteboard_object(recipe_id):
    """
    Get whiteboard object for a recipe (if it exists on any whiteboard)
    
    GET /api/v2/whiteboard/recipes/123/whiteboard-object
    
    Returns:
        {
            "success": true,
            "whiteboard_object": {
                "id": 456,
                "whiteboard_id": 789,
                "type": "rc",
                "position": {...},
                "tags": ["quick", "italian"],
                "created_at": "2025-11-10T10:00:00"
            }
        }
    """
    user_id = request.user_id
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        # Find whiteboard object for this recipe
        # Only return if user has access to the household
        cursor.execute("""
            SELECT 
                wbo.id,
                wbo.wid as whiteboard_id,
                wbo.t as type,
                wbo.p as position,
                wbo.s as style,
                wbo.tags,
                wbo.ca as created_at,
                wb.n as whiteboard_name,
                wb.hid as household_id
            FROM wbo
            JOIN wb ON wbo.wid = wb.id
            JOIN household_members hm ON wb.hid = hm.household_id
            WHERE wbo.rid = %s 
                AND hm.user_id = %s
                AND wbo.deleted_at IS NULL
            ORDER BY wbo.ca DESC
            LIMIT 1
        """, (recipe_id, user_id))
        
        result = cursor.fetchone()
        
        if result:
            return jsonify({
                'success': True,
                'whiteboard_object': dict(result)
            }), 200
        else:
            return jsonify({
                'success': True,
                'whiteboard_object': None
            }), 200
            
    finally:
        cursor.close()
        return_db_connection(conn)


@whiteboard_bp.route('/meal-plans/<int:meal_plan_id>/whiteboard-object', methods=['GET'])
@jwt_required_v2
@handle_errors
def get_meal_plan_whiteboard_object(meal_plan_id):
    """
    Get whiteboard object for a meal plan
    
    GET /api/v2/whiteboard/meal-plans/123/whiteboard-object
    
    Returns whiteboard object or null if not on any whiteboard
    """
    user_id = request.user_id
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("""
            SELECT 
                wbo.id,
                wbo.wid as whiteboard_id,
                wbo.t as type,
                wbo.p as position,
                wbo.s as style,
                wbo.tags,
                wbo.ca as created_at,
                wb.n as whiteboard_name,
                wb.hid as household_id
            FROM wbo
            JOIN wb ON wbo.wid = wb.id
            JOIN household_members hm ON wb.hid = hm.household_id
            WHERE wbo.mid = %s 
                AND hm.user_id = %s
                AND wbo.deleted_at IS NULL
            ORDER BY wbo.ca DESC
            LIMIT 1
        """, (meal_plan_id, user_id))
        
        result = cursor.fetchone()
        
        if result:
            return jsonify({
                'success': True,
                'whiteboard_object': dict(result)
            }), 200
        else:
            return jsonify({
                'success': True,
                'whiteboard_object': None
            }), 200
            
    finally:
        cursor.close()
        return_db_connection(conn)


@whiteboard_bp.route('/grocery-lists/<int:grocery_list_id>/whiteboard-object', methods=['GET'])
@jwt_required_v2
@handle_errors
def get_grocery_list_whiteboard_object(grocery_list_id):
    """
    Get whiteboard object for a grocery list
    
    GET /api/v2/whiteboard/grocery-lists/123/whiteboard-object
    
    Returns whiteboard object or null if not on any whiteboard
    """
    user_id = request.user_id
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("""
            SELECT 
                wbo.id,
                wbo.wid as whiteboard_id,
                wbo.t as type,
                wbo.p as position,
                wbo.s as style,
                wbo.tags,
                wbo.ca as created_at,
                wb.n as whiteboard_name,
                wb.hid as household_id
            FROM wbo
            JOIN wb ON wbo.wid = wb.id
            JOIN household_members hm ON wb.hid = hm.household_id
            WHERE wbo.gid = %s 
                AND hm.user_id = %s
                AND wbo.deleted_at IS NULL
            ORDER BY wbo.ca DESC
            LIMIT 1
        """, (grocery_list_id, user_id))
        
        result = cursor.fetchone()
        
        if result:
            return jsonify({
                'success': True,
                'whiteboard_object': dict(result)
            }), 200
        else:
            return jsonify({
                'success': True,
                'whiteboard_object': None
            }), 200
            
    finally:
        cursor.close()
        return_db_connection(conn)


# =====================================================
# HOUSEHOLD DATA SHARING ENDPOINTS
# =====================================================
# These endpoints allow household members to access
# recipes and meal plans created by other members
# when viewing them in a shared whiteboard context

@whiteboard_bp.route('/<int:wid>/recipes/<int:recipe_id>', methods=['GET'])
@jwt_required_v2
@handle_errors
def get_whiteboard_recipe(wid, recipe_id):
    """Get recipe in context of whiteboard (household-aware)"""
    user_id = request.user_id
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cursor.execute("""
            SELECT wb.hid as household_id FROM wb
            JOIN household_members hm ON wb.hid = hm.household_id
            WHERE wb.id = %s AND hm.user_id = %s AND wb.deleted_at IS NULL
        """, (wid, user_id))
        whiteboard = cursor.fetchone()
        if not whiteboard:
            return jsonify({'success': False, 'error': 'Whiteboard not found'}), 403
        household_id = whiteboard['household_id']
        cursor.execute("""
            SELECT r.*, u.name as author_name FROM recipes r
            JOIN users u ON r.user_id = u.id
            JOIN household_members hm ON r.user_id = hm.user_id
            WHERE r.id = %s AND hm.household_id = %s
        """, (recipe_id, household_id))
        recipe = cursor.fetchone()
        if not recipe:
            return jsonify({'success': False, 'error': 'Recipe not found'}), 404
        return jsonify({'success': True, 'data': dict(recipe)}), 200
    finally:
        cursor.close()
        return_db_connection(conn)

@whiteboard_bp.route('/<int:wid>/meal-plans/<int:meal_plan_id>', methods=['GET'])
@jwt_required_v2
@handle_errors
def get_whiteboard_meal_plan(wid, meal_plan_id):
    """Get meal plan in context of whiteboard (household-aware)"""
    user_id = request.user_id
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cursor.execute("""
            SELECT wb.hid as household_id FROM wb
            JOIN household_members hm ON wb.hid = hm.household_id
            WHERE wb.id = %s AND hm.user_id = %s AND wb.deleted_at IS NULL
        """, (wid, user_id))
        whiteboard = cursor.fetchone()
        if not whiteboard:
            return jsonify({'success': False, 'error': 'Whiteboard not found'}), 403
        household_id = whiteboard['household_id']
        cursor.execute("""
            SELECT mp.*, u.name as author_name FROM meal_plans mp
            JOIN users u ON mp.user_id = u.id
            JOIN household_members hm ON mp.user_id = hm.user_id
            WHERE mp.id = %s AND hm.household_id = %s
        """, (meal_plan_id, household_id))
        meal_plan = cursor.fetchone()
        if not meal_plan:
            return jsonify({'success': False, 'error': 'Meal plan not found'}), 404
        return jsonify({'success': True, 'data': dict(meal_plan)}), 200
    finally:
        cursor.close()
        return_db_connection(conn)
