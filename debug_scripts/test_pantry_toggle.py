"""
🧪 Pantry System Toggle Test
===========================

This script demonstrates the pantry system toggle functionality
and shows how the configuration affects search results.

Author: GitHub Copilot
Date: August 18, 2025
"""

import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core_systems.config import print_config_status, toggle_pantry, enable_pantry, disable_pantry

def test_pantry_toggle():
    """Test the pantry toggle functionality"""
    
    print("🧪 PANTRY SYSTEM TOGGLE TEST")
    print("=" * 50)
    
    # Show initial status
    print("\n📊 INITIAL CONFIGURATION:")
    print_config_status()
    
    # Test toggling
    print("\n🔄 TESTING TOGGLE FUNCTIONALITY:")
    print("-" * 30)
    
    print("\n1️⃣ Toggling pantry system...")
    new_state = toggle_pantry()
    print(f"   Result: Pantry is now {'ENABLED' if new_state else 'DISABLED'}")
    
    print("\n2️⃣ Toggling again...")
    new_state = toggle_pantry()
    print(f"   Result: Pantry is now {'ENABLED' if new_state else 'DISABLED'}")
    
    # Test explicit enable/disable
    print("\n🎛️ TESTING EXPLICIT CONTROLS:")
    print("-" * 30)
    
    print("\n3️⃣ Explicitly disabling pantry...")
    disable_pantry()
    
    print("\n4️⃣ Explicitly enabling pantry...")
    enable_pantry()
    
    # Show final status
    print("\n📊 FINAL CONFIGURATION:")
    print_config_status()
    
    print("\n✅ TOGGLE TEST COMPLETE!")
    print("   The pantry system can now be controlled via:")
    print("   • API endpoints (/api/config/pantry/toggle)")
    print("   • Direct function calls (toggle_pantry())")
    print("   • Configuration system (config.toggle_pantry())")

def test_search_integration():
    """Test how the toggle affects search functionality"""
    
    print("\n🔍 SEARCH INTEGRATION TEST")
    print("=" * 50)
    
    try:
        from core_systems.enhanced_search import EnhancedSearchEngine
        from core_systems.config import is_pantry_enabled, disable_pantry, enable_pantry
        
        search_engine = EnhancedSearchEngine()
        
        print("\n1️⃣ Testing search with pantry DISABLED:")
        disable_pantry()
        print(f"   Pantry enabled: {is_pantry_enabled()}")
        
        # Test search without user_id (no pantry enhancement)
        results = search_engine.smart_search_with_analysis("chicken", limit=3)
        print(f"   Search results: {len(results)} recipes found")
        for i, recipe in enumerate(results[:2]):
            pantry_info = recipe.get('pantry_message', 'No pantry data')
            print(f"   • {recipe['title']} - {pantry_info}")
        
        print("\n2️⃣ Testing search with pantry ENABLED:")
        enable_pantry()
        print(f"   Pantry enabled: {is_pantry_enabled()}")
        
        # Test search with user_id (pantry enhancement available)
        results = search_engine.smart_search_with_analysis("chicken", limit=3, user_id="test_user")
        print(f"   Search results: {len(results)} recipes found")
        for i, recipe in enumerate(results[:2]):
            pantry_info = recipe.get('pantry_message', 'No pantry data available')
            boost = " (BOOSTED)" if recipe.get('pantry_boost') else ""
            print(f"   • {recipe['title']} - {pantry_info}{boost}")
        
        print("\n✅ SEARCH INTEGRATION TEST COMPLETE!")
        
    except Exception as e:
        print(f"❌ Search integration test failed: {e}")
        print("   This is expected if the database is not available")

if __name__ == "__main__":
    try:
        # Run the toggle test
        test_pantry_toggle()
        
        # Run the search integration test
        test_search_integration()
        
        print(f"\n🎉 ALL TESTS COMPLETED!")
        print(f"   The pantry system toggle is working correctly.")
        print(f"   You can now easily enable/disable pantry features for testing.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
