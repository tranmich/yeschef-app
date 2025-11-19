"""
Households API Routes (v2)
RESTful endpoints for households and household members management
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from app.services.households_service import get_households_service

logger = logging.getLogger(__name__)

# Create blueprint
households_bp = Blueprint('households', __name__, url_prefix='/api/v2')

# Get service instance
households_service = get_households_service()


@households_bp.route('/households/user/<int:user_id>', methods=['GET'])
def get_user_households(user_id):
    """
    Get all households for a user
    
    Path Parameters:
        user_id: User ID
    
    Response:
        {
            "success": true,
            "data": {
                "households": [
                    {
                        "id": 1,
                        "name": "Family",
                        "description": "Our family household",
                        "created_by": 1,
                        "creator_name": "John Doe",
                        "user_role": "owner",
                        "member_count": 4,
                        "is_active": true,
                        "created_at": "2025-01-15T10:30:00"
                    }
                ],
                "count": 1
            }
        }
    """
    try:
        result = households_service.get_user_households(user_id)
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in get_user_households: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@households_bp.route('/households/<int:household_id>', methods=['GET'])
def get_household(household_id):
    """
    Get household by ID with members
    
    Path Parameters:
        household_id: Household ID
    
    Query Parameters:
        user_id: User ID (for authorization check)
    
    Response:
        {
            "success": true,
            "data": {
                "household": {...},
                "members": [...]
            }
        }
    """
    try:
        user_id = request.args.get('user_id', type=int)
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        result = households_service.get_household(household_id, user_id)
        status_code = 200 if result.get('success') else 404
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in get_household: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@households_bp.route('/households', methods=['POST'])
def create_household():
    """
    Create new household
    
    Request Body:
        {
            "name": "Family",
            "created_by": 1,
            "description": "Our family household"  // optional
        }
    
    Response:
        {
            "success": true,
            "data": {
                "household": {...},
                "membership": {...}
            },
            "message": "Household 'Family' created successfully"
        }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        name = data.get('name')
        created_by = data.get('created_by')
        
        if not name:
            return jsonify({
                'success': False,
                'error': 'name is required'
            }), 400
        
        if not created_by:
            return jsonify({
                'success': False,
                'error': 'created_by is required'
            }), 400
        
        # Optional description
        description = data.get('description')
        
        # Create household
        result = households_service.create_household(
            name=name,
            created_by=created_by,
            description=description
        )
        
        status_code = 201 if result.get('success') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in create_household: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@households_bp.route('/households/<int:household_id>', methods=['PUT'])
def update_household(household_id):
    """
    Update household details
    
    Path Parameters:
        household_id: Household ID
    
    Request Body:
        {
            "user_id": 1,  // User making the request (must be owner/admin)
            "name": "New Family Name",  // optional
            "description": "Updated description",  // optional
            "is_active": true  // optional
        }
    
    Response:
        {
            "success": true,
            "data": {...},
            "message": "Household updated successfully"
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
        
        # Extract updates (exclude user_id)
        updates = {k: v for k, v in data.items() if k != 'user_id' and k in ['name', 'description', 'is_active']}
        
        if not updates:
            return jsonify({
                'success': False,
                'error': 'No fields to update'
            }), 400
        
        result = households_service.update_household(household_id, user_id, updates)
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in update_household: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@households_bp.route('/households/<int:household_id>', methods=['DELETE'])
def delete_household(household_id):
    """
    Delete household (soft delete) - owner only
    
    Path Parameters:
        household_id: Household ID
    
    Query Parameters:
        user_id: User ID (must be owner)
    
    Response:
        {
            "success": true,
            "message": "Household deleted successfully"
        }
    """
    try:
        user_id = request.args.get('user_id', type=int)
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        result = households_service.delete_household(household_id, user_id)
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in delete_household: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@households_bp.route('/households/<int:household_id>/members', methods=['GET'])
@jwt_required()
def get_household_members(household_id):
    """
    Get all members of a household
    
    Path Parameters:
        household_id: Household ID
    
    Response:
        {
            "success": true,
            "data": {
                "members": [
                    {
                        "membership_id": 1,
                        "household_id": 1,
                        "user_id": 1,
                        "user_name": "John Doe",
                        "user_email": "john@example.com",
                        "role": "owner",
                        "joined_at": "2025-01-15T10:30:00"
                    }
                ],
                "count": 4
            }
        }
    """
    try:
        user_id = int(get_jwt_identity())
        
        result = households_service.get_household_members(household_id, user_id)
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in get_household_members: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@households_bp.route('/households/<int:household_id>/members', methods=['POST'])
def add_household_member(household_id):
    """
    Add member to household
    
    Path Parameters:
        household_id: Household ID
    
    Request Body:
        {
            "requesting_user_id": 1,  // User making the request (must be owner/admin)
            "user_id": 2,  // User to add
            "role": "member"  // optional, default: "member"
        }
    
    Response:
        {
            "success": true,
            "data": {...},
            "message": "Member added to household successfully"
        }
    """
    try:
        data = request.get_json()
        
        requesting_user_id = data.get('requesting_user_id')
        user_id_to_add = data.get('user_id')
        role = data.get('role', 'member')
        
        if not requesting_user_id:
            return jsonify({
                'success': False,
                'error': 'requesting_user_id is required'
            }), 400
        
        if not user_id_to_add:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        result = households_service.add_household_member(
            household_id=household_id,
            requesting_user_id=requesting_user_id,
            user_id_to_add=user_id_to_add,
            role=role
        )
        
        status_code = 201 if result.get('success') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in add_household_member: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@households_bp.route('/households/<int:household_id>/members/<int:member_id>', methods=['DELETE'])
def remove_household_member(household_id, member_id):
    """
    Remove member from household
    
    Path Parameters:
        household_id: Household ID
        member_id: User ID to remove
    
    Query Parameters:
        user_id: User ID making the request
    
    Response:
        {
            "success": true,
            "message": "Member removed from household successfully"
        }
    """
    try:
        requesting_user_id = request.args.get('user_id', type=int)
        
        if not requesting_user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        result = households_service.remove_household_member(
            household_id=household_id,
            requesting_user_id=requesting_user_id,
            user_id_to_remove=member_id
        )
        
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in remove_household_member: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@households_bp.route('/households/<int:household_id>/members/<int:member_id>/role', methods=['PUT'])
def update_member_role(household_id, member_id):
    """
    Update member's role in household
    
    Path Parameters:
        household_id: Household ID
        member_id: User ID whose role to update
    
    Request Body:
        {
            "requesting_user_id": 1,  // User making the request (must be owner)
            "role": "admin"  // new role: "member", "admin", or "owner"
        }
    
    Response:
        {
            "success": true,
            "data": {...},
            "message": "Member role updated to admin"
        }
    """
    try:
        data = request.get_json()
        
        requesting_user_id = data.get('requesting_user_id')
        new_role = data.get('role')
        
        if not requesting_user_id:
            return jsonify({
                'success': False,
                'error': 'requesting_user_id is required'
            }), 400
        
        if not new_role:
            return jsonify({
                'success': False,
                'error': 'role is required'
            }), 400
        
        result = households_service.update_member_role(
            household_id=household_id,
            requesting_user_id=requesting_user_id,
            user_id_to_update=member_id,
            new_role=new_role
        )
        
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in update_member_role: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@households_bp.route('/household/<int:household_id>/activity', methods=['GET'])
def get_household_activity(household_id):
    """
    Get recent household activity (for mobile collaboration)
    
    Path Parameters:
        household_id: Household ID
    
    Query Parameters:
        limit: Number of activities to return (default: 20, max: 50)
        offset: Number of activities to skip (for pagination)
    
    Response:
        {
            "success": true,
            "activities": [
                {
                    "id": 123,
                    "type": "recipe_added",
                    "user": {
                        "id": 1,
                        "name": "Sarah",
                        "avatar": "https://..."
                    },
                    "action": "added Chicken Parmesan",
                    "preview": "Let's make this Tuesday!",
                    "tags": ["quick", "italian"],
                    "created_at": "2025-11-10T14:30:00",
                    "is_live": false,
                    "related_object": {
                        "type": "recipe",
                        "id": 456
                    }
                }
            ],
            "count": 20,
            "has_more": true
        }
    """
    try:
        from app.database.connection import get_db_connection, return_db_connection
        
        # Get query parameters
        limit = min(int(request.args.get('limit', 20)), 50)
        offset = int(request.args.get('offset', 0))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # For now, get activities from comments table (most active data source)
        # Later can merge with whiteboard_events when that's populated
        query = """
            SELECT 
                c.id,
                'comment_added' as event_type,
                c.object_type,
                c.object_id,
                c.content,
                c.created_at,
                u.id as user_id,
                u.name as user_name,
                u.email as user_email,
                c.whiteboard_id
            FROM comments c
            JOIN whiteboards wb ON c.whiteboard_id = wb.id
            LEFT JOIN users u ON c.user_id = u.id
            WHERE wb.household_id = %s
                AND c.created_at >= NOW() - INTERVAL '7 days'
            ORDER BY c.created_at DESC
            LIMIT %s OFFSET %s
        """
        
        cursor.execute(query, (household_id, limit + 1, offset))
        rows = cursor.fetchall()
        
        has_more = len(rows) > limit
        if has_more:
            rows = rows[:limit]
        
        # Transform results into activity objects
        activities = []
        for row in rows:
            object_type = row[2]
            object_id = row[3]
            
            # Parse object info for better display
            object_name = 'an item'
            related_type = 'unknown'
            related_id = None
            
            if object_type == 'recipeCard':
                object_name = 'a recipe'
                related_type = 'recipe'
                # Extract recipe ID from 'recipe-2609' format
                if object_id and object_id.startswith('recipe-'):
                    try:
                        related_id = int(object_id.replace('recipe-', ''))
                    except:
                        pass
            elif object_type == 'groceryListNode':
                object_name = 'a grocery list'
                related_type = 'grocery_list'
            elif object_type == 'mealPlanContainer':
                object_name = 'a meal plan'
                related_type = 'meal_plan'
            elif object_type == 'note':
                object_name = 'a note'
                related_type = 'note'
            
            # Build activity object
            activity = {
                'id': row[0],
                'type': 'comment_added',
                'user': {
                    'id': row[6],
                    'name': row[7] or 'Anonymous',
                    'email': row[8],
                    'avatar': None
                },
                'action': f"commented on {object_name}",
                'preview': row[4][:100] if row[4] else None,  # First 100 chars
                'tags': [],
                'created_at': row[5].isoformat() if row[5] else None,
                'is_live': False,
                'related_object': {
                    'type': related_type,
                    'id': related_id
                } if related_id else None,
                'whiteboard': {
                    'id': row[9],
                    'name': 'Whiteboard'
                }
            }
            
            activities.append(activity)
        
        return_db_connection(conn)
        
        return jsonify({
            'success': True,
            'activities': activities,
            'count': len(activities),
            'has_more': has_more
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_household_activity: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'activities': []
        }), 500


def _format_activity_action(event_type, event_data):
    """Format activity action text based on event type"""
    actions = {
        'object_created': f"added {event_data.get('object_name', 'an item')}",
        'comment_added': f"commented on {event_data.get('object_name', 'an item')}",
        'object_updated': f"updated {event_data.get('object_name', 'an item')}",
        'tag_added': f"tagged {event_data.get('object_name', 'an item')}",
        'user_joined': 'joined the whiteboard',
    }
    return actions.get(event_type, 'did something')
