#!/usr/bin/env python3
"""
Database Migration Utilities
Extracted from hungie_server.py to reduce file complexity
"""
import os
import logging
import psycopg2
import psycopg2.extras
from flask import jsonify
from datetime import datetime

logger = logging.getLogger(__name__)

def get_db_connection():
    """Get PostgreSQL database connection with proper error handling and fallback to public URL"""
    try:
        # Always try public URL first for Railway deployment reliability
        public_database_url = "postgresql://postgres:udQLpljdqTYmESmntwzmwDcOlBVbqlJG@shuttle.proxy.rlwy.net:31331/railway"
        logger.info("🔄 Trying reliable public DATABASE_URL first...")
        
        try:
            conn = psycopg2.connect(public_database_url)
            conn.cursor_factory = psycopg2.extras.RealDictCursor
            logger.info("✅ Connected to PostgreSQL database via public URL")
            return conn
        except Exception as public_error:
            logger.warning(f"⚠️ Public DATABASE_URL failed: {public_error}")
            
            # Fallback to environment DATABASE_URL (internal Railway URL)
            database_url = os.getenv('DATABASE_URL')
            if not database_url:
                raise Exception("DATABASE_URL environment variable not found. PostgreSQL connection required.")
            
            logger.info("🔄 Trying internal DATABASE_URL as fallback...")
            conn = psycopg2.connect(database_url)
            conn.cursor_factory = psycopg2.extras.RealDictCursor
            logger.info("✅ Connected to PostgreSQL database via internal URL")
            return conn
        
    except Exception as e:
        logger.error(f"❌ All PostgreSQL connection attempts failed: {e}")
        raise

def run_intelligence_migration():
    """Run the intelligence migration logic - DATA BACKFILL ONLY - VERSION 2.0"""
    try:
        logger.info("🤖 Starting intelligence data backfill...")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        logger.info("✅ Database connection established")
        
        # Backfill ALL recipes in production database
        logger.info("📊 Querying ALL recipes from database... [VERSION 2.0 - NO LIMITS]")
        
        # First check total count and database info
        cursor.execute("SELECT COUNT(*) FROM recipes")
        total_count = cursor.fetchone()[0]
        logger.info(f"🔢 TOTAL RECIPES IN DATABASE: {total_count}")
        
        # Check a few sample recipes to verify we're in the right database
        cursor.execute("SELECT id, title FROM recipes ORDER BY id LIMIT 5")
        sample_recipes = cursor.fetchall()
        logger.info(f"🔍 Sample recipes (first 5): {[(r['id'], r['title'][:30]) for r in sample_recipes]}")
        
        cursor.execute("SELECT id, title, description, total_time, servings, ingredients FROM recipes ORDER BY id")
        recipes = cursor.fetchall()
        
        logger.info(f"📊 Found {len(recipes)} recipes to backfill... [FULL DATASET] - Expected: {total_count}")
        
        if not recipes:
            logger.warning("⚠️ No recipes found in database!")
            return {
                'success': False,
                'error': 'No recipes found to process'
            }
        
        updated_count = 0
        for recipe in recipes:
            try:
                recipe_id = recipe['id']
                title = recipe.get('title', '')
                description = recipe.get('description', '')
                total_time = recipe.get('total_time', '')
                ingredients = recipe.get('ingredients', '')
                
                # Progress logging every 50 recipes
                if updated_count % 50 == 0 and updated_count > 0:
                    logger.info(f"🔄 Processing progress: {updated_count}/{len(recipes)} recipes completed...")
                
                # Simple meal role classification
                text = f"{title} {description or ''}".lower()
                meal_role = "dinner"  # Default
                confidence = 50
                
                if any(word in text for word in ['breakfast', 'pancake', 'oatmeal', 'morning']):
                    meal_role = "breakfast"
                    confidence = 80
                elif any(word in text for word in ['dessert', 'cake', 'cookie', 'sweet']):
                    meal_role = "dessert"
                    confidence = 90
                elif any(word in text for word in ['sauce', 'dressing', 'marinade']):
                    meal_role = "sauce"
                    confidence = 85
                elif any(word in text for word in ['salad', 'lunch', 'sandwich']):
                    meal_role = "lunch"
                    confidence = 70
                
                # Simple time parsing
                time_min = None
                if total_time:
                    import re
                    minute_match = re.search(r'(\d+)\s*m', total_time.lower())
                    hour_match = re.search(r'(\d+)\s*h', total_time.lower())
                    if minute_match:
                        time_min = int(minute_match.group(1))
                    elif hour_match:
                        time_min = int(hour_match.group(1)) * 60
                    else:
                        # Look for any number and assume minutes if < 10, hours if > 10
                        number_match = re.search(r'(\d+)', total_time)
                        if number_match:
                            num = int(number_match.group(1))
                            time_min = num if num > 10 else num * 60
                
                # Simple flags
                is_easy = time_min and time_min <= 30
                is_one_pot = 'one pot' in text or 'sheet pan' in text or 'skillet' in text
                leftover_friendly = any(word in text for word in ['stew', 'soup', 'casserole', 'curry'])
                kid_friendly = any(word in text for word in ['mild', 'simple', 'classic']) and not any(word in text for word in ['spicy', 'hot'])
                
                # Count ingredients roughly
                ingredient_count = len(ingredients.split(',')) if ingredients else 5
                steps_count = text.count('.') + text.count('\n') if description else 5
                pots_pans_count = 1 if is_one_pot else 2
                
                # Update database with detailed error handling
                try:
                    cursor.execute("""
                        UPDATE recipes 
                        SET meal_role = %s, meal_role_confidence = %s, time_min = %s,
                            steps_count = %s, pots_pans_count = %s,
                            is_easy = %s, is_one_pot = %s, leftover_friendly = %s, kid_friendly = %s
                        WHERE id = %s
                    """, (meal_role, confidence, time_min, steps_count, pots_pans_count,
                          is_easy, is_one_pot, leftover_friendly, kid_friendly, recipe_id))
                    
                    updated_count += 1
                    if updated_count <= 5:  # Log first 5 updates for debugging
                        logger.info(f"✅ Updated recipe {recipe_id}: {meal_role} (confidence: {confidence})")
                        
                except Exception as sql_error:
                    logger.error(f"❌ SQL error for recipe {recipe_id}: {sql_error}")
                    logger.error(f"   Values: meal_role={meal_role}, confidence={confidence}, time_min={time_min}")
                    logger.error(f"   Values: steps={steps_count}, pots={pots_pans_count}, easy={is_easy}")
                    # Continue processing other recipes
                    continue
                
            except Exception as e:
                logger.error(f"Error processing recipe {recipe_id}: {e}")
                continue
        
        conn.commit()
        logger.info(f"✅ Committed {updated_count} recipe updates to database")
        
        # Get statistics with error handling
        try:
            cursor.execute("SELECT COUNT(*) FROM recipes WHERE meal_role IS NOT NULL")
            classified_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM recipes WHERE is_easy = true")
            easy_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT meal_role, COUNT(*) as count FROM recipes WHERE meal_role IS NOT NULL GROUP BY meal_role")
            role_stats = cursor.fetchall()
            
            statistics = {
                'recipes_processed': len(recipes),
                'recipes_updated': updated_count,
                'total_classified': classified_count,
                'easy_recipes': easy_count,
                'meal_role_breakdown': {row['meal_role']: row['count'] for row in role_stats}
            }
            
        except Exception as stats_error:
            logger.error(f"❌ Error gathering statistics: {stats_error}")
            statistics = {
                'recipes_processed': len(recipes),
                'recipes_updated': updated_count,
                'total_in_database': len(recipes),
                'note': 'Statistics gathering failed'
            }
        
        conn.close()
        
        return {
            'success': True,
            'message': 'Intelligence migration completed successfully!',
            'statistics': statistics
        }
        
    except Exception as e:
        logger.error(f"Intelligence migration error: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def run_schema_migration_endpoint(action):
    """Admin endpoint to run database schema migrations"""
    try:
        if action == 'add_intelligence_columns':
            logger.info("🔧 Running intelligence columns schema migration...")
            
            # Embedded SQL migration (avoid file path issues in production)
            migration_sql = """
            -- Add intelligence fields to existing recipes table
            ALTER TABLE recipes 
            ADD COLUMN IF NOT EXISTS meal_role TEXT,
            ADD COLUMN IF NOT EXISTS meal_role_confidence INTEGER DEFAULT 0,
            ADD COLUMN IF NOT EXISTS time_min INTEGER,
            ADD COLUMN IF NOT EXISTS steps_count INTEGER,
            ADD COLUMN IF NOT EXISTS pots_pans_count INTEGER DEFAULT 1,
            ADD COLUMN IF NOT EXISTS is_easy BOOLEAN DEFAULT FALSE,
            ADD COLUMN IF NOT EXISTS is_one_pot BOOLEAN DEFAULT FALSE,
            ADD COLUMN IF NOT EXISTS leftover_friendly BOOLEAN DEFAULT FALSE,
            ADD COLUMN IF NOT EXISTS kid_friendly BOOLEAN DEFAULT FALSE;

            -- Performance index for intelligent filtering
            CREATE INDEX IF NOT EXISTS idx_recipes_intelligence 
            ON recipes(meal_role, is_easy, is_one_pot, time_min);

            -- Index for pantry-first searches (future enhancement)
            CREATE INDEX IF NOT EXISTS idx_recipes_time_difficulty 
            ON recipes(time_min, is_easy) WHERE time_min IS NOT NULL;
            """
            
            # Execute migration
            conn = get_db_connection()
            cursor = conn.cursor()
            
            try:
                # Split and execute each statement
                statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]
                
                for stmt in statements:
                    if stmt.strip():
                        cursor.execute(stmt)
                        logger.info(f"✅ Executed: {stmt[:100]}...")
                
                conn.commit()
                conn.close()
                
                logger.info("✅ Intelligence columns schema migration completed successfully")
                return {
                    'success': True,
                    'message': 'Intelligence columns added successfully',
                    'statements_executed': len(statements)
                }
                
            except Exception as e:
                conn.rollback()
                conn.close()
                logger.error(f"❌ Schema migration failed: {e}")
                return {
                    'success': False,
                    'error': f'Schema migration failed: {str(e)}'
                }
        
        else:
            return {
                'success': False,
                'error': 'Invalid action. Use action=add_intelligence_columns'
            }
            
    except Exception as e:
        logger.error(f"❌ Schema migration endpoint error: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def add_sample_recipes():
    """Admin endpoint to add sample recipes to PostgreSQL database"""
    try:
        logger.info("🚀 Starting sample recipe addition to PostgreSQL")
        
        # Check database connection
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            return {
                'success': False,
                'error': 'PostgreSQL DATABASE_URL not available'
            }
        
        # Sample recipes to add
        sample_recipes = [
            {
                'title': 'Classic Chicken Parmesan',
                'description': 'Crispy breaded chicken cutlets topped with marinara sauce and melted mozzarella cheese. Servings: 4 | Total time: 45 minutes',
                'ingredients': '4 boneless chicken breasts, 1 cup breadcrumbs, 1 cup marinara sauce, 1 cup mozzarella cheese, 2 eggs, flour for dredging, olive oil, salt, pepper',
                'instructions': '1. Pound chicken to 1/4 inch thickness. 2. Set up breading station with flour, beaten eggs, and breadcrumbs. 3. Bread chicken cutlets. 4. Pan fry until golden brown. 5. Top with marinara and cheese. 6. Bake until cheese melts.',
                'source': 'Recipe Collection | Chapter: Main Dishes',
                'category': 'Main Course'
            },
            {
                'title': 'Beef Stroganoff',
                'description': 'Tender beef strips in a creamy mushroom sauce served over egg noodles. Servings: 6 | Total time: 30 minutes',
                'ingredients': '1 lb beef sirloin, 8 oz mushrooms, 1 cup sour cream, 2 cups beef broth, 1 onion, 2 tbsp flour, egg noodles, butter, salt, pepper',
                'instructions': '1. Slice beef into strips. 2. Sauté onions and mushrooms. 3. Brown beef strips. 4. Add flour and cook 1 minute. 5. Add broth and simmer. 6. Stir in sour cream. 7. Serve over noodles.',
                'source': 'Recipe Collection | Chapter: Comfort Food',
                'category': 'Main Course'
            },
            {
                'title': 'Chocolate Chip Cookies',
                'description': 'Classic homemade chocolate chip cookies with crispy edges and chewy centers. Servings: 24 cookies | Total time: 25 minutes',
                'ingredients': '2 1/4 cups flour, 1 tsp baking soda, 1 cup butter, 3/4 cup brown sugar, 1/2 cup white sugar, 2 eggs, 2 tsp vanilla, 2 cups chocolate chips',
                'instructions': '1. Preheat oven to 375°F. 2. Mix dry ingredients. 3. Cream butter and sugars. 4. Add eggs and vanilla. 5. Combine wet and dry ingredients. 6. Stir in chocolate chips. 7. Drop onto baking sheets. 8. Bake 9-11 minutes.',
                'source': 'Recipe Collection | Chapter: Desserts',
                'category': 'Dessert'
            }
        ]
        
        # Insert recipes into PostgreSQL
        conn = get_db_connection()
        cursor = conn.cursor()
        
        inserted_count = 0
        for recipe_data in sample_recipes:
            try:
                cursor.execute("""
                    INSERT INTO recipes (title, description, ingredients, instructions, source, category, created_at)
                    VALUES (%(title)s, %(description)s, %(ingredients)s, %(instructions)s, %(source)s, %(category)s, NOW())
                    RETURNING id
                """, recipe_data)
                
                new_id = cursor.fetchone()[0]
                inserted_count += 1
                logger.info(f"✅ Inserted recipe: {recipe_data['title']} (ID: {new_id})")
                
            except Exception as e:
                logger.error(f"❌ Error inserting recipe {recipe_data['title']}: {e}")
        
        conn.commit()
        conn.close()
        
        # Verify the migration
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM recipes")
        total_recipes = cursor.fetchone()[0]
        conn.close()
        
        return {
            'success': True,
            'message': f'Sample recipes added successfully',
            'recipes_inserted': inserted_count,
            'total_recipes': total_recipes
        }
        
    except Exception as e:
        logger.error(f"❌ Migration error: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def check_database_info():
    """Diagnostic endpoint to check database connection and content"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get database stats
        cursor.execute("SELECT COUNT(*) FROM recipes")
        total_recipes = cursor.fetchone()[0]
        
        # Get sample data
        cursor.execute("SELECT id, title FROM recipes ORDER BY id LIMIT 10")
        sample_recipes = cursor.fetchall()
        
        # Check if intelligence columns exist
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'recipes' 
            AND column_name IN ('meal_role', 'is_easy', 'time_min')
        """)
        intelligence_columns = [row['column_name'] for row in cursor.fetchall()]
        
        # Get database connection info (sanitized)
        database_url = os.getenv('DATABASE_URL', 'NOT_SET')
        db_info = 'PostgreSQL' if database_url.startswith('postgres') else 'Unknown'
        
        conn.close()
        
        return {
            'success': True,
            'database_type': db_info,
            'total_recipes': total_recipes,
            'intelligence_columns_exist': intelligence_columns,
            'sample_recipes': [{'id': r['id'], 'title': r['title'][:50]} for r in sample_recipes],
            'database_url_prefix': database_url[:30] + '...' if len(database_url) > 30 else database_url
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'database_url_set': 'DATABASE_URL' in os.environ
        }
