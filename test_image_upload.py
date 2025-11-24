#!/usr/bin/env python3
"""
Test script to verify whiteboard image upload endpoint
"""

import requests
import os

# Get JWT token (you'll need to login first)
API_URL = "http://127.0.0.1:5000"

print("Testing Whiteboard Image Upload Endpoint")
print("=" * 50)

# Test 1: Check if endpoint exists
print("\n1. Testing endpoint accessibility...")
try:
    response = requests.get(f"{API_URL}/api/v2/whiteboards/images/upload")
    print(f"   Status: {response.status_code}")
    if response.status_code == 405:
        print("   ✅ Endpoint exists (Method Not Allowed for GET is expected)")
    elif response.status_code == 404:
        print("   ❌ Endpoint not found - server may need restart")
    else:
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n2. Instructions to fix:")
print("   - Make sure the Python server is running")
print("   - Restart the Python server if you made changes:")
print("     Terminal: python")
print("     Command: python hungie_server.py")
print("\n3. To test with actual upload:")
print("   - Login to get JWT token")
print("   - Use Postman or curl with Authorization header")
print("   - POST to /api/v2/whiteboards/images/upload")
print("   - Include 'image' file in multipart/form-data")

print("\n" + "=" * 50)
