"""
Test Voice Recording Backend
Quick test script for Phase 1 implementation

Run this to verify:
1. Language search works
2. Voice processor can transcribe (needs real audio)
3. Recipe generation works from text

Created: October 6, 2025
"""

import requests
import json

# Backend URL
BASE_URL = 'https://yeschefapp-production.up.railway.app'
# BASE_URL = 'http://localhost:5000'  # For local testing

def test_language_search():
    """Test language autocomplete"""
    print("\n🧪 Testing Language Search...")
    print("=" * 50)
    
    test_queries = [
        "filipino",
        "mexican",
        "italian",
        "korean",
        ""  # Should return popular languages
    ]
    
    for query in test_queries:
        response = requests.get(
            f'{BASE_URL}/api/recipes/voice/languages/search',
            params={'q': query}
        )
        
        data = response.json()
        
        print(f"\nQuery: '{query}'")
        if data.get('success'):
            print(f"✅ Found {data['count']} languages")
            for lang in data['languages'][:3]:
                print(f"   - {lang['displayName']} ({lang['whisperCode']})")
        else:
            print(f"❌ Error: {data.get('error')}")

def test_recipe_generation():
    """
    Test recipe generation from text (simulates approved transcript)
    This works without audio files
    """
    print("\n🧪 Testing Recipe Generation...")
    print("=" * 50)
    
    # You need a valid JWT token for this
    # Get it by logging in first
    token = input("\nEnter your JWT token (or press Enter to skip): ").strip()
    
    if not token:
        print("⏭️ Skipping recipe generation test (requires authentication)")
        return
    
    test_transcript = """
    This is my mom's pizza recipe. You need about three cups of flour, 
    one cup of warm water, a packet of yeast, and a teaspoon of salt. 
    
    First, you mix the flour, water, yeast and salt together. Then you 
    knead it for about five minutes until it's smooth. Let it rise for 
    an hour in a warm place until it doubles in size.
    
    After that, you roll it out into a circle, spread some tomato sauce 
    on it, add mozzarella cheese and whatever toppings you like. Then 
    bake it in a hot oven at about 425 degrees for 12 to 15 minutes 
    until the crust is golden and the cheese is bubbly.
    """
    
    payload = {
        'transcript': test_transcript,
        'metadata': {
            'recorded_by': 'Mom',
            'culture': 'Italian-American',
            'language': 'en',
            'duration': 60000,
            'session_id': 'test-123'
        }
    }
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("\n📤 Sending transcript to API...")
    response = requests.post(
        f'{BASE_URL}/api/recipes/voice/generate',
        headers=headers,
        json=payload
    )
    
    data = response.json()
    
    if data.get('success'):
        recipe = data['recipe_data']
        print("\n✅ Recipe Generated Successfully!")
        print(f"\nTitle: {recipe.get('title')}")
        print(f"Servings: {recipe.get('servings')}")
        print(f"Category: {recipe.get('category')}")
        print(f"\nIngredients ({len(recipe.get('ingredients', []))}):")
        for ing in recipe.get('ingredients', [])[:5]:
            print(f"  - {ing}")
        print(f"\nInstructions ({len(recipe.get('instructions', []))}):")
        for idx, step in enumerate(recipe.get('instructions', [])[:3], 1):
            print(f"  {idx}. {step}")
        print(f"\nExtraction Method: {data.get('extraction_method')}")
        print(f"Confidence: {data.get('confidence')}")
    else:
        print(f"\n❌ Error: {data.get('error')}")
        if response.status_code == 401:
            print("   (Authentication failed - check your token)")

def test_health_check():
    """Test basic connectivity"""
    print("\n🧪 Testing Backend Health...")
    print("=" * 50)
    
    try:
        response = requests.get(f'{BASE_URL}/api/health', timeout=10)
        data = response.json()
        
        print(f"\n✅ Backend is UP")
        print(f"Status: {data.get('status')}")
        
        if 'capabilities' in data:
            caps = data['capabilities']
            print(f"\nCapabilities:")
            print(f"  - Voice Recording: {caps.get('voice_recording', 'Not Available')}")
            print(f"  - Recipe Import: {caps.get('recipe_import', False)}")
            print(f"  - Universal Search: {caps.get('universal_search', False)}")
    except Exception as e:
        print(f"\n❌ Cannot reach backend: {e}")

if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("🎤 VOICE RECORDING BACKEND TEST")
    print("=" * 50)
    
    # Run tests
    test_health_check()
    test_language_search()
    test_recipe_generation()
    
    print("\n" + "=" * 50)
    print("✅ Testing Complete!")
    print("=" * 50)
    print("\n💡 Next Steps:")
    print("  1. Test with real audio files (requires Postman/curl)")
    print("  2. Verify database columns were added")
    print("  3. Start mobile UI implementation")
    print("\n")
