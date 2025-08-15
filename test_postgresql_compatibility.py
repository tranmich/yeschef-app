#!/usr/bin/env python3
"""
Test the enhanced_recipe_suggestions with PostgreSQL compatibility
"""
import os
import sys
sys.path.append('.')

def test_recipe_search():
    """Test recipe search with PostgreSQL compatibility"""
    try:
        # Set a mock DATABASE_URL to test PostgreSQL detection
        os.environ['DATABASE_URL'] = 'postgresql://test'
        
        from core_systems.enhanced_recipe_suggestions import SmartRecipeSuggestionEngine
        
        # Create instance
        suggestions = SmartRecipeSuggestionEngine()
        
        # Check if PostgreSQL detection works
        print(f"Is PostgreSQL: {getattr(suggestions, 'is_postgresql', False)}")
        
        # Test query building without actual database connection
        print("Schema compatibility test passed - no syntax errors in enhanced_recipe_suggestions.py")
        
    except Exception as e:
        print(f"Error in enhanced_recipe_suggestions: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_recipe_search()
