#!/usr/bin/env python3
"""
ChatAPI Database Connection Diagnostic
Tests the complete chain from ChatAPI to PostgreSQL
"""

import os
import sys
import traceback

def diagnose_chatapi_database_connection():
    """Comprehensive diagnosis of ChatAPI database connectivity"""
    
    print("🔍 CHATAPI DATABASE CONNECTION DIAGNOSIS")
    print("=" * 60)
    
    # Step 1: Check environment variables
    print("1️⃣ ENVIRONMENT CHECK")
    print("-" * 30)
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        print("✅ DATABASE_URL is set")
        print(f"   Preview: {database_url[:50]}...")
    else:
        print("❌ DATABASE_URL is NOT set")
        print("   This means the system will fallback to SQLite")
    
    # Step 2: Test direct PostgreSQL connection
    print(f"\n2️⃣ DIRECT POSTGRESQL TEST")
    print("-" * 30)
    if database_url:
        try:
            import psycopg2
            import psycopg2.extras
            
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            cursor.execute("SELECT COUNT(*) as count FROM recipes")
            recipe_count = cursor.fetchone()['count']
            print(f"✅ PostgreSQL connection successful")
            print(f"   Recipes available: {recipe_count}")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"❌ PostgreSQL connection failed: {e}")
            return False
    else:
        print("⏭️  Skipping PostgreSQL test (DATABASE_URL not set)")
    
    # Step 3: Test SmartRecipeSuggestionEngine
    print(f"\n3️⃣ SMART RECIPE ENGINE TEST")
    print("-" * 30)
    try:
        # Add the core_systems directory to Python path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'core_systems'))
        
        from enhanced_recipe_suggestions import SmartRecipeSuggestionEngine
        
        print("✅ Successfully imported SmartRecipeSuggestionEngine")
        
        # Create engine instance
        engine = SmartRecipeSuggestionEngine()
        print("✅ Engine instance created")
        
        # Check database connection type
        conn = engine.get_database_connection()
        if conn:
            if hasattr(engine, 'is_postgresql') and engine.is_postgresql:
                print("✅ Engine is using PostgreSQL")
            else:
                print("⚠️  Engine is using SQLite (fallback)")
            conn.close()
        else:
            print("❌ Engine failed to get database connection")
            return False
            
    except Exception as e:
        print(f"❌ SmartRecipeSuggestionEngine test failed: {e}")
        traceback.print_exc()
        return False
    
    # Step 4: Test get_smart_suggestions function
    print(f"\n4️⃣ GET_SMART_SUGGESTIONS TEST")
    print("-" * 30)
    try:
        from enhanced_recipe_suggestions import get_smart_suggestions
        
        print("✅ Successfully imported get_smart_suggestions")
        
        # Test with a simple query
        test_query = "chicken recipes"
        print(f"   Testing query: '{test_query}'")
        
        result = get_smart_suggestions(test_query, session_id="diagnostic_test", limit=3)
        
        if result and 'suggestions' in result:
            suggestions_count = len(result['suggestions'])
            print(f"✅ get_smart_suggestions returned {suggestions_count} recipes")
            
            if suggestions_count > 0:
                first_recipe = result['suggestions'][0]
                print(f"   Sample recipe: {first_recipe.get('title', 'No title')}")
            
            return True
        else:
            print("❌ get_smart_suggestions returned invalid result")
            print(f"   Result: {result}")
            return False
            
    except Exception as e:
        print(f"❌ get_smart_suggestions test failed: {e}")
        traceback.print_exc()
        return False
    
    # Step 5: Test complete ChatAPI flow
    print(f"\n5️⃣ COMPLETE CHATAPI FLOW TEST")
    print("-" * 30)
    try:
        # This simulates what the server does
        from enhanced_recipe_suggestions import get_smart_suggestions
        
        user_message = "I want some chicken recipes"
        session_id = "test_session"
        
        print(f"   Simulating ChatAPI call: '{user_message}'")
        
        # Check if this is a recipe request (like the server does)
        recipe_keywords = ['recipe', 'cook', 'eat', 'make', 'dinner', 'lunch', 'breakfast', 'tonight', 'today']
        is_recipe_request = any(keyword in user_message.lower() for keyword in recipe_keywords)
        
        if is_recipe_request:
            print("   ✅ Recipe request detected")
            
            suggestion_result = get_smart_suggestions(user_message, session_id, limit=5)
            suggestions = suggestion_result['suggestions']
            preferences = suggestion_result['preferences_detected']
            contextual_response = suggestion_result.get('contextual_response', '')
            
            print(f"   ✅ ChatAPI flow completed successfully")
            print(f"   📊 Results: {len(suggestions)} recipes, {len(preferences)} preferences detected")
            print(f"   💬 AI Response: {contextual_response[:100]}...")
            
            return True
        else:
            print("   ❌ Recipe request not detected (keyword detection failed)")
            return False
            
    except Exception as e:
        print(f"❌ Complete ChatAPI flow test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run complete diagnosis"""
    success = diagnose_chatapi_database_connection()
    
    if success:
        print(f"\n🎉 DIAGNOSIS COMPLETE - ALL TESTS PASSED!")
        print("✅ ChatAPI should be working correctly")
        print("✅ Recipe data is accessible")
        print("✅ Database connectivity confirmed")
    else:
        print(f"\n❌ DIAGNOSIS FAILED")
        print("💡 Check the error messages above")
        print("💡 Ensure DATABASE_URL is set for PostgreSQL")
        print("💡 Verify recipes have been migrated to PostgreSQL")
    
    return success

if __name__ == "__main__":
    main()
