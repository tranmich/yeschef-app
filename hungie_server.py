#!/usr/bin/env python3
"""
Hungie Backend Server - Enhanced with Meal Planning System
Complete recipe search, meal planning, and grocery list functionality
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json, os
import psycopg2
import psycopg2.extras
import openai
from dotenv import load_dotenv
from pathlib import Path
import logging
from datetime import datetime

# Configure logging immediately after basic imports
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Import authentication system
from auth_system import AuthenticationSystem
from auth_routes import create_auth_routes

# Import template recipe system
try:
    from template_recipe_system import TemplateRecipeSystem
    TEMPLATE_SYSTEM_AVAILABLE = True
    logger.info("✅ Template recipe system loaded")
except ImportError as e:
    TEMPLATE_SYSTEM_AVAILABLE = False
    logger.warning(f"⚠️ Template recipe system not available: {e}")

# Import admin system
try:
    from admin_system import AdminSystem
    from admin_routes import create_admin_routes
    ADMIN_SYSTEM_AVAILABLE = True
    logger.info("✅ Admin system loaded")
except ImportError as e:
    ADMIN_SYSTEM_AVAILABLE = False
    logger.warning(f"⚠️ Admin system not available: {e}")

# Import database migrations (extracted for cleaner code) - with fallback
try:
    from database_migrations import (
        run_intelligence_migration,
        run_schema_migration_endpoint,
        add_sample_recipes,
        check_database_info
    )
    DATABASE_MIGRATIONS_AVAILABLE = True
    logger.info("✅ Database migrations module loaded")
except ImportError as e:
    DATABASE_MIGRATIONS_AVAILABLE = False
    logger.warning(f"⚠️ Database migrations not available: {e}")
    # Define fallback functions
    def run_intelligence_migration():
        return {"error": "Database migrations module not available"}
    def run_schema_migration_endpoint():
        return {"error": "Database migrations module not available"}
    def add_sample_recipes():
        return {"error": "Database migrations module not available"}
    def check_database_info():
        return {"error": "Database migrations module not available"}

# Import unified search system (Day 4 Enhancement - Full Integration)
from core_systems.universal_search import UniversalSearchEngine

# Import recipe import system (Day 1 Implementation - Universal Import System)
try:
    from core_systems.recipe_importer import UniversalRecipeImporter, ImportRequest, ImportResult
    RECIPE_IMPORT_AVAILABLE = True
    logger.info("✅ Universal recipe import system loaded")
except ImportError as e:
    RECIPE_IMPORT_AVAILABLE = False
    logger.warning(f"⚠️ Recipe import system not available: {e}")

# Import meal planning systems
try:
    from core_systems.meal_planning_system import MealPlanningSystem
    from core_systems.grocery_list_generator import GroceryListGenerator
    MEAL_PLANNING_AVAILABLE = True
    logger.info("✅ Meal planning systems imported successfully")
except ImportError as e:
    MEAL_PLANNING_AVAILABLE = False
    logger.warning(f"⚠️ Meal planning systems not available: {e}")

# Load environment variables
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    logger.info("✅ OpenAI client initialized")
else:
    client = None
    logger.warning("⚠️ OpenAI API key not found")

# Chef personality for AI responses
CHEF_PERSONALITY = """You are Hungie, an enthusiastic and knowledgeable personal chef assistant. You're passionate about food, cooking, and helping people discover amazing recipes. You always maintain a friendly, encouraging tone and love to share cooking tips. When talking about recipes, you're descriptive and make food sound delicious. You occasionally use food emojis and express excitement about cooking. Always end your responses with "Yes, Chef! 🍴" to maintain your chef personality."""

# Initialize Flask app
app = Flask(__name__)

# Configure CORS properly - use only one method
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "https://yeschef-app.vercel.app"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Initialize Authentication System
try:
    # auth_system = AuthenticationSystem(app)  # Moved to after DB init
    # auth_routes = create_auth_routes(auth_system)  # Moved to after DB init
    # app.register_blueprint(auth_routes)  # Moved to after DB init
    logger.info("Authentication system will be initialized after DB setup")
    logger.info("🔐 Authentication system initialized and routes registered")
except Exception as e:
    logger.error(f"❌ Failed to initialize authentication system: {e}")
    auth_system = None

def check_authentication():
    """
    Check if request has valid JWT authentication
    Returns (user_id, error_response, status_code) tuple
    """
    print(f"🔐 Authentication check called for {request.method} {request.path}")
    try:
        # Get Authorization header
        auth_header = request.headers.get('Authorization')
        print(f"🔐 Authorization header: {auth_header}")
        if not auth_header:
            print("❌ Missing Authorization header")
            return None, jsonify({'error': 'Missing Authorization header'}), 401
        
        # Extract token
        if not auth_header.startswith('Bearer '):
            print("❌ Invalid Authorization header format")
            return None, jsonify({'error': 'Invalid Authorization header format'}), 401
        
        token = auth_header.split(' ')[1]
        print(f"🔐 Token extracted: {token[:20]}...")
        
        # Try to use the auth_system's JWT manager if available
        if auth_system and hasattr(auth_system, 'jwt'):
            try:
                print("🔐 Using auth_system JWT manager")
                from flask_jwt_extended import decode_token
                with auth_system.app.app_context():
                    decoded_token = decode_token(token)
                    user_id = decoded_token['sub']
                    # Convert to integer if it's a string representation of a number
                    if isinstance(user_id, str) and user_id.isdigit():
                        user_id = int(user_id)
                    print(f"✅ Token valid via auth_system, user_id: {user_id}")
                    return user_id, None, None
            except Exception as e:
                print(f"❌ Auth system validation failed: {e}")
                # Fall through to manual validation
        
        # Fallback: Manual JWT validation with same secret logic as AuthenticationSystem
        try:
            import jwt
            import json
            import base64
            
            # Use exact same secret generation as AuthenticationSystem
            jwt_secret = os.getenv('JWT_SECRET_KEY')
            if not jwt_secret:
                database_url = os.getenv('DATABASE_URL', '')
                if database_url:
                    import hashlib
                    jwt_secret = hashlib.sha256(database_url.encode()).hexdigest()
                else:
                    jwt_secret = 'dev-secret-key-for-local-testing-only'
            
            print(f"🔐 Using JWT secret: {jwt_secret[:10]}...")
            
            # First, try to decode without verification to see the payload
            try:
                payload_part = token.split('.')[1]
                # Add padding if needed
                padding_needed = len(payload_part) % 4
                if padding_needed:
                    payload_part += '=' * (4 - padding_needed)
                    
                payload_bytes = base64.urlsafe_b64decode(payload_part)
                payload = json.loads(payload_bytes)
                print(f"🔐 Decoded payload: {payload}")
                
                user_id = payload.get('sub')
                print(f"🔐 Raw user_id from payload: {user_id} (type: {type(user_id)})")
                
                # Now verify the signature manually
                try:
                    jwt.decode(token, jwt_secret, algorithms=['HS256'], options={"verify_sub": False})
                    print("✅ JWT signature verified successfully")
                except Exception as sig_error:
                    print(f"❌ JWT signature verification failed: {sig_error}")
                    return None, jsonify({'error': f'Invalid token signature: {str(sig_error)}'}), 401
                
                # Handle both string and integer user IDs
                if isinstance(user_id, str):
                    if user_id.isdigit():
                        user_id = int(user_id)
                    else:
                        print(f"❌ Non-numeric string user_id: {user_id}")
                        return None, jsonify({'error': 'Invalid token payload'}), 401
                elif isinstance(user_id, int):
                    pass  # Already an integer, which is what we want
                else:
                    print(f"❌ Invalid user_id type: {type(user_id)}")
                    return None, jsonify({'error': 'Invalid token payload'}), 401
                
                print(f"✅ Token valid via manual validation, user_id: {user_id} (type: {type(user_id)})")
                if not user_id:
                    print("❌ Token payload missing user_id")
                    return None, jsonify({'error': 'Invalid token payload'}), 401
                return user_id, None, None
                
            except Exception as decode_error:
                print(f"❌ Token payload decoding failed: {decode_error}")
                return None, jsonify({'error': f'Invalid token format: {str(decode_error)}'}), 401
        except jwt.InvalidTokenError as e:
            print(f"❌ Token validation failed: {e}")
            return None, jsonify({'error': f'Invalid token: {str(e)}'}), 401
    
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None, jsonify({'error': f'Authentication error: {str(e)}'}), 500

# Enhanced systems - with proper error handling
UNIVERSAL_SEARCH_AVAILABLE = False

# Global Universal Search Engine
search_engine = None

# Initialize Universal Search Engine (Day 4 Full Integration)
try:
    from core_systems.universal_search import UniversalSearchEngine
    # Initialize universal search engine
    search_engine = UniversalSearchEngine()
    UNIVERSAL_SEARCH_AVAILABLE = True
    logger.info("🔍 Universal search engine initialized - ALL search functions consolidated")
except ImportError as e:
    logger.warning(f"⚠️ Universal search engine not available: {e}")
    search_engine = None
except Exception as e:
    logger.error(f"❌ Failed to initialize universal search engine: {e}")
    search_engine = None

# Session management (disabled)
session_manager = None

# Database connection
def get_db_connection():
    """Get PostgreSQL database connection with Railway-optimized approach"""
    import psycopg2
    import psycopg2.extras

    # Railway-proven public URL that works from local testing
    public_database_url = "postgresql://postgres:udQLpljdqTYmESmntwzmwDcOlBVbqlJG@shuttle.proxy.rlwy.net:31331/railway"

    try:
        logger.info("🔄 Connecting to PostgreSQL via Railway public URL...")
        conn = psycopg2.connect(public_database_url)
        conn.cursor_factory = psycopg2.extras.RealDictCursor
        logger.info("✅ Connected to PostgreSQL database successfully")
        return conn
    except Exception as e:
        logger.error(f"❌ PostgreSQL connection failed: {e}")
        logger.error(f"❌ Connection string used: {public_database_url[:50]}...")
        raise Exception(f"Database connection failed: {str(e)}")

def init_db():
    """Initialize PostgreSQL database tables with complete schema"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # PostgreSQL schema with ALL required columns for migrated recipes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recipes (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                ingredients TEXT,
                instructions TEXT,
                category TEXT,
                book_id INTEGER,
                page_number INTEGER,
                servings TEXT,
                hands_on_time TEXT,
                total_time TEXT,
                url TEXT,
                date_saved TEXT,
                why_this_works TEXT,
                chapter TEXT,
                chapter_number INTEGER,
                image_url TEXT,
                source TEXT,
                flavor_profile TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()
        logger.info("? Database tables initialized successfully")

    except Exception as e:
        logger.error(f"? Database initialization error: {e}")
        if 'conn' in locals():
            conn.close()
        raise

# Core search function - ENHANCED WITH INTELLIGENT INGREDIENT RECOGNITION
def search_recipes_by_query(query, limit=50):
    """
    Search recipes by query - UNIVERSAL SEARCH INTEGRATION
    
    ✨ CONSOLIDATION: Now uses UniversalSearchEngine instead of scattered logic
    🎯 FEATURES: Intelligence filtering, smart explanations, session awareness
    📈 PERFORMANCE: Optimized queries with intelligence metadata
    """
    try:
        logger.info(f"🔍 Universal Search (consolidated) for: '{query}' (limit: {limit})")

        # Use universal search engine - SINGLE SOURCE OF TRUTH
        if search_engine:
            search_result = search_engine.unified_intelligent_search(
                query=query,
                session_memory=None,
                user_pantry=[],
                exclude_ids=[],
                limit=limit,
                include_explanations=True
            )

            if search_result['success']:
                recipes = search_result['recipes']
                logger.info(f"🔍 Universal search found {len(recipes)} recipes with intelligence")

                # Transform to expected format for API compatibility
                enhanced_recipes = []
                for recipe in recipes:
                    enhanced_recipe = {
                        'id': recipe['id'],
                        'title': recipe['title'],
                        'name': recipe['title'],  # Frontend compatibility
                        'description': recipe['description'] or '',
                        'servings': recipe['servings'] or '4 servings',
                        'prep_time': recipe.get('prep_time', ''),
                        'cook_time': recipe.get('cook_time', '30 minutes'),
                        'total_time': recipe['total_time'] or '30 minutes',
                        'ingredients': recipe['ingredients'] or '',
                        'instructions': recipe['instructions'] or '',
                        'source': recipe['source'] or 'Recipe Collection',
                        'category': recipe['category'] or 'Main Course',
                        'recipe_types': recipe.get('recipe_types', []),
                        # NEW: Intelligence metadata from universal search
                        'explanations': recipe.get('explanations', ''),
                        'meal_role': recipe.get('meal_role'),
                        'is_easy': recipe.get('is_easy', False),
                        'is_one_pot': recipe.get('is_one_pot', False),
                        'kid_friendly': recipe.get('kid_friendly', False),
                        'time_min': recipe.get('time_min'),
                        'intelligence_enabled': True,
                        'universal_search': True,
                        'detected_preferences': search_result.get('search_metadata', {})
                    }
                    enhanced_recipes.append(enhanced_recipe)

                logger.info(f"🎯 Universal search returning {len(enhanced_recipes)} enhanced recipes")
                return enhanced_recipes
            else:
                logger.warning(f"Universal search failed: {search_result.get('error', 'Unknown error')}")

        # This should never happen in production
        logger.error("⚠️ Universal search engine not available - this is a configuration error")
        return []

    except Exception as e:
        logger.error(f"Universal search integration error: {e}")
        return []

def get_recipe_by_id(recipe_id):
    """Get a single recipe by ID - PostgreSQL version"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # PostgreSQL syntax with %s placeholder
        cursor.execute("""
            SELECT * FROM recipes r
            WHERE r.id = %s
        """, (recipe_id,))

        row = cursor.fetchone()
        if not row:
            return None

        recipe = {
            'id': row['id'],
            'title': row['title'],
            'name': row['title'],
            'description': row['description'] or '',
            'servings': row['servings'] or '4 servings',
            'prep_time': row['hands_on_time'] or '',
            'cook_time': row['total_time'] or '30 minutes',
            'total_time': row['total_time'] or '30 minutes',
            'ingredients': row['ingredients'] or '',
            'instructions': row['instructions'] or ''
        }

        # Parse JSON fields
        for field in ['ingredients', 'instructions']:
            try:
                if recipe[field] and isinstance(recipe[field], str):
                    parsed = json.loads(recipe[field])
                    if isinstance(parsed, list):
                        recipe[field] = parsed
            except (json.JSONDecodeError, TypeError):
                pass

        # NEW: Add recipe type classification for individual recipes using universal search
        try:
            from core_systems.universal_search import UniversalSearchEngine
            engine = UniversalSearchEngine()
            recipe_types = engine.classify_recipe_types(recipe['title'],
                                                      ' '.join(recipe['instructions']) if isinstance(recipe['instructions'], list)
                                                      else str(recipe['instructions']))
            recipe['recipe_types'] = recipe_types
            logger.info(f"🏷️ Recipe '{recipe['title']}' classified as: {recipe_types}")
        except Exception as e:
            logger.warning(f"⚠️ Recipe type classification failed: {e}")
            recipe['recipe_types'] = []

        conn.close()
        return recipe

    except Exception as e:
        logger.error(f"Get recipe error: {e}")
        return None

# API Routes
@app.route('/')
def api_root():
    """API root endpoint - DEPLOYMENT TEST"""
    return jsonify({
        'message': 'Hungie API Server',
        'status': 'healthy',
        'deployment_test': '2025-08-17-universal-search-v3',
        'universal_search_ready': search_engine is not None,
        'commit_version': '5bda815',
        'endpoints': {
            'recipes': '/api/recipes',
            'search': '/api/search',
            'auth': '/api/auth',
            'health': '/api/health',
            'version': '/api/version'
        }
    })

@app.route('/api/recipes', methods=['POST'])
def create_recipe():
    """Create a new recipe"""
    try:
        data = request.get_json()
        if not data or not data.get('title'):
            return jsonify({
                'success': False,
                'error': 'Recipe title is required'
            }), 400

        # Insert recipe into database
        conn = get_db_connection()
        cursor = conn.cursor()

        # PostgreSQL syntax with RETURNING
        cursor.execute('''
            INSERT INTO recipes (title, description, ingredients, instructions, image_url, source, category, flavor_profile)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (
            data.get('title', ''),
            data.get('description', ''),
            data.get('ingredients', ''),
            data.get('instructions', ''),
            data.get('image_url', ''),
            data.get('source', ''),
            data.get('category', ''),
            data.get('flavor_profile', '')
        ))
        recipe_id = cursor.fetchone()['id']

        conn.commit()
        conn.close()

        logger.info(f"? Recipe created: {data.get('title')} (ID: {recipe_id})")

        return jsonify({
            'success': True,
            'data': {
                'id': recipe_id,
                'message': 'Recipe created successfully'
            }
        }), 201

    except Exception as e:
        logger.error(f"Create recipe API error: {e}")
        return jsonify({
            'success': False,
            'error': f'Database error: {str(e)}'
        }), 500

@app.route('/api/recipes/<recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    """Get a single recipe"""
    try:
        recipe = get_recipe_by_id(recipe_id)
        if recipe:
            return jsonify({
                'success': True,
                'data': recipe
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Recipe not found'
            }), 404
    except Exception as e:
        logger.error(f"Get recipe API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# TEMPLATE RECIPE SYSTEM ENDPOINTS
# ============================================================================

@app.route('/api/user/recipes', methods=['GET'])
def get_user_recipes():
    """Get user's personal recipe collection with admin override"""
    try:
        user_id, error_response, status_code = check_authentication()
        if error_response:
            return error_response, status_code
        
        if not template_system:
            return jsonify({
                'success': False,
                'error': 'Template system not available'
            }), 503
        
        # Check if user is admin - CLEAN VERSION
        is_admin = False
        admin_debug_info = {"detected": False, "email": None, "token_valid": False, "user_id": None}
        
        try:
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                # Use the working authentication method
                user_id, error_response, status_code = check_authentication()
                if user_id:
                    admin_debug_info["token_valid"] = True
                    admin_debug_info["user_id"] = user_id
                    
                    # Get user email from database
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute('SELECT email FROM users WHERE id = %s', (user_id,))
                    result = cursor.fetchone()
                    conn.close()
                    
                    if result:
                        # Handle both RealDictRow and tuple results
                        if hasattr(result, 'get'):
                            user_email = result['email'].lower().strip()
                        else:
                            user_email = result[0].lower().strip()
                            
                        admin_debug_info["email"] = user_email
                        
                        # Check if user is admin
                        is_admin = (user_email == 'tran.mich@gmail.com')
                        admin_debug_info["detected"] = is_admin
                        
                        if is_admin:
                            logger.info(f"� Admin access granted for: {user_email}")
                    else:
                        logger.error(f"❌ User ID {user_id} not found in database")
                        
        except Exception as e:
            logger.error(f"❌ Admin detection error: {e}")
        
        if is_admin:
            # Admin sees ALL recipes in the database for curation
            logger.info(f"🔧 Admin requesting all recipes for curation")
            try:
                conn = get_db_connection()
                cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                
                cursor.execute('''
                    SELECT r.*, 
                           CASE WHEN r.is_template THEN 'template' 
                                WHEN r.template_id IS NOT NULL THEN 'template_copy' 
                                ELSE 'original' END as recipe_type,
                           u.email as owner_email
                    FROM recipes r
                    LEFT JOIN users u ON r.user_id = u.id
                    ORDER BY r.created_at DESC
                ''')
                
                all_recipes = [dict(row) for row in cursor.fetchall()]
                conn.close()
                
                logger.info(f"🔧 Admin retrieved {len(all_recipes)} total recipes for curation")
                return jsonify({
                    'success': True,
                    'data': all_recipes,
                    'count': len(all_recipes),
                    'admin_access': True,
                    'message': f'All {len(all_recipes)} recipes available for admin curation'
                })
                
            except Exception as e:
                logger.error(f"❌ Failed to get admin recipes: {e}")
                return jsonify({'success': False, 'error': 'Failed to retrieve admin recipes'}), 500
        else:
            # Regular users get their personal collection (limited to 500)
            recipes = template_system.get_user_recipes(user_id)
            
            # Apply 500 recipe limit for regular users
            if len(recipes) > 500:
                recipes = recipes[:500]
                limited_message = f"Showing first 500 of your recipes"
            else:
                limited_message = f"All {len(recipes)} personal recipes"
            
            logger.info(f"👤 User {user_id} retrieved {len(recipes)} personal recipes")
            return jsonify({
                'success': True,
                'data': recipes,
                'count': len(recipes),
                'admin_access': False,
                'message': limited_message
            })
        
    except Exception as e:
        logger.error(f"Get user recipes error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/recipes/<recipe_id>/edit', methods=['POST'])
def edit_recipe_copy_on_write(recipe_id):
    """Edit a recipe - creates user copy if editing a template"""
    try:
        user_id, error_response, status_code = check_authentication()
        if error_response:
            return error_response, status_code
        
        if not template_system:
            return jsonify({
                'success': False,
                'error': 'Template system not available'
            }), 503
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Check if we need to create a copy (editing a template)
        actual_recipe_id = template_system.copy_template_on_edit(user_id, int(recipe_id))
        
        if not actual_recipe_id:
            return jsonify({
                'success': False,
                'error': 'Failed to prepare recipe for editing'
            }), 500
        
        # Now update the recipe (either original user recipe or new copy)
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute('''
            UPDATE recipes SET
                title = %s,
                description = %s,
                ingredients = %s,
                instructions = %s,
                category = %s,
                meal_role = %s,
                prep_time = %s,
                cook_time = %s,
                servings = %s,
                source_url = %s,
                confidence = %s
            WHERE id = %s AND user_id = %s
        ''', (
            data.get('title'),
            data.get('description'),
            data.get('ingredients'),
            data.get('instructions'),
            data.get('category'),
            data.get('meal_role'),
            data.get('prep_time'),
            data.get('cook_time'),
            data.get('servings'),
            data.get('source_url'),
            data.get('confidence'),
            actual_recipe_id,
            user_id
        ))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Recipe not found or permission denied'
            }), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'recipe_id': actual_recipe_id,
            'message': 'Recipe updated successfully',
            'was_copied': actual_recipe_id != int(recipe_id)
        })
        
    except Exception as e:
        logger.error(f"Edit recipe error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/admin/template-stats', methods=['GET'])
def get_template_system_stats():
    """Get statistics about the template system (admin only)"""
    try:
        if not template_system:
            return jsonify({
                'success': False,
                'error': 'Template system not available'
            }), 503
        
        stats = template_system.get_system_stats()
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"Template stats error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# END TEMPLATE RECIPE SYSTEM ENDPOINTS
# ============================================================================

@app.route('/api/search', methods=['GET'])
def search_recipes():
    """
    Search for recipes by query - UNIVERSAL SEARCH INTEGRATION
    
    ✨ CONSOLIDATION: Now uses UniversalSearchEngine for consistency
    🎯 FEATURES: Intelligence filtering, smart explanations, session awareness
    📈 PERFORMANCE: Optimized queries with intelligence metadata
    """
    try:
        query = request.args.get('q', '').strip()
        logger.info(f"🌐 Universal API Search request for: '{query}' [UNIVERSAL SEARCH ACTIVE]")

        if not query:
            return jsonify({
                'success': False,
                'error': 'Query parameter is required'
            }), 400

        # Use universal search engine - SINGLE SOURCE OF TRUTH
        # Admin override: No limits for tran.mich@gmail.com
        # Regular users: Max 500 recipes (configurable limit)
        # For general recipe loading (query='recipe'), use higher limit but with admin override
        
        # Check if user is admin
        is_admin = False
        try:
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                user_data = auth_system.validate_token(token)
                if user_data['valid']:
                    user_email = user_data.get('email', '').lower()
                    is_admin = (user_email == 'tran.mich@gmail.com')
        except:
            pass  # Non-critical - default to non-admin
        
        if is_admin:
            # Admin sees ALL recipes with no limits
            search_limit = 10000 if query.lower() == 'recipe' else 1000
            logger.info(f"🔧 Admin access detected - using unlimited search (limit: {search_limit})")
        else:
            # Regular users get limited results
            search_limit = 500 if query.lower() == 'recipe' else 50
            logger.info(f"👤 Regular user access - using limited search (limit: {search_limit})")
        
        recipes = search_recipes_by_query(query, limit=search_limit)
        logger.info(f"🌐 Universal API returning {len(recipes)} enhanced recipes (limit: {search_limit})")

        # Extract enhanced search metadata
        search_metadata = {
            'query': query,
            'total_results': len(recipes),
            'universal_search_used': True,
            'intelligence_enabled': True,
            'features': ['smart_explanations', 'intelligence_filtering', 'session_awareness']
        }

        # Get metadata from universal search results
        if recipes:
            first_recipe = recipes[0]
            search_metadata.update({
                'detected_preferences': first_recipe.get('detected_preferences', {}),
                'meal_roles_found': list(set(r.get('meal_role') for r in recipes if r.get('meal_role'))),
                'easy_recipes': len([r for r in recipes if r.get('is_easy', False)]),
                'one_pot_recipes': len([r for r in recipes if r.get('is_one_pot', False)]),
                'kid_friendly_recipes': len([r for r in recipes if r.get('kid_friendly', False)])
            })

        return jsonify({
            'success': True,
            'data': recipes,
            'metadata': search_metadata,
            'universal_search': True  # Flag for frontend to know this is enhanced
        })

    except Exception as e:
        logger.error(f"Universal Search API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'universal_search': False
        }), 500

@app.route('/api/search/intelligent', methods=['POST', 'OPTIONS'])
def intelligent_session_search():
    """
    Intelligent session-aware search - UNIVERSAL SEARCH INTEGRATION
    
    ✨ CONSOLIDATION: Now uses UniversalSearchEngine for session awareness
    🎯 FEATURES: Intelligence filtering, smart explanations, session memory
    📈 PERFORMANCE: Optimized queries with universal search engine
    """
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        session_id = data.get('session_id', 'default')
        shown_recipe_ids = data.get('shown_recipe_ids', [])
        page_size = data.get('page_size', 5)
        
        # Extract pantry data from request
        user_pantry = data.get('user_pantry', [])
        pantry_first = data.get('pantry_first', False)

        logger.info(f"🧠 Universal intelligent search: '{query}' | Session: {session_id} | Excluding: {len(shown_recipe_ids)} recipes")
        
        # Debug pantry integration
        if user_pantry:
            logger.info(f"🥫 Intelligent search - Pantry data received: {[item.get('name') for item in user_pantry]} (pantry_first: {pantry_first})")
        else:
            logger.info("📝 Intelligent search - No pantry data provided")

        if not query:
            return jsonify({
                'success': False,
                'error': 'Query parameter is required'
            }), 400

        # Try universal search engine first
        if search_engine:
            try:
                search_result = search_engine.unified_intelligent_search(
                    query=query,
                    session_memory={'session_id': session_id, 'shown_recipes': shown_recipe_ids},
                    user_pantry=user_pantry,
                    exclude_ids=shown_recipe_ids,
                    limit=page_size * 3,  # Get more to account for exclusions
                    include_explanations=True,
                    filters={'pantry_first': pantry_first}
                )

                if search_result['success']:
                    all_recipes = search_result['recipes']

                    # Format for API compatibility
                    formatted_recipes = []
                    for recipe in all_recipes:
                        formatted_recipe = {
                            'id': recipe['id'],
                            'title': recipe['title'],
                            'name': recipe['title'],
                            'description': recipe['description'] or '',
                            'servings': recipe['servings'] or '4 servings',
                            'prep_time': recipe.get('prep_time', ''),
                            'cook_time': recipe.get('cook_time', '30 minutes'),
                            'total_time': recipe['total_time'] or '30 minutes',
                            'ingredients': recipe['ingredients'] or '',
                            'instructions': recipe['instructions'] or '',
                            'source': recipe['source'] or 'Recipe Collection',
                            'category': recipe.get('category', 'Main Course'),
                            # NEW: Intelligence metadata
                            'explanations': recipe.get('explanations', ''),
                            'meal_role': recipe.get('meal_role'),
                            'is_easy': recipe.get('is_easy', False),
                            'is_one_pot': recipe.get('is_one_pot', False),
                            'kid_friendly': recipe.get('kid_friendly', False),
                            'universal_search': True,
                            'session_aware': True
                        }
                        formatted_recipes.append(formatted_recipe)

                    # Return the next batch
                    next_batch = formatted_recipes[:page_size]

                    logger.info(f"🧠 Universal intelligent search found {len(all_recipes)} total matches, returning {len(next_batch)} recipes")

                    return jsonify({
                        'success': True,
                        'recipes': next_batch,
                        'total_available': len(all_recipes),
                        'has_more': len(all_recipes) > page_size,
                        'shown_count': len(shown_recipe_ids),
                        'session_id': session_id,
                        'search_metadata': {
                            'query': query,
                            'universal_search_used': True,
                            'intelligence_enabled': True,
                            'session_aware': True,
                            'exclusions_applied': len(shown_recipe_ids),
                            'search_explanations': search_result.get('search_metadata', {})
                        }
                    })
                else:
                    logger.warning(f"Universal intelligent search failed: {search_result.get('error', 'Unknown error')}")
            except Exception as e:
                logger.error(f"⚠️ Universal search engine error: {str(e)}")

        # FALLBACK: Use basic search with session awareness
        logger.warning("⚠️ Falling back to basic search with session awareness")

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Build search query with exclusions
            where_conditions = []
            params = []

            if query:
                where_conditions.append("(LOWER(r.title) LIKE %s OR LOWER(r.ingredients) LIKE %s)")
                search_term = f"%{query.lower()}%"
                params.extend([search_term, search_term])

            # Add exclusions
            if shown_recipe_ids:
                placeholders = ','.join(['%s' for _ in shown_recipe_ids])
                where_conditions.append(f"r.id NOT IN ({placeholders})")
                params.extend(shown_recipe_ids)

            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"

            # If no new recipes found with exclusions, remove exclusions (fallback behavior you requested)
            fallback_query = f"""
            SELECT DISTINCT r.id, r.title, r.description, r.servings, r.total_time,
                   r.ingredients, r.instructions, r.source, r.category
            FROM recipes r
            WHERE {where_clause}
            ORDER BY r.id
            LIMIT %s
            """
            params.append(page_size * 2)

            cursor.execute(fallback_query, params)
            recipes = cursor.fetchall()

            # If no results and we had exclusions, try again without exclusions
            if not recipes and shown_recipe_ids and query:
                logger.info(f"🔄 No new {query} recipes found, showing all {query} recipes as fallback")
                where_conditions = ["(LOWER(r.title) LIKE %s OR LOWER(r.ingredients) LIKE %s)"]
                search_term = f"%{query.lower()}%"
                params = [search_term, search_term, page_size]

                fallback_query = f"""
                SELECT DISTINCT r.id, r.title, r.description, r.servings, r.total_time,
                       r.ingredients, r.instructions, r.source, r.category
                FROM recipes r
                WHERE {where_conditions[0]}
                ORDER BY r.id
                LIMIT %s
                """

                cursor.execute(fallback_query, params)
                recipes = cursor.fetchall()

            # Format recipes
            formatted_recipes = []
            for recipe in recipes:
                formatted_recipe = {
                    'id': recipe['id'],
                    'title': recipe['title'],
                    'name': recipe['title'],
                    'description': recipe['description'] or '',
                    'servings': recipe['servings'] or '4 servings',
                    'total_time': recipe['total_time'] or '30 minutes',
                    'ingredients': recipe['ingredients'] or '',
                    'instructions': recipe['instructions'] or '',
                    'source': recipe['source'] or 'Recipe Collection',
                    'category': recipe['category'] or 'Main Course',
                    'universal_search': False,
                    'fallback_search': True
                }
                formatted_recipes.append(formatted_recipe)

            conn.close()

            logger.info(f"🔄 Fallback search found {len(formatted_recipes)} recipes for '{query}'")

            return jsonify({
                'success': True,
                'recipes': formatted_recipes,
                'total_available': len(formatted_recipes),
                'has_more': False,
                'shown_count': len(shown_recipe_ids),
                'session_id': session_id,
                'search_metadata': {
                    'query': query,
                    'universal_search_used': False,
                    'fallback_used': True,
                    'exclusions_applied': len(shown_recipe_ids)
                }
            })

        except Exception as fallback_error:
            logger.error(f"❌ Fallback search also failed: {str(fallback_error)}")
            return jsonify({
                'success': False,
                'error': f'Both universal and fallback search failed: {str(fallback_error)}',
                'universal_search': False
            }), 500

    except Exception as e:
        logger.error(f"?? Intelligent search error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def search_recipes_with_exclusions(query, exclude_ids=None):
    """
    Enhanced search that excludes already shown recipes - UNIVERSAL SEARCH INTEGRATION
    
    ✨ CONSOLIDATION: Now uses UniversalSearchEngine for consistency
    🎯 FEATURES: Intelligence filtering, smart explanations, exclusion logic
    📈 PERFORMANCE: Optimized queries with universal search engine
    """
    try:
        # Use universal search engine - SINGLE SOURCE OF TRUTH
        if search_engine:
            search_result = search_engine.unified_intelligent_search(
                query=query,
                session_memory=None,
                user_pantry=[],
                exclude_ids=exclude_ids or [],
                limit=2000,  # High limit for intelligent session-aware search
                include_explanations=True
            )

            if search_result['success']:
                recipes = search_result['recipes']

                # Transform to expected format for API compatibility
                enhanced_recipes = []
                for recipe in recipes:
                    enhanced_recipe = {
                        'id': recipe['id'],
                        'title': recipe['title'],
                        'name': recipe['title'],
                        'description': recipe['description'] or '',
                        'servings': recipe['servings'] or '4 servings',
                        'prep_time': recipe.get('prep_time', ''),
                        'cook_time': recipe.get('cook_time', '30 minutes'),
                        'total_time': recipe['total_time'] or '30 minutes',
                        'ingredients': recipe['ingredients'] or '',
                        'instructions': recipe['instructions'] or '',
                        'source': recipe['source'] or 'Recipe Collection',
                        'category': recipe['category'] or 'Main Course',
                        'recipe_types': recipe.get('recipe_types', []),
                        # NEW: Intelligence metadata from universal search
                        'explanations': recipe.get('explanations', ''),
                        'meal_role': recipe.get('meal_role'),
                        'is_easy': recipe.get('is_easy', False),
                        'is_one_pot': recipe.get('is_one_pot', False),
                        'kid_friendly': recipe.get('kid_friendly', False),
                        'time_min': recipe.get('time_min'),
                        'universal_search': True,
                        'exclusions_applied': True
                    }
                    enhanced_recipes.append(enhanced_recipe)

                logger.info(f"🔍 Universal search with exclusions found {len(enhanced_recipes)} recipes")
                return enhanced_recipes
            else:
                logger.warning(f"Universal search with exclusions failed: {search_result.get('error', 'Unknown error')}")

        # This should never happen in production
        logger.error("⚠️ Universal search engine not available for exclusion search")
        return []

    except Exception as e:
        logger.error(f"Universal search with exclusions error: {e}")
        return []

def basic_search_with_exclusions(query, exclude_ids=None):
    """
    Basic search with exclusions - UNIVERSAL SEARCH INTEGRATION
    
    ✨ CONSOLIDATION: Now uses UniversalSearchEngine for consistency
    🎯 FEATURES: Intelligence filtering, smart explanations, exclusion logic
    📈 PERFORMANCE: Optimized queries with universal search engine
    """
    try:
        logger.info(f"🔄 Basic search with exclusions redirecting to universal search for: '{query}'")

        # Use universal search instead of basic search - CONSOLIDATION
        return search_recipes_with_exclusions(query, exclude_ids)

    except Exception as e:
        logger.error(f"🔄 Basic search consolidation error: {str(e)}")
        return []

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all categories"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT c.id, c.name, COUNT(rc.recipe_id) as recipe_count
            FROM categories c
            LEFT JOIN recipe_categories rc ON c.id = rc.category_id
            GROUP BY c.id, c.name
            ORDER BY c.name
        """)

        categories = []
        for row in cursor.fetchall():
            categories.append({
                'id': row['id'],
                'name': row['name'],
                'recipe_count': row['recipe_count']
            })

        conn.close()
        return jsonify({
            'success': True,
            'data': categories
        })

    except Exception as e:
        logger.error(f"Categories API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/smart-search', methods=['POST'])
@app.route('/api/recipe-suggestions', methods=['POST'])
def smart_search():
    """
    UNIVERSAL SMART SEARCH - Day 4 Full Integration
    The single search function that replaces ALL scattered search implementations
    Intelligent recipe search with complete filter support and consolidated logic
    """
    try:
        data = request.get_json()
        logger.info(f"🔍 Smart search request received: {data}")
        
        user_message = data.get('message', '').strip()
        query = data.get('query', user_message).strip()  # Support both message and query
        session_id = data.get('session_id', 'default')

        # Day 4: Extract intelligence filters from request
        filters = {
            'meal_role': data.get('meal_role'),
            'max_time': data.get('max_time'),
            'is_easy': data.get('is_easy', False),
            'is_one_pot': data.get('is_one_pot', False),
            'kid_friendly': data.get('kid_friendly', False),
            'leftover_friendly': data.get('leftover_friendly', False),
            'pantry_first': data.get('pantry_first', False)
        }

        # Get user pantry if available (future enhancement)
        user_pantry = data.get('user_pantry', [])
        exclude_ids = data.get('exclude_ids', [])
        limit = data.get('limit', 10)
        
        # Debug logging for pantry integration
        if user_pantry:
            logger.info(f"🥫 Pantry data received: {[item.get('name') for item in user_pantry]} (pantry_first: {filters['pantry_first']})")
        else:
            logger.info("📝 No pantry data provided in request")

        if not query:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400

        # Use universal search engine (consolidated from ALL scattered functions)
        if not search_engine:
            return jsonify({
                'success': False,
                'error': 'Universal search engine not available'
            }), 503

        # Get session memory if available
        session_memory = None
        if session_manager:
            try:
                session_memory = session_manager.get_session_data(session_id)
            except:
                session_memory = None

        # UNIVERSAL SEARCH CALL - replaces ALL 14+ scattered search functions with filter support
        search_result = search_engine.unified_intelligent_search(
            query=query,
            session_memory=session_memory,
            user_pantry=user_pantry,
            exclude_ids=exclude_ids,
            limit=limit,
            include_explanations=True,
            filters=filters  # Day 4: Pass filters to search engine
        )

        if not search_result['success']:
            return jsonify({
                'success': False,
                'error': search_result.get('error', 'Search failed')
            }), 500

        recipes = search_result['recipes']
        filters_applied = search_result['filters_applied']
        search_metadata = search_result['search_metadata']

        # Record query in session if available
        if session_manager:
            try:
                session_manager.record_query(
                    session_id=session_id,
                    user_query=query,
                    intent="recipe_search",
                    context=f"filters: {filters_applied}",
                    result_count=len(recipes),
                    displayed_count=len(recipes),
                    search_phase="universal_search"
                )
            except:
                pass  # Session manager not available

        # Generate intelligent response based on results
        if recipes:
            # Smart response based on filters applied
            response_parts = [f"Found {len(recipes)} recipes"]

            if filters_applied.get('max_time'):
                response_parts.append(f"ready in ≤{filters_applied['max_time']} minutes")
            if filters_applied.get('is_easy'):
                response_parts.append("that are easy to make")
            if filters_applied.get('is_one_pot'):
                response_parts.append("using just one pot")
            if filters_applied.get('kid_friendly'):
                response_parts.append("that are kid-friendly")
            if filters_applied.get('meal_role'):
                response_parts.append(f"perfect for {filters_applied['meal_role']}")

            ai_response = " ".join(response_parts) + "! 🍴"

            # Generate conversation suggestions if available
            # Conversation suggestions disabled
            conversation_suggestions = []

            # Enhanced response with intelligence metadata
            response_data = {
                'success': True,
                'data': {
                    'response': ai_response,
                    'context': query,
                    'recipes': recipes,
                    'filters_applied': filters_applied,
                    'search_metadata': search_metadata,
                    'session_id': session_id,
                    'total_results': len(recipes),
                    'intelligence_enabled': True,  # Day 4 feature flag
                    'universal_search': True  # Full integration flag
                }
            }

            # Add conversation suggestions if available
            if conversation_suggestions:
                response_data['data']['conversation_suggestions'] = conversation_suggestions

            return jsonify(response_data)

        else:
            # No results found - provide helpful suggestions
            ai_response = "I couldn't find recipes matching those criteria. Try adjusting your filters or being more specific about ingredients or cooking style. 🔍"

            return jsonify({
                'success': True,
                'data': {
                    'response': ai_response,
                    'context': query,
                    'recipes': [],
                    'filters_applied': filters_applied,
                    'search_metadata': search_metadata,
                    'session_id': session_id,
                    'total_results': 0,
                    'intelligence_enabled': True,
                    'universal_search': True,
                    'suggestions': [
                        "Try removing some filters",
                        "Search for ingredients you have",
                        "Look for a different meal type",
                        "Ask for general recipe ideas"
                    ]
                }
            })

    except Exception as e:
        logger.error(f"Universal search error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'universal_search': True
        }), 500

# ===================================
# DATABASE STATISTICS ENDPOINTS
# ===================================

@app.route('/api/database-stats', methods=['GET'])
def get_database_stats():
    """Get database statistics for debugging - UNIVERSAL SEARCH INTEGRATION"""
    try:
        from core_systems.universal_search import get_database_info

        stats = get_database_info()

        return jsonify({
            'success': True,
            'data': stats
        })

    except Exception as e:
        logger.error(f"Database stats API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/recipe-types', methods=['GET'])
def get_recipe_types():
    """Get all available recipe types and their statistics - UNIVERSAL SEARCH INTEGRATION"""
    try:
        from core_systems.universal_search import UniversalSearchEngine

        engine = UniversalSearchEngine()

        # Get all recipe type categories
        recipe_type_info = {
            'one_pot': {
                'name': 'One-Pot Meals',
                'description': 'Complete meals made in a single pot or pan',
                'keywords': engine.recipe_type_keywords['one_pot'],
                'count': 0
            },
            'quick': {
                'name': 'Quick & Fast',
                'description': 'Recipes ready in 30 minutes or less',
                'keywords': engine.recipe_type_keywords['quick'],
                'count': 0
            },
            'easy': {
                'name': 'Easy & Simple',
                'description': 'Beginner-friendly recipes with simple techniques',
                'keywords': engine.recipe_type_keywords['easy'],
                'count': 0
            },
            'challenging': {
                'name': 'Challenging',
                'description': 'Advanced recipes requiring technique and skill',
                'keywords': engine.recipe_type_keywords['challenging'],
                'count': 0
            },
            'low_prep': {
                'name': 'Low Prep',
                'description': 'Minimal preparation required',
                'keywords': engine.recipe_type_keywords['low_prep'],
                'count': 0
            },
            'slow_cook': {
                'name': 'Slow Cooked',
                'description': 'Long cooking times for deep flavors',
                'keywords': engine.recipe_type_keywords['slow_cook'],
                'count': 0
            }
        }

        # Get sample counts by doing quick searches
        for recipe_type, info in recipe_type_info.items():
            try:
                # Use first keyword to get a count estimate
                sample_query = info['keywords'][0] if info['keywords'] else recipe_type
                results = search_recipes_by_query(sample_query, limit=10)

                # Count recipes that actually have this type
                actual_count = sum(1 for recipe in results if recipe_type in recipe.get('recipe_types', []))
                info['count'] = actual_count

            except Exception as e:
                logger.warning(f"Failed to get count for {recipe_type}: {e}")
                info['count'] = 0

        return jsonify({
            'success': True,
            'data': {
                'recipe_types': recipe_type_info,
                'total_types': len(recipe_type_info),
                'classification_available': True
            }
        })

    except Exception as e:
        logger.error(f"Recipe types API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'data': {
                'classification_available': False
            }
        }), 500

@app.route('/api/search/by-type/<recipe_type>', methods=['GET'])
def search_by_recipe_type(recipe_type):
    """
    Search recipes by specific recipe type - UNIVERSAL SEARCH INTEGRATION
    
    ✨ CONSOLIDATION: Now uses UniversalSearchEngine for type-based search
    🎯 FEATURES: Intelligence filtering, smart explanations, type classification
    📈 PERFORMANCE: Optimized queries with universal search engine
    """
    try:
        logger.info(f"🏷️ Universal search by recipe type: '{recipe_type}'")

        # Validate recipe type - expanded to match intelligence filters
        valid_types = ['one_pot', 'quick', 'easy', 'challenging', 'low_prep', 'slow_cook',
                      'kid_friendly', 'leftover_friendly', 'breakfast', 'lunch', 'dinner', 'snack']
        if recipe_type not in valid_types:
            return jsonify({
                'success': False,
                'error': f'Invalid recipe type. Valid types: {valid_types}'
            }), 400

        # Use universal search with intelligence filtering
        if search_engine:
            # Map recipe type to intelligence filters
            intelligence_filters = {}
            if recipe_type == 'one_pot':
                intelligence_filters['is_one_pot'] = True
            elif recipe_type == 'easy' or recipe_type == 'quick':
                intelligence_filters['is_easy'] = True
            elif recipe_type == 'kid_friendly':
                intelligence_filters['kid_friendly'] = True
            elif recipe_type == 'leftover_friendly':
                intelligence_filters['leftover_friendly'] = True
            elif recipe_type in ['breakfast', 'lunch', 'dinner', 'snack']:
                intelligence_filters['meal_role'] = recipe_type

            # Use type keyword as query
            search_query = recipe_type.replace('_', ' ')

            search_result = search_engine.unified_intelligent_search(
                query=search_query,
                session_memory=None,
                user_pantry=[],
                exclude_ids=[],
                limit=50,
                include_explanations=True,
                intelligence_filters=intelligence_filters
            )

            if search_result['success']:
                recipes = search_result['recipes']

                logger.info(f"🏷️ Universal search found {len(recipes)} recipes of type '{recipe_type}'")

                return jsonify({
                    'success': True,
                    'data': recipes,
                    'metadata': {
                        'recipe_type': recipe_type,
                        'total_found': len(recipes),
                        'universal_search_used': True,
                        'intelligence_enabled': True,
                        'intelligence_filters': intelligence_filters,
                        'search_explanations': search_result.get('search_metadata', {})
                    }
                })
            else:
                logger.warning(f"Universal search by type failed: {search_result.get('error', 'Unknown error')}")
                return jsonify({
                    'success': False,
                    'error': search_result.get('error', 'Universal search failed'),
                    'universal_search': False
                }), 500
        else:
            logger.error("⚠️ Universal search engine not available for type search")
            return jsonify({
                'success': False,
                'error': 'Universal search engine not configured'
            }), 500

    except Exception as e:
        logger.error(f"Universal search by type API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'universal_search': False
        }), 500

    except Exception as e:
        logger.error(f"Search by type API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/recipes/<recipe_id>/analyze', methods=['GET'])
def analyze_recipe(recipe_id):
    """Analyze a recipe with AI"""
    try:
        recipe = get_recipe_by_id(recipe_id)
        if not recipe:
            return jsonify({
                'success': False,
                'error': 'Recipe not found'
            }), 404

        if not client:
            return jsonify({
                'success': False,
                'error': 'AI service not available'
            }), 503

        # Create analysis prompt
        prompt = f"""
        Analyze this recipe and provide helpful cooking insights:
        
        Title: {recipe['title']}
        Ingredients: {recipe['ingredients']}
        Instructions: {recipe['instructions']}
        
        Please provide:
        1. Cooking difficulty level
        2. Key techniques used
        3. Flavor profile
        4. Helpful tips
        5. Possible substitutions
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": CHEF_PERSONALITY},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.7
        )

        analysis = response.choices[0].message.content

        return jsonify({
            'success': True,
            'data': {
                'recipe': recipe,
                'analysis': analysis
            }
        })

    except Exception as e:
        logger.error(f"Recipe analysis error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/session/<session_id>/stats', methods=['GET'])
def get_session_stats(session_id):
    """Get session statistics and information"""
    try:
        if not session_manager:
            return jsonify({
                'success': False,
                'error': 'Session management not available'
            }), 503

        stats = session_manager.get_session_stats(session_id)

        if not stats:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404

        return jsonify({
            'success': True,
            'data': stats
        })

    except Exception as e:
        logger.error(f"Session stats API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/session/<session_id>/shown-recipes', methods=['GET'])
def get_session_shown_recipes(session_id):
    """Get recipes already shown to this session"""
    try:
        if not session_manager:
            return jsonify({
                'success': False,
                'error': 'Session management not available'
            }), 503

        shown_recipes = session_manager.get_shown_recipes(session_id)

        return jsonify({
            'success': True,
            'data': {
                'session_id': session_id,
                'shown_recipe_ids': shown_recipes,
                'count': len(shown_recipes)
            }
        })

    except Exception as e:
        logger.error(f"Session shown recipes API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/conversation-suggestions', methods=['POST'])
def get_conversation_suggestions():
    """
    Generate dynamic conversation suggestions - UNIVERSAL SEARCH INTEGRATION
    
    ✨ CONSOLIDATION: Now uses UniversalSearchEngine for contextual suggestions
    🎯 FEATURES: Intelligence filtering, smart explanations, context awareness
    📈 PERFORMANCE: Optimized queries with universal search engine
    """
    try:
        data = request.get_json()
        user_query = data.get('query', '')
        search_results = data.get('search_results', [])
        session_id = data.get('session_id', 'default')

        if not user_query:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400

        logger.info(f"💬 Universal conversation suggestions for: '{user_query}' | Session: {session_id}")

        # Use universal search for contextual suggestions
        if search_engine:
            # Generate contextual follow-up queries based on user query
            follow_up_queries = [
                f"easy {user_query}",
                f"quick {user_query}",
                f"one pot {user_query}",
                f"kid friendly {user_query}",
                f"{user_query} with leftovers"
            ]

            suggestions = []
            for query in follow_up_queries:
                search_result = search_engine.unified_intelligent_search(
                    query=query,
                    session_memory={'session_id': session_id},
                    user_pantry=[],
                    exclude_ids=[],
                    limit=3,
                    include_explanations=True
                )

                if search_result['success'] and search_result['recipes']:
                    suggestions.append({
                        'text': query.title(),
                        'type': 'search_suggestion',
                        'results_count': len(search_result['recipes']),
                        'preview_recipes': [r['title'] for r in search_result['recipes'][:2]],
                        'intelligence_enabled': True
                    })

            return jsonify({
                'success': True,
                'data': {
                    'suggestions': suggestions,
                    'query': user_query,
                    'session_id': session_id,
                    'timestamp': datetime.now().isoformat(),
                    'universal_search_used': True,
                    'intelligence_enabled': True
                }
            })
        else:
            # Fallback to basic suggestions if universal search not available
            basic_suggestions = [
                {'text': f"Easy {user_query}", 'type': 'search_suggestion'},
                {'text': f"Quick {user_query}", 'type': 'search_suggestion'},
                {'text': f"One pot {user_query}", 'type': 'search_suggestion'}
            ]

            return jsonify({
                'success': True,
                'data': {
                    'suggestions': basic_suggestions,
                    'query': user_query,
                    'session_id': session_id,
                    'timestamp': datetime.now().isoformat(),
                    'universal_search_used': False
                }
            })

    except Exception as e:
        logger.error(f"Universal conversation suggestions API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'universal_search': False
        }), 500

# ===================================
# MEAL PLANNING API ENDPOINTS
# ===================================

@app.route('/api/meal-plans', methods=['POST'])
def create_meal_plan():
    """Create a new meal plan"""
    if not MEAL_PLANNING_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Meal planning system not available'
        }), 503

    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        plan_name = data.get('plan_name', f'Meal Plan {datetime.now().strftime("%Y-%m-%d")}')
        week_start_date = data.get('week_start_date', datetime.now().strftime("%Y-%m-%d"))
        meal_data = data.get('meal_data', {})

        try:
            meal_planner = MealPlanningSystem()
            plan_id = meal_planner.create_meal_plan(plan_name, week_start_date, meal_data)
            
            return jsonify({
                'success': True,
                'plan_id': plan_id,
                'plan_name': plan_name,
                'week_start_date': week_start_date
            })
        finally:
            # Ensure connection cleanup
            if hasattr(meal_planner, 'db_connection') and meal_planner.db_connection:
                meal_planner.db_connection.close()

    except Exception as e:
        logger.error(f"Create meal plan error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/meal-plans', methods=['GET'])
def list_meal_plans():
    """List all meal plans"""
    if not MEAL_PLANNING_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Meal planning system not available'
        }), 503

    try:
        limit = request.args.get('limit', 50, type=int)

        # Temporary fix: Return empty meal plans instead of erroring
        # TODO: Fix meal planning system database connection issue
        return jsonify({
            'success': True,
            'meal_plans': [],
            'count': 0,
            'note': 'Meal planning temporarily disabled due to database connection issue'
        })

        # meal_planner = MealPlanningSystem()
        # plans = meal_planner.list_meal_plans(limit=limit)
        # 
        # return jsonify({
        #     'success': True,
        #     'meal_plans': plans,
        #     'count': len(plans)
        # })

    except Exception as e:
        logger.error(f"List meal plans error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/meal-plans/<int:plan_id>', methods=['GET'])
def get_meal_plan(plan_id):
    """Get a specific meal plan"""
    if not MEAL_PLANNING_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Meal planning system not available'
        }), 503

    try:
        meal_planner = MealPlanningSystem()
        plan = meal_planner.get_meal_plan(plan_id)

        if not plan:
            return jsonify({
                'success': False,
                'error': 'Meal plan not found'
            }), 404

        return jsonify({
            'success': True,
            'meal_plan': plan
        })

    except Exception as e:
        logger.error(f"Get meal plan error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/meal-plans/<int:plan_id>', methods=['PUT'])
def update_meal_plan(plan_id):
    """Update a meal plan"""
    if not MEAL_PLANNING_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Meal planning system not available'
        }), 503

    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        meal_data = data.get('meal_data', {})

        meal_planner = MealPlanningSystem()
        success = meal_planner.update_meal_plan(plan_id, meal_data)

        if not success:
            return jsonify({
                'success': False,
                'error': 'Meal plan not found'
            }), 404

        return jsonify({
            'success': True,
            'plan_id': plan_id
        })

    except Exception as e:
        logger.error(f"Update meal plan error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/meal-plans/<int:plan_id>/grocery-list', methods=['GET'])
def get_grocery_list(plan_id):
    """Generate grocery list from meal plan"""
    if not MEAL_PLANNING_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Meal planning system not available'
        }), 503

    try:
        grocery_generator = GroceryListGenerator()
        grocery_list = grocery_generator.generate_grocery_list_from_meal_plan(plan_id)

        return jsonify(grocery_list)

    except Exception as e:
        logger.error(f"Generate grocery list error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/grocery-list', methods=['POST'])
def generate_grocery_list_from_recipes():
    """Generate grocery list from recipe IDs"""
    if not MEAL_PLANNING_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Meal planning system not available'
        }), 503

    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        recipe_ids = data.get('recipe_ids', [])
        if not recipe_ids:
            return jsonify({
                'success': False,
                'error': 'No recipe IDs provided'
            }), 400

        grocery_generator = GroceryListGenerator()
        grocery_list = grocery_generator.generate_grocery_list_from_recipes(recipe_ids)

        return jsonify(grocery_list)

    except Exception as e:
        logger.error(f"Generate grocery list from recipes error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ===================================
# FAVORITES API ENDPOINTS
# ===================================

@app.route('/api/favorites', methods=['POST'])
def toggle_favorite():
    """Add or remove a recipe from favorites - DISABLED"""
    return jsonify({
        'success': False,
        'error': 'Favorites system temporarily disabled'
    }), 503

@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    """Get user's favorite recipes - DISABLED"""
    return jsonify({
        'success': False,
        'error': 'Favorites system temporarily disabled'
    }), 503

@app.route('/api/favorites/check', methods=['POST'])
def check_favorites():
    """Check favorite status for multiple recipes - DISABLED"""
    return jsonify({
        'success': False,
        'error': 'Favorites system temporarily disabled'
    }), 503

@app.route('/api/favorites/summary', methods=['GET'])
def get_favorites_summary():
    """Get favorites summary information - DISABLED"""
    return jsonify({
        'success': False,
        'error': 'Favorites system temporarily disabled'
    }), 503

@app.route('/api/admin/migrate-intelligence', methods=['POST'])
def migrate_intelligence_endpoint():
    """Admin endpoint to add intelligence fields and backfill existing recipes"""
    try:
        result = run_intelligence_migration()
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
    except Exception as e:
        logger.error(f"Migration endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/admin/check-database', methods=['GET'])
def check_database_info_endpoint():
    """Diagnostic endpoint to check database connection and content"""
    try:
        result = check_database_info()
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'database_url_set': 'DATABASE_URL' in os.environ
        }), 500

@app.route('/api/admin/run-schema-migration', methods=['POST'])
def run_schema_migration_endpoint_route():
    """Admin endpoint to run database schema migrations"""
    try:
        # Check authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header or auth_header != 'Bearer admin-token-2024':
            return jsonify({
                'success': False,
                'error': 'Unauthorized - Admin token required'
            }), 401

        action = request.json.get('action') if request.json else None
        result = run_schema_migration_endpoint(action)

        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400 if 'Invalid action' in result['error'] else 500

    except Exception as e:
        logger.error(f"? Schema migration endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/admin/migrate-recipes', methods=['POST'])
def migrate_recipes_endpoint():
    """Admin endpoint to add sample recipes to PostgreSQL database AND run intelligence migration"""
    try:
        # Check if this is an intelligence migration request
        migrate_type = request.json.get('type', 'recipes') if request.json else 'recipes'

        if migrate_type == 'intelligence':
            result = run_intelligence_migration()
            if result['success']:
                return jsonify(result)
            else:
                return jsonify(result), 500

        # Check authorization for recipe migration
        admin_key = request.headers.get('X-Admin-Key')
        if admin_key != 'migrate-recipes-2025':
            return jsonify({
                'success': False,
                'error': 'Unauthorized - Admin key required'
            }), 401

        result = add_sample_recipes()
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500

    except Exception as e:
        logger.error(f"? Migration error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/db-test', methods=['GET'])
def database_connection_test():
    """Simple database connection test"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM recipes')
        result = cursor.fetchone()
        recipe_count = result[0] if result else 0
        conn.close()

        return jsonify({
            'success': True,
            'recipe_count': recipe_count,
            'message': f'Found {recipe_count} recipes'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Database connection failed'
        }), 500

@app.route('/api/version', methods=['GET'])
def get_version():
    """Get deployment version and universal search status"""
    return jsonify({
        'version': '2025-08-17-universal-search-v2',
        'deployment_time': datetime.now().isoformat(),
        'universal_search_engine_available': search_engine is not None,
        'universal_search_class': str(type(search_engine)) if search_engine else None,
        'git_commit': 'df3de02-universal-consolidation',
        'features': {
            'universal_search': True,
            'intelligence_filtering': True,
            'session_awareness': True,
            'consolidated_architecture': True
        }
    })

@app.route('/api/config', methods=['GET'])
def get_configuration():
    """Get current system configuration"""
    try:
        from core_systems.config import get_config
        config = get_config()
        
        return jsonify({
            'success': True,
            'config': config.get_status(),
            'message': 'Configuration retrieved successfully'
        })
        
    except Exception as e:
        logger.error(f"❌ Configuration retrieval error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to retrieve configuration'
        }), 500

@app.route('/api/config/pantry/toggle', methods=['POST'])
def toggle_pantry_system():
    """Toggle the pantry system on/off"""
    try:
        from core_systems.config import toggle_pantry, get_config
        
        new_state = toggle_pantry()
        config = get_config()
        
        return jsonify({
            'success': True,
            'pantry_enabled': new_state,
            'config': config.get_status(),
            'message': f'Pantry system {"enabled" if new_state else "disabled"}'
        })
        
    except Exception as e:
        logger.error(f"❌ Pantry toggle error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to toggle pantry system'
        }), 500

@app.route('/api/config/pantry/enable', methods=['POST'])
def enable_pantry_system():
    """Enable the pantry system"""
    try:
        from core_systems.config import enable_pantry, get_config
        
        enable_pantry()
        config = get_config()
        
        return jsonify({
            'success': True,
            'pantry_enabled': True,
            'config': config.get_status(),
            'message': 'Pantry system enabled'
        })
        
    except Exception as e:
        logger.error(f"❌ Pantry enable error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to enable pantry system'
        }), 500

@app.route('/api/config/pantry/disable', methods=['POST'])
def disable_pantry_system():
    """Disable the pantry system"""
    try:
        from core_systems.config import disable_pantry, get_config
        
        disable_pantry()
        config = get_config()
        
        return jsonify({
            'success': True,
            'pantry_enabled': False,
            'config': config.get_status(),
            'message': 'Pantry system disabled'
        })
        
    except Exception as e:
        logger.error(f"❌ Pantry disable error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to disable pantry system'
        }), 500

# ===================================
# PANTRY MANAGEMENT ENDPOINTS
# ===================================

@app.route('/api/pantry', methods=['GET'])
def get_pantry_items():
    """Get all pantry items"""
    try:
        from core_systems.pantry_system import PantrySystem
        pantry = PantrySystem()
        items = pantry.get_all_pantry_items()
        
        return jsonify({
            'success': True,
            'items': items,
            'count': len(items)
        })
        
    except Exception as e:
        logger.error(f"❌ Get pantry items error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/pantry', methods=['POST'])
def add_pantry_item():
    """Add item to pantry"""
    try:
        from core_systems.pantry_system import PantrySystem
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        ingredient_name = data.get('ingredient_name', '').strip()
        amount = data.get('amount', 1)
        
        if not ingredient_name:
            return jsonify({
                'success': False,
                'error': 'Ingredient name required'
            }), 400
        
        pantry = PantrySystem()
        result = pantry.add_pantry_item(ingredient_name, amount)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Add pantry item error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/pantry/<int:item_id>', methods=['PUT'])
def update_pantry_item(item_id):
    """Update pantry item"""
    try:
        from core_systems.pantry_system import PantrySystem
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        amount = data.get('amount')
        if amount is None:
            return jsonify({
                'success': False,
                'error': 'Amount required'
            }), 400
        
        pantry = PantrySystem()
        result = pantry.update_pantry_item(item_id, amount)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Update pantry item error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/pantry/<int:item_id>', methods=['DELETE'])
def remove_pantry_item(item_id):
    """Remove item from pantry"""
    try:
        from core_systems.pantry_system import PantrySystem
        
        pantry = PantrySystem()
        result = pantry.remove_pantry_item(item_id)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Remove pantry item error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ingredients', methods=['GET'])
def get_ingredients():
    """Get available canonical ingredients for pantry"""
    try:
        logger.info("🔍 Fetching canonical ingredients from PostgreSQL...")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get query parameter for search filtering
        query = request.args.get('query', '').strip()
        logger.info(f"📝 Search query parameter: '{query}'")
        
        # Get clean ingredients (exclude entries with measurements, brackets, or complex formatting)
        sql_query = """
            SELECT DISTINCT 
                canonical_name, 
                category,
                CASE category 
                    WHEN 'protein' THEN 1
                    WHEN 'produce' THEN 2
                    WHEN 'dairy' THEN 3
                    WHEN 'grain' THEN 4
                    WHEN 'spice' THEN 5
                    WHEN 'herb' THEN 6
                    WHEN 'cooking' THEN 7
                    WHEN 'baking' THEN 8
                    ELSE 9
                END as category_order
            FROM canonical_ingredients 
            WHERE canonical_name NOT LIKE '%cup%'
            AND canonical_name NOT LIKE '%teaspoon%'
            AND canonical_name NOT LIKE '%tablespoon%'
            AND canonical_name NOT LIKE '%[%'
            AND canonical_name NOT LIKE '"%'
            AND canonical_name NOT LIKE '%{%'
            AND canonical_name NOT LIKE '½%'
            AND canonical_name NOT LIKE '¼%'
            AND canonical_name NOT LIKE '1%'
            AND canonical_name NOT LIKE '2%'
            AND canonical_name NOT LIKE '3%'
            AND canonical_name NOT LIKE '4%'
            AND canonical_name NOT LIKE '5%'
            AND LENGTH(canonical_name) < 50
        """
        
        # Add search filter if query provided
        if query:
            sql_query += " AND canonical_name ILIKE %s"
            cursor.execute(sql_query + " ORDER BY category_order, canonical_name LIMIT 200", (f'%{query}%',))
            logger.info(f"🔍 Applied search filter for: '{query}'")
        else:
            cursor.execute(sql_query + " ORDER BY category_order, canonical_name LIMIT 200")
            logger.info("📋 Fetching all ingredients (no search filter)")
        
        ingredients = []
        for row in cursor.fetchall():
            ingredients.append({
                'name': row['canonical_name'],
                'category': row['category'] or 'other'
            })
        
        logger.info(f"✅ Retrieved {len(ingredients)} ingredients from canonical_ingredients table")
        if ingredients:
            logger.info(f"📊 Sample ingredients: {[ing['name'] for ing in ingredients[:5]]}")
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'ingredients': ingredients,
            'count': len(ingredients),
            'query': query
        })
        
    except Exception as e:
        logger.error(f"❌ Get ingredients error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'ingredients': []
        }), 500

@app.route('/api/pantry/status', methods=['GET'])
def get_pantry_status():
    """Get current pantry system status - frontend compatibility"""
    try:
        from core_systems.config import get_config
        
        config = get_config()
        status = config.get_status()
        
        # Extract pantry status information
        pantry_enabled = status.get('pantry_enabled', True)
        status_text = "🟢 PANTRY: ENABLED" if pantry_enabled else "🔴 PANTRY: DISABLED"
        
        return jsonify({
            'success': True,
            'status': status_text,
            'enabled': pantry_enabled
        })
        
    except Exception as e:
        logger.error(f"❌ Get pantry status error: {e}")
        return jsonify({
            'success': False,
            'status': '🔴 PANTRY: ERROR',
            'error': str(e)
        }), 500

@app.route('/api/pantry/toggle', methods=['GET'])
def get_pantry_toggle_status():
    """Get current pantry system status"""
    try:
        from core_systems.config import get_config
        
        config = get_config()
        status = config.get_status()
        
        return jsonify({
            'success': True,
            'pantry_enabled': status['pantry']['enabled'],
            'status': status['pantry']['status']
        })
        
    except Exception as e:
        logger.error(f"❌ Get pantry toggle status error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ===================================
# RECIPE IMPORT ENDPOINTS - DAY 1 IMPLEMENTATION
# ===================================

@app.route('/api/recipes/import/text', methods=['POST'])
def import_recipe_from_text():
    """Import recipe from pasted text"""
    if not RECIPE_IMPORT_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Recipe import system not available'
        }), 503
    
    # Check authentication
    user_id, error_response, status_code = check_authentication()
    if error_response:
        return error_response, status_code
    
    try:
        data = request.get_json()
        
        # Validate request
        if not data or 'recipe_text' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing recipe_text in request body'
            }), 400
        
        recipe_text = data['recipe_text']
        
        # Create import request
        import_request = ImportRequest(
            source_type='text',
            source_data=recipe_text,
            user_id=user_id,
            metadata=data.get('metadata', {})
        )
        
        # Initialize importer and process
        importer = UniversalRecipeImporter()
        result = importer.import_recipe(import_request)
        
        # Return result
        return jsonify({
            'success': result.success,
            'recipe_id': result.recipe_id,
            'recipe_data': result.recipe_data,
            'confidence': result.confidence,
            'needs_review': result.needs_review,
            'extraction_method': result.extraction_method,
            'processing_time': result.processing_time,
            'errors': result.errors,
            'warnings': result.warnings
        })
        
    except Exception as e:
        logger.error(f"Text import failed: {e}")
        return jsonify({
            'success': False,
            'error': f'Import failed: {str(e)}'
        }), 500

@app.route('/api/recipes/import/url', methods=['POST'])
def import_recipe_from_url():
    """Import recipe from website URL (Day 2 implementation)"""
    print("🚨 IMPORT REQUEST RECEIVED!")  # This will definitely show up
    logger.info("🚨 IMPORT REQUEST RECEIVED!")
    
    if not RECIPE_IMPORT_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Recipe import system not available'
        }), 503
    
    # Check authentication
    user_id, error_response, status_code = check_authentication()
    if error_response:
        return error_response, status_code
    
    try:
        data = request.get_json()
        
        # Validate request
        if not data or 'url' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing url in request body'
            }), 400
        
        url = data['url']
        
        # Create import request
        import_request = ImportRequest(
            source_type='url',
            source_data=url,
            user_id=user_id,
            metadata=data.get('metadata', {})
        )
        
        # Initialize importer and process
        importer = UniversalRecipeImporter()
        result = importer.import_recipe(import_request)
        
        # CRITICAL: Refresh search engine cache after successful import
        if result.success and result.recipe_id:
            logger.info(f"🔄 Refreshing search cache for new recipe ID: {result.recipe_id}")
            if search_engine:
                search_engine.refresh_database_cache()
            logger.info(f"✅ Search cache refreshed - new recipe should be visible")
        
        # Return result
        return jsonify({
            'success': result.success,
            'recipe_id': result.recipe_id,
            'recipe_data': result.recipe_data,
            'confidence': result.confidence,
            'needs_review': result.needs_review,
            'extraction_method': result.extraction_method,
            'processing_time': result.processing_time,
            'errors': result.errors,
            'warnings': result.warnings
        })
        
    except Exception as e:
        logger.error(f"URL import failed: {e}")
        return jsonify({
            'success': False,
            'error': f'Import failed: {str(e)}'
        }), 500

@app.route('/api/recipes/import/check-duplicates', methods=['POST'])
def check_recipe_duplicates():
    """Check for duplicate recipes before importing"""
    if not RECIPE_IMPORT_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Recipe import system not available'
        }), 503
    
    # Check authentication
    user_id, error_response, status_code = check_authentication()
    if error_response:
        return error_response, status_code
    
    try:
        data = request.get_json()
        
        if not data or 'recipe_data' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing recipe_data in request body'
            }), 400
        
        recipe_data = data['recipe_data']
        
        # Initialize importer and check for duplicates
        importer = UniversalRecipeImporter()
        duplicates = importer.check_for_duplicates(recipe_data, user_id)
        
        return jsonify({
            'success': True,
            'has_duplicates': len(duplicates) > 0,
            'duplicates': duplicates,
            'count': len(duplicates)
        })
        
    except Exception as e:
        logger.error(f"Duplicate check failed: {e}")
        return jsonify({
            'success': False,
            'error': f'Duplicate check failed: {str(e)}'
        }), 500

# ===================================
# HEALTH CHECK ENDPOINT
# ===================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint with backend capabilities"""
    try:
        capabilities = {
            'universal_search': UNIVERSAL_SEARCH_AVAILABLE,
            'flavor_profile': False,
            'meal_planning': MEAL_PLANNING_AVAILABLE,
            'recipe_import': RECIPE_IMPORT_AVAILABLE,
            'session_management': session_manager is not None,
            'ai_chat': client is not None,
            'database_connection': True
        }

        # Test database connection
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM recipes')
            recipe_count = cursor.fetchone()[0]
            conn.close()
            capabilities['recipe_count'] = recipe_count
        except Exception as e:
            capabilities['database_connection'] = False
            capabilities['database_error'] = str(e)

        return jsonify({
            'success': True,
            'status': 'healthy',
            'capabilities': capabilities,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }), 500
if __name__ == "__main__":
    logger.info("?? Starting Yes Chef! Backend Server...")

    # Initialize database
    try:
        init_db()
        logger.info("? Database initialization completed")
    except Exception as e:
        logger.error(f"? Database initialization failed: {e}")

    # Initialize Authentication System with database connection
    try:
        auth_system = AuthenticationSystem(app, get_db_connection)
        auth_routes = create_auth_routes(auth_system)
        app.register_blueprint(auth_routes)
        logger.info("✅ Authentication system initialized and routes registered")
    except Exception as e:
        logger.error(f"❌ Failed to initialize authentication system: {e}")
        auth_system = None

    # Initialize Template Recipe System
    template_system = None
    if TEMPLATE_SYSTEM_AVAILABLE:
        try:
            template_system = TemplateRecipeSystem(get_db_connection)
            # Initialize schema (safe to run multiple times)
            if template_system.initialize_schema():
                logger.info("✅ Template recipe system schema initialized")
                # Create default recipes if they don't exist
                if template_system.create_default_templates():
                    logger.info("✅ Default template recipes ready")
            logger.info("🎯 Template recipe system initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize template system: {e}")
            template_system = None
    else:
        logger.warning("⚠️ Template recipe system not available")

    # Initialize Admin System
    admin_system = None
    if ADMIN_SYSTEM_AVAILABLE and auth_system:
        try:
            admin_system = AdminSystem(get_db_connection, auth_system)
            admin_routes = create_admin_routes(admin_system, auth_system)
            app.register_blueprint(admin_routes)
            logger.info("🔧 Admin system initialized and routes registered")
        except Exception as e:
            logger.error(f"❌ Failed to initialize admin system: {e}")
            admin_system = None
    else:
        logger.warning("⚠️ Admin system not available")

    # Universal Search Engine status check
    if search_engine:
        logger.info("🔍 Universal search engine ready - ALL search functions consolidated")
    else:
        logger.warning("⚠️ Universal search engine not available - some features may be limited")

    # Production hosting configuration (Railway/Heroku compatible)
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")

    logger.info(f"?? Server starting on {host}:{port}")

    try:
        app.run(
            host=host,
            port=port,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except Exception as e:
        logger.error(f"? Server startup failed: {e}")
        logger.error("Please check if ports are available and try again")
