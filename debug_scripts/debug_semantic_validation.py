#!/usr/bin/env python3
"""
Debug semantic validation in detail
"""

import sys, os
sys.path.append('.')
from core_systems.semantic_recipe_engine import SemanticRecipeEngine, ValidationLevel

def debug_semantic_validation():
    semantic_engine = SemanticRecipeEngine(ValidationLevel.STRICT)
    
    title = 'Perfect Scrambled Eggs'
    ingredients = '''8large whole eggs
2large yolks
¼cup half-and-half
⅜teaspoon table salt
¼teaspoon pepper
1tablespoon unsalted butter, chilled'''
    
    instructions = '''1. Beat eggs, y olks, hal f-and-hal f, salt, and pepper wi th fork unti l eggs ar e thor oughly combined and color is pur e yellow; do not
2. Heat but ter in 10-inch nonstick ski llet over medium-high heat unti l fully mel ted (but ter should not br own), swirl ing to coat pan. Add egg mixtur e and, using heatpr oof rubber spatula, constantly and firmly scrape along bot tom and sides of ski llet unti l eggs begin to clump and spatula just lea ves trail on bot tom of pan, 1½ to 2½ minutes. Reduce heat to low and gently but constantly f old eggs unti l clumped and just sl ightly wet, 30 to 60 seconds. I mmediately transfer eggs to w armed plates and season wi th sal t to taste. S erve immediately .'''
    
    print("=== TESTING SEMANTIC VALIDATION ===")
    print(f"Title: {title}")
    print(f"Ingredients: {ingredients}")
    print(f"Instructions: {instructions}")
    
    # Test each component
    print("\n=== COMPONENT VALIDATION ===")
    
    # Test title
    title_result = semantic_engine.classify_content_type(title)
    print(f"Title classification: {title_result}")
    
    # Test ingredients
    ingredient_result = semantic_engine.classify_content_type(ingredients)
    print(f"Ingredients classification: {ingredient_result}")
    
    # Test instructions
    instruction_result = semantic_engine.classify_content_type(instructions)
    print(f"Instructions classification: {instruction_result}")
    
    # Full validation
    result = semantic_engine.validate_complete_recipe({
        'title': title,
        'ingredients': ingredients,
        'instructions': instructions
    })
    
    print(f"\n=== FULL VALIDATION ===")
    print(f"Valid: {result.is_valid_recipe}")
    print(f"Confidence: {result.confidence_score}")
    print(f"Errors: {result.validation_errors}")
    print(f"Warnings: {result.validation_warnings}")

if __name__ == "__main__":
    debug_semantic_validation()
