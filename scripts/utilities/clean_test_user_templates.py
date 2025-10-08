#!/usr/bin/env python3
"""
Script to clean existing template copies from test user during manual curation phase
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

def clean_user_template_copies(user_email):
    """Clean template copies for a specific user by email"""
    try:
        conn = get_db_connection()
        if not conn:
            print("❌ Could not connect to database")
            return
            
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # First, find the user ID
        cursor.execute('SELECT id, email FROM users WHERE email = %s', (user_email,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ User not found: {user_email}")
            conn.close()
            return
            
        user_id = user['id']
        print(f"📋 Found user: {user['email']} (ID: {user_id})")
        
        # Check what template copies exist
        cursor.execute('''
            SELECT id, title, template_id 
            FROM recipes 
            WHERE user_id = %s AND template_id IS NOT NULL
            ORDER BY title
        ''', (user_id,))
        
        template_copies = cursor.fetchall()
        
        if not template_copies:
            print(f"✅ No template copies found for user {user_email}")
            conn.close()
            return
            
        print(f"🔍 Found {len(template_copies)} template copies:")
        for recipe in template_copies:
            print(f"   - {recipe['title']} (ID: {recipe['id']}, Template: {recipe['template_id']})")
        
        # Ask for confirmation
        response = input(f"\n🗑️ Delete all {len(template_copies)} template copies? (y/N): ")
        
        if response.lower() != 'y':
            print("❌ Cancelled")
            conn.close()
            return
            
        # Delete the template copies
        template_system = TemplateRecipeSystem(lambda: get_db_connection())
        result = template_system.clean_existing_template_copies(user_id)
        
        if result['success']:
            print(f"✅ Successfully deleted {result['deleted_count']} template copies")
            print("🎯 User now has a clean slate for manual curation")
        else:
            print(f"❌ Error: {result['error']}")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧹 Template Copy Cleanup Tool")
    print("=============================")
    
    user_email = input("Enter user email to clean: ").strip()
    
    if not user_email:
        print("❌ Please provide a user email")
    else:
        clean_user_template_copies(user_email)
