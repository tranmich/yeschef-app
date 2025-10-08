"""
Quick test of spaCy ingredient normalizer
"""
import sys
sys.path.append('d:\\Mik\\Downloads\\Me Hungie')

from core_systems.spacy_ingredient_normalizer import get_normalizer

print("🧪 Testing spaCy Ingredient Normalizer\n")
print("="*60)

# Test 1: Basic enhancement
print("\n📝 Test 1: Basic Enhancement")
print("-"*60)

test_items = [
    {'id': '1', 'name': '2 cloves garlic', 'checked': False},
    {'id': '2', 'name': '1 head garlic', 'checked': False},
    {'id': '3', 'name': 'minced garlic', 'checked': False},
    {'id': '4', 'name': 'yellow onion', 'checked': False},
    {'id': '5', 'name': 'red onion, diced', 'checked': False},
]

print("\nInput items:")
for item in test_items:
    print(f"  - {item['name']}")

normalizer = get_normalizer()
result = normalizer.enhance_combining(test_items)

print(f"\nOutput: {len(result['enhanced_items'])} items")
for item in result['enhanced_items']:
    print(f"  - {item['name']}")

print(f"\n✨ Improvements: {result['improvements']}")

# Test 2: Novel ingredients
print("\n\n📝 Test 2: Novel Ingredients")
print("-"*60)

novel_items = [
    {'id': '1', 'name': 'kohlrabi, sliced', 'checked': False},
    {'id': '2', 'name': '1 kohlrabi bulb', 'checked': False},
    {'id': '3', 'name': 'purple kohlrabi', 'checked': False},
]

print("\nInput items:")
for item in novel_items:
    print(f"  - {item['name']}")

result = normalizer.enhance_combining(novel_items)

print(f"\nOutput: {len(result['enhanced_items'])} items")
for item in result['enhanced_items']:
    print(f"  - {item['name']}")

print(f"\n✨ Improvements: {result['improvements']}")

# Test 3: Similarity scoring
print("\n\n📝 Test 3: Semantic Similarity")
print("-"*60)

import spacy
nlp = spacy.load("en_core_web_md")

pairs = [
    ("fresh mozzarella", "mozzarella cheese"),
    ("cheddar", "mozzarella"),
    ("butter", "margarine"),
    ("garlic cloves", "minced garlic"),
]

for item1, item2 in pairs:
    doc1 = nlp(item1)
    doc2 = nlp(item2)
    similarity = doc1.similarity(doc2)
    print(f"  '{item1}' vs '{item2}': {similarity:.3f}")

print("\n✅ All tests complete!")
print("="*60)
