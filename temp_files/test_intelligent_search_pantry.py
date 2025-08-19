#!/usr/bin/env python3
"""
Quick Test: Pantry Integration in RecipeDetail Search
Tests that the intelligent search endpoint properly receives pantry data
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_intelligent_search_with_pantry():
    """Test the intelligent search endpoint with pantry data"""
    print("🧪 Testing Intelligent Search with Pantry Integration")
    print("=" * 60)

    # Test payload with pantry data (similar to what frontend sends)
    test_payload = {
        "query": "easy dinner recipes",
        "session_id": "test_session_123",
        "shown_recipe_ids": [],
        "page_size": 5,
        "user_pantry": [
            {"name": "ribeye steak", "category": "protein", "amount": "some"},
            {"name": "eggs", "category": "protein", "amount": "plenty"},
            {"name": "tofu", "category": "protein", "amount": "some"},
            {"name": "ketchup", "category": "condiment", "amount": "some"},
            {"name": "basil", "category": "herb", "amount": "some"}
        ],
        "pantry_first": True
    }

    print("📤 Sending request to /api/search/intelligent with pantry data:")
    print(f"   Pantry items: {[item['name'] for item in test_payload['user_pantry']]}")
    print(f"   Pantry first: {test_payload['pantry_first']}")
    print(f"   Query: '{test_payload['query']}'")

    try:
        url = f"{BASE_URL}/api/search/intelligent"
        response = requests.post(url, json=test_payload, timeout=30)

        if response.status_code == 200:
            data = response.json()
            recipes = data.get('recipes', [])

            print(f"\n✅ SUCCESS! Received {len(recipes)} recipes")

            if recipes:
                print("\n📋 Recipe Results:")
                for i, recipe in enumerate(recipes[:3], 1):
                    title = recipe.get('title', 'Unknown Recipe')
                    recipe_id = recipe.get('id', 'Unknown ID')
                    print(f"   {i}. {title} (ID: {recipe_id})")

                # Check for pantry-related metadata
                metadata = data.get('search_metadata', {})
                if metadata:
                    print(f"\n📊 Search Metadata:")
                    for key, value in metadata.items():
                        print(f"   {key}: {value}")
            else:
                print("⚠️ No recipes returned")

        else:
            print(f"\n❌ API Error: {response.status_code}")
            print(f"Response: {response.text[:500]}")

    except requests.exceptions.ConnectionError:
        print("\n❌ Connection failed - is the server running on port 5000?")
    except Exception as e:
        print(f"\n❌ Error: {e}")

    print("\n" + "=" * 60)
    print("🎯 Expected Server Logs:")
    print("Look for these messages in your server terminal:")
    print("🥫 Intelligent search - Pantry data received: ['ribeye steak', 'eggs', 'tofu', 'ketchup', 'basil'] (pantry_first: True)")

if __name__ == "__main__":
    test_intelligent_search_with_pantry()
