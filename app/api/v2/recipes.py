"""
Recipe API Routes (v2)
RESTful endpoints for recipe operations
Uses RecipeService for business logic
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import logging

from app.services.recipe_service import get_recipe_service

logger = logging.getLogger(__name__)

# Create blueprint
recipe_bp = Blueprint('recipe_v2', __name__, url_prefix='/api/v2/recipes')


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


# GET /api/v2/recipes/<recipe_id>
@recipe_bp.route('/<int:recipe_id>', methods=['GET'])
@handle_errors
def get_recipe(recipe_id):
    """
    Get recipe by ID
    
    Example:
        GET /api/v2/recipes/123?user_id=11
        
    Response:
        {
            "success": true,
            "data": {
                "id": 123,
                "title": "Chicken Soup",
                "ingredients": ["chicken", "water"],
                "instructions": ["Step 1", "Step 2"],
                ...
            }
        }
    """
    recipe_service = get_recipe_service()
    user_id = request.args.get('user_id', type=int)
    
    result = recipe_service.get_recipe_by_id(recipe_id, user_id)
    
    if result['success']:
        return jsonify(result), 200
    else:
        status_code = 404 if result.get('error_code') == 'NOT_FOUND' else 403
        return jsonify(result), status_code


# GET /api/v2/recipes/user/<user_id>
@recipe_bp.route('/user/<int:user_id>', methods=['GET'])
@handle_errors
def get_user_recipes(user_id):
    """
    Get user's recipes with pagination
    
    Example:
        GET /api/v2/recipes/user/11?category=dinner&page=1&per_page=20
        
    Response:
        {
            "success": true,
            "data": {
                "items": [...],
                "pagination": {
                    "page": 1,
                    "per_page": 20,
                    "total": 37,
                    "total_pages": 2,
                    "has_next": true,
                    "has_prev": false
                },
                "user": {"id": 11, "name": "YesChef"},
                "total_recipes": 37
            }
        }
    """
    recipe_service = get_recipe_service()
    
    category = request.args.get('category')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    result = recipe_service.get_user_recipes(user_id, category, page, per_page)
    
    if result['success']:
        return jsonify(result), 200
    else:
        status_code = 404 if result.get('error_code') == 'NOT_FOUND' else 400
        return jsonify(result), status_code


# GET /api/v2/recipes/user/<user_id>/stats
@recipe_bp.route('/user/<int:user_id>/stats', methods=['GET'])
@handle_errors
def get_user_recipes_with_stats(user_id):
    """
    Get user's recipes WITH statistics
    THIS IS THE STAR ENDPOINT! 🌟
    
    Example:
        GET /api/v2/recipes/user/11/stats
        
    Response:
        {
            "success": true,
            "data": {
                "user": {
                    "id": 11,
                    "name": "YesChef",
                    "email": "test@example.com"
                },
                "recipes": [...],  // All recipes
                "stats": {
                    "total_recipes": 37,
                    "categories": ["breakfast", "dinner", "lunch"],
                    "category_counts": {
                        "breakfast": 1,
                        "dinner": 2,
                        "lunch": 5
                    },
                    "flavor_profiles": [...],
                    "recent_recipes": [...]  // Last 5
                }
            }
        }
    """
    recipe_service = get_recipe_service()
    result = recipe_service.get_user_recipes_with_stats(user_id)
    
    if result['success']:
        return jsonify(result), 200
    else:
        status_code = 404 if result.get('error_code') == 'NOT_FOUND' else 400
        return jsonify(result), status_code


# POST /api/v2/recipes
@recipe_bp.route('', methods=['POST'])
@handle_errors
def create_recipe():
    """
    Create new recipe with duplicate detection
    
    Example:
        POST /api/v2/recipes
        {
            "user_id": 11,
            "title": "My Recipe",
            "ingredients": ["ingredient 1", "ingredient 2"],
            "instructions": ["step 1", "step 2"],
            "category": "dinner"
        }
        
    Response:
        {
            "success": true,
            "data": {...},
            "message": "Recipe created successfully"
        }
        
    OR if duplicate:
        {
            "success": false,
            "error": "You just created a recipe with this title 5 minutes ago",
            "error_code": "DUPLICATE",
            "details": {
                "existing_recipe": {...}
            }
        }
    """
    recipe_service = get_recipe_service()
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'error': 'No data provided'
        }), 400
    
    # Get user_id from request data
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({
            'success': False,
            'error': 'user_id is required'
        }), 400
    
    # Check if duplicate detection should be disabled
    check_duplicates = request.args.get('check_duplicates', 'true').lower() != 'false'
    
    result = recipe_service.create_recipe(user_id, data, check_duplicates)
    
    if result['success']:
        return jsonify(result), 201  # 201 Created
    else:
        if result.get('error_code') == 'DUPLICATE':
            return jsonify(result), 409  # 409 Conflict
        else:
            return jsonify(result), 400


# PATCH /api/v2/recipes/<recipe_id>
@recipe_bp.route('/<int:recipe_id>', methods=['PATCH'])
@handle_errors
def update_recipe(recipe_id):
    """
    Update recipe (authorization required)
    
    Example:
        PATCH /api/v2/recipes/123
        {
            "user_id": 11,
            "title": "Updated Title",
            "category": "lunch"
        }
        
    Response:
        {
            "success": true,
            "data": {...},
            "message": "Recipe updated successfully"
        }
    """
    recipe_service = get_recipe_service()
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'error': 'No data provided'
        }), 400
    
    # Get user_id from request data (for authorization)
    user_id = data.pop('user_id', None)
    if not user_id:
        return jsonify({
            'success': False,
            'error': 'user_id is required for authorization'
        }), 400
    
    result = recipe_service.update_recipe(recipe_id, user_id, data)
    
    if result['success']:
        return jsonify(result), 200
    else:
        if result.get('error_code') == 'UNAUTHORIZED':
            return jsonify(result), 403
        elif result.get('error_code') == 'NOT_FOUND':
            return jsonify(result), 404
        else:
            return jsonify(result), 400


# DELETE /api/v2/recipes/<recipe_id>
@recipe_bp.route('/<int:recipe_id>', methods=['DELETE'])
@handle_errors
def delete_recipe(recipe_id):
    """
    Delete recipe (authorization required)
    
    Example:
        DELETE /api/v2/recipes/123?user_id=11
        
    Response:
        {
            "success": true,
            "data": {"recipe_id": 123},
            "message": "Recipe deleted successfully"
        }
    """
    recipe_service = get_recipe_service()
    
    # Get user_id from query params (for authorization)
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({
            'success': False,
            'error': 'user_id is required for authorization'
        }), 400
    
    result = recipe_service.delete_recipe(recipe_id, user_id)
    
    if result['success']:
        return jsonify(result), 200
    else:
        if result.get('error_code') == 'UNAUTHORIZED':
            return jsonify(result), 403
        elif result.get('error_code') == 'NOT_FOUND':
            return jsonify(result), 404
        else:
            return jsonify(result), 400


# POST /api/v2/recipes/<recipe_id>/share
@recipe_bp.route('/<int:recipe_id>/share', methods=['POST'])
@handle_errors
def share_recipe(recipe_id):
    """
    Share recipe to community
    
    Example:
        POST /api/v2/recipes/123/share
        {
            "user_id": 11
        }
        
    Response:
        {
            "success": true,
            "data": {...},
            "message": "Recipe shared to community"
        }
    """
    recipe_service = get_recipe_service()
    data = request.get_json() or {}
    
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({
            'success': False,
            'error': 'user_id is required'
        }), 400
    
    result = recipe_service.share_to_community(recipe_id, user_id)
    
    if result['success']:
        return jsonify(result), 200
    else:
        if result.get('error_code') == 'UNAUTHORIZED':
            return jsonify(result), 403
        else:
            return jsonify(result), 400


# POST /api/v2/recipes/<recipe_id>/unshare
@recipe_bp.route('/<int:recipe_id>/unshare', methods=['POST'])
@handle_errors
def unshare_recipe(recipe_id):
    """
    Unshare recipe from community
    
    Example:
        POST /api/v2/recipes/123/unshare
        {
            "user_id": 11
        }
        
    Response:
        {
            "success": true,
            "data": {...},
            "message": "Recipe removed from community"
        }
    """
    recipe_service = get_recipe_service()
    data = request.get_json() or {}
    
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({
            'success': False,
            'error': 'user_id is required'
        }), 400
    
    result = recipe_service.unshare_from_community(recipe_id, user_id)
    
    if result['success']:
        return jsonify(result), 200
    else:
        if result.get('error_code') == 'UNAUTHORIZED':
            return jsonify(result), 403
        else:
            return jsonify(result), 400


# GET /api/v2/recipes/search
@recipe_bp.route('/search', methods=['GET'])
@handle_errors
def search_recipes():
    """
    Search user's recipes
    
    Example:
        GET /api/v2/recipes/search?user_id=11&q=chicken&limit=20
        
    Response:
        {
            "success": true,
            "data": {
                "recipes": [...],
                "count": 12,
                "search_term": "chicken"
            }
        }
    """
    recipe_service = get_recipe_service()
    
    user_id = request.args.get('user_id', type=int)
    search_term = request.args.get('q', '')
    limit = request.args.get('limit', 50, type=int)
    
    if not user_id:
        return jsonify({
            'success': False,
            'error': 'user_id is required'
        }), 400
    
    if not search_term:
        return jsonify({
            'success': False,
            'error': 'Search term required (q parameter)'
        }), 400
    
    result = recipe_service.search_recipes(user_id, search_term, limit)
    
    return jsonify(result), 200


# GET /api/v2/recipes/community
@recipe_bp.route('/community', methods=['GET'])
@handle_errors
def get_community_recipes():
    """
    Get community-shared recipes
    
    Example:
        GET /api/v2/recipes/community?page=1&per_page=20
        
    Response:
        {
            "success": true,
            "data": {
                "items": [...],
                "pagination": {...}
            }
        }
    """
    recipe_service = get_recipe_service()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    result = recipe_service.get_community_recipes(page, per_page)
    
    return jsonify(result), 200
