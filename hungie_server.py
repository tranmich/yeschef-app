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

# Import meal planning systems
try:
    from core_systems.meal_planning_system import MealPlanningSystem
    from core_systems.grocery_list_generator import GroceryListGenerator
    from core_systems.favorites_manager import FavoritesManager
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

# Enhanced systems - with proper error handling
ENHANCED_SEARCH_AVAILABLE = False
FLAVOR_PROFILE_AVAILABLE = False

# Global Universal Search Engine
search_engine = None

try:
    from core_systems.enhanced_search import EnhancedSearchEngine
    ENHANCED_SEARCH_AVAILABLE = True
    logger.info("🧠 Enhanced search loaded")
except ImportError as e:
    logger.warning(f"⚠️ Enhanced search not available: {e}")

# Initialize Universal Search Engine (Day 4 Full Integration)
try:
    from core_systems.universal_search import UniversalSearchEngine
    # Initialize universal search engine
    search_engine = UniversalSearchEngine()
    logger.info("🔍 Universal search engine initialized - ALL search functions consolidated")
except ImportError as e:
    logger.warning(f"⚠️ Universal search engine not available: {e}")
    search_engine = None
except Exception as e:
    logger.error(f"❌ Failed to initialize universal search engine: {e}")
    search_engine = None

try:
    from core_systems.production_flavor_system import FlavorProfileSystem, enhance_recipe_with_flavor_intelligence
    from recipe_database_enhancer import RecipeDatabaseEnhancer
    FLAVOR_PROFILE_AVAILABLE = True
    logger.info("🔥 Flavor profile system loaded")
except ImportError as e:
    logger.warning(f"⚠️ Flavor profile system not available: {e}")

# Import backend modernization components
try:
    from backend_modernization_patch import (
        ModernSessionManager, 
        EnhancedResponseBuilder, 
        ConversationSuggestionGenerator,
        get_session_manager
    )
    session_manager = get_session_manager()
    logger.info("✅ Backend modernization patch loaded")
except ImportError as e:
    session_manager = None
    logger.warning(f"⚠️ Backend modernization patch not available: {e}")

# Database connection
def get_db_connection():
    """Get PostgreSQL database connection with proper error handling and fallback to public URL"""
    try:
        # Always try public URL first for Railway deployment reliability
        public_database_url = "postgresql://postgres:udQLpljdqTYmESmntwzmwDcOlBVbqlJG@shuttle.proxy.rlwy.net:31331/railway"
        logger.info("🔄 Trying reliable public DATABASE_URL first...")
        
        try:
            conn = psycopg2.connect(public_database_url)
            conn.cursor_factory = psycopg2.extras.RealDictCursor
            logger.info("✅ Connected to PostgreSQL database via public URL")
            return conn
        except Exception as public_error:
            logger.warning(f"⚠️ Public DATABASE_URL failed: {public_error}")
            
            # Fallback to environment DATABASE_URL (internal Railway URL)
            database_url = os.getenv('DATABASE_URL')
            if not database_url:
                raise Exception("DATABASE_URL environment variable not found. PostgreSQL connection required.")
            
            logger.info("🔄 Trying internal DATABASE_URL as fallback...")
            conn = psycopg2.connect(database_url)
            conn.cursor_factory = psycopg2.extras.RealDictCursor
            logger.info("✅ Connected to PostgreSQL database via internal URL")
            return conn
        
    except Exception as e:
        logger.error(f"❌ All PostgreSQL connection attempts failed: {e}")
        raise

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
        recipes = search_recipes_by_query(query, limit=50)
        logger.info(f"🌐 Universal API returning {len(recipes)} enhanced recipes")
        
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
        
        logger.info(f"🧠 Universal intelligent search: '{query}' | Session: {session_id} | Excluding: {len(shown_recipe_ids)} recipes")
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query parameter is required'
            }), 400
        
        # Use universal search engine with session awareness
        if search_engine:
            search_result = search_engine.unified_intelligent_search(
                query=query,
                session_memory={'session_id': session_id, 'shown_recipes': shown_recipe_ids},
                user_pantry=[],
                exclude_ids=shown_recipe_ids,
                limit=page_size * 3,  # Get more to account for exclusions
                include_explanations=True
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
                        'category': recipe['category'] or 'Main Course',
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
        
        # Fallback should never happen in production
        logger.error("⚠️ Universal search engine not available for intelligent search")
        return jsonify({
            'success': False,
            'error': 'Universal search engine not configured',
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
        
        # UNIVERSAL SEARCH CALL - replaces ALL 14+ scattered search functions
        search_result = search_engine.unified_intelligent_search(
            query=query,
            session_memory=session_memory,
            user_pantry=user_pantry,
            exclude_ids=exclude_ids,
            limit=limit,
            include_explanations=True
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
            conversation_suggestions = []
            if session_manager:
                try:
                    conversation_suggestions = ConversationSuggestionGenerator.generate_suggestions(
                        query, recipes
                    )
                except:
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
@app.route('/api/recipe-suggestions', methods=['POST'])
def get_recipe_suggestions():
    """
    Get recipe suggestions based on user preferences - UNIVERSAL SEARCH INTEGRATION
    
    ✨ CONSOLIDATION: Now uses UniversalSearchEngine for suggestions
    🎯 FEATURES: Intelligence filtering, smart explanations, preference learning
    📈 PERFORMANCE: Optimized queries with universal search engine
    """
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        session_id = data.get('session_id', 'default')
        limit = data.get('limit', 5)
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400
        
        logger.info(f"💡 Universal recipe suggestions for: '{query}' | Session: {session_id}")
        
        # Use universal search engine for suggestions
        if search_engine:
            search_result = search_engine.unified_intelligent_search(
                query=query,
                session_memory={'session_id': session_id},
                user_pantry=[],
                exclude_ids=[],
                limit=limit,
                include_explanations=True
            )
            
            if search_result['success']:
                return jsonify({
                    'success': True,
                    'data': {
                        'suggestions': search_result['recipes'],
                        'preferences_detected': search_result.get('search_metadata', {}),
                        'universal_search_used': True,
                        'intelligence_enabled': True,
                        'session_id': session_id
                    }
                })
            else:
                logger.warning(f"Universal recipe suggestions failed: {search_result.get('error', 'Unknown error')}")
                return jsonify({
                    'success': False,
                    'error': search_result.get('error', 'Universal search failed'),
                    'universal_search': False
                }), 500
        else:
            logger.error("⚠️ Universal search engine not available for recipe suggestions")
            return jsonify({
                'success': False,
                'error': 'Universal search engine not configured'
            }), 500
        
    except Exception as e:
        logger.error(f"Universal recipe suggestions API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'universal_search': False
        }), 500

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
        
        meal_planner = MealPlanningSystem()
        plan_id = meal_planner.create_meal_plan(plan_name, week_start_date, meal_data)
        
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
    """List all meal plans"""
    if not MEAL_PLANNING_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Meal planning system not available'
        }), 503
    
    try:
        limit = request.args.get('limit', 50, type=int)
        
        meal_planner = MealPlanningSystem()
        plans = meal_planner.list_meal_plans(limit=limit)
        
        return jsonify({
            'success': True,
            'meal_plans': plans,
            'count': len(plans)
        })
        
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
    """Add or remove a recipe from favorites"""
    if not MEAL_PLANNING_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Favorites system not available'
        }), 503
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        recipe_id = data.get('recipe_id')
        notes = data.get('notes', '')
        
        if not recipe_id:
            return jsonify({
                'success': False,
                'error': 'Recipe ID required'
            }), 400
        
        favorites_manager = FavoritesManager()
        result = favorites_manager.toggle_favorite(recipe_id, notes)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Toggle favorite error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    """Get user's favorite recipes"""
    if not MEAL_PLANNING_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Favorites system not available'
        }), 503
    
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        favorites_manager = FavoritesManager()
        favorites = favorites_manager.get_favorites(limit=limit, offset=offset)
        total_count = favorites_manager.get_favorites_count()
        
        return jsonify({
            'success': True,
            'favorites': favorites,
            'count': len(favorites),
            'total_count': total_count
        })
        
    except Exception as e:
        logger.error(f"Get favorites error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/favorites/check', methods=['POST'])
def check_favorites():
    """Check favorite status for multiple recipes"""
    if not MEAL_PLANNING_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Favorites system not available'
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
        
        favorites_manager = FavoritesManager()
        favorite_status = favorites_manager.bulk_check_favorites(recipe_ids)
        
        return jsonify({
            'success': True,
            'favorite_status': favorite_status
        })
        
    except Exception as e:
        logger.error(f"Check favorites error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/favorites/summary', methods=['GET'])
def get_favorites_summary():
    """Get favorites summary information"""
    if not MEAL_PLANNING_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Favorites system not available'
        }), 503
    
    try:
        favorites_manager = FavoritesManager()
        summary = favorites_manager.get_favorites_summary()
        
        return jsonify({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        logger.error(f"Get favorites summary error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint with backend capabilities"""
    try:
        capabilities = {
            'enhanced_search': ENHANCED_SEARCH_AVAILABLE,
            'flavor_profile': FLAVOR_PROFILE_AVAILABLE,
            'meal_planning': MEAL_PLANNING_AVAILABLE,
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

    logger.info("🚀 Starting Hungie Backend Server...")
    logger.info("� UNIVERSAL SEARCH CONSOLIDATION VERSION: 2025-08-17-v2")
    logger.info("�🚀 Server starting on http://localhost:5000")
    
    # Windows-stable configuration with error handling
    try:
        app.run(
            host="127.0.0.1",   # Use localhost only for Windows stability
            port=5000,          # Use standard Flask port
            debug=False,        # Disable debug for stability
            use_reloader=False, # Disable reloader to prevent conflicts
            threaded=True       # Enable threading
        )
    except Exception as e:
        logger.error(f"❌ Server startup failed: {e}")
        # Try alternative port as fallback
        try:
            logger.info("🔄 Trying alternative port 5001...")
            app.run(
                host="127.0.0.1",
                port=5001,
                debug=False,
                use_reloader=False,
                threaded=True
            )
        except Exception as e2:
            logger.error(f"❌ Fallback also failed: {e2}")
            logger.error("Please check if ports are available and try again")
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
        logger.info("?? Authentication system initialized and routes registered")
    except Exception as e:
        logger.error(f"? Failed to initialize authentication system: {e}")
        auth_system = None
    
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
