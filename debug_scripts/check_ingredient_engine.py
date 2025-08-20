#!/usr/bin/env python3
"""
Check what ingredients are available in the ingredient intelligence engine
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core_systems.ingredient_intelligence_engine import IngredientIntelligenceEngine
    
    print("🧠 INGREDIENT INTELLIGENCE ENGINE ANALYSIS")
    print("=" * 60)
    
    engine = IngredientIntelligenceEngine()
    
    print(f"📊 Total canonical ingredients loaded: {len(engine.canonical_ingredients)}")
    
    if engine.canonical_ingredients:
        print("\n🥬 Sample ingredients from database:")
        for i, (ingredient_id, data) in enumerate(list(engine.canonical_ingredients.items())[:15]):
            name = data['name']
            category = data.get('category', 'Unknown')
            print(f"  {i+1:2d}. {name} ({category})")
        
        if len(engine.canonical_ingredients) > 15:
            print(f"  ... and {len(engine.canonical_ingredients) - 15} more")
        
        # Check for specific ingredients that were missing
        search_ingredients = ['salmon', 'fish', 'chicken', 'beef', 'eggs', 'butter', 'oil', 'salt', 'pepper']
        print(f"\n🔍 Checking for specific ingredients:")
        
        found_ingredients = []
        for search_term in search_ingredients:
            found = False
            for ingredient_id, data in engine.canonical_ingredients.items():
                if search_term.lower() in data['name'].lower():
                    found_ingredients.append((search_term, data['name']))
                    found = True
                    break
            
            if found:
                print(f"  ✅ Found '{search_term}': {found_ingredients[-1][1]}")
            else:
                print(f"  ❌ Missing '{search_term}'")
        
        # Get ingredient categories
        categories = {}
        for data in engine.canonical_ingredients.values():
            category = data.get('category', 'Unknown')
            categories[category] = categories.get(category, 0) + 1
        
        print(f"\n📂 Ingredient categories:")
        for category, count in sorted(categories.items()):
            print(f"  {category}: {count} ingredients")
    
    else:
        print("❌ No ingredients loaded from database!")
        
except Exception as e:
    print(f"❌ Error loading ingredient engine: {e}")
    import traceback
    traceback.print_exc()
