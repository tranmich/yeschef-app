#!/usr/bin/env python3
"""
Test specific criteria for instruction validation
"""

import sys
import os
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_systems.semantic_recipe_engine import SemanticRecipeEngine

def test_instruction_criteria():
    """Test specific criteria that instructions must meet"""
    
    instructions = """1. Process all but 1 cup of beans with broth and salt in food processor until smooth, about 15 seconds, scraping down sides of workbowl with rubber spatula if necessary. Add remaining beans and pulse until slightly chunky, about 10 pulses.
2. Cook bacon in 12-inch nonstick skillet over medium heat until bacon just begins to brown and most of fat has rendered, about 4 minutes. Transfer to small bowl lined with strainer; discard bacon and add 1 tablespoon fat back to skillet. Increase heat to medium-high; add onion, jalapeño, and cumin; and cook until softened and just starting to brown, 3 to 5 minutes. Stir in garlic and cook until fragrant, about 30 seconds. Reduce heat to medium, stir in pureed beans, and cook until thick and creamy, 4 to 6 minutes. Off heat, stir in cilantro and lime juice."""

    engine = SemanticRecipeEngine()
    
    print("=== Testing Instruction Criteria ===")
    print(f"Instructions length: {len(instructions)} chars")
    
    # Test numbered steps
    numbered_steps = len(re.findall(r'^\d+\.', instructions, re.MULTILINE))
    print(f"Numbered steps found: {numbered_steps}")
    
    # Test cooking words
    has_cooking_words = engine._contains_cooking_words(instructions)
    print(f"Contains cooking words: {has_cooking_words}")
    
    # Test if it passes _is_instruction_steps
    is_instructions = engine._is_instruction_steps(instructions)
    print(f"Passes _is_instruction_steps: {is_instructions}")
    
    # Let's check what cooking methods are in the database
    print(f"\nCooking methods database has {len(engine.cooking_methods)} categories")
    for category, methods in engine.cooking_methods.items():
        methods_list = list(methods)
        print(f"{category}: {methods_list[:5]}...")  # First 5 methods
    
    # Check which cooking words are found in our text
    text_lower = instructions.lower()
    found_methods = []
    for method_category in engine.cooking_methods.values():
        for method in method_category:
            if method in text_lower:
                found_methods.append(method)
    
    print(f"\nCooking methods found in text: {found_methods}")

if __name__ == "__main__":
    test_instruction_criteria()
