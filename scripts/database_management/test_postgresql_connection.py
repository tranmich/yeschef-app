#!/usr/bin/env python3
"""
Test PostgreSQL Connection and Recipe Data Access
Diagnose why Chat API isn't fetching recipe data on Railway
"""

import os
import sys
import psycopg2
import psycopg2.extras
from datetime import datetime

def test_postgresql_connection():
    """Test PostgreSQL connection and basic recipe queries"""
    
    print("🔍 POSTGRESQL CONNECTION DIAGNOSTIC")
    print("=" * 50)
    
    # Check environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not set!")
        print("💡 This script needs to run on Railway or with DATABASE_URL set locally")
        return False
    
    try:
        # Connect to PostgreSQL
        print("🔗 Connecting to PostgreSQL...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        print("✅ PostgreSQL connection successful!")
        
        # Test recipe data
        print("\n📊 RECIPE DATA VERIFICATION")
        print("=" * 40)
        
        # Check total recipes
        cursor.execute("SELECT COUNT(*) as count FROM recipes")
        recipe_count = cursor.fetchone()['count']
        print(f"Total Recipes: {recipe_count}")
        
        # Check sample recipes
        cursor.execute("SELECT id, title, category FROM recipes LIMIT 5")
        sample_recipes = cursor.fetchall()
        
        print("\n📋 Sample Recipes:")
        for recipe in sample_recipes:
            print(f"  {recipe['id']}: {recipe['title']} ({recipe['category']})")
        
        # Check ingredients
        cursor.execute("SELECT COUNT(*) as count FROM ingredients")
        ingredient_count = cursor.fetchone()['count']
        print(f"\nTotal Ingredients: {ingredient_count}")
        
        # Test search query (similar to what ChatAPI would use)
        print("\n🔍 Testing Search Query (like ChatAPI):")
        search_term = "chicken"
        cursor.execute("""
            SELECT r.id, r.title, r.category 
            FROM recipes r 
            WHERE r.title ILIKE %s OR r.ingredients ILIKE %s 
            LIMIT 5
        """, (f'%{search_term}%', f'%{search_term}%'))
        
        search_results = cursor.fetchall()
        print(f"Search for '{search_term}' found {len(search_results)} recipes:")
        for recipe in search_results:
            print(f"  - {recipe['title']} ({recipe['category']})")
        
        cursor.close()
        conn.close()
        
        print(f"\n✅ PostgreSQL verification complete!")
        print(f"📊 {recipe_count} recipes available")
        print(f"🧪 Search functionality working")
        
        return True
        
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

def test_chatapi_integration():
    """Test the ChatAPI integration with PostgreSQL"""
    
    print("\n🤖 TESTING CHATAPI INTEGRATION")
    print("=" * 40)
    
    try:
        # Import the search engine
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'core_systems'))
        from enhanced_recipe_suggestions import SmartRecipeSuggestionEngine
        
        # Initialize the engine
        engine = SmartRecipeSuggestionEngine()
        
        # Test a simple search
        test_query = "chicken recipes"
        print(f"Testing query: '{test_query}'")
        
        # This should use PostgreSQL if DATABASE_URL is set
        suggestions = engine.get_smart_suggestions(test_query, session_id="test_session")
        
        if suggestions and 'recipes' in suggestions:
            recipe_count = len(suggestions['recipes'])
            print(f"✅ ChatAPI returned {recipe_count} recipes")
            
            if recipe_count > 0:
                first_recipe = suggestions['recipes'][0]
                print(f"Sample recipe: {first_recipe.get('title', 'No title')}")
                return True
            else:
                print("⚠️  ChatAPI returned empty results")
                return False
        else:
            print("❌ ChatAPI returned no suggestions")
            return False
            
    except Exception as e:
        print(f"❌ ChatAPI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 POSTGRESQL & CHATAPI VERIFICATION")
    print("=" * 50)
    
    # Test 1: PostgreSQL Connection
    postgres_ok = test_postgresql_connection()
    
    # Test 2: ChatAPI Integration (only if PostgreSQL works)
    if postgres_ok:
        chatapi_ok = test_chatapi_integration()
        
        if chatapi_ok:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ PostgreSQL connection working")
            print("✅ Recipe data accessible") 
            print("✅ ChatAPI integration working")
        else:
            print("\n⚠️  CHATAPI INTEGRATION ISSUE")
            print("✅ PostgreSQL connection working")
            print("✅ Recipe data accessible")
            print("❌ ChatAPI not fetching recipes")
    else:
        print("\n❌ SETUP REQUIRED")
        print("❌ PostgreSQL connection failed")
        print("💡 Set DATABASE_URL environment variable")
