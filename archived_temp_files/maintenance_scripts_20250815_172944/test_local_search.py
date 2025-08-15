#!/usr/bin/env python3
"""Test script to locally test the recipe search functionality"""

import os
import sys
sys.path.append('.')
sys.path.append('./core_systems')

from core_systems.enhanced_recipe_suggestions import SmartRecipeSuggestionEngine

def test_search():
    # Test the search functionality
    try:
        search_engine = SmartRecipeSuggestionEngine()
        
        print("Testing recipe search with 'chicken recipes'...")
        
        # Test search using the wrapper function (like the server does)
        from core_systems.enhanced_recipe_suggestions import get_smart_suggestions
        
        results = get_smart_suggestions(
            user_query="chicken recipes",
            session_id="test_session"
        )
        
        print(f"Search completed. Results: {results}")
        
        if results.get('recipes'):
            print(f"Found {len(results['recipes'])} recipes:")
            for i, recipe in enumerate(results['recipes'][:3]):  # Show first 3
                print(f"{i+1}. {recipe.get('title', 'No title')}")
        else:
            print("No recipes found")
            
    except Exception as e:
        import traceback
        print(f"Error during search: {e}")
        print("Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    test_search()
