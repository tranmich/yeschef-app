#!/usr/bin/env python3
"""
🔧 SEMANTIC ENGINE DEBUGGING
Debug the classification logic to understand why good recipes are being rejected
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core_systems.semantic_recipe_engine import SemanticRecipeEngine, ValidationLevel, ContentType

def debug_classification():
    """Debug the content classification with detailed output"""
    print("🔧 DEBUGGING SEMANTIC CLASSIFICATION")
    print("=" * 60)
    
    engine = SemanticRecipeEngine(ValidationLevel.STRICT)
    
    # Test individual components
    test_titles = [
        "Chocolate Chip Cookies",  # Should be RECIPE_TITLE
        "Grilled Chicken Salad",   # Should be RECIPE_TITLE
        "Start Cooking!",          # Should be INSTRUCTION_HEADER
        "ATK Recipe from Page 14", # Should be PAGE_METADATA
        "Before You Begin",        # Should be INSTRUCTION_HEADER
        "PREPARE INGREDIENTS"      # Should be INSTRUCTION_HEADER
    ]
    
    print("\n🧪 TESTING TITLE CLASSIFICATION:")
    print("-" * 40)
    
    for title in test_titles:
        content_type, confidence = engine.classify_content_type(title)
        print(f"'{title}'")
        print(f"  → {content_type.value} (confidence: {confidence:.2f})")
        
        # Debug the food word detection
        has_food_words = engine._contains_food_words(title)
        has_cooking_words = engine._contains_cooking_words(title)
        is_recipe_title = engine._is_recipe_title(title)
        
        print(f"  Food words: {has_food_words}, Cooking words: {has_cooking_words}")
        print(f"  Recipe title check: {is_recipe_title}")
        print()
    
    # Test ingredient classification
    test_ingredients = [
        "• 2 cups all-purpose flour\n• 1 cup butter\n• 1 cup chocolate chips",
        "• 2 tablespoons butter",
        "• See page reference",
        "• Various ingredients listed below"
    ]
    
    print("\n🧪 TESTING INGREDIENT CLASSIFICATION:")
    print("-" * 40)
    
    for ingredients in test_ingredients:
        content_type, confidence = engine.classify_content_type(ingredients)
        print(f"'{ingredients[:50]}...'")
        print(f"  → {content_type.value} (confidence: {confidence:.2f})")
        
        is_ingredient_list = engine._is_ingredient_list(ingredients)
        print(f"  Ingredient list check: {is_ingredient_list}")
        print()
    
    # Test instruction classification
    test_instructions = [
        "1. Preheat oven to 350°F.\n2. Mix flour and butter.\n3. Add chocolate chips and bake.",
        "1. Grill chicken until cooked through.\n2. Slice chicken and serve over greens.",
        "1. Heat oil in pan.",
        "1. Follow instructions on page 14."
    ]
    
    print("\n🧪 TESTING INSTRUCTION CLASSIFICATION:")
    print("-" * 40)
    
    for instructions in test_instructions:
        content_type, confidence = engine.classify_content_type(instructions)
        print(f"'{instructions[:50]}...'")
        print(f"  → {content_type.value} (confidence: {confidence:.2f})")
        
        is_instruction_steps = engine._is_instruction_steps(instructions)
        print(f"  Instruction steps check: {is_instruction_steps}")
        print()

if __name__ == "__main__":
    debug_classification()
