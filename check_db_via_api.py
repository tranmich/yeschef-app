#!/usr/bin/env python3
"""
Simple database count check using the existing search API
"""
import requests

def check_database_via_api():
    app_url = "https://yeschefapp-production.up.railway.app"
    
    print("🔍 Checking database via various API endpoints...")
    
    # Try some basic search terms to see what we get
    test_queries = ['chicken', 'pasta', 'soup', 'salad', 'dessert']
    
    for query in test_queries:
        try:
            response = requests.post(
                f"{app_url}/api/suggestions",
                headers={'Content-Type': 'application/json'},
                json={
                    'query': query,
                    'session_id': 'test',
                    'limit': 100
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"Query '{query}': Found {len(result.get('recipes', []))} recipes")
                if result.get('recipes'):
                    print(f"  Sample recipe IDs: {[r.get('id') for r in result['recipes'][:5]]}")
            else:
                print(f"Query '{query}': Error {response.status_code}")
                
        except Exception as e:
            print(f"Query '{query}': Exception {e}")

    print("\n🔍 Testing direct search endpoint...")
    try:
        response = requests.post(
            f"{app_url}/api/search",
            headers={'Content-Type': 'application/json'},
            json={'query': ''},  # Empty query to get all
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Empty search: {result}")
        else:
            print(f"Empty search error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Search error: {e}")

if __name__ == "__main__":
    check_database_via_api()
