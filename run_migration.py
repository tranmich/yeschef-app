#!/usr/bin/env python3
"""
Simple migration runner for Railway
Run with: python run_migration.py
"""

import requests
import json

def run_migration():
    """Call the existing migration endpoint with intelligence flag"""
    url = "https://yeschefapp-production.up.railway.app/api/admin/migrate-recipes"
    
    # Send intelligence migration request
    payload = {"type": "intelligence"}
    headers = {"X-Admin-Key": "migrate-recipes-2025"}
    
    try:
        print("🚀 Calling intelligence migration endpoint...")
        response = requests.post(url, json=payload, headers=headers, timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Migration successful!")
            print(json.dumps(data, indent=2))
        else:
            print(f"❌ Migration failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_migration()
