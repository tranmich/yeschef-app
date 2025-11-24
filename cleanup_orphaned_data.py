#!/usr/bin/env python3
"""
Cleanup Orphaned Whiteboard Data
=================================
Soft deletes grocery lists and meal plans that are linked to deleted whiteboards.

This script identifies and cleans up data bloat from deleted whiteboards.
"""

import sys
sys.path.insert(0, '.')

from app.database.connection import get_db_connection
import psycopg2.extras
from datetime import datetime

def cleanup_orphaned_grocery_lists():
    """Delete grocery lists linked to deleted whiteboards"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    try:
        print("=" * 70)
        print("CLEANING UP ORPHANED GROCERY LISTS")
        print("=" * 70)
        
        # Find orphaned grocery lists
        cur.execute("""
            SELECT gl.id, gl.name, gl.wid, wb.deleted_at
            FROM grocery_lists gl
            INNER JOIN wb ON gl.wid = wb.id
            WHERE gl.wid IS NOT NULL
            AND wb.deleted_at IS NOT NULL
            AND gl.deleted_at IS NULL
            ORDER BY gl.wid, gl.id
        """)
        
        orphaned_lists = cur.fetchall()
        
        if not orphaned_lists:
            print("✅ No orphaned grocery lists found!")
            return 0
        
        print(f"\n📋 Found {len(orphaned_lists)} orphaned grocery lists:")
        for lst in orphaned_lists:
            print(f"  - List ID {lst['id']}: '{lst['name']}' (whiteboard {lst['wid']} deleted on {lst['deleted_at']})")
        
        # Confirm deletion
        confirm = input(f"\n⚠️  Delete these {len(orphaned_lists)} orphaned lists? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ Cleanup cancelled by user")
            return 0
        
        # Soft delete orphaned lists
        cur.execute("""
            UPDATE grocery_lists
            SET deleted_at = NOW()
            WHERE id IN (
                SELECT gl.id
                FROM grocery_lists gl
                INNER JOIN wb ON gl.wid = wb.id
                WHERE gl.wid IS NOT NULL
                AND wb.deleted_at IS NOT NULL
                AND gl.deleted_at IS NULL
            )
        """)
        
        deleted_count = cur.rowcount
        conn.commit()
        
        print(f"\n✅ Successfully deleted {deleted_count} orphaned grocery lists!")
        return deleted_count
        
    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")
        conn.rollback()
        return 0
    finally:
        cur.close()
        conn.close()


def cleanup_orphaned_whiteboard_objects():
    """Delete whiteboard objects linked to deleted whiteboards"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    try:
        print("\n" + "=" * 70)
        print("CLEANING UP ORPHANED WHITEBOARD OBJECTS")
        print("=" * 70)
        
        # Find orphaned objects
        cur.execute("""
            SELECT wbo.id, wbo.t as type, wbo.wid, wb.deleted_at
            FROM wbo
            INNER JOIN wb ON wbo.wid = wb.id
            WHERE wb.deleted_at IS NOT NULL
            AND wbo.deleted_at IS NULL
            ORDER BY wbo.wid, wbo.id
        """)
        
        orphaned_objects = cur.fetchall()
        
        if not orphaned_objects:
            print("✅ No orphaned whiteboard objects found!")
            return 0
        
        print(f"\n📦 Found {len(orphaned_objects)} orphaned whiteboard objects:")
        type_counts = {}
        for obj in orphaned_objects:
            obj_type = obj['type']
            type_counts[obj_type] = type_counts.get(obj_type, 0) + 1
        
        for obj_type, count in type_counts.items():
            type_map = {'rc': 'recipe cards', 'gl': 'grocery lists', 'mp': 'meal plans', 'nt': 'notes'}
            print(f"  - {count} {type_map.get(obj_type, obj_type)}")
        
        # Confirm deletion
        confirm = input(f"\n⚠️  Delete these {len(orphaned_objects)} orphaned objects? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ Cleanup cancelled by user")
            return 0
        
        # Soft delete orphaned objects
        cur.execute("""
            UPDATE wbo
            SET deleted_at = NOW()
            WHERE id IN (
                SELECT wbo.id
                FROM wbo
                INNER JOIN wb ON wbo.wid = wb.id
                WHERE wb.deleted_at IS NOT NULL
                AND wbo.deleted_at IS NULL
            )
        """)
        
        deleted_count = cur.rowcount
        conn.commit()
        
        print(f"\n✅ Successfully deleted {deleted_count} orphaned whiteboard objects!")
        return deleted_count
        
    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")
        conn.rollback()
        return 0
    finally:
        cur.close()
        conn.close()


def main():
    """Run all cleanup tasks"""
    print("\n" + "=" * 70)
    print("ORPHANED WHITEBOARD DATA CLEANUP UTILITY")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Cleanup grocery lists
    deleted_lists = cleanup_orphaned_grocery_lists()
    
    # Cleanup whiteboard objects
    deleted_objects = cleanup_orphaned_whiteboard_objects()
    
    # Summary
    print("\n" + "=" * 70)
    print("CLEANUP SUMMARY")
    print("=" * 70)
    print(f"✅ Deleted {deleted_lists} orphaned grocery lists")
    print(f"✅ Deleted {deleted_objects} orphaned whiteboard objects")
    print(f"✅ Total: {deleted_lists + deleted_objects} records cleaned up")
    print("=" * 70)
    
    if deleted_lists + deleted_objects > 0:
        print("\n💡 Future deletions will be automatic via CASCADE DELETE in the API")
    

if __name__ == '__main__':
    main()
