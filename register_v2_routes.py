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
        
        # Register v2 blueprints
        from app.api.v2.users import user_bp
        from app.api.v2.recipes import recipe_bp
        
        app.register_blueprint(user_bp)
        app.register_blueprint(recipe_bp)
        
        logger.info("  ✅ User API v2 registered: /api/v2/users")
        logger.info("  ✅ Recipe API v2 registered: /api/v2/recipes")
        
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
