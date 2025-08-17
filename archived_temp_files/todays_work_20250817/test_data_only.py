#!/usr/bin/env python3
"""
Simple test to run just the data backfill part via Railway API
"""
import requests

def test_data_only():
    app_url = "https://yeschefapp-production.up.railway.app"
    
    print("🧪 Testing data backfill only...")
    
    try:
        response = requests.post(
            f"{app_url}/api/admin/migrate-recipes",
            headers={
                'Content-Type': 'application/json',
                'X-Admin-Key': 'migrate-recipes-2025'
            },
            json={"type": "intelligence"},
            timeout=60
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_data_only()
