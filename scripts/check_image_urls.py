"""Check image URLs in the database"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core_systems.recipe_importer import UniversalRecipeImporter

def check_image_urls():
    """Check image URLs for recent recipes"""
    try:
        importer = UniversalRecipeImporter()
        conn = importer.get_database_connection()
        cursor = conn.cursor()
        
        # Get recent recipes with their image URLs
        cursor.execute("""
            SELECT id, title, image_url, category, imported_at
            FROM recipes 
            WHERE user_id IS NOT NULL
            ORDER BY COALESCE(imported_at, created_at) DESC 
            LIMIT 10
        """)
        recipes = cursor.fetchall()
        
        print(f"\n{'='*80}")
        print(f"RECENT RECIPES - IMAGE URL CHECK")
        print(f"{'='*80}\n")
        
        for recipe in recipes:
            print(f"ID: {recipe['id']}")
            print(f"Title: {recipe['title']}")
            print(f"Category: {recipe['category']}")
            print(f"Imported: {recipe['imported_at']}")
            
            image_url = recipe['image_url']
            if image_url:
                print(f"Image URL: {image_url[:100]}{'...' if len(image_url) > 100 else ''}")
                
                # Check format
                if image_url.startswith('http'):
                    print(f"  ✅ Format: Clean HTTP URL")
                elif image_url.startswith('/api'):
                    print(f"  ✅ Format: API path (relative)")
                elif "contentUrl" in image_url or "'url'" in image_url:
                    print(f"  ❌ Format: CORRUPTED (Python dict string)")
                else:
                    print(f"  ⚠️  Format: Unknown")
            else:
                print(f"Image URL: None/Empty")
                print(f"  ❌ No image URL")
            
            print("-" * 80)
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_image_urls()
