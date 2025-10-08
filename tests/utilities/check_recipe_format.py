"""
Check how recipe 2608 is stored and returned
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import json

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

def check_recipe_format():
    print("="*80)
    print("🔍 CHECKING RECIPE 2608 FORMAT")
    print("="*80)
    
    conn = get_db_connection()
    if not conn:
        print("❌ Could not connect to database")
        return
    
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, ingredients, instructions
            FROM recipes 
            WHERE id = 2608
        """)
        
        recipe = cursor.fetchone()
        
        if recipe:
            print(f"\n📋 Recipe: {recipe['title']}\n")
            
            print("🥘 INGREDIENTS (raw from database):")
            print(f"   Type: {type(recipe['ingredients'])}")
            print(f"   Length: {len(recipe['ingredients'])} chars")
            print(f"   First 200 chars: {recipe['ingredients'][:200]}")
            
            # Try to parse as JSON
            try:
                if recipe['ingredients'].strip().startswith('['):
                    ingredients_list = json.loads(recipe['ingredients'])
                    print(f"\n   ✅ Valid JSON array with {len(ingredients_list)} items")
                    print(f"   Sample items:")
                    for i, item in enumerate(ingredients_list[:3], 1):
                        print(f"      {i}. {item}")
                else:
                    print(f"\n   ⚠️ Not JSON format - plain text")
            except json.JSONDecodeError as e:
                print(f"\n   ❌ JSON parse error: {e}")
            
            print("\n" + "-"*80)
            
            print("\n👨‍🍳 INSTRUCTIONS (raw from database):")
            print(f"   Type: {type(recipe['instructions'])}")
            print(f"   Length: {len(recipe['instructions'])} chars")
            print(f"   First 200 chars: {recipe['instructions'][:200]}")
            
            # Try to parse as JSON
            try:
                if recipe['instructions'].strip().startswith('['):
                    instructions_list = json.loads(recipe['instructions'])
                    print(f"\n   ✅ Valid JSON array with {len(instructions_list)} items")
                    print(f"   Sample steps:")
                    for i, item in enumerate(instructions_list[:3], 1):
                        print(f"      {i}. {item[:80]}...")
                else:
                    print(f"\n   ⚠️ Not JSON format - plain text")
            except json.JSONDecodeError as e:
                print(f"\n   ❌ JSON parse error: {e}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_recipe_format()
