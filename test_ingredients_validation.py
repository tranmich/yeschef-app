#!/usr/bin/env python3
"""
Test ingredients validation specifically
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_systems.semantic_recipe_engine import SemanticRecipeEngine

def test_ingredients_validation():
    """Test ingredients validation"""
    
    # These are our cleaned ingredients
    ingredients = """• 2(15-ounce) cans pinto beans, rinsed, divided
• ¾cup chicken broth
• ½teaspoon table salt
• 3slices bacon, chopped fine
• 1small onion, chopped fine
• 1large jalapeño chile, stemmed, seeded, and minced
• ½teaspoon ground cumin
• 2garlic cloves, minced
• 2tablespoons minced fresh cilantro
• 2teaspoons lime juice"""

    engine = SemanticRecipeEngine()
    
    print("=== Testing Ingredients Validation ===")
    
    # Test content type classification
    ingredients_type, ingredients_conf = engine.classify_content_type(ingredients)
    print(f"Ingredients type: {ingredients_type}, confidence: {ingredients_conf}")
    
    # Test specific checks
    print(f"\nIs ingredient list: {engine._is_ingredient_list(ingredients)}")
    print(f"Is non-recipe content: {engine._is_non_recipe_content(ingredients)}")
    print(f"Contains food words: {engine._contains_food_words(ingredients)}")
    
    # Test line by line
    print(f"\n--- Testing individual lines ---")
    for line in ingredients.split('\n'):
        if line.strip():
            line_type, line_conf = engine.classify_content_type(line)
            print(f"'{line[:50]}...' -> {line_type} ({line_conf})")

if __name__ == "__main__":
    test_ingredients_validation()
