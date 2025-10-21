# V2 API Blueprint Registration
from flask import Blueprint
from .friends import friends_bp
from .households import households_bp
from .community import community_bp

def register_v2_routes(app):
    v2_bp = Blueprint('v2', __name__, url_prefix='/api/v2')
    v2_bp.register_blueprint(friends_bp)
    v2_bp.register_blueprint(households_bp)
    v2_bp.register_blueprint(community_bp)
    app.register_blueprint(v2_bp)
    return v2_bp
