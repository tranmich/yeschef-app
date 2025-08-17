#!/usr/bin/env python3
"""Quick test of the universal search system"""

from core_systems.universal_search import UniversalSearchEngine

def test_universal_search():
    print("🔍 Testing Universal Search Engine...")
    
    try:
        # Initialize engine
        engine = UniversalSearchEngine()
        print("✅ Engine initialized successfully")
        
        # Test a simple search
        result = engine.unified_intelligent_search(
            query='chicken pasta',
            session_memory=None,
            user_pantry=[],
            exclude_ids=[],
            limit=3,
            include_explanations=True
        )
        
        print(f"🔍 Search Result:")
        print(f"  Success: {result['success']}")
        
        if result['success']:
            recipes = result['recipes']
            print(f"  Found: {len(recipes)} recipes")
            
            for i, recipe in enumerate(recipes[:2], 1):
                print(f"  {i}. {recipe['title']} (ID: {recipe['id']})")
                if recipe.get('explanations'):
                    print(f"     💡 {recipe['explanations']}")
                if recipe.get('meal_role'):
                    print(f"     🍽️ Meal: {recipe['meal_role']}")
                if recipe.get('is_easy'):
                    print(f"     ⚡ Easy recipe")
        else:
            print(f"  ❌ Error: {result.get('error', 'Unknown')}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_universal_search()
