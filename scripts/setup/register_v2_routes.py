"""
Register v2 API Blueprints to existing Flask app
This file bridges the new v2 architecture with the existing hungie_server.py
"""

import logging
from flask import Flask

logger = logging.getLogger(__name__)


def register_v2_routes(app: Flask):
    """
    Register v2 API routes to the existing Flask app
    
    This adds the new v2 endpoints alongside existing routes:
    - /api/v2/auth/*  🔐 NEW!
    - /api/v2/users/*
    - /api/v2/recipes/*
    - /api/v2/health
    
    Old routes remain unchanged!
    """
    try:
        logger.info("🚀 Registering v2 API routes...")
        
        # Initialize database if not already done
        from app.database.connection import init_database
        init_database()
        logger.info("  ✅ Database connection pool initialized")
        
        # Initialize auth service with existing auth_system
        try:
            from auth_system import AuthenticationSystem
            from app.services.auth_service import get_auth_service
            
            # Get the auth_system from the app context if it exists
            auth_system = getattr(app, 'auth_system', None)
            
            if auth_system:
                # Initialize auth service with existing auth system
                auth_service = get_auth_service(auth_system)
                logger.info("  ✅ Auth service initialized with existing auth_system")
            else:
                logger.warning("  ⚠️  No auth_system found on app - auth service may have limited functionality")
        except Exception as e:
            logger.warning(f"  ⚠️  Could not initialize auth service: {e}")
        
        # Register v2 blueprints
        try:
            from app.api.v2.auth import auth_bp  # 🔐 NEW!
            logger.info("  ✅ Auth blueprint imported successfully")
        except Exception as e:
            logger.error(f"  ❌ FAILED to import auth blueprint: {e}")
            logger.exception("Full auth import error:")
            raise  # Re-raise to see full error
        
        from app.api.v2.users import user_bp
        from app.api.v2.recipes import recipe_bp
        from app.api.v2.recipe_import import recipe_import_bp  # 📥 Recipe import
        from app.api.v2.recipe_voice import recipe_voice_bp  # 🎤 Voice recipes
        from app.api.v2.meal_plans import meal_plan_bp
        from app.api.v2.grocery_lists import grocery_list_bp
        from app.api.v2.friends import friends_bp
        from app.api.v2.households import households_bp
        from app.api.v2.community import community_bp
        from app.api.v2.profile import profile_bp
        from app.api.v2.pantry import pantry_bp
        from app.api.v2.recipe_search import recipe_search_bp
        from app.api.v2.system import system_bp
        from app.api.v2.images import image_bp  # Image serving
        from app.api.v2.whiteboards import whiteboard_bp  # 🆕 Whiteboards (Phase 1)
        from app.api.v2.whiteboard_images import whiteboard_images_bp  # 🆕 Whiteboard image uploads
        from app.api.v2.liveblocks import liveblocks_bp  # 🆕 Liveblocks auth (Phase 3A)
        from app.api.v2.comments import comments_bp  # 🆕 Comments with Pusher
        from app.api.v2.pusher_auth import pusher_auth_bp  # 🆕 Pusher presence auth
        from app.api.v2.activity import activity_bp  # 🆕 Activity Feed & Notifications
        
        app.register_blueprint(auth_bp)  # 🔐 Authentication - Register FIRST!
        app.register_blueprint(user_bp)
        app.register_blueprint(recipe_bp)
        app.register_blueprint(recipe_import_bp)  # 📥 Recipe import
        app.register_blueprint(recipe_voice_bp)  # 🎤 Voice recipes
        app.register_blueprint(meal_plan_bp)
        app.register_blueprint(grocery_list_bp)
        app.register_blueprint(friends_bp)
        app.register_blueprint(households_bp)
        app.register_blueprint(community_bp)
        app.register_blueprint(profile_bp)
        app.register_blueprint(pantry_bp)
        app.register_blueprint(recipe_search_bp)
        app.register_blueprint(system_bp)
        app.register_blueprint(image_bp)  # Image serving
        app.register_blueprint(whiteboard_bp)  # 🆕 Whiteboards (Phase 1)
        app.register_blueprint(whiteboard_images_bp)  # 🆕 Whiteboard image uploads
        app.register_blueprint(liveblocks_bp)  # 🆕 Liveblocks auth (Phase 3A)
        app.register_blueprint(comments_bp)  # 🆕 Comments with Pusher
        app.register_blueprint(pusher_auth_bp)  # 🆕 Pusher presence auth
        app.register_blueprint(activity_bp)  # 🆕 Activity Feed & Notifications
        
        logger.info("  ✅ Auth API v2 registered: /api/v2/auth 🔐 NEW!")
        logger.info("  ✅ User API v2 registered: /api/v2/users")
        logger.info("  ✅ Recipe API v2 registered: /api/v2/recipes")
        logger.info("  ✅ Recipe Import API v2 registered: /api/v2/recipes/import 📥 NEW!")
        logger.info("  ✅ Recipe Voice API v2 registered: /api/v2/recipes/voice 🎤 NEW!")
        logger.info("  ✅ MealPlan API v2 registered: /api/v2/meal-plans")
        logger.info("  ✅ GroceryList API v2 registered: /api/v2/grocery-lists")
        logger.info("  ✅ Friends API v2 registered: /api/v2/friends 👥")
        logger.info("  ✅ Households API v2 registered: /api/v2/households 🏠")
        logger.info("  ✅ Community API v2 registered: /api/v2/community 🌟")
        logger.info("  ✅ Favorites API v2 registered: /api/v2/favorites ⭐")
        logger.info("  ✅ Profile API v2 registered: /api/v2/profile 👤")
        logger.info("  ✅ Pantry API v2 registered: /api/v2/pantry 🥫")
        logger.info("  ✅ Recipe Search API v2 registered: /api/v2/recipes/search 🔍")
        logger.info("  ✅ Images API v2 registered: /api/v2/images 📸")
        logger.info("  ✅ System API v2 registered: /api/v2/system ⚙️")
        logger.info("  ✅ Whiteboard API v2 registered: /api/v2/whiteboard (25 endpoints) 🎨 NEW!")
        logger.info("  ✅ Whiteboard Images API v2 registered: /api/v2/whiteboards/images 📸 NEW!")
        logger.info("  ✅ Liveblocks API v2 registered: /api/v2/liveblocks 🔴 LIVE!")
        logger.info("  ✅ Comments API v2 registered: /api/v2/comments 💬 NEW!")
        logger.info("  ✅ Pusher Auth API v2 registered: /api/v2/pusher/auth 🔌 NEW!")
        logger.info("  ✅ Activity Feed API v2 registered: /api/v2/activity 🔔 NEW!")
        
        # Add health check endpoint
        from flask import jsonify
        
        @app.route('/api/v2/health', methods=['GET'])
        def v2_health_check():
            """Health check endpoint for v2 API"""
            return jsonify({
                'status': 'healthy',
                'version': '2.0',
                'message': 'YesChef v2 API is running'
            })
        
        logger.info("  ✅ Health check endpoint registered: /api/v2/health")
        logger.info("=" * 70)
        logger.info("✅ V2 API ROUTES REGISTERED SUCCESSFULLY!")
        logger.info("=" * 70)
        logger.info("\nAvailable v2 endpoints:")
        logger.info("  GET  /api/v2/health")
        logger.info("  GET  /api/v2/users/<id>")
        logger.info("  GET  /api/v2/users/<id>/stats")
        logger.info("  GET  /api/v2/users/search?q=<term>")
        logger.info("  GET  /api/v2/recipes/user/<id>/stats  ⭐ THE STAR!")
        logger.info("  GET  /api/v2/recipes/user/<id>")
        logger.info("  GET  /api/v2/recipes/<id>")
        logger.info("  GET  /api/v2/recipes/search?user_id=<id>&q=<term>")
        logger.info("  GET  /api/v2/recipes/community")
        logger.info("  POST /api/v2/recipes")
        logger.info("  PATCH /api/v2/recipes/<id>")
        logger.info("  DELETE /api/v2/recipes/<id>")
        logger.info("  GET  /api/v2/meal-plans/user/<id>  🍽️")
        logger.info("  GET  /api/v2/meal-plans/<id>")
        logger.info("  POST /api/v2/meal-plans")
        logger.info("  PATCH /api/v2/meal-plans/<id>")
        logger.info("  DELETE /api/v2/meal-plans/<id>")
        logger.info("  GET  /api/v2/meal-plans/<id>/grocery-list  🌟 POWER!")
        logger.info("  GET  /api/v2/grocery-lists/user/<id>  🛒")
        logger.info("  GET  /api/v2/grocery-lists/<id>")
        logger.info("  POST /api/v2/grocery-lists")
        logger.info("  POST /api/v2/grocery-lists/from-meal-plan/<id>  🌟 POWER!")
        logger.info("  PATCH /api/v2/grocery-lists/<id>")
        logger.info("  POST /api/v2/grocery-lists/<id>/items")
        logger.info("  DELETE /api/v2/grocery-lists/<id>/items/<index>")
        logger.info("  POST /api/v2/grocery-lists/<id>/items/<index>/purchase")
        logger.info("  POST /api/v2/grocery-lists/<id>/clear-purchased")
        logger.info("  DELETE /api/v2/grocery-lists/<id>")
        logger.info("  GET  /api/v2/friends/user/<id>  👥 NEW!")
        logger.info("  GET  /api/v2/friends/requests/user/<id>  👥 NEW!")
        logger.info("  POST /api/v2/friends/request  👥 NEW!")
        logger.info("  POST /api/v2/friends/request/<id>/accept  👥 NEW!")
        logger.info("  POST /api/v2/friends/request/<id>/decline  👥 NEW!")
        logger.info("  DELETE /api/v2/friends/<id>  👥 NEW!")
        logger.info("  GET  /api/v2/friends/status  👥 NEW!")
        logger.info("  GET  /api/v2/households/user/<id>  🏠 NEW!")
        logger.info("  GET  /api/v2/households/<id>  🏠 NEW!")
        logger.info("  POST /api/v2/households  🏠 NEW!")
        logger.info("  PUT  /api/v2/households/<id>  🏠 NEW!")
        logger.info("  DELETE /api/v2/households/<id>  🏠 NEW!")
        logger.info("  GET  /api/v2/households/<id>/members  🏠 NEW!")
        logger.info("  POST /api/v2/households/<id>/members  🏠 NEW!")
        logger.info("  DELETE /api/v2/households/<id>/members/<id>  🏠 NEW!")
        logger.info("  PUT  /api/v2/households/<id>/members/<id>/role  🏠 NEW!")
        logger.info("  GET  /api/v2/community/recipes  🌟 NEW!")
        logger.info("  GET  /api/v2/community/recipes/<id>  🌟 NEW!")
        logger.info("  POST /api/v2/community/recipes  🌟 NEW!")
        logger.info("  DELETE /api/v2/community/recipes/<id>  🌟 NEW!")
        logger.info("  GET  /api/v2/community/my-shares  🌟 NEW!")
        logger.info("  GET  /api/v2/community/check/<id>  🌟 NEW!")
        logger.info("  POST /api/v2/community/recipes/<id>/claim  🌟 NEW!")
        logger.info("  POST /api/v2/community/recipes/<id>/like  🌟 NEW!")
        logger.info("=" * 70)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to register v2 routes: {e}")
        logger.exception("Full error details:")
        return False


if __name__ == '__main__':
    # Test registration
    from flask import Flask
    test_app = Flask(__name__)
    success = register_v2_routes(test_app)
    print(f"\n✅ Registration {'succeeded' if success else 'failed'}!")
