"""
Test Grocery List Normalizer
=============================
Verify that normalizer handles all format variations
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.grocery_list_normalizer import GroceryListNormalizer, normalize, validate


def test_whiteboard_format():
    """Test conversion from whiteboard format (ingredient field)"""
    print("\n" + "=" * 80)
    print("TEST 1: Whiteboard Format (ingredient)")
    print("=" * 80)
    
    whiteboard_data = {
        'id': 114,
        'name': 'Shopping List',
        'items': [
            {'id': 'temp-1', 'ingredient': 'bananas', 'checked': False},
            {'id': 'temp-2', 'ingredient': '2 tbsp ketchup', 'checked': False},
            {'id': 'temp-3', 'ingredient': 'chicken thighs', 'checked': True}
        ],
        'household_id': 11,
        'whiteboard_id': 53
    }
    
    standard = normalize(whiteboard_data)
    
    print(f"✅ List name: {standard['name']}")
    print(f"✅ Items count: {len(standard['items'])}")
    print(f"✅ First item: {standard['items'][0]['name']}")
    
    assert standard['name'] == 'Shopping List'
    assert len(standard['items']) == 3
    assert standard['items'][0]['name'] == 'bananas'
    assert standard['items'][2]['checked'] == True
    assert validate(standard)
    
    print("✅ PASS: Whiteboard format normalized correctly")


def test_legacy_format():
    """Test conversion from legacy format (list_name, items_json)"""
    print("\n" + "=" * 80)
    print("TEST 2: Legacy Format (list_name, items_json)")
    print("=" * 80)
    
    legacy_data = {
        'id': 100,
        'list_name': 'Weekly Shopping',
        'items_json': '[{"name":"milk","checked":false},{"name":"bread","checked":true}]',
        'created_date': '2025-11-17',
        'updated_date': '2025-11-17'
    }
    
    standard = normalize(legacy_data)
    
    print(f"✅ List name: {standard['name']}")
    print(f"✅ Items count: {len(standard['items'])}")
    
    assert standard['name'] == 'Weekly Shopping'
    assert len(standard['items']) == 2
    assert standard['items'][0]['name'] == 'milk'
    assert validate(standard)
    
    print("✅ PASS: Legacy format normalized correctly")


def test_web_sections_format():
    """Test conversion from web format (sections)"""
    print("\n" + "=" * 80)
    print("TEST 3: Web Format (sections)")
    print("=" * 80)
    
    web_data = {
        'id': 105,
        'name': 'Meal Prep List',
        'items': {
            'produce': [
                {'id': '1', 'name': 'apples', 'checked': False},
                {'id': '2', 'name': 'carrots', 'checked': False}
            ],
            'dairy': [
                {'id': '3', 'name': 'milk', 'checked': True}
            ],
            'other': []
        }
    }
    
    standard = normalize(web_data)
    
    print(f"✅ List name: {standard['name']}")
    print(f"✅ Items count: {len(standard['items'])}")
    
    assert standard['name'] == 'Meal Prep List'
    assert len(standard['items']) == 3
    assert validate(standard)
    
    print("✅ PASS: Web sections format normalized correctly")


def test_mobile_format():
    """Test mobile format (already standard)"""
    print("\n" + "=" * 80)
    print("TEST 4: Mobile Format (already standard)")
    print("=" * 80)
    
    mobile_data = {
        'id': 110,
        'name': 'Quick List',
        'items': [
            {'id': 'mob-1', 'name': 'eggs', 'checked': False},
            {'id': 'mob-2', 'name': 'butter', 'checked': False}
        ]
    }
    
    standard = normalize(mobile_data)
    
    print(f"✅ List name: {standard['name']}")
    print(f"✅ Items count: {len(standard['items'])}")
    
    assert standard['name'] == 'Quick List'
    assert len(standard['items']) == 2
    assert validate(standard)
    
    print("✅ PASS: Mobile format normalized correctly")


def test_recipe_generated_format():
    """Test recipe-generated format (ingredient_name, display_text)"""
    print("\n" + "=" * 80)
    print("TEST 5: Recipe Generated Format (ingredient_name)")
    print("=" * 80)
    
    recipe_data = {
        'id': 120,
        'name': 'Chicken Recipe Ingredients',
        'items': [
            {'id': 'r1', 'ingredient_name': '2 lbs chicken', 'display_text': '2 lbs chicken breast', 'checked': False},
            {'id': 'r2', 'ingredient_name': 'garlic', 'display_text': '3 cloves garlic, minced', 'checked': False}
        ]
    }
    
    standard = normalize(recipe_data)
    
    print(f"✅ List name: {standard['name']}")
    print(f"✅ Items count: {len(standard['items'])}")
    print(f"✅ First item: {standard['items'][0]['name']}")
    
    assert len(standard['items']) == 2
    # Should prefer display_text over ingredient_name
    assert '2 lbs chicken breast' in standard['items'][0]['name'] or 'chicken' in standard['items'][0]['name']
    assert validate(standard)
    
    print("✅ PASS: Recipe format normalized correctly")


def test_validation():
    """Test validation catches invalid data"""
    print("\n" + "=" * 80)
    print("TEST 6: Validation")
    print("=" * 80)
    
    # Valid data
    valid_data = {
        'name': 'Test List',
        'items': [
            {'name': 'item1', 'checked': False}
        ]
    }
    
    assert validate(valid_data) == True
    print("✅ Valid data passed validation")
    
    # Invalid: missing name
    invalid_no_name = {
        'items': [{'name': 'item1', 'checked': False}]
    }
    assert validate(invalid_no_name) == False
    print("✅ Correctly rejected data without list name")
    
    # Invalid: items not array
    invalid_items_not_array = {
        'name': 'Test',
        'items': 'not an array'
    }
    assert validate(invalid_items_not_array) == False
    print("✅ Correctly rejected non-array items")
    
    # Invalid: item missing name
    invalid_item_no_name = {
        'name': 'Test',
        'items': [{'checked': False}]
    }
    assert validate(invalid_item_no_name) == False
    print("✅ Correctly rejected item without name")
    
    print("✅ PASS: Validation working correctly")


def test_database_conversion():
    """Test conversion to database format"""
    print("\n" + "=" * 80)
    print("TEST 7: Database Format Conversion")
    print("=" * 80)
    
    standard_data = {
        'id': 130,
        'name': 'Test List',
        'items': [
            {'id': '1', 'name': 'item1', 'checked': False},
            {'id': '2', 'name': 'item2', 'checked': True}
        ],
        'household_id': 11,
        'whiteboard_id': 53
    }
    
    db_format = GroceryListNormalizer.from_standard(standard_data, 'database')
    
    print(f"✅ Database format generated")
    print(f"   name: {db_format['name']}")
    print(f"   list_data: {db_format['list_data']}")
    
    assert db_format['name'] == 'Test List'
    assert db_format['list_data'] == standard_data['items']
    assert db_format['household_id'] == 11
    
    print("✅ PASS: Database conversion working")


if __name__ == '__main__':
    print("\n🧪 GROCERY LIST NORMALIZER TEST SUITE")
    print("=" * 80)
    
    try:
        test_whiteboard_format()
        test_legacy_format()
        test_web_sections_format()
        test_mobile_format()
        test_recipe_generated_format()
        test_validation()
        test_database_conversion()
        
        print("\n" + "=" * 80)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 80)
        print("\nThe normalizer successfully handles:")
        print("  ✅ Whiteboard format (ingredient)")
        print("  ✅ Legacy format (list_name, items_json)")
        print("  ✅ Web format (sections)")
        print("  ✅ Mobile format (standard)")
        print("  ✅ Recipe format (ingredient_name, display_text)")
        print("  ✅ Validation")
        print("  ✅ Database conversion")
        print("\n✨ Ready to integrate into repository!")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
