"""
Recipe Search & Import API v2 Routes
RESTful endpoints for advanced recipe search, import, and recommendations
"""

from flask import Blueprint, request, jsonify
import logging

from app.services.recipe_search_service import RecipeSearchService

logger = logging.getLogger(__name__)

# Create blueprint
recipe_search_bp = Blueprint('recipe_search_v2', __name__, url_prefix='/api/v2/recipes')

# Initialize service
search_service = RecipeSearchService()


@recipe_search_bp.route('/search/advanced', methods=['GET'])
def advanced_search():
    """
    Advanced recipe search with filters
    
    Query params:
    - user_id (required): User ID
    - q (optional): Search term
    - category (optional): Category filter
    - prep_time_max (optional): Max prep time in minutes
    - cook_time_max (optional): Max cook time in minutes
    - limit (optional): Results limit (default: 50)
    - offset (optional): Pagination offset (default: 0)
    """
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        query = request.args.get('q', '')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        filters = {}
        if request.args.get('category'):
            filters['category'] = request.args.get('category')
        if request.args.get('prep_time_max'):
            filters['prep_time_max'] = request.args.get('prep_time_max', type=int)
        if request.args.get('cook_time_max'):
            filters['cook_time_max'] = request.args.get('cook_time_max', type=int)
        
        result = search_service.search(
            user_id=user_id,
            query=query,
            filters=filters,
            limit=limit,
            offset=offset
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in advanced_search: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@recipe_search_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    """
    Get personalized recipe recommendations
    
    Query params:
    - user_id (required): User ID
    - limit (optional): Results limit (default: 10)
    """
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        limit = request.args.get('limit', 10, type=int)
        
        result = search_service.get_recommendations(
            user_id=user_id,
            limit=limit
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in get_recommendations: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@recipe_search_bp.route('/search/ingredients', methods=['POST'])
def search_by_ingredients():
    """
    Search recipes by available ingredients
    
    Request body:
    {
        "user_id": 10,
        "ingredients": ["tomato", "onion", "garlic"],
        "limit": 20
    }
    """
    try:
        data = request.get_json()
        
        user_id = data.get('user_id')
        ingredients = data.get('ingredients', [])
        limit = data.get('limit', 20)
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        result = search_service.search_by_ingredients(
            user_id=user_id,
            ingredients=ingredients,
            limit=limit
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in search_by_ingredients: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@recipe_search_bp.route('/popular', methods=['GET'])
def get_popular():
    """
    Get popular community recipes
    
    Query params:
    - limit (optional): Results limit (default: 20)
    """
    try:
        limit = request.args.get('limit', 20, type=int)
        
        result = search_service.get_popular(limit=limit)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in get_popular: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@recipe_search_bp.route('/recent', methods=['GET'])
def get_recent():
    """
    Get recent recipes
    
    Query params:
    - user_id (required): User ID
    - days (optional): Number of days to look back (default: 7)
    - limit (optional): Results limit (default: 20)
    """
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        days = request.args.get('days', 7, type=int)
        limit = request.args.get('limit', 20, type=int)
        
        result = search_service.get_recent(
            user_id=user_id,
            days=days,
            limit=limit
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in get_recent: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@recipe_search_bp.route('/import', methods=['POST'])
def import_recipe():
    """
    Import recipe from URL
    
    Request body:
    {
        "user_id": 10,
        "url": "https://example.com/recipe"
    }
    """
    try:
        data = request.get_json()
        
        user_id = data.get('user_id')
        url = data.get('url')
        
        if not user_id or not url:
            return jsonify({
                'success': False,
                'error': 'user_id and url are required'
            }), 400
        
        result = search_service.import_from_url(
            user_id=user_id,
            url=url
        )
        
        if result['success']:
            return jsonify(result), 201
        
        return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Error in import_recipe: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@recipe_search_bp.route('/import/text', methods=['POST'])
def import_from_text():
    """
    Import recipe from raw text (placeholder for AI parsing)
    
    Request body:
    {
        "user_id": 10,
        "text": "Recipe text with ingredients and instructions..."
    }
    """
    try:
        data = request.get_json()
        
        user_id = data.get('user_id')
        text = data.get('text')
        
        if not user_id or not text:
            return jsonify({
                'success': False,
                'error': 'user_id and text are required'
            }), 400
        
        # Placeholder implementation
        # In production, this would use AI/LLM to parse the text
        
        # Simple extraction for now
        lines = text.strip().split('\n')
        title = lines[0] if lines else 'Imported Recipe from Text'
        
        recipe_data = {
            'title': title,
            'description': 'Recipe imported from text (placeholder)',
            'ingredients': ['Ingredient 1 (parsed)', 'Ingredient 2 (parsed)'],
            'instructions': ['Step 1 (parsed)', 'Step 2 (parsed)'],
            'prep_time': '15 minutes',
            'cook_time': '30 minutes',
            'servings': 4
        }
        
        # Log import
        search_service.repository.log_import(
            user_id=user_id,
            source_url='text_import',
            status='success'
        )
        
        result = {
            'success': True,
            'data': recipe_data,
            'message': 'Recipe imported from text (placeholder - ready for AI integration)',
            'placeholder': True
        }
        
        return jsonify(result), 201
        
    except Exception as e:
        logger.error(f"Error in import_from_text: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@recipe_search_bp.route('/import/ocr', methods=['POST'])
def import_from_ocr():
    """
    Import recipe from image using OCR (placeholder)
    
    Request body:
    {
        "user_id": 10,
        "image_data": "base64_encoded_image_data"
    }
    """
    try:
        data = request.get_json()
        
        user_id = data.get('user_id')
        image_data = data.get('image_data')
        
        if not user_id or not image_data:
            return jsonify({
                'success': False,
                'error': 'user_id and image_data are required'
            }), 400
        
        # Placeholder implementation
        # In production, this would use OCR (Tesseract/Google Vision) + AI parsing
        
        recipe_data = {
            'title': 'Recipe from Image (OCR)',
            'description': 'Recipe scanned from image (placeholder)',
            'ingredients': [
                'Ingredient extracted from image',
                'Another ingredient from OCR'
            ],
            'instructions': [
                'Step 1 extracted via OCR',
                'Step 2 extracted via OCR'
            ],
            'prep_time': '10 minutes',
            'cook_time': '25 minutes',
            'servings': 2
        }
        
        # Log import
        search_service.repository.log_import(
            user_id=user_id,
            source_url='ocr_import',
            status='success'
        )
        
        result = {
            'success': True,
            'data': recipe_data,
            'message': 'Recipe imported from image (placeholder - ready for OCR integration)',
            'placeholder': True,
            'ocr_confidence': 0.85
        }
        
        return jsonify(result), 201
        
    except Exception as e:
        logger.error(f"Error in import_from_ocr: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@recipe_search_bp.route('/import/history', methods=['GET'])
def get_import_history():
    """
    Get import history
    
    Query params:
    - user_id (required): User ID
    - limit (optional): Results limit (default: 20)
    """
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        limit = request.args.get('limit', 20, type=int)
        
        result = search_service.get_import_history(
            user_id=user_id,
            limit=limit
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in get_import_history: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@recipe_search_bp.route('/bulk-delete', methods=['DELETE'])
def bulk_delete():
    """
    Delete multiple recipes at once
    
    Request body:
    {
        "user_id": 10,
        "recipe_ids": [1, 2, 3, 4]
    }
    """
    try:
        data = request.get_json()
        
        user_id = data.get('user_id')
        recipe_ids = data.get('recipe_ids', [])
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        result = search_service.bulk_delete(
            user_id=user_id,
            recipe_ids=recipe_ids
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in bulk_delete: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


# Register error handlers
@recipe_search_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Resource not found'
    }), 404


@recipe_search_bp.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500
