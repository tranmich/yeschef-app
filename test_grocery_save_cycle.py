"""
Test Grocery List Save/Load Cycle
==================================
Simulates what the whiteboard does: save changes, reload, verify
"""

import requests
import json
from datetime import datetime

# Configuration
API_URL = "http://127.0.0.1:5000"
WHITEBOARD_ID = 53
USER_TOKEN = "your-jwt-token-here"  # Get from browser console: localStorage.getItem('token')

def test_save_load_cycle():
    print("=" * 80)
    print("TESTING GROCERY LIST SAVE/LOAD CYCLE")
    print("=" * 80)
    print()
    
    # You need to get your JWT token from the browser
    print("⚠️  To run this test:")
    print("   1. Open browser console")
    print("   2. Type: localStorage.getItem('token')")
    print("   3. Copy the token")
    print("   4. Update USER_TOKEN in this script")
    print()
    
    headers = {
        "Authorization": f"Bearer {USER_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Step 1: Get existing lists
    print("STEP 1: Loading existing grocery lists...")
    print("-" * 80)
    
    response = requests.get(
        f"{API_URL}/api/v2/whiteboard/{WHITEBOARD_ID}/grocery-lists",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to load lists: {response.status_code}")
        print(response.text)
        return
    
    data = response.json()
    lists = data.get('data', {}).get('grocery_lists', [])
    
    print(f"✅ Loaded {len(lists)} grocery lists")
    for lst in lists:
        print(f"   • ID {lst['id']}: '{lst['name']}' - {len(lst.get('items', []))} items")
    
    if len(lists) == 0:
        print("\n❌ No grocery lists found to test with!")
        return
    
    # Use first list for testing
    test_list = lists[0]
    list_id = test_list['id']
    original_items = test_list.get('items', [])
    
    print(f"\nUsing list #{list_id} for testing: '{test_list['name']}'")
    print(f"Original items: {len(original_items)}")
    print()
    
    # Step 2: Make changes (simulate what user does)
    print("STEP 2: Making changes...")
    print("-" * 80)
    
    # Add a test item
    new_item = {
        "id": max([item.get('id', 0) for item in original_items] + [0]) + 1,
        "ingredient": f"TEST BANANA {datetime.now().strftime('%H:%M:%S')}",
        "checked": False
    }
    
    # Reorder: move last item to first
    modified_items = original_items.copy()
    if len(modified_items) > 1:
        modified_items = [modified_items[-1]] + modified_items[:-1]
    
    # Add new item at top
    modified_items = [new_item] + modified_items
    
    print(f"   • Added item: '{new_item['ingredient']}'")
    print(f"   • Reordered items")
    print(f"   • New count: {len(modified_items)} items")
    print()
    
    # Step 3: Save changes
    print("STEP 3: Saving changes...")
    print("-" * 80)
    
    update_data = {
        "name": test_list['name'],
        "items": modified_items
    }
    
    print(f"Sending update with {len(modified_items)} items...")
    
    response = requests.patch(
        f"{API_URL}/api/v2/whiteboard/{WHITEBOARD_ID}/grocery-lists/{list_id}",
        headers=headers,
        json=update_data
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to save: {response.status_code}")
        print(response.text)
        return
    
    save_result = response.json()
    print(f"✅ Saved successfully")
    print()
    
    # Step 4: Reload and verify
    print("STEP 4: Reloading to verify...")
    print("-" * 80)
    
    response = requests.get(
        f"{API_URL}/api/v2/whiteboard/{WHITEBOARD_ID}/grocery-lists",
        headers=headers
    )
    
    reloaded_data = response.json()
    reloaded_lists = reloaded_data.get('data', {}).get('grocery_lists', [])
    reloaded_list = next((lst for lst in reloaded_lists if lst['id'] == list_id), None)
    
    if not reloaded_list:
        print(f"❌ List {list_id} not found after reload!")
        return
    
    reloaded_items = reloaded_list.get('items', [])
    
    print(f"Reloaded {len(reloaded_items)} items")
    print()
    
    # Step 5: Compare
    print("STEP 5: Verification...")
    print("-" * 80)
    
    if len(reloaded_items) == len(modified_items):
        print(f"✅ Item count matches: {len(reloaded_items)}")
    else:
        print(f"❌ Item count mismatch!")
        print(f"   Expected: {len(modified_items)}")
        print(f"   Got: {len(reloaded_items)}")
    
    # Check if new item exists
    found_test_item = any("TEST BANANA" in item.get('ingredient', '') for item in reloaded_items)
    if found_test_item:
        print(f"✅ New item found in reloaded data")
    else:
        print(f"❌ New item NOT found!")
    
    # Check order
    if reloaded_items and modified_items:
        if reloaded_items[0].get('ingredient') == modified_items[0].get('ingredient'):
            print(f"✅ Item order preserved")
        else:
            print(f"❌ Item order changed!")
            print(f"   Expected first: '{modified_items[0].get('ingredient')}'")
            print(f"   Got first: '{reloaded_items[0].get('ingredient')}'")
    
    print()
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    test_save_load_cycle()
