#!/usr/bin/env python3
"""
Debug title validation to see why good titles are being rejected
"""

import sys
import os
import re

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_systems.semantic_recipe_engine import SemanticRecipeEngine, ValidationLevel, ContentType

def debug_title_validation():
    """Debug why good titles are being rejected"""
    
    engine = SemanticRecipeEngine(ValidationLevel.STRICT)
    
    test_titles = [
        "Refried Beans",
        "Classic Chicken Soup", 
        "Grilled Salmon with Herbs"
    ]
    
    for title in test_titles:
        print(f"\n🔍 DEBUGGING TITLE: '{title}'")
        print("=" * 50)
        
        # Test each validation step manually
        print(f"Length check: {3 <= len(title) <= 100} (length: {len(title)})")
        
        text_lower = title.lower()
        text_clean = title.strip()
        
        # Check for measurement patterns
        has_measurements = re.search(r'\d+\s*(cup|tablespoon|teaspoon|pound|ounce|tbsp|tsp|lb|oz|clove|slice)', text_lower)
        print(f"Has measurements: {bool(has_measurements)}")
        
        # Check word count
        word_count = len(text_clean.split())
        print(f"Word count: {word_count}")
        
        # Check if starts with capital
        starts_capital = text_clean[0].isupper()
        print(f"Starts with capital: {starts_capital}")
        
        # Check for fragment indicators
        fragment_indicators = [
            'saucepan', 'skillet', 'bowl', 'plate', 'serving', 'mixture',
            'remaining', 'additional', 'optional', 'garnish', 'aside',
            'transfer', 'combine', 'process', 'continue', 'until'
        ]
        has_fragment_indicators = any(indicator in text_lower for indicator in fragment_indicators)
        print(f"Has fragment indicators: {has_fragment_indicators}")
        
        # Check for incomplete punctuation
        bad_ending = text_clean.endswith((',', ';', '...', '.'))
        print(f"Bad ending: {bad_ending}")
        
        # Check for brackets
        has_brackets = any(char in text_clean for char in ['(', ')', '[', ']', '{', '}'])
        print(f"Has brackets: {has_brackets}")
        
        # Check food words
        has_food_words = engine._contains_food_words(title)
        print(f"Has food words: {has_food_words}")
        
        # Check cooking words
        has_cooking_words = engine._contains_cooking_words(title)
        print(f"Has cooking words: {has_cooking_words}")
        
        # Test the new completion method
        sounds_complete = engine._sounds_like_complete_dish(title)
        print(f"Sounds like complete dish: {sounds_complete}")
        
        # Test overall classification
        content_type, confidence = engine.classify_content_type(title)
        print(f"Classified as: {content_type} (confidence: {confidence:.2f})")
        
        # Test title validation specifically
        is_recipe_title = engine._is_recipe_title(title)
        print(f"Is recipe title: {is_recipe_title}")

if __name__ == "__main__":
    debug_title_validation()
