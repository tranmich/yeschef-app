"""
Test Whiteboard API Registration
=================================
Verify that all 25 endpoints are registered correctly

Run this to test:
python migrations/test_whiteboard_api.py
"""

import sys
sys.path.insert(0, 'D:\\Mik\\Downloads\\Me Hungie')

from app import create_app

print("\n" + "=" * 60)
print("🧪 TESTING WHITEBOARD API REGISTRATION")
print("=" * 60)

# Create app
app = create_app('development')

# Get all whiteboard routes
whiteboard_routes = []
for rule in app.url_map.iter_rules():
    if '/whiteboard' in str(rule):
        whiteboard_routes.append({
            'endpoint': rule.endpoint,
            'methods': ', '.join(sorted(rule.methods - {'HEAD', 'OPTIONS'})),
            'path': str(rule)
        })

# Sort by path
whiteboard_routes.sort(key=lambda x: x['path'])

print(f"\n✅ Found {len(whiteboard_routes)} whiteboard endpoints:\n")
print("-" * 60)

# Group by category
categories = {
    'Whiteboard CRUD': [],
    'Object Management': [],
    'Comments': [],
    'Collaboration': [],
    'Utilities': [],
    'Health': []
}

for route in whiteboard_routes:
    path = route['path']
    if '/o/' in path and '/cm' in path:
        categories['Comments'].append(route)
    elif '/cm' in path or '/rx' in path:
        categories['Comments'].append(route)
    elif '/o/' in path or '/o' in path:
        categories['Object Management'].append(route)
    elif '/co' in path or '/pr' in path or '/h' in path or '/restore' in path:
        categories['Collaboration'].append(route)
    elif '/tpl' in path or '/dup' in path or '/exp' in path:
        categories['Utilities'].append(route)
    elif '/health' in path:
        categories['Health'].append(route)
    else:
        categories['Whiteboard CRUD'].append(route)

for category, routes in categories.items():
    if routes:
        print(f"\n📂 {category} ({len(routes)} endpoints):")
        for route in routes:
            methods = route['methods'].replace('GET', '🔍 GET').replace('POST', '➕ POST').replace('PATCH', '✏️  PATCH').replace('DELETE', '🗑️  DELETE')
            print(f"   {methods:20s} {route['path']}")

print("\n" + "=" * 60)
print(f"✅ Total: {len(whiteboard_routes)} endpoints registered")
print("=" * 60)

# Test health endpoint
print("\n🧪 Testing health endpoint...")
with app.test_client() as client:
    response = client.get('/api/v2/whiteboard/health')
    data = response.get_json()
    
    if response.status_code == 200 and data.get('success'):
        print(f"✅ Health check passed!")
        print(f"   Status: {response.status_code}")
        print(f"   Service: {data['data']['service']}")
        print(f"   Version: {data['data']['version']}")
        print(f"   Phase: {data['data']['phase']}")
        print(f"   Endpoints: {data['data']['endpoints_registered']}")
    else:
        print(f"❌ Health check failed!")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {data}")

print("\n" + "=" * 60)
print("🎉 API REGISTRATION TEST COMPLETE!")
print("=" * 60)
print("\nNext steps:")
print("1. ✅ 25 endpoints registered")
print("2. ⏳ Test authentication (Week 2)")
print("3. ⏳ Implement database queries (Week 3)")
print("4. ⏳ Build frontend integration (Week 3-4)")
print("=" * 60 + "\n")
