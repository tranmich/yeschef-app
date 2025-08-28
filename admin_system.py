#!/usr/bin/env python3
"""
Admin System for Me Hungie - Live PostgreSQL Management
Phase 1: Analysis Tools (Read-Only)
Phase 2: Single Operations (Controlled Risk)  
Phase 3: Bulk Operations (High Risk - With Safety)
"""

import psycopg2
import psycopg2.extras
from datetime import datetime
import json
import logging
from flask import request, jsonify
from functools import wraps

logger = logging.getLogger(__name__)

# Admin email - hardcoded for security
ADMIN_EMAIL = "tran.mich@gmail.com"

class AdminSystem:
    def __init__(self, get_db_connection, auth_system):
        self.get_db_connection = get_db_connection
        self.auth_system = auth_system
        self.init_admin_tables()
    
    def init_admin_tables(self):
        """Initialize admin logging table"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Create admin logs table for audit trail
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admin_logs (
                    id SERIAL PRIMARY KEY,
                    admin_email TEXT NOT NULL,
                    action TEXT NOT NULL,
                    target_type TEXT NOT NULL,
                    target_id INTEGER,
                    old_data JSONB,
                    new_data JSONB,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT,
                    user_agent TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("✅ Admin system tables initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize admin tables: {e}")
    
    def is_admin_user(self, user_email):
        """Check if user is admin"""
        return user_email and user_email.lower() == ADMIN_EMAIL.lower()
    
    def log_admin_action(self, admin_email, action, target_type, target_id=None, 
                        old_data=None, new_data=None, ip_address=None, user_agent=None):
        """Log all admin actions for audit trail"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO admin_logs (
                    admin_email, action, target_type, target_id,
                    old_data, new_data, ip_address, user_agent
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                admin_email, action, target_type, target_id,
                json.dumps(old_data) if old_data else None,
                json.dumps(new_data) if new_data else None,
                ip_address, user_agent
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"📝 Admin action logged: {action} on {target_type} {target_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to log admin action: {e}")
    
    # ========================================================================
    # PHASE 1: ANALYSIS TOOLS (READ-ONLY)
    # ========================================================================
    
    def get_database_stats(self):
        """Get comprehensive database statistics"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            stats = {}
            
            # Recipe counts
            cursor.execute('SELECT COUNT(*) as total FROM recipes')
            stats['total_recipes'] = cursor.fetchone()['total']
            
            cursor.execute('SELECT COUNT(*) as count FROM recipes WHERE is_template = TRUE')
            stats['template_recipes'] = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM recipes WHERE user_id IS NOT NULL')
            stats['user_recipes'] = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(DISTINCT user_id) as count FROM recipes WHERE user_id IS NOT NULL')
            stats['users_with_recipes'] = cursor.fetchone()['count']
            
            # Template usage
            cursor.execute('SELECT COUNT(*) as count FROM recipes WHERE template_id IS NOT NULL')
            stats['template_copies'] = cursor.fetchone()['count']
            
            # Recipe quality metrics
            cursor.execute('SELECT COUNT(*) as count FROM recipes WHERE ingredients IS NULL OR ingredients = \'\'')
            stats['recipes_missing_ingredients'] = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM recipes WHERE instructions IS NULL OR instructions = \'\'')
            stats['recipes_missing_instructions'] = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM recipes WHERE title IS NULL OR title = \'\'')
            stats['recipes_missing_title'] = cursor.fetchone()['count']
            
            # Duplicates detection
            cursor.execute('''
                SELECT title, COUNT(*) as count 
                FROM recipes 
                WHERE title IS NOT NULL AND title != ''
                GROUP BY title 
                HAVING COUNT(*) > 1
                ORDER BY count DESC
                LIMIT 10
            ''')
            stats['duplicate_titles'] = [dict(row) for row in cursor.fetchall()]
            
            # Recent activity
            cursor.execute('''
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM recipes 
                WHERE created_at > CURRENT_DATE - INTERVAL '30 days'
                GROUP BY DATE(created_at)
                ORDER BY date DESC
                LIMIT 10
            ''')
            stats['recent_activity'] = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get database stats: {e}")
            return {}
    
    def find_duplicate_recipes(self, similarity_threshold=0.8):
        """Find potential duplicate recipes"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Find exact title matches
            cursor.execute('''
                SELECT title, array_agg(id) as recipe_ids, COUNT(*) as count
                FROM recipes 
                WHERE title IS NOT NULL AND title != ''
                GROUP BY title 
                HAVING COUNT(*) > 1
                ORDER BY count DESC
            ''')
            exact_matches = [dict(row) for row in cursor.fetchall()]
            
            # Find similar ingredients (basic approach)
            cursor.execute('''
                SELECT r1.id as id1, r1.title as title1,
                       r2.id as id2, r2.title as title2,
                       r1.ingredients as ingredients1,
                       r2.ingredients as ingredients2
                FROM recipes r1, recipes r2
                WHERE r1.id < r2.id 
                  AND r1.ingredients IS NOT NULL 
                  AND r2.ingredients IS NOT NULL
                  AND LENGTH(r1.ingredients) > 50
                  AND LENGTH(r2.ingredients) > 50
                  AND r1.ingredients = r2.ingredients
                LIMIT 20
            ''')
            ingredient_matches = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return {
                'exact_title_matches': exact_matches,
                'identical_ingredients': ingredient_matches,
                'total_exact_duplicates': len(exact_matches),
                'total_ingredient_duplicates': len(ingredient_matches)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to find duplicates: {e}")
            return {}
    
    def find_broken_recipes(self):
        """Find recipes with missing or invalid data"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            broken = {}
            
            # Missing essential fields
            cursor.execute('''
                SELECT id, title, 
                       CASE 
                           WHEN title IS NULL OR title = '' THEN 'missing_title'
                           WHEN ingredients IS NULL OR ingredients = '' THEN 'missing_ingredients'
                           WHEN instructions IS NULL OR instructions = '' THEN 'missing_instructions'
                           ELSE 'unknown'
                       END as issue_type
                FROM recipes 
                WHERE (title IS NULL OR title = '')
                   OR (ingredients IS NULL OR ingredients = '')
                   OR (instructions IS NULL OR instructions = '')
                ORDER BY issue_type, id
                LIMIT 50
            ''')
            broken['missing_fields'] = [dict(row) for row in cursor.fetchall()]
            
            # Orphaned template copies
            cursor.execute('''
                SELECT r.id, r.title, r.template_id
                FROM recipes r
                LEFT JOIN recipes t ON r.template_id = t.id
                WHERE r.template_id IS NOT NULL 
                  AND t.id IS NULL
            ''')
            broken['orphaned_copies'] = [dict(row) for row in cursor.fetchall()]
            
            # Invalid user references
            cursor.execute('''
                SELECT r.id, r.title, r.user_id
                FROM recipes r
                LEFT JOIN users u ON r.user_id = u.id
                WHERE r.user_id IS NOT NULL 
                  AND u.id IS NULL
            ''')
            broken['invalid_users'] = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return broken
            
        except Exception as e:
            logger.error(f"❌ Failed to find broken recipes: {e}")
            return {}
    
    def get_template_analytics(self):
        """Get detailed template usage analytics"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Template usage stats
            cursor.execute('''
                SELECT 
                    t.id,
                    t.title,
                    t.original_author,
                    t.meal_role,
                    COUNT(c.id) as copy_count,
                    COUNT(DISTINCT c.user_id) as unique_users,
                    MIN(c.created_at) as first_copy,
                    MAX(c.created_at) as last_copy
                FROM recipes t
                LEFT JOIN recipes c ON c.template_id = t.id
                WHERE t.is_template = TRUE
                GROUP BY t.id, t.title, t.original_author, t.meal_role
                ORDER BY copy_count DESC
            ''')
            template_stats = [dict(row) for row in cursor.fetchall()]
            
            # Most modified templates
            cursor.execute('''
                SELECT 
                    t.title as template_title,
                    COUNT(*) as modification_count
                FROM recipes c
                JOIN recipes t ON c.template_id = t.id
                WHERE c.template_id IS NOT NULL
                GROUP BY t.id, t.title
                ORDER BY modification_count DESC
                LIMIT 10
            ''')
            most_modified = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return {
                'template_stats': template_stats,
                'most_modified_templates': most_modified,
                'total_templates': len(template_stats)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get template analytics: {e}")
            return {}
    
    # ========================================================================
    # PHASE 2: SINGLE OPERATIONS (CONTROLLED RISK)
    # ========================================================================
    
    def get_recipe_with_metadata(self, recipe_id):
        """Get single recipe with all admin metadata"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            cursor.execute('''
                SELECT r.*,
                       u.email as owner_email,
                       t.title as template_title,
                       (SELECT COUNT(*) FROM recipes WHERE template_id = r.id) as copy_count
                FROM recipes r
                LEFT JOIN users u ON r.user_id = u.id
                LEFT JOIN recipes t ON r.template_id = t.id
                WHERE r.id = %s
            ''', (recipe_id,))
            
            recipe = cursor.fetchone()
            conn.close()
            return dict(recipe) if recipe else None
            
        except Exception as e:
            logger.error(f"❌ Failed to get recipe metadata: {e}")
            return None
    
    def promote_recipe_to_template(self, recipe_id, admin_email, original_author="Me Hungie Team"):
        """Promote a recipe to template status"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Get current recipe data for logging
            old_data = self.get_recipe_with_metadata(recipe_id)
            if not old_data:
                return {'success': False, 'error': 'Recipe not found'}
            
            # Update recipe to template status
            cursor.execute('''
                UPDATE recipes 
                SET is_template = TRUE,
                    original_author = %s,
                    user_id = NULL
                WHERE id = %s
            ''', (original_author, recipe_id))
            
            if cursor.rowcount == 0:
                conn.close()
                return {'success': False, 'error': 'Recipe not found or already a template'}
            
            conn.commit()
            conn.close()
            
            # Log the action
            new_data = {'is_template': True, 'original_author': original_author}
            self.log_admin_action(admin_email, 'promote_to_template', 'recipe', 
                                recipe_id, old_data, new_data)
            
            logger.info(f"✅ Recipe {recipe_id} promoted to template by {admin_email}")
            return {'success': True, 'message': 'Recipe promoted to template'}
            
        except Exception as e:
            logger.error(f"❌ Failed to promote recipe: {e}")
            return {'success': False, 'error': str(e)}
    
    def demote_template_to_recipe(self, recipe_id, admin_email):
        """Remove template status from a recipe"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Get current data for logging
            old_data = self.get_recipe_with_metadata(recipe_id)
            if not old_data:
                return {'success': False, 'error': 'Recipe not found'}
            
            # Check if it's actually a template
            if not old_data.get('is_template'):
                return {'success': False, 'error': 'Recipe is not a template'}
            
            # Remove template status
            cursor.execute('''
                UPDATE recipes 
                SET is_template = FALSE
                WHERE id = %s AND is_template = TRUE
            ''', (recipe_id,))
            
            if cursor.rowcount == 0:
                conn.close()
                return {'success': False, 'error': 'Recipe not found or not a template'}
            
            conn.commit()
            conn.close()
            
            # Log the action
            new_data = {'is_template': False}
            self.log_admin_action(admin_email, 'demote_from_template', 'recipe',
                                recipe_id, old_data, new_data)
            
            logger.info(f"✅ Recipe {recipe_id} demoted from template by {admin_email}")
            return {'success': True, 'message': 'Template status removed'}
            
        except Exception as e:
            logger.error(f"❌ Failed to demote template: {e}")
            return {'success': False, 'error': str(e)}
    
    def delete_single_recipe(self, recipe_id, admin_email):
        """Delete a single recipe (with safety checks)"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Get current data for logging
            old_data = self.get_recipe_with_metadata(recipe_id)
            if not old_data:
                return {'success': False, 'error': 'Recipe not found'}
            
            # Safety check: Don't delete templates with copies
            if old_data.get('is_template') and old_data.get('copy_count', 0) > 0:
                return {
                    'success': False, 
                    'error': f'Cannot delete template with {old_data["copy_count"]} user copies'
                }
            
            # Delete the recipe
            cursor.execute('DELETE FROM recipes WHERE id = %s', (recipe_id,))
            
            if cursor.rowcount == 0:
                conn.close()
                return {'success': False, 'error': 'Recipe not found'}
            
            conn.commit()
            conn.close()
            
            # Log the action
            self.log_admin_action(admin_email, 'delete_recipe', 'recipe',
                                recipe_id, old_data, None)
            
            logger.info(f"✅ Recipe {recipe_id} deleted by {admin_email}")
            return {'success': True, 'message': 'Recipe deleted successfully'}
            
        except Exception as e:
            logger.error(f"❌ Failed to delete recipe: {e}")
            return {'success': False, 'error': str(e)}
    
    # ========================================================================
    # PHASE 3: BULK OPERATIONS (HIGH RISK - WITH SAFETY)
    # ========================================================================
    
    def preview_bulk_delete(self, recipe_ids):
        """Preview what would be deleted in a bulk operation"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Get details of recipes to be deleted
            placeholders = ','.join(['%s'] * len(recipe_ids))
            cursor.execute(f'''
                SELECT r.id, r.title, r.is_template,
                       COALESCE(copy_counts.copy_count, 0) as copy_count,
                       u.email as owner_email
                FROM recipes r
                LEFT JOIN users u ON r.user_id = u.id
                LEFT JOIN (
                    SELECT template_id, COUNT(*) as copy_count
                    FROM recipes 
                    WHERE template_id IS NOT NULL
                    GROUP BY template_id
                ) copy_counts ON r.id = copy_counts.template_id
                WHERE r.id IN ({placeholders})
            ''', recipe_ids)
            
            recipes_to_delete = [dict(row) for row in cursor.fetchall()]
            
            # Safety analysis
            templates_with_copies = [r for r in recipes_to_delete if r['is_template'] and r['copy_count'] > 0]
            safe_to_delete = [r for r in recipes_to_delete if not (r['is_template'] and r['copy_count'] > 0)]
            
            conn.close()
            
            return {
                'total_selected': len(recipe_ids),
                'found_recipes': len(recipes_to_delete),
                'safe_to_delete': len(safe_to_delete),
                'blocked_templates': len(templates_with_copies),
                'recipes_to_delete': recipes_to_delete,
                'safety_warnings': templates_with_copies,
                'safe_recipes': safe_to_delete
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to preview bulk delete: {e}")
            return {'error': str(e)}
    
    def execute_bulk_delete(self, recipe_ids, admin_email, force_delete_templates=False):
        """Execute bulk delete with safety checks"""
        try:
            # First, preview the operation
            preview = self.preview_bulk_delete(recipe_ids)
            
            if 'error' in preview:
                return {'success': False, 'error': preview['error']}
            
            # Check for safety warnings
            if preview['blocked_templates'] and not force_delete_templates:
                return {
                    'success': False,
                    'error': f'Cannot delete {preview["blocked_templates"]} templates with user copies',
                    'blocked_templates': preview['safety_warnings']
                }
            
            # Execute deletion
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            deleted_count = 0
            errors = []
            
            for recipe_id in recipe_ids:
                try:
                    # Get recipe data for logging
                    old_data = self.get_recipe_with_metadata(recipe_id)
                    
                    # Delete the recipe
                    cursor.execute('DELETE FROM recipes WHERE id = %s', (recipe_id,))
                    
                    if cursor.rowcount > 0:
                        deleted_count += 1
                        # Log each deletion
                        self.log_admin_action(admin_email, 'bulk_delete_recipe', 'recipe',
                                            recipe_id, old_data, None)
                    
                except Exception as e:
                    errors.append(f"Recipe {recipe_id}: {str(e)}")
            
            conn.commit()
            conn.close()
            
            # Log the bulk operation
            self.log_admin_action(admin_email, 'bulk_delete_operation', 'bulk',
                                None, {'recipe_ids': recipe_ids}, 
                                {'deleted_count': deleted_count, 'errors': errors})
            
            logger.info(f"✅ Bulk delete completed: {deleted_count} recipes deleted by {admin_email}")
            
            return {
                'success': True,
                'deleted_count': deleted_count,
                'total_requested': len(recipe_ids),
                'errors': errors
            }
            
        except Exception as e:
            logger.error(f"❌ Failed bulk delete: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_admin_logs(self, limit=50):
        """Get recent admin actions for audit"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            cursor.execute('''
                SELECT * FROM admin_logs 
                ORDER BY timestamp DESC 
                LIMIT %s
            ''', (limit,))
            
            logs = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return logs
            
        except Exception as e:
            logger.error(f"❌ Failed to get admin logs: {e}")
            return []
