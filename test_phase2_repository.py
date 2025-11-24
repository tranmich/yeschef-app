"""
Test Phase 2 Repository Changes
================================
Verify that repository works with clean schema (name, list_data, updated_at)
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.repositories.grocery_list_repository import GroceryListRepository
from datetime import datetime

def test_phase2_repository():
    print("=" * 80)
    print("TESTING PHASE 2 REPOSITORY CHANGES")
    print("=" * 80)
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    repo = GroceryListRepository()
    test_results = []
    
    # Test 1: Create grocery list
    print("TEST 1: Create grocery list (Phase 2 schema)")
    print("-" * 80)
    
    try:
        test_list = repo.create_grocery_list(
            user_id=11,
            name=f"Phase 2 Test {datetime.now().strftime('%H:%M:%S')}",
            items=[
                {"id": 1, "ingredient": "Test Item 1", "checked": False},
                {"id": 2, "ingredient": "Test Item 2", "checked": False}
            ],
            household_id=11,
            whiteboard_id=53
        )
        
        if test_list and 'id' in test_list:
            print(f"   ✅ PASS: Created list ID {test_list['id']}")
            print(f"      Name: {test_list['name']}")
            print(f"      Items: {len(test_list.get('items', []))}")
            test_results.append(("Create", True, test_list['id']))
            created_id = test_list['id']
        else:
            print(f"   ❌ FAIL: Create returned None or invalid data")
            test_results.append(("Create", False, None))
            created_id = None
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        test_results.append(("Create", False, None))
        created_id = None
    
    print()
    
    # Test 2: Read grocery list
    if created_id:
        print("TEST 2: Read grocery list by ID")
        print("-" * 80)
        
        try:
            read_list = repo.get_grocery_list_by_id(created_id, user_id=11)
            
            if read_list and read_list.get('name'):
                print(f"   ✅ PASS: Retrieved list ID {created_id}")
                print(f"      Name: {read_list['name']}")
                print(f"      Items: {len(read_list.get('items', []))}")
                test_results.append(("Read", True, created_id))
            else:
                print(f"   ❌ FAIL: Could not read list")
                test_results.append(("Read", False, created_id))
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            test_results.append(("Read", False, created_id))
        
        print()
    
    # Test 3: Update grocery list
    if created_id:
        print("TEST 3: Update grocery list")
        print("-" * 80)
        
        try:
            updated_list = repo.update_grocery_list(
                list_id=created_id,
                user_id=11,
                name=f"Phase 2 Updated {datetime.now().strftime('%H:%M:%S')}",
                items=[
                    {"id": 1, "ingredient": "Updated Item 1", "checked": True},
                    {"id": 2, "ingredient": "Updated Item 2", "checked": False},
                    {"id": 3, "ingredient": "New Item 3", "checked": False}
                ]
            )
            
            if updated_list and updated_list.get('name'):
                print(f"   ✅ PASS: Updated list ID {created_id}")
                print(f"      Name: {updated_list['name']}")
                print(f"      Items: {len(updated_list.get('items', []))}")
                test_results.append(("Update", True, created_id))
            else:
                print(f"   ❌ FAIL: Update returned None")
                test_results.append(("Update", False, created_id))
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            test_results.append(("Update", False, created_id))
        
        print()
    
    # Test 4: Get user lists
    print("TEST 4: Get user grocery lists")
    print("-" * 80)
    
    try:
        user_lists = repo.get_user_grocery_lists(user_id=11, limit=10)
        
        if user_lists is not None:
            print(f"   ✅ PASS: Retrieved {len(user_lists)} lists")
            if created_id:
                found = any(lst.get('id') == created_id for lst in user_lists)
                print(f"      Test list found: {found}")
            test_results.append(("List", True, None))
        else:
            print(f"   ❌ FAIL: Could not retrieve lists")
            test_results.append(("List", False, None))
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        test_results.append(("List", False, None))
    
    print()
    
    # Test 5: Delete (cleanup)
    if created_id:
        print("TEST 5: Delete test list (cleanup)")
        print("-" * 80)
        
        try:
            deleted = repo.delete_grocery_list(created_id, user_id=11)
            
            if deleted:
                print(f"   ✅ PASS: Deleted list ID {created_id}")
                test_results.append(("Delete", True, created_id))
            else:
                print(f"   ❌ FAIL: Could not delete list")
                test_results.append(("Delete", False, created_id))
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            test_results.append(("Delete", False, created_id))
        
        print()
    
    # Summary
    print("=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    
    for test_name, passed, test_id in test_results:
        status = "✅ PASS" if passed else "❌ FAIL"
        id_str = f"(ID: {test_id})" if test_id else ""
        print(f"  {status:10} {test_name:10} {id_str}")
    
    all_passed = all(result[1] for result in test_results)
    
    print()
    print("=" * 80)
    
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print()
        print("Phase 2 repository changes are working correctly.")
        print("Safe to proceed with dropping legacy columns.")
    else:
        print("⚠️  SOME TESTS FAILED")
        print()
        print("Do NOT drop columns until all tests pass!")
    
    print("=" * 80)
    
    return all_passed

if __name__ == '__main__':
    success = test_phase2_repository()
    sys.exit(0 if success else 1)
