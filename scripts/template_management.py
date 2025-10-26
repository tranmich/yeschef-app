#!/usr/bin/env python3
"""
Template Management System - Admin Interface for Managing Default Recipes
Allows curating which recipes become templates without hardcoding
"""

import psycopg2
import psycopg2.extras
from datetime import datetime
import logging
from flask import request, jsonify

logger = logging.getLogger(__name__)

class TemplateManager:
    def __init__(self, get_db_connection):
        self.get_db_connection = get_db_connection
    
    def get_all_recipes(self, limit=100):
        """Get all recipes that could potentially become templates"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            cursor.execute('''
                SELECT id, title, description, category, meal_role, 
                       original_author, is_template, created_at,
                       (CASE WHEN user_id IS NULL THEN 'system' ELSE 'user' END) as owner_type
                FROM recipes 
                ORDER BY created_at DESC 
                LIMIT %s
            ''', (limit,))
            
            recipes = cursor.fetchall()
            conn.close()
            return [dict(recipe) for recipe in recipes]
            
        except Exception as e:
            logger.error(f"Failed to get recipes: {e}")
            return []
    
    def promote_recipe_to_template(self, recipe_id, original_author="Me Hungie Team"):
        """Convert an existing recipe into a template"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Create a template copy of the recipe
            cursor.execute('''
                INSERT INTO recipes (
                    title, description, ingredients, instructions, category,
                    meal_role, prep_time, cook_time, servings, why_this_works,
                    source, flavor_profile, image_url,
                    is_template, user_id, original_author, created_at
                )
                SELECT 
                    title, description, ingredients, instructions, category,
                    meal_role, prep_time, cook_time, servings, why_this_works,
                    source, flavor_profile, image_url,
                    TRUE, NULL, %s, CURRENT_TIMESTAMP
                FROM recipes 
                WHERE id = %s
                RETURNING id
            ''', (original_author, recipe_id))
            
            result = cursor.fetchone()
            if result:
                template_id = result['id']
                conn.commit()
                conn.close()
                logger.info(f"✅ Recipe {recipe_id} promoted to template {template_id}")
                return template_id
            else:
                conn.close()
                return None
                
        except Exception as e:
            logger.error(f"Failed to promote recipe to template: {e}")
            return None
    
    def get_current_templates(self):
        """Get all current template recipes"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            cursor.execute('''
                SELECT id, title, description, category, meal_role,
                       original_author, created_at
                FROM recipes 
                WHERE is_template = TRUE
                ORDER BY created_at DESC
            ''')
            
            templates = cursor.fetchall()
            conn.close()
            return [dict(template) for template in templates]
            
        except Exception as e:
            logger.error(f"Failed to get templates: {e}")
            return []
    
    def remove_template(self, template_id):
        """Remove a recipe from template status (but keep the recipe)"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE recipes 
                SET is_template = FALSE
                WHERE id = %s AND is_template = TRUE
            ''', (template_id,))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                logger.info(f"✅ Template {template_id} removed from template status")
                return True
            else:
                conn.close()
                return False
                
        except Exception as e:
            logger.error(f"Failed to remove template: {e}")
            return False
    
    def get_template_usage_stats(self):
        """Get statistics about how templates are being used"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Get usage stats for each template
            cursor.execute('''
                SELECT 
                    t.id,
                    t.title,
                    t.original_author,
                    COUNT(c.id) as copy_count,
                    COUNT(DISTINCT c.user_id) as user_count
                FROM recipes t
                LEFT JOIN recipes c ON c.template_id = t.id
                WHERE t.is_template = TRUE
                GROUP BY t.id, t.title, t.original_author
                ORDER BY copy_count DESC
            ''')
            
            stats = cursor.fetchall()
            conn.close()
            return [dict(stat) for stat in stats]
            
        except Exception as e:
            logger.error(f"Failed to get template stats: {e}")
            return []

def create_template_management_endpoints(app, template_manager):
    """Add admin endpoints for template management"""
    
    @app.route('/api/admin/templates', methods=['GET'])
    def get_admin_templates():
        """Get all current templates"""
        templates = template_manager.get_current_templates()
        return {'success': True, 'data': templates}
    
    @app.route('/api/admin/recipes/candidates', methods=['GET'])
    def get_template_candidates():
        """Get recipes that could become templates"""
        limit = request.args.get('limit', 50, type=int)
        recipes = template_manager.get_all_recipes(limit)
        return {'success': True, 'data': recipes}
    
    @app.route('/api/admin/templates/promote/<recipe_id>', methods=['POST'])
    def promote_to_template(recipe_id):
        """Promote a recipe to template status"""
        data = request.get_json() or {}
        author = data.get('original_author', 'Me Hungie Team')
        
        template_id = template_manager.promote_recipe_to_template(recipe_id, author)
        if template_id:
            return {'success': True, 'template_id': template_id}
        else:
            return {'success': False, 'error': 'Failed to promote recipe'}, 500
    
    @app.route('/api/admin/templates/<template_id>', methods=['DELETE'])
    def remove_template_status(template_id):
        """Remove template status from a recipe"""
        success = template_manager.remove_template(template_id)
        if success:
            return {'success': True, 'message': 'Template status removed'}
        else:
            return {'success': False, 'error': 'Failed to remove template'}, 500
    
    @app.route('/api/admin/templates/stats', methods=['GET'])
    def get_template_usage():
        """Get usage statistics for templates"""
        stats = template_manager.get_template_usage_stats()
        return {'success': True, 'data': stats}
