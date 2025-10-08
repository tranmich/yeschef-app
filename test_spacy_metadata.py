"""
Test spaCy metadata extraction for JavaScript combiner
"""
import sys
sys.path.append('d:\\Mik\\Downloads\\Me Hungie')

from core_systems.spacy_ingredient_normalizer import get_normalizer
import json

print("🧪 Testing spaCy Metadata Extraction (Tier 1)\n")
print("="*60)

# Test: Fresh vs Canned tomatoes (should separate)
print("\n📝 Test 1: Quality Separation (Fresh vs Canned)")
print("-"*60)

test_items = [
    {'id': '1', 'name': '6 fresh tomatoes', 'checked': False},
    {'id': '2', 'name': '2 canned tomatoes', 'checked': False},
    {'id': '3', 'name': '6 large eggs', 'checked': False},
    {'id': '4', 'name': '6 eggs', 'checked': False},
]

print("\nInput items:")
for item in test_items:
    print(f"  - {item['name']}")

normalizer = get_normalizer()
metadata = normalizer.extract_metadata(test_items)

print("\n✨ spaCy Metadata:")
for item_id, meta in metadata.items():
    item = next(i for i in test_items if i['id'] == item_id)
    print(f"\n  '{item['name']}':")
    print(f"    Core: {meta['core_ingredient']}")
    print(f"    Qualities: {meta['qualities']}")
    print(f"    Sizes: {meta['sizes']}")
    print(f"    Should Separate: {meta['should_separate']}")
    if meta['similar_items']:
        print(f"    Similar to: {[s['name'] for s in meta['similar_items']]}")

# Expected results
print("\n✅ Expected Behavior:")
print("  - Fresh tomatoes: should_separate = True (fresh != canned)")
print("  - Canned tomatoes: should_separate = True (canned != fresh)")
print("  - Eggs: should_separate = False (both can combine)")
print("  - Large extracted as SIZE, not quality")

# Test 2: Novel ingredients
print("\n\n📝 Test 2: Novel Ingredient Detection")
print("-"*60)

novel_items = [
    {'id': '1', 'name': 'kohlrabi, sliced', 'checked': False},
    {'id': '2', 'name': '1 kohlrabi bulb', 'checked': False},
    {'id': '3', 'name': 'purple kohlrabi', 'checked': False},
]

print("\nInput items:")
for item in novel_items:
    print(f"  - {item['name']}")

metadata = normalizer.extract_metadata(novel_items)

print("\n✨ spaCy Metadata:")
for item_id, meta in metadata.items():
    item = next(i for i in novel_items if i['id'] == item_id)
    print(f"\n  '{item['name']}':")
    print(f"    Core: {meta['core_ingredient']}")
    print(f"    Preparations: {meta['preparations']}")
    if meta['similar_items']:
        print(f"    Similar to ({len(meta['similar_items'])}): {[s['name'] for s in meta['similar_items']]}")
        similarities = [f"{s['similarity']:.3f}" for s in meta['similar_items']]
        print(f"    Similarities: {similarities}")

print("\n✅ Expected: All 3 kohlrabi items should be similar to each other")

# Test 3: Size adjectives (should combine)
print("\n\n📝 Test 3: Size Adjectives (Can Combine)")
print("-"*60)

size_items = [
    {'id': '1', 'name': '6 large eggs', 'checked': False},
    {'id': '2', 'name': '6 small eggs', 'checked': False},
    {'id': '3', 'name': '12 eggs', 'checked': False},
]

print("\nInput items:")
for item in size_items:
    print(f"  - {item['name']}")

metadata = normalizer.extract_metadata(size_items)

print("\n✨ spaCy Metadata:")
for item_id, meta in metadata.items():
    item = next(i for i in size_items if i['id'] == item_id)
    print(f"\n  '{item['name']}':")
    print(f"    Core: {meta['core_ingredient']}")
    print(f"    Sizes: {meta['sizes']}")
    print(f"    Should Separate: {meta['should_separate']}")

print("\n✅ Expected: All eggs should combine (sizes don't trigger separation)")

print("\n\n" + "="*60)
print("✅ All tests complete!")
print("="*60)
