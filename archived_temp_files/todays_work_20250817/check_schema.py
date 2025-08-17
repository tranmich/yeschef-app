#!/usr/bin/env python3
"""
Check if intelligence columns exist in recipes table
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor

def check_intelligence_columns():
    try:
        # Connect to database
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            print("❌ DATABASE_URL not found")
            return
            
        conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        cur = conn.cursor()
        
        # Check if intelligence columns exist
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'recipes' 
            AND column_name IN (
                'meal_role', 'meal_role_confidence', 'time_min', 'steps_count',
                'pots_pans_count', 'is_easy', 'is_one_pot', 'leftover_friendly', 'kid_friendly'
            )
            ORDER BY column_name;
        """)
        
        columns = cur.fetchall()
        
        if columns:
            print(f"✅ Found {len(columns)} intelligence columns:")
            for col in columns:
                print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        else:
            print("❌ No intelligence columns found - need to run schema migration first!")
            
        # Also check total column count
        cur.execute("""
            SELECT COUNT(*) as total_columns
            FROM information_schema.columns 
            WHERE table_name = 'recipes';
        """)
        
        total = cur.fetchone()
        print(f"📊 Total columns in recipes table: {total['total_columns']}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking schema: {e}")

if __name__ == "__main__":
    check_intelligence_columns()
