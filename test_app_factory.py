"""
Test script for app factory
Run from project root: python test_app_factory.py
"""

from app import create_app

print("Testing app factory...")

# Create development app
dev_app = create_app('development')
print(f"\n✅ Development app created")
print(f"   Debug: {dev_app.config['DEBUG']}")
print(f"   Routes: {len(dev_app.url_map._rules)} registered")

# Test health endpoint
with dev_app.test_client() as client:
    response = client.get('/api/v2/health')
    print(f"\n✅ Health check endpoint works!")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.get_json()}")

print("\n✅ App factory tests passed!")
