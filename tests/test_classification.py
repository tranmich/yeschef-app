#!/usr/bin/env python3

import requests
import json

def test_classification(user_input, expected_type):
    """Test AI classification for a specific user input"""
    
    classification_prompt = f"""CLASSIFICATION TASK: Analyze the user request and respond with ONLY one word.

User request: "{user_input}"

RESPOND WITH ONLY ONE OF THESE WORDS:
- recipe_search (if user wants to find recipes/dishes to cook)
- ingredient_advice (if user wants substitutions/alternatives for ingredients)  
- cooking_advice (if user wants cooking tips/techniques/general guidance)

Examples:
"I want to make chicken" → recipe_search
"I don't eat butter, what can I use instead?" → ingredient_advice
"How can I make this more exciting?" → cooking_advice
"What's a good recipe for dinner?" → recipe_search
"I'm allergic to nuts, what can I substitute?" → ingredient_advice
"Any tips for better flavor?" → cooking_advice
"How do I make food taste better?" → cooking_advice

RESPOND WITH ONLY THE CATEGORY NAME. NO OTHER TEXT."""

    url = "http://localhost:8000/api/smart-search"
    payload = {
        "message": classification_prompt,
        "skipRecipeSearch": True
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"\n🧪 Testing: '{user_input}'")
        print(f"Expected: {expected_type}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            ai_response = data.get('chat_response', '').lower().strip()
            print(f"AI Response: '{ai_response}'")
            
            if expected_type in ai_response:
                print("✅ PASS")
            else:
                print("❌ FAIL")
                print(f"Full response: {data}")
        else:
            print(f"❌ HTTP Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    print("🤖 Testing AI Classification System")
    
    test_classification("can you suggest an alternative to vegetable oil", "ingredient_advice")
    test_classification("how do I make food taste better?", "cooking_advice") 
    test_classification("I want to make chicken", "recipe_search")
