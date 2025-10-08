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

# Database migrations module not available - using fallback functions for admin endpoints
DATABASE_MIGRATIONS_AVAILABLE = False
logger.info("ℹ️ Database migrations module not available - using fallback functions")

# Import spaCy ingredient normalizer
try:
    from core_systems.spacy_ingredient_normalizer import get_normalizer
    SPACY_NORMALIZER_AVAILABLE = True
    logger.info("✅ spaCy ingredient normalizer loaded")
except Exception as e:
    SPACY_NORMALIZER_AVAILABLE = False
    logger.warning(f"⚠️ spaCy normalizer not available: {e}")

# Define fallback functions for admin endpoints
def run_intelligence_migration():
    return {"success": False, "error": "Database migrations module not available"}

def run_schema_migration_endpoint(action=None):
    return {"success": False, "error": "Database migrations module not available"}

def add_sample_recipes():
    return {"success": False, "error": "Database migrations module not available"}

def check_database_info():
    return {"success": False, "error": "Database migrations module not available"}

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
app.secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-for-sessions-' + str(os.urandom(24).hex()))

# Add a simple direct test endpoint (not through blueprints) - for debugging
@app.route('/api/direct-test', methods=['GET'])
def direct_test():
    from datetime import datetime
    return jsonify({
        'success': True,
        'message': 'Direct route is working!',
        'timestamp': datetime.now().isoformat(),
        'method': 'direct_app_route'
    })

# Configure CORS properly - use only one method
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3000",
            "http://localhost:3001", 
            "http://localhost:3002",
            "http://localhost:3003",
            "http://localhost:3004",
            "http://localhost:3005",
            "http://localhost:3006",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
            "http://127.0.0.1:3002", 
            "http://127.0.0.1:3003",
            "http://127.0.0.1:3004",
            "http://127.0.0.1:3005",
            "http://127.0.0.1:3006",
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                -- 🍳 Community Sharing Features (Phase 1)
                is_community_shared BOOLEAN DEFAULT FALSE,
                shared_at TIMESTAMP NULL,
                community_title TEXT NULL,
                community_description TEXT NULL,
                community_background TEXT DEFAULT 'default',
                community_icon TEXT DEFAULT '🍽️',
                -- 🎤 Voice Recording Features (Phase 1 - Oct 6, 2025)
                user_id INTEGER,
                audio_url TEXT,
                recorded_by VARCHAR(255),
                recorded_date TIMESTAMP,
                transcript TEXT,
                recording_occasion VARCHAR(255),
                source_attribution VARCHAR(500)
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

        # 📰 Latest Updates Feature - Evergreen Content & Friend Activity
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_pieces (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                category VARCHAR(50) DEFAULT 'tip',
                is_active BOOLEAN DEFAULT true,
                sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_follows (
                id SERIAL PRIMARY KEY,
                follower_id INTEGER REFERENCES users(id),
                following_id INTEGER REFERENCES users(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(follower_id, following_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_feed (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                activity_type VARCHAR(50),
                reference_id INTEGER,
                title TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 💡 Community Cooking Tips (Phase 2 - Oct 6, 2025)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS community_cooking_tips (
                id SERIAL PRIMARY KEY,
                tip_text TEXT NOT NULL,
                dish_type VARCHAR(100),
                technique_category VARCHAR(50),
                ingredient_related VARCHAR(100),
                cuisine VARCHAR(50),
                source_recipe_id INTEGER REFERENCES recipes(id),
                contributed_by_user_id INTEGER REFERENCES users(id),
                contributed_date TIMESTAMP DEFAULT NOW(),
                helpfulness_score FLOAT DEFAULT 0.0,
                times_shown INTEGER DEFAULT 0,
                times_marked_helpful INTEGER DEFAULT 0,
                is_approved BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE,
                tags TEXT[],
                keywords TEXT[],
                UNIQUE(tip_text, dish_type)
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_tips_dish_type ON community_cooking_tips(dish_type)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_tips_technique ON community_cooking_tips(technique_category)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_tips_score ON community_cooking_tips(helpfulness_score DESC)
        ''')

        # 💡 Tip Interactions Tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tip_interactions (
                id SERIAL PRIMARY KEY,
                tip_id INTEGER REFERENCES community_cooking_tips(id),
                user_id INTEGER REFERENCES users(id),
                recipe_id INTEGER REFERENCES recipes(id),
                marked_helpful BOOLEAN,
                interaction_date TIMESTAMP DEFAULT NOW()
            )
        ''')

        # 🎤 Migration: Add voice recording columns to existing recipes table
        try:
            logger.info("🔄 Checking for voice recording columns migration...")
            cursor.execute("""
                ALTER TABLE recipes 
                ADD COLUMN IF NOT EXISTS user_id INTEGER,
                ADD COLUMN IF NOT EXISTS audio_url TEXT,
                ADD COLUMN IF NOT EXISTS recorded_by VARCHAR(255),
                ADD COLUMN IF NOT EXISTS recorded_date TIMESTAMP,
                ADD COLUMN IF NOT EXISTS transcript TEXT,
                ADD COLUMN IF NOT EXISTS recording_occasion VARCHAR(255),
                ADD COLUMN IF NOT EXISTS source_attribution VARCHAR(500)
            """)
            logger.info("✅ Voice recording columns migration complete")
        except Exception as migration_error:
            logger.warning(f"⚠️ Voice recording migration skipped (columns may already exist): {migration_error}")

        conn.commit()
        conn.close()
        logger.info("✅ Database tables initialized successfully")

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

@app.route('/api/recipes', methods=['GET'])
def get_recipes():
    """Get recipes with optional filtering"""
    try:
        # Check authentication first
        user_id, error_response, status_code = check_authentication()
        if error_response:
            return error_response, status_code
        
        # Get query parameters
        category = request.args.get('category')
        search = request.args.get('search')
        limit = int(request.args.get('limit', 50))
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Build query with filters (always filter by user_id for user's own recipes)
        where_conditions = ["r.user_id = %s"]
        params = [user_id]
        
        if category:
            where_conditions.append("r.category ILIKE %s")
            params.append(f"%{category}%")
            
        if search:
            where_conditions.append("(r.title ILIKE %s OR r.description ILIKE %s)")
            params.extend([f"%{search}%", f"%{search}%"])
        
        where_clause = "WHERE " + " AND ".join(where_conditions)
            
        query = f"""
            SELECT r.id, r.title, r.description, r.ingredients, r.instructions, 
                   r.category, r.source, r.confidence, r.prep_time, r.cook_time, 
                   r.servings, r.created_at, r.user_id,
                   u.name as author_name, u.email as author_email
            FROM recipes r
            LEFT JOIN users u ON r.user_id = u.id
            {where_clause}
            ORDER BY r.created_at DESC 
            LIMIT %s
        """
        params.append(limit)
        
        cursor.execute(query, params)
        recipes = cursor.fetchall()
        
        # Convert to list of dicts
        recipe_list = []
        for recipe in recipes:
            recipe_dict = dict(recipe)
            # Parse JSON fields if they're stored as strings
            if isinstance(recipe_dict.get('ingredients'), str):
                try:
                    recipe_dict['ingredients'] = json.loads(recipe_dict['ingredients'])
                except:
                    recipe_dict['ingredients'] = recipe_dict['ingredients'].split('\n') if recipe_dict['ingredients'] else []
            
            if isinstance(recipe_dict.get('instructions'), str):
                try:
                    recipe_dict['instructions'] = json.loads(recipe_dict['instructions'])
                except:
                    recipe_dict['instructions'] = recipe_dict['instructions'].split('\n') if recipe_dict['instructions'] else []
            
            # Ensure confidence_score is available for mobile app
            if recipe_dict.get('confidence'):
                recipe_dict['confidence_score'] = float(recipe_dict['confidence']) * 100
            else:
                recipe_dict['confidence_score'] = 85  # Default confidence
                
            recipe_list.append(recipe_dict)
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'recipes': recipe_list,
            'count': len(recipe_list)
        })
        
    except Exception as e:
        logger.error(f"Get recipes error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch recipes'
        }), 500

@app.route('/api/recipes', methods=['POST'])
def create_recipe():
    """Create a new recipe"""
    try:
        # Check authentication to get user_id
        user_id, error_response, status_code = check_authentication()
        if error_response:
            return error_response, status_code
        
        data = request.get_json()
        if not data or not data.get('title'):
            return jsonify({
                'success': False,
                'error': 'Recipe title is required'
            }), 400

        # 🔧 Ensure ingredients and instructions are properly formatted as JSON arrays
        ingredients = data.get('ingredients', '')
        if isinstance(ingredients, list):
            ingredients = json.dumps(ingredients)  # Convert list to JSON string
        elif isinstance(ingredients, str) and not ingredients.strip().startswith('['):
            # If it's a plain string, keep it as is
            pass
        
        instructions = data.get('instructions', '')
        if isinstance(instructions, list):
            instructions = json.dumps(instructions)  # Convert list to JSON string
        elif isinstance(instructions, str) and not instructions.strip().startswith('['):
            # If it's a plain string, keep it as is
            pass

        # Insert recipe into database WITH user_id
        conn = get_db_connection()
        cursor = conn.cursor()

        # PostgreSQL syntax with RETURNING - NOW includes user_id
        cursor.execute('''
            INSERT INTO recipes (title, description, ingredients, instructions, image_url, source, category, flavor_profile, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (
            data.get('title', ''),
            data.get('description', ''),
            ingredients,  # Now properly formatted
            instructions,  # Now properly formatted
            data.get('image_url', ''),
            data.get('source', ''),
            data.get('category', ''),
            data.get('flavor_profile', ''),
            user_id  # ✅ NOW includes user_id from authentication
        ))
        recipe_id = cursor.fetchone()['id']

        conn.commit()
        conn.close()

        logger.info(f"✅ Recipe created: {data.get('title')} (ID: {recipe_id}) for user {user_id}")

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
    """Get user's personal recipe collection with admin override and category filtering"""
    try:
        user_id, error_response, status_code = check_authentication()
        if error_response:
            return error_response, status_code
        
        # Get category filter from query parameters for Recent Imports functionality
        category_filter = request.args.get('category', 'all')
        logger.info(f"📂 User recipes request for category: '{category_filter}'")
        
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
            # Admin sees ALL recipes in the database for curation with category filtering
            logger.info(f"🔧 Admin requesting all recipes for curation (category: {category_filter})")
            try:
                conn = get_db_connection()
                cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                
                # Build query based on category filter
                base_query = '''
                    SELECT r.*, 
                           CASE WHEN r.is_template THEN 'template' 
                                WHEN r.template_id IS NOT NULL THEN 'template_copy' 
                                ELSE 'original' END as recipe_type,
                           u.email as owner_email
                    FROM recipes r
                    LEFT JOIN users u ON r.user_id = u.id
                '''
                
                # Add category filtering
                if category_filter == 'recent-imports':
                    # Filter for imported recipes
                    base_query += " WHERE r.category = 'imported' OR r.imported_at IS NOT NULL"
                elif category_filter != 'all':
                    # Filter by other categories
                    if category_filter in ['breakfast', 'lunch', 'dinner']:
                        base_query += f" WHERE r.meal_role = '{category_filter}'"
                    elif category_filter == 'desserts':
                        base_query += " WHERE r.meal_role = 'dessert'"
                    elif category_filter == 'one-pot':
                        base_query += " WHERE r.is_one_pot = true"
                    elif category_filter == 'quick':
                        base_query += " WHERE r.time_min <= 30"
                
                base_query += " ORDER BY r.created_at DESC"
                
                cursor.execute(base_query)
                all_recipes = [dict(row) for row in cursor.fetchall()]
                conn.close()
                
                logger.info(f"🔧 Admin retrieved {len(all_recipes)} recipes for category '{category_filter}'")
                return jsonify({
                    'success': True,
                    'data': all_recipes,
                    'count': len(all_recipes),
                    'admin_access': True,
                    'category': category_filter,
                    'message': f'Found {len(all_recipes)} recipes in category "{category_filter}"'
                })
                
            except Exception as e:
                logger.error(f"❌ Failed to get admin recipes: {e}")
                return jsonify({'success': False, 'error': 'Failed to retrieve admin recipes'}), 500
        else:
            # Regular users get their personal collection with category filtering
            if category_filter == 'all':
                recipes = template_system.get_user_recipes(user_id)
            else:
                # Get all user recipes first, then filter by category
                all_user_recipes = template_system.get_user_recipes(user_id)
                
                # Filter by category
                if category_filter == 'recent-imports':
                    recipes = [r for r in all_user_recipes if r.get('category') == 'imported' or r.get('imported_at')]
                elif category_filter in ['breakfast', 'lunch', 'dinner']:
                    recipes = [r for r in all_user_recipes if r.get('meal_role') == category_filter]
                elif category_filter == 'desserts':
                    recipes = [r for r in all_user_recipes if r.get('meal_role') == 'dessert']
                elif category_filter == 'one-pot':
                    recipes = [r for r in all_user_recipes if r.get('is_one_pot')]
                elif category_filter == 'quick':
                    recipes = [r for r in all_user_recipes if r.get('time_min') and r.get('time_min') <= 30]
                else:
                    recipes = all_user_recipes
            
            # Apply 500 recipe limit for regular users
            if len(recipes) > 500:
                recipes = recipes[:500]
                limited_message = f"Showing first 500 recipes in category '{category_filter}'"
            else:
                limited_message = f"Found {len(recipes)} recipes in category '{category_filter}'"
            
            logger.info(f"👤 User {user_id} retrieved {len(recipes)} recipes for category '{category_filter}'")
            return jsonify({
                'success': True,
                'data': recipes,
                'count': len(recipes),
                'admin_access': False,
                'category': category_filter,
                'message': limited_message
            })
        
    except Exception as e:
        logger.error(f"Get user recipes error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# =====================================================
# 👤 PROFILE API ENDPOINTS
# =====================================================

@app.route('/api/profile', methods=['GET'])
def get_user_profile():
    """Get complete user profile information"""
    try:
        user_id, error_response, status_code = check_authentication()
        if error_response:
            logger.error(f"❌ Authentication failed for profile request: {error_response}")
            return error_response, status_code
        
        logger.info(f"👤 Getting profile for user {user_id}")
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Get user basic information including avatar
        cursor.execute("""
            SELECT id, name, email, created_at, avatar_background, avatar_icon
            FROM users 
            WHERE id = %s
        """, (user_id,))
        
        user_data = cursor.fetchone()
        if not user_data:
            logger.error(f"❌ User {user_id} not found in database")
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        logger.info(f"✅ Found user data for {user_data['email']}")
        
        # Get user statistics (with safe table checks)
        try:
            cursor.execute("""
                SELECT 
                    (SELECT COUNT(*) FROM recipes WHERE user_id = %s) as recipes_saved,
                    (SELECT COUNT(*) FROM recipes WHERE user_id = %s AND COALESCE(is_community_shared, false) = true) as recipes_shared
            """, (user_id, user_id))
            
            basic_stats = cursor.fetchone()
            logger.info(f"🔍 DEBUG: Basic stats query result: {basic_stats}")
            logger.info(f"🔍 DEBUG: Basic stats type: {type(basic_stats)}")
            
            # Try to get grocery list count (table might not exist)
            grocery_count = 0
            try:
                cursor.execute("SELECT COUNT(*) as grocery_count FROM grocery_lists WHERE user_id = %s", (user_id,))
                grocery_result = cursor.fetchone()
                grocery_count = grocery_result['grocery_count'] if grocery_result else 0
                logger.info(f"🛒 DEBUG: Found {grocery_count} grocery lists for user {user_id}")
                
                # Additional debugging - show the actual lists
                cursor.execute("SELECT id, list_name, user_id, created_at FROM grocery_lists WHERE user_id = %s ORDER BY created_at DESC LIMIT 5", (user_id,))
                debug_lists = cursor.fetchall()
                logger.info(f"🛒 DEBUG: Recent grocery lists for user {user_id}: {[dict(row) for row in debug_lists]}")
                
            except psycopg2.Error as e:
                logger.error(f"grocery_lists table error: {e}")
                logger.info("grocery_lists table not found, using 0")
                grocery_count = 0
            
            # Try to get friends count (table might not exist)
            friends_count = 0
            try:
                cursor.execute("SELECT COUNT(*) as friends_count FROM friends WHERE (user_id = %s OR friend_user_id = %s) AND status = 'accepted'", (user_id, user_id))
                friends_result = cursor.fetchone()
                friends_count = friends_result['friends_count'] if friends_result else 0
            except psycopg2.Error:
                logger.info("friends table not found, using 0")
                friends_count = 0

            # Try to get meal plans count (table might not exist)  
            meal_plans_count = 0
            try:
                cursor.execute("SELECT COUNT(*) as meal_plans_count FROM meal_plans WHERE user_id = %s", (user_id,))
                meal_plans_result = cursor.fetchone()
                meal_plans_count = meal_plans_result['meal_plans_count'] if meal_plans_result else 0
                logger.info(f"📅 DEBUG: Found {meal_plans_count} meal plans for user {user_id}")
            except psycopg2.Error:
                logger.info("meal_plans table not found, using 0")
                meal_plans_count = 0
            
            # Try to get meal plans count (table might not exist)
            meal_plans_count = 0
            try:
                cursor.execute("SELECT COUNT(*) FROM meal_plans WHERE user_id = %s", (user_id,))
                meal_plans_result = cursor.fetchone()
                meal_plans_count = meal_plans_result[0] if meal_plans_result else 0
            except psycopg2.Error:
                logger.info("meal_plans table not found, using 0")
                meal_plans_count = 0
            
            stats_data = {
                'recipes_saved': basic_stats['recipes_saved'] if basic_stats and basic_stats['recipes_saved'] is not None else 0,
                'recipes_shared': basic_stats['recipes_shared'] if basic_stats and basic_stats['recipes_shared'] is not None else 0,
                'grocery_lists_created': grocery_count,
                'meal_plans_created': meal_plans_count,
                'friends_count': friends_count
            }
            
        except Exception as stats_error:
            logger.error(f"Stats query error: {stats_error}")
            logger.error(f"Stats query error details: {type(stats_error).__name__}: {str(stats_error)}")
            
            # Still provide detailed debug info even with error
            try:
                cursor.execute("SELECT COUNT(*) as grocery_count FROM grocery_lists WHERE user_id = %s", (user_id,))
                grocery_result = cursor.fetchone()
                grocery_debug_count = grocery_result['grocery_count'] if grocery_result else 0
                logger.error(f"🛒 DEBUG FALLBACK: Found {grocery_debug_count} grocery lists for user {user_id}")
            except Exception as debug_error:
                logger.error(f"🛒 DEBUG FALLBACK ERROR: {debug_error}")
                
            stats_data = {
                'recipes_saved': 0,
                'recipes_shared': 0,
                'grocery_lists_created': 0,
                'meal_plans_created': 0,
                'friends_count': 0
            }
        
        # Create username from email (like the mobile app expects)
        email = user_data['email']
        username = email.split('@')[0] + 'Chef' if email else 'YesChef User'
        
        # Build profile response
        profile = {
            'id': user_data['id'],
            'username': username,
            'firstName': 'Not Set',  # TODO: Add to database schema
            'lastName': 'Not Set',   # TODO: Add to database schema
            'email': user_data['email'],
            'name': user_data.get('name', 'User'),
            'cookingLevel': 'Beginner',      # TODO: Add to database schema
            'householdSize': 2,              # TODO: Add to database schema
            'measurementUnits': 'Imperial',  # TODO: Add to database schema
            'profilePhotoUrl': None,         # TODO: Add to database schema
            'created_at': user_data.get('created_at'),
            'avatar': {
                'background': user_data.get('avatar_background', 'default'),
                'icon': user_data.get('avatar_icon', '🍎')
            },
            'stats': {
                'recipesSaved': stats_data['recipes_saved'] if stats_data else 0,
                'recipesShared': stats_data['recipes_shared'] if stats_data else 0,
                'groceryListsCreated': stats_data['grocery_lists_created'] if stats_data else 0,
                'friendsCount': stats_data['friends_count'] if stats_data else 0,
                'mealPlansCreated': stats_data['meal_plans_created'] if stats_data else 0
            }
        }
        
        logger.info(f"✅ Profile retrieved for {email} with {profile['stats']['recipesSaved']} recipes")
        
        return jsonify({
            'success': True,
            'profile': profile
        })
        
    except Exception as e:
        logger.error(f"❌ Get profile error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/api/profile', methods=['PUT'])
def update_user_profile():
    """Update user profile information"""
    try:
        user_id, error_response, status_code = check_authentication()
        if error_response:
            return error_response, status_code
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        logger.info(f"👤 Updating profile for user {user_id} with data: {list(data.keys())}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # For now, we can only update the name field (which exists in current schema)
        # TODO: Add other fields to database schema later
        updatable_fields = []
        values = []
        
        if 'name' in data:
            updatable_fields.append('name = %s')
            values.append(data['name'])
            
        # Also update email if provided (email column exists in users table)
        if 'email' in data:
            updatable_fields.append('email = %s')
            values.append(data['email'])
        
        if updatable_fields:
            values.append(user_id)  # For WHERE clause
            update_query = f"""
                UPDATE users 
                SET {', '.join(updatable_fields)}
                WHERE id = %s
            """
            cursor.execute(update_query, values)
            conn.commit()
            
            logger.info(f"✅ Profile updated for user {user_id} - fields: {updatable_fields}")
        else:
            logger.warning(f"⚠️ No updatable fields provided for user {user_id}")
        
        logger.info(f"✅ Profile update completed for user {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully'
        })
        
    except Exception as e:
        logger.error(f"❌ Update profile error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/api/profile/avatar', methods=['PUT'])
def update_user_avatar():
    """Update user profile avatar (background and icon)"""
    try:
        user_id, error_response, status_code = check_authentication()
        if error_response:
            return error_response, status_code
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No avatar data provided'
            }), 400
        
        # Validate required fields
        if 'background' not in data or 'icon' not in data:
            return jsonify({
                'success': False,
                'error': 'Both background and icon are required'
            }), 400
        
        background = data['background']
        icon = data['icon']
        
        logger.info(f"🎨 Updating avatar for user {user_id}: background={background}, icon={icon}")
        
        # Validate background options
        valid_backgrounds = [
            'default', 'warm', 'fresh', 'elegant', 'sunset', 'ocean', 
            'earth', 'lavender', 'mint', 'peach', 'sky', 'rose'
        ]
        
        if background not in valid_backgrounds:
            return jsonify({
                'success': False,
                'error': f'Invalid background. Must be one of: {", ".join(valid_backgrounds)}'
            }), 400
        
        # Basic validation for icon (should be emoji character)
        if len(icon) > 10:  # Emojis can be multiple bytes but shouldn't be extremely long
            return jsonify({
                'success': False,
                'error': 'Icon must be a valid emoji character'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update avatar fields
        cursor.execute("""
            UPDATE users 
            SET avatar_background = %s, avatar_icon = %s
            WHERE id = %s
        """, (background, icon, user_id))
        
        conn.commit()
        
        logger.info(f"✅ Avatar updated successfully for user {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Avatar updated successfully',
            'avatar': {
                'background': background,
                'icon': icon
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Update avatar error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/api/profile/avatar', methods=['GET'])
def get_user_avatar():
    """Get user profile avatar"""
    try:
        user_id, error_response, status_code = check_authentication()
        if error_response:
            return error_response, status_code
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Get avatar data
        cursor.execute("""
            SELECT avatar_background, avatar_icon
            FROM users 
            WHERE id = %s
        """, (user_id,))
        
        user_data = cursor.fetchone()
        if not user_data:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        avatar = {
            'background': user_data.get('avatar_background', 'default'),
            'icon': user_data.get('avatar_icon', '🍎')
        }
        
        logger.info(f"🎨 Retrieved avatar for user {user_id}: {avatar}")
        
        return jsonify({
            'success': True,
            'avatar': avatar
        })
        
    except Exception as e:
        logger.error(f"❌ Get avatar error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/api/profile/stats', methods=['GET'])
def get_user_stats():
    """Get user statistics for dashboard"""
    try:
        user_id, error_response, status_code = check_authentication()
        if error_response:
            return error_response, status_code
        
        logger.info(f"📊 Getting stats for user {user_id}")
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Get comprehensive user statistics
        cursor.execute("""
            SELECT 
                (SELECT COUNT(*) FROM recipes WHERE user_id = %s) as recipes_saved,
                (SELECT COUNT(*) FROM recipes WHERE user_id = %s AND is_community_shared = true) as recipes_shared,
                (SELECT COUNT(*) FROM grocery_lists WHERE user_id = %s) as grocery_lists_created,
                (SELECT COUNT(*) FROM friends WHERE (user_id = %s OR friend_user_id = %s) AND status = 'accepted') as friends_count,
                (SELECT COUNT(*) FROM meal_plans WHERE user_id = %s) as meal_plans_created
        """, (user_id, user_id, user_id, user_id, user_id, user_id))
        
        stats = cursor.fetchone()
        
        return jsonify({
            'success': True,
            'stats': {
                'recipesSaved': stats['recipes_saved'] if stats else 0,
                'recipesShared': stats['recipes_shared'] if stats else 0,
                'groceryListsCreated': stats['grocery_lists_created'] if stats else 0,
                'friendsCount': stats['friends_count'] if stats else 0,
                'mealPlansCreated': stats['meal_plans_created'] if stats else 0
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Get stats error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if 'conn' in locals():
            conn.close()

# 🎨 Profile Avatar Endpoints
@app.route('/api/profile/avatar', methods=['GET'])
def get_profile_avatar():
    """Get user's profile avatar configuration"""
    try:
        user_id, error_response, status_code = check_authentication()
        if error_response:
            return error_response, status_code
        
        logger.info(f"🎨 Getting avatar for user {user_id}")
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute("""
            SELECT avatar_background, avatar_icon 
            FROM users 
            WHERE id = %s
        """, (user_id,))
        
        user = cursor.fetchone()
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'avatar': {
                'background': user['avatar_background'] or 'default',
                'icon': user['avatar_icon'] or '🍎'
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Get avatar error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/api/profile/avatar', methods=['PUT'])
def save_profile_avatar():
    """Save user's profile avatar configuration"""
    try:
        user_id, error_response, status_code = check_authentication()
        if error_response:
            return error_response, status_code
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        background = data.get('background', 'default')
        icon = data.get('icon', '🍎')
        
        logger.info(f"🎨 Saving avatar for user {user_id}: {background} + {icon}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update user's avatar fields
        cursor.execute("""
            UPDATE users 
            SET avatar_background = %s, 
                avatar_icon = %s, 
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (background, icon, user_id))
        
        if cursor.rowcount == 0:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        conn.commit()
        
        logger.info(f"✅ Avatar saved successfully for user {user_id}")
        
        return jsonify({
            'success': True,
            'avatar': {
                'background': background,
                'icon': icon
            },
            'message': 'Avatar saved successfully'
        })
        
    except Exception as e:
        logger.error(f"❌ Save avatar error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if 'conn' in locals():
            conn.close()

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

@app.route('/api/recipes/<recipe_id>', methods=['DELETE'])
def delete_user_recipe(recipe_id):
    """Delete a user's recipe - only works for user-owned recipes, not templates"""
    try:
        user_id, error_response, status_code = check_authentication()
        if error_response:
            return error_response, status_code
        
        logger.info(f"🗑️ User {user_id} attempting to delete recipe {recipe_id}")
        
        if not template_system:
            return jsonify({
                'success': False,
                'error': 'Template system not available'
            }), 503
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # First check if the recipe exists and belongs to the user
        cursor.execute('''
            SELECT id, title, is_template, user_id 
            FROM recipes 
            WHERE id = %s
        ''', (recipe_id,))
        
        recipe = cursor.fetchone()
        if not recipe:
            conn.close()
            logger.warning(f"❌ Recipe {recipe_id} not found for deletion by user {user_id}")
            
            # Let's check if the recipe exists for any user for debugging
            cursor2 = get_db_connection().cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor2.execute('SELECT id, user_id, is_template FROM recipes WHERE id = %s', (recipe_id,))
            any_recipe = cursor2.fetchone()
            cursor2.close()
            
            if any_recipe:
                logger.info(f"🔍 Recipe {recipe_id} exists but belongs to user {any_recipe['user_id']}, is_template={any_recipe['is_template']}")
                return jsonify({
                    'success': False,
                    'error': f'Recipe {recipe_id} not found or access denied'
                }), 404
            else:
                logger.info(f"🔍 Recipe {recipe_id} does not exist in database at all")
                return jsonify({
                    'success': False,
                    'error': f'Recipe {recipe_id} does not exist'
                }), 404
        
        logger.info(f"🔍 Recipe details: ID={recipe['id']}, title='{recipe['title']}', is_template={recipe['is_template']}, user_id={recipe['user_id']}")
        
        # Check ownership - users can only delete their own recipes, not templates
        if recipe['is_template']:
            conn.close()
            logger.warning(f"❌ User {user_id} tried to delete template recipe {recipe_id}")
            return jsonify({
                'success': False,
                'error': 'Cannot delete template recipes. Templates can only be removed by administrators.'
            }), 403
        
        if recipe['user_id'] != user_id:
            conn.close()
            if recipe['user_id'] is None:
                logger.warning(f"❌ User {user_id} tried to delete orphaned recipe {recipe_id} (no owner)")
                return jsonify({
                    'success': False,
                    'error': f'This recipe has no owner. You can claim it first using the "Claim Recipe" option, then delete it.',
                    'can_claim': True,
                    'recipe_id': recipe_id
                }), 403
            else:
                logger.warning(f"❌ User {user_id} tried to delete recipe {recipe_id} owned by user {recipe['user_id']}")
                return jsonify({
                    'success': False,
                    'error': f'You can only delete your own recipes. This recipe belongs to user {recipe["user_id"]} but you are user {user_id}.'
                }), 403
        
        # Delete the recipe (only user-owned, non-template recipes)
        cursor.execute('''
            DELETE FROM recipes 
            WHERE id = %s AND user_id = %s AND is_template = FALSE
        ''', (recipe_id, user_id))
        
        if cursor.rowcount == 0:
            conn.close()
            logger.warning(f"❌ Failed to delete recipe {recipe_id} for user {user_id}")
            return jsonify({
                'success': False,
                'error': 'Failed to delete recipe - recipe may not belong to you or may be a template'
            }), 403
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ User {user_id} deleted recipe {recipe_id}: {recipe['title']}")
        
        return jsonify({
            'success': True,
            'message': f'Recipe "{recipe["title"]}" deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Delete user recipe error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/recipes/<recipe_id>/info', methods=['GET'])
def get_recipe_debug_info(recipe_id):
    """Debug endpoint to check recipe ownership and details"""
    try:
        user_id, error_response, status_code = check_authentication()
        if error_response:
            return error_response, status_code
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute('''
            SELECT id, title, is_template, user_id, template_id, created_at
            FROM recipes 
            WHERE id = %s
        ''', (recipe_id,))
        
        recipe = cursor.fetchone()
        conn.close()
        
        if not recipe:
            return jsonify({
                'success': False,
                'error': 'Recipe not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'recipe_id': recipe['id'],
                'title': recipe['title'],
                'is_template': recipe['is_template'],
                'user_id': recipe['user_id'],
                'template_id': recipe['template_id'],
                'created_at': str(recipe['created_at']),
                'current_user_id': user_id,
                'can_delete': recipe['user_id'] == user_id and not recipe['is_template']
            }
        })
        
    except Exception as e:
        logger.error(f"Recipe debug info error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/debug/user-recipes', methods=['GET'])
def debug_user_recipes():
    """Debug endpoint to check what recipes exist for the current user"""
    try:
        user_id, error_response, status_code = check_authentication()
        if error_response:
            return error_response, status_code
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Get all recipes that could be visible to this user
        cursor.execute('''
            SELECT id, title, is_template, user_id, template_id, created_at
            FROM recipes 
            ORDER BY id
            LIMIT 20
        ''')
        
        all_recipes = cursor.fetchall()
        
        # Get recipes specifically for this user
        cursor.execute('''
            SELECT id, title, is_template, user_id, template_id, created_at
            FROM recipes 
            WHERE user_id = %s OR user_id IS NULL
            ORDER BY id
        ''', (user_id,))
        
        user_recipes = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'current_user_id': user_id,
            'all_recipes_sample': [dict(r) for r in all_recipes],
            'user_recipes': [dict(r) for r in user_recipes],
            'total_all_recipes': len(all_recipes),
            'total_user_recipes': len(user_recipes)
        })
        
    except Exception as e:
        logger.error(f"Debug user recipes error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/debug/all-recipes-public', methods=['GET'])
def debug_all_recipes_public():
    """Public debug endpoint to check what recipes exist (no auth required)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Get all recipes in the database
        cursor.execute('''
            SELECT id, title, is_template, user_id, template_id, created_at
            FROM recipes 
            ORDER BY id
            LIMIT 50
        ''')
        
        all_recipes = cursor.fetchall()
        
        # Get count by user_id
        cursor.execute('''
            SELECT user_id, COUNT(*) as count
            FROM recipes 
            GROUP BY user_id
            ORDER BY user_id
        ''')
        
        user_counts = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'all_recipes': [dict(r) for r in all_recipes],
            'total_recipes': len(all_recipes),
            'recipes_by_user': [dict(r) for r in user_counts],
            'message': 'This shows all recipes in the database for debugging'
        })
        
    except Exception as e:
        logger.error(f"Debug all recipes public error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/debug/recipe-list-api', methods=['GET'])
def debug_recipe_list_api():
    """Debug what the recipe list API actually returns"""
    try:
        user_id, error_response, status_code = check_authentication()
        if error_response:
            return error_response, status_code
        
        # Call the same function that the recipe list uses
        if template_system:
            recipes = template_system.get_user_recipes(user_id, include_templates=True)
            
            return jsonify({
                'success': True,
                'user_id': user_id,
                'total_recipes': len(recipes),
                'recipe_ids': [r.get('id') for r in recipes],
                'recipes_sample': recipes[:10],  # First 10 recipes
                'message': 'This is what the recipe list API returns for your user'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Template system not available'
            }), 503
        
    except Exception as e:
        logger.error(f"Debug recipe list API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/recipes/<recipe_id>/claim', methods=['POST'])
def claim_orphaned_recipe(recipe_id):
    """Claim ownership of a recipe that has no user_id (orphaned recipe)"""
    try:
        user_id, error_response, status_code = check_authentication()
        if error_response:
            return error_response, status_code
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Check if recipe exists and is orphaned (no user_id)
        cursor.execute('''
            SELECT id, title, is_template, user_id 
            FROM recipes 
            WHERE id = %s
        ''', (recipe_id,))
        
        recipe = cursor.fetchone()
        if not recipe:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Recipe not found'
            }), 404
        
        # Only allow claiming orphaned recipes (user_id is NULL) that are not templates
        if recipe['is_template']:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Cannot claim template recipes'
            }), 403
        
        if recipe['user_id'] is not None:
            conn.close()
            return jsonify({
                'success': False,
                'error': f'Recipe already belongs to user {recipe["user_id"]}'
            }), 403
        
        # Claim the recipe by setting user_id
        cursor.execute('''
            UPDATE recipes 
            SET user_id = %s 
            WHERE id = %s AND user_id IS NULL AND is_template = FALSE
        ''', (user_id, recipe_id))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Failed to claim recipe'
            }), 500
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ User {user_id} claimed orphaned recipe {recipe_id}: {recipe['title']}")
        
        return jsonify({
            'success': True,
            'message': f'Successfully claimed recipe "{recipe["title"]}"'
        })
        
    except Exception as e:
        logger.error(f"Claim recipe error: {e}")
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

    # Check authentication
    user_id, error_response, status_code = check_authentication()
    if error_response:
        return error_response, status_code

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

        logger.info(f"💾 User {user_id} creating meal plan: {plan_name}")

        meal_planner = MealPlanningSystem()
        plan_id = meal_planner.create_meal_plan(plan_name, week_start_date, meal_data, user_id)
        
        logger.info(f"✅ Meal plan created successfully: ID {plan_id}")
        
        return jsonify({
            'success': True,
            'plan_id': plan_id,
            'plan_name': plan_name,
            'week_start_date': week_start_date
        })

    except Exception as e:
        logger.error(f"Create meal plan error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/meal-plans', methods=['GET'])
def list_meal_plans():
    """List all meal plans for the authenticated user (owned + shared)"""
    if not MEAL_PLANNING_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Meal planning system not available'
        }), 503

    # Check authentication
    user_id, error_response, status_code = check_authentication()
    if error_response:
        return error_response, status_code

    try:
        limit = request.args.get('limit', 50, type=int)

        meal_planner = MealPlanningSystem()
        owned_plans = meal_planner.list_user_meal_plans(user_id, limit=limit)
        
        # Get shared meal plans from collaboration system
        shared_plans = []
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get meal plan IDs shared with this user
            cursor.execute("""
                SELECT DISTINCT c.resource_id, c.permission_level, c.created_at,
                       u.name as owner_name
                FROM collaborations c
                JOIN users u ON c.invited_by = u.id
                WHERE c.resource_type = 'meal_plan' 
                AND c.user_id = %s 
                AND c.status = 'active'
                ORDER BY c.created_at DESC
            """, (user_id,))
            
            collaborations = cursor.fetchall()
            
            # For each shared meal plan, try to load it
            for collab in collaborations:
                try:
                    shared_plan = meal_planner.get_meal_plan(collab['resource_id'])
                    if shared_plan:
                        # Mark it as shared and add owner info
                        shared_plan['is_shared'] = True
                        shared_plan['permission_level'] = collab['permission_level']
                        shared_plan['shared_by'] = collab['owner_name']
                        shared_plan['plan_name'] = f"📤 {shared_plan.get('plan_name', f'Shared Plan #{collab["resource_id"]}')} (by {collab['owner_name']})"
                        shared_plans.append(shared_plan)
                except Exception as e:
                    logger.warning(f"Could not load shared meal plan {collab['resource_id']}: {e}")
                    continue
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.warning(f"Could not load shared meal plans: {e}")
            shared_plans = []
        
        # Combine owned and shared plans
        all_plans = owned_plans + shared_plans
        
        logger.info(f"📋 User {user_id} meal plans: {len(owned_plans)} owned + {len(shared_plans)} shared = {len(all_plans)} total")
        
        return jsonify({
            'success': True,
            'meal_plans': all_plans,
            'count': len(all_plans),
            'owned_count': len(owned_plans),
            'shared_count': len(shared_plans)
        })

    except Exception as e:
        logger.error(f"List meal plans error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/meal-plans/<int:plan_id>', methods=['GET'])
def get_meal_plan(plan_id):
    """Get a specific meal plan for the authenticated user (owned or shared)"""
    if not MEAL_PLANNING_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Meal planning system not available'
        }), 503

    # Check authentication
    user_id, error_response, status_code = check_authentication()
    if error_response:
        return error_response, status_code

    try:
        meal_planner = MealPlanningSystem()
        
        # First try to get as owner
        plan = meal_planner.get_user_meal_plan(plan_id, user_id)
        
        # If not found as owner, check if user has collaboration access
        if not plan:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # Check if user has collaboration access
                cursor.execute("""
                    SELECT permission_level FROM collaborations 
                    WHERE resource_type = 'meal_plan' AND resource_id = %s 
                    AND user_id = %s AND status = 'active'
                """, (plan_id, user_id))
                
                collaboration = cursor.fetchone()
                if collaboration:
                    # User has access via collaboration, load the plan
                    plan = meal_planner.get_meal_plan(plan_id)
                    if plan:
                        plan['is_shared'] = True
                        plan['permission_level'] = collaboration['permission_level']
                        logger.info(f"📤 User {user_id} accessing shared meal plan {plan_id} with {collaboration['permission_level']} permission")
                
                cursor.close()
                conn.close()
                
            except Exception as e:
                logger.warning(f"Could not check collaboration access for meal plan {plan_id}: {e}")

        if not plan:
            return jsonify({
                'success': False,
                'error': 'Meal plan not found or access denied'
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

@app.route('/api/meal-plans/<int:plan_id>', methods=['DELETE'])
def delete_meal_plan(plan_id):
    """Delete a meal plan"""
    if not MEAL_PLANNING_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Meal planning system not available'
        }), 503
    
    # Check authentication
    user_id, error_response, status_code = check_authentication()
    if error_response:
        return error_response, status_code
    
    try:
        logger.info(f"User {user_id} deleting meal plan {plan_id}")
        
        meal_planner = MealPlanningSystem()
        success = meal_planner.delete_meal_plan(plan_id)
        
        if success:
            logger.info(f"Meal plan {plan_id} deleted successfully")
            return jsonify({
                'success': True,
                'message': f'Meal plan deleted successfully',
                'plan_id': plan_id
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Meal plan not found or could not be deleted'
            }), 404

    except Exception as e:
        logger.error(f"Delete meal plan error: {e}")
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
# 🍳 COMMUNITY RECIPE SHARING API
# ===================================

@app.route('/api/community/recipes', methods=['POST'])
def share_recipe():
    """Share a recipe with the community"""
    try:
        # Check authentication
        user_id, error_response, status_code = check_authentication()
        if error_response:
            return error_response, status_code
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        recipe_id = data.get('recipe_id')
        community_title = data.get('community_title', '').strip()
        community_description = data.get('community_description', '').strip()
        community_background = data.get('community_background', 'default')
        community_icon = data.get('community_icon', '🍽️')
        
        if not recipe_id:
            return jsonify({'success': False, 'error': 'Recipe ID is required'}), 400
        if not community_title:
            return jsonify({'success': False, 'error': 'Community title is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First, check if the recipe belongs to the user
        cursor.execute('SELECT id, title FROM recipes WHERE id = %s AND user_id = %s', [recipe_id, user_id])
        recipe = cursor.fetchone()
        if not recipe:
            return jsonify({'success': False, 'error': 'Recipe not found or not owned by user'}), 404
        
        # Update the recipe with community sharing data
        cursor.execute("""
            UPDATE recipes 
            SET is_community_shared = TRUE,
                shared_at = CURRENT_TIMESTAMP,
                community_title = %s,
                community_description = %s,
                community_background = %s,
                community_icon = %s
            WHERE id = %s AND user_id = %s
        """, [community_title, community_description, community_background, community_icon, recipe_id, user_id])
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Recipe {recipe_id} shared to community by user {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Recipe shared successfully!',
            'recipe_id': recipe_id,
            'community_title': community_title
        })
        
    except Exception as e:
        logger.error(f"❌ Share recipe error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/community/recipes', methods=['GET'])
def get_community_recipes():
    """Get shared community recipes"""
    try:
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        sort_by = request.args.get('sort', 'recent')  # recent, popular, trending
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Build query based on sort parameter
        if sort_by == 'popular':
            # TODO: Add likes/saves count for popularity sorting
            order_clause = "ORDER BY shared_at DESC"
        elif sort_by == 'trending':
            # TODO: Add trending algorithm based on recent engagement
            order_clause = "ORDER BY shared_at DESC"
        else:  # recent
            order_clause = "ORDER BY shared_at DESC"
        
        # Get community recipes with user info AND existing recipe content only
        cursor.execute(f"""
            SELECT 
                r.id,
                COALESCE(r.community_title, r.title) as title,
                r.community_title,
                COALESCE(r.community_description, r.description) as description,
                r.community_description,
                r.community_background,
                r.community_icon,
                r.shared_at,
                -- 🔧 FIX: Only include columns that definitely exist
                r.ingredients,
                r.instructions,
                r.servings,
                r.prep_time,
                r.cook_time,
                r.source,
                u.email,
                -- Use actual user name/username instead of generating from email
                COALESCE(u.name, LEFT(u.email, POSITION('@' IN u.email) - 1) || 'Chef', 'AnonymousChef') as display_name,
                u.avatar_background,
                u.avatar_icon,
                0 as likes  -- TODO: Add real likes count when like system is implemented
            FROM recipes r
            LEFT JOIN users u ON r.user_id = u.id
            WHERE r.is_community_shared = TRUE
            {order_clause}
            LIMIT %s OFFSET %s
        """, [limit, offset])
        
        recipes = cursor.fetchall()
        
        # Convert to list of dicts for JSON serialization
        community_recipes = []
        for recipe in recipes:
            community_recipes.append({
                'id': recipe['id'],
                'title': recipe['title'],
                'community_title': recipe['community_title'],
                'description': recipe['description'],
                'community_description': recipe['community_description'],
                'community_background': recipe['community_background'],
                'community_icon': recipe['community_icon'],
                'shared_at': recipe['shared_at'].isoformat() if recipe['shared_at'] else None,
                'user': recipe['display_name'],
                'shared_by': recipe['display_name'],
                'author_avatar': {
                    'background': recipe['avatar_background'] or 'default',
                    'icon': recipe['avatar_icon'] or '🍎'
                },
                'likes': recipe['likes'],
                'image': recipe['community_icon'],  # For compatibility with existing frontend
                # 🔧 FIX: Only include existing recipe content columns
                'ingredients': recipe['ingredients'],
                'instructions': recipe['instructions'],
                'servings': recipe['servings'],
                'prep_time': recipe['prep_time'],
                'cook_time': recipe['cook_time'],
                'source': recipe['source'],
                # Default values for missing columns
                'tags': [],  # Default empty array since column doesn't exist
                'difficulty': 'medium'  # Default value since column doesn't exist
            })
        
        conn.close()
        
        logger.info(f"📱 Served {len(community_recipes)} community recipes (sort: {sort_by})")
        
        return jsonify({
            'success': True,
            'recipes': community_recipes,
            'total': len(community_recipes),
            'has_more': len(community_recipes) == limit
        })
        
    except Exception as e:
        logger.error(f"❌ Get community recipes error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/community/recipes/<int:recipe_id>', methods=['GET'])
def get_community_recipe_detail(recipe_id):
    """Get detailed view of a community recipe"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Get full recipe details for community viewing
        cursor.execute("""
            SELECT 
                r.*,
                u.email,
                CASE 
                    WHEN u.email IS NOT NULL THEN LEFT(u.email, POSITION('@' IN u.email) - 1) || 'Chef'
                    ELSE 'AnonymousChef'
                END as display_name
            FROM recipes r
            LEFT JOIN users u ON r.user_id = u.id
            WHERE r.id = %s AND r.is_community_shared = TRUE
        """, [recipe_id])
        
        recipe = cursor.fetchone()
        if not recipe:
            return jsonify({'success': False, 'error': 'Community recipe not found'}), 404
        
        # Convert to dict for JSON response
        recipe_data = dict(recipe)
        recipe_data['shared_at'] = recipe_data['shared_at'].isoformat() if recipe_data['shared_at'] else None
        recipe_data['created_at'] = recipe_data['created_at'].isoformat() if recipe_data['created_at'] else None
        
        conn.close()
        
        return jsonify({
            'success': True,
            'recipe': recipe_data
        })
        
    except Exception as e:
        logger.error(f"❌ Get community recipe detail error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/community/recipes/<int:recipe_id>', methods=['DELETE'])
def delete_community_recipe(recipe_id):
    """Remove a recipe from community sharing (unshare, don't delete)"""
    try:
        # Check authentication
        user_id, error_response, status_code = check_authentication()
        if error_response:
            return error_response, status_code
        
        logger.info(f"🗑️ User {user_id} attempting to unshare community recipe {recipe_id}")
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # First, verify the recipe exists and is owned by the user
        cursor.execute("""
            SELECT id, title, user_id, is_community_shared
            FROM recipes 
            WHERE id = %s
        """, (recipe_id,))
        
        recipe = cursor.fetchone()
        if not recipe:
            logger.warning(f"❌ Recipe {recipe_id} not found for deletion")
            return jsonify({
                'success': False,
                'error': 'Recipe not found'
            }), 404
        
        # Check ownership - users can only unshare their own recipes
        if recipe['user_id'] != user_id:
            logger.warning(f"❌ User {user_id} tried to unshare recipe {recipe_id} owned by user {recipe['user_id']}")
            return jsonify({
                'success': False,
                'error': 'You can only unshare your own recipes'
            }), 403
        
        # Check if it's actually shared
        if not recipe.get('is_community_shared', False):
            logger.info(f"ℹ️ Recipe {recipe_id} is not currently shared")
            return jsonify({
                'success': True,
                'message': 'Recipe was not shared in the community'
            })
        
        # Unshare the recipe (set is_community_shared to FALSE)
        cursor.execute("""
            UPDATE recipes 
            SET is_community_shared = FALSE,
                community_title = NULL,
                community_description = NULL,
                shared_at = NULL
            WHERE id = %s AND user_id = %s
        """, (recipe_id, user_id))
        
        # Check if the update was successful
        if cursor.rowcount == 0:
            logger.warning(f"❌ Failed to unshare recipe {recipe_id} for user {user_id}")
            return jsonify({
                'success': False,
                'error': 'Failed to unshare recipe - recipe may not belong to you'
            }), 400
        
        conn.commit()
        
        logger.info(f"✅ User {user_id} unshared recipe {recipe_id}: {recipe['title']}")
        
        return jsonify({
            'success': True,
            'message': f'Recipe "{recipe["title"]}" has been removed from community sharing',
            'recipe_id': recipe_id
        })
        
    except Exception as e:
        logger.error(f"❌ Delete community recipe error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if 'conn' in locals():
            conn.close()

# ===================================
# GROCERY LIST MANAGEMENT API
# ===================================

@app.route('/api/grocery-lists', methods=['GET'])
def get_user_grocery_lists():
    """Get user's saved grocery lists (owned + shared)"""
    try:
        # Check authentication
        user_id, error_response, status_code = check_authentication()
        if error_response:
            return error_response, status_code
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Create table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS grocery_lists (
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                list_name TEXT NOT NULL,
                list_data JSONB NOT NULL,
                recipe_ids INTEGER[] DEFAULT '{}',
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Get user's owned grocery lists
        cursor.execute("""
            SELECT id, list_name, recipe_ids, created_at, updated_at,
                   (list_data->>'ingredient_count')::int as item_count,
                   false as is_shared
            FROM grocery_lists 
            WHERE user_id = %s 
            ORDER BY updated_at DESC
        """, (user_id,))
        
        owned_lists = cursor.fetchall()
        
        # Get shared grocery lists from collaboration system
        cursor.execute("""
            SELECT DISTINCT c.resource_id, c.permission_level, c.created_at as shared_at,
                   u.name as owner_name,
                   gl.list_name, gl.recipe_ids, gl.created_at, gl.updated_at,
                   (gl.list_data->>'ingredient_count')::int as item_count
            FROM collaborations c
            JOIN users u ON c.invited_by = u.id
            JOIN grocery_lists gl ON c.resource_id = gl.id
            WHERE c.resource_type = 'grocery_list' 
            AND c.user_id = %s 
            AND c.status = 'active'
            ORDER BY c.created_at DESC
        """, (user_id,))
        
        shared_lists_raw = cursor.fetchall()
        
        logger.info(f"🛒 GROCERY COLLABORATION DEBUG: User {user_id} has {len(shared_lists_raw)} shared grocery lists")
        for shared in shared_lists_raw:
            logger.info(f"🛒 GROCERY COLLABORATION DEBUG: Shared list - ID: {shared['resource_id']}, Name: {shared['list_name']}, Owner: {shared['owner_name']}")
        
        # Format shared lists with sharing indicators
        shared_lists = []
        for shared in shared_lists_raw:
            shared_list = dict(shared)
            # CRITICAL: Ensure the ID field matches what frontend expects
            shared_list['id'] = shared['resource_id']  # Map resource_id to id
            shared_list['is_shared'] = True
            shared_list['permission_level'] = shared['permission_level']
            shared_list['shared_by'] = shared['owner_name']
            shared_list['list_name'] = f"📤 {shared['list_name']} (by {shared['owner_name']})"
            shared_lists.append(shared_list)
            logger.info(f"🛒 GROCERY COLLABORATION DEBUG: Formatted shared list - ID: {shared_list['id']}, Name: {shared_list['list_name']}")
        
        # Combine owned and shared lists
        all_lists = list(owned_lists) + shared_lists
        
        logger.info(f"🛒 User {user_id} grocery lists: {len(owned_lists)} owned + {len(shared_lists)} shared = {len(all_lists)} total")
        logger.info(f"🛒 GROCERY LIST DEBUG: Final response will contain {len(all_lists)} lists")
        for i, lst in enumerate(all_lists):
            logger.info(f"🛒 GROCERY LIST DEBUG: List {i+1} - ID: {lst.get('id')}, Name: {lst.get('list_name')}, Shared: {lst.get('is_shared', False)}")
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'grocery_lists': all_lists,
            'count': len(all_lists),
            'owned_count': len(owned_lists),
            'shared_count': len(shared_lists)
        })
        
        lists = cursor.fetchall()
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'grocery_lists': [dict(list_item) for list_item in lists]
        })
        
    except Exception as e:
        logger.error(f"Get grocery lists error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/grocery-lists', methods=['POST'])
def save_grocery_list():
    """Save a grocery list"""
    try:
        # Check authentication
        user_id, error_response, status_code = check_authentication()
        if error_response:
            return error_response, status_code
            
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        list_name = data.get('list_name')
        list_data = data.get('list_data')
        recipe_ids = data.get('recipe_ids', [])
        
        if not list_name or not list_data:
            return jsonify({
                'success': False,
                'error': 'List name and data are required'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Create table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS grocery_lists (
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                list_name TEXT NOT NULL,
                list_data JSONB NOT NULL,
                recipe_ids INTEGER[] DEFAULT '{}',
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Insert the grocery list
        cursor.execute("""
            INSERT INTO grocery_lists (user_id, list_name, list_data, recipe_ids)
            VALUES (%s, %s, %s, %s)
            RETURNING id, created_at
        """, (user_id, list_name, json.dumps(list_data), recipe_ids))
        
        result = cursor.fetchone()
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'list_id': result['id'],
            'message': f'Grocery list "{list_name}" saved successfully',
            'created_at': result['created_at'].isoformat()
        })
        
    except Exception as e:
        logger.error(f"Save grocery list error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/grocery-lists/<int:list_id>', methods=['GET'])
def get_grocery_list_details(list_id):
    """Get detailed grocery list data (owned or shared)"""
    try:
        # Check authentication
        user_id, error_response, status_code = check_authentication()
        if error_response:
            return error_response, status_code
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # First try to get as owner
        cursor.execute("""
            SELECT id, list_name, list_data, recipe_ids, created_at, updated_at,
                   false as is_shared
            FROM grocery_lists 
            WHERE id = %s AND user_id = %s
        """, (list_id, user_id))
        
        grocery_list = cursor.fetchone()
        
        # If not found as owner, check if user has collaboration access
        if not grocery_list:
            cursor.execute("""
                SELECT permission_level FROM collaborations 
                WHERE resource_type = 'grocery_list' AND resource_id = %s 
                AND user_id = %s AND status = 'active'
            """, (list_id, user_id))
            
            collaboration = cursor.fetchone()
            if collaboration:
                # User has access via collaboration, load the list
                cursor.execute("""
                    SELECT id, list_name, list_data, recipe_ids, created_at, updated_at
                    FROM grocery_lists 
                    WHERE id = %s
                """, (list_id,))
                
                grocery_list = cursor.fetchone()
                if grocery_list:
                    grocery_list = dict(grocery_list)
                    grocery_list['is_shared'] = True
                    grocery_list['permission_level'] = collaboration['permission_level']
                    logger.info(f"🛒 User {user_id} accessing shared grocery list {list_id} with {collaboration['permission_level']} permission")
        
        if not grocery_list:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Grocery list not found or access denied'
            }), 404
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'grocery_list': dict(grocery_list)
        })
        
    except Exception as e:
        logger.error(f"Get grocery list details error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/grocery-lists/<int:list_id>', methods=['PUT'])
def update_grocery_list(list_id):
    """Update an existing grocery list (with collaboration support)"""
    try:
        # Check authentication
        user_id, error_response, status_code = check_authentication()
        if error_response:
            return error_response, status_code
            
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        list_name = data.get('list_name')
        list_data = data.get('list_data')
        recipe_ids = data.get('recipe_ids', [])
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Check if user owns the list
        cursor.execute("""
            SELECT id FROM grocery_lists 
            WHERE id = %s AND user_id = %s
        """, (list_id, user_id))
        
        owned_list = cursor.fetchone()
        can_edit = bool(owned_list)
        
        # If not owner, check collaboration access
        if not can_edit:
            cursor.execute("""
                SELECT permission_level FROM collaborations 
                WHERE resource_type = 'grocery_list' AND resource_id = %s 
                AND user_id = %s AND status = 'active'
            """, (list_id, user_id))
            
            collaboration = cursor.fetchone()
            if collaboration and collaboration['permission_level'] == 'editor':
                can_edit = True
                logger.info(f"🛒 User {user_id} editing shared grocery list {list_id} with editor permission")
        
        if not can_edit:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Grocery list not found or insufficient permissions'
            }), 403
        
        # Update the grocery list
        cursor.execute("""
            UPDATE grocery_lists 
            SET list_name = COALESCE(%s, list_name),
                list_data = COALESCE(%s, list_data),
                recipe_ids = COALESCE(%s, recipe_ids),
                updated_at = NOW()
            WHERE id = %s
            RETURNING id, updated_at
        """, (list_name, json.dumps(list_data) if list_data else None, recipe_ids, list_id))
        
        result = cursor.fetchone()
        
        if not result:
            return jsonify({
                'success': False,
                'error': 'Grocery list not found or unauthorized'
            }), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Grocery list updated successfully',
            'updated_at': result['updated_at'].isoformat()
        })
        
    except Exception as e:
        logger.error(f"Update grocery list error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/grocery-lists/<int:list_id>', methods=['DELETE'])
def delete_grocery_list(list_id):
    """Delete a grocery list"""
    try:
        # Check authentication
        user_id, error_response, status_code = check_authentication()
        if error_response:
            return error_response, status_code
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM grocery_lists 
            WHERE id = %s AND user_id = %s
        """, (list_id, user_id))
        
        if cursor.rowcount == 0:
            return jsonify({
                'success': False,
                'error': 'Grocery list not found or unauthorized'
            }), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Grocery list deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Delete grocery list error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ===================================
# 🧠 SPACY GROCERY COMBINING ENHANCEMENT
# ===================================

@app.route('/api/grocery/enhance-combining', methods=['POST'])
def enhance_combining():
    """
    Enhance JavaScript combining with spaCy intelligence (Tier 2)
    Called in background after JavaScript combining completes
    """
    if not SPACY_NORMALIZER_AVAILABLE:
        # Gracefully fail if spaCy not available
        return jsonify({
            'enhanced_items': request.json.get('items', []),
            'improvements': 0,
            'details': [],
            'status': 'spacy_unavailable'
        })
    
    try:
        data = request.get_json()
        items = data.get('items', [])
        
        if not items:
            return jsonify({
                'success': False,
                'error': 'No items provided'
            }), 400
        
        logger.info(f"🧠 Enhancing {len(items)} items with spaCy...")
        
        # Get normalizer and enhance
        normalizer = get_normalizer()
        result = normalizer.enhance_combining(items)
        
        return jsonify({
            'success': True,
            **result
        })
        
    except Exception as e:
        logger.error(f"❌ spaCy enhancement error: {e}")
        # Return original items on error (graceful fallback)
        return jsonify({
            'enhanced_items': request.json.get('items', []),
            'improvements': 0,
            'details': [],
            'error': str(e)
        })

@app.route('/api/grocery/merge-lists', methods=['POST'])
def merge_grocery_lists():
    """
    Intelligently merge multiple grocery lists using spaCy
    """
    if not SPACY_NORMALIZER_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'spaCy normalizer not available'
        }), 503
    
    try:
        # Check authentication
        user_id, error_response, status_code = check_authentication()
        if error_response:
            return error_response, status_code
        
        data = request.get_json()
        list_ids = data.get('list_ids', [])
        
        if not list_ids or len(list_ids) < 2:
            return jsonify({
                'success': False,
                'error': 'Please provide at least 2 list IDs to merge'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Fetch all lists
        lists = []
        for list_id in list_ids:
            cursor.execute("""
                SELECT id, list_name, list_data 
                FROM grocery_lists 
                WHERE id = %s AND user_id = %s
            """, (list_id, user_id))
            
            grocery_list = cursor.fetchone()
            if grocery_list:
                # Extract items from list_data
                list_data = grocery_list['list_data']
                if isinstance(list_data, list):
                    items = list_data
                else:
                    # Handle structured format
                    items = []
                    if isinstance(list_data, dict):
                        for section, section_items in list_data.items():
                            if isinstance(section_items, list):
                                items.extend(section_items)
                
                lists.append(items)
        
        conn.close()
        
        if not lists:
            return jsonify({
                'success': False,
                'error': 'No valid lists found'
            }), 404
        
        logger.info(f"🔄 Merging {len(lists)} lists with spaCy...")
        
        # Use spaCy to merge
        normalizer = get_normalizer()
        result = normalizer.merge_multiple_lists(lists)
        
        return jsonify({
            'success': True,
            **result
        })
        
    except Exception as e:
        logger.error(f"❌ Merge lists error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/grocery/compare-lists', methods=['POST'])
def compare_grocery_lists():
    """
    Compare two grocery lists semantically using spaCy
    """
    if not SPACY_NORMALIZER_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'spaCy normalizer not available'
        }), 503
    
    try:
        # Check authentication
        user_id, error_response, status_code = check_authentication()
        if error_response:
            return error_response, status_code
        
        data = request.get_json()
        list_a_id = data.get('list_a_id')
        list_b_id = data.get('list_b_id')
        
        if not list_a_id or not list_b_id:
            return jsonify({
                'success': False,
                'error': 'Please provide both list_a_id and list_b_id'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Fetch both lists
        cursor.execute("""
            SELECT id, list_name, list_data 
            FROM grocery_lists 
            WHERE id IN (%s, %s) AND user_id = %s
        """, (list_a_id, list_b_id, user_id))
        
        lists = cursor.fetchall()
        conn.close()
        
        if len(lists) != 2:
            return jsonify({
                'success': False,
                'error': 'Could not find both lists'
            }), 404
        
        # Extract items from both lists
        list_a_items = lists[0]['list_data'] if isinstance(lists[0]['list_data'], list) else []
        list_b_items = lists[1]['list_data'] if isinstance(lists[1]['list_data'], list) else []
        
        logger.info(f"🔍 Comparing lists: {len(list_a_items)} vs {len(list_b_items)} items")
        
        # Use spaCy to compare
        normalizer = get_normalizer()
        result = normalizer.compare_lists(list_a_items, list_b_items)
        
        return jsonify({
            'success': True,
            **result
        })
        
    except Exception as e:
        logger.error(f"❌ Compare lists error: {e}")
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
    """Get user's pantry items"""
    try:
        # Get user from JWT token
        user_id, error_response, status_code = check_authentication()
        if error_response:
            return error_response, status_code
        
        logger.info(f"🔍 Fetching pantry items for user {user_id}")
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            # Create pantry table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pantry_items (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    category VARCHAR(100) DEFAULT 'other',
                    amount VARCHAR(100) DEFAULT 'some',
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            conn.commit()
            logger.info("✅ Pantry table ensured to exist")
            
            # Fetch all pantry items for this user
            cursor.execute("""
                SELECT id, name, category, amount, added_at
                FROM pantry_items 
                WHERE user_id = %s
                ORDER BY added_at DESC
            """, (user_id,))
            
            rows = cursor.fetchall()
            
            items = []
            for row in rows:
                items.append({
                    'id': row['id'],
                    'name': row['name'],
                    'category': row['category'],
                    'amount': row['amount'],
                    'addedAt': row['added_at'].isoformat() if row['added_at'] else None
                })
            
            logger.info(f"✅ Retrieved {len(items)} pantry items for user {user_id}")
            
            return jsonify({
                'success': True,
                'items': items,
                'count': len(items)
            })
            
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logger.error(f"❌ Get pantry items error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'items': []
        }), 500

@app.route('/api/pantry', methods=['POST'])
def add_pantry_item():
    """Add item to user's pantry"""
    try:
        # Get user from JWT token
        user_id, error_response, status_code = check_authentication()
        if error_response:
            return error_response, status_code
            
        data = request.get_json()
        logger.info(f"🔍 Received request data: {data}")
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Support both 'name' and 'ingredient_name' for flexibility
        ingredient_name = data.get('name', data.get('ingredient_name', '')).strip()
        amount = data.get('amount', 'some')
        category = data.get('category', 'other')
        
        logger.info(f"🔍 Parsed values - name: '{ingredient_name}', amount: '{amount}', category: '{category}'")
        
        if not ingredient_name:
            logger.error(f"❌ Missing ingredient name in data: {data}")
            return jsonify({
                'success': False,
                'error': 'Ingredient name required'
            }), 400
        
        logger.info(f"🥫 Adding pantry item for user {user_id}: {ingredient_name} ({category})")
        
        # Connect to database and actually save the item
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            # Create pantry table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pantry_items (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    category VARCHAR(100) DEFAULT 'other',
                    amount VARCHAR(100) DEFAULT 'some',
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            conn.commit()
            logger.info("✅ Pantry table ensured to exist")
            
            # Insert the new pantry item
            cursor.execute("""
                INSERT INTO pantry_items (user_id, name, category, amount)
                VALUES (%s, %s, %s, %s)
                RETURNING id, added_at
            """, (user_id, ingredient_name, category, amount))
            
            result = cursor.fetchone()
            item_id = result['id']
            added_at = result['added_at']
            
            conn.commit()
            logger.info(f"✅ Pantry item saved to database with ID: {item_id}")
            
            item_data = {
                'id': item_id,
                'name': ingredient_name,
                'category': category,
                'amount': amount,
                'addedAt': added_at.isoformat()
            }
            
            return jsonify({
                'success': True,
                'message': f'Added {ingredient_name} to pantry',
                'item': item_data
            })
            
        except Exception as db_error:
            conn.rollback()
            logger.error(f"❌ Database error: {db_error}")
            raise db_error
        finally:
            cursor.close()
            conn.close()
        
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
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Get query parameter for search filtering
        query = request.args.get('query', '').strip()
        logger.info(f"📝 Search query parameter: '{query}'")
        
        # Get clean ingredients with simplified query
        if query:
            # Use simple string formatting temporarily to avoid parameterization issues
            sql_query = f"""
                SELECT DISTINCT canonical_name, category
                FROM canonical_ingredients 
                WHERE canonical_name ILIKE '%{query}%'
                AND canonical_name NOT LIKE '%cup%'
                AND canonical_name NOT LIKE '%teaspoon%'
                AND canonical_name NOT LIKE '%tablespoon%'
                AND LENGTH(canonical_name) < 50
                ORDER BY canonical_name
                LIMIT 200
            """
            logger.info(f"🔍 Executing simple search query for: '{query}'")
            cursor.execute(sql_query)
        else:
            sql_query = """
                SELECT DISTINCT canonical_name, category
                FROM canonical_ingredients 
                WHERE canonical_name NOT LIKE '%cup%'
                AND canonical_name NOT LIKE '%teaspoon%'
                AND canonical_name NOT LIKE '%tablespoon%'
                AND LENGTH(canonical_name) < 50
                ORDER BY canonical_name
                LIMIT 200
            """
            logger.info("� Executing simple query without search filter")
            cursor.execute(sql_query)
        
        logger.info("📊 Fetching query results...")
        rows = cursor.fetchall()
        logger.info(f"📊 Retrieved {len(rows)} rows from database")
        
        ingredients = []
        for row in rows:
            try:
                # Use dictionary access since we have RealDictCursor
                ingredients.append({
                    'name': row['canonical_name'],
                    'category': row['category'] or 'other'
                })
            except Exception as row_error:
                logger.error(f"❌ Error processing row: {row}, error: {row_error}")
                continue
        
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
        logger.error("❌ Recipe import system not available")
        return jsonify({
            'success': False,
            'error': 'Recipe import system not available'
        }), 503
    
    # Check authentication
    try:
        user_id, error_response, status_code = check_authentication()
        if error_response:
            logger.error(f"❌ Authentication failed: {error_response}")
            return error_response, status_code
        logger.info(f"✅ Authentication successful for user {user_id}")
    except Exception as e:
        logger.error(f"❌ Authentication error: {e}")
        return jsonify({'success': False, 'error': f'Authentication error: {str(e)}'}), 500
    
    try:
        data = request.get_json()
        logger.info(f"📝 Request data: {data}")
        
        # Validate request
        if not data or 'url' not in data:
            logger.error("❌ Missing URL in request")
            return jsonify({
                'success': False,
                'error': 'Missing url in request body'
            }), 400
        
        url = data['url']
        logger.info(f"🌐 Processing URL: {url}")
        
        # Create import request
        try:
            import_request = ImportRequest(
                source_type='url',
                source_data=url,
                user_id=user_id,
                metadata=data.get('metadata', {})
            )
            logger.info(f"✅ Import request created successfully")
        except Exception as e:
            logger.error(f"❌ Failed to create import request: {e}")
            return jsonify({'success': False, 'error': f'Request creation failed: {str(e)}'}), 500
        
        # Initialize importer and process
        try:
            logger.info("🚀 Initializing UniversalRecipeImporter...")
            importer = UniversalRecipeImporter()
            logger.info("✅ Importer initialized, starting import...")
            
            result = importer.import_recipe(import_request)
            logger.info(f"📊 Import result: success={result.success}, confidence={result.confidence}, errors={result.errors}")
            
        except Exception as e:
            logger.error(f"❌ Import processing failed: {e}")
            import traceback
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")
            return jsonify({'success': False, 'error': f'Import processing failed: {str(e)}'}), 500
        
        # CRITICAL: Refresh search engine cache after successful import
        if result.success and result.recipe_id:
            logger.info(f"🔄 Refreshing search cache for new recipe ID: {result.recipe_id}")
            if search_engine:
                search_engine.refresh_database_cache()
            logger.info(f"✅ Search cache refreshed - new recipe should be visible")
        
        # Return result
        response_data = {
            'success': result.success,
            'recipe_id': result.recipe_id,
            'recipe_data': result.recipe_data,
            'confidence': result.confidence,
            'needs_review': result.needs_review,
            'extraction_method': result.extraction_method,
            'processing_time': result.processing_time,
            'errors': result.errors,
            'warnings': result.warnings
        }
        
        # 🔍 DEBUG: Log what we're sending to mobile
        logger.info(f"📤 Sending response to mobile:")
        logger.info(f"   Success: {response_data['success']}")
        logger.info(f"   Recipe ID: {response_data['recipe_id']}")
        if response_data['recipe_data']:
            logger.info(f"   Recipe title: {response_data['recipe_data'].get('title', 'MISSING')}")
            logger.info(f"   Ingredients type: {type(response_data['recipe_data'].get('ingredients'))}")
            logger.info(f"   Ingredients count: {len(response_data['recipe_data'].get('ingredients', []))}")
            logger.info(f"   Instructions type: {type(response_data['recipe_data'].get('instructions'))}")
            logger.info(f"   Instructions count: {len(response_data['recipe_data'].get('instructions', []))}")
        
        logger.info(f"📤 Sending full response data")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"❌ URL import failed with exception: {e}")
        import traceback
        logger.error(f"❌ Full traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'Import failed: {str(e)}'
        }), 500

@app.route('/api/recipes/import/ocr', methods=['POST'])
def import_recipe_from_ocr():
    """
    Import recipe from scanned images using OCR
    Phase 3: OCR/Camera Import System (Oct 7, 2025)
    """
    logger.info("📸 OCR import request received")
    
    # Check authentication
    user_id, error_response, status_code = check_authentication()
    if error_response:
        logger.error(f"❌ Authentication failed: {error_response}")
        return error_response, status_code
    
    try:
        # Get uploaded images
        images = []
        metadata = {}
        
        # Parse metadata if present
        if 'metadata' in request.form:
            import json
            metadata = json.loads(request.form['metadata'])
            logger.info(f"📋 Metadata: {metadata}")
        
        # Collect all uploaded images
        for key in request.files:
            if key.startswith('image_'):
                image_file = request.files[key]
                image_content = image_file.read()
                images.append(image_content)
                logger.info(f"📷 Received {key}: {len(image_content)} bytes")
        
        if not images:
            return jsonify({
                'success': False,
                'error': 'No images provided'
            }), 400
        
        logger.info(f"📸 Processing {len(images)} images...")
        
        # Step 1: OCR Processing
        try:
            from ocr_processor import get_ocr_processor
            
            ocr_processor = get_ocr_processor()
            if not ocr_processor:
                logger.error("❌ OCR processor not available")
                return jsonify({
                    'success': False,
                    'error': 'OCR service not available. Please contact support.'
                }), 503
        except Exception as e:
            logger.error(f"❌ Failed to import OCR processor: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': f'OCR service initialization failed: {str(e)}'
            }), 503
        
        ocr_result = ocr_processor.process_images(images)
        
        if not ocr_result['success']:
            logger.error(f"❌ OCR processing failed: {ocr_result.get('error')}")
            return jsonify({
                'success': False,
                'error': ocr_result.get('error', 'OCR processing failed')
            }), 500
        
        extracted_text = ocr_result['text']
        ocr_confidence = ocr_result['confidence']
        
        logger.info(f"✅ OCR complete: {len(extracted_text)} characters extracted")
        logger.info(f"🎯 OCR confidence: {ocr_confidence:.2%}")
        logger.info(f"📝 EXTRACTED TEXT (first 1000 chars):\n{extracted_text[:1000]}\n{'='*50}")
        
        # Step 2: Validate extracted text
        validation = ocr_processor.validate_recipe_text(extracted_text)
        
        if not validation['is_likely_recipe']:
            logger.warning("⚠️ Extracted text doesn't look like a recipe")
            return jsonify({
                'success': False,
                'error': 'Could not find recipe content in images. Please ensure images contain recipe text.',
                'extracted_text': extracted_text[:500],  # First 500 chars for debugging
                'validation': validation
            }), 400
        
        # Step 3: Parse recipe from text using Universal Parser
        if not RECIPE_IMPORT_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Recipe import system not available'
            }), 503
        
        # Create import request with OCR text
        import_request = ImportRequest(
            source_type='ocr',
            source_data=extracted_text,
            user_id=user_id,
            metadata={
                **metadata,
                'ocr_confidence': ocr_confidence,
                'pages_processed': ocr_result['pages_processed'],
                'validation': validation
            }
        )
        
        # Initialize importer and process
        importer = UniversalRecipeImporter()
        result = importer.import_recipe(import_request)
        
        if result.success:
            logger.info(f"✅ Recipe imported from OCR: {result.recipe_data.get('title')}")
            
            # Adjust confidence based on OCR and validation
            final_confidence = result.confidence * ocr_confidence * validation['confidence_multiplier']
            
            return jsonify({
                'success': True,
                'recipe': result.recipe_data,
                'recipe_id': result.recipe_id,
                'confidence': final_confidence,
                'extraction_method': 'ocr_scan',
                'ocr_stats': {
                    'ocr_confidence': ocr_confidence,
                    'pages_processed': ocr_result['pages_processed'],
                    'text_length': len(extracted_text),
                    'is_likely_recipe': validation['is_likely_recipe']
                },
                'needs_review': final_confidence < 0.8,
                'processing_time': result.processing_time,
                'warnings': result.warnings
            })
        else:
            logger.error(f"❌ Recipe import failed: {result.errors}")
            return jsonify({
                'success': False,
                'error': 'Failed to parse recipe from extracted text',
                'details': result.errors,
                'extracted_text': extracted_text[:500]  # For debugging
            }), 500
        
    except Exception as e:
        logger.error(f"OCR import error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'OCR import failed: {str(e)}'
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
# VOICE RECIPE RECORDING ENDPOINTS (Phase 1 - Oct 6, 2025)
# ===================================

# Import voice recording systems
try:
    from core_systems.voice_session_processor import VoiceSessionProcessor
    from core_systems.language_matcher import LanguageMatcher
    
    voice_processor = VoiceSessionProcessor(client)
    language_matcher = LanguageMatcher()
    VOICE_RECORDING_AVAILABLE = True
    logger.info("🎤 Voice recording system loaded successfully")
except ImportError as e:
    voice_processor = None
    language_matcher = None
    VOICE_RECORDING_AVAILABLE = False
    logger.warning(f"⚠️ Voice recording system not available: {e}")

@app.route('/api/recipes/voice/languages/search', methods=['GET'])
def search_languages():
    """
    Search available languages for voice recording
    Query parameter: ?q=filipino
    """
    if not VOICE_RECORDING_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Voice recording system not available'
        }), 503
    
    try:
        query = request.args.get('q', '')
        results = language_matcher.search(query)
        
        return jsonify({
            'success': True,
            'languages': results,
            'count': len(results)
        })
    except Exception as e:
        logger.error(f"Language search failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/recipes/voice/session/process', methods=['POST'])
def process_voice_session():
    """
    Process complete voice recording session
    
    Expects multipart/form-data with:
    - segment_0, segment_1, segment_2, ... (audio files)
    - metadata (JSON string with session info)
    """
    if not VOICE_RECORDING_AVAILABLE:
        logger.error("❌ Voice recording system not available")
        return jsonify({
            'success': False,
            'error': 'Voice recording system not available'
        }), 503
    
    # Check authentication
    try:
        user_id, error_response, status_code = check_authentication()
        if error_response:
            logger.error(f"❌ Authentication failed: {error_response}")
            return error_response, status_code
        logger.info(f"✅ Authentication successful for user {user_id}")
    except Exception as e:
        logger.error(f"❌ Authentication error: {e}")
        return jsonify({'success': False, 'error': f'Authentication error: {str(e)}'}), 500
    
    try:
        # Parse metadata
        metadata_str = request.form.get('metadata', '{}')
        metadata = json.loads(metadata_str)
        
        logger.info(f"🎤 Processing voice session for user {user_id}")
        logger.info(f"   Session ID: {metadata.get('session_id')}")
        logger.info(f"   Language: {metadata.get('language_config', {}).get('culture', 'Unknown')}")
        
        # Extract audio segments from request
        segments = []
        segment_index = 0
        while True:
            audio_file = request.files.get(f'segment_{segment_index}')
            if not audio_file:
                break
            
            segment_metadata = metadata.get('segments', [])[segment_index] if segment_index < len(metadata.get('segments', [])) else {}
            
            segments.append({
                'audio_file': audio_file,
                'label': segment_metadata.get('label'),
                'duration_ms': segment_metadata.get('duration_ms', 0)
            })
            
            segment_index += 1
        
        if not segments:
            logger.error("❌ No audio segments found in request")
            return jsonify({
                'success': False,
                'error': 'No audio segments provided'
            }), 400
        
        logger.info(f"   Found {len(segments)} audio segments")
        
        # Process session
        session_data = {
            'session_id': metadata.get('session_id'),
            'segments': segments,
            'total_duration_ms': metadata.get('total_duration_ms', 0),
            'language_config': metadata.get('language_config', {})
        }
        
        result = voice_processor.process_session(session_data, user_id)
        
        if result.get('success'):
            logger.info(f"✅ Session processed successfully")
            logger.info(f"   Transcript length: {len(result.get('combined_transcript', ''))} chars")
            logger.info(f"   Confidence: {result.get('confidence', 0):.2f}")
        else:
            logger.error(f"❌ Session processing failed: {result.get('error')}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Voice session processing failed: {e}")
        import traceback
        logger.error(f"❌ Full traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'Session processing failed: {str(e)}'
        }), 500

@app.route('/api/recipes/voice/generate', methods=['POST'])
def generate_recipe_from_transcript():
    """
    Generate structured recipe from approved transcript
    
    Expects JSON:
    {
        "transcript": "user-approved transcript text",
        "metadata": {
            "recorded_by": "Grandma",
            "culture": "Filipino",
            "language": "tl",
            "duration": 120000,
            "session_id": "uuid"
        }
    }
    """
    if not VOICE_RECORDING_AVAILABLE:
        logger.error("❌ Voice recording system not available")
        return jsonify({
            'success': False,
            'error': 'Voice recording system not available'
        }), 503
    
    # Check authentication
    try:
        user_id, error_response, status_code = check_authentication()
        if error_response:
            logger.error(f"❌ Authentication failed: {error_response}")
            return error_response, status_code
        logger.info(f"✅ Authentication successful for user {user_id}")
    except Exception as e:
        logger.error(f"❌ Authentication error: {e}")
        return jsonify({'success': False, 'error': f'Authentication error: {str(e)}'}), 500
    
    try:
        data = request.get_json()
        
        if not data or 'transcript' not in data:
            logger.error("❌ Missing transcript in request")
            return jsonify({
                'success': False,
                'error': 'Missing transcript in request body'
            }), 400
        
        transcript = data['transcript']
        metadata = data.get('metadata', {})
        
        logger.info(f"🤖 Generating recipe from transcript for user {user_id}")
        logger.info(f"   Transcript length: {len(transcript)} chars")
        logger.info(f"   Culture: {metadata.get('culture', 'Unknown')}")
        
        # Generate recipe
        recipe_data = voice_processor.generate_recipe_from_approved_transcript(
            transcript, 
            metadata
        )
        
        # Add user attribution
        recipe_data['user_id'] = user_id
        recipe_data['transcript'] = transcript
        recipe_data['recorded_by'] = metadata.get('recorded_by', 'Family')
        
        logger.info(f"✅ Recipe generated: {recipe_data.get('title')}")
        logger.info(f"   Ingredients: {len(recipe_data.get('ingredients', []))}")
        logger.info(f"   Instructions: {len(recipe_data.get('instructions', []))}")
        
        # Return in same format as URL import (for consistency)
        response_data = {
            'success': True,
            'recipe_id': None,  # Not saved yet
            'recipe_data': recipe_data,
            'confidence': 0.85,
            'needs_review': False,  # User already reviewed transcript
            'extraction_method': 'voice_session',
            'processing_time': metadata.get('duration', 0) / 1000.0
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"❌ Recipe generation failed: {e}")
        import traceback
        logger.error(f"❌ Full traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'Recipe generation failed: {str(e)}'
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
        
        # Debug: List auth routes
        auth_route_list = []
        for rule in app.url_map.iter_rules():
            if rule.rule.startswith('/api/auth/'):
                auth_route_list.append(rule.rule)
        logger.info(f"🔧 Registered auth routes: {auth_route_list}")
        
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
                # Skip default template creation during manual curation phase
                logger.info("📋 Default template creation disabled - manual curation mode")
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
            logger.info("🔧 Starting admin system initialization...")
            admin_system = AdminSystem(get_db_connection, auth_system)
            logger.info("🔧 AdminSystem created successfully")
            
            admin_routes = create_admin_routes(admin_system, auth_system, check_authentication)
            logger.info("🔧 Admin routes created successfully")
            
            app.register_blueprint(admin_routes)
            logger.info("🔧 Admin routes blueprint registered successfully")
            
            # Test if the routes are actually available
            with app.test_request_context():
                all_routes = []
                for rule in app.url_map.iter_rules():
                    if '/admin/' in rule.rule:
                        all_routes.append(rule.rule)
                logger.info(f"🔧 Registered admin routes: {all_routes}")
            
            logger.info("🔧 Admin system initialized and routes registered")
            
            # Add a simple test endpoint to verify admin routes are working
            @app.route('/api/admin/test', methods=['GET'])
            def admin_test():
                from datetime import datetime
                return jsonify({
                    'success': True,
                    'message': 'Admin routes are working!',
                    'timestamp': datetime.now().isoformat()
                })
            
            # Add a test endpoint WITHOUT authentication to verify blueprint is working
            @app.route('/api/admin/test-no-auth', methods=['GET'])
            def admin_test_no_auth():
                from datetime import datetime
                return jsonify({
                    'success': True,
                    'message': 'Admin blueprint is working! (no auth required)',
                    'timestamp': datetime.now().isoformat(),
                    'routes_registered': True
                })
            
            # Add a test endpoint that goes through admin authentication
            @app.route('/api/admin/auth-test', methods=['GET'])
            def admin_auth_test():
                try:
                    # Check JWT authentication first
                    auth_header = request.headers.get('Authorization')
                    logger.info(f"🔧 Auth test - Header: {auth_header}")
                    
                    if not auth_header or not auth_header.startswith('Bearer '):
                        return jsonify({'error': 'No valid authentication token', 'step': 'header_check'}), 401
                    
                    token = auth_header.split(' ')[1]
                    logger.info(f"🔑 Auth test - Token: {token[:20]}...")
                    
                    # Try to validate token
                    user_data = auth_system.validate_token(token)
                    logger.info(f"🔑 Auth test - Token validation: {user_data}")
                    
                    if not user_data['valid']:
                        return jsonify({'error': 'Invalid authentication token', 'step': 'token_validation'}), 401
                    
                    # Check if user is admin
                    user_email = user_data.get('email')
                    logger.info(f"👤 Auth test - User email: {user_email}")
                    
                    is_admin = admin_system.is_admin_user(user_email)
                    logger.info(f"🔧 Auth test - Is admin: {is_admin}")
                    
                    return jsonify({
                        'success': True,
                        'user_email': user_email,
                        'is_admin': is_admin,
                        'token_valid': user_data['valid'],
                        'message': 'Authentication test complete'
                    })
                    
                except Exception as e:
                    logger.error(f"❌ Auth test error: {e}")
                    return jsonify({'error': str(e), 'step': 'exception'}), 500
            
            # Add a test endpoint that uses the admin_required decorator
            @app.route('/api/admin/test-with-auth', methods=['GET'])
            def admin_test_with_auth():
                try:
                    # This will simulate the admin_required decorator manually
                    auth_header = request.headers.get('Authorization')
                    if not auth_header or not auth_header.startswith('Bearer '):
                        return jsonify({'error': 'No valid authentication token'}), 401
                    
                    token = auth_header.split(' ')[1]
                    user_data = auth_system.validate_token(token)
                    
                    if not user_data['valid']:
                        return jsonify({'error': 'Invalid authentication token'}), 401
                    
                    user_email = user_data.get('email')
                    if not admin_system.is_admin_user(user_email):
                        return jsonify({'error': 'Admin access required'}), 403
                    
                    return jsonify({
                        'success': True,
                        'message': 'Admin test with authentication successful!',
                        'admin_email': user_email
                    })
                    
                except Exception as e:
                    logger.error(f"❌ Admin test with auth error: {e}")
                    return jsonify({'error': str(e)}), 500
                
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

    # ===================================================================
    # FRIENDS & COLLABORATION API ENDPOINTS
    # ===================================================================
    
    def get_authenticated_user():
        """Extract and validate user from JWT token"""
        try:
            import jwt
            import json
            import base64
            import hashlib
            
            # Get Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return None
            
            token = auth_header.split(' ')[1]
            
            # Use same JWT secret generation as AuthenticationSystem
            jwt_secret = os.getenv('JWT_SECRET_KEY')
            if not jwt_secret:
                database_url = os.getenv('DATABASE_URL', '')
                if database_url:
                    jwt_secret = hashlib.sha256(database_url.encode()).hexdigest()
                else:
                    jwt_secret = 'dev-secret-key-for-local-testing-only'
            
            # Manual decode without strict subject validation
            payload_part = token.split('.')[1]
            padding_needed = len(payload_part) % 4
            if padding_needed:
                payload_part += '=' * (4 - padding_needed)
                
            payload_bytes = base64.urlsafe_b64decode(payload_part)
            payload = json.loads(payload_bytes)
            
            user_id = payload.get('sub')
            if isinstance(user_id, str) and user_id.isdigit():
                user_id = int(user_id)
            
            # Verify signature
            jwt.decode(token, jwt_secret, algorithms=['HS256'], options={"verify_sub": False})
            
            # Get user from database
            user = auth_system.get_user_by_id(user_id)
            return user
            
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return None

    @app.route('/api/friends/list', methods=['GET'])
    def get_friends_list():
        """Get user's friends list with status and metadata"""
        try:
            current_user = get_authenticated_user()
            if not current_user:
                return jsonify({'error': 'Authentication required'}), 401
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get all accepted friendships for the current user
            cursor.execute("""
                SELECT 
                    u.id, u.name, u.email,
                    f.created_at as friend_since,
                    f.updated_at as last_activity
                FROM friendships f
                JOIN users u ON f.friend_id = u.id
                WHERE f.user_id = %s AND f.status = 'accepted'
                ORDER BY u.name
            """, (current_user['id'],))
            
            friends = []
            for row in cursor.fetchall():
                # Get initials from name
                name_parts = row['name'].split()
                initials = ''.join([part[0].upper() for part in name_parts[:2]])
                
                # Calculate shared lists (placeholder for now)
                shared_lists = 0  # TODO: Implement shared lists count
                
                # Format last active
                from datetime import datetime
                last_activity = row['last_activity'] or row['friend_since']
                now = datetime.now()
                time_diff = now - last_activity.replace(tzinfo=None)
                
                if time_diff.days > 0:
                    last_active = f"{time_diff.days}d ago"
                elif time_diff.seconds > 3600:
                    hours = time_diff.seconds // 3600
                    last_active = f"{hours}h ago"
                else:
                    minutes = max(1, time_diff.seconds // 60)
                    last_active = f"{minutes}m ago"
                
                friends.append({
                    'id': row['id'],
                    'name': row['name'],
                    'email': row['email'],
                    'initials': initials,
                    'status': 'Active',  # TODO: Implement real status
                    'sharedLists': shared_lists,
                    'lastActive': last_active
                })
            
            cursor.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'friends': friends,
                'count': len(friends)
            })
            
        except Exception as e:
            logger.error(f"❌ Get friends list error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/friends/requests', methods=['GET'])
    def get_friend_requests():
        """Get incoming and outgoing friend requests"""
        try:
            current_user = get_authenticated_user()
            if not current_user:
                return jsonify({'error': 'Authentication required'}), 401
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get incoming requests
            cursor.execute("""
                SELECT 
                    fr.id, fr.message, fr.created_at,
                    u.id as user_id, u.name, u.email
                FROM friend_requests fr
                JOIN users u ON fr.requester_id = u.id
                WHERE fr.recipient_id = %s AND fr.status = 'pending'
                ORDER BY fr.created_at DESC
            """, (current_user['id'],))
            
            incoming_requests = []
            for row in cursor.fetchall():
                name_parts = row['name'].split()
                initials = ''.join([part[0].upper() for part in name_parts[:2]])
                
                # Format time
                from datetime import datetime
                created_at = row['created_at']
                now = datetime.now()
                time_diff = now - created_at.replace(tzinfo=None)
                
                if time_diff.days > 0:
                    sent_at = f"{time_diff.days} days ago"
                elif time_diff.seconds > 3600:
                    hours = time_diff.seconds // 3600
                    sent_at = f"{hours} hours ago"
                else:
                    minutes = max(1, time_diff.seconds // 60)
                    sent_at = f"{minutes} minutes ago"
                
                incoming_requests.append({
                    'id': row['id'],
                    'name': row['name'],
                    'email': row['email'],
                    'initials': initials,
                    'type': 'incoming',
                    'message': row['message'] or 'Would like to connect!',
                    'sentAt': sent_at
                })
            
            # Get outgoing requests
            cursor.execute("""
                SELECT 
                    fr.id, fr.message, fr.created_at,
                    u.id as user_id, u.name, u.email
                FROM friend_requests fr
                JOIN users u ON fr.recipient_id = u.id
                WHERE fr.requester_id = %s AND fr.status = 'pending'
                ORDER BY fr.created_at DESC
            """, (current_user['id'],))
            
            outgoing_requests = []
            for row in cursor.fetchall():
                name_parts = row['name'].split()
                initials = ''.join([part[0].upper() for part in name_parts[:2]])
                
                # Format time
                from datetime import datetime
                created_at = row['created_at']
                now = datetime.now()
                time_diff = now - created_at.replace(tzinfo=None)
                
                if time_diff.days > 0:
                    sent_at = f"{time_diff.days} days ago"
                elif time_diff.seconds > 3600:
                    hours = time_diff.seconds // 3600
                    sent_at = f"{hours} hours ago"
                else:
                    minutes = max(1, time_diff.seconds // 60)
                    sent_at = f"{minutes} minutes ago"
                
                outgoing_requests.append({
                    'id': row['id'],
                    'name': row['name'],
                    'email': row['email'],
                    'initials': initials,
                    'type': 'outgoing',
                    'message': row['message'] or 'Sent a friend request',
                    'sentAt': sent_at
                })
            
            cursor.close()
            conn.close()
            
            # Combine all requests
            all_requests = incoming_requests + outgoing_requests
            
            return jsonify({
                'success': True,
                'requests': all_requests,
                'incoming_count': len(incoming_requests),
                'outgoing_count': len(outgoing_requests)
            })
            
        except Exception as e:
            logger.error(f"❌ Get friend requests error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/friends/request', methods=['POST'])
    def send_friend_request():
        """Send a friend request by email"""
        try:
            current_user = get_authenticated_user()
            if not current_user:
                return jsonify({'error': 'Authentication required'}), 401
                
            data = request.get_json()
            recipient_email = data.get('email', '').strip().lower()
            message = data.get('message', '').strip()
            
            if not recipient_email:
                return jsonify({'error': 'Email address is required'}), 400
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if recipient exists
            cursor.execute("SELECT id, name FROM users WHERE LOWER(email) = %s", (recipient_email,))
            recipient = cursor.fetchone()
            
            if not recipient:
                return jsonify({'error': 'User not found'}), 404
            
            if recipient['id'] == current_user['id']:
                return jsonify({'error': 'Cannot send friend request to yourself'}), 400
            
            # Check if already friends
            cursor.execute("""
                SELECT status FROM friendships 
                WHERE user_id = %s AND friend_id = %s
            """, (current_user['id'], recipient['id']))
            
            existing_friendship = cursor.fetchone()
            if existing_friendship:
                if existing_friendship['status'] == 'accepted':
                    return jsonify({'error': 'Already friends'}), 400
                elif existing_friendship['status'] == 'blocked':
                    return jsonify({'error': 'Cannot send request'}), 400
            
            # Check if request already exists
            cursor.execute("""
                SELECT status FROM friend_requests 
                WHERE requester_id = %s AND recipient_id = %s
            """, (current_user['id'], recipient['id']))
            
            existing_request = cursor.fetchone()
            if existing_request and existing_request['status'] == 'pending':
                return jsonify({'error': 'Friend request already sent'}), 400
            
            # Create friend request
            cursor.execute("""
                INSERT INTO friend_requests (requester_id, recipient_id, message, status)
                VALUES (%s, %s, %s, 'pending')
                RETURNING id
            """, (current_user['id'], recipient['id'], message))
            
            request_id = cursor.fetchone()['id']
            conn.commit()
            
            cursor.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': f'Friend request sent to {recipient["name"]}',
                'request_id': request_id
            })
            
        except Exception as e:
            logger.error(f"❌ Send friend request error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/friends/request/<int:request_id>/accept', methods=['POST'])
    def accept_friend_request(request_id):
        """Accept a friend request"""
        try:
            current_user = get_authenticated_user()
            if not current_user:
                return jsonify({'error': 'Authentication required'}), 401
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Verify the request exists and is for this user
            cursor.execute("""
                SELECT requester_id, recipient_id 
                FROM friend_requests 
                WHERE id = %s AND recipient_id = %s AND status = 'pending'
            """, (request_id, current_user['id']))
            
            request_data = cursor.fetchone()
            if not request_data:
                return jsonify({'error': 'Friend request not found'}), 404
            
            requester_id = request_data['requester_id']
            
            # Update request status
            cursor.execute("""
                UPDATE friend_requests 
                SET status = 'accepted', responded_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (request_id,))
            
            # Create mutual friendship using the function
            cursor.execute("SELECT create_mutual_friendship(%s, %s)", (current_user['id'], requester_id))
            
            conn.commit()
            
            # Get friend info
            cursor.execute("SELECT name FROM users WHERE id = %s", (requester_id,))
            friend_name = cursor.fetchone()['name']
            
            cursor.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': f'You are now friends with {friend_name}!'
            })
            
        except Exception as e:
            logger.error(f"❌ Accept friend request error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/friends/request/<int:request_id>/decline', methods=['POST'])
    def decline_friend_request(request_id):
        """Decline a friend request"""
        try:
            current_user = get_authenticated_user()
            if not current_user:
                return jsonify({'error': 'Authentication required'}), 401
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Verify and update request
            cursor.execute("""
                UPDATE friend_requests 
                SET status = 'declined', responded_at = CURRENT_TIMESTAMP
                WHERE id = %s AND recipient_id = %s AND status = 'pending'
                RETURNING requester_id
            """, (request_id, current_user['id']))
            
            result = cursor.fetchone()
            if not result:
                return jsonify({'error': 'Friend request not found'}), 404
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': 'Friend request declined'
            })
            
        except Exception as e:
            logger.error(f"❌ Decline friend request error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/friends/<int:friend_id>/remove', methods=['DELETE'])
    def remove_friend(friend_id):
        """Remove a friend"""
        try:
            current_user = get_authenticated_user()
            if not current_user:
                return jsonify({'error': 'Authentication required'}), 401
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get friend name first
            cursor.execute("SELECT name FROM users WHERE id = %s", (friend_id,))
            friend = cursor.fetchone()
            
            if not friend:
                return jsonify({'error': 'User not found'}), 404
            
            # Remove both directions of friendship
            cursor.execute("""
                DELETE FROM friendships 
                WHERE (user_id = %s AND friend_id = %s) OR (user_id = %s AND friend_id = %s)
            """, (current_user['id'], friend_id, friend_id, current_user['id']))
            
            if cursor.rowcount == 0:
                return jsonify({'error': 'Friendship not found'}), 404
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': f'{friend["name"]} has been removed from your friends'
            })
            
        except Exception as e:
            logger.error(f"❌ Remove friend error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/households/list', methods=['GET'])
    def get_households_list():
        """Get user's households"""
        try:
            current_user = get_authenticated_user()
            if not current_user:
                return jsonify({'error': 'Authentication required'}), 401
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    h.id, h.name, h.description, h.created_at,
                    hm.role,
                    COUNT(hm2.id) as member_count
                FROM households h
                JOIN household_members hm ON h.id = hm.household_id
                LEFT JOIN household_members hm2 ON h.id = hm2.household_id
                WHERE hm.user_id = %s AND h.is_active = TRUE
                GROUP BY h.id, h.name, h.description, h.created_at, hm.role
                ORDER BY h.name
            """, (current_user['id'],))
            
            households = []
            for row in cursor.fetchall():
                # Format created date
                from datetime import datetime
                created_at = row['created_at']
                created_date = created_at.strftime('%b %Y')
                
                households.append({
                    'id': row['id'],
                    'name': row['name'],
                    'role': row['role'],
                    'members': row['member_count'],
                    'sharedLists': 0,  # TODO: Implement shared lists count
                    'sharedPlans': 0,  # TODO: Implement shared plans count
                    'createdAt': created_date
                })
            
            cursor.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'households': households,
                'count': len(households)
            })
            
        except Exception as e:
            logger.error(f"❌ Get households error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/households/create', methods=['POST'])
    def create_household():
        """Create a new household"""
        try:
            current_user = get_authenticated_user()
            if not current_user:
                return jsonify({'error': 'Authentication required'}), 401
                
            data = request.get_json()
            name = data.get('name', '').strip()
            description = data.get('description', '').strip()
            
            if not name:
                return jsonify({'error': 'Household name is required'}), 400
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Create household
            cursor.execute("""
                INSERT INTO households (name, description, owner_user_id)
                VALUES (%s, %s, %s)
                RETURNING id, invite_code
            """, (name, description, current_user['id']))
            
            household = cursor.fetchone()
            household_id = household['id']
            invite_code = household['invite_code']
            
            # Add creator as owner
            cursor.execute("""
                INSERT INTO household_members (household_id, user_id, role)
                VALUES (%s, %s, 'owner')
            """, (household_id, current_user['id']))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': f'Household "{name}" created successfully!',
                'household': {
                    'id': household_id,
                    'name': name,
                    'invite_code': invite_code
                }
            })
            
        except Exception as e:
            logger.error(f"❌ Create household error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/households/<int:household_id>/delete', methods=['DELETE'])
    def delete_household(household_id):
        """Delete a household"""
        try:
            current_user = get_authenticated_user()
            if not current_user:
                return jsonify({'error': 'Authentication required'}), 401
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if user is owner of the household
            cursor.execute("""
                SELECT name FROM households 
                WHERE id = %s AND owner_user_id = %s
            """, (household_id, current_user['id']))
            
            household = cursor.fetchone()
            if not household:
                return jsonify({'error': 'Household not found or you are not the owner'}), 404
            
            # Delete household (cascade will handle members)
            cursor.execute("DELETE FROM households WHERE id = %s", (household_id,))
            
            if cursor.rowcount == 0:
                return jsonify({'error': 'Household not found'}), 404
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': f'Household "{household["name"]}" has been deleted'
            })
            
        except Exception as e:
            logger.error(f"❌ Delete household error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/households/<int:household_id>/members/add', methods=['POST'])
    def add_household_member(household_id):
        """Add a member to household"""
        try:
            current_user = get_authenticated_user()
            if not current_user:
                return jsonify({'error': 'Authentication required'}), 401
            
            data = request.get_json()
            new_member_id = data.get('user_id')
            
            if not new_member_id:
                return jsonify({'error': 'User ID is required'}), 400
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if current user has permission (owner or admin)
            cursor.execute("""
                SELECT hm.role, h.name as household_name
                FROM household_members hm
                JOIN households h ON hm.household_id = h.id
                WHERE hm.household_id = %s AND hm.user_id = %s
            """, (household_id, current_user['id']))
            
            user_role = cursor.fetchone()
            if not user_role or user_role['role'] not in ['owner', 'admin']:
                return jsonify({'error': 'Permission denied'}), 403
            
            # Check if users are friends
            cursor.execute("""
                SELECT 1 FROM friendships 
                WHERE user_id = %s AND friend_id = %s AND status = 'accepted'
            """, (current_user['id'], new_member_id))
            
            if not cursor.fetchone():
                return jsonify({'error': 'Can only add friends to household'}), 400
            
            # Check if user is already a member
            cursor.execute("""
                SELECT 1 FROM household_members 
                WHERE household_id = %s AND user_id = %s
            """, (household_id, new_member_id))
            
            if cursor.fetchone():
                return jsonify({'error': 'User is already a member of this household'}), 400
            
            # Add member
            cursor.execute("""
                INSERT INTO household_members (household_id, user_id, role, invited_by)
                VALUES (%s, %s, 'member', %s)
            """, (household_id, new_member_id, current_user['id']))
            
            # Get member name
            cursor.execute("SELECT name FROM users WHERE id = %s", (new_member_id,))
            member_name = cursor.fetchone()['name']
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': f'{member_name} has been added to {user_role["household_name"]}'
            })
            
        except Exception as e:
            logger.error(f"❌ Add household member error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/households/<int:household_id>/members/<int:member_id>/remove', methods=['DELETE'])
    def remove_household_member(household_id, member_id):
        """Remove a member from household"""
        try:
            current_user = get_authenticated_user()
            if not current_user:
                return jsonify({'error': 'Authentication required'}), 401
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if current user has permission (owner or admin)
            cursor.execute("""
                SELECT hm.role, h.name as household_name
                FROM household_members hm
                JOIN households h ON hm.household_id = h.id
                WHERE hm.household_id = %s AND hm.user_id = %s
            """, (household_id, current_user['id']))
            
            user_role = cursor.fetchone()
            if not user_role or user_role['role'] not in ['owner', 'admin']:
                return jsonify({'error': 'Permission denied'}), 403
            
            # Get member info before removing
            cursor.execute("""
                SELECT u.name, hm.role 
                FROM household_members hm
                JOIN users u ON hm.user_id = u.id
                WHERE hm.household_id = %s AND hm.user_id = %s
            """, (household_id, member_id))
            
            member_info = cursor.fetchone()
            if not member_info:
                return jsonify({'error': 'Member not found in household'}), 404
            
            # Prevent removing the owner
            if member_info['role'] == 'owner':
                return jsonify({'error': 'Cannot remove the household owner'}), 400
            
            # Remove member
            cursor.execute("""
                DELETE FROM household_members 
                WHERE household_id = %s AND user_id = %s
            """, (household_id, member_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': f'{member_info["name"]} has been removed from the household'
            })
            
        except Exception as e:
            logger.error(f"❌ Remove household member error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/households/<int:household_id>/members', methods=['GET'])
    def get_household_members(household_id):
        """Get household members"""
        try:
            current_user = get_authenticated_user()
            if not current_user:
                return jsonify({'error': 'Authentication required'}), 401
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if current user is a member
            cursor.execute("""
                SELECT 1 FROM household_members 
                WHERE household_id = %s AND user_id = %s
            """, (household_id, current_user['id']))
            
            if not cursor.fetchone():
                return jsonify({'error': 'Access denied'}), 403
            
            # Get all members
            cursor.execute("""
                SELECT 
                    u.id, u.name, u.email,
                    hm.role, hm.joined_at
                FROM household_members hm
                JOIN users u ON hm.user_id = u.id
                WHERE hm.household_id = %s
                ORDER BY 
                    CASE hm.role 
                        WHEN 'owner' THEN 1 
                        WHEN 'admin' THEN 2 
                        ELSE 3 
                    END,
                    u.name
            """, (household_id,))
            
            members = []
            for row in cursor.fetchall():
                # Get initials
                name_parts = row['name'].split()
                initials = ''.join([part[0].upper() for part in name_parts[:2]])
                
                members.append({
                    'id': row['id'],
                    'name': row['name'],
                    'email': row['email'],
                    'initials': initials,
                    'role': row['role'],
                    'joined_at': row['joined_at'].strftime('%b %Y') if row['joined_at'] else 'Unknown'
                })
            
            cursor.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'members': members
            })
            
        except Exception as e:
            logger.error(f"❌ Get household members error: {e}")
            return jsonify({'error': str(e)}), 500

    # ==================================================
    # 🤝 COLLABORATION SYSTEM ENDPOINTS
    # ==================================================
    
    @app.route('/api/collaboration/invite', methods=['POST'])
    def invite_to_collaborate():
        """Invite household members to collaborate on a meal plan or grocery list"""
        try:
            current_user = get_authenticated_user()
            if not current_user:
                return jsonify({'error': 'Authentication required'}), 401
            
            data = request.get_json()
            resource_type = data.get('resource_type')  # 'meal_plan' or 'grocery_list'
            resource_id = data.get('resource_id')
            household_id = data.get('household_id')
            permission_level = data.get('permission_level', 'editor')  # 'editor' or 'viewer'
            
            if not all([resource_type, resource_id, household_id]):
                return jsonify({'error': 'Missing required fields'}), 400
            
            if resource_type not in ['meal_plan', 'grocery_list']:
                return jsonify({'error': 'Invalid resource type'}), 400
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            logger.info(f"🎯 COLLABORATION DEBUG: Starting invite process")
            logger.info(f"🎯 COLLABORATION DEBUG: resource_type={resource_type}, resource_id={resource_id}, household_id={household_id}")
            
            # For now, simulate success since we don't have proper meal_plans/grocery_lists tables
            # Get household info for response
            try:
                cursor.execute("""
                    SELECT name FROM households 
                    WHERE id = %s
                """, (household_id,))
                
                household = cursor.fetchone()
                logger.info(f"🎯 COLLABORATION DEBUG: Household query result: {household}")
                
                if not household:
                    return jsonify({'error': 'Household not found'}), 404
                
                # Get household members (except the current user)
                cursor.execute("""
                    SELECT u.id, u.name, u.email
                    FROM household_members hm
                    JOIN users u ON hm.user_id = u.id
                    WHERE hm.household_id = %s AND u.id != %s
                """, (household_id, current_user['id']))
                
                members = cursor.fetchall()
                logger.info(f"🎯 COLLABORATION DEBUG: Found {len(members)} members to invite")
                
            except Exception as query_error:
                logger.error(f"❌ COLLABORATION DEBUG: Query error: {query_error}")
                cursor.close()
                conn.close()
                return jsonify({'error': f'Database query error: {str(query_error)}'}), 500
            
            # Create collaboration records for each member
            invitations_created = 0
            try:
                for member in members:
                    logger.info(f"🎯 COLLABORATION DEBUG: Processing member: {member['name']} (ID: {member['id']})")
                    
                    # Check if collaboration already exists
                    cursor.execute("""
                        SELECT 1 FROM collaborations 
                        WHERE resource_type = %s AND resource_id = %s AND user_id = %s
                    """, (resource_type, resource_id, member['id']))
                    
                    existing = cursor.fetchone()
                    if not existing:
                        logger.info(f"🎯 COLLABORATION DEBUG: Creating collaboration for {member['name']}")
                        cursor.execute("""
                            INSERT INTO collaborations 
                            (resource_type, resource_id, user_id, invited_by, permission_level, status)
                            VALUES (%s, %s, %s, %s, %s, 'active')
                        """, (resource_type, resource_id, member['id'], current_user['id'], permission_level))
                        invitations_created += 1
                    else:
                        logger.info(f"🎯 COLLABORATION DEBUG: Collaboration already exists for {member['name']}")
                
                conn.commit()
                logger.info(f"🎯 COLLABORATION DEBUG: Successfully created {invitations_created} invitations")
                
            except Exception as insert_error:
                logger.error(f"❌ COLLABORATION DEBUG: Insert error: {insert_error}")
                conn.rollback()
                cursor.close()
                conn.close()
                return jsonify({'error': f'Failed to create collaborations: {str(insert_error)}'}), 500
            cursor.close()
            conn.close()
            
            resource_name = f"{resource_type.replace('_', ' ').title()} #{resource_id}"
            
            return jsonify({
                'success': True,
                'message': f'Invited household members to collaborate on "{resource_name}"',
                'invitations_created': invitations_created,
                'total_members': len(members),
                'household_name': household['name']
            })
            
        except Exception as e:
            logger.error(f"❌ Collaboration invite error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/collaboration/my-shared', methods=['GET'])
    def get_my_shared_resources():
        """Get all meal plans and grocery lists shared with the current user"""
        try:
            current_user = get_authenticated_user()
            if not current_user:
                return jsonify({'error': 'Authentication required'}), 401
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get shared meal plans (simplified for PostgreSQL)
            cursor.execute("""
                SELECT DISTINCT c.resource_id, c.permission_level, c.created_at,
                       u.name as owner_name
                FROM collaborations c
                JOIN users u ON c.invited_by = u.id
                WHERE c.resource_type = 'meal_plan' 
                AND c.user_id = %s 
                AND c.status = 'active'
                ORDER BY c.created_at DESC
            """, (current_user['id'],))
            
            shared_meal_plans_raw = cursor.fetchall()
            
            # Format meal plans for response
            shared_meal_plans = []
            for plan in shared_meal_plans_raw:
                shared_meal_plans.append({
                    'id': plan['resource_id'],
                    'plan_name': f'Shared Meal Plan #{plan["resource_id"]}',
                    'owner_name': plan['owner_name'],
                    'permission_level': plan['permission_level'],
                    'shared_date': plan['created_at']
                })
            
            # Get shared grocery lists (simplified for PostgreSQL)
            cursor.execute("""
                SELECT DISTINCT c.resource_id, c.permission_level, c.created_at,
                       u.name as owner_name
                FROM collaborations c
                JOIN users u ON c.invited_by = u.id
                WHERE c.resource_type = 'grocery_list' 
                AND c.user_id = %s 
                AND c.status = 'active'
                ORDER BY c.created_at DESC
            """, (current_user['id'],))
            
            shared_grocery_lists_raw = cursor.fetchall()
            
            # Format grocery lists for response
            shared_grocery_lists = []
            for list_item in shared_grocery_lists_raw:
                shared_grocery_lists.append({
                    'id': list_item['resource_id'],
                    'list_name': f'Shared Grocery List #{list_item["resource_id"]}',
                    'owner_name': list_item['owner_name'],
                    'permission_level': list_item['permission_level'],
                    'shared_date': list_item['created_at']
                })
            
            cursor.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'shared_meal_plans': shared_meal_plans,
                'shared_grocery_lists': shared_grocery_lists
            })
            
        except Exception as e:
            logger.error(f"❌ Get shared resources error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/collaboration/check-access/<resource_type>/<int:resource_id>', methods=['GET'])
    def check_collaboration_access(resource_type, resource_id):
        """Check if current user has access to a resource"""
        try:
            current_user = get_authenticated_user()
            if not current_user:
                return jsonify({'error': 'Authentication required'}), 401
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # For now, assume the user has access if they're logged in (simplified)
            # In the future, this would check actual ownership and collaboration records
            
            # Check collaboration access
            cursor.execute("""
                SELECT permission_level FROM collaborations 
                WHERE resource_type = %s AND resource_id = %s 
                AND user_id = %s AND status = 'active'
            """, (resource_type, resource_id, current_user['id']))
            
            collaboration = cursor.fetchone()
            if collaboration:
                cursor.close()
                conn.close()
                return jsonify({
                    'has_access': True, 
                    'role': collaboration['permission_level']
                })
            
            cursor.close()
            conn.close()
            return jsonify({'has_access': False, 'role': None})
            
        except Exception as e:
            logger.error(f"❌ Check collaboration access error: {e}")
            return jsonify({'error': str(e)}), 500

    # 📰 Latest Updates API - Evergreen Content + Friend Activity
    def populate_content_pieces():
        """Populate the content_pieces table with evergreen cooking tips"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if content already exists
            try:
                cursor.execute("SELECT COUNT(*) FROM content_pieces")
                count = cursor.fetchone()[0]
                
                if count > 0:
                    logger.info(f"📰 Content pieces already populated ({count} pieces)")
                    conn.close()
                    return
            except Exception as table_error:
                logger.warning(f"📰 Content table may not exist yet: {table_error}")
                # Continue to populate since table might be newly created
            
            # Evergreen content pieces with categories
            content_pieces = [
                ("Sheet pan formula", "When you don't feel like cooking, throw some protein, a veggie, and your favorite spice on a sheet pan. The oven does the rest, and you've got dinner without the fuss.", "tip"),
                ("The fastest sauce in the world", "A little garlic in olive oil and a splash of pasta water is all it takes. It turns plain noodles into something cozy and flavorful in minutes.", "technique"),
                ("Leftovers to tacos", "Got leftover chicken? Shred it, toss it on a tortilla, squeeze some lime, and boom — a brand-new meal that doesn't feel like leftovers.", "tip"),
                ("One-pot wonders", "Soup, curry, stew — they all start the same way. One pot, everything goes in, and you end up with something warm, flavorful, and way less cleanup.", "tip"),
                ("15-minute fried rice", "Cold rice, an egg, soy sauce, and whatever vegetables you've got sitting around. In 15 minutes, you've got fried rice that tastes like you planned it.", "tip"),
                ("Pasta + pantry = dinner", "Tomato paste, garlic, and chili flakes — three pantry staples that can turn plain pasta into something you'll actually look forward to eating.", "tip"),
                ("The power of toast", "Toast isn't just for breakfast. Top it with beans, avocado, or ricotta — whatever's around — and suddenly it feels like a whole meal.", "tip"),
                ("Soup starter pack", "Start with onion, carrot, and celery. Add stock, then whatever else you've got in the fridge, and you've just built yourself a soup base.", "technique"),
                ("Microwave heroics", "Want quick vegetables? Toss them in a bowl with a splash of water, microwave for a few minutes, and finish with olive oil and salt. Done.", "tip"),
                ("Wrap it up", "Grab a tortilla, spread some hummus, add leftover protein, and roll it up. That's lunch in two minutes.", "tip"),
                ("Eggs for dinner", "When in doubt, crack an egg. Omelets, frittatas, even shakshuka — eggs can save dinner faster than you think.", "tip"),
                ("Pantry pasta sauce", "A can of tomatoes, a knob of butter, and half an onion simmered together. It tastes like magic and barely takes any effort.", "technique"),
                ("Quesadilla magic", "A tortilla with cheese in a hot pan is good enough. Add beans or veggies and suddenly it's a full meal.", "tip"),
                ("Salad = meal", "Greens get serious when you top them with a fried egg, a can of tuna, or yesterday's chicken. That's how you turn a side into dinner.", "tip"),
                ("Double once, eat twice", "Make extra rice or beans today. Tomorrow they'll become burritos, bowls, or soup without any extra work.", "tip"),
                ("A sharp knife saves time", "A sharp knife makes cooking easier. Dull blades slip, fight back, and slow you down. Keep it sharp and everything feels smoother.", "equipment"),
                ("One good pan beats three cheap ones", "You don't need a full set of pots and pans. One heavy skillet can sear, sauté, bake, and even go straight to the table.", "equipment"),
                ("Tongs are your best friend", "Tongs are basically an extra set of hands. Flip, toss, serve — once you get used to them, you'll wonder how you cooked without them.", "equipment"),
                ("The underrated bench scraper", "A bench scraper clears your cutting board in one swipe and moves chopped veggies without juggling your knife. Total game-changer.", "equipment"),
                ("The lid does half the work", "Want food to cook faster? Just cover the pan. Steam gets trapped, and dinner comes together way quicker.", "technique"),
                ("Keep a scrap bowl nearby", "Keep a little bowl on the counter for peels, cores, and scraps. You'll be amazed how much cleaner and easier cooking feels.", "tip"),
                ("Salt in layers", "Don't just salt at the end. A pinch while you're cooking brings out flavor at every step.", "technique"),
                ("Heat is an ingredient", "High heat gives you sear and smoke, low heat brings out sweetness. Knowing when to use each makes a huge difference.", "technique"),
                ("Rest is cooking, too", "Take that steak off the heat and let it sit. Resting keeps the juices in and makes it taste so much better.", "technique"),
                ("Acid balances fat", "Rich and creamy dishes need a squeeze of lemon or a splash of vinegar. It makes everything taste brighter.", "technique"),
                ("Use your hands", "Your hands tell you more than gadgets. Dough feels alive, and you can check a steak's doneness with just a touch.", "technique"),
                ("Cook in odd numbers", "Here's a chef trick: three scallops look better than two, five dumplings look better than four. Odd numbers just please the eye.", "technique"),
                ("Smell tells the truth", "You don't always need a timer. When garlic smells fragrant or bread smells toasted — that's when it's ready.", "technique"),
                ("Chill the bowl, whip the cream", "Pop your bowl and whisk in the freezer before you whip cream. It makes the job faster and fluffier.", "technique"),
                ("Knives, not gadgets", "One good knife will outwork half the gadgets in your drawer. Learn the knife, lose the clutter.", "equipment"),
                ("Taste twice, serve once", "Always taste before you serve. That last spoonful is your chance to adjust salt, acid, or seasoning before it hits the plate.", "technique")
            ]
            
            # Insert content pieces
            for i, (title, content, category) in enumerate(content_pieces):
                cursor.execute("""
                    INSERT INTO content_pieces (title, content, category, sort_order)
                    VALUES (%s, %s, %s, %s)
                """, (title, content, category, i + 1))
            
            conn.commit()
            conn.close()
            logger.info(f"📰 Successfully populated {len(content_pieces)} content pieces")
            
        except Exception as e:
            logger.error(f"📰 Error populating content pieces: {e}")
            if 'conn' in locals():
                conn.close()

    @app.route('/api/latest-updates', methods=['GET'])
    def get_latest_updates():
        """Get mixed feed of evergreen content and friend activity"""
        try:
            current_user = get_authenticated_user()
            if not current_user:
                return jsonify({'error': 'Authentication required'}), 401
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get weekly rotation seed (same content for same week)
            import datetime
            week_of_year = datetime.datetime.now().isocalendar()[1]
            user_seed = current_user['id']
            rotation_seed = (week_of_year + user_seed) % 1000
            
            # Get evergreen content (70% of feed) - Use seeded selection to avoid duplicates
            # Create a deterministic but varied selection based on week + user
            cursor.execute("""
                SELECT id, title, content, category, created_at
                FROM content_pieces 
                WHERE is_active = true
                ORDER BY ((id * 13 + %s * 7) %% 10007)
                LIMIT 4
            """, (rotation_seed,))
            
            content_pieces = cursor.fetchall()
            
            # Get friend activity (30% of feed) - for now, get recent community shares
            cursor.execute("""
                SELECT r.id, r.community_title as title,
                       CASE 
                           WHEN u.email IS NOT NULL THEN LEFT(u.email, POSITION('@' IN u.email) - 1) || 'Chef'
                           ELSE 'AnonymousChef'
                       END as user_name,
                       'recipe_shared' as activity_type, r.shared_at as created_at
                FROM recipes r
                LEFT JOIN users u ON r.user_id = u.id
                WHERE r.is_community_shared = true 
                AND r.shared_at IS NOT NULL
                ORDER BY r.shared_at DESC
                LIMIT 2
            """)
            
            friend_activity = cursor.fetchall()
            
            # Mix the content
            updates = []
            
            # Add evergreen content
            for piece in content_pieces:
                updates.append({
                    'id': f"content_{piece['id']}",
                    'type': 'content',
                    'title': piece['title'],
                    'content': piece['content'],
                    'category': piece['category'],
                    'created_at': piece['created_at'].isoformat() if piece['created_at'] else None,
                    'icon': ''  # No emoji icons
                })
            
            # Add friend activity
            for activity in friend_activity:
                updates.append({
                    'id': f"activity_{activity['id']}",
                    'type': 'activity',
                    'title': f"{activity['user_name']} shared a recipe",
                    'content': f"Check out their latest recipe: {activity['title']}",
                    'category': 'social',
                    'created_at': activity['created_at'].isoformat() if activity['created_at'] else None,
                    'icon': '',  # No emoji icons
                    'reference_id': activity['id'],
                    'activity_type': activity['activity_type']
                })
            
            # Shuffle the mixed content for variety
            import random
            random.Random(rotation_seed).shuffle(updates)
            
            conn.close()
            
            logger.info(f"📰 Served {len(updates)} latest updates (rotation seed: {rotation_seed})")
            return jsonify({
                'success': True,
                'updates': updates,
                'rotation_week': week_of_year
            })
            
        except Exception as e:
            logger.error(f"📰 Error getting latest updates: {e}")
            if 'conn' in locals():
                conn.close()
            return jsonify({'error': 'Failed to get latest updates'}), 500

    # Initialize content pieces on startup
    try:
        populate_content_pieces()
    except Exception as e:
        logger.error(f"📰 Failed to initialize content pieces: {e}")

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
