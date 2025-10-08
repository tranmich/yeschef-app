#!/usr/bin/env python3
"""
Script to manually copy current templates to a specific test user
"""

import psycopg2
import psycopg2.extras
import logging
from template_recipe_system import TemplateRecipeSystem

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Get database connection using the same settings as the main app"""
    try:
        # Try PostgreSQL first (production/Heroku)
        import os
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            conn = psycopg2.connect(database_url, sslmode='require')
            return conn
        else:
            # Local PostgreSQL
            conn = psycopg2.connect(
                host="localhost",
                database="hungie_db",
                user="postgres",
                password="your_password"  # Update this
            )
            return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        return None

def copy_templates_to_test_user(user_email):
    """Manually copy current templates to a test user"""
    try:
        conn = get_db_connection()
        if not conn:
            print("❌ Could not connect to database")
            return
            
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Find the user
        cursor.execute('SELECT id, email FROM users WHERE email = %s', (user_email,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ User not found: {user_email}")
            conn.close()
            return
            
        user_id = user['id']
        print(f"📋 Found user: {user['email']} (ID: {user_id})")
        
        # Get current templates
        cursor.execute('''
            SELECT id, title, description, ingredients, instructions, 
                   cooking_time, difficulty, cuisine_type, dietary_tags, 
                   meal_type, servings, created_at
            FROM recipes 
            WHERE is_template = true
            ORDER BY created_at ASC
        ''')
        
        templates = cursor.fetchall()
        
        if not templates:
            print("❌ No templates found in the system")
            conn.close()
            return
            
        print(f"🔍 Found {len(templates)} template recipes:")
        for template in templates:
            print(f"   - {template['title']}")
        
        # Check if user already has copies
        cursor.execute('''
            SELECT COUNT(*) as count FROM recipes 
            WHERE user_id = %s AND template_id IS NOT NULL
        ''', (user_id,))
        
        existing_count = cursor.fetchone()['count']
        if existing_count > 0:
            print(f"⚠️ User already has {existing_count} template copies")
            response = input("🗑️ Delete existing copies first? (y/N): ")
            if response.lower() == 'y':
                cursor.execute('DELETE FROM recipes WHERE user_id = %s AND template_id IS NOT NULL', (user_id,))
                print(f"✅ Deleted {cursor.rowcount} existing template copies")
        
        # Copy each template
        copied_count = 0
        for template in templates:
            try:
                cursor.execute('''
                    INSERT INTO recipes (
                        title, description, ingredients, instructions,
                        cooking_time, difficulty, cuisine_type, dietary_tags,
                        meal_type, servings, user_id, template_id, is_template,
                        created_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
                    )
                ''', (
                    template['title'],
                    template['description'], 
                    template['ingredients'],
                    template['instructions'],
                    template['cooking_time'],
                    template['difficulty'],
                    template['cuisine_type'],
                    template['dietary_tags'],
                    template['meal_type'],
                    template['servings'],
                    user_id,
                    template['id'],  # Reference to original template
                    False  # User copy, not a template
                ))
                copied_count += 1
                print(f"   ✅ Copied: {template['title']}")
                
            except Exception as e:
                print(f"   ❌ Failed to copy {template['title']}: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"\n🎉 Successfully copied {copied_count} templates to user {user_email}")
        print("🎯 User should now see the template recipes in their collection!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("📋 Template Copy Tool for Testing")
    print("=================================")
    
    user_email = input("Enter test user email: ").strip()
    
    if not user_email:
        print("❌ Please provide a user email")
    else:
        copy_templates_to_test_user(user_email)
