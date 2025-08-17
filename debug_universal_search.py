#!/usr/bin/env python3
"""
Debug Universal Search System in Production
Comprehensive debugging of the universal search consolidation
"""

import requests
import json
from datetime import datetime

BASE_URL = "https://yeschefapp-production.up.railway.app"

def test_basic_search_debug():
    """Test basic search with detailed error analysis"""
    print("🔍 DEBUGGING BASIC SEARCH ENDPOINT")
    print("=" * 60)
    
    try:
        # Test with a simple query
        response = requests.get(f"{BASE_URL}/api/search", 
                              params={'q': 'chicken'}, 
                              timeout=15)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Analyze the response structure
            print(f"\nResponse Structure:")
            print(f"  - success: {data.get('success')}")
            print(f"  - data: {type(data.get('data', []))} with {len(data.get('data', []))} items")
            print(f"  - metadata: {data.get('metadata', 'Not present')}")
            print(f"  - universal_search: {data.get('universal_search')}")
            
            # Check first recipe structure
            if data.get('data') and len(data['data']) > 0:
                first_recipe = data['data'][0]
                print(f"\nFirst Recipe Analysis:")
                print(f"  - title: {first_recipe.get('title')}")
                print(f"  - id: {first_recipe.get('id')}")
                print(f"  - universal_search: {first_recipe.get('universal_search')}")
                print(f"  - intelligence_enabled: {first_recipe.get('intelligence_enabled')}")
                print(f"  - meal_role: {first_recipe.get('meal_role')}")
                print(f"  - is_easy: {first_recipe.get('is_easy')}")
                print(f"  - explanations: {first_recipe.get('explanations', 'None')}")
                
                # Check for intelligence fields
                intelligence_fields = ['meal_role', 'is_easy', 'is_one_pot', 'kid_friendly', 'time_min']
                intelligence_present = {field: first_recipe.get(field) for field in intelligence_fields}
                print(f"  - Intelligence fields: {intelligence_present}")
                
            # Check metadata if present
            if 'metadata' in data:
                metadata = data['metadata']
                print(f"\nMetadata Analysis:")
                print(f"  - universal_search_used: {metadata.get('universal_search_used')}")
                print(f"  - intelligence_enabled: {metadata.get('intelligence_enabled')}")
                print(f"  - features: {metadata.get('features')}")
                
        else:
            print(f"Error Response: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

def test_universal_search_engine_direct():
    """Test if we can hit the server and get any response"""
    print(f"\n🚀 TESTING SERVER CONNECTIVITY")
    print("=" * 60)
    
    try:
        # Test basic connectivity
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        print(f"Health Check Status: {response.status_code}")
        
        if response.status_code == 200:
            health_data = response.json()
            print(f"Health Data: {json.dumps(health_data, indent=2)}")
            
            # Check specifically for universal search capabilities
            capabilities = health_data.get('capabilities', {})
            print(f"\nUniversal Search Detection:")
            print(f"  - Database Connection: {capabilities.get('database_connection')}")
            print(f"  - Recipe Count: {capabilities.get('recipe_count')}")
            print(f"  - Enhanced Search: {capabilities.get('enhanced_search')}")
            
    except Exception as e:
        print(f"Health check failed: {e}")

def test_direct_database_check():
    """Check if recipes are being returned with intelligence data"""
    print(f"\n📊 TESTING RECIPE DATA QUALITY")
    print("=" * 60)
    
    try:
        # Get a small sample of recipes to check intelligence data
        response = requests.get(f"{BASE_URL}/api/search", 
                              params={'q': 'pasta'}, 
                              timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            recipes = data.get('data', [])
            
            print(f"Found {len(recipes)} recipes")
            
            # Analyze first 3 recipes for intelligence data
            for i, recipe in enumerate(recipes[:3]):
                print(f"\nRecipe {i+1}: {recipe.get('title')}")
                print(f"  - Has meal_role: {recipe.get('meal_role') is not None}")
                print(f"  - Has is_easy: {recipe.get('is_easy') is not None}")
                print(f"  - Has is_one_pot: {recipe.get('is_one_pot') is not None}")
                print(f"  - Has kid_friendly: {recipe.get('kid_friendly') is not None}")
                print(f"  - Has explanations: {bool(recipe.get('explanations', '').strip())}")
                print(f"  - Intelligence enabled flag: {recipe.get('intelligence_enabled')}")
                print(f"  - Universal search flag: {recipe.get('universal_search')}")
                
            # Count recipes with intelligence data
            with_intelligence = sum(1 for r in recipes if any([
                r.get('meal_role'),
                r.get('is_easy') is not None,
                r.get('is_one_pot') is not None,
                r.get('kid_friendly') is not None
            ]))
            
            print(f"\nIntelligence Summary:")
            print(f"  - Recipes with intelligence: {with_intelligence}/{len(recipes)}")
            print(f"  - Intelligence percentage: {(with_intelligence/len(recipes)*100):.1f}%")
            
        else:
            print(f"Failed to get recipes: {response.status_code}")
            
    except Exception as e:
        print(f"Recipe analysis failed: {e}")

if __name__ == "__main__":
    print("🔬 UNIVERSAL SEARCH PRODUCTION DEBUGGING")
    print("=" * 80)
    print(f"Target: {BASE_URL}")
    print(f"Time: {datetime.now()}")
    print()
    
    test_universal_search_engine_direct()
    test_basic_search_debug()
    test_direct_database_check()
    
    print("\n" + "=" * 80)
    print("🎯 DEBUGGING COMPLETE")
