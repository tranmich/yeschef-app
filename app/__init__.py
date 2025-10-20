"""

YesChef Application Factory
Creates and configures the Flask application
"""

from flask import Flask
from flask_cors import CORS
import logging
from typing import Optional

from app.config import get_config, Config
from app.database.connection import init_database


def create_app(config_name: str = None, config_object: Config = None) -> Flask:
    """
    Application factory pattern
    Creates and configures a Flask application instance
    
    Args:
        config_name: Name of configuration to use ('development', 'testing', 'production')
        config_object: Configuration object (overrides config_name if provided)
    
    Returns:
        Configured Flask application
    
    Usage:
        # Development
        app = create_app('development')
        
        # Production
        app = create_app('production')
        
        # Testing
        app = create_app('testing')
    """
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    if config_object:
        app.config.from_object(config_object)
    else:
        config_class = get_config(config_name)
        app.config.from_object(config_class)
    
    # Set up logging
    configure_logging(app)
    
    app.logger.info("=" * 70)
    app.logger.info("🚀 YesChef Application Starting (v2 Architecture)")
    app.logger.info("=" * 70)
    app.logger.info(f"Environment: {config_name or 'auto-detected'}")
    app.logger.info(f"Debug mode: {app.config['DEBUG']}")
    app.logger.info(f"Testing mode: {app.config['TESTING']}")
    
    # Initialize extensions
    initialize_extensions(app)
    
    # Initialize database
    initialize_database(app)
    
    # Register blueprints (routes)
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    app.logger.info("=" * 70)
    app.logger.info("✅ YesChef Application initialized successfully!")
    app.logger.info("=" * 70)
    
    return app


def configure_logging(app: Flask):
    """Configure application logging"""
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    
    # Set Flask logger level
    app.logger.setLevel(getattr(logging, log_level))
    
    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(getattr(logging, log_level))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Add handler to app logger
    app.logger.addHandler(handler)
    
    app.logger.info(f"📝 Logging configured: {log_level}")


def initialize_extensions(app: Flask):
    """Initialize Flask extensions"""
    app.logger.info("🔧 Initializing extensions...")
    
    # CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    app.logger.info("  ✅ CORS configured")
    
    # Flask-Caching (we'll set this up properly in Phase 6)
    # For now, just log that it's available
    if app.config.get('CACHE_TYPE') == 'redis':
        app.logger.info("  ℹ️  Redis caching available (will configure in Phase 6)")
    else:
        app.logger.info("  ℹ️  Simple caching enabled")


def initialize_database(app: Flask):
    """Initialize database connection pool"""
    app.logger.info("🗄️  Initializing database...")
    
    try:
        database_url = app.config.get('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL not configured")
        
        # Initialize connection pool
        init_database(
            database_url=database_url,
            min_connections=1,
            max_connections=20
        )
        
        app.logger.info("  ✅ Database connection pool initialized")
        
    except Exception as e:
        app.logger.error(f"  ❌ Database initialization failed: {e}")
        raise


def register_blueprints(app: Flask):
    """
    Register application blueprints (routes)
    This is where we'll add our v2 API routes
    """
    app.logger.info("🛣️  Registering blueprints...")
    
    # Health check endpoint (always available)
    from flask import jsonify
    
    @app.route('/api/v2/health', methods=['GET'])
    def health_check():
        """Health check endpoint for v2 API"""
        return jsonify({
            'status': 'healthy',
            'version': '2.0',
            'message': 'YesChef v2 API is running'
        })
    
    app.logger.info("  ✅ Health check endpoint registered: /api/v2/health")
    
    # Register v2 API blueprints
    from app.api.v2.users import user_bp
    from app.api.v2.recipes import recipe_bp
    
    app.register_blueprint(user_bp)
    app.register_blueprint(recipe_bp)
    
    app.logger.info("  ✅ User API v2 registered: /api/v2/users")
    app.logger.info("  ✅ Recipe API v2 registered: /api/v2/recipes")


def register_error_handlers(app: Flask):
    """Register error handlers"""
    
    @app.errorhandler(404)
    def not_found(error):
        from flask import jsonify
        return jsonify({
            'success': False,
            'error': 'Resource not found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import jsonify
        app.logger.error(f"Internal server error: {error}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
    
    app.logger.info("  ✅ Error handlers registered")


# For backward compatibility with existing code
# This allows: from app import app
# But we prefer using create_app() factory
app: Optional[Flask] = None


def get_app() -> Flask:
    """
    Get or create application instance
    Useful for backward compatibility
    """
    global app
    if app is None:
        app = create_app()
    return app


if __name__ == '__main__':
    # Test application creation
    print("Testing app factory...")
    
    # Create development app
    dev_app = create_app('development')
    print(f"\n✅ Development app created")
    print(f"   Debug: {dev_app.config['DEBUG']}")
    print(f"   Routes: {len(dev_app.url_map._rules)} registered")
    
    # Test health endpoint
    with dev_app.test_client() as client:
        response = client.get('/api/v2/health')
        print(f"\n✅ Health check endpoint works!")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.get_json()}")
    
    print("\n✅ App factory tests passed!")
