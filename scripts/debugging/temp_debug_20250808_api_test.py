#!/usr/bin/env python3
"""
API Test Client
Created: 2025-08-08
Purpose: Test API endpoints while server is running
"""

import requests
import json
import time

def test_api():
    """Test API endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing API endpoints...")
    
    # Test endpoints
    endpoints = [
        "/api/search?q=chicken",
        "/api/categories",
        "/api/search?q=beef"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\n🔍 Testing {endpoint}")
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            
            print(f"✅ Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success: {data.get('success', 'Unknown')}")
                
                if 'data' in data:
                    data_items = data['data']
                    if isinstance(data_items, list):
                        print(f"✅ Data count: {len(data_items)}")
                        if len(data_items) > 0:
                            first_item = data_items[0]
                            title = first_item.get('title', first_item.get('name', 'No title'))
                            print(f"✅ First item: {title}")
                    else:
                        print(f"✅ Data type: {type(data_items)}")
            else:
                print(f"❌ Error: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection failed - server not running")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api()
