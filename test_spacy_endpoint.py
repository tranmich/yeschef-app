"""
Quick test to verify spaCy endpoint is working
"""
import requests
import json

print("🧪 Testing spaCy Endpoint\n")
print("="*60)

# Test data
test_items = [
    {'id': '1', 'name': '2 chicken breasts'},
    {'id': '2', 'name': '4 chicken thighs'},
    {'id': '3', 'name': '1 cup chicken broth'},
    {'id': '4', 'name': '6 large eggs'},
    {'id': '5', 'name': '6 eggs'},
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
            
            print("\n📤 Metadata Results:")
            for item_id, meta in result.get('metadata', {}).items():
                item = next(i for i in test_items if i['id'] == item_id)
                print(f"\n  '{item['name']}':")
                print(f"    Core: {meta.get('core_ingredient')}")
                print(f"    Qualities: {meta.get('qualities', [])}")
                print(f"    Sizes: {meta.get('sizes', [])}")
                print(f"    Should Separate: {meta.get('should_separate', False)}")
        else:
            print(f"❌ API returned success=False")
            print(f"Error: {result.get('error')}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ CONNECTION ERROR!")
    print("   Backend server is not running or not accessible")
    print("\n💡 Make sure to:")
    print("   1. Start the backend: python hungie_server.py")
    print("   2. Check it's running on: http://192.168.1.72:5000")
    print("   3. Verify firewall allows connections")
    
except requests.exceptions.Timeout:
    print("\n❌ TIMEOUT!")
    print("   Server took too long to respond (> 5 seconds)")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")

print("\n" + "="*60)
print("✅ Test complete!")
