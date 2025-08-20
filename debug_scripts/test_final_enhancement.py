#!/usr/bin/env python3
"""
Test final enhancement to catch sentence fragments
"""

import sys
import os

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_systems.semantic_recipe_engine import SemanticRecipeEngine, ValidationLevel

def test_final_enhancement():
    """Test final enhancement catches sentence fragments"""
    
    engine = SemanticRecipeEngine(ValidationLevel.STRICT)
    
    # Test cases that should be rejected
    should_reject = [
        "Place br ead on wir e rack set o ver rimmed baking sheet. B ake bread",
        "Heat o il in large skillet",
        "Transfer to serving bowl",
        "Bake until golden brown",
        "Cook until tender",
        "Slice and serve immediately"
    ]
    
    # Test cases that should still pass
    should_accept = [
        "Refried Beans",
        "Baharat-Spiced Beef Topping for Hummus",
        "Scrambled Eggs with Pinto Beans and Cotija Cheese",
        "Classic Chicken Soup",
        "Grilled Salmon with Herbs"
    ]
    
    print("🧠 TESTING FINAL ENHANCEMENT - SENTENCE FRAGMENT DETECTION")
    print("=" * 70)
    
    print("\n🚫 Testing fragment rejection:")
    for title in should_reject:
        is_recipe_title = engine._is_recipe_title(title)
        status = "✅ REJECTED" if not is_recipe_title else "❌ ACCEPTED"
        print(f"  {status}: '{title}'")
    
    print("\n✅ Testing proper title acceptance:")
    for title in should_accept:
        is_recipe_title = engine._is_recipe_title(title)
        status = "✅ ACCEPTED" if is_recipe_title else "❌ REJECTED"
        print(f"  {status}: '{title}'")

if __name__ == "__main__":
    test_final_enhancement()
