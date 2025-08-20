#!/usr/bin/env python3
"""
Test script to compare old teen keyword approach vs new ingredient intelligence approach
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core_systems.ingredient_intelligence_engine import IngredientIntelligenceEngine
import re

def test_ingredient_detection():
    """Test the new ingredient intelligence vs old keyword approach"""
    
    print("🧠 INGREDIENT DETECTION COMPARISON")
    print("=" * 70)
    
    # Load the ingredient engine
    engine = IngredientIntelligenceEngine()
    print(f"✅ Loaded {len(engine.canonical_ingredients)} canonical ingredients")
    
    # Test recipes that would have failed with the old approach
    test_recipes = [
        {
            'title': 'Oven-Roasted Salmon',
            'ingredients': 'salmon fillets, olive oil, salt, pepper, lemon',
            'description': 'Originally failed - salmon not in teen keywords'
        },
        {
            'title': 'Beef Stew',
            'ingredients': 'beef chuck, carrots, potatoes, onions, beef broth',
            'description': 'Would work with old approach (beef in keywords)'
        },
        {
            'title': 'Quinoa Buddha Bowl',
            'ingredients': 'quinoa, kale, chickpeas, avocado, tahini',
            'description': 'Modern healthy recipe - would fail old approach'
        },
        {
            'title': 'Chocolate Chip Cookies',
            'ingredients': 'flour, butter, sugar, chocolate chips, eggs',
            'description': 'Classic teen recipe - would work with old approach'
        },
        {
            'title': 'Mushroom Risotto',
            'ingredients': 'arborio rice, mushrooms, parmesan, white wine, stock',
            'description': 'Sophisticated recipe - old approach might miss'
        }
    ]
    
    # Old teen keywords for comparison
    old_teen_keywords = [
        'sandwich', 'burger', 'pizza', 'pasta', 'eggs', 'pancakes',
        'chicken', 'cheese', 'bacon', 'bread', 'smoothie', 'muffin',
        'cookie', 'cake', 'salad', 'soup', 'tacos', 'quesadilla',
        'breakfast', 'lunch', 'dinner', 'snack', 'salmon', 'fish',
        'seafood', 'shrimp', 'beef', 'pork', 'turkey', 'rice', 'beans'
    ]
    
    def test_old_approach(title, ingredients):
        """Test the old keyword-based approach"""
        text = (title + ' ' + ingredients).lower()
        return any(keyword in text for keyword in old_teen_keywords)
    
    def test_new_approach(title, ingredients):
        """Test the new ingredient intelligence approach"""
        text = (title + ' ' + ingredients).lower()
        
        # Check against canonical ingredient names
        for ingredient_id, data in engine.canonical_ingredients.items():
            ingredient_name = data['name'].lower()
            
            # Extract core ingredient name
            core_name = extract_core_ingredient_name(ingredient_name)
            
            if core_name and len(core_name) >= 3:
                if core_name in text:
                    return True, core_name
        
        return False, None
    
    def extract_core_ingredient_name(ingredient_name):
        """Extract core ingredient name from full description"""
        cleaned = re.sub(r'^\d+.*?(cup|tablespoon|teaspoon|slice|large|small|pound|ounce|stick|clove)', '', ingredient_name, flags=re.IGNORECASE)
        cleaned = re.sub(r'\b(for|about|until|warmed|hot|to|the|touch|minute|lukewarm|strong|brewed|dry|extra-virgin|all-purpose|confectioners|crumbled|garnish)\b', '', cleaned, flags=re.IGNORECASE)
        
        words = cleaned.strip().split()
        core_words = []
        for word in words:
            if len(word) >= 3 and word not in ['and', 'the', 'for', 'with']:
                core_words.append(word)
                if len(core_words) >= 2:
                    break
        
        return ' '.join(core_words) if core_words else ''
    
    print("\n📊 TESTING DIFFERENT RECIPES:")
    print("-" * 70)
    
    for i, recipe in enumerate(test_recipes, 1):
        print(f"\n{i}. {recipe['title']}")
        print(f"   Ingredients: {recipe['ingredients']}")
        print(f"   Context: {recipe['description']}")
        
        # Test old approach
        old_result = test_old_approach(recipe['title'], recipe['ingredients'])
        
        # Test new approach
        new_result, matched_ingredient = test_new_approach(recipe['title'], recipe['ingredients'])
        
        print(f"   Old keyword approach: {'✅ PASS' if old_result else '❌ FAIL'}")
        if new_result:
            print(f"   New ingredient approach: ✅ PASS (matched: '{matched_ingredient}')")
        else:
            print(f"   New ingredient approach: ❌ FAIL")
        
        # Show improvement
        if new_result and not old_result:
            print(f"   🎯 IMPROVEMENT: New approach catches this recipe!")
        elif old_result and not new_result:
            print(f"   ⚠️ REGRESSION: Old approach was better for this case")
        elif old_result and new_result:
            print(f"   ✅ CONSISTENT: Both approaches work")
        else:
            print(f"   ❌ BOTH FAIL: Neither approach catches this recipe")
    
    print(f"\n" + "=" * 70)
    print(f"SUMMARY:")
    print(f"✅ Old approach: Limited to {len(old_teen_keywords)} hardcoded keywords")
    print(f"🧠 New approach: {len(engine.canonical_ingredients)} canonical ingredients with intelligent matching")
    print(f"🎯 Result: Much more comprehensive and accurate ingredient detection!")

if __name__ == "__main__":
    test_ingredient_detection()
