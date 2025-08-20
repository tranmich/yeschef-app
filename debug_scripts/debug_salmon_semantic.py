#!/usr/bin/env python3
"""
Debug script to trace why Oven-Roasted Salmon fails semantic validation
"""

import sys
import os
import re

# Add the parent directory to the path to import the extractor
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("🐟 DEBUGGING OVEN-ROASTED SALMON SEMANTIC VALIDATION")
print("=" * 70)

# First, let's check if we can find the specific multi-page recipe data
def debug_multi_page_logic():
    """Debug the multi-page recipe logic"""
    
    print("1. CHECKING MULTI-PAGE RECIPE TRACKING...")
    
    # The issue is likely in the _validate_multi_page_recipe_requirements or semantic validation
    # Let's manually trace what would happen:
    
    # Simulate the recipe data that would be extracted
    recipe_data = {
        'title': 'Oven-Roasted Salmon',
        'ingredients': '',  # This might be empty!
        'instructions': '',  # This might be empty too!
    }
    
    print(f"   Title: '{recipe_data['title']}'")
    print(f"   Ingredients: '{recipe_data['ingredients']}'")
    print(f"   Instructions: '{recipe_data['instructions']}'")
    
    # Check validation requirements
    print("\n2. VALIDATION REQUIREMENTS CHECK:")
    
    # Must have title
    has_title = bool(recipe_data.get('title'))
    print(f"   ✅ Has title: {has_title}")
    
    # For multi-page recipes, need EITHER ingredients OR instructions
    has_ingredients = recipe_data.get('ingredients') and len(recipe_data['ingredients'].strip()) >= 5
    has_instructions = recipe_data.get('instructions') and len(recipe_data['instructions'].strip()) >= 10
    
    print(f"   Has ingredients (≥5 chars): {has_ingredients}")
    print(f"   Has instructions (≥10 chars): {has_instructions}")
    
    validation_passes = has_title and (has_ingredients or has_instructions)
    print(f"   Overall validation: {validation_passes}")
    
    if not validation_passes:
        print("\n❌ LIKELY ISSUE: Recipe fails basic validation requirements")
        if not has_ingredients and not has_instructions:
            print("   The recipe has no substantial ingredients OR instructions content!")
            print("   This suggests the visual extraction is not capturing the recipe content properly.")
    
    print("\n3. SEMANTIC VALIDATION FACTORS:")
    print("   Even if basic validation passes, semantic validation looks for:")
    print("   - Food-related keywords in title/ingredients")
    print("   - Cooking action words in instructions")
    print("   - Proper recipe structure and measurements")
    print("   - Coherent recipe flow")
    
    # Teen food indicators check
    teen_food_keywords = [
        'salmon', 'fish', 'oil', 'salt', 'pepper', 'lemon', 'herbs',
        'oven', 'roast', 'bake', 'cook'
    ]
    
    title_lower = recipe_data.get('title', '').lower()
    title_food_words = [word for word in teen_food_keywords if word in title_lower]
    print(f"\n   Food words in title: {title_food_words}")
    
    if 'salmon' in title_lower:
        print("   ✅ Title contains 'salmon' - should pass food indicator check")
    else:
        print("   ❌ Title missing key food words")
    
    print("\n4. POSSIBLE REASONS FOR FAILURE:")
    print("   A. Visual extraction not capturing ingredients/instructions properly")
    print("   B. Multi-page content combination logic has issues")
    print("   C. Semantic engine too strict for teen cookbook content")
    print("   D. Text cleaning removing important content")
    print("   E. Teen cookbook override not triggering")

def check_teen_override_logic():
    """Check why teen cookbook override might not be working"""
    
    print("\n" + "="*70)
    print("TEEN COOKBOOK OVERRIDE ANALYSIS")
    print("="*70)
    
    # Teen override triggers when:
    # 1. visual confidence >= 10 (multi-page gets 12, so ✅)
    # 2. has_teen_food_indicators() returns True
    # 3. has_proper_teen_structure() returns True
    
    print("Teen override requirements:")
    print("  1. Visual confidence ≥ 10: ✅ (multi-page gets 12)")
    print("  2. Teen food indicators: ?")
    print("  3. Proper teen structure: ?")
    
    # Food indicators check
    print("\nTeen food indicators check:")
    teen_food_keywords = [
        'sandwich', 'burger', 'pizza', 'pasta', 'eggs', 'pancakes',
        'chicken', 'cheese', 'bacon', 'bread', 'smoothie', 'muffin',
        'cookie', 'cake', 'salad', 'soup', 'tacos', 'quesadilla',
        'breakfast', 'lunch', 'dinner', 'snack'
    ]
    
    title = "Oven-Roasted Salmon"
    ingredients = ""  # Empty in our case
    
    title_has_food = any(keyword in title.lower() for keyword in teen_food_keywords)
    ingredients_have_food = any(keyword in ingredients.lower() for keyword in teen_food_keywords)
    
    basic_ingredients = ['salt', 'pepper', 'oil', 'butter', 'egg', 'milk', 'cheese']
    has_basic_ingredients = any(ingredient in ingredients.lower() for ingredient in basic_ingredients)
    
    food_indicator_result = title_has_food or (ingredients_have_food and has_basic_ingredients)
    
    print(f"  Title has food words: {title_has_food}")
    print(f"  Ingredients have food words: {ingredients_have_food}")
    print(f"  Has basic ingredients: {has_basic_ingredients}")
    print(f"  Overall food indicator result: {food_indicator_result}")
    
    if not food_indicator_result:
        print("  ❌ ISSUE: 'salmon' is not in the teen food keywords list!")
        print("  The teen food keywords are focused on typical teen foods")
        print("  but don't include 'salmon' or 'fish'")
    
    # Structure check
    print("\nTeen structure check:")
    print("  Title length ≥ 5: ✅ (Oven-Roasted Salmon = 19 chars)")
    print("  Ingredients length ≥ 20: ❌ (empty)")
    print("  Instructions length ≥ 20: ❌ (empty)")
    print("  Has measurements: ❌ (no ingredients)")
    
    print("\n❌ MAIN ISSUE IDENTIFIED:")
    print("  1. 'salmon' is not in teen food keywords")
    print("  2. Empty ingredients/instructions fail structure check")
    print("  3. Teen override won't trigger due to both failures")

if __name__ == "__main__":
    debug_multi_page_logic()
    check_teen_override_logic()
    
    print("\n" + "="*70)
    print("RECOMMENDED FIXES:")
    print("="*70)
    print("1. Add 'salmon', 'fish' to teen food keywords")
    print("2. Debug visual extraction for pages 299-300")
    print("3. Check if content combination logic is working")
    print("4. Consider more lenient semantic validation for seafood recipes")
