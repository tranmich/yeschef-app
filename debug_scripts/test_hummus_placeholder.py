#!/usr/bin/env python3
"""
Test hummus recipe with placeholder instructions
"""

import sys
import os

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_systems.semantic_recipe_engine import SemanticRecipeEngine, ValidationLevel

def test_hummus_with_placeholder():
    """Test if hummus passes with placeholder instructions"""
    
    engine = SemanticRecipeEngine(ValidationLevel.STRICT)
    
    hummus_recipe = {
        'title': 'Ultracreamy Hummus',
        'ingredients': '''• 2(15-ounce) cans chickpeas, rinsed
• ½teaspoon baking soda
• ⅓cup lemon juice (2 lemons), plus extra for seasoning
• 1teaspoon table salt
• ¼teaspoon ground cumin, plus extra for garnish
• ½cup tahini
• ¼cup extra-virgin olive oil, plus extra for serving
• 1tablespoon minced fresh parsley''',
        'instructions': '1. Prepare ingredients according to recipe specifications.\n2. Cook and combine ingredients following standard method for this dish type.'
    }
    
    print("🧠 TESTING HUMMUS WITH PLACEHOLDER INSTRUCTIONS")
    print("=" * 60)
    
    result = engine.validate_complete_recipe(hummus_recipe)
    
    print(f"Is valid recipe: {result.is_valid_recipe}")
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
    
    print(f"\nComponent details:")
    for i, component in enumerate(result.components, 1):
        print(f"  {i}. {component.content_type}: confidence {component.confidence_score:.2f}")

if __name__ == "__main__":
    test_hummus_with_placeholder()
