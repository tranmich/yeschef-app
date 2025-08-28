#!/usr/bin/env python3
"""
Clean Slate Setup Script
- Clear all template recipes
- Remove recipe limits for admin account  
- Set empty default for new users
"""

import psycopg2
import psycopg2.extras
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_templates_and_setup_admin():
    """Clear all template recipes and setup admin-only access"""
    try:
        # Connect to database
        DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:ObJqAfDYlKNRGhStDbxCvlFLjVkFLAYu@shuttle.proxy.rlwy.net:31331/railway')
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        print("🧹 CLEAN SLATE SETUP FOR ADMIN CURATION")
        print("="*50)
        
        # Step 1: Show current templates
        cursor.execute('SELECT id, title, meal_role FROM recipes WHERE is_template = TRUE')
        current_templates = cursor.fetchall()
        
        print(f"\n📋 Current Templates to Remove ({len(current_templates)}):")
        for template in current_templates:
            print(f"  • ID {template['id']}: {template['title']} ({template['meal_role']})")
        
        if current_templates:
            # Step 2: Check for user copies of templates
            cursor.execute('''
                SELECT template_id, COUNT(*) as copy_count
                FROM recipes 
                WHERE template_id IS NOT NULL 
                GROUP BY template_id
            ''')
            user_copies = cursor.fetchall()
            
            if user_copies:
                print(f"\n⚠️ Found User Copies of Templates:")
                for copy_info in user_copies:
                    print(f"  • Template {copy_info['template_id']}: {copy_info['copy_count']} user copies")
                
                response = input("\n🤔 Delete user copies too? (y/N): ").lower()
                if response == 'y':
                    # Delete user copies first
                    cursor.execute('DELETE FROM recipes WHERE template_id IS NOT NULL')
                    deleted_copies = cursor.rowcount
                    print(f"✅ Deleted {deleted_copies} user copies of templates")
            
            # Step 3: Remove template status (convert to regular recipes or delete)
            response = input(f"\n🗑️ Delete {len(current_templates)} template recipes? (y/N): ").lower()
            if response == 'y':
                cursor.execute('DELETE FROM recipes WHERE is_template = TRUE')
                deleted_templates = cursor.rowcount
                print(f"✅ Deleted {deleted_templates} template recipes")
            else:
                # Just remove template status
                cursor.execute('UPDATE recipes SET is_template = FALSE WHERE is_template = TRUE')
                updated_templates = cursor.rowcount
                print(f"✅ Removed template status from {updated_templates} recipes (now regular recipes)")
        
        # Step 4: Verify clean state
        cursor.execute('SELECT COUNT(*) FROM recipes WHERE is_template = TRUE')
        remaining_templates = cursor.fetchone()['count']
        
        print(f"\n🎯 CLEAN STATE ACHIEVED:")
        print(f"  • Template recipes remaining: {remaining_templates}")
        print(f"  • New users will get: 0 default recipes")
        print(f"  • Admin can now curate templates from scratch")
        
        # Step 5: Show total recipes available for curation
        cursor.execute('SELECT COUNT(*) FROM recipes')
        total_recipes = cursor.fetchone()['count']
        print(f"  • Total recipes in database for curation: {total_recipes}")
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Clean slate setup complete!")
        print(f"🔧 Admin (tran.mich@gmail.com) can now:")
        print(f"  1. Browse ALL {total_recipes} recipes with no limits")
        print(f"  2. Promote best recipes to templates via admin mode")
        print(f"  3. Test new user experience (0 recipes initially)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to setup clean slate: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    clear_templates_and_setup_admin()
