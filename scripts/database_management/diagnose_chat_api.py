#!/usr/bin/env python3
"""
Railway Chat API Diagnostic
Specifically test the recipe search functionality that's failing on Railway
"""

import os
import sys

def test_chat_api_issue():
    """Test the specific issue with Chat API not fetching recipes on Railway"""
    
    print("🔍 RAILWAY CHAT API DIAGNOSTIC")
    print("=" * 50)
    print("Testing the specific issue: Chat API not fetching recipe data")
    print()
    
    # Test 1: Check DATABASE_URL (should be set on Railway)
    database_url = os.getenv('DATABASE_URL')
    print(f"1. DATABASE_URL check:")
    if database_url:
        print(f"   ✅ Found: {database_url[:50]}...")
        has_database_url = True
    else:
        print("   ❌ Not set (this is the likely issue on Railway)")
        has_database_url = False
    print()
    
    # Test 2: Try importing the enhanced search system
    print("2. Enhanced search system import:")
    try:
        sys.path.append('.')
        from core_systems.enhanced_recipe_suggestions import get_smart_suggestions, SmartRecipeSuggestionEngine
        print("   ✅ Successfully imported enhanced search functions")
        import_success = True
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        import_success = False
    print()
    
    # Test 3: Try creating search engine instance
    if import_success:
        print("3. Search engine initialization:")
        try:
            engine = SmartRecipeSuggestionEngine()
            print("   ✅ Search engine created successfully")
            engine_success = True
        except Exception as e:
            print(f"   ❌ Engine creation failed: {e}")
            engine_success = False
        print()
        
        # Test 4: Try actual search (if we have DATABASE_URL)
        if engine_success and has_database_url:
            print("4. Recipe search test:")
            try:
                result = get_smart_suggestions("chicken recipes", "test_session", limit=3)
                if result and 'suggestions' in result:
                    recipes = result['suggestions']
                    print(f"   ✅ Found {len(recipes)} recipes")
                    for recipe in recipes[:2]:
                        print(f"      - {recipe.get('title', 'No title')}")
                else:
                    print(f"   ❌ No recipes returned: {result}")
            except Exception as e:
                print(f"   ❌ Search failed: {e}")
                print(f"      Error type: {type(e).__name__}")
                if "relation" in str(e) and "does not exist" in str(e):
                    print("      💡 PostgreSQL tables not found - migration issue")
                elif "connect" in str(e):
                    print("      💡 Database connection issue")
        elif engine_success:
            print("4. Recipe search test:")
            print("   ⏭️  Skipped (no DATABASE_URL - would fallback to SQLite)")
        print()
    
    # Test 5: Check what happens with SQLite fallback
    if import_success and not has_database_url:
        print("5. SQLite fallback test (local development):")
        try:
            result = get_smart_suggestions("pasta recipes", "test_session", limit=2)
            if result and 'suggestions' in result:
                recipes = result['suggestions']
                print(f"   ✅ SQLite fallback working: {len(recipes)} recipes found")
            else:
                print(f"   ❌ SQLite fallback failed: {result}")
        except Exception as e:
            print(f"   ❌ SQLite fallback error: {e}")
        print()
    
    # Summary and diagnosis
    print("📋 DIAGNOSIS SUMMARY")
    print("=" * 30)
    
    if not has_database_url:
        print("🔧 LIKELY ISSUE: DATABASE_URL not set on Railway")
        print("   Solution: Set DATABASE_URL environment variable on Railway")
        print("   Command: railway variables set DATABASE_URL=<postgresql_connection_string>")
    elif not import_success:
        print("🔧 LIKELY ISSUE: Import problems on Railway")
        print("   Solution: Check Railway build logs for missing dependencies")
    elif import_success and has_database_url:
        print("🔧 LIKELY ISSUE: PostgreSQL connection or table migration")
        print("   Solution: Check if recipe tables exist in PostgreSQL")
    else:
        print("🤔 Issue unclear - need more investigation")
    
    print()
    print("💡 Next steps:")
    print("   1. Run this script on Railway (via Railway CLI or logs)")
    print("   2. Check Railway environment variables")
    print("   3. Verify PostgreSQL tables exist with recipe data")

if __name__ == "__main__":
    test_chat_api_issue()
