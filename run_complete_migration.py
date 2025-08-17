#!/usr/bin/env python3
"""
Complete intelligence migration: Schema + Data
Runs via HTTP endpoint to avoid Railway connection issues
"""
import requests
import json
import os

def run_complete_migration():
    # Get Railway app URL
    app_url = "https://yeschefapp-production.up.railway.app"
    
    print("🚀 Starting complete intelligence migration...")
    
    # Step 1: Run schema migration
    print("\n📋 Step 1: Running schema migration...")
    
    try:
        response = requests.post(
            f"{app_url}/api/admin/run-schema-migration",
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer admin-token-2024'
            },
            json={"action": "add_intelligence_columns"},
            timeout=30
        )
        
        print(f"Schema migration response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Schema migration successful: {result}")
        else:
            print(f"❌ Schema migration failed: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Schema migration error: {e}")
        return
    
    # Step 2: Run data backfill
    print("\n🤖 Step 2: Running intelligence backfill...")
    
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
        
        print(f"Data backfill response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Data backfill successful: {result}")
        else:
            print(f"❌ Data backfill failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Data backfill error: {e}")

if __name__ == "__main__":
    run_complete_migration()
