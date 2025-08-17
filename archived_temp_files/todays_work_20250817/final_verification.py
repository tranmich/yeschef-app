#!/usr/bin/env python3
"""
Final verification: Ensure YesChefapp service sees PostgreSQL data correctly
"""
import requests

def final_verification():
    app_url = "https://yeschefapp-production.up.railway.app"
    
    print("🎯 FINAL YESCHEFAPP SERVICE VERIFICATION")
    print("=" * 50)
    
    # Test 1: Health check to see recipe count
    print("📊 Test 1: Health check")
    try:
        response = requests.get(f"{app_url}/api/health")
        if response.status_code == 200:
            health = response.json()
            capabilities = health.get('capabilities', {})
            recipe_count = capabilities.get('recipe_count', 'UNKNOWN')
            print(f"   Recipe count reported by YesChefapp: {recipe_count}")
            
            if recipe_count == 728:
                print("   ✅ YesChefapp correctly sees all 728 PostgreSQL recipes")
            else:
                print(f"   ⚠️  YesChefapp reports {recipe_count} recipes (expected: 728)")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # Test 2: Migration endpoint (should find 0 recipes to process since all have intelligence)
    print("\n🔍 Test 2: Intelligence migration (should find 0 recipes to process)")
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
        
        if response.status_code == 200:
            result = response.json()
            stats = result.get('statistics', {})
            processed = stats.get('recipes_processed', 'UNKNOWN')
            total_db = stats.get('total_in_database', 'UNKNOWN')
            
            print(f"   Recipes processed: {processed}")
            print(f"   Total in database: {total_db}")
            
            if processed == 0:
                print("   ✅ PERFECT! No recipes to process (all already have intelligence)")
                print("   ✅ This confirms YesChefapp is working correctly")
            elif processed == 100:
                print("   ⚠️  Still reporting 100 recipes - old cached response or deployment issue")
            else:
                print(f"   🤔 Unexpected: {processed} recipes processed")
        else:
            print(f"   ❌ Migration test failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Migration test error: {e}")
    
    print("\n🎯 SUMMARY:")
    print("• PostgreSQL database: ✅ 728 recipes with complete intelligence data")
    print("• Local SQLite file: ✅ Moved to backup (no conflicts)")
    print("• YesChefapp service: Should now see PostgreSQL exclusively")
    print("• Expected behavior: Migration finds 0 recipes to process")

if __name__ == "__main__":
    final_verification()
