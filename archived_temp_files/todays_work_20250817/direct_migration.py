#!/usr/bin/env python3
"""
Direct intelligence migration call with cache busting
"""
import requests
import time

def direct_migration():
    app_url = "https://yeschefapp-production.up.railway.app"
    
    print("🚀 Direct intelligence migration call...")
    
    # Add timestamp to bypass caching
    timestamp = int(time.time())
    
    try:
        response = requests.post(
            f"{app_url}/api/admin/migrate-recipes?t={timestamp}",
            headers={
                'Content-Type': 'application/json',
                'X-Admin-Key': 'migrate-recipes-2025',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            },
            json={"type": "intelligence", "timestamp": timestamp, "force_all": True},
            timeout=300
        )
        
        print(f"Response: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response text: {response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    direct_migration()
