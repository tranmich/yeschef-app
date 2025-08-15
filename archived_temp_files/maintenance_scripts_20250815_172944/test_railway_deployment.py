#!/usr/bin/env python3
"""
Test Chat API recipe search on Railway deployment
"""
import requests
import json

def test_railway_recipe_search():
    """Test recipe search functionality on Railway"""
    # Your Railway URL (replace with actual URL)
    BASE_URL = "https://your-railway-app.railway.app"  # Replace with actual Railway URL
    
    # Test endpoints
    test_cases = [
        {
            "description": "Simple ingredient search",
            "endpoint": "/chat/recipes",
            "data": {
                "message": "chicken recipes",
                "user_id": "test_user_123"
            }
        },
        {
            "description": "Multiple ingredient search", 
            "endpoint": "/chat/recipes",
            "data": {
                "message": "chicken and rice dishes",
                "user_id": "test_user_123"
            }
        },
        {
            "description": "Quick meal search",
            "endpoint": "/chat/recipes", 
            "data": {
                "message": "quick dinner ideas",
                "user_id": "test_user_123"
            }
        }
    ]
    
    print("Testing Railway Chat API Recipe Search...")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['description']}")
        print(f"URL: {BASE_URL}{test_case['endpoint']}")
        print(f"Data: {test_case['data']}")
        
        try:
            # Make request to Railway deployment
            response = requests.post(
                f"{BASE_URL}{test_case['endpoint']}", 
                json=test_case['data'],
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Success! Found {len(data.get('recipes', []))} recipes")
                
                # Show first recipe if any
                recipes = data.get('recipes', [])
                if recipes:
                    first_recipe = recipes[0]
                    print(f"First recipe: {first_recipe.get('title', 'No title')}")
                    print(f"Ingredients: {len(first_recipe.get('ingredients', []))} items")
                else:
                    print("No recipes returned")
            else:
                print(f"Error: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
        
        print("-" * 30)

if __name__ == "__main__":
    print("IMPORTANT: Replace BASE_URL with your actual Railway deployment URL")
    print("Example: https://me-hungie-production.up.railway.app")
    print()
    test_railway_recipe_search()
