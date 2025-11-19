"""
Whiteboard Image Upload API
Handles image uploads for NoteBlock journal entries
"""

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from functools import wraps
import logging
import os
import io
from PIL import Image
import uuid
import jwt
import hashlib

logger = logging.getLogger(__name__)

# Create blueprint
whiteboard_images_bp = Blueprint('whiteboard_images', __name__, url_prefix='/api/v2/whiteboards/images')

# Configuration
UPLOAD_FOLDER = os.path.join('data', 'whiteboard_images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_IMAGE_WIDTH = 1200
MAX_IMAGE_HEIGHT = 1200
WEBP_QUALITY = 85


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
    Compatible with existing auth system
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.info("🔐 JWT Authentication Check")
        token = None
        
        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            logger.info(f"📨 Authorization header present: {auth_header[:50]}...")
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
                logger.info(f"✅ Token extracted: {token[:20]}...")
            except IndexError:
                logger.error("❌ Invalid authorization header format")
                return jsonify({
                    'success': False,
                    'error': 'Invalid authorization header format'
                }), 401
        else:
            logger.error("❌ No Authorization header found")
            logger.info(f"📋 Available headers: {list(request.headers.keys())}")
        
        if not token:
            logger.error("❌ No token provided")
            return jsonify({
                'success': False,
                'error': 'Authentication token required'
            }), 401
        
        try:
            # Decode JWT token
            logger.info("🔍 Decoding JWT token...")
            payload = jwt.decode(token, get_jwt_secret(), algorithms=['HS256'])
            logger.info(f"✅ Token decoded successfully. Payload keys: {list(payload.keys())}")
            
            # Try both 'sub' (standard) and 'user_id' (legacy) for compatibility
            request.user_id = payload.get('sub') or payload.get('user_id')
            
            if not request.user_id:
                logger.error(f"❌ No user ID in token payload. Payload: {payload}")
                return jsonify({
                    'success': False,
                    'error': 'Invalid token payload - missing user ID'
                }), 401
            
            logger.info(f"✅ User authenticated: {request.user_id}")
                
        except jwt.ExpiredSignatureError:
            logger.error("❌ Token has expired")
            return jsonify({
                'success': False,
                'error': 'Token has expired'
            }), 401
        except jwt.InvalidTokenError as e:
            logger.error(f"❌ Invalid token: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Invalid token: {str(e)}'
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated_function


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def ensure_upload_directory():
    """Create upload directory if it doesn't exist"""
    try:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        logger.info(f"✅ Whiteboard image storage ready: {UPLOAD_FOLDER}")
    except Exception as e:
        logger.error(f"❌ Failed to create upload directory: {e}")
        raise


@whiteboard_images_bp.route('/upload', methods=['POST'])
@jwt_required_v2
def upload_image():
    """
    Upload image for NoteBlock
    
    Request:
        POST /api/v2/whiteboards/images/upload
        Content-Type: multipart/form-data
        Body: {
            "image": <file>,
            "whiteboard_id": 123 (optional)
        }
        
    Returns:
        {
            "success": true,
            "data": {
                "url": "/api/v2/whiteboards/images/abc123.webp",
                "filename": "abc123.webp",
                "size": 125000,
                "width": 800,
                "height": 600
            }
        }
    """
    logger.info("=" * 60)
    logger.info("🖼️  IMAGE UPLOAD REQUEST RECEIVED")
    logger.info("=" * 60)
    
    try:
        user_id = request.user_id
        logger.info(f"👤 User ID: {user_id}")
        logger.info(f"📋 Request files: {list(request.files.keys())}")
        logger.info(f"📋 Request form: {dict(request.form)}")
        
        # Check if image file is present
        if 'image' not in request.files:
            logger.error("❌ No 'image' field in request.files")
            return jsonify({
                'success': False,
                'error': 'No image file provided'
            }), 400
        
        file = request.files['image']
        logger.info(f"📎 File received: {file.filename}")
        
        # Check if file has a filename
        if file.filename == '':
            logger.error("❌ Empty filename")
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Check file type
        if not allowed_file(file.filename):
            logger.error(f"❌ Invalid file type: {file.filename}")
            return jsonify({
                'success': False,
                'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        logger.info(f"✅ File type valid: {file.filename}")
        
        # Read file into memory
        file_data = file.read()
        file_size = len(file_data)
        logger.info(f"📏 File size: {file_size} bytes ({file_size / 1024:.1f} KB)")
        
        # Check file size
        if file_size > MAX_FILE_SIZE:
            logger.error(f"❌ File too large: {file_size} > {MAX_FILE_SIZE}")
            return jsonify({
                'success': False,
                'error': f'File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB'
            }), 400
        
        # Process image
        try:
            img = Image.open(io.BytesIO(file_data))
            original_width, original_height = img.size
            
            # Convert RGBA to RGB if needed
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background
            
            # Resize if too large
            if original_width > MAX_IMAGE_WIDTH or original_height > MAX_IMAGE_HEIGHT:
                img.thumbnail((MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT), Image.Resampling.LANCZOS)
                logger.info(f"📏 Resized image from {original_width}×{original_height} to {img.size[0]}×{img.size[1]}")
            
            # Generate unique filename
            unique_id = str(uuid.uuid4())[:12]
            filename = f"noteblock_{user_id}_{unique_id}.webp"
            
            # Ensure upload directory exists
            ensure_upload_directory()
            
            # Save as WebP
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            img.save(
                filepath,
                'WEBP',
                quality=WEBP_QUALITY,
                method=6  # Slowest but best compression
            )
            
            # Get file size
            file_size = os.path.getsize(filepath)
            
            logger.info(f"✅ Image uploaded: {filename} ({file_size} bytes, {img.size[0]}×{img.size[1]})")
            
            return jsonify({
                'success': True,
                'data': {
                    'url': f'/api/v2/whiteboards/images/{filename}',
                    'filename': filename,
                    'size': file_size,
                    'width': img.size[0],
                    'height': img.size[1]
                }
            }), 200
            
        except Exception as e:
            logger.error(f"❌ Error processing image: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to process image'
            }), 500
        
    except Exception as e:
        logger.error(f"❌ Error uploading image: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@whiteboard_images_bp.route('/<filename>')
def serve_image(filename):
    """
    Serve uploaded whiteboard image
    
    Example:
        GET /api/v2/whiteboards/images/noteblock_123_abc.webp
        
    Returns:
        WebP image file
    """
    try:
        from flask import send_from_directory
        
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
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(filepath):
            logger.warning(f"⚠️ Image not found: {filename}")
            return jsonify({
                'success': False,
                'error': 'Image not found'
            }), 404
        
        # Serve the file
        return send_from_directory(
            UPLOAD_FOLDER,
            filename,
            mimetype='image/webp',
            max_age=31536000  # Cache for 1 year
        )
        
    except Exception as e:
        logger.error(f"❌ Error serving image {filename}: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
