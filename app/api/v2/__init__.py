# V2 API Blueprint Registration
"""
All v2 blueprints already have '/api/v2' prefix defined in their files,
so we register them directly to the app without a wrapper blueprint.
"""
from .auth import auth_bp  # ✅ NEW: Authentication endpoints
from .friends import friends_bp
from .households import households_bp
from .community import community_bp
from .meal_plans import meal_plan_bp  # ✅ Fixed: meal_plan_bp not meal_plans_bp
from .grocery_lists import grocery_list_bp  # ✅ Fixed: grocery_list_bp not grocery_lists_bp
from .recipes import recipe_bp  # ✅ Fixed: recipe_bp not recipes_bp
from .users import user_bp  # ✅ Fixed: user_bp not users_bp
from .profile import profile_bp
from .system import system_bp
# from .favorites import favorites_bp  # ❌ Removed: file doesn't exist
from .pantry import pantry_bp  # ✅ Added: was missing
from .images import image_bp  # ✅ NEW: Image serving endpoint
from .whiteboards import whiteboard_bp  # 🆕 Whiteboard API (Phase 1)
from .whiteboard_images import whiteboard_images_bp  # 🆕 Whiteboard image uploads (NoteBlock)
from .liveblocks import liveblocks_bp  # 🆕 Liveblocks authentication (Phase 3A)
from .comments import comments_bp  # 🆕 Comments API with Pusher
from .pusher_auth import pusher_auth_bp  # 🆕 Pusher presence authentication
from .activity import activity_bp  # 🆕 Activity Feed & Notifications

def register_v2_routes(app):
    """
    Register all v2 API blueprints directly to app
    Each blueprint already has '/api/v2' prefix, so no wrapper needed
    """
    # Authentication
    app.register_blueprint(auth_bp)
    
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
    # app.register_blueprint(favorites_bp)  # ❌ Disabled: file doesn't exist
    app.register_blueprint(pantry_bp)
    
    # Media features
    app.register_blueprint(image_bp)  # ✅ NEW: Image serving
    
    # Collaboration features
    app.register_blueprint(whiteboard_bp)  # 🆕 Whiteboards (Phase 1)
    app.register_blueprint(whiteboard_images_bp)  # 🆕 Whiteboard image uploads (NoteBlock)
    app.register_blueprint(liveblocks_bp)  # 🆕 Liveblocks auth (Phase 3A)
    app.register_blueprint(comments_bp)  # 🆕 Comments with Pusher
    app.register_blueprint(pusher_auth_bp)  # 🆕 Pusher presence auth
    app.register_blueprint(activity_bp)  # 🆕 Activity Feed & Notifications
    
    # System
    app.register_blueprint(system_bp)
    
    print("✅ All v2 API blueprints registered successfully")
    print("   - Authentication (login, register, logout, password reset)")
    print("   - Friends, Households, Community")
    print("   - Meal Plans, Grocery Lists, Recipes")
    print("   - Users, Profile, Favorites, Pantry, System")
    print("   - Images (optimized recipe photos)")
    print("   - Whiteboards (canvas collaboration)")
    print("   - Liveblocks (real-time collaboration auth)")
    print("   - Activity Feed (household notifications)")
    
    return friends_bp  # Return one for reference
