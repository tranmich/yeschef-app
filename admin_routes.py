#!/usr/bin/env python3
"""
Admin Routes for Me Hungie - Flask Endpoints
Secure admin-only routes for database management
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def create_admin_routes(admin_system, auth_system):
    """Create admin routes blueprint"""
    admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')
    
    def admin_required(f):
        """Decorator to require admin authentication"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Check JWT authentication first
                auth_header = request.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    return jsonify({'error': 'No valid authentication token'}), 401
                
                token = auth_header.split(' ')[1]
                user_data = auth_system.validate_token(token)
                
                if not user_data['valid']:
                    return jsonify({'error': 'Invalid authentication token'}), 401
                
                # Check if user is admin
                user_email = user_data.get('email')
                if not admin_system.is_admin_user(user_email):
                    return jsonify({'error': 'Admin access required'}), 403
                
                # Add admin info to request context
                request.admin_email = user_email
                request.admin_user_id = user_data.get('user_id')
                
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"Admin auth error: {e}")
                return jsonify({'error': 'Authentication failed'}), 401
        
        return decorated_function
    
    # ========================================================================
    # PHASE 1: ANALYSIS ENDPOINTS (READ-ONLY)
    # ========================================================================
    
    @admin_bp.route('/stats', methods=['GET'])
    @admin_required
    def get_database_stats():
        """Get comprehensive database statistics"""
        try:
            stats = admin_system.get_database_stats()
            admin_system.log_admin_action(
                request.admin_email, 'view_database_stats', 'database',
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            return jsonify({'success': True, 'data': stats})
        except Exception as e:
            logger.error(f"Admin stats error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @admin_bp.route('/duplicates', methods=['GET'])
    @admin_required
    def find_duplicate_recipes():
        """Find potential duplicate recipes"""
        try:
            duplicates = admin_system.find_duplicate_recipes()
            admin_system.log_admin_action(
                request.admin_email, 'find_duplicates', 'analysis',
                ip_address=request.remote_addr
            )
            return jsonify({'success': True, 'data': duplicates})
        except Exception as e:
            logger.error(f"Admin duplicates error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @admin_bp.route('/broken-recipes', methods=['GET'])
    @admin_required
    def find_broken_recipes():
        """Find recipes with missing or invalid data"""
        try:
            broken = admin_system.find_broken_recipes()
            admin_system.log_admin_action(
                request.admin_email, 'find_broken_recipes', 'analysis',
                ip_address=request.remote_addr
            )
            return jsonify({'success': True, 'data': broken})
        except Exception as e:
            logger.error(f"Admin broken recipes error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @admin_bp.route('/template-analytics', methods=['GET'])
    @admin_required
    def get_template_analytics():
        """Get detailed template usage analytics"""
        try:
            analytics = admin_system.get_template_analytics()
            admin_system.log_admin_action(
                request.admin_email, 'view_template_analytics', 'templates',
                ip_address=request.remote_addr
            )
            return jsonify({'success': True, 'data': analytics})
        except Exception as e:
            logger.error(f"Admin template analytics error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @admin_bp.route('/recipes/<int:recipe_id>/details', methods=['GET'])
    @admin_required
    def get_recipe_admin_details(recipe_id):
        """Get single recipe with all admin metadata"""
        try:
            recipe = admin_system.get_recipe_with_metadata(recipe_id)
            if not recipe:
                return jsonify({'success': False, 'error': 'Recipe not found'}), 404
            
            admin_system.log_admin_action(
                request.admin_email, 'view_recipe_details', 'recipe', recipe_id,
                ip_address=request.remote_addr
            )
            return jsonify({'success': True, 'data': recipe})
        except Exception as e:
            logger.error(f"Admin recipe details error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ========================================================================
    # PHASE 2: SINGLE OPERATIONS (CONTROLLED RISK)
    # ========================================================================
    
    @admin_bp.route('/recipes/<int:recipe_id>/promote', methods=['POST'])
    @admin_required
    def promote_recipe_to_template(recipe_id):
        """Promote a recipe to template status"""
        try:
            data = request.get_json() or {}
            original_author = data.get('original_author', 'Me Hungie Team')
            
            result = admin_system.promote_recipe_to_template(
                recipe_id, request.admin_email, original_author
            )
            
            if result['success']:
                return jsonify(result)
            else:
                return jsonify(result), 400
                
        except Exception as e:
            logger.error(f"Admin promote recipe error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @admin_bp.route('/recipes/<int:recipe_id>/demote', methods=['POST'])
    @admin_required
    def demote_template_to_recipe(recipe_id):
        """Remove template status from a recipe"""
        try:
            result = admin_system.demote_template_to_recipe(recipe_id, request.admin_email)
            
            if result['success']:
                return jsonify(result)
            else:
                return jsonify(result), 400
                
        except Exception as e:
            logger.error(f"Admin demote template error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @admin_bp.route('/recipes/<int:recipe_id>', methods=['DELETE'])
    @admin_required
    def delete_single_recipe(recipe_id):
        """Delete a single recipe with safety checks"""
        try:
            result = admin_system.delete_single_recipe(recipe_id, request.admin_email)
            
            if result['success']:
                return jsonify(result)
            else:
                return jsonify(result), 400
                
        except Exception as e:
            logger.error(f"Admin delete recipe error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ========================================================================
    # PHASE 3: BULK OPERATIONS (HIGH RISK - WITH SAFETY)
    # ========================================================================
    
    @admin_bp.route('/recipes/bulk-delete/preview', methods=['POST'])
    @admin_required
    def preview_bulk_delete():
        """Preview what would be deleted in a bulk operation"""
        try:
            data = request.get_json()
            if not data or 'recipe_ids' not in data:
                return jsonify({'success': False, 'error': 'recipe_ids required'}), 400
            
            recipe_ids = data['recipe_ids']
            if not isinstance(recipe_ids, list) or len(recipe_ids) == 0:
                return jsonify({'success': False, 'error': 'Invalid recipe_ids'}), 400
            
            # Limit bulk operations to reasonable size
            if len(recipe_ids) > 100:
                return jsonify({'success': False, 'error': 'Maximum 100 recipes per bulk operation'}), 400
            
            preview = admin_system.preview_bulk_delete(recipe_ids)
            
            admin_system.log_admin_action(
                request.admin_email, 'preview_bulk_delete', 'bulk',
                None, {'recipe_ids': recipe_ids}, preview,
                ip_address=request.remote_addr
            )
            
            return jsonify({'success': True, 'data': preview})
            
        except Exception as e:
            logger.error(f"Admin bulk delete preview error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @admin_bp.route('/recipes/bulk-delete/execute', methods=['POST'])
    @admin_required
    def execute_bulk_delete():
        """Execute bulk delete with safety checks"""
        try:
            data = request.get_json()
            if not data or 'recipe_ids' not in data:
                return jsonify({'success': False, 'error': 'recipe_ids required'}), 400
            
            recipe_ids = data['recipe_ids']
            force_delete_templates = data.get('force_delete_templates', False)
            confirmation_text = data.get('confirmation_text', '')
            
            # Require explicit confirmation for bulk delete
            expected_confirmation = f"DELETE {len(recipe_ids)} RECIPES FROM LIVE DATABASE"
            if confirmation_text != expected_confirmation:
                return jsonify({
                    'success': False, 
                    'error': f'Confirmation required. Type: "{expected_confirmation}"'
                }), 400
            
            # Limit bulk operations
            if len(recipe_ids) > 100:
                return jsonify({'success': False, 'error': 'Maximum 100 recipes per bulk operation'}), 400
            
            result = admin_system.execute_bulk_delete(
                recipe_ids, request.admin_email, force_delete_templates
            )
            
            if result['success']:
                return jsonify(result)
            else:
                return jsonify(result), 400
                
        except Exception as e:
            logger.error(f"Admin bulk delete execute error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ========================================================================
    # AUDIT AND LOGGING
    # ========================================================================
    
    @admin_bp.route('/logs', methods=['GET'])
    @admin_required
    def get_admin_logs():
        """Get recent admin actions for audit"""
        try:
            limit = request.args.get('limit', 50, type=int)
            if limit > 200:
                limit = 200  # Maximum limit
            
            logs = admin_system.get_admin_logs(limit)
            return jsonify({'success': True, 'data': logs})
            
        except Exception as e:
            logger.error(f"Admin logs error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @admin_bp.route('/check-access', methods=['GET'])
    @admin_required
    def check_admin_access():
        """Check if current user has admin access"""
        return jsonify({
            'success': True,
            'admin': True,
            'email': request.admin_email,
            'message': 'Admin access confirmed'
        })
    
    return admin_bp
