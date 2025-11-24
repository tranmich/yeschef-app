#!/usr/bin/env python3
"""
Enhance activity_feed table for household collaboration
Adds columns needed for household activity tracking
"""

import sys
sys.path.insert(0, '.')

from app.database.connection import get_db_connection
import psycopg2.extras

def enhance_activity_feed():
    """Add columns and indexes to activity_feed table"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    try:
        print("=" * 70)
        print("ENHANCING ACTIVITY_FEED TABLE FOR HOUSEHOLD FEATURES")
        print("=" * 70)
        
        # Add household_id column
        print("\n1. Adding household_id column...")
        cur.execute("""
            ALTER TABLE activity_feed 
            ADD COLUMN IF NOT EXISTS household_id INTEGER
        """)
        print("   ✓ household_id added")
        
        # Add resource_type column
        print("\n2. Adding resource_type column...")
        cur.execute("""
            ALTER TABLE activity_feed 
            ADD COLUMN IF NOT EXISTS resource_type VARCHAR(50)
        """)
        print("   ✓ resource_type added")
        
        # Add event_data JSONB column
        print("\n3. Adding event_data JSONB column...")
        cur.execute("""
            ALTER TABLE activity_feed 
            ADD COLUMN IF NOT EXISTS event_data JSONB
        """)
        print("   ✓ event_data added")
        
        # Add is_read column
        print("\n4. Adding is_read column...")
        cur.execute("""
            ALTER TABLE activity_feed 
            ADD COLUMN IF NOT EXISTS is_read BOOLEAN DEFAULT FALSE
        """)
        print("   ✓ is_read added")
        
        # Rename activity_type to event_type for consistency
        print("\n5. Renaming activity_type to event_type...")
        cur.execute("""
            DO $$ 
            BEGIN
                IF EXISTS(SELECT 1 FROM information_schema.columns 
                         WHERE table_name='activity_feed' AND column_name='activity_type') THEN
                    ALTER TABLE activity_feed RENAME COLUMN activity_type TO event_type;
                END IF;
            END $$;
        """)
        print("   ✓ event_type renamed")
        
        # Create indexes for performance
        print("\n6. Creating performance indexes...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_activity_feed_household_date 
            ON activity_feed(household_id, created_at DESC)
        """)
        print("   ✓ Index on household_id + created_at")
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_activity_feed_user_date 
            ON activity_feed(user_id, created_at DESC)
        """)
        print("   ✓ Index on user_id + created_at")
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_activity_feed_event_type 
            ON activity_feed(event_type)
        """)
        print("   ✓ Index on event_type")
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_activity_feed_resource 
            ON activity_feed(resource_type, reference_id)
        """)
        print("   ✓ Index on resource_type + reference_id")
        
        conn.commit()
        
        # Verify changes
        print("\n" + "=" * 70)
        print("VERIFICATION - Updated Schema:")
        print("=" * 70)
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'activity_feed'
            ORDER BY ordinal_position
        """)
        
        columns = cur.fetchall()
        for col in columns:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            default = f", DEFAULT {col['column_default']}" if col['column_default'] else ""
            print(f"  {col['column_name']:<20} {col['data_type']:<20} {nullable}{default}")
        
        print("\n" + "=" * 70)
        print("SUCCESS! activity_feed table is ready for household events")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()
    
    return True


if __name__ == '__main__':
    success = enhance_activity_feed()
    sys.exit(0 if success else 1)
