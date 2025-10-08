"""
🧪 Test YouTube Import via Flask API
=====================================

Tests the complete integration:
Mobile App → Flask API → YouTube Extractor → AI Parser → Database

Author: GitHub Copilot
Date: October 2, 2025
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_youtube_import_api():
    """
    Test YouTube recipe import through Flask API endpoint
    """
    print("="*80)
    print("🧪 TESTING YOUTUBE IMPORT VIA FLASK API")
    print("="*80)
    
    # Configuration
    API_BASE_URL = "http://localhost:5000"  # Change to Railway URL for production
    TEST_VIDEO_URL = "https://www.youtube.com/watch?v=CfchYxh7Q9g"
    
    # You'll need a valid token - get this from your app or create a test user
    # For now, we'll show the structure
    print(f"\n📍 API Endpoint: {API_BASE_URL}/api/recipes/import/url")
    print(f"🎥 Test Video: {TEST_VIDEO_URL}")
    
    print(f"\n⚠️  NOTE: You need to be logged in to test this.")
    print("   Options:")
    print("   1. Run Flask server: python hungie_server.py")
    print("   2. Login via mobile app or web")
    print("   3. Get your auth token from SecureStore/localStorage")
    print("   4. Add token to this script")
    
    # Check if server is running
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print(f"\n✅ Flask server is running!")
            print(f"   Response: {response.json()}")
        else:
            print(f"\n⚠️  Flask server responded but may have issues")
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Flask server is not running at {API_BASE_URL}")
        print("   Please start it with: python hungie_server.py")
        return
    except Exception as e:
        print(f"\n❌ Error checking server: {e}")
        return
    
    # Example request (will fail without auth token)
    print(f"\n📤 Example API Request:")
    print("-"*80)
    
    request_body = {
        "url": TEST_VIDEO_URL
    }
    
    print(f"POST {API_BASE_URL}/api/recipes/import/url")
    print(f"Headers:")
    print(f"  Authorization: Bearer <YOUR_TOKEN_HERE>")
    print(f"  Content-Type: application/json")
    print(f"\nBody:")
    print(json.dumps(request_body, indent=2))
    
    print("-"*80)
    
    # Try to make request (will likely fail without auth)
    print(f"\n🔐 Attempting request (this will likely fail without auth token)...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/recipes/import/url",
            json=request_body,
            headers={
                "Content-Type": "application/json",
                # Add your token here: "Authorization": "Bearer YOUR_TOKEN"
            },
            timeout=60  # YouTube import can take 10-30 seconds
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        print(f"Response Body:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("\n🎉 SUCCESS! YouTube recipe imported!")
                print(f"   Recipe ID: {result.get('recipe_id')}")
                print(f"   Title: {result.get('recipe_data', {}).get('title')}")
                print(f"   Confidence: {result.get('confidence')}")
            else:
                print(f"\n❌ Import failed: {result.get('error')}")
        elif response.status_code == 401:
            print("\n🔐 Authentication required (expected)")
            print("   This is normal - you need to login first")
        else:
            print(f"\n⚠️  Unexpected response code")
            
    except requests.exceptions.Timeout:
        print("\n⏱️  Request timed out (YouTube import can take 10-30 seconds)")
    except Exception as e:
        print(f"\n❌ Request error: {e}")
    
    print("\n" + "="*80)
    print("📱 HOW TO TEST FROM MOBILE APP:")
    print("="*80)
    print("""
1. Open your YesChef mobile app
2. Go to Recipe Collection screen
3. Tap the import URL input field
4. Paste a YouTube cooking video URL:
   https://www.youtube.com/watch?v=CfchYxh7Q9g
5. Tap 'Import Recipe'
6. Wait 10-30 seconds for processing
7. Review the imported recipe!

The mobile app already has all the code needed - it just sends
the URL to /api/recipes/import/url and the backend will:
✅ Detect it's a YouTube URL
✅ Extract video content (metadata + transcript)
✅ Parse with AI (GPT-4)
✅ Save to database
✅ Return to RecipeImportReviewScreen
""")
    
    print("\n" + "="*80)
    print("🚀 TESTING WITH MOBILE APP IS THE EASIEST WAY!")
    print("="*80)


if __name__ == "__main__":
    test_youtube_import_api()
