"""
Quick test of Ollama integration for grocery combining
Run after installing Ollama and downloading llama3.2:3b
"""
from core_systems.ollama_assistant import get_ollama_assistant
import json

print("🧪 Testing Ollama Grocery Assistant\n")
print("="*60)

# Get assistant
assistant = get_ollama_assistant()

if not assistant.available:
    print("\n❌ Ollama is not available!")
    print("\n📝 To fix:")
    print("   1. Install Ollama: https://ollama.com/download")
    print("   2. Download model: ollama pull llama3.2:3b")
    print("   3. Verify: ollama run llama3.2:3b 'Hello'")
    print("   4. Run this test again!")
    exit(1)

print(f"\n✅ Ollama is available with model: {assistant.model}")
print("="*60)

# Test 1: Should chicken thighs and chicken broth combine?
print("\n🧪 TEST 1: Chicken Thighs vs Chicken Broth")
print("-"*60)
result = assistant.should_combine(
    {'name': '2 Chicken Thighs', 'core': 'thigh'},
    {'name': '1 cup Chicken Broth', 'core': 'broth'}
)
print(f"\nResult: {json.dumps(result, indent=2)}")
print(f"\nExpected: should_combine = False (different items!)")

# Test 2: Should chicken stock and chicken broth combine?
print("\n\n🧪 TEST 2: Chicken Stock vs Chicken Broth")
print("-"*60)
result = assistant.should_combine(
    {'name': '9 cups Chicken Stock', 'core': 'stock'},
    {'name': '0.5 cup Chicken Broth', 'core': 'broth'}
)
print(f"\nResult: {json.dumps(result, indent=2)}")
print(f"\nExpected: should_combine = True (same thing!)")

# Test 3: Should black pepper and red pepper flakes combine?
print("\n\n🧪 TEST 3: Black Pepper vs Red Pepper Flakes")
print("-"*60)
result = assistant.should_combine(
    {'name': 'Black Pepper', 'core': 'pepper'},
    {'name': '1 tsp Red Pepper Flakes', 'core': 'pepper'}
)
print(f"\nResult: {json.dumps(result, indent=2)}")
print(f"\nExpected: should_combine = False (different types!)")

# Test 4: Group analysis of chicken items
print("\n\n🧪 TEST 4: Group Multiple Chicken Items")
print("-"*60)
items = [
    {'id': '1', 'name': '2 Bone-In Chicken Thighs', 'core': 'thigh'},
    {'id': '2', 'name': '2 Chicken Breasts', 'core': 'breast'},
    {'id': '3', 'name': '9 cups Chicken Stock', 'core': 'stock'},
    {'id': '4', 'name': '0.5 cup Chicken Broth', 'core': 'broth'}
]
print("\nItems to group:")
for item in items:
    print(f"  - {item['name']}")

result = assistant.analyze_ambiguous_group(items)
print(f"\nResult: {json.dumps(result, indent=2)}")
print(f"\nExpected: 3 groups:")
print(f"  1. Thighs (separate)")
print(f"  2. Breasts (separate)")
print(f"  3. Stock + Broth (combined)")

# Test 5: Parsley variations
print("\n\n🧪 TEST 5: Group Parsley Items")
print("-"*60)
items = [
    {'id': '1', 'name': '1 tablespoon Finely Chopped Parsley', 'core': 'parsley'},
    {'id': '2', 'name': '1 tablespoon Chopped Parsley', 'core': 'parsley'},
    {'id': '3', 'name': '2 Parsley Sprigs', 'core': 'parsley'},
    {'id': '4', 'name': '0.25 cup Finely Chopped Parsley Leaves', 'core': 'parsley'}
]
print("\nItems to group:")
for item in items:
    print(f"  - {item['name']}")

result = assistant.analyze_ambiguous_group(items)
print(f"\nResult: {json.dumps(result, indent=2)}")
print(f"\nExpected: All combined (same ingredient, different prep)")

print("\n" + "="*60)
print("✅ Tests complete!")
print("\nIf all tests show good reasoning, Ollama is working perfectly! 🎉")
