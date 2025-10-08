"""
Check why recipe 2608 isn't appearing in user's recipe list
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        try:
            return psycopg2.connect(database_url, cursor_factory=RealDictCursor)
        except:
            public_url = database_url.replace(
                "postgres.railway.internal:5432",
                "shuttle.proxy.rlwy.net:31331"
            )
            return psycopg2.connect(public_url, cursor_factory=RealDictCursor)
    return None

def check_recipe_2608():
    print("="*80)
    print("🔍 CHECKING RECIPE 2608")
    print("="*80)
    
    conn = get_db_connection()
    if not conn:
        print("❌ Could not connect to database")
        return
    
    try:
        cursor = conn.cursor()
        
        # Check recipe 2608
        cursor.execute("""
            SELECT id, title, category, created_at, user_id,
                   LENGTH(ingredients) as ing_len,
                   LENGTH(instructions) as inst_len,
                   source_url
            FROM recipes 
            WHERE id = 2608
        """)
        
        recipe = cursor.fetchone()
        
        if recipe:
            print(f"\n✅ Recipe 2608 EXISTS in database:\n")
            print(f"   ID: {recipe['id']}")
            print(f"   Title: {recipe['title']}")
            print(f"   Category: {recipe['category']}")
            print(f"   User ID: {recipe['user_id']} ← ⚠️ CHECK THIS!")
            print(f"   Created: {recipe['created_at']}")
            print(f"   Ingredients: {recipe['ing_len']} chars")
            print(f"   Instructions: {recipe['inst_len']} chars")
            print(f"   Source: {recipe['source_url']}")
            
            if recipe['user_id'] is None:
                print(f"\n❌ PROBLEM: user_id is NULL!")
                print(f"   This recipe won't show in user's list")
                print(f"   Need to set user_id to 11")
                
                fix = input("\n🔧 Fix this by setting user_id to 11? (yes/no): ").strip().lower()
                if fix == 'yes':
                    cursor.execute("""
                        UPDATE recipes SET user_id = 11 WHERE id = 2608
                    """)
                    conn.commit()
                    print("✅ Fixed! Recipe now belongs to user 11")
            elif recipe['user_id'] != 11:
                print(f"\n⚠️  WARNING: user_id is {recipe['user_id']}, not 11")
                print(f"   Recipe belongs to different user")
        else:
            print("\n❌ Recipe 2608 NOT FOUND in database!")
        
        # Check all recipes for user 11
        cursor.execute("""
            SELECT id, title, created_at, user_id
            FROM recipes 
            WHERE user_id = 11
            ORDER BY created_at DESC
            LIMIT 10
        """)
        
        user_recipes = cursor.fetchall()
        print(f"\n📊 User 11 has {len(user_recipes)} recent recipes:")
        for r in user_recipes:
            marker = "🆕" if r['id'] == 2608 else "  "
            print(f"{marker} ID: {r['id']} - {r['title']} ({r['created_at']})")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_recipe_2608()
