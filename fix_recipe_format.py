"""
Check column types and fix recipe format
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

def check_and_fix():
    print("="*80)
    print("🔧 CHECKING AND FIXING RECIPE FORMAT")
    print("="*80)
    
    conn = get_db_connection()
    if not conn:
        print("❌ Could not connect to database")
        return
    
    try:
        cursor = conn.cursor()
        
        # Check column types
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name='recipes' 
            AND column_name IN ('ingredients', 'instructions')
        """)
        
        print("\n📊 Column Types:")
        for row in cursor.fetchall():
            print(f"   {row['column_name']}: {row['data_type']}")
        
        # Get recipe 2608
        cursor.execute("""
            SELECT id, title, ingredients, instructions
            FROM recipes 
            WHERE id = 2608
        """)
        
        recipe = cursor.fetchone()
        
        if recipe:
            print(f"\n📋 Recipe: {recipe['title']}")
            print(f"\n🔍 Current format:")
            print(f"   Ingredients: {recipe['ingredients'][:100]}...")
            print(f"   Instructions: {recipe['instructions'][:100]}...")
            
            # The data is stored as PostgreSQL array format with {} brackets
            # Need to convert to proper JSON format with [] brackets
            
            ingredients_raw = recipe['ingredients']
            instructions_raw = recipe['instructions']
            
            # Try to parse - PostgreSQL returns {} for arrays, we need []
            if ingredients_raw.startswith('{') and ingredients_raw.endswith('}'):
                # It's a PostgreSQL array - convert to JSON array format
                # Replace { with [ and } with ]
                ingredients_json = ingredients_raw.replace('{', '[', 1)
                ingredients_json = ingredients_json[::-1].replace('}', ']', 1)[::-1]
                
                try:
                    ingredients_list = json.loads(ingredients_json)
                    print(f"\n✅ Ingredients: Valid array with {len(ingredients_list)} items")
                except:
                    print(f"\n❌ Ingredients: Could not parse")
                    ingredients_list = None
            else:
                ingredients_list = None
            
            if instructions_raw.startswith('{') and instructions_raw.endswith('}'):
                instructions_json = instructions_raw.replace('{', '[', 1)
                instructions_json = instructions_json[::-1].replace('}', ']', 1)[::-1]
                
                try:
                    instructions_list = json.loads(instructions_json)
                    print(f"✅ Instructions: Valid array with {len(instructions_list)} items")
                except:
                    print(f"❌ Instructions: Could not parse")
                    instructions_list = None
            else:
                instructions_list = None
            
            if ingredients_list and instructions_list:
                print(f"\n🔧 Fixing format to proper JSON arrays...")
                
                # Update with proper JSON format
                cursor.execute("""
                    UPDATE recipes 
                    SET ingredients = %s, instructions = %s
                    WHERE id = 2608
                """, (
                    json.dumps(ingredients_list),  # Proper JSON array
                    json.dumps(instructions_list)   # Proper JSON array
                ))
                
                conn.commit()
                print("✅ Recipe format fixed!")
                
                # Verify
                cursor.execute("SELECT ingredients, instructions FROM recipes WHERE id = 2608")
                updated = cursor.fetchone()
                print(f"\n📋 Updated format:")
                print(f"   Ingredients: {updated['ingredients'][:100]}...")
                print(f"   Instructions: {updated['instructions'][:100]}...")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_and_fix()
