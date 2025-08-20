#!/usr/bin/env python3
"""
Debug why specific good titles are being rejected
"""

import sys
import os

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_systems.semantic_recipe_engine import SemanticRecipeEngine, ValidationLevel

def debug_specific_titles():
    """Debug why specific titles that should pass are being rejected"""
    
    engine = SemanticRecipeEngine(ValidationLevel.STRICT)
    
    # These should clearly be valid recipe titles
    test_titles = [
        "Ultracreamy Hummus",
        "Spiced Walnut Topping for Hummus", 
        "Curry Deviled Eggs with Easy-Peel Hard-Cooked Eggs",
        "Easy-Peel Hard-Cooked Eggs"
    ]
    
    for title in test_titles:
        print(f"\n🔍 DEBUGGING: '{title}'")
        print("-" * 50)
        
        # Test step by step
        print(f"Length: {len(title)} (valid: {3 <= len(title) <= 100})")
        print(f"Starts with capital: {title[0].isupper()}")
        
        # Check food/cooking words
        has_food = engine._contains_food_words(title)
        has_cooking = engine._contains_cooking_words(title)
        print(f"Has food words: {has_food}")
        print(f"Has cooking words: {has_cooking}")
        
        # Check for measurements
        import re
        has_measurements = re.search(r'\d+\s*(cup|tablespoon|teaspoon|pound|ounce)', title.lower())
        print(f"Has measurements: {bool(has_measurements)}")
        
        # Check word count
        word_count = len(title.split())
        print(f"Word count: {word_count} (valid range: 2-8)")
        
        # Test title validation
        is_valid = engine._is_recipe_title(title)
        print(f"Is valid recipe title: {is_valid}")
        
        # Test content classification
        content_type, confidence = engine.classify_content_type(title)
        print(f"Content type: {content_type}")
        print(f"Confidence: {confidence:.2f}")
        
        # Test sounds like complete dish
        sounds_complete = engine._sounds_like_complete_dish(title)
        print(f"Sounds like complete dish: {sounds_complete}")
        
        # If not valid, let's trace through the validation logic manually
        if not is_valid:
            print("\nDetailed rejection analysis:")
            text_lower = title.lower()
            
            # Check each condition
            if not (has_food or has_cooking):
                print("  ❌ No food or cooking words")
            
            if word_count == 1:
                iconic_dishes = {'chili', 'risotto', 'paella', 'ratatouille', 'gazpacho', 'bouillabaisse', 'jambalaya'}
                if text_lower not in iconic_dishes:
                    print("  ❌ Single word but not iconic dish")
            
            if not sounds_complete:
                print("  ❌ Doesn't sound like complete dish")

if __name__ == "__main__":
    debug_specific_titles()
