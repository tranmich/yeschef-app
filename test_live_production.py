#!/usr/bin/env python3
"""
Live Production Testing - Universal Search Consolidation
Testing the deployed Railway backend with real PostgreSQL data
"""

import requests
import json
import time

# Railway backend URL
BASE_URL = "https://yeschefapp-production.up.railway.app"

def test_live_search_endpoints():
    """Test all search endpoints with the live Railway deployment"""
    print("🚀 TESTING LIVE UNIVERSAL SEARCH SYSTEM")
    print("=" * 60)
    print(f"Backend URL: {BASE_URL}")
    print(f"Testing Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = {}
    
    # Test 1: Basic Search API
    print("🔍 Test 1: Basic Search API")
    try:
        response = requests.get(f"{BASE_URL}/api/search", 
                              params={'q': 'chicken pasta'}, 
                              timeout=10)
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  Success: {data.get('success', False)}")
            print(f"  Total Results: {len(data.get('data', []))}")
            print(f"  Universal Search: {data.get('universal_search', False)}")
            print(f"  Intelligence Enabled: {data.get('metadata', {}).get('intelligence_enabled', False)}")
            
            # Show first recipe if available
            if data.get('data') and len(data['data']) > 0:
                first_recipe = data['data'][0]
                print(f"  Sample Recipe: '{first_recipe.get('title', 'N/A')}' (ID: {first_recipe.get('id', 'N/A')})")
                if first_recipe.get('universal_search'):
                    print(f"  ✅ Recipe has universal search metadata")
                if first_recipe.get('intelligence_enabled'):
                    print(f"  🧠 Recipe has intelligence features")
            
            results['basic_search'] = {
                'status': response.status_code,
                'success': data.get('success', False),
                'recipe_count': len(data.get('data', [])),
                'universal_search': data.get('universal_search', False)
            }
        else:
            print(f"  ❌ Failed with status {response.status_code}")
            results['basic_search'] = {'status': response.status_code, 'success': False}
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        results['basic_search'] = {'error': str(e)}
    
    print()
    
    # Test 2: Day 4 Smart-Search Route with Intelligence Filters
    print("🎯 Test 2: Day 4 Smart-Search Route with Intelligence Filters")
    try:
        payload = {
            'message': 'easy chicken dinner',  # Changed from 'query' to 'message'
            'filters': {
                'meal_role': 'dinner',
                'max_time': 30,
                'is_easy': True,
                'kid_friendly': True
            },
            'include_explanations': True
        }
        
        response = requests.post(f"{BASE_URL}/api/smart-search", 
                               json=payload, 
                               timeout=10)
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  Success: {data.get('success', False)}")
            print(f"  Universal Search: {data.get('universal_search', False)}")
            print(f"  Intelligence Enabled: {data.get('intelligence_enabled', False)}")
            print(f"  Filters Applied: {data.get('intelligence_filters_applied', False)}")
            print(f"  Recipe Count: {len(data.get('recipes', []))}")
            
            # Show intelligence features if available
            if data.get('recipes') and len(data['recipes']) > 0:
                first_recipe = data['recipes'][0]
                print(f"  Sample Recipe: '{first_recipe.get('title', 'N/A')}'")
                if first_recipe.get('explanations'):
                    print(f"  💡 Explanation: {first_recipe['explanations'][:100]}...")
                if first_recipe.get('meal_role'):
                    print(f"  🍽️ Meal Role: {first_recipe['meal_role']}")
                if first_recipe.get('is_easy'):
                    print(f"  ⚡ Easy Recipe: Yes")
            
            results['smart_search'] = {
                'status': response.status_code,
                'success': data.get('success', False),
                'intelligence_enabled': data.get('intelligence_enabled', False),
                'recipe_count': len(data.get('recipes', []))
            }
        else:
            print(f"  ❌ Failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"  Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"  Raw response: {response.text[:200]}")
            results['smart_search'] = {'status': response.status_code, 'success': False}
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        results['smart_search'] = {'error': str(e)}
    
    print()
    
    # Test 3: Intelligent Session-Aware Search
    print("🧠 Test 3: Intelligent Session-Aware Search")
    try:
        payload = {
            'query': 'pasta recipes',
            'session_id': 'test_session_' + str(int(time.time())),
            'shown_recipe_ids': [],
            'page_size': 5
        }
        
        response = requests.post(f"{BASE_URL}/api/search/intelligent", 
                               json=payload, 
                               timeout=10)
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  Success: {data.get('success', False)}")
            print(f"  Session Aware: {data.get('search_metadata', {}).get('session_aware', False)}")
            print(f"  Recipe Count: {len(data.get('recipes', []))}")
            print(f"  Has More: {data.get('has_more', False)}")
            print(f"  Total Available: {data.get('total_available', 0)}")
            
            if data.get('recipes'):
                print(f"  Sample Recipe: '{data['recipes'][0].get('title', 'N/A')}'")
                if data['recipes'][0].get('session_aware'):
                    print(f"  ✅ Recipe has session awareness")
            
            results['intelligent_search'] = {
                'status': response.status_code,
                'success': data.get('success', False),
                'session_aware': data.get('search_metadata', {}).get('session_aware', False),
                'recipe_count': len(data.get('recipes', []))
            }
        else:
            print(f"  ❌ Failed with status {response.status_code}")
            results['intelligent_search'] = {'status': response.status_code, 'success': False}
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        results['intelligent_search'] = {'error': str(e)}
    
    print()
    
    # Test 4: Database Health Check
    print("🏥 Test 4: Database Health Check")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  Database Connected: {data.get('database_connection', False)}")
            print(f"  Recipe Count: {data.get('recipe_count', 'Unknown')}")
            print(f"  Universal Search Ready: {data.get('universal_search_ready', False)}")
            
            results['health_check'] = {
                'status': response.status_code,
                'database_connected': data.get('database_connection', False),
                'recipe_count': data.get('recipe_count', 0)
            }
        else:
            print(f"  ❌ Health check failed")
            results['health_check'] = {'status': response.status_code}
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        results['health_check'] = {'error': str(e)}
    
    print()
    
    # Test 5: Simple Recipe Count Test
    print("🔢 Test 5: Recipe Count Verification")
    try:
        # Test with a very simple query to see actual recipe access
        response = requests.get(f"{BASE_URL}/api/search", 
                              params={'q': 'chicken'}, 
                              timeout=10)
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            recipe_count = len(data.get('data', []))
            print(f"  Recipes Retrieved: {recipe_count}")
            print(f"  Database Access: {'✅ Working' if recipe_count > 0 else '❌ No Data'}")
            
            # Check if we're getting the expected 728 recipes or a subset
            if recipe_count > 0:
                sample_recipe = data['data'][0]
                print(f"  Sample Recipe: '{sample_recipe.get('title')}'")
                print(f"  Has Intelligence Data: {bool(sample_recipe.get('intelligence_enabled'))}")
                
                # Look for intelligence metadata
                intelligence_fields = ['meal_role', 'is_easy', 'is_one_pot', 'kid_friendly']
                intelligence_count = sum(1 for field in intelligence_fields if sample_recipe.get(field) is not None)
                print(f"  Intelligence Fields Present: {intelligence_count}/{len(intelligence_fields)}")
            
            results['recipe_verification'] = {
                'status': response.status_code,
                'recipe_count': recipe_count,
                'database_working': recipe_count > 0
            }
        else:
            print(f"  ❌ Failed to retrieve recipes")
            results['recipe_verification'] = {'status': response.status_code}
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        results['recipe_verification'] = {'error': str(e)}
    
    print()
    print("📊 LIVE TESTING SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results.values() if r.get('status') == 200 and r.get('success', False))
    
    print(f"Tests Completed: {total_tests}")
    print(f"Successful Tests: {successful_tests}")
    print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    print("\n🎯 Key Findings:")
    
    if results.get('basic_search', {}).get('universal_search'):
        print("  ✅ Universal Search Engine: OPERATIONAL")
    
    if results.get('smart_search', {}).get('intelligence_enabled'):
        print("  ✅ Day 4 Intelligence Filters: OPERATIONAL")
        
    if results.get('intelligent_search', {}).get('session_aware'):
        print("  ✅ Session-Aware Search: OPERATIONAL")
        
    if results.get('health_check', {}).get('database_connected'):
        print("  ✅ PostgreSQL Database: CONNECTED")
        recipe_count = results.get('health_check', {}).get('recipe_count', 0)
        if recipe_count > 0:
            print(f"  ✅ Recipe Database: {recipe_count} recipes available")
    
    print(f"\n🎊 UNIVERSAL SEARCH CONSOLIDATION: {'SUCCESS' if successful_tests >= 3 else 'NEEDS ATTENTION'}")
    
    return results

if __name__ == "__main__":
    test_live_search_endpoints()
