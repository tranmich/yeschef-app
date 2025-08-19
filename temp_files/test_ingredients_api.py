#!/usr/bin/env python3
"""
Test the ingredients API to verify canonical_ingredients table data
"""

import requests

def test_ingredients_api():
    """Test the /api/ingredients endpoint"""
    try:
        print("🧪 Testing /api/ingredients endpoint...")
        response = requests.get('http://127.0.0.1:5000/api/ingredients')
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Status: {response.status_code}")
            print(f"📊 Total ingredients from your recipe database: {data.get('count', 0)}")
            
            print("\n🥫 Sample ingredients extracted from your recipes:")
            for i, ing in enumerate(data.get('ingredients', [])[:15]):
                print(f"  {i+1:2d}. {ing['name']} - {ing['category']}")
            
            if data.get('count', 0) > 15:
                print(f"  ... and {data.get('count', 0) - 15} more ingredients")
            
            print("\n🔍 Testing specific ingredient searches:")
            
            # Check for basic ingredients
            ingredients = data.get('ingredients', [])
            salt_found = any('salt' in ing['name'].lower() for ing in ingredients)
            pepper_found = any('pepper' in ing['name'].lower() for ing in ingredients)
            garlic_found = any('garlic' in ing['name'].lower() for ing in ingredients)
            
            print(f"  Salt found: {'✅' if salt_found else '❌'}")
            print(f"  Pepper found: {'✅' if pepper_found else '❌'}")
            print(f"  Garlic found: {'✅' if garlic_found else '❌'}")
            
            return True
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

if __name__ == "__main__":
    test_ingredients_api()
