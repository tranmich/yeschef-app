#!/usr/bin/env python3
"""
Test Progressive Batching Logic
Verify that the Universal Search Engine can find more recipes as session progresses
"""

import sys
import os
sys.path.append('.')

from core_systems.universal_search import UniversalSearchEngine

def test_progressive_batching():
    print("🎯 TESTING PROGRESSIVE BATCHING SOLUTION")
    print("=" * 50)
    
    engine = UniversalSearchEngine()
    
    # Simulate a long session where user has seen many chicken recipes
    print("Scenario: User has been searching for chicken recipes in a long session")
    print()
    
    # Test with increasing exclusions
    scenarios = [
        {"session": "Fresh start", "exclusions": 0},
        {"session": "Early session", "exclusions": 8}, 
        {"session": "Mid session", "exclusions": 15},
        {"session": "Long session", "exclusions": 25},
        {"session": "Very long session", "exclusions": 40}
    ]
    
    for scenario in scenarios:
        print(f"📊 {scenario['session']} ({scenario['exclusions']} seen recipes)")
        
        # Create fake exclusion IDs
        exclude_ids = list(range(1, scenario['exclusions'] + 1))
        
        try:
            result = engine.unified_intelligent_search(
                query='chicken',
                session_memory={'session_id': 'test_session', 'shown_recipes': exclude_ids},
                user_pantry=[],
                exclude_ids=exclude_ids,
                limit=5,  # Request 5 recipes
                include_explanations=False
            )
            
            if result['success']:
                recipes_found = len(result['recipes'])
                total_searched = result.get('search_metadata', {}).get('total_searched', 'unknown')
                
                print(f"   ✅ Found: {recipes_found} recipes")
                if 'search_metadata' in result:
                    meta = result['search_metadata']
                    if 'progressive_limit' in meta:
                        print(f"   🎯 Progressive limit used: {meta['progressive_limit']}")
                    if meta.get('fallback_used'):
                        print(f"   🔄 Fallback was used")
                    if meta.get('exclusions_removed'):
                        print(f"   🔄 Exclusions were removed")
                        
                # Check if we're getting different recipes
                if recipes_found > 0:
                    print(f"   📝 Sample: {result['recipes'][0]['title']}")
                
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            
        print()
    
    print("🎉 Progressive batching test complete!")
    print()
    print("Expected behavior:")
    print("- Early sessions: Search 15-25 recipes")  
    print("- Long sessions: Search 40-65 recipes")
    print("- Always find results (with fallback if needed)")

if __name__ == "__main__":
    test_progressive_batching()
