"""
Households API Routes (v2)
RESTful endpoints for households and household members management
"""

from flask import Blueprint, request, jsonify
import logging

from app.services.households_service import get_households_service

logger = logging.getLogger(__name__)

# Create blueprint
households_bp = Blueprint('households', __name__)

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
def get_household_members(household_id):
    """
    Get all members of a household
    
    Path Parameters:
        household_id: Household ID
    
    Query Parameters:
        user_id: User ID (for authorization check)
    
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
        user_id = request.args.get('user_id', type=int)
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
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
