"""Check how many recipes don't have a user_id"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core_systems.recipe_importer import UniversalRecipeImporter

def check_recipes():
    """Check recipes without user_id"""
    try:
        importer = UniversalRecipeImporter()
        conn = importer.get_database_connection()
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute('SELECT COUNT(*) as total FROM recipes')
        total = cursor.fetchone()['total']
        
        # Get count without user_id
        cursor.execute('SELECT COUNT(*) as null_count FROM recipes WHERE user_id IS NULL')
        null_count = cursor.fetchone()['null_count']
        
        # Get count with user_id
        with_user = total - null_count
        
        print(f"\n{'='*60}")
        print(f"RECIPE DATABASE ANALYSIS")
        print(f"{'='*60}")
        print(f"Total recipes:              {total:,}")
        print(f"Recipes WITHOUT user_id:    {null_count:,} ({null_count/total*100:.1f}%)")
        print(f"Recipes WITH user_id:       {with_user:,} ({with_user/total*100:.1f}%)")
        print(f"{'='*60}\n")
        
        # Show sample recipes without user_id
        cursor.execute("""
            SELECT id, title, category, created_at 
            FROM recipes 
            WHERE user_id IS NULL 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        samples = cursor.fetchall()
        
        if samples:
            print("Sample recipes WITHOUT user_id:")
            print("-" * 60)
            for recipe in samples:
                print(f"  ID: {recipe['id']}")
                print(f"  Title: {recipe['title']}")
                print(f"  Category: {recipe['category']}")
                print(f"  Created: {recipe['created_at']}")
                print()
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_recipes()
