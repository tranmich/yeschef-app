#!/usr/bin/env python3
"""
Pantry Search Debug Test Script
Tests the ingredient search functionality with debugging
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def test_ingredient_search():
    """Test ingredient search with various queries"""
    print("🧪 Testing Pantry Ingredient Search with Debugging")
    print("=" * 50)
    
    # Test queries
    test_queries = [
        "",  # All ingredients
        "chicken",  # Protein search
        "onion",   # Produce search
        "salt",    # Seasoning search
        "xyz123"   # Non-existent ingredient
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing search query: '{query}'")
        try:
            # Make API request
            url = f"{BASE_URL}/api/ingredients"
            params = {'query': query} if query else {}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success! Found {data.get('count', 0)} ingredients")
                
                # Show sample results
                ingredients = data.get('ingredients', [])
                if ingredients:
                    print(f"📋 Sample results:")
                    for i, ingredient in enumerate(ingredients[:5]):
                        print(f"   {i+1}. {ingredient['name']} ({ingredient['category']})")
                    if len(ingredients) > 5:
                        print(f"   ... and {len(ingredients) - 5} more")
                else:
                    print("📋 No ingredients found")
                    
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection failed - is the server running on port 5000?")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Debug Instructions:")
    print("1. Check browser console for frontend logs")
    print("2. Check server terminal for backend logs") 
    print("3. Try searching in the frontend UI")

if __name__ == "__main__":
    test_ingredient_search()
