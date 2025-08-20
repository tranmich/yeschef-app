#!/usr/bin/env python3
"""
Test our enhanced semantic validation to ensure it properly rejects fragments
"""

import sys
import os

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_systems.semantic_recipe_engine import SemanticRecipeEngine, ValidationLevel

def test_fragment_rejection():
    """Test that our enhanced semantic engine rejects obvious fragments"""
    
    engine = SemanticRecipeEngine(ValidationLevel.STRICT)
    
    # Test cases: titles that SHOULD be rejected (fragments)
    fragment_titles = [
        "Soup",
        "Salad", 
        "2½ cups chicken broth",
        "saucepan. Stir in 2 teaspoons soy sauce",
        "Sauce",
        "1 tablespoon olive oil",
        "remaining ingredients",
        "Transfer to serving bowl",
        "Makes 4 servings",
        "30 minutes",
        "(see page 45)",
        "continued...",
        "additional salt and pepper to taste",
        "mixture is smooth",
        "until tender"
    ]
    
    # Test cases: titles that SHOULD be accepted (proper recipe names)
    proper_titles = [
        "Refried Beans",
        "Classic Chicken Soup",
        "Grilled Salmon with Herbs",
        "Italian Pasta Salad",
        "Perfect Roast Chicken",
        "Easy Beef Stew",
        "Homemade Pizza Dough",
        "Chocolate Chip Cookies",
        "Traditional Ratatouille",
        "Pan-Fried Fish Tacos"
    ]
    
    print("🧠 TESTING ENHANCED SEMANTIC VALIDATION")
    print("=" * 60)
    
    # Test fragment rejection
    print("\n🚫 TESTING FRAGMENT REJECTION:")
    rejected_count = 0
    for title in fragment_titles:
        result = engine.validate_complete_recipe({
            'title': title,
            'ingredients': "• 1 cup test ingredient",
            'instructions': "1. Test instruction step."
        })
        
        is_valid = result.is_valid_recipe
        confidence = result.confidence_score
        
        if not is_valid:
            rejected_count += 1
            print(f"  ✅ REJECTED: '{title}' (confidence: {confidence:.2f})")
        else:
            print(f"  ❌ ACCEPTED: '{title}' (confidence: {confidence:.2f}) - SHOULD BE REJECTED!")
    
    print(f"\n  📊 Fragment Rejection: {rejected_count}/{len(fragment_titles)} properly rejected")
    
    # Test proper title acceptance
    print("\n✅ TESTING PROPER TITLE ACCEPTANCE:")
    accepted_count = 0
    for title in proper_titles:
        result = engine.validate_complete_recipe({
            'title': title,
            'ingredients': "• 1 cup test ingredient\n• 2 tablespoons olive oil",
            'instructions': "1. Test instruction step.\n2. Another cooking step."
        })
        
        is_valid = result.is_valid_recipe
        confidence = result.confidence_score
        
        if is_valid:
            accepted_count += 1
            print(f"  ✅ ACCEPTED: '{title}' (confidence: {confidence:.2f})")
        else:
            print(f"  ❌ REJECTED: '{title}' (confidence: {confidence:.2f}) - SHOULD BE ACCEPTED!")
    
    print(f"\n  📊 Proper Title Acceptance: {accepted_count}/{len(proper_titles)} properly accepted")
    
    # Summary
    total_correct = rejected_count + accepted_count
    total_tests = len(fragment_titles) + len(proper_titles)
    accuracy = (total_correct / total_tests) * 100
    
    print(f"\n🎯 OVERALL VALIDATION ACCURACY: {accuracy:.1f}%")
    print(f"   - Fragments rejected: {rejected_count}/{len(fragment_titles)}")
    print(f"   - Proper titles accepted: {accepted_count}/{len(proper_titles)}")
    
    if accuracy >= 90:
        print("🎉 EXCELLENT! Enhanced validation working correctly!")
    elif accuracy >= 75:
        print("⚠️ GOOD but needs some tuning")
    else:
        print("❌ NEEDS SIGNIFICANT IMPROVEMENT")
    
    return accuracy

if __name__ == "__main__":
    test_fragment_rejection()
