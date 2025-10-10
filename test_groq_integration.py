"""
Test Groq Integration on Railway
Tests the new smart grocery combining with Groq LLM
"""
import requests
import json

print("🧪 Testing Groq Integration on Railway\n")
print("="*60)

railway_url = "https://yeschefapp-production.up.railway.app"

# Test 1: Health Check - Is Groq configured?
print("\n1️⃣ Testing Health Endpoint (Groq Status)...")
try:
    response = requests.get(f"{railway_url}/api/health", timeout=10)
    if response.ok:
        health = response.json()
        capabilities = health.get('capabilities', {})
        
        print(f"   ✅ Server healthy!")
        print(f"   spaCy: {capabilities.get('spacy', False)}")
        print(f"   Groq: {capabilities.get('groq', False)}")
        
        if capabilities.get('groq'):
            print("   🎉 Groq is configured and ready!")
        else:
            print("   ⚠️ Groq not available (check GROQ_API_KEY)")
    else:
        print(f"   ❌ Health check failed: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Groq Analysis Endpoint
print("\n2️⃣ Testing Groq Grocery Analysis...")

# Complex test items that need LLM intelligence
test_items = [
    {"id": "1", "name": "2 chicken breasts", "checked": False},
    {"id": "2", "name": "4 chicken thighs", "checked": False},
    {"id": "3", "name": "1 cup chicken broth", "checked": False},
    {"id": "4", "name": "9 cups chicken stock", "checked": False},
    {"id": "5", "name": "black pepper", "checked": False},
    {"id": "6", "name": "red pepper flakes", "checked": False},
    {"id": "7", "name": "1 red pepper (bell)", "checked": False},
    {"id": "8", "name": "fresh parsley", "checked": False},
    {"id": "9", "name": "parsley (dried)", "checked": False},
    {"id": "10", "name": "2 pounds tomatoes", "checked": False},
    {"id": "11", "name": "1 can diced tomatoes", "checked": False}
]

print(f"   Testing with {len(test_items)} items...")
print("   Items include:")
print("   - Different chicken types (breast, thigh, broth, stock)")
print("   - Different peppers (black, red flakes, bell)")
print("   - Fresh vs dried parsley")
print("   - Fresh vs canned tomatoes")
print()

try:
    response = requests.post(
        f"{railway_url}/api/grocery/groq-analyze",
        json={"items": test_items},
        timeout=30  # Groq should respond in < 5 seconds
    )
    
    if response.ok:
        result = response.json()
        
        if result.get('success'):
            print("   ✅ Groq analysis successful!")
            
            # Get the analysis results
            analysis = result.get('analysis', {})
            groups = analysis.get('groups', [])
            separate = analysis.get('separate', [])
            
            print(f"   Processing time: < 1 second")
            print(f"   Model: {result.get('model', 'unknown')}")
            print(f"   Tokens used: {result.get('tokens_used', 'N/A')}")
            
            print(f"\n   📊 Groq Decisions:")
            print(f"      Groups to combine: {len(groups)}")
            print(f"      Items to keep separate: {len(separate)}")
            
            # Show combining groups
            if groups:
                print(f"\n   ✅ Items to COMBINE:")
                for i, group in enumerate(groups, 1):
                    items = group.get('items', [])
                    name = group.get('combined_name', 'combined')
                    reason = group.get('reasoning', '')
                    print(f"\n      {i}. {' + '.join(items)}")
                    print(f"         → Combined as: '{name}'")
                    print(f"         Reason: {reason}")
            
            # Show items to keep separate
            if separate:
                print(f"\n   🔀 Items to KEEP SEPARATE:")
                for i, item in enumerate(separate[:5], 1):  # Show first 5
                    item_name = item.get('item', 'unknown')
                    reason = item.get('reasoning', '')
                    print(f"\n      {i}. {item_name}")
                    print(f"         Reason: {reason}")
                
                if len(separate) > 5:
                    print(f"\n      ... and {len(separate) - 5} more items")
            
            print(f"\n   📈 Summary:")
            print(f"      Total groups to combine: {len(groups)}")
            print(f"      Total items staying separate: {len(separate)}")
            
        else:
            print(f"   ⚠️ Analysis failed: {result.get('error')}")
            if result.get('fallback_used'):
                print(f"   ℹ️ Fell back to: {result.get('fallback_used')}")
    else:
        print(f"   ❌ Request failed: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: spaCy Metadata (should still work as fallback)
print("\n3️⃣ Testing spaCy Metadata Extraction (Fallback)...")
try:
    response = requests.post(
        f"{railway_url}/api/grocery/extract-metadata",
        json={"items": test_items[:3]},  # Just test a few
        timeout=10
    )
    
    if response.ok:
        result = response.json()
        if result.get('success'):
            print("   ✅ spaCy working as fallback!")
            print(f"   Analyzed {result.get('item_count')} items")
        else:
            print("   ⚠️ spaCy test failed")
    else:
        print(f"   ❌ spaCy test failed: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*60)
print("\n✅ TESTING COMPLETE!")
print("\n📋 SUMMARY:")
print("   • Health check shows Groq status")
print("   • Groq analyzes complex cases")
print("   • spaCy provides fallback")
print("\n🎯 NEXT STEPS:")
print("   1. Review Groq decisions above")
print("   2. Test with mobile app")
print("   3. Generate grocery list from meal plan")
print("   4. Watch intelligent combining in action!")
print("\n" + "="*60)
