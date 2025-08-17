#!/usr/bin/env python3
"""
Test deployment and database connection
"""
import requests
import time

def test_deployment():
    app_url = "https://yeschefapp-production.up.railway.app"
    
    print("🔍 Testing Railway deployment and database connection...")
    
    # Test the new diagnostic endpoint
    print("\n1. Testing database diagnostic endpoint...")
    try:
        r = requests.get(f"{app_url}/api/admin/check-database", timeout=30)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test with a simple endpoint that should exist
    print("\n2. Testing basic app health...")
    try:
        r = requests.get(f"{app_url}/", timeout=30)
        print(f"App status: {r.status_code}")
    except Exception as e:
        print(f"App error: {e}")
    
    # Try intelligence migration with maximum diagnostics
    print("\n3. Testing intelligence migration with diagnostics...")
    try:
        r = requests.post(
            f"{app_url}/api/admin/migrate-recipes",
            headers={
                'Content-Type': 'application/json',
                'X-Admin-Key': 'migrate-recipes-2025'
            },
            json={"type": "intelligence", "debug": True, "full_diagnostics": True},
            timeout=120
        )
        print(f"Migration status: {r.status_code}")
        print(f"Migration response: {r.text}")
    except Exception as e:
        print(f"Migration error: {e}")

if __name__ == "__main__":
    test_deployment()
