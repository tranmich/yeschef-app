#!/usr/bin/env python3
"""
Check total recipes in database
"""
import requests

def check_recipes():
    app_url = "https://yeschefapp-production.up.railway.app"
    
    print("🔍 Checking total recipes...")
    
    try:
        # Try to get a recipe count via search API
        response = requests.get(
            f"{app_url}/api/search?query=*&limit=1",
            timeout=30
        )
        
        print(f"Search response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Search result: {result}")
        else:
            print(f"❌ Search failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_recipes()
