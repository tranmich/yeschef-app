"""
Image API Routes (v2)
Serves optimized recipe images
"""

from flask import Blueprint, send_from_directory, jsonify
import logging
import os

from app.services.image_service import get_image_service, IMAGE_STORAGE_PATH

logger = logging.getLogger(__name__)

# Create blueprint
image_bp = Blueprint('image_v2', __name__, url_prefix='/api/v2/images')


@image_bp.route('/<filename>')
def serve_image(filename):
    """
    Serve optimized recipe image
    
    Example:
        GET /api/v2/images/recipe_123.webp
        
    Returns:
        WebP image file (80-100 KB typically)
    """
    try:
        # Security: Only allow .webp files
        if not filename.endswith('.webp'):
            return jsonify({
                'success': False,
                'error': 'Invalid file type'
            }), 400
        
        # Security: Prevent directory traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            return jsonify({
                'success': False,
                'error': 'Invalid filename'
            }), 400
        
        # Check if file exists
        image_service = get_image_service()
        filepath = image_service.get_image_path(filename)
        
        if not filepath or not os.path.exists(filepath):
            logger.warning(f"⚠️ Image not found: {filename}")
            return jsonify({
                'success': False,
                'error': 'Image not found'
            }), 404
        
        # Serve the file
        return send_from_directory(
            IMAGE_STORAGE_PATH,
            filename,
            mimetype='image/webp',
            max_age=31536000  # Cache for 1 year (images don't change)
        )
        
    except Exception as e:
        logger.error(f"❌ Error serving image {filename}: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@image_bp.route('/health')
def health_check():
    """
    Check if image service is working
    
    Example:
        GET /api/v2/images/health
        
    Returns:
        {
            "success": true,
            "storage_path": "data/recipe_images",
            "storage_exists": true
        }
    """
    try:
        storage_exists = os.path.exists(IMAGE_STORAGE_PATH)
        return jsonify({
            'success': True,
            'storage_path': IMAGE_STORAGE_PATH,
            'storage_exists': storage_exists
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
