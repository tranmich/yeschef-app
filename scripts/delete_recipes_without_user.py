"""Delete all recipes without a user_id to clean up the database"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core_systems.recipe_importer import UniversalRecipeImporter

def delete_recipes_without_user():
    """Delete all recipes that don't have a user_id assigned"""
    try:
        importer = UniversalRecipeImporter()
        conn = importer.get_database_connection()
        cursor = conn.cursor()
        
        # First, get count of recipes to delete
        cursor.execute('SELECT COUNT(*) as count FROM recipes WHERE user_id IS NULL')
        count_to_delete = cursor.fetchone()['count']
        
        if count_to_delete == 0:
            print("\n✅ No recipes without user_id found. Database is clean!")
            conn.close()
            return
        
        print(f"\n{'='*60}")
        print(f"DATABASE CLEANUP - DELETE RECIPES WITHOUT USER_ID")
        print(f"{'='*60}")
        print(f"Recipes to delete: {count_to_delete:,}")
        print(f"{'='*60}\n")
        
        # Ask for confirmation
        response = input(f"⚠️  Are you sure you want to DELETE {count_to_delete:,} recipes? (yes/no): ")
        
        if response.lower() != 'yes':
            print("\n❌ Deletion cancelled. No changes made.")
            conn.close()
            return
        
        print("\n🗑️  Deleting recipes without user_id...")
        
        # Delete the recipes
        cursor.execute('DELETE FROM recipes WHERE user_id IS NULL')
        deleted_count = cursor.rowcount
        
        # Commit the changes
        conn.commit()
        
        # Verify deletion
        cursor.execute('SELECT COUNT(*) as count FROM recipes WHERE user_id IS NULL')
        remaining = cursor.fetchone()['count']
        
        # Get new total
        cursor.execute('SELECT COUNT(*) as total FROM recipes')
        new_total = cursor.fetchone()['total']
        
        print(f"\n{'='*60}")
        print(f"CLEANUP COMPLETE!")
        print(f"{'='*60}")
        print(f"✅ Deleted recipes:         {deleted_count:,}")
        print(f"✅ Remaining without user:  {remaining:,}")
        print(f"✅ Total recipes now:       {new_total:,}")
        print(f"{'='*60}\n")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
            conn.close()

if __name__ == '__main__':
    delete_recipes_without_user()
