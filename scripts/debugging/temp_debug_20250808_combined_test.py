#!/usr/bin/env python3
"""
Combined Server and Test
Created: 2025-08-08
Purpose: Start server and test API in sequence
"""

import sys
import os
import threading
import time
import requests
import json

sys.path.insert(0, os.path.abspath('.'))

def start_server():
    """Start the Flask server in a thread"""
    try:
        from hungie_server import app, logger
        print("🚀 Starting server in background thread...")
        app.run(
            host="127.0.0.1",
            port=5000,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except Exception as e:
        print(f"❌ Server error: {e}")

def test_api():
    """Test API endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Waiting for server to start...")
    time.sleep(3)
    
    print("🧪 Testing API endpoints...")
    
    # Test endpoints
    endpoints = [
        "/api/search?q=chicken",
        "/api/categories"
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
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    return True

if __name__ == "__main__":
    # Start server in background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Test API
    success = test_api()
    
    if success:
        print("\n🎉 API tests completed successfully!")
        print("✅ Backend server is working correctly on port 5000")
        print("💡 You can now update your frontend to use: http://localhost:5000")
    else:
        print("\n❌ API tests failed")
    
    print("\nPress Ctrl+C to stop the server...")
