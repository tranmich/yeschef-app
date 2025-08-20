#!/usr/bin/env python3
"""
Test enhanced validation with more realistic recipe components
"""

import sys
import os

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_systems.semantic_recipe_engine import SemanticRecipeEngine, ValidationLevel

def test_realistic_recipes():
    """Test with complete, realistic recipe data"""
    
    engine = SemanticRecipeEngine(ValidationLevel.STRICT)
    
    # Test a complete realistic recipe
    good_recipe = {
        'title': 'Refried Beans',
        'ingredients': '''• 2 (15-ounce) cans pinto beans, drained and rinsed
• 3 tablespoons lard or vegetable oil
• 1 small onion, chopped fine
• 3 garlic cloves, minced
• 1 teaspoon ground cumin
• Salt and pepper to taste''',
        'instructions': '''1. Heat lard in large skillet over medium-high heat until shimmering.
2. Add onion and cook until softened, about 5 minutes.
3. Stir in garlic and cumin and cook until fragrant, about 30 seconds.
4. Add beans and mash with potato masher until mostly smooth but with some chunky texture remaining.
5. Season with salt and pepper to taste. Serve immediately.'''
    }
    
    # Test fragment-based "recipes" 
    fragment_recipe1 = {
        'title': 'Soup',
        'ingredients': '• 2 cups broth',
        'instructions': '1. Heat and serve.'
    }
    
    fragment_recipe2 = {
        'title': '2½ cups chicken broth',
        'ingredients': '• Salt to taste',
        'instructions': '1. Mix together.'
    }
    
    fragment_recipe3 = {
        'title': 'Grilled Salmon with Herbs', 
        'ingredients': '''• 4 (6-ounce) salmon fillets, skin removed
• 2 tablespoons olive oil
• 2 tablespoons fresh herbs (dill, parsley, or chives), minced
• 1 lemon, cut into wedges
• Salt and pepper''',
        'instructions': '''1. Heat gas grill or prepare charcoal fire for hot grilling.
2. Pat salmon dry and season both sides with salt and pepper.
3. Brush grill grates clean and oil well.
4. Grill salmon over hot fire until cooked through, 4 to 6 minutes per side.
5. Transfer to platter, drizzle with olive oil, and sprinkle with herbs.
6. Serve with lemon wedges.'''
    }
    
    test_cases = [
        ("Good Recipe (Refried Beans)", good_recipe, True),
        ("Fragment Recipe (Soup)", fragment_recipe1, False),
        ("Fragment Recipe (Measurement)", fragment_recipe2, False),
        ("Good Recipe (Grilled Salmon)", fragment_recipe3, True)
    ]
    
    print("🧠 TESTING ENHANCED VALIDATION WITH REALISTIC RECIPES")
    print("=" * 70)
    
    for name, recipe, should_pass in test_cases:
        print(f"\n🔍 Testing: {name}")
        print("-" * 50)
        
        result = engine.validate_complete_recipe(recipe)
        
        print(f"Title: '{recipe['title']}'")
        print(f"Valid Recipe: {result.is_valid_recipe}")
        print(f"Confidence: {result.confidence_score:.2f}")
        print(f"Components: {len(result.components)}")
        
        if result.validation_errors:
            print("Errors:")
            for error in result.validation_errors:
                print(f"  - {error}")
        
        if result.validation_warnings:
            print("Warnings:")
            for warning in result.validation_warnings:
                print(f"  - {warning}")
        
        # Check if result matches expectation
        if result.is_valid_recipe == should_pass:
            print(f"✅ CORRECT: {'Passed' if should_pass else 'Rejected'} as expected")
        else:
            print(f"❌ INCORRECT: {'Rejected' if should_pass else 'Passed'} but should be {'passed' if should_pass else 'rejected'}")

if __name__ == "__main__":
    test_realistic_recipes()
