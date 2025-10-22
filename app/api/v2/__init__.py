# V2 API Blueprint Registration
"""
All v2 blueprints already have '/api/v2' prefix defined in their files,
so we register them directly to the app without a wrapper blueprint.
"""
from .friends import friends_bp
from .households import households_bp
from .community import community_bp
from .meal_plans import meal_plans_bp
from .grocery_lists import grocery_lists_bp
from .recipes import recipes_bp
from .users import users_bp
from .profile import profile_bp
from .system import system_bp

def register_v2_routes(app):
    """
    Register all v2 API blueprints directly to app
    Each blueprint already has '/api/v2' prefix, so no wrapper needed
    """
    # Social features
    app.register_blueprint(friends_bp)
    app.register_blueprint(households_bp)
    app.register_blueprint(community_bp)
    
    # Core features
    app.register_blueprint(meal_plans_bp)
    app.register_blueprint(grocery_lists_bp)
    app.register_blueprint(recipes_bp)
    
    # User features
    app.register_blueprint(users_bp)
    app.register_blueprint(profile_bp)
    
    # System
    app.register_blueprint(system_bp)
    
    print("✅ All v2 API blueprints registered successfully")
    return friends_bp  # Return one for reference
