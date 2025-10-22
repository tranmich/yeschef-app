# V2 API Blueprint Registration
"""
All v2 blueprints already have '/api/v2' prefix defined in their files,
so we register them directly to the app without a wrapper blueprint.
"""
from .friends import friends_bp
from .households import households_bp
from .community import community_bp
from .meal_plans import meal_plan_bp  # ✅ Fixed: meal_plan_bp not meal_plans_bp
from .grocery_lists import grocery_list_bp  # ✅ Fixed: grocery_list_bp not grocery_lists_bp
from .recipes import recipe_bp  # ✅ Fixed: recipe_bp not recipes_bp
from .users import user_bp  # ✅ Fixed: user_bp not users_bp
from .profile import profile_bp
from .system import system_bp
from .favorites import favorites_bp  # ✅ Added: was missing
from .pantry import pantry_bp  # ✅ Added: was missing

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
    app.register_blueprint(meal_plan_bp)
    app.register_blueprint(grocery_list_bp)
    app.register_blueprint(recipe_bp)
    
    # User features
    app.register_blueprint(user_bp)
    app.register_blueprint(profile_bp)
    
    # Additional features
    app.register_blueprint(favorites_bp)
    app.register_blueprint(pantry_bp)
    
    # System
    app.register_blueprint(system_bp)
    
    print("✅ All v2 API blueprints registered successfully")
    print("   - Friends, Households, Community")
    print("   - Meal Plans, Grocery Lists, Recipes")
    print("   - Users, Profile, Favorites, Pantry, System")
    
    return friends_bp  # Return one for reference
