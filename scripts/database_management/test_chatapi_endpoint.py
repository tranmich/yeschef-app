#!/usr/bin/env python3
"""
Test ChatAPI Endpoint Directly
Tests the actual HTTP endpoint that the frontend calls
"""

import requests
import json
import sys

def test_chatapi_endpoint():
    """Test the actual ChatAPI endpoint"""
    
    print("🧪 TESTING CHATAPI ENDPOINT")
    print("=" * 40)
    
    # Server details
    server_url = "http://127.0.0.1:5000"
    endpoint = "/api/smart-search"
    full_url = f"{server_url}{endpoint}"
    
    print(f"🌐 Server URL: {full_url}")
    
    # Test data (simulating frontend request)
    test_data = {
        "message": "I want some chicken recipes",
        "context": "",
        "session_id": "test_session_123"
    }
    
    print(f"📤 Sending request...")
    print(f"   Message: '{test_data['message']}'")
    print(f"   Session ID: {test_data['session_id']}")
    
    try:
        # Make the POST request
        response = requests.post(
            full_url,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\n📨 RESPONSE STATUS: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Request successful!")
            
            # Parse JSON response
            try:
                data = response.json()
                print(f"\n📋 RESPONSE DATA:")
                print(f"   Success: {data.get('success', False)}")
                
                if 'data' in data:
                    response_data = data['data']
                    print(f"   AI Response: {response_data.get('response', 'No response')[:100]}...")
                    
                    if 'recipes' in response_data:
                        recipes = response_data['recipes']
                        print(f"   Recipes Found: {len(recipes)}")
                        
                        if len(recipes) > 0:
                            first_recipe = recipes[0]
                            print(f"   Sample Recipe: {first_recipe.get('title', 'No title')}")
                            print(f"   Recipe ID: {first_recipe.get('id', 'No ID')}")
                            return True
                        else:
                            print("   ❌ No recipes in response")
                            return False
                    else:
                        print("   ❌ No 'recipes' field in response")
                        return False
                else:
                    print("   ❌ No 'data' field in response")
                    return False
                    
            except json.JSONDecodeError as e:
                print(f"   ❌ Failed to parse JSON response: {e}")
                print(f"   Raw response: {response.text[:200]}...")
                return False
                
        else:
            print(f"❌ Request failed!")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed!")
        print("   Is the server running on http://127.0.0.1:5000?")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out!")
        print("   Server may be overloaded or not responding")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_server_health():
    """Test if server is responding at all"""
    
    print("\n🏥 TESTING SERVER HEALTH")
    print("=" * 30)
    
    server_url = "http://127.0.0.1:5000"
    
    try:
        response = requests.get(f"{server_url}/api/health", timeout=10)
        
        if response.status_code == 200:
            print("✅ Server health check passed")
            data = response.json()
            print(f"   Status: {data.get('status', 'Unknown')}")
            print(f"   Database: {data.get('database', 'Unknown')}")
            return True
        else:
            print(f"⚠️  Health check returned {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def main():
    """Run all tests"""
    
    print("🚀 CHATAPI ENDPOINT TESTING")
    print("=" * 50)
    
    # Test 1: Server health
    health_ok = test_server_health()
    
    # Test 2: ChatAPI endpoint
    if health_ok:
        chatapi_ok = test_chatapi_endpoint()
        
        if chatapi_ok:
            print(f"\n🎉 ALL TESTS PASSED!")
            print("✅ Server is running")
            print("✅ ChatAPI endpoint is working")
            print("✅ Recipe data is being returned")
            print("\n💡 If the frontend isn't getting data, check:")
            print("   - Frontend is making requests to the right URL")
            print("   - CORS settings are correct")
            print("   - Frontend error handling")
        else:
            print(f"\n❌ CHATAPI ENDPOINT FAILED")
            print("✅ Server is running")
            print("❌ ChatAPI endpoint has issues")
    else:
        print(f"\n❌ SERVER NOT RESPONDING")
        print("❌ Server health check failed")
        print("💡 Make sure server is running: python hungie_server.py")

if __name__ == "__main__":
    main()
