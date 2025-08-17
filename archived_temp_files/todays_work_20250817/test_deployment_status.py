#!/usr/bin/env python3
"""
Test Railway Deployment Status
Simple connectivity and basic response analysis
"""

import requests
import json
from datetime import datetime

BASE_URL = "https://yeschefapp-production.up.railway.app"

def test_basic_endpoints():
    """Test basic endpoints for any changes"""
    print("🔍 TESTING BASIC RAILWAY ENDPOINTS")
    print("=" * 50)
    
    endpoints = [
        "/api/health",
        "/api/search?q=test",
        "/api/version",  # Should exist if new code is deployed
        "/"  # Basic root endpoint
    ]
    
    for endpoint in endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            response = requests.get(url, timeout=10)
            
            print(f"\n{endpoint}:")
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                # Try to parse as JSON
                try:
                    data = response.json()
                    
                    # Look for specific indicators
                    if 'universal_search' in str(data):
                        print(f"  🎯 Universal search mention found!")
                    if 'enhanced_search_used' in str(data):
                        print(f"  📊 Enhanced search (old system) detected")
                    if 'version' in str(data):
                        print(f"  🔢 Version info: {data.get('version', 'Unknown')}")
                        
                    # Print relevant keys
                    if isinstance(data, dict):
                        relevant_keys = [k for k in data.keys() if any(word in k.lower() for word in ['search', 'version', 'universal', 'enhanced'])]
                        if relevant_keys:
                            print(f"  📋 Relevant keys: {relevant_keys}")
                            
                except:
                    # Not JSON, check for HTML indicators
                    if "Not Found" in response.text:
                        print(f"  ❌ Endpoint not found (404)")
                    elif len(response.text) < 200:
                        print(f"  📝 Response: {response.text[:100]}")
                    else:
                        print(f"  📄 HTML response ({len(response.text)} chars)")
                        
            else:
                print(f"  ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"  💥 Exception: {e}")

def check_deployment_indicators():
    """Look for any signs the deployment updated"""
    print(f"\n🕵️ CHECKING DEPLOYMENT INDICATORS")
    print("=" * 50)
    
    try:
        # Test search endpoint response format
        response = requests.get(f"{BASE_URL}/api/search", params={'q': 'chicken'}, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Analyze response format to detect version
            print(f"Response structure analysis:")
            
            if 'metadata' in data:
                metadata = data['metadata']
                print(f"  Metadata keys: {list(metadata.keys())}")
                
                # Old system indicators
                if 'enhanced_search_used' in metadata:
                    print(f"  🔴 OLD SYSTEM: enhanced_search_used = {metadata['enhanced_search_used']}")
                
                # New system indicators  
                if 'universal_search_used' in metadata:
                    print(f"  🟢 NEW SYSTEM: universal_search_used = {metadata['universal_search_used']}")
                    
                # Recipe intelligence indicators
                if data.get('data') and len(data['data']) > 0:
                    first_recipe = data['data'][0]
                    intelligence_fields = ['meal_role', 'is_easy', 'universal_search', 'intelligence_enabled']
                    present_fields = {field: first_recipe.get(field) for field in intelligence_fields if first_recipe.get(field) is not None}
                    
                    if present_fields:
                        print(f"  🧠 Intelligence fields found: {present_fields}")
                    else:
                        print(f"  ❌ No intelligence fields in recipes")
                        
    except Exception as e:
        print(f"Error checking indicators: {e}")

if __name__ == "__main__":
    print("🚀 RAILWAY DEPLOYMENT STATUS CHECK")
    print("=" * 60)
    print(f"Target: {BASE_URL}")
    print(f"Time: {datetime.now()}")
    
    test_basic_endpoints()
    check_deployment_indicators()
    
    print("\n" + "=" * 60)
    print("🎯 ANALYSIS COMPLETE")
    print("\nIf /api/version returns 404, the latest code is NOT deployed")
    print("If enhanced_search_used appears, the OLD system is running")
    print("If universal_search_used appears, the NEW system is running")
