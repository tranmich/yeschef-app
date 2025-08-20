#!/usr/bin/env python3
"""
Debug script to analyze the "Why This Recipe Works" text pollution issue
"""

print("🔍 ANALYZING 'WHY THIS RECIPE WORKS' TEXT POLLUTION")
print("=" * 70)

# The problematic extractions
problematic_extractions = [
    "Our ideal bak ed ziti has al dente pasta, a",
    "Italian fontina cheese works best in this dish. If it is not"
]

print("\n❌ PROBLEMATIC EXTRACTIONS:")
for i, extraction in enumerate(problematic_extractions, 1):
    print(f"   {i}. '{extraction}'")

print("\n🔍 ANALYSIS:")
print("These are NOT recipe titles - they are:")
print("   • Editorial explanations ('Why This Recipe Works' sections)")
print("   • Ingredient substitution notes")
print("   • Cooking tips and techniques")

print("\n🎯 ROOT CAUSE:")
print("The visual structure detector is identifying these as titles because:")
print("   1. ✅ They have sentence-like structure")
print("   2. ✅ They contain food keywords (pasta, cheese, etc.)")
print("   3. ✅ They appear in prominent positions")
print("   4. ❌ BUT they are explanatory text, not recipe names")

print("\n🛠️ SOLUTION STRATEGIES:")
print("1. **Pattern Recognition**: Detect 'Why This Recipe Works' sections")
print("2. **Length Filtering**: Real recipe titles are typically 15-60 characters")
print("3. **Sentence Structure**: Recipe titles don't usually contain full sentences")
print("4. **Context Clues**: Look for explanatory keywords")
print("5. **Title Format**: Real titles are more concise and descriptive")

# Analyze the text patterns
print("\n📊 TEXT PATTERN ANALYSIS:")

explanatory_indicators = [
    "why this recipe works",
    "this recipe", "this dish", "this method",
    "we found", "we discovered", "we tested", "we tried",
    "traditional", "classic", "ideal", "perfect",
    "the key", "the secret", "the trick",
    "if it is not available", "if your", "substitute",
    "works best", "easily stood up", "allowed it to",
    "provided", "replaced", "helped"
]

print("   🚫 Explanatory text indicators:")
for indicator in explanatory_indicators[:8]:
    print(f"     - '{indicator}'")
print("     ... and more")

# Real recipe title examples
real_titles = [
    "Baked Ziti with Spinach",
    "Classic Spinach Lasagna", 
    "Fontina and Spinach Lasagna",
    "No-Boil Spinach Lasagna"
]

print("\n   ✅ Real recipe title examples:")
for title in real_titles:
    print(f"     - '{title}' ({len(title)} chars)")

print("\n💡 ENHANCED FILTERING NEEDED:")
print("   1. Reject text containing explanatory phrases")
print("   2. Prefer shorter, more title-like text")
print("   3. Look for noun-based titles vs sentence fragments")
print("   4. Check for cooking method + ingredient patterns")

print("\n🎯 IMPLEMENTATION:")
print("   Add exclusion patterns to the visual structure detector")
print("   to filter out 'Why This Recipe Works' type content!")
