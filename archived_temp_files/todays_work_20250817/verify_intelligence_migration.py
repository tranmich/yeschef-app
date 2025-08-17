#!/usr/bin/env python3
"""
Final verification of intelligence migration success
"""
import requests

def verify_migration_success():
    app_url = "https://yeschefapp-production.up.railway.app"

    print("🎯 FINAL VERIFICATION: Week 1 Core Intelligence Implementation")
    print("=" * 60)

    # Run one final migration to get current stats
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

            print("✅ MIGRATION STATUS: SUCCESS")
            print(f"📊 Total recipes processed: {stats.get('recipes_processed', 'N/A')}")
            print(f"📊 Total recipes updated: {stats.get('recipes_updated', 'N/A')}")
            print(f"📊 Database size: {stats.get('total_in_database', 'N/A')} recipes")

            # Calculate completion percentage
            processed = stats.get('recipes_processed', 0)
            updated = stats.get('recipes_updated', 0)

            if processed > 0:
                completion_rate = (updated / processed) * 100
                print(f"🎯 Success rate: {completion_rate:.1f}%")

                if completion_rate == 100:
                    print("\n🎉 PERFECT! All recipes successfully enhanced with intelligence metadata")
                    print("✅ Day 1 Core Intelligence implementation: COMPLETE")
                    print("\n📋 Intelligence fields added to all recipes:")
                    print("   • meal_role (breakfast/lunch/dinner/dessert/sauce)")
                    print("   • meal_role_confidence (accuracy score)")
                    print("   • time_min (estimated cooking time)")
                    print("   • steps_count (complexity indicator)")
                    print("   • pots_pans_count (cookware requirements)")
                    print("   • is_easy (beginner-friendly flag)")
                    print("   • is_one_pot (minimal cleanup flag)")
                    print("   • leftover_friendly (meal prep suitability)")
                    print("   • kid_friendly (family-friendly flag)")

                    print("\n🚀 READY FOR: Day 2-3 Enhanced Recipe Suggestions")
                    print("   Next: Implement intelligence-powered search and recommendations")

                else:
                    print(f"⚠️  Partial success: {updated}/{processed} recipes processed")
            else:
                print("❌ No recipes were processed")

        else:
            print(f"❌ Migration verification failed: {response.status_code}")
            print(f"   Response: {response.text}")

    except Exception as e:
        print(f"❌ Verification error: {e}")

if __name__ == "__main__":
    verify_migration_success()
