"""
Quick diagnostic - check what routes are available on Railway
"""

import requests

BASE_URL = "https://yeschefapp-production.up.railway.app"

print("🔍 Checking Railway deployment...")
print(f"Base URL: {BASE_URL}\n")

# Test health endpoint
print("1. Testing /api/v2/health...")
response = requests.get(f"{BASE_URL}/api/v2/health")
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    print(f"   Response: {response.json()}")
print()

# Test if friends endpoint exists
print("2. Testing /api/v2/friends/user/1...")
response = requests.get(f"{BASE_URL}/api/v2/friends/user/1")
print(f"   Status: {response.status_code}")
if response.status_code != 404:
    print(f"   Response: {response.text[:200]}")
else:
    print(f"   ❌ Route not found - needs deployment")
print()

# Check if old v1 friends endpoint exists
print("3. Testing old /api/friends/list (v1)...")
response = requests.get(f"{BASE_URL}/api/friends/list")
print(f"   Status: {response.status_code}")
print()

print("=" * 60)
print("CONCLUSION:")
if response.status_code == 404:
    print("❌ New v2 routes are NOT deployed yet")
    print("   Railway needs to redeploy with new code")
else:
    print("✅ Routes are available!")
