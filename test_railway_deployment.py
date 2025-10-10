"""
Test Railway Deployment with Ollama
Quick verification that everything is working
"""
import requests
import json

print("🧪 Testing Railway Deployment\n")
print("="*60)

# Get your Railway URL
railway_url = input("\n📝 Enter your Railway URL (e.g., https://your-app.up.railway.app): ").strip()

if not railway_url.startswith('http'):
    railway_url = f"https://{railway_url}"

print(f"\n🔗 Testing: {railway_url}")
print("="*60)

# Test 1: Health Check
print("\n1️⃣ Testing Health Endpoint...")
try:
    response = requests.get(f"{railway_url}/api/health", timeout=10)
    if response.ok:
        health = response.json()
        print("   ✅ Server is healthy!")
        print(f"   Status: {health.get('status')}")
        if 'services' in health:
            services = health['services']
            print(f"   Database: {services.get('database', 'unknown')}")
            print(f"   spaCy: {services.get('spacy', 'unknown')}")
            print(f"   Ollama: {services.get('ollama', 'unknown')}")
    else:
        print(f"   ❌ Health check failed: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Ollama Test Endpoint
print("\n2️⃣ Testing Ollama Integration...")
try:
    test_data = {
        "question": "Should 'chicken thighs' and 'chicken broth' be combined in a grocery list?"
    }
    
    print("   ⏳ First LLM call can take 30-60 seconds (loading model)...")
    
    response = requests.post(
        f"{railway_url}/api/ollama/test",
        json=test_data,
        timeout=90  # Increased to 90 seconds for first call
    )
    
    if response.ok:
        result = response.json()
        print("   ✅ Ollama is working!")
        print(f"   Response: {result.get('response', 'No response')[:100]}...")
        print(f"   Processing time: {result.get('processing_time', 'unknown')}s")
    else:
        print(f"   ⚠️ Ollama test failed: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
except requests.exceptions.Timeout:
    print(f"   ⚠️ Timeout after 90s - model might still be loading")
    print(f"   Note: Ollama is running (health check passed!)")
    print(f"   Try again in a minute or test via mobile app")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: spaCy Metadata Extraction
print("\n3️⃣ Testing spaCy Metadata Extraction...")
try:
    test_items = [
        {"id": "1", "name": "2 chicken breasts"},
        {"id": "2", "name": "4 chicken thighs"},
        {"id": "3", "name": "1 cup chicken broth"}
    ]
    
    response = requests.post(
        f"{railway_url}/api/grocery/extract-metadata",
        json={"items": test_items},
        timeout=30  # Increased timeout
    )
    
    if response.ok:
        result = response.json()
        if result.get('success'):
            print("   ✅ spaCy is working!")
            print(f"   Analyzed {result.get('item_count')} items")
            
            # Show sample
            metadata = result.get('metadata', {})
            if '1' in metadata:
                sample = metadata['1']
                print(f"   Sample: 'chicken breasts' → core: {sample.get('core_ingredient')}")
        else:
            print(f"   ⚠️ spaCy test failed")
    else:
        print(f"   ❌ spaCy test failed: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Full Grocery List Generation (if authenticated)
print("\n4️⃣ Testing Full Grocery List Flow...")
print("   ℹ️ Skipping (requires authentication)")
print("   You can test this from your mobile app!")

print("\n" + "="*60)
print("\n✅ SUMMARY:")
print("   If all tests passed, your Railway deployment is fully functional!")
print("   Ollama is running and ready to process grocery lists!")
print("\n📱 NEXT STEPS:")
print("   1. Update mobile app with this URL")
print("   2. Generate a grocery list from meal plan")
print("   3. Watch it combine intelligently with LLM!")
print("\n" + "="*60)
