#!/usr/bin/env python3
"""
Test semantic validation directly to see why it's rejecting the instructions
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_systems.semantic_recipe_engine import SemanticRecipeEngine

def test_semantic_validation():
    """Test semantic validation on our extracted components"""
    
    # These are the exact components we extracted
    title = "Refried Beans"
    
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

    instructions = """1. Process al l but 1 cup of beans wi th broth and sal t in food processor unti l smooth, about 15 seconds, scr aping down sides of workbowl wi th rubber spatula i f necessary . Add r emaining beans and pulse unti l slightly chunky , about 10 pulses.
2. Cook bacon in 12-inch nonstick ski llet over medium heat unti l bacon just begins to br own and most of f at has r ender ed, about 4 minutes. T ransfer to smal l bowl l ined wi th strainer; discar d bacon and add 1 tablespoon f at back to ski llet. Increase heat to medium- high; add onion, jalapeño , and cumin; and cook unti l softened and just starting to br own, 3 to 5 minutes. Stir in garl ic and cook unti l fragrant, about 30 seconds. R educe heat to medium, stir in pur eed beans, and cook unti l thick and cr eamy, 4 to 6 minutes. Of f heat, stir in cilantro and l ime juice."""

    print("=== Testing Semantic Validation ===")
    print(f"Title: {title}")
    print(f"Ingredients: {len(ingredients.split('•'))-1} items")
    print(f"Instructions: {len(instructions.split('.'))} steps")
    
    engine = SemanticRecipeEngine()
    
    # Test full recipe validation
    recipe_data = {
        'title': title,
        'ingredients': ingredients,
        'instructions': instructions
    }
    
    print("\n--- Full Recipe Validation ---")
    result = engine.validate_complete_recipe(recipe_data)
    print(f"Recipe valid: {result.is_valid_recipe}")
    print(f"Recipe confidence: {result.confidence_score}")
    print(f"Recipe errors: {result.validation_errors}")
    print(f"Recipe warnings: {result.validation_warnings}")
    
    # Let's also test the content type classification for each component
    print("\n--- Content Type Classification ---")
    title_type, title_conf = engine.classify_content_type(title)
    print(f"Title type: {title_type}, confidence: {title_conf}")
    
    ingredients_type, ingredients_conf = engine.classify_content_type(ingredients)
    print(f"Ingredients type: {ingredients_type}, confidence: {ingredients_conf}")
    
    instructions_type, instructions_conf = engine.classify_content_type(instructions)
    print(f"Instructions type: {instructions_type}, confidence: {instructions_conf}")

if __name__ == "__main__":
    test_semantic_validation()
