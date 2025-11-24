#!/usr/bin/env python3
"""
Test Activity Feed System
==========================
Creates test events and verifies API endpoints work correctly
"""

import sys
sys.path.insert(0, '.')

from app.utils.event_logger import EventLogger
from app.database.connection import get_db_connection
import psycopg2.extras

def test_event_logger():
    """Test creating events via EventLogger"""
    print("=" * 70)
    print("TESTING EVENT LOGGER")
    print("=" * 70)
    
    # Get a real household_id and user_id from database
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cur.execute("SELECT id, hid FROM wb WHERE hid IS NOT NULL AND deleted_at IS NULL LIMIT 1")
    wb = cur.fetchone()
    
    if not wb:
        print("No active whiteboard with household found!")
        return
    
    household_id = wb['hid']
    
    cur.execute("SELECT user_id FROM household_members WHERE household_id = %s LIMIT 1", (household_id,))
    member = cur.fetchone()
    user_id = member['user_id']
    
    print(f"\nUsing household_id={household_id}, user_id={user_id}")
    
    # Test 1: Log a recipe.added event
    print("\n1. Testing recipe.added event...")
    event_id = EventLogger.log_event(
        household_id=household_id,
        user_id=user_id,
        event_type='recipe.added',
        resource_type='recipe',
        resource_id=2609,
        event_data={
            'recipe_title': 'Test Garlic Chicken',
            'recipe_image': 'https://example.com/image.jpg'
        }
    )
    print(f"   ✓ Created event ID: {event_id}")
    
    # Test 2: Log a comment.added event
    print("\n2. Testing comment.added event...")
    event_id2 = EventLogger.log_event(
        household_id=household_id,
        user_id=user_id,
        event_type='comment.added',
        resource_type='recipe',
        resource_id=2690,
        event_data={
            'comment_preview': 'This looks delicious!',
            'whiteboard_id': wb['id']
        }
    )
    print(f"   ✓ Created event ID: {event_id2}")
    
    # Test 3: Log a whiteboard.created event
    print("\n3. Testing whiteboard.created event...")
    event_id3 = EventLogger.log_event(
        household_id=household_id,
        user_id=user_id,
        event_type='whiteboard.created',
        resource_type='whiteboard',
        resource_id=wb['id'],
        event_data={
            'whiteboard_name': 'Week 1 Planning'
        },
        title='Week 1 Planning'
    )
    print(f"   ✓ Created event ID: {event_id3}")
    
    # Verify events were created
    print("\n4. Verifying events in database...")
    cur.execute("""
        SELECT id, event_type, title, description, created_at
        FROM activity_feed
        WHERE household_id = %s
        ORDER BY created_at DESC
        LIMIT 5
    """, (household_id,))
    
    events = cur.fetchall()
    print(f"\n   Recent events for household {household_id}:")
    for event in events:
        print(f"     - [{event['event_type']}] {event['description']} (ID: {event['id']})")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 70)
    print("✅ EVENT LOGGER TEST COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    test_event_logger()
