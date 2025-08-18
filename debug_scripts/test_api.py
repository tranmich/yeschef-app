"""
🌐 API Testing Script
=====================

Test the pantry toggle API endpoints
"""

import requests
import json
import time

def test_api_endpoints():
    """Test all the configuration API endpoints"""
    
    base_url = "http://localhost:5000"
    
    print("🌐 TESTING PANTRY TOGGLE API ENDPOINTS")
    print("=" * 50)
    
    # Test 1: Get current configuration
    print("\n1️⃣ Testing GET /api/config")
    try:
        response = requests.get(f"{base_url}/api/config")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data['success']}")
            print(f"   Config: {json.dumps(data['config'], indent=4)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Connection Error: {e}")
        print("   Make sure the server is running!")
        return False
    
    # Test 2: Toggle pantry system
    print("\n2️⃣ Testing POST /api/config/pantry/toggle")
    try:
        response = requests.post(f"{base_url}/api/config/pantry/toggle")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data['success']}")
            print(f"   Pantry Enabled: {data['pantry_enabled']}")
            print(f"   Message: {data['message']}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Toggle again
    print("\n3️⃣ Testing POST /api/config/pantry/toggle (again)")
    try:
        response = requests.post(f"{base_url}/api/config/pantry/toggle")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data['success']}")
            print(f"   Pantry Enabled: {data['pantry_enabled']}")
            print(f"   Message: {data['message']}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Explicitly disable
    print("\n4️⃣ Testing POST /api/config/pantry/disable")
    try:
        response = requests.post(f"{base_url}/api/config/pantry/disable")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data['success']}")
            print(f"   Pantry Enabled: {data['pantry_enabled']}")
            print(f"   Message: {data['message']}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 5: Explicitly enable
    print("\n5️⃣ Testing POST /api/config/pantry/enable")
    try:
        response = requests.post(f"{base_url}/api/config/pantry/enable")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data['success']}")
            print(f"   Pantry Enabled: {data['pantry_enabled']}")
            print(f"   Message: {data['message']}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 6: Final configuration check
    print("\n6️⃣ Final configuration check")
    try:
        response = requests.get(f"{base_url}/api/config")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Final Config:")
            config = data['config']
            pantry_status = "🟢 ENABLED" if config['pantry_enabled'] else "🔴 DISABLED"
            print(f"   🥫 Pantry System: {pantry_status}")
            print(f"   🔍 Pantry Search: {'🟢 ENABLED' if config['pantry_search_enabled'] else '🔴 DISABLED'}")
            print(f"   📅 Expiry Tracking: {'🟢 ENABLED' if config['expiry_tracking_enabled'] else '🔴 DISABLED'}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n✅ API TESTING COMPLETE!")
    return True

if __name__ == "__main__":
    # Check if requests is available
    try:
        import requests
    except ImportError:
        print("❌ requests library not found!")
        print("Install with: pip install requests")
        exit(1)
    
    print("🚀 Starting API tests...")
    print("Make sure the server is running with: python hungie_server.py")
    print()
    
    # Wait a moment for server to be ready
    time.sleep(1)
    
    test_api_endpoints()
