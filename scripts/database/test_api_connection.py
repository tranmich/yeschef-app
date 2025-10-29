"""
Quick API Diagnostic Script
Run this to check if backend is accessible and working
"""

import requests
import json
import sys

def test_endpoint(name, url, method='GET', headers=None, data=None):
    """Test a single endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print(f"Method: {method}")
    print(f"{'='*60}")
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=5)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=5)
        
        print(f"✅ Status: {response.status_code}")
        
        try:
            json_data = response.json()
            print(f"📄 Response: {json.dumps(json_data, indent=2)[:500]}...")
        except:
            print(f"📄 Response: {response.text[:500]}...")
        
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print(f"❌ CONNECTION ERROR: Cannot reach server")
        print(f"   - Check if server is running")
        print(f"   - Check if IP address is correct")
        print(f"   - Check if phone is on same WiFi")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ TIMEOUT: Server not responding")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("🔍 YesChef API Diagnostic Tool")
    print("="*60)
    
    # Base URL (update if needed)
    BASE_URL = "http://192.168.1.72:5000"
    print(f"\n🌐 Testing backend at: {BASE_URL}")
    
    results = {}
    
    # Test 1: Health Check
    results['health'] = test_endpoint(
        "Health Check",
        f"{BASE_URL}/api/health"
    )
    
    # Test 2: System Info
    results['system'] = test_endpoint(
        "System Info",
        f"{BASE_URL}/api/v2/system/info"
    )
    
    # Test 3: Login (if credentials provided)
    if len(sys.argv) >= 3:
        email = sys.argv[1]
        password = sys.argv[2]
        print(f"\n🔐 Testing login with: {email}")
        
        results['login'] = test_endpoint(
            "Login",
            f"{BASE_URL}/api/auth/login",
            method='POST',
            data={'email': email, 'password': password}
        )
    else:
        print("\n⏭️  Skipping login test (provide email & password as arguments)")
        print("   Usage: python test_api_connection.py email@example.com password")
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{test:15} {status}")
    
    print(f"\n🎯 Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed! Backend is working correctly.")
    elif results.get('health') == False:
        print("\n❌ CRITICAL: Cannot reach backend server!")
        print("\n🔧 TROUBLESHOOTING:")
        print("   1. Check if server is running:")
        print("      cd \"d:\\Mik\\Downloads\\Me Hungie\"")
        print("      python hungie_server.py")
        print("\n   2. Check your local IP:")
        print("      ipconfig | Select-String \"IPv4\"")
        print(f"      Current in script: {BASE_URL}")
        print("\n   3. Make sure phone is on same WiFi network")
    else:
        print("\n⚠️  Some tests failed. Check details above.")

if __name__ == '__main__':
    main()
