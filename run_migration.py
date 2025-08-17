#!/usr/bin/env python3
"""
Simple migration runner for Railway
Run with: railway run python run_migration.py
"""

import requests
import json

def run_migration():
    """Call the migration endpoint"""
    url = "https://yeschefapp-production.up.railway.app/api/admin/migrate-intelligence"
    
    try:
        print("🚀 Calling migration endpoint...")
        response = requests.post(url, timeout=60)
        
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
