#!/usr/bin/env python3
"""
Template Recipe System for Hungie
Handles default recipes for new users with copy-on-write editing
"""

import psycopg2
import psycopg2.extras
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TemplateRecipeSystem:
    def __init__(self, get_db_connection):
        self.get_db_connection = get_db_connection
    
    def initialize_schema(self):
        """Add template system columns to recipes table"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            logger.info("🔧 Adding template system columns to recipes table...")
            
            # Add columns for template system
            schema_updates = [
                "ALTER TABLE recipes ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id)",
                "ALTER TABLE recipes ADD COLUMN IF NOT EXISTS is_template BOOLEAN DEFAULT FALSE", 
                "ALTER TABLE recipes ADD COLUMN IF NOT EXISTS template_id INTEGER REFERENCES recipes(id)",
                "ALTER TABLE recipes ADD COLUMN IF NOT EXISTS original_author TEXT",
                "ALTER TABLE recipes ADD COLUMN IF NOT EXISTS meal_role TEXT",
                "ALTER TABLE recipes ADD COLUMN IF NOT EXISTS prep_time TEXT",
                "ALTER TABLE recipes ADD COLUMN IF NOT EXISTS cook_time TEXT",
                "ALTER TABLE recipes ADD COLUMN IF NOT EXISTS source_url TEXT",
                "ALTER TABLE recipes ADD COLUMN IF NOT EXISTS imported_at TIMESTAMP",
                "ALTER TABLE recipes ADD COLUMN IF NOT EXISTS confidence DECIMAL(3,2)"
            ]
            
            for update in schema_updates:
                try:
                    cursor.execute(update)
                    logger.info(f"✅ Schema update: {update}")
                except psycopg2.errors.DuplicateColumn:
                    logger.info(f"📋 Column already exists: {update}")
                except Exception as e:
                    logger.warning(f"⚠️ Schema update failed: {e}")
            
            # Create indexes for performance
            index_updates = [
                "CREATE INDEX IF NOT EXISTS idx_recipes_user_id ON recipes(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_recipes_is_template ON recipes(is_template)",
                "CREATE INDEX IF NOT EXISTS idx_recipes_template_id ON recipes(template_id)",
                "CREATE INDEX IF NOT EXISTS idx_recipes_meal_role ON recipes(meal_role)"
            ]
            
            for index in index_updates:
                try:
                    cursor.execute(index)
                    logger.info(f"✅ Index created: {index}")
                except Exception as e:
                    logger.warning(f"⚠️ Index creation failed: {e}")
            
            conn.commit()
            conn.close()
            logger.info("🎉 Template system schema initialized successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize template schema: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return False
    
    def create_default_templates(self):
        """Create a curated collection of default recipes for new users"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            logger.info("🍽️ Creating default template recipes...")
            
            # Default recipes that represent good home cooking
            default_recipes = [
                {
                    "title": "Perfect Scrambled Eggs",
                    "description": "Creamy, restaurant-quality scrambled eggs that are simple to master",
                    "ingredients": "3 large eggs\n2 tablespoons butter\n2 tablespoons heavy cream\nSalt and pepper to taste\nFresh chives for garnish",
                    "instructions": "1. Crack eggs into a bowl and whisk until well combined\n2. Heat butter in a non-stick pan over medium-low heat\n3. Add eggs and stir constantly with a rubber spatula\n4. When eggs start to set, add cream and continue stirring\n5. Remove from heat when still slightly wet (they'll continue cooking)\n6. Season with salt, pepper, and garnish with chives",
                    "category": "Breakfast",
                    "meal_role": "breakfast",
                    "prep_time": "5 minutes",
                    "cook_time": "5 minutes",
                    "servings": "2",
                    "original_author": "Me Hungie Team",
                    "why_this_works": "Low heat and constant stirring create silky, creamy eggs. The cream adds richness while removing from heat prevents overcooking."
                },
                {
                    "title": "Classic Caesar Salad",
                    "description": "Fresh, crisp romaine with homemade Caesar dressing",
                    "ingredients": "2 heads romaine lettuce, chopped\n1/2 cup parmesan cheese, grated\n1/4 cup croutons\n\nFor dressing:\n3 anchovy fillets\n2 garlic cloves\n1 egg yolk\n2 tablespoons lemon juice\n1/2 cup olive oil\nSalt and pepper",
                    "instructions": "1. Make dressing: mash anchovies and garlic into a paste\n2. Whisk in egg yolk and lemon juice\n3. Slowly drizzle in olive oil while whisking\n4. Season with salt and pepper\n5. Toss romaine with dressing\n6. Top with parmesan and croutons",
                    "category": "Salad",
                    "meal_role": "lunch",
                    "prep_time": "15 minutes",
                    "cook_time": "0 minutes",
                    "servings": "4",
                    "original_author": "Me Hungie Team",
                    "why_this_works": "Fresh ingredients and proper emulsion technique create the classic tangy, creamy Caesar flavor."
                },
                {
                    "title": "One-Pan Lemon Herb Chicken",
                    "description": "Juicy chicken thighs with roasted vegetables in a bright lemon sauce",
                    "ingredients": "6 chicken thighs, bone-in\n1 lb baby potatoes, halved\n1 lb asparagus, trimmed\n3 lemons, sliced\n4 garlic cloves, minced\n2 tablespoons olive oil\n1 tablespoon fresh thyme\n1 tablespoon fresh rosemary\nSalt and pepper",
                    "instructions": "1. Preheat oven to 425°F\n2. Season chicken with salt, pepper, and herbs\n3. Heat olive oil in large oven-safe pan\n4. Sear chicken skin-side down until golden, flip\n5. Add potatoes and garlic around chicken\n6. Roast 25 minutes, add asparagus and lemon slices\n7. Roast 10-15 minutes until chicken is cooked through\n8. Rest 5 minutes before serving",
                    "category": "Main Course",
                    "meal_role": "dinner",
                    "prep_time": "15 minutes",
                    "cook_time": "45 minutes",
                    "servings": "6",
                    "original_author": "Me Hungie Team",
                    "why_this_works": "High heat creates crispy skin while vegetables cook in the flavorful chicken drippings. Lemon adds brightness to balance the rich flavors."
                },
                {
                    "title": "Classic Chocolate Chip Cookies",
                    "description": "Perfectly chewy cookies with crispy edges and soft centers",
                    "ingredients": "2 1/4 cups all-purpose flour\n1 tsp baking soda\n1 tsp salt\n1 cup butter, softened\n3/4 cup brown sugar\n3/4 cup white sugar\n2 large eggs\n2 tsp vanilla extract\n2 cups chocolate chips",
                    "instructions": "1. Preheat oven to 375°F\n2. Mix flour, baking soda, and salt in a bowl\n3. Cream butter and both sugars until fluffy\n4. Beat in eggs and vanilla\n5. Gradually add flour mixture\n6. Stir in chocolate chips\n7. Drop rounded tablespoons on baking sheet\n8. Bake 9-11 minutes until golden brown\n9. Cool on baking sheet 5 minutes before transferring",
                    "category": "Dessert",
                    "meal_role": "dessert",
                    "prep_time": "15 minutes",
                    "cook_time": "11 minutes",
                    "servings": "24 cookies",
                    "original_author": "Me Hungie Team",
                    "why_this_works": "The combination of brown and white sugar creates the perfect texture, while slightly underbaking keeps centers soft."
                },
                {
                    "title": "Quick Tomato Basil Pasta",
                    "description": "Fresh, simple pasta that comes together in 20 minutes",
                    "ingredients": "1 lb spaghetti\n4 large tomatoes, diced\n4 garlic cloves, minced\n1/4 cup olive oil\n1/2 cup fresh basil, chopped\n1/2 cup parmesan cheese\nSalt and pepper\nRed pepper flakes (optional)",
                    "instructions": "1. Cook pasta according to package directions\n2. Heat olive oil in large pan\n3. Add garlic and cook 30 seconds until fragrant\n4. Add tomatoes, season with salt and pepper\n5. Cook 5-7 minutes until tomatoes break down\n6. Add drained pasta to sauce\n7. Toss with basil and parmesan\n8. Serve immediately with extra cheese",
                    "category": "Main Course",
                    "meal_role": "dinner",
                    "prep_time": "10 minutes",
                    "cook_time": "15 minutes",
                    "servings": "4",
                    "original_author": "Me Hungie Team",
                    "why_this_works": "Fresh tomatoes create a light, bright sauce while the pasta water helps bind everything together."
                }
            ]
            
            for recipe in default_recipes:
                cursor.execute('''
                    INSERT INTO recipes (
                        title, description, ingredients, instructions, category, 
                        meal_role, prep_time, cook_time, servings, original_author,
                        why_this_works, is_template, user_id, created_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    ) ON CONFLICT DO NOTHING
                ''', (
                    recipe['title'], recipe['description'], recipe['ingredients'],
                    recipe['instructions'], recipe['category'], recipe['meal_role'],
                    recipe['prep_time'], recipe['cook_time'], recipe['servings'],
                    recipe['original_author'], recipe['why_this_works'],
                    True, None, datetime.now()  # is_template=True, user_id=None (system owned)
                ))
            
            conn.commit()
            conn.close()
            logger.info(f"🎉 Created {len(default_recipes)} default template recipes!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create default templates: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return False
    
    def copy_templates_for_new_user(self, user_id):
        """Copy all template recipes for a new user (Admin Curation Mode)"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            logger.info(f"📋 Copying template recipes for user {user_id}...")
            
            # Get all template recipes (will be empty during admin curation phase)
            cursor.execute('''
                SELECT * FROM recipes WHERE is_template = TRUE
            ''')
            templates = cursor.fetchall()
            
            if not templates:
                logger.info(f"🎯 No template recipes found - admin curation mode active")
                logger.info(f"✅ User {user_id} starts with empty recipe collection")
                conn.close()
                return 0
            
            copied_count = 0
            for template in templates:
                # Create user copy of template
                cursor.execute('''
                    INSERT INTO recipes (
                        title, description, ingredients, instructions, category,
                        meal_role, prep_time, cook_time, servings, original_author,
                        why_this_works, source, flavor_profile, image_url,
                        is_template, template_id, user_id, created_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                ''', (
                    template['title'], template['description'], template['ingredients'],
                    template['instructions'], template['category'], template['meal_role'],
                    template['prep_time'], template['cook_time'], template['servings'],
                    template['original_author'], template['why_this_works'],
                    template.get('source'), template.get('flavor_profile'), 
                    template.get('image_url'),
                    False, template['id'], user_id, datetime.now()  # User copy
                ))
                copied_count += 1
            
            conn.commit()
            conn.close()
            logger.info(f"🎉 Copied {copied_count} template recipes for user {user_id}!")
            return copied_count
            
        except Exception as e:
            logger.error(f"❌ Failed to copy templates for user {user_id}: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return 0
    
    def get_user_recipes(self, user_id, include_templates=True):
        """Get all recipes for a user (their personal copies + any they created)"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            if include_templates:
                # Get user's personal recipes (copies of templates + original creations)
                cursor.execute('''
                    SELECT r.*, 
                           CASE WHEN r.template_id IS NOT NULL THEN 'template_copy' ELSE 'original' END as recipe_type,
                           t.title as template_title
                    FROM recipes r
                    LEFT JOIN recipes t ON r.template_id = t.id
                    WHERE r.user_id = %s AND r.is_template = FALSE
                    ORDER BY r.created_at DESC
                ''', (user_id,))
            else:
                # Get only user's original recipes (not copies of templates)
                cursor.execute('''
                    SELECT r.*, 'original' as recipe_type, NULL as template_title
                    FROM recipes r
                    WHERE r.user_id = %s AND r.is_template = FALSE AND r.template_id IS NULL
                    ORDER BY r.created_at DESC
                ''', (user_id,))
            
            recipes = cursor.fetchall()
            conn.close()
            
            # Convert to list of dicts for JSON serialization
            return [dict(recipe) for recipe in recipes]
            
        except Exception as e:
            logger.error(f"❌ Failed to get user recipes: {e}")
            return []
    
    def copy_template_on_edit(self, user_id, recipe_id):
        """
        When user edits a template recipe, create their personal copy
        Returns the new recipe ID for the personal copy
        """
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Check if this is already a user's personal recipe
            cursor.execute('''
                SELECT * FROM recipes WHERE id = %s AND user_id = %s
            ''', (recipe_id, user_id))
            
            existing_recipe = cursor.fetchone()
            if existing_recipe:
                # Already user's recipe, no need to copy
                conn.close()
                return recipe_id
            
            # Get the template recipe
            cursor.execute('''
                SELECT * FROM recipes WHERE id = %s AND is_template = TRUE
            ''', (recipe_id,))
            
            template = cursor.fetchone()
            if not template:
                logger.warning(f"⚠️ Recipe {recipe_id} is not a template")
                conn.close()
                return None
            
            # Create user's personal copy
            cursor.execute('''
                INSERT INTO recipes (
                    title, description, ingredients, instructions, category,
                    meal_role, prep_time, cook_time, servings, original_author,
                    why_this_works, source, flavor_profile, image_url,
                    is_template, template_id, user_id, created_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) RETURNING id
            ''', (
                template['title'], template['description'], template['ingredients'],
                template['instructions'], template['category'], template['meal_role'],
                template['prep_time'], template['cook_time'], template['servings'],
                template['original_author'], template['why_this_works'],
                template.get('source'), template.get('flavor_profile'), 
                template.get('image_url'),
                False, template['id'], user_id, datetime.now()
            ))
            
            new_recipe_id = cursor.fetchone()['id']
            conn.commit()
            conn.close()
            
            logger.info(f"📋 Created personal copy {new_recipe_id} of template {recipe_id} for user {user_id}")
            return new_recipe_id
            
        except Exception as e:
            logger.error(f"❌ Failed to copy template on edit: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return None
    
    def get_system_stats(self):
        """Get statistics about the template system"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            stats = {}
            
            # Count templates
            cursor.execute('SELECT COUNT(*) as count FROM recipes WHERE is_template = TRUE')
            stats['template_count'] = cursor.fetchone()['count']
            
            # Count user recipes
            cursor.execute('SELECT COUNT(*) as count FROM recipes WHERE is_template = FALSE AND user_id IS NOT NULL')
            stats['user_recipe_count'] = cursor.fetchone()['count']
            
            # Count template copies
            cursor.execute('SELECT COUNT(*) as count FROM recipes WHERE template_id IS NOT NULL')
            stats['template_copy_count'] = cursor.fetchone()['count']
            
            # Count users with recipes
            cursor.execute('SELECT COUNT(DISTINCT user_id) as count FROM recipes WHERE user_id IS NOT NULL')
            stats['users_with_recipes'] = cursor.fetchone()['count']
            
            conn.close()
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get system stats: {e}")
            return {}
