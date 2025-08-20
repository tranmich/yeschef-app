#!/usr/bin/env python3
"""
Test which extraction artifact pattern is matching
"""

import sys
import os
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_systems.semantic_recipe_engine import SemanticRecipeEngine

def test_artifact_patterns():
    """Test which artifact pattern is matching our instructions"""
    
    instructions = """1. Process all but 1 cup of beans with broth and salt in food processor until smooth, about 15 seconds, scraping down sides of workbowl with rubber spatula if necessary. Add remaining beans and pulse until slightly chunky, about 10 pulses.
2. Cook bacon in 12-inch nonstick skillet over medium heat until bacon just begins to brown and most of fat has rendered, about 4 minutes. Transfer to small bowl lined with strainer; discard bacon and add 1 tablespoon fat back to skillet. Increase heat to medium-high; add onion, jalapeño, and cumin; and cook until softened and just starting to brown, 3 to 5 minutes. Stir in garlic and cook until fragrant, about 30 seconds. Reduce heat to medium, stir in pureed beans, and cook until thick and creamy, 4 to 6 minutes. Off heat, stir in cilantro and lime juice."""

    engine = SemanticRecipeEngine()
    
    print("=== Testing Artifact Pattern Matching ===")
    print(f"Instructions are flagged as artifact: {engine._is_extraction_artifact(instructions.lower())}")
    
    # Check specific patterns
    print("\n--- Testing specific artifact patterns ---")
    
    # Page reference patterns
    page_ref_match = re.search(r'recipe from page \d+', instructions, re.IGNORECASE)
    print(f"Page reference pattern matches: {page_ref_match}")
    
    # Check each pattern category
    for category, patterns in engine.artifact_patterns.items():
        print(f"\n{category}:")
        for pattern in patterns:
            match = re.search(pattern, instructions, re.IGNORECASE)
            if match:
                print(f"  MATCH: {pattern} -> {match.group()}")
            else:
                print(f"  no match: {pattern}")
    
    # Test heuristics
    print("\n--- Testing heuristics ---")
    print(f"Length: {len(instructions)} chars")
    print(f"Is single alpha ≤3 chars: {len(instructions) <= 3 and instructions.isalpha()}")
    
    words = instructions.split()
    print(f"Word count: {len(words)}")
    print(f"Single word <15 chars: {len(words) == 1 and len(instructions) < 15}")
    print(f"Contains food words: {engine._contains_food_words(instructions)}")

if __name__ == "__main__":
    test_artifact_patterns()
