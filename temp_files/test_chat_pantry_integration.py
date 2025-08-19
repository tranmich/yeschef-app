#!/usr/bin/env python3
"""
Pantry-Chat Integration Test Script
Tests that the chat API properly receives and uses pantry data
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_chat_pantry_integration():
    """Test chat API with pantry data"""
    print("🧪 Testing Chat-Pantry Integration")
    print("=" * 50)
    
    # Test case 1: Chat without pantry
    print("\n1️⃣ Testing chat WITHOUT pantry data:")
    test_chat_request({
        "message": "What can I cook for dinner?",
        "context": "",
        "user_pantry": [],
        "pantry_first": False
    })
    
    # Test case 2: Chat with pantry data
    print("\n2️⃣ Testing chat WITH pantry data:")
    test_chat_request({
        "message": "What can I cook for dinner?", 
        "context": "",
        "user_pantry": [
            {"name": "Chicken Breast", "category": "protein", "amount": "some"},
            {"name": "Rice", "category": "grain", "amount": "plenty"},
            {"name": "Onion", "category": "produce", "amount": "some"},
            {"name": "Garlic", "category": "produce", "amount": "some"}
        ],
        "pantry_first": True
    })
    
    # Test case 3: Specific pantry ingredient request
    print("\n3️⃣ Testing specific ingredient request:")
    test_chat_request({
        "message": "I have chicken and rice, what can I make?",
        "context": "",
        "user_pantry": [
            {"name": "Chicken Breast", "category": "protein", "amount": "some"},
            {"name": "Rice", "category": "grain", "amount": "plenty"}
        ],
        "pantry_first": True
    })

def test_chat_request(request_data):
    """Send a test request to the chat API"""
    try:
        url = f"{BASE_URL}/api/smart-search"
        response = requests.post(url, json=request_data, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            recipes = data.get('recipes', [])
            chat_response = data.get('chat_response', '')
            
            print(f"✅ Success! Found {len(recipes)} recipes")
            print(f"💬 Chat response: {chat_response[:100]}...")
            
            if recipes:
                print("📋 Sample recipes:")
                for i, recipe in enumerate(recipes[:3]):
                    print(f"   {i+1}. {recipe.get('title', 'Unknown')}")
                    
            # Check if pantry was considered
            pantry_items = request_data.get('user_pantry', [])
            if pantry_items:
                print(f"🥫 Pantry sent: {[item['name'] for item in pantry_items]}")
                print(f"🎯 Pantry priority: {request_data.get('pantry_first', False)}")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - is the server running on port 5000?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_chat_pantry_integration()
    print("\n" + "=" * 50)
    print("🎯 Integration Test Complete!")
    print("Expected behavior:")
    print("- Chat requests include pantry data")
    print("- Backend logs show pantry information")
    print("- Recipe suggestions prioritize pantry ingredients")
