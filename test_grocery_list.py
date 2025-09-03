import psycopg2
import psycopg2.extras
import json
import sys
import os
from dotenv import load_dotenv

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

def test_grocery_list():
    """Test the grocery list generator with sample data"""
    
    try:
        # Import the grocery list generator
        from core_systems.grocery_list_generator import GroceryListGenerator
        
        print("✅ Successfully imported GroceryListGenerator")
        
        # Initialize the generator
        generator = GroceryListGenerator()
        print("✅ Successfully initialized GroceryListGenerator")
        
        # Test with some sample recipe IDs (we need to find real ones from the database)
        DATABASE_URL = os.getenv('DATABASE_URL')
        
        if DATABASE_URL:
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Get some recipe IDs to test with
            cursor.execute("SELECT id, title FROM recipes LIMIT 5")
            recipes = cursor.fetchall()
            
            if recipes:
                print(f"📋 Found {len(recipes)} recipes in database:")
                for recipe in recipes:
                    print(f"   - ID {recipe['id']}: {recipe['title']}")
                
                # Test with first 3 recipe IDs
                test_recipe_ids = [recipe['id'] for recipe in recipes[:3]]
                print(f"\n🧪 Testing grocery list generation with recipe IDs: {test_recipe_ids}")
                
                # Generate grocery list
                result = generator.generate_grocery_list_from_recipes(test_recipe_ids)
                
                print("\n📊 GROCERY LIST RESULT:")
                print(json.dumps(result, indent=2))
                
                return True
                
            else:
                print("❌ No recipes found in database")
                return False
                
        else:
            print("❌ No DATABASE_URL environment variable")
            return False
            
    except Exception as e:
        print(f"❌ Error testing grocery list: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_grocery_list()
    if success:
        print("\n🎉 Grocery list test completed successfully!")
    else:
        print("\n💥 Grocery list test failed!")
