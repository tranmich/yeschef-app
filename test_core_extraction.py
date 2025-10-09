"""
Test the problematic items that need better core extraction
"""
import requests
import json

print("🧪 Testing Problematic Items\n")
print("="*60)

# Problematic test items
test_items = [
    {'id': '1', 'name': '9 cups Chicken Stock'},
    {'id': '2', 'name': '0.5 cup Chicken Broth'},
    {'id': '3', 'name': '2 pounds Manila Clams (scrubbed well)'},
    {'id': '4', 'name': 'Salt And Pepper To Taste (as needed)'},
    {'id': '5', 'name': '1 ounce Parmesan (~1/4 cup)'},
    {'id': '6', 'name': '2 Garlic Cloves (minced)'},
    {'id': '7', 'name': '2 Parsley Sprigs'},
    {'id': '8', 'name': '1 tsp Red Pepper Flakes'},
    {'id': '9', 'name': '1 tablespoon Lemon Juice'},
    {'id': '10', 'name': '1 tablespoon Finely Chopped Parsley'},
    {'id': '11', 'name': '1 tablespoon Chopped Parsley'},
    {'id': '12', 'name': '0.25 cup Finely Chopped Parsley Leaves'},
]

print("\n📥 Test Items:")
for item in test_items:
    print(f"  - {item['name']}")

# Test the endpoint
url = 'http://192.168.1.72:5000/api/grocery/extract-metadata'
print(f"\n🔗 Testing URL: {url}")

try:
    response = requests.post(
        url,
        json={'items': test_items},
        timeout=5
    )
    
    print(f"\n✅ Response Status: {response.status_code}")
    
    if response.ok:
        result = response.json()
        
        if result.get('success'):
            print(f"✅ Success! Metadata received for {result.get('item_count')} items")
            
            print("\n📤 Core Ingredient Results:")
            print("-" * 60)
            
            # Group by core ingredient
            core_groups = {}
            for item_id, meta in result.get('metadata', {}).items():
                item = next(i for i in test_items if i['id'] == item_id)
                core = meta.get('core_ingredient')
                
                if core not in core_groups:
                    core_groups[core] = []
                core_groups[core].append(item['name'])
            
            # Show groups
            for core, items in sorted(core_groups.items()):
                print(f"\n✅ Core: '{core}'")
                for item_name in items:
                    print(f"   - {item_name}")
            
            # Check expected improvements
            print("\n" + "="*60)
            print("🎯 EXPECTED IMPROVEMENTS:")
            print("-" * 60)
            
            # Check: Stock and Broth should combine
            has_stock = any('stock' in m.get('core_ingredient', '').lower() 
                           for m in result.get('metadata', {}).values())
            has_broth = any('broth' in m.get('core_ingredient', '').lower() 
                           for m in result.get('metadata', {}).values())
            
            if not has_stock and has_broth:
                print("✅ Stock → broth (will combine!) ")
            else:
                print("❌ Stock and broth still separate")
            
            # Check: Manila Clams should be 'clams' not 'pound'
            manila_meta = result.get('metadata', {}).get('3', {})
            if manila_meta.get('core_ingredient') == 'clams':
                print("✅ Manila Clams → clams (not 'pound'!)")
            else:
                print(f"❌ Manila Clams → {manila_meta.get('core_ingredient')} (should be 'clams')")
            
            # Check: Garlic Cloves should be 'garlic' not 'clove'
            garlic_meta = result.get('metadata', {}).get('6', {})
            if garlic_meta.get('core_ingredient') == 'garlic':
                print("✅ Garlic Cloves → garlic (not 'clove'!)")
            else:
                print(f"❌ Garlic Cloves → {garlic_meta.get('core_ingredient')} (should be 'garlic')")
            
            # Check: Parsley items should all be 'parsley'
            parsley_cores = [result.get('metadata', {}).get(str(i), {}).get('core_ingredient') 
                            for i in [7, 10, 11, 12]]
            if all(c == 'parsley' for c in parsley_cores if c):
                print(f"✅ All parsley items → parsley ({len([c for c in parsley_cores if c == 'parsley'])} items will combine!)")
            else:
                print(f"⚠️ Parsley cores: {parsley_cores}")
            
        else:
            print(f"❌ API returned success=False")
            print(f"Error: {result.get('error')}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")

print("\n" + "="*60)
print("✅ Test complete!")
