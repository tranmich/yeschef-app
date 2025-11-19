"""
Recipe Import API Routes (v2)
Handles recipe imports from URLs, OCR, and voice
Wraps existing V1 import logic with V2 response format
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import logging

logger = logging.getLogger(__name__)

# Create blueprint
recipe_import_bp = Blueprint('recipe_import_v2', __name__, url_prefix='/api/v2/recipes/import')


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
                'error': 'Internal server error',
                'code': 'SERVER_ERROR'
            }), 500
    return decorated_function


# POST /api/v2/recipes/import/url
@recipe_import_bp.route('/url', methods=['POST'])
@handle_errors
def import_from_url():
    """
    Import recipe from URL
    
    Request:
        {
            "url": "https://example.com/recipe",
            "user_id": 123
        }
        
    Response:
        {
            "success": true,
            "data": {
                "recipe": { ... },
                "message": "Recipe imported successfully"
            }
        }
    """
    # Import here to avoid circular imports
    from hungie_server import app as main_app
    
    data = request.get_json()
    
    if not data or not data.get('url'):
        return jsonify({
            'success': False,
            'error': 'URL is required',
            'code': 'VALIDATION_ERROR'
        }), 400
    
    # Get user_id from request data or auth token
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({
            'success': False,
            'error': 'User ID is required',
            'code': 'VALIDATION_ERROR'
        }), 400
    
    try:
        # V2: Call import logic directly instead of wrapping v1
        from core_systems.recipe_importer import UniversalRecipeImporter, ImportRequest
        
        # Create import request
        import_request = ImportRequest(
            source_type='url',
            source_data=data['url'],
            user_id=user_id,
            metadata=data.get('metadata', {})
        )
        
        # Initialize importer and process
        importer = UniversalRecipeImporter()
        result = importer.import_recipe(import_request)
        
        # Return v2 formatted response
        if result.success:
            return jsonify({
                'success': True,
                'data': {
                    'recipe': result.recipe_data,
                    'recipe_id': result.recipe_id,
                    'confidence': result.confidence,
                    'needs_review': result.needs_review,
                    'extraction_method': result.extraction_method,
                    'processing_time': result.processing_time,
                    'message': 'Recipe imported successfully'
                }
            }), 200
        else:
            # ImportResult uses 'errors' (list) not 'error' (string)
            error_message = result.errors[0] if result.errors and len(result.errors) > 0 else 'Import failed'
            return jsonify({
                'success': False,
                'error': error_message,
                'code': 'IMPORT_FAILED',
                'errors': result.errors or [],
                'warnings': result.warnings or []
            }), 400
                
    except Exception as e:
        logger.error(f"Import from URL failed: {e}")
        logger.error(f"Full error details: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'Failed to import recipe from URL: {str(e)}',
            'code': 'IMPORT_ERROR',
            'details': str(e)
        }), 500


# POST /api/v2/recipes/import/ocr
@recipe_import_bp.route('/ocr', methods=['POST'])
@handle_errors
def import_from_image():
    """
    Import recipe from image using OCR
    
    Request:
        Multipart form data with 'image' file and 'user_id'
        
    Response:
        {
            "success": true,
            "data": {
                "recipe": { ... },
                "confidence": 0.95,
                "message": "Recipe extracted from image"
            }
        }
    """
    from hungie_server import app as main_app
    
    if 'image' not in request.files:
        return jsonify({
            'success': False,
            'error': 'Image file is required',
            'code': 'VALIDATION_ERROR'
        }), 400
    
    user_id = request.form.get('user_id')
    if not user_id:
        return jsonify({
            'success': False,
            'error': 'User ID is required',
            'code': 'VALIDATION_ERROR'
        }), 400
    
    try:
        # Use the existing V1 OCR logic
        with main_app.test_client() as client:
            response = client.post(
                '/api/recipes/import/ocr',
                data=request.form,
                files={'image': request.files['image']},
                headers=request.headers
            )
            
            v1_data = response.get_json()
            
            # V1 OCR Response format:
            # {
            #   success: bool,
            #   recipe: {...},  <-- Note: OCR uses 'recipe', not 'recipe_data'
            #   recipe_id: int,
            #   confidence: float,
            #   extraction_method: str,
            #   ocr_stats: {...},
            #   needs_review: bool,
            #   processing_time: float,
            #   warnings: [...]
            # }
            
            # Convert V1 response to V2 format
            if response.status_code == 200 and v1_data.get('success'):
                return jsonify({
                    'success': True,
                    'data': {
                        'recipe': v1_data.get('recipe'),  # OCR already uses 'recipe'
                        'recipe_id': v1_data.get('recipe_id'),
                        'confidence': v1_data.get('confidence'),
                        'ocr_stats': v1_data.get('ocr_stats'),
                        'needs_review': v1_data.get('needs_review'),
                        'extraction_method': v1_data.get('extraction_method'),
                        'processing_time': v1_data.get('processing_time'),
                        'message': 'Recipe extracted from image'
                    }
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': v1_data.get('error', 'OCR import failed'),
                    'code': 'OCR_ERROR',
                    'details': v1_data.get('details'),
                    'extracted_text': v1_data.get('extracted_text')
                }), response.status_code
                
    except Exception as e:
        logger.error(f"OCR import failed: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to extract recipe from image',
            'code': 'OCR_ERROR'
        }), 500


# POST /api/v2/recipes/import/text
@recipe_import_bp.route('/text', methods=['POST'])
@handle_errors
def import_from_text():
    """
    Import recipe from plain text
    
    Request:
        {
            "text": "Recipe text...",
            "user_id": 123
        }
        
    Response:
        {
            "success": true,
            "data": {
                "recipe": { ... },
                "message": "Recipe imported successfully"
            }
        }
    """
    from hungie_server import app as main_app
    
    data = request.get_json()
    
    if not data or not data.get('text'):
        return jsonify({
            'success': False,
            'error': 'Text is required',
            'code': 'VALIDATION_ERROR'
        }), 400
    
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({
            'success': False,
            'error': 'User ID is required',
            'code': 'VALIDATION_ERROR'
        }), 400
    
    try:
        # V2: Call import logic directly instead of wrapping v1
        from core_systems.recipe_importer import UniversalRecipeImporter, ImportRequest
        
        # Create import request
        import_request = ImportRequest(
            source_type='text',
            source_data=data['text'],
            user_id=user_id,
            metadata=data.get('metadata', {})
        )
        
        # Initialize importer and process
        importer = UniversalRecipeImporter()
        result = importer.import_recipe(import_request)
        
        # Return v2 formatted response
        if result.success:
            return jsonify({
                'success': True,
                'data': {
                    'recipe': result.recipe_data,
                    'recipe_id': result.recipe_id,
                    'confidence': result.confidence,
                    'needs_review': result.needs_review,
                    'extraction_method': result.extraction_method,
                    'processing_time': result.processing_time,
                    'message': 'Recipe imported successfully'
                }
            }), 200
        else:
            # ImportResult uses 'errors' (list) not 'error' (string)
            error_message = result.errors[0] if result.errors and len(result.errors) > 0 else 'Import failed'
            return jsonify({
                'success': False,
                'error': error_message,
                'code': 'IMPORT_FAILED',
                'errors': result.errors or []
            }), 400
                
    except Exception as e:
        logger.error(f"Text import failed: {e}")
        logger.error(f"Full error details: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'Failed to import recipe from text: {str(e)}',
            'code': 'IMPORT_ERROR',
            'details': str(e)
        }), 500
