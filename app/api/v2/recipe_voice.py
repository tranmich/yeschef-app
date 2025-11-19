"""
Voice Recipe API Routes (v2)
Handles voice-based recipe creation and language detection
Wraps existing V1 voice logic with V2 response format
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import logging

logger = logging.getLogger(__name__)

# Create blueprint
recipe_voice_bp = Blueprint('recipe_voice_v2', __name__, url_prefix='/api/v2/recipes/voice')


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


# GET /api/v2/recipes/voice/languages/search
@recipe_voice_bp.route('/languages/search', methods=['GET'])
@handle_errors
def search_languages():
    """
    Search for supported languages
    
    Query params:
        q: search query
        
    Response:
        {
            "success": true,
            "data": {
                "languages": [
                    {"code": "en", "name": "English", "native_name": "English"},
                    ...
                ]
            }
        }
    """
    from hungie_server import app as main_app
    
    query = request.args.get('q', '')
    
    try:
        # Use the existing V1 language search logic
        with main_app.test_client() as client:
            response = client.get(
                f'/api/recipes/voice/languages/search?q={query}',
                headers=request.headers
            )
            
            v1_data = response.get_json()
            
            # Convert V1 response to V2 format
            if response.status_code == 200:
                return jsonify({
                    'success': True,
                    'data': {
                        'languages': v1_data.get('languages', [])
                    }
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': v1_data.get('error', 'Language search failed'),
                    'code': 'SEARCH_ERROR'
                }), response.status_code
                
    except Exception as e:
        logger.error(f"Language search failed: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to search languages',
            'code': 'SEARCH_ERROR'
        }), 500


# POST /api/v2/recipes/voice/session/process
@recipe_voice_bp.route('/session/process', methods=['POST'])
@handle_errors
def process_voice_session():
    """
    Process voice recording session
    
    Request:
        Multipart form data with 'audio' file and session metadata
        
    Response:
        {
            "success": true,
            "data": {
                "session_id": "...",
                "transcript": "...",
                "language": "en",
                "confidence": 0.95
            }
        }
    """
    from hungie_server import app as main_app
    
    if 'audio' not in request.files:
        return jsonify({
            'success': False,
            'error': 'Audio file is required',
            'code': 'VALIDATION_ERROR'
        }), 400
    
    try:
        # Use the existing V1 voice session processing logic
        with main_app.test_client() as client:
            response = client.post(
                '/api/recipes/voice/session/process',
                data=request.form,
                files={'audio': request.files['audio']},
                headers=request.headers
            )
            
            v1_data = response.get_json()
            
            # Convert V1 response to V2 format
            if response.status_code == 200 and v1_data.get('success'):
                return jsonify({
                    'success': True,
                    'data': {
                        'session_id': v1_data.get('session_id'),
                        'transcript': v1_data.get('transcript'),
                        'language': v1_data.get('language'),
                        'confidence': v1_data.get('confidence')
                    }
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': v1_data.get('error', 'Voice processing failed'),
                    'code': 'VOICE_ERROR'
                }), response.status_code
                
    except Exception as e:
        logger.error(f"Voice session processing failed: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to process voice recording',
            'code': 'VOICE_ERROR'
        }), 500


# POST /api/v2/recipes/voice/generate
@recipe_voice_bp.route('/generate', methods=['POST'])
@handle_errors
def generate_from_voice():
    """
    Generate recipe from voice transcript
    
    Request:
        {
            "transcript": "...",
            "language": "en",
            "user_id": 123
        }
        
    Response:
        {
            "success": true,
            "data": {
                "recipe": { ... },
                "confidence": 0.95,
                "message": "Recipe generated from voice"
            }
        }
    """
    from hungie_server import app as main_app
    
    data = request.get_json()
    
    if not data or not data.get('transcript'):
        return jsonify({
            'success': False,
            'error': 'Transcript is required',
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
        # Use the existing V1 voice generation logic
        with main_app.test_client() as client:
            response = client.post(
                '/api/recipes/voice/generate',
                json=data,
                headers=request.headers
            )
            
            v1_data = response.get_json()
            
            # V1 Voice Generate Response format:
            # {
            #   success: bool,
            #   recipe_id: int (or None),
            #   recipe_data: {...},  <-- Note: Uses 'recipe_data', not 'recipe'
            #   confidence: float,
            #   needs_review: bool,
            #   extraction_method: str,
            #   processing_time: float
            # }
            
            # Convert V1 response to V2 format
            if response.status_code == 200 and v1_data.get('success'):
                return jsonify({
                    'success': True,
                    'data': {
                        'recipe': v1_data.get('recipe_data'),  # V1 uses 'recipe_data'
                        'recipe_id': v1_data.get('recipe_id'),
                        'confidence': v1_data.get('confidence'),
                        'needs_review': v1_data.get('needs_review'),
                        'extraction_method': v1_data.get('extraction_method'),
                        'processing_time': v1_data.get('processing_time'),
                        'message': 'Recipe generated from voice'
                    }
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': v1_data.get('error', 'Voice generation failed'),
                    'code': 'GENERATION_ERROR'
                }), response.status_code
                
    except Exception as e:
        logger.error(f"Voice recipe generation failed: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate recipe from voice',
            'code': 'GENERATION_ERROR'
        }), 500
