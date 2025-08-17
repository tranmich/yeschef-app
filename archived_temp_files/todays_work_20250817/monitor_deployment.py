#!/usr/bin/env python3
"""
Monitor Railway Deployment Progress
Wait for universal search consolidation to go live
"""

import requests
import time
import json
from datetime import datetime

BASE_URL = "https://yeschefapp-production.up.railway.app"

def check_universal_search_status():
    """Check if universal search is active"""
    try:
        response = requests.get(f"{BASE_URL}/api/search", 
                              params={'q': 'test'}, 
                              timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for universal search indicators
            universal_active = data.get('universal_search', False)
            metadata = data.get('metadata', {})
            enhanced_search = metadata.get('enhanced_search_used', False)
            universal_search_used = metadata.get('universal_search_used', False)
            
            return {
                'status': 'success',
                'universal_search': universal_active,
                'universal_search_used': universal_search_used,
                'enhanced_search_used': enhanced_search,
                'deployment_status': 'new' if universal_active else 'old'
            }
        else:
            return {
                'status': 'error',
                'code': response.status_code,
                'deployment_status': 'unknown'
            }
            
    except Exception as e:
        return {
            'status': 'exception',
            'error': str(e),
            'deployment_status': 'unknown'
        }

def monitor_deployment(max_checks=10, interval=30):
    """Monitor deployment progress"""
    print("🚀 MONITORING RAILWAY DEPLOYMENT")
    print("=" * 50)
    print(f"Waiting for universal search consolidation to deploy...")
    print(f"Max checks: {max_checks}, Interval: {interval}s")
    print()
    
    for check in range(1, max_checks + 1):
        print(f"Check {check}/{max_checks} at {datetime.now().strftime('%H:%M:%S')}")
        
        status = check_universal_search_status()
        
        print(f"  Status: {status['status']}")
        print(f"  Deployment: {status['deployment_status']}")
        
        if status['deployment_status'] == 'new':
            print(f"  🎉 UNIVERSAL SEARCH IS LIVE!")
            print(f"  - Universal Search Flag: {status['universal_search']}")
            print(f"  - Universal Search Used: {status['universal_search_used']}")
            return True
        elif status['deployment_status'] == 'old':
            print(f"  ⏳ Still running old deployment")
            print(f"  - Enhanced Search Used: {status.get('enhanced_search_used', 'Unknown')}")
        else:
            print(f"  ❓ Unknown deployment status")
        
        if check < max_checks:
            print(f"  Waiting {interval} seconds...")
            print()
            time.sleep(interval)
    
    print("🔚 Monitoring complete - manual check recommended")
    return False

if __name__ == "__main__":
    print("🔍 UNIVERSAL SEARCH DEPLOYMENT MONITOR")
    print("=" * 60)
    print(f"Target: {BASE_URL}")
    print(f"Time: {datetime.now()}")
    print()
    
    # Initial check
    initial_status = check_universal_search_status()
    print(f"Initial Status: {initial_status['deployment_status']}")
    
    if initial_status['deployment_status'] == 'new':
        print("🎉 Universal search is already live!")
    else:
        # Monitor for changes
        success = monitor_deployment(max_checks=8, interval=45)
        
        if success:
            print("\n✅ DEPLOYMENT SUCCESSFUL!")
            print("🔍 Universal search consolidation is now live in production")
        else:
            print("\n⏳ DEPLOYMENT STILL IN PROGRESS")
            print("🔍 Check again manually or increase monitoring time")
