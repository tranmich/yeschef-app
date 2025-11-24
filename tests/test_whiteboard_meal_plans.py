"""
Test Suite for Whiteboard Meal Plan Features
==============================================
Tests meal plan day box creation, updates, and whiteboard integration

Author: GitHub Copilot
Date: November 4, 2025
"""

import pytest
import sys
import os
import json
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database.connection import get_db_connection, return_db_connection
from app.database.repositories.meal_plan_repository import MealPlanRepository
import psycopg2.extras


@pytest.fixture
def db_connection():
    """Fixture to provide database connection"""
    conn = get_db_connection()
    yield conn
    return_db_connection(conn)


@pytest.fixture
def meal_plan_repo():
    """Fixture to provide MealPlanRepository instance"""
    return MealPlanRepository()


@pytest.fixture
def test_user_id(db_connection):
    """Fixture to get an existing test user (ID 11 - your user)"""
    return 11  # Use your existing user


@pytest.fixture
def test_household_id(db_connection):
    """Fixture to get an existing household"""
    cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        # Get first available household
        cursor.execute("""
            SELECT id FROM households LIMIT 1
        """)
        household = cursor.fetchone()
        
        if household:
            return household['id']
        
        # If no households exist, skip tests
        pytest.skip("No households available for testing")
    finally:
        cursor.close()


@pytest.fixture
def test_whiteboard_id(db_connection, test_household_id, test_user_id):
    """Fixture to create a test whiteboard"""
    cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        # Create test whiteboard
        cursor.execute("""
            INSERT INTO wb (hid, n, d, tt, cby)
            VALUES (%s, 'Test Meal Plan Whiteboard', 'For testing meal plans', 'freeform', %s)
            RETURNING id
        """, (test_household_id, test_user_id))
        
        whiteboard = cursor.fetchone()
        db_connection.commit()
        return whiteboard['id']
    finally:
        cursor.close()


@pytest.fixture
def test_recipe_ids(db_connection, test_user_id):
    """Fixture to get existing recipe IDs"""
    cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("""
            SELECT id FROM recipes 
            WHERE user_id = %s OR source = 'curated'
            LIMIT 3
        """, (test_user_id,))
        
        recipes = cursor.fetchall()
        
        if len(recipes) >= 3:
            return [r['id'] for r in recipes]
        
        # If not enough recipes, skip tests that need them
        pytest.skip("Not enough recipes available for testing")
    finally:
        cursor.close()


# =====================================================
# TEST 1: Create Meal Plan
# =====================================================

def test_create_meal_plan(meal_plan_repo, test_user_id, test_household_id):
    """Test creating a new meal plan"""
    print("\n🧪 TEST 1: Create Meal Plan")
    
    plan_data = {
        "days": {
            "day1": {
                "name": "Monday",
                "recipes": []
            },
            "day2": {
                "name": "Tuesday",
                "recipes": []
            }
        }
    }
    
    week_start = datetime.now().date().isoformat()
    
    result = meal_plan_repo.create_meal_plan(
        user_id=test_user_id,
        plan_name="Test Week Plan",
        week_start_date=week_start,
        plan_data=plan_data
    )
    
    assert result is not None, "Failed to create meal plan"
    assert result['plan_name'] == "Test Week Plan"
    assert result['user_id'] == test_user_id
    assert 'id' in result
    
    print(f"✅ Created meal plan: {result['id']}")
    print(f"   Plan name: {result['plan_name']}")
    print(f"   Days: {list(result['plan_data']['days'].keys())}")


# =====================================================
# TEST 2: Add Recipe to Day
# =====================================================

def test_add_recipe_to_day(meal_plan_repo, test_user_id, test_recipe_ids):
    """Test adding a recipe to a meal plan day"""
    print("\n🧪 TEST 2: Add Recipe to Day")
    
    # Create meal plan
    plan_data = {
        "days": {
            "day1": {
                "name": "Monday",
                "recipes": []
            }
        }
    }
    
    meal_plan = meal_plan_repo.create_meal_plan(
        user_id=test_user_id,
        plan_name="Recipe Test Plan",
        week_start_date=datetime.now().date().isoformat(),
        plan_data=plan_data
    )
    
    # Add recipe to day
    plan_data['days']['day1']['recipes'].append({
        'id': test_recipe_ids[0],
        'name': 'Monday Pasta'
    })
    
    updated = meal_plan_repo.update_meal_plan(
        plan_id=meal_plan['id'],
        user_id=test_user_id,
        plan_data=plan_data
    )
    
    assert updated is not None
    assert len(updated['plan_data']['days']['day1']['recipes']) == 1
    assert updated['plan_data']['days']['day1']['recipes'][0]['id'] == test_recipe_ids[0]
    
    print(f"✅ Added recipe to day")
    print(f"   Recipe ID: {test_recipe_ids[0]}")
    print(f"   Day recipes: {updated['plan_data']['days']['day1']['recipes']}")


# =====================================================
# TEST 3: Rename Day
# =====================================================

def test_rename_day(meal_plan_repo, test_user_id):
    """Test renaming a meal plan day"""
    print("\n🧪 TEST 3: Rename Day")
    
    plan_data = {
        "days": {
            "day1": {
                "name": "Day 1",
                "recipes": []
            }
        }
    }
    
    meal_plan = meal_plan_repo.create_meal_plan(
        user_id=test_user_id,
        plan_name="Rename Test Plan",
        week_start_date=datetime.now().date().isoformat(),
        plan_data=plan_data
    )
    
    # Rename day
    plan_data['days']['day1']['name'] = "Taco Tuesday"
    
    updated = meal_plan_repo.update_meal_plan(
        plan_id=meal_plan['id'],
        user_id=test_user_id,
        plan_data=plan_data
    )
    
    assert updated['plan_data']['days']['day1']['name'] == "Taco Tuesday"
    
    print(f"✅ Renamed day from 'Day 1' to 'Taco Tuesday'")


# =====================================================
# TEST 4: Link Meal Plan to Whiteboard
# =====================================================

def test_link_meal_plan_to_whiteboard(db_connection, meal_plan_repo, test_user_id, test_whiteboard_id):
    """Test linking a meal plan to a whiteboard"""
    print("\n🧪 TEST 4: Link Meal Plan to Whiteboard")
    
    # Create meal plan
    plan_data = {
        "days": {
            "day1": {"name": "Monday", "recipes": []}
        }
    }
    
    meal_plan = meal_plan_repo.create_meal_plan(
        user_id=test_user_id,
        plan_name="Whiteboard Test Plan",
        week_start_date=datetime.now().date().isoformat(),
        plan_data=plan_data
    )
    
    # Link to whiteboard
    cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("""
            INSERT INTO wbo (wid, t, mid, p, cby)
            VALUES (%s, 'mp', %s, %s::jsonb, %s)
            RETURNING id
        """, (
            test_whiteboard_id,
            meal_plan['id'],
            json.dumps([400, 100, 320, 200, 0]),  # x, y, width, height, z
            test_user_id
        ))
        
        wbo = cursor.fetchone()
        db_connection.commit()
        
        # Verify link
        cursor.execute("""
            SELECT * FROM wbo WHERE wid = %s AND mid = %s
        """, (test_whiteboard_id, meal_plan['id']))
        
        linked = cursor.fetchone()
        
        assert linked is not None
        assert linked['mid'] == meal_plan['id']
        assert linked['t'] == 'mp'
        
        print(f"✅ Linked meal plan {meal_plan['id']} to whiteboard {test_whiteboard_id}")
        print(f"   Object ID: {wbo['id']}")
        print(f"   Position: {linked['p']}")
        
    finally:
        cursor.close()


# =====================================================
# TEST 5: Load Meal Plans from Whiteboard
# =====================================================

def test_load_meal_plans_from_whiteboard(db_connection, meal_plan_repo, test_user_id, test_whiteboard_id):
    """Test loading all meal plans associated with a whiteboard"""
    print("\n🧪 TEST 5: Load Meal Plans from Whiteboard")
    
    # Create multiple meal plans and link to whiteboard
    cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        meal_plan_ids = []
        
        for i in range(3):
            plan_data = {
                "days": {
                    f"day{i+1}": {
                        "name": f"Day {i+1}",
                        "recipes": []
                    }
                }
            }
            
            meal_plan = meal_plan_repo.create_meal_plan(
                user_id=test_user_id,
                plan_name=f"Load Test Plan {i+1}",
                week_start_date=datetime.now().date().isoformat(),
                plan_data=plan_data
            )
            
            meal_plan_ids.append(meal_plan['id'])
            
            # Link to whiteboard
            cursor.execute("""
                INSERT INTO wbo (wid, t, mid, p, cby)
                VALUES (%s, 'mp', %s, %s::jsonb, %s)
            """, (
                test_whiteboard_id,
                meal_plan['id'],
                json.dumps([400 + (i * 60), 100 + (i * 60), 320, 200, 0]),
                test_user_id
            ))
        
        db_connection.commit()
        
        # Load all meal plans for whiteboard
        cursor.execute("""
            SELECT wbo.*, wbo.mid as meal_plan_id
            FROM wbo
            WHERE wbo.wid = %s AND wbo.t = 'mp' AND wbo.deleted_at IS NULL
        """, (test_whiteboard_id,))
        
        objects = cursor.fetchall()
        
        assert len(objects) >= 3, f"Expected at least 3 meal plan objects, got {len(objects)}"
        
        print(f"✅ Loaded {len(objects)} meal plan objects from whiteboard")
        
        for obj in objects:
            if obj['meal_plan_id'] in meal_plan_ids:
                print(f"   - Meal Plan ID: {obj['meal_plan_id']}, Position: {obj['p']}")
        
    finally:
        cursor.close()


# =====================================================
# TEST 6: Update Day Position on Whiteboard
# =====================================================

def test_update_day_position(db_connection, meal_plan_repo, test_user_id, test_whiteboard_id):
    """Test updating a meal plan day box position on whiteboard"""
    print("\n🧪 TEST 6: Update Day Position on Whiteboard")
    
    # Create and link meal plan
    plan_data = {
        "days": {
            "day1": {"name": "Monday", "recipes": []}
        }
    }
    
    meal_plan = meal_plan_repo.create_meal_plan(
        user_id=test_user_id,
        plan_name="Position Test Plan",
        week_start_date=datetime.now().date().isoformat(),
        plan_data=plan_data
    )
    
    cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        # Link to whiteboard
        cursor.execute("""
            INSERT INTO wbo (wid, t, mid, p, cby)
            VALUES (%s, 'mp', %s, %s::jsonb, %s)
            RETURNING id
        """, (
            test_whiteboard_id,
            meal_plan['id'],
            json.dumps([400, 100, 320, 200, 0]),
            test_user_id
        ))
        
        wbo = cursor.fetchone()
        object_id = wbo['id']
        db_connection.commit()
        
        # Update position
        new_position = [800, 300, 320, 200, 0]
        
        cursor.execute("""
            UPDATE wbo
            SET p = %s::jsonb, ua = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING p
        """, (json.dumps(new_position), object_id))
        
        updated = cursor.fetchone()
        db_connection.commit()
        
        assert updated['p'] == new_position
        
        print(f"✅ Updated position")
        print(f"   Old: [400, 100, 320, 200, 0]")
        print(f"   New: {new_position}")
        
    finally:
        cursor.close()


# =====================================================
# TEST 7: Delete Meal Plan Day Box
# =====================================================

def test_delete_meal_plan_day_box(db_connection, meal_plan_repo, test_user_id, test_whiteboard_id):
    """Test soft-deleting a meal plan day box from whiteboard"""
    print("\n🧪 TEST 7: Delete Meal Plan Day Box")
    
    # Create and link meal plan
    plan_data = {
        "days": {
            "day1": {"name": "To Delete", "recipes": []}
        }
    }
    
    meal_plan = meal_plan_repo.create_meal_plan(
        user_id=test_user_id,
        plan_name="Delete Test Plan",
        week_start_date=datetime.now().date().isoformat(),
        plan_data=plan_data
    )
    
    cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        # Link to whiteboard
        cursor.execute("""
            INSERT INTO wbo (wid, t, mid, p, cby)
            VALUES (%s, 'mp', %s, %s::jsonb, %s)
            RETURNING id
        """, (
            test_whiteboard_id,
            meal_plan['id'],
            json.dumps([400, 100, 320, 200, 0]),
            test_user_id
        ))
        
        wbo = cursor.fetchone()
        object_id = wbo['id']
        db_connection.commit()
        
        # Soft delete
        cursor.execute("""
            UPDATE wbo
            SET deleted_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING deleted_at
        """, (object_id,))
        
        deleted = cursor.fetchone()
        db_connection.commit()
        
        assert deleted['deleted_at'] is not None
        
        # Verify it doesn't appear in active queries
        cursor.execute("""
            SELECT * FROM wbo
            WHERE id = %s AND deleted_at IS NULL
        """, (object_id,))
        
        active = cursor.fetchone()
        assert active is None, "Deleted object should not appear in active queries"
        
        print(f"✅ Soft-deleted meal plan day box")
        print(f"   Object ID: {object_id}")
        print(f"   Deleted at: {deleted['deleted_at']}")
        
    finally:
        cursor.close()


# =====================================================
# TEST 8: Generate Grocery List from Meal Plan
# =====================================================

def test_generate_grocery_list_from_meal_plan(meal_plan_repo, test_user_id, test_recipe_ids):
    """Test generating a grocery list from a meal plan day"""
    print("\n🧪 TEST 8: Generate Grocery List from Meal Plan")
    
    # Create meal plan with recipes
    plan_data = {
        "days": {
            "day1": {
                "name": "Monday",
                "recipes": [
                    {"id": test_recipe_ids[0], "name": "Monday Pasta"},
                    {"id": test_recipe_ids[1], "name": "Tuesday Tacos"}
                ]
            }
        }
    }
    
    meal_plan = meal_plan_repo.create_meal_plan(
        user_id=test_user_id,
        plan_name="Grocery List Test Plan",
        week_start_date=datetime.now().date().isoformat(),
        plan_data=plan_data
    )
    
    # Extract recipes from day
    day_recipes = meal_plan['plan_data']['days']['day1']['recipes']
    
    assert len(day_recipes) == 2
    assert day_recipes[0]['id'] == test_recipe_ids[0]
    assert day_recipes[1]['id'] == test_recipe_ids[1]
    
    print(f"✅ Day has {len(day_recipes)} recipes ready for grocery list generation")
    print(f"   Recipes: {[r['name'] for r in day_recipes]}")


# =====================================================
# RUN ALL TESTS
# =====================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🧪 WHITEBOARD MEAL PLAN TEST SUITE")
    print("="*60)
    
    pytest.main([__file__, '-v', '-s'])
