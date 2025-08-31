#!/usr/bin/env python3
"""
Admin Routes for Me Hungie - Flask Endpoints
Secure admin-only routes for database management
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def create_admin_routes(admin_system, auth_system, check_authentication_func=None):
    """Create admin routes blueprint"""
    admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')
    
    def admin_required(f):
        """Decorator to require admin authentication"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                logger.info(f"🔧 Admin endpoint accessed: {request.endpoint}")
                
                # Use the passed check_authentication function
                if check_authentication_func:
                    user_id, error_response, status_code = check_authentication_func()
                else:
                    # Fallback: manual token validation
                    auth_header = request.headers.get('Authorization')
                    if not auth_header or not auth_header.startswith('Bearer '):
                        logger.warning("❌ No valid authentication token")
                        return jsonify({'error': 'No valid authentication token', 'debug': 'header_missing'}), 401
                    
                    # Import check_authentication from global scope
                    import sys
                    if 'hungie_server' in sys.modules:
                        check_auth = getattr(sys.modules['hungie_server'], 'check_authentication', None)
                        if check_auth:
                            user_id, error_response, status_code = check_auth()
                        else:
                            logger.error("❌ check_authentication function not found")
                            return jsonify({'error': 'Authentication system error', 'debug': 'check_auth_not_found'}), 500
                    else:
                        logger.error("❌ hungie_server module not found")
                        return jsonify({'error': 'Authentication system error', 'debug': 'module_not_found'}), 500
                
                if error_response:
                    logger.warning(f"❌ Authentication failed: {error_response}")
                    return error_response, status_code
                
                if not user_id:
                    logger.warning("❌ No user ID from authentication")
                    return jsonify({'error': 'Authentication failed', 'debug': 'no_user_id'}), 401
                
                logger.info(f"✅ User authenticated: {user_id}")
                
                # Get user email from database
                try:
                    conn = admin_system.get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute('SELECT email FROM users WHERE id = %s', (user_id,))
                    result = cursor.fetchone()
                    conn.close()
                    
                    if not result:
                        logger.warning(f"❌ User ID {user_id} not found in database")
                        return jsonify({'error': 'User not found', 'debug': 'user_not_found'}), 401
                    
                    # Handle both RealDictRow and tuple results
                    if hasattr(result, 'get'):
                        user_email = result['email']
                    else:
                        user_email = result[0]
                        
                    logger.info(f"👤 User email: {user_email}")
                    
                except Exception as db_error:
                    logger.error(f"❌ Database error: {db_error}")
                    return jsonify({'error': 'Database error', 'debug': 'db_error'}), 500
                
                # Check if user is admin
                is_admin = admin_system.is_admin_user(user_email)
                logger.info(f"🔧 Is admin check: {is_admin}")
                
                if not is_admin:
                    logger.warning(f"❌ Admin access denied for: {user_email}")
                    return jsonify({'error': 'Admin access required', 'debug': 'not_admin', 'user_email': user_email}), 403
                
                # Add admin info to request context
                request.admin_email = user_email
                request.admin_user_id = user_id
                
                logger.info(f"✅ Admin access granted to: {user_email}")
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"❌ Admin auth error: {e}")
                import traceback
                logger.error(f"❌ Full traceback: {traceback.format_exc()}")
                return jsonify({'error': 'Authentication failed', 'debug': 'exception', 'exception': str(e)}), 401
        
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

    @admin_bp.route('/all-recipes', methods=['GET'])
    @admin_required
    def get_all_recipes():
        """Get all recipes for browsing and management with search and filters"""
        try:
            limit = request.args.get('limit', 200, type=int)  # Increased default from 50 to 200
            offset = request.args.get('offset', 0, type=int)
            search = request.args.get('search', '').strip()
            filter_type = request.args.get('filter', 'all')
            
            if limit > 500:  # Increased max from 100 to 500
                limit = 500  # Higher limit for admin operations
            
            logger.info(f"🔧 Getting recipes: limit={limit}, offset={offset}, search='{search}', filter='{filter_type}'")
            
            conn = admin_system.get_db_connection()
            cursor = conn.cursor()
            
            # Build WHERE conditions
            where_conditions = []
            params = []
            
            # Search condition
            if search:
                where_conditions.append("""
                    (LOWER(title) LIKE LOWER(%s) 
                     OR LOWER(COALESCE(ingredients, '')) LIKE LOWER(%s)
                     OR LOWER(COALESCE(original_author, '')) LIKE LOWER(%s)
                     OR id::text LIKE %s)
                """)
                search_param = f'%{search}%'
                params.extend([search_param, search_param, search_param, f'%{search}%'])
            
            # Filter conditions
            if filter_type == 'templates':
                where_conditions.append("is_template = true")
            elif filter_type == 'copies':
                where_conditions.append("template_id IS NOT NULL")
            elif filter_type == 'standalone':
                where_conditions.append("is_template = false AND template_id IS NULL")
            
            # Combine WHERE conditions
            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)
            
            # First, let's check what columns actually exist
            try:
                cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'recipes'")
                available_columns = [row[0] for row in cursor.fetchall()]
                logger.info(f"🔧 Available columns in recipes table: {available_columns}")
            except Exception as schema_error:
                logger.warning(f"Could not check schema: {schema_error}")
                available_columns = ['id', 'title']  # Fallback to basic columns
            
            # Build query based on available columns
            base_columns = ['id', 'title']
            optional_columns = {
                'is_template': 'COALESCE(is_template, false) as is_template',
                'template_id': 'template_id',
                'user_id': 'user_id',
                'meal_role': 'COALESCE(meal_role, \'\') as meal_role',
                'original_author': 'COALESCE(original_author, \'\') as original_author',
                'prep_time': 'COALESCE(prep_time, \'\') as prep_time',
                'cook_time': 'COALESCE(cook_time, \'\') as cook_time',
                'servings': 'COALESCE(servings, \'\') as servings'
            }
            
            # Only select columns that actually exist
            select_columns = base_columns.copy()
            for col_name, col_query in optional_columns.items():
                if col_name in available_columns:
                    select_columns.append(col_query)
                else:
                    logger.info(f"🔧 Column {col_name} not found, skipping")
            
            # Build the main query
            query = f'''
                SELECT {', '.join(select_columns)}
                FROM recipes 
                {where_clause}
                ORDER BY id DESC 
                LIMIT %s OFFSET %s
            '''
            
            # Add limit and offset to params
            params.extend([limit, offset])
            
            logger.info(f"🔧 Executing query: {query}")
            logger.info(f"🔧 Query params: {params}")
            cursor.execute(query, params)
            
            recipes = cursor.fetchall()
            logger.info(f"🔧 Retrieved {len(recipes)} recipes from database")
            
            # Convert to list of dicts for JSON serialization
            recipe_list = []
            for i, recipe in enumerate(recipes):
                try:
                    if hasattr(recipe, '_asdict'):
                        recipe_dict = recipe._asdict()
                    elif hasattr(recipe, 'keys'):
                        # Handle RealDictRow
                        recipe_dict = dict(recipe)
                    else:
                        # Handle tuple format - build dict based on available columns
                        recipe_dict = {
                            'id': recipe[0],
                            'title': recipe[1] if len(recipe) > 1 else 'Untitled Recipe'
                        }
                        
                        # Add optional fields if they were selected
                        col_index = 2
                        for col_name in ['is_template', 'template_id', 'user_id', 'meal_role', 'original_author', 'prep_time', 'cook_time', 'servings']:
                            if col_name in available_columns and col_index < len(recipe):
                                recipe_dict[col_name] = recipe[col_index]
                                col_index += 1
                            else:
                                # Set default values for missing columns
                                if col_name == 'is_template':
                                    recipe_dict[col_name] = False
                                elif col_name in ['template_id', 'user_id']:
                                    recipe_dict[col_name] = None
                                else:
                                    recipe_dict[col_name] = ''
                    
                    recipe_list.append(recipe_dict)
                    
                except Exception as recipe_error:
                    logger.error(f"Error processing recipe {i}: {recipe_error}")
                    logger.error(f"Recipe data: {recipe}")
                    # Add a minimal recipe entry
                    recipe_list.append({
                        'id': recipe[0] if len(recipe) > 0 else i,
                        'title': 'Error loading recipe',
                        'is_template': False,
                        'template_id': None,
                        'user_id': None,
                        'meal_role': '',
                        'original_author': '',
                        'prep_time': '',
                        'cook_time': '',
                        'servings': ''
                    })
            
            # Get total count with same filters
            count_query = f'SELECT COUNT(*) FROM recipes {where_clause}'
            count_params = params[:-2]  # Remove limit and offset
            try:
                cursor.execute(count_query, count_params)
                total_result = cursor.fetchone()
                total_count = total_result[0] if total_result else 0
            except Exception as count_error:
                logger.error(f"Error getting total count: {count_error}")
                total_count = len(recipe_list)
            
            conn.close()
            
            logger.info(f"🔧 Successfully processed {len(recipe_list)} recipes, total: {total_count}")
            
            admin_system.log_admin_action(
                request.admin_email, 'browse_all_recipes', 'management',
                ip_address=request.remote_addr
            )
            
            return jsonify({
                'success': True, 
                'data': recipe_list,
                'total_count': total_count,
                'limit': limit,
                'offset': offset,
                'search': search,
                'filter': filter_type,
                'available_columns': available_columns  # Debug info
            })
            
        except Exception as e:
            logger.error(f"❌ Admin all recipes error: {e}")
            import traceback
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")
            return jsonify({'success': False, 'error': str(e), 'error_type': type(e).__name__}), 500
    
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
            logger.info(f"🔧 Bulk delete request data: {data}")
            
            if not data or 'recipe_ids' not in data:
                return jsonify({'success': False, 'error': 'recipe_ids required'}), 400
            
            recipe_ids = data['recipe_ids']
            logger.info(f"🔧 Recipe IDs type: {type(recipe_ids)}, value: {recipe_ids}")
            
            # Ensure recipe_ids is a list
            if isinstance(recipe_ids, (int, str)):
                recipe_ids = [recipe_ids]
            elif not isinstance(recipe_ids, list):
                return jsonify({'success': False, 'error': 'recipe_ids must be a list'}), 400
            
            force_delete_templates = data.get('force_delete_templates', False)
            confirmation_text = data.get('confirmation_text', '')
            
            # Require explicit confirmation for bulk delete - simplified to just "DELETE"
            if confirmation_text.strip().upper() != "DELETE":
                return jsonify({
                    'success': False, 
                    'error': 'Confirmation required. Type: "DELETE"'
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
