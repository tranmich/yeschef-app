#!/usr/bin/env python3
"""
Initialize Template Recipe System
Run this script to set up the default template recipes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from template_recipe_system import TemplateRecipeSystem
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection():
    """Get database connection"""
    try:
        # Railway PostgreSQL connection
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            print("✅ Using Railway PostgreSQL database")
            conn = psycopg2.connect(database_url)
            conn.cursor_factory = psycopg2.extras.RealDictCursor
            return conn
        else:
            print("❌ No DATABASE_URL found")
            return None
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def main():
    """Initialize the template system"""
    print("🚀 Initializing Template Recipe System...")
    
    # Test database connection
    conn = get_db_connection()
    if not conn:
        print("❌ Cannot proceed without database connection")
        return False
    conn.close()
    
    # Initialize template system
    template_system = TemplateRecipeSystem(get_db_connection)
    
    # Run schema migration
    print("\n📊 Setting up database schema...")
    if not template_system.initialize_schema():
        print("❌ Schema initialization failed")
        return False
    
    # Create default templates
    print("\n🍽️ Creating default template recipes...")
    if not template_system.create_default_templates():
        print("❌ Template creation failed")
        return False
    
    # Get stats
    print("\n📈 System Statistics:")
    stats = template_system.get_system_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n🎉 Template Recipe System initialized successfully!")
    print("\nℹ️ What happens next:")
    print("  1. New users will automatically get default recipes")
    print("  2. Users can edit recipes (creates personal copies)")
    print("  3. Original templates remain unchanged")
    print("  4. Frontend can use /api/user/recipes endpoint")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
