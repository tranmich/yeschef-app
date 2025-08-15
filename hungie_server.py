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

# Import authentication system
from auth_system import AuthenticationSystem
from auth_routes import create_auth_routes

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Import meal planning systems
try:
    from core_systems.meal_planning_system import MealPlanningSystem
    from core_systems.grocery_list_generator import GroceryListGenerator
    from core_systems.favorites_manager import FavoritesManager
    MEAL_PLANNING_AVAILABLE = True
    logger.info("âœ… Meal planning systems imported successfully")
except ImportError as e:
    MEAL_PLANNING_AVAILABLE = False
    logger.warning(f"âš ï¸ Meal planning systems not available: {e}")

# Load environment variables
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    logger.info("âœ… OpenAI client initialized")
else:
    client = None
    logger.warning("âš ï¸ OpenAI API key not found")

# Chef personality for AI responses
CHEF_PERSONALITY = """You are Hungie, an enthusiastic and knowledgeable personal chef assistant. You're passionate about food, cooking, and helping people discover amazing recipes. You always maintain a friendly, encouraging tone and love to share cooking tips. When talking about recipes, you're descriptive and make food sound delicious. You occasionally use food emojis and express excitement about cooking. Always end your responses with "Yes, Chef! ðŸ´" to maintain your chef personality."""

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
    auth_routes = create_auth_routes(auth_system)
    app.register_blueprint(auth_routes)
    logger.info("ðŸ” Authentication system initialized and routes registered")
except Exception as e:
    logger.error(f"âŒ Failed to initialize authentication system: {e}")
    auth_system = None

# Enhanced systems - with proper error handling
ENHANCED_SEARCH_AVAILABLE = False
FLAVOR_PROFILE_AVAILABLE = False

try:
    from core_systems.enhanced_search import EnhancedSearchEngine
    ENHANCED_SEARCH_AVAILABLE = True
    logger.info("ðŸ§  Enhanced search loaded")
except ImportError as e:
    logger.warning(f"âš ï¸ Enhanced search not available: {e}")

try:
    from core_systems.production_flavor_system import FlavorProfileSystem, enhance_recipe_with_flavor_intelligence
    from recipe_database_enhancer import RecipeDatabaseEnhancer
    FLAVOR_PROFILE_AVAILABLE = True
    logger.info("ðŸ”¥ Flavor profile system loaded")
except ImportError as e:
    logger.warning(f"âš ï¸ Flavor profile system not available: {e}")

# Import backend modernization components
try:
    from backend_modernization_patch import (
        ModernSessionManager, 
        EnhancedResponseBuilder, 
        ConversationSuggestionGenerator,
        get_session_manager
    )
    session_manager = get_session_manager()
    logger.info("âœ… Backend modernization patch loaded")
except ImportError as e:
    session_manager = None
    logger.warning(f"âš ï¸ Backend modernization patch not available: {e}")

# Database connection
def get_db_connection():
    """Get PostgreSQL database connection with proper error handling"""
    try:
        # Use PostgreSQL connection from Railway environment
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise Exception("DATABASE_URL environment variable not found. PostgreSQL connection required.")
        
        # PostgreSQL connection
        conn = psycopg2.connect(database_url)
        conn.cursor_factory = psycopg2.extras.RealDictCursor
        logger.info("✅ Connected to PostgreSQL database")
        return conn
        
    except Exception as e:
        logger.error(f"❌ PostgreSQL connection error: {e}")
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
        logger.info("✅ Database tables initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")
        if 'conn' in locals():
            conn.close()
        raise

# Core search function - ENHANCED WITH INTELLIGENT INGREDIENT RECOGNITION
def search_recipes_by_query(query, limit=20):
    """Search recipes by query - ENHANCED with intelligent ingredient recognition"""
    try:
        logger.info(f"ðŸ§  Enhanced Search for: '{query}' (limit: {limit})")
        
        # Use enhanced recipe suggestion engine for intelligent search
        try:
            from core_systems.enhanced_recipe_suggestions import get_smart_suggestions
            
            # Get intelligent suggestions with recipe type classification
            result = get_smart_suggestions(query, session_id='search', limit=limit)
            recipes = result['suggestions']
            preferences = result['preferences_detected']
            
            logger.info(f"ðŸ§  Enhanced search detected ingredients: {preferences.get('ingredients', [])}")
            logger.info(f"ðŸ§  Enhanced search found {len(recipes)} recipes with types")
            
            # Transform to expected format
            enhanced_recipes = []
            for recipe in recipes:
                enhanced_recipe = {
                    'id': recipe['id'],
                    'title': recipe['title'],
                    'name': recipe['title'],  # For frontend compatibility
                    'description': recipe['description'] or '',
                    'servings': recipe['servings'] or '4 servings',
                    'prep_time': recipe['prep_time'] or '',
                    'cook_time': recipe['cook_time'] or '30 minutes',
                    'total_time': recipe['total_time'] or '30 minutes',
                    'ingredients': recipe['ingredients'] or '',
                    'instructions': recipe['instructions'] or '',
                    'recipe_types': recipe.get('recipe_types', []),  # NEW: Recipe type classification
                    'detected_preferences': preferences  # NEW: What the AI detected
                }
                enhanced_recipes.append(enhanced_recipe)
                logger.debug(f"âœ“ Enhanced Recipe: {recipe['title']} (Types: {recipe.get('recipe_types', [])})")
            
            logger.info(f"ðŸŽ¯ Enhanced search returning {len(enhanced_recipes)} recipes")
            return enhanced_recipes
            
        except ImportError as e:
            logger.warning(f"âš ï¸ Enhanced search not available, falling back to basic search: {e}")
            # Fallback to basic search if enhanced system not available
            pass
        
        # FALLBACK: Basic search (original logic)
        logger.info(f"ðŸ” Fallback search for: '{query}' (limit: {limit})")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        search_term = f"%{query}%"
        
        # PostgreSQL syntax - use ILIKE for case-insensitive search, %s placeholders
        cursor.execute("""
            SELECT DISTINCT r.id, r.title, r.description, r.servings, 
                   r.hands_on_time, r.total_time, r.ingredients, r.instructions
            FROM recipes r
            WHERE r.title ILIKE %s OR r.description ILIKE %s OR r.ingredients ILIKE %s
            ORDER BY r.title
            LIMIT %s
        """, (search_term, search_term, search_term, limit))
        
        recipes = []
        rows = cursor.fetchall()
        logger.info(f"ðŸ” Basic search returned {len(rows)} results")
        
        for row in rows:
            recipe = {
                'id': row['id'],
                'title': row['title'],
                'name': row['title'],  # For frontend compatibility
                'description': row['description'] or '',
                'servings': row['servings'] or '4 servings',
                'prep_time': row['hands_on_time'] or '',
                'cook_time': row['total_time'] or '30 minutes',
                'total_time': row['total_time'] or '30 minutes',
                'ingredients': row['ingredients'] or '',
                'instructions': row['instructions'] or '',
                'recipe_types': [],  # Empty for basic search
                'detected_preferences': {}  # Empty for basic search
            }
            
            # Parse JSON if needed
            try:
                if recipe['ingredients'] and isinstance(recipe['ingredients'], str):
                    parsed = json.loads(recipe['ingredients'])
                    if isinstance(parsed, list):
                        recipe['ingredients'] = parsed
            except (json.JSONDecodeError, TypeError):
                pass
                
            try:
                if recipe['instructions'] and isinstance(recipe['instructions'], str):
                    parsed = json.loads(recipe['instructions'])
                    if isinstance(parsed, list):
                        recipe['instructions'] = parsed
            except (json.JSONDecodeError, TypeError):
                pass
            
            recipes.append(recipe)
            logger.debug(f"âœ“ Basic Recipe: {recipe['title']}")
        
        conn.close()
        logger.info(f"ðŸŽ¯ Basic search returning {len(recipes)} recipes")
        return recipes
        
    except Exception as e:
        logger.error(f"Search error: {e}")
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
        
        # NEW: Add recipe type classification for individual recipes
        try:
            from core_systems.enhanced_recipe_suggestions import SmartRecipeSuggestionEngine
            engine = SmartRecipeSuggestionEngine()
            recipe_types = engine.classify_recipe_types(recipe['title'], 
                                                      ' '.join(recipe['instructions']) if isinstance(recipe['instructions'], list) 
                                                      else str(recipe['instructions']))
            recipe['recipe_types'] = recipe_types
            logger.info(f"ðŸ·ï¸ Recipe '{recipe['title']}' classified as: {recipe_types}")
        except Exception as e:
            logger.warning(f"âš ï¸ Recipe type classification failed: {e}")
            recipe['recipe_types'] = []
        
        conn.close()
        return recipe
        
    except Exception as e:
        logger.error(f"Get recipe error: {e}")
        return None

# API Routes
@app.route('/')
def api_root():
    """API root endpoint"""
    return jsonify({
        'message': 'Hungie API Server',
        'status': 'healthy',
        'endpoints': {
            'recipes': '/api/recipes',
            'search': '/api/search',
            'auth': '/api/auth',
            'health': '/api/health'
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
        
        logger.info(f"✅ Recipe created: {data.get('title')} (ID: {recipe_id})")
        
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
    """Search for recipes by query - ENHANCED with intelligent ingredient detection"""
    try:
        query = request.args.get('q', '').strip()
        logger.info(f"ðŸŒ Enhanced API Search request for: '{query}'")
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query parameter is required'
            }), 400
        
        recipes = search_recipes_by_query(query, limit=20)
        logger.info(f"ðŸŒ Enhanced API returning {len(recipes)} recipes")
        
        # Extract search metadata for frontend
        search_metadata = {
            'query': query,
            'total_results': len(recipes),
            'enhanced_search_used': True,
            'detected_ingredients': [],
            'recipe_types_found': []
        }
        
        # Get metadata from first recipe if available
        if recipes and 'detected_preferences' in recipes[0]:
            preferences = recipes[0]['detected_preferences']
            search_metadata['detected_ingredients'] = preferences.get('ingredients', [])
            
            # Collect all recipe types found
            all_types = []
            for recipe in recipes:
                all_types.extend(recipe.get('recipe_types', []))
            search_metadata['recipe_types_found'] = list(set(all_types))
        
        return jsonify({
            'success': True,
            'data': recipes,
            'metadata': search_metadata  # NEW: Enhanced search metadata
        })
        
    except Exception as e:
        logger.error(f"Search API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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
def smart_search():
    """AI-powered smart search with enhanced session management and response building"""
    try:
        if not client:
            return jsonify({
                'success': False,
                'error': 'AI service not available'
            }), 503
        
        data = request.get_json()
        user_message = data.get('message', '').strip()
        context = data.get('context', '')
        session_id = data.get('session_id', 'default')
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        # Initialize/update session if modernization is available
        if session_manager:
            session_manager.get_or_create_session(session_id)
        
        # Import the enhanced suggestion engine
        try:
            from core_systems.enhanced_recipe_suggestions import get_smart_suggestions
            
            # Check if this is a recipe request
            recipe_keywords = ['recipe', 'cook', 'eat', 'make', 'dinner', 'lunch', 'breakfast', 'tonight', 'today']
            is_recipe_request = any(keyword in user_message.lower() for keyword in recipe_keywords)
            
            if is_recipe_request:
                # Get smart recipe suggestions with contextual response
                suggestion_result = get_smart_suggestions(user_message, session_id, limit=5)
                suggestions = suggestion_result['suggestions']
                preferences = suggestion_result['preferences_detected']
                contextual_response = suggestion_result.get('contextual_response', '')
                
                # Record query in session if modernization is available
                if session_manager:
                    session_manager.record_query(
                        session_id=session_id,
                        user_query=user_message,
                        intent="recipe_search",
                        context=context,
                        result_count=len(suggestions),
                        displayed_count=len(suggestions),
                        search_phase="initial_search"
                    )
                
                if suggestions:
                    # Use the intelligent contextual response instead of template
                    ai_response = contextual_response if contextual_response else f"Here are {len(suggestions)} delicious recipe suggestions for you! Yes, Chef! ðŸ´"
                    
                    # Generate conversation suggestions if modernization is available
                    conversation_suggestions = None
                    if session_manager:
                        conversation_suggestions = ConversationSuggestionGenerator.generate_suggestions(
                            user_message, suggestions
                        )
                    
                    # Build enhanced response if modernization is available
                    if session_manager:
                        return jsonify(EnhancedResponseBuilder.build_smart_search_response(
                            ai_response=ai_response,
                            user_message=user_message,
                            session_id=session_id,
                            suggestions=suggestions,
                            preferences=preferences,
                            conversation_suggestions=conversation_suggestions
                        ))
                    else:
                        # Fallback to original response format
                        return jsonify({
                            'success': True,
                            'data': {
                                'response': ai_response,
                                'context': user_message,
                                'recipes': suggestions,
                                'preferences': preferences,
                                'session_id': session_id
                            }
                        })
                else:
                    # Fallback to general AI response if no recipes found
                    ai_response = "I'd love to help you cook something delicious! Could you be more specific about what you're in the mood for? For example, tell me about ingredients you have, cuisine preferences, or cooking style. Yes, Chef! ðŸ´"
                    
                    # Record query even if no results
                    if session_manager:
                        session_manager.record_query(
                            session_id=session_id,
                            user_query=user_message,
                            intent="recipe_search",
                            context=context,
                            result_count=0,
                            displayed_count=0,
                            search_phase="no_results"
                        )
                        
                        conversation_suggestions = ConversationSuggestionGenerator.generate_suggestions(user_message)
                        
                        return jsonify(EnhancedResponseBuilder.build_smart_search_response(
                            ai_response=ai_response,
                            user_message=user_message,
                            session_id=session_id,
                            conversation_suggestions=conversation_suggestions
                        ))
                    else:
                        return jsonify({
                            'success': True,
                            'data': {
                                'response': ai_response,
                                'context': user_message,
                                'session_id': session_id
                            }
                        })
            
        except ImportError as e:
            logger.warning(f"Enhanced suggestions not available: {e}")
        
        # Build conversation context for general AI chat
        messages = [
            {"role": "system", "content": CHEF_PERSONALITY},
            {"role": "user", "content": f"Context: {context}\n\nUser: {user_message}"}
        ]
        
        # Call OpenAI API for general chat
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        # Record general chat query
        if session_manager:
            session_manager.record_query(
                session_id=session_id,
                user_query=user_message,
                intent="general_chat",
                context=context,
                result_count=1,
                displayed_count=1,
                search_phase="ai_chat"
            )
            
            conversation_suggestions = ConversationSuggestionGenerator.generate_suggestions(user_message)
            
            return jsonify(EnhancedResponseBuilder.build_smart_search_response(
                ai_response=ai_response,
                user_message=user_message,
                session_id=session_id,
                conversation_suggestions=conversation_suggestions
            ))
        else:
            return jsonify({
                'success': True,
                'data': {
                    'response': ai_response,
                    'context': user_message,
                    'session_id': session_id
                }
            })
        
    except Exception as e:
        logger.error(f"Smart search API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/recipe-suggestions', methods=['POST'])
def get_recipe_suggestions():
    """Get recipe suggestions based on user preferences"""
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
        
        # Import the enhanced suggestion engine
        from core_systems.enhanced_recipe_suggestions import get_smart_suggestions
        
        # Get suggestions
        result = get_smart_suggestions(query, session_id, limit)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Recipe suggestions API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/database-stats', methods=['GET'])
def get_database_stats():
    """Get database statistics for debugging"""
    try:
        from core_systems.enhanced_recipe_suggestions import get_database_info
        
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
    """Get all available recipe types and their statistics"""
    try:
        from core_systems.enhanced_recipe_suggestions import SmartRecipeSuggestionEngine
        
        engine = SmartRecipeSuggestionEngine()
        
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
    """Search recipes by specific recipe type"""
    try:
        logger.info(f"ðŸ·ï¸ Searching by recipe type: '{recipe_type}'")
        
        # Validate recipe type
        valid_types = ['one_pot', 'quick', 'easy', 'challenging', 'low_prep', 'slow_cook']
        if recipe_type not in valid_types:
            return jsonify({
                'success': False,
                'error': f'Invalid recipe type. Valid types: {valid_types}'
            }), 400
        
        # Get keywords for this recipe type
        from core_systems.enhanced_recipe_suggestions import SmartRecipeSuggestionEngine
        engine = SmartRecipeSuggestionEngine()
        
        # Use the first keyword as the search query
        keywords = engine.recipe_type_keywords.get(recipe_type, [recipe_type])
        search_query = keywords[0] if keywords else recipe_type
        
        # Search recipes
        recipes = search_recipes_by_query(search_query, limit=20)
        
        # Filter to only recipes that actually have this type
        filtered_recipes = [
            recipe for recipe in recipes 
            if recipe_type in recipe.get('recipe_types', [])
        ]
        
        logger.info(f"ðŸ·ï¸ Found {len(filtered_recipes)} recipes of type '{recipe_type}'")
        
        return jsonify({
            'success': True,
            'data': filtered_recipes,
            'metadata': {
                'recipe_type': recipe_type,
                'total_found': len(filtered_recipes),
                'search_keywords': keywords
            }
        })
        
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
    """Generate dynamic conversation suggestions based on context"""
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
        
        suggestions = ConversationSuggestionGenerator.generate_suggestions(
            user_query, search_results
        )
        
        return jsonify({
            'success': True,
            'data': {
                'suggestions': suggestions,
                'query': user_query,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Conversation suggestions API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
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

@app.route('/api/admin/migrate-recipes', methods=['POST'])
def migrate_recipes_endpoint():
    """Admin endpoint to add sample recipes to PostgreSQL database"""
    try:
        # Simple security check
        admin_key = request.headers.get('X-Admin-Key')
        if admin_key != 'migrate-recipes-2025':
            return jsonify({
                'success': False,
                'error': 'Unauthorized - Admin key required'
            }), 401
        
        logger.info("🚀 Starting sample recipe addition to PostgreSQL")
        
        # Check database connection
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            return jsonify({
                'success': False,
                'error': 'PostgreSQL DATABASE_URL not available'
            }), 500
        
        # Sample recipes to add
        sample_recipes = [
            {
                'title': 'Classic Chicken Parmesan',
                'description': 'Crispy breaded chicken cutlets topped with marinara sauce and melted mozzarella cheese. Servings: 4 | Total time: 45 minutes',
                'ingredients': '4 boneless chicken breasts, 1 cup breadcrumbs, 1 cup marinara sauce, 1 cup mozzarella cheese, 2 eggs, flour for dredging, olive oil, salt, pepper',
                'instructions': '1. Pound chicken to 1/4 inch thickness. 2. Set up breading station with flour, beaten eggs, and breadcrumbs. 3. Bread chicken cutlets. 4. Pan fry until golden brown. 5. Top with marinara and cheese. 6. Bake until cheese melts.',
                'source': 'Recipe Collection | Chapter: Main Dishes',
                'category': 'Main Course'
            },
            {
                'title': 'Beef Stroganoff',
                'description': 'Tender beef strips in a creamy mushroom sauce served over egg noodles. Servings: 6 | Total time: 30 minutes',
                'ingredients': '1 lb beef sirloin, 8 oz mushrooms, 1 cup sour cream, 2 cups beef broth, 1 onion, 2 tbsp flour, egg noodles, butter, salt, pepper',
                'instructions': '1. Slice beef into strips. 2. Sauté onions and mushrooms. 3. Brown beef strips. 4. Add flour and cook 1 minute. 5. Add broth and simmer. 6. Stir in sour cream. 7. Serve over noodles.',
                'source': 'Recipe Collection | Chapter: Comfort Food',
                'category': 'Main Course'
            },
            {
                'title': 'Chocolate Chip Cookies',
                'description': 'Classic homemade chocolate chip cookies with crispy edges and chewy centers. Servings: 24 cookies | Total time: 25 minutes',
                'ingredients': '2 1/4 cups flour, 1 tsp baking soda, 1 cup butter, 3/4 cup brown sugar, 1/2 cup white sugar, 2 eggs, 2 tsp vanilla, 2 cups chocolate chips',
                'instructions': '1. Preheat oven to 375°F. 2. Mix dry ingredients. 3. Cream butter and sugars. 4. Add eggs and vanilla. 5. Combine wet and dry ingredients. 6. Stir in chocolate chips. 7. Drop onto baking sheets. 8. Bake 9-11 minutes.',
                'source': 'Recipe Collection | Chapter: Desserts',
                'category': 'Dessert'
            },
            {
                'title': 'Caesar Salad',
                'description': 'Fresh romaine lettuce with homemade Caesar dressing, croutons, and parmesan cheese. Servings: 4 | Total time: 15 minutes',
                'ingredients': '1 head romaine lettuce, 1/2 cup parmesan cheese, 1 cup croutons, 2 cloves garlic, 2 anchovy fillets, 1 egg yolk, 1/4 cup olive oil, 2 tbsp lemon juice, Worcestershire sauce',
                'instructions': '1. Wash and chop romaine lettuce. 2. Make dressing by whisking garlic, anchovies, egg yolk, lemon juice, and Worcestershire. 3. Slowly add olive oil. 4. Toss lettuce with dressing. 5. Top with parmesan and croutons.',
                'source': 'Recipe Collection | Chapter: Salads',
                'category': 'Salad'
            },
            {
                'title': 'Vegetable Stir Fry',
                'description': 'Quick and healthy vegetable stir fry with a savory sauce. Servings: 4 | Total time: 20 minutes',
                'ingredients': '2 cups broccoli florets, 1 bell pepper, 1 carrot, 1 zucchini, 2 cloves garlic, 1 inch ginger, 3 tbsp soy sauce, 1 tbsp sesame oil, 2 tbsp vegetable oil, 1 tsp cornstarch',
                'instructions': '1. Cut all vegetables into bite-sized pieces. 2. Heat oil in wok or large skillet. 3. Stir fry vegetables starting with hardest ones first. 4. Add garlic and ginger. 5. Mix sauce ingredients and add to pan. 6. Stir fry until vegetables are tender-crisp.',
                'source': 'Recipe Collection | Chapter: Vegetables',
                'category': 'Vegetarian'
            },
            {
                'title': 'Grilled Salmon with Lemon',
                'description': 'Fresh salmon fillets grilled to perfection with lemon and herbs. Servings: 4 | Total time: 20 minutes',
                'ingredients': '4 salmon fillets, 2 lemons, 2 tbsp olive oil, 2 cloves garlic, fresh dill, salt, pepper',
                'instructions': '1. Preheat grill to medium-high. 2. Brush salmon with olive oil. 3. Season with salt, pepper, and minced garlic. 4. Grill 4-5 minutes per side. 5. Finish with lemon juice and fresh dill.',
                'source': 'Recipe Collection | Chapter: Seafood',
                'category': 'Seafood'
            },
            {
                'title': 'Homemade Pizza Dough',
                'description': 'Perfect pizza dough recipe that\'s easy to make and delicious. Makes 2 large pizzas | Total time: 2 hours (includes rising)',
                'ingredients': '3 cups flour, 1 packet active dry yeast, 1 tsp salt, 1 tbsp olive oil, 1 cup warm water, 1 tsp sugar',
                'instructions': '1. Dissolve yeast and sugar in warm water. 2. Mix flour and salt in large bowl. 3. Add yeast mixture and olive oil. 4. Knead 8-10 minutes. 5. Let rise 1 hour. 6. Divide and shape. 7. Add toppings and bake.',
                'source': 'Recipe Collection | Chapter: Breads',
                'category': 'Bread'
            }
        ]
        
        # Insert recipes into PostgreSQL
        conn = get_db_connection()
        cursor = conn.cursor()
        
        inserted_count = 0
        for recipe_data in sample_recipes:
            try:
                cursor.execute("""
                    INSERT INTO recipes (title, description, ingredients, instructions, source, category, created_at)
                    VALUES (%(title)s, %(description)s, %(ingredients)s, %(instructions)s, %(source)s, %(category)s, NOW())
                    RETURNING id
                """, recipe_data)
                
                new_id = cursor.fetchone()[0]
                inserted_count += 1
                logger.info(f"✅ Inserted recipe: {recipe_data['title']} (ID: {new_id})")
                
            except Exception as e:
                logger.error(f"❌ Error inserting recipe {recipe_data['title']}: {e}")
        
        conn.commit()
        conn.close()
        
        # Verify the migration
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM recipes")
        total_recipes = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Sample recipes added successfully',
            'recipes_inserted': inserted_count,
            'total_recipes': total_recipes
        })
        
    except Exception as e:
        logger.error(f"❌ Migration error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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

    logger.info("ðŸš€ Starting Hungie Backend Server...")
    logger.info("ðŸš€ Server starting on http://localhost:5000")
    
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
        logger.error(f"âŒ Server startup failed: {e}")
        # Try alternative port as fallback
        try:
            logger.info("ðŸ”„ Trying alternative port 5001...")
            app.run(
                host="127.0.0.1",
                port=5001,
                debug=False,
                use_reloader=False,
                threaded=True
            )
        except Exception as e2:
            logger.error(f"âŒ Fallback also failed: {e2}")
            logger.error("Please check if ports are available and try again")
if __name__ == "__main__":
    logger.info("🚀 Starting Yes Chef! Backend Server...")
    
    # Initialize database
    try:
        init_db()
        logger.info("✅ Database initialization completed")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
    
    # Initialize Authentication System with database connection
    try:
        auth_system = AuthenticationSystem(app, get_db_connection)
        auth_routes = create_auth_routes(auth_system)
        app.register_blueprint(auth_routes)
        logger.info("🔐 Authentication system initialized and routes registered")
    except Exception as e:
        logger.error(f"❌ Failed to initialize authentication system: {e}")
        auth_system = None
    
    # Production hosting configuration (Railway/Heroku compatible)
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    logger.info(f"🚀 Server starting on {host}:{port}")
    
    try:
        app.run(
            host=host,
            port=port,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except Exception as e:
        logger.error(f"❌ Server startup failed: {e}")
        logger.error("Please check if ports are available and try again")
