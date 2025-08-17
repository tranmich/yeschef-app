#!/usr/bin/env python3
"""
Debug migration: Check exactly what's happening
"""
import requests
import json

def debug_migration():
    app_url = "https://yeschefapp-production.up.railway.app"

    print("🔍 Starting debug migration...")

    try:
        response = requests.post(
            f"{app_url}/api/admin/migrate-recipes",
            headers={
                'Content-Type': 'application/json',
                'X-Admin-Key': 'migrate-recipes-2025'
            },
            json={"type": "intelligence", "debug": True},
            timeout=300
        )

        print(f"Debug response: {response.status_code}")
        print(f"Response text: {response.text}")

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Debug successful: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Debug failed: {response.text}")

    except Exception as e:
        print(f"❌ Debug error: {e}")

if __name__ == "__main__":
    debug_migration()
