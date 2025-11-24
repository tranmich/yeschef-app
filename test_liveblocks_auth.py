"""
Quick test script for Liveblocks auth endpoint
"""
import requests
import json

# Base URL
BASE_URL = "http://127.0.0.1:5000"

# Test user credentials (use your existing test user)
TEST_EMAIL = "test@example.com"  # Change this to a real user in your DB
TEST_PASSWORD = "test123"  # Change this

print("🧪 Testing Liveblocks Auth Endpoint")
print("=" * 50)

# Step 1: Login to get YesChef JWT token
print("\n1️⃣ Logging in to YesChef...")
login_response = requests.post(f"{BASE_URL}/api/v2/auth/login", json={
    "email": TEST_EMAIL,
    "password": TEST_PASSWORD
})

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    print(f"Response: {login_response.text}")
    print("\n💡 You need to create a test user first or update TEST_EMAIL/TEST_PASSWORD")
    exit(1)

login_data = login_response.json()
yeschef_token = login_data.get('access_token') or login_data.get('token')

if not yeschef_token:
    print(f"❌ No token in response: {login_data}")
    exit(1)

print(f"✅ Logged in successfully")
print(f"Token (first 50 chars): {yeschef_token[:50]}...")

# Step 2: Request Liveblocks auth token
print("\n2️⃣ Requesting Liveblocks auth token...")
liveblocks_response = requests.post(
    f"{BASE_URL}/api/v2/liveblocks/auth",
    headers={
        "Authorization": f"Bearer {yeschef_token}",
        "Content-Type": "application/json"
    },
    json={
        "room": "whiteboard-123"  # Test room ID
    }
)

print(f"Status Code: {liveblocks_response.status_code}")

if liveblocks_response.status_code == 200:
    liveblocks_data = liveblocks_response.json()
    liveblocks_token = liveblocks_data.get('token')
    
    if liveblocks_token:
        print(f"✅ Liveblocks token received!")
        print(f"Token (first 50 chars): {liveblocks_token[:50]}...")
        
        # Decode token to see payload (optional)
        import jwt
        try:
            # Don't verify signature for inspection (we just want to see payload)
            payload = jwt.decode(liveblocks_token, options={"verify_signature": False})
            print(f"\n📦 Token Payload:")
            print(json.dumps(payload, indent=2, default=str))
        except Exception as e:
            print(f"⚠️ Could not decode token: {e}")
        
        print("\n✅ TEST PASSED! Liveblocks auth endpoint is working!")
    else:
        print(f"❌ No token in response: {liveblocks_data}")
else:
    print(f"❌ Request failed: {liveblocks_response.status_code}")
    print(f"Response: {liveblocks_response.text}")

print("\n" + "=" * 50)
