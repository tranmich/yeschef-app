#!/usr/bin/env python3
"""
Test properly formatted instructions vs our extraction
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_systems.semantic_recipe_engine import SemanticRecipeEngine

def test_instruction_formatting():
    """Test different instruction formats to understand semantic validation"""
    
    # Our current extraction (single line, 2 steps)
    extracted_instructions = """1. Process all but 1 cup of beans with broth and salt in food processor until smooth, about 15 seconds, scraping down sides of workbowl with rubber spatula if necessary. Add remaining beans and pulse until slightly chunky, about 10 pulses.
2. Cook bacon in 12-inch nonstick skillet over medium heat until bacon just begins to brown and most of fat has rendered, about 4 minutes. Transfer to small bowl lined with strainer; discard bacon and add 1 tablespoon fat back to skillet. Increase heat to medium-high; add onion, jalapeño, and cumin; and cook until softened and just starting to brown, 3 to 5 minutes. Stir in garlic and cook until fragrant, about 30 seconds. Reduce heat to medium, stir in pureed beans, and cook until thick and creamy, 4 to 6 minutes. Off heat, stir in cilantro and lime juice."""

    # Manually formatted perfect instructions
    perfect_instructions = """1. Process all but 1 cup of beans with broth and salt in food processor until smooth, about 15 seconds, scraping down sides of workbowl with rubber spatula if necessary. Add remaining beans and pulse until slightly chunky, about 10 pulses.

2. Cook bacon in 12-inch nonstick skillet over medium heat until bacon just begins to brown and most of fat has rendered, about 4 minutes. Transfer to small bowl lined with strainer; discard bacon and add 1 tablespoon fat back to skillet. Increase heat to medium-high; add onion, jalapeño, and cumin; and cook until softened and just starting to brown, 3 to 5 minutes. Stir in garlic and cook until fragrant, about 30 seconds. Reduce heat to medium, stir in pureed beans, and cook until thick and creamy, 4 to 6 minutes. Off heat, stir in cilantro and lime juice."""

    # Simple test instructions
    simple_instructions = """1. Heat oil in large skillet over medium heat.
2. Add onions and cook until softened, about 5 minutes.
3. Season with salt and pepper to taste."""

    engine = SemanticRecipeEngine()
    
    print("=== Testing Different Instruction Formats ===")
    
    print("\n1. EXTRACTED INSTRUCTIONS:")
    extracted_type, extracted_conf = engine.classify_content_type(extracted_instructions)
    print(f"Type: {extracted_type}, confidence: {extracted_conf}")
    
    print("\n2. PERFECT INSTRUCTIONS:")
    perfect_type, perfect_conf = engine.classify_content_type(perfect_instructions)
    print(f"Type: {perfect_type}, confidence: {perfect_conf}")
    
    print("\n3. SIMPLE INSTRUCTIONS:")
    simple_type, simple_conf = engine.classify_content_type(simple_instructions)
    print(f"Type: {simple_type}, confidence: {simple_conf}")
    
    print(f"\nLength comparison:")
    print(f"Extracted: {len(extracted_instructions)} chars")
    print(f"Perfect: {len(perfect_instructions)} chars")
    print(f"Simple: {len(simple_instructions)} chars")

if __name__ == "__main__":
    test_instruction_formatting()
