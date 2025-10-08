"""
Clean up duplicate/test recipes from database
"""
import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

def get_db_connection():
    """Get database connection"""
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        try:
            return psycopg2.connect(database_url, cursor_factory=RealDictCursor)
        except:
            # Try public URL
            public_url = database_url.replace(
                "postgres.railway.internal:5432",
                "shuttle.proxy.rlwy.net:31331"
            )
            return psycopg2.connect(public_url, cursor_factory=RealDictCursor)
    return None

def check_bbq_mushroom_duplicates():
    """Check for BBQ Mushroom Pizza duplicates"""
    print("="*80)
    print("🔍 CHECKING FOR DUPLICATE BBQ MUSHROOM PIZZA RECIPES")
    print("="*80)
    
    conn = get_db_connection()
    if not conn:
        print("❌ Could not connect to database")
        return
    
    try:
        cursor = conn.cursor()
        
        # Find all BBQ Mushroom recipes
        cursor.execute("""
            SELECT id, title, category, created_at, user_id, 
                   LENGTH(ingredients) as ing_len,
                   LENGTH(instructions) as inst_len,
                   source_url
            FROM recipes 
            WHERE title ILIKE '%bbq%mushroom%'
            ORDER BY created_at DESC
        """)
        
        recipes = cursor.fetchall()
        
        print(f"\n📊 Found {len(recipes)} BBQ Mushroom Pizza recipes:\n")
        
        for recipe in recipes:
            print(f"ID: {recipe['id']}")
            print(f"   Title: {recipe['title']}")
            print(f"   Category: {recipe['category']}")
            print(f"   Created: {recipe['created_at']}")
            print(f"   User: {recipe['user_id']}")
            print(f"   Ingredients length: {recipe['ing_len']} chars")
            print(f"   Instructions length: {recipe['inst_len']} chars")
            print(f"   Source: {recipe['source_url'] or 'None'}")
            print()
        
        if len(recipes) > 1:
            print("="*80)
            print("🧹 CLEANUP OPTIONS")
            print("="*80)
            print("\nYou have duplicate BBQ Mushroom Pizza recipes.")
            print("Would you like to:")
            print("1. Keep the most recent one")
            print("2. Keep all of them")
            print("3. Delete all test recipes")
            
            choice = input("\nEnter choice (1/2/3) or 'n' to skip: ").strip()
            
            if choice == '1' and len(recipes) > 1:
                # Keep most recent, delete others
                keep_id = recipes[0]['id']
                delete_ids = [r['id'] for r in recipes[1:]]
                
                print(f"\n✅ Keeping recipe ID {keep_id}")
                print(f"🗑️  Deleting recipe IDs: {delete_ids}")
                
                confirm = input("Confirm deletion? (yes/no): ").strip().lower()
                if confirm == 'yes':
                    cursor.execute("""
                        DELETE FROM recipes WHERE id = ANY(%s)
                    """, (delete_ids,))
                    conn.commit()
                    print(f"✅ Deleted {len(delete_ids)} duplicate recipes")
                else:
                    print("❌ Deletion cancelled")
                    
            elif choice == '3':
                # Delete all
                all_ids = [r['id'] for r in recipes]
                print(f"\n🗑️  Deleting all BBQ Mushroom Pizza recipes: {all_ids}")
                
                confirm = input("Confirm deletion? (yes/no): ").strip().lower()
                if confirm == 'yes':
                    cursor.execute("""
                        DELETE FROM recipes WHERE id = ANY(%s)
                    """, (all_ids,))
                    conn.commit()
                    print(f"✅ Deleted {len(all_ids)} recipes")
                else:
                    print("❌ Deletion cancelled")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def check_recent_youtube_imports():
    """Check recent YouTube imports"""
    print("\n" + "="*80)
    print("🎥 CHECKING RECENT YOUTUBE IMPORTS")
    print("="*80)
    
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, category, created_at, user_id,
                   LENGTH(ingredients) as ing_len,
                   LENGTH(instructions) as inst_len,
                   source_url
            FROM recipes 
            WHERE source_url LIKE '%youtube%' OR source_url LIKE '%youtu.be%'
            ORDER BY created_at DESC
            LIMIT 10
        """)
        
        recipes = cursor.fetchall()
        
        print(f"\n📊 Found {len(recipes)} recent YouTube imports:\n")
        
        for recipe in recipes:
            print(f"ID: {recipe['id']}")
            print(f"   Title: {recipe['title']}")
            print(f"   Created: {recipe['created_at']}")
            print(f"   Ingredients: {recipe['ing_len']} chars")
            print(f"   Instructions: {recipe['inst_len']} chars")
            print(f"   URL: {recipe['source_url']}")
            print()
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_bbq_mushroom_duplicates()
    check_recent_youtube_imports()
