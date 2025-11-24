#!/usr/bin/env python3
"""Check if comment events are being logged"""

import sys
sys.path.insert(0, '.')

from app.database.connection import get_db_connection
import psycopg2.extras

def check_comment_events():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    print("=" * 70)
    print("CHECKING COMMENT EVENTS")
    print("=" * 70)
    
    # Check recent comments
    cur.execute("""
        SELECT c.id, c.whiteboard_id, c.object_type, c.content, c.created_at, 
               wb.hid as household_id
        FROM comments c
        LEFT JOIN wb ON c.whiteboard_id = wb.id
        ORDER BY c.created_at DESC
        LIMIT 3
    """)
    
    comments = cur.fetchall()
    print("\n📝 Recent Comments:")
    for c in comments:
        print(f"  Comment {c['id']}: '{c['content'][:50]}...' | WB:{c['whiteboard_id']} | HID:{c['household_id']} | {c['created_at']}")
    
    # Check if events were logged for these comments
    print("\n🔔 Checking for comment events in activity_feed...")
    cur.execute("""
        SELECT id, event_type, household_id, user_id, description, created_at
        FROM activity_feed
        WHERE event_type = 'comment.added'
        ORDER BY created_at DESC
        LIMIT 5
    """)
    
    events = cur.fetchall()
    if events:
        print(f"\n✅ Found {len(events)} comment events:")
        for e in events:
            print(f"  Event {e['id']}: {e['description']} | HID:{e['household_id']} | {e['created_at']}")
    else:
        print("\n❌ NO comment events found in activity_feed!")
        print("   This means event logging is NOT working for comments.")
    
    # Check all recent events
    print("\n📊 All Recent Events:")
    cur.execute("""
        SELECT id, event_type, description, created_at
        FROM activity_feed
        ORDER BY created_at DESC
        LIMIT 10
    """)
    
    all_events = cur.fetchall()
    for e in all_events:
        print(f"  {e['event_type']}: {e['description']} | {e['created_at']}")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    check_comment_events()
