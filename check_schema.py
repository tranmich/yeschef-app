#!/usr/bin/env python3
"""
Quick database schema checker
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor

def check_schema():
    # Connect to database
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Check existing tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)

        tables = cursor.fetchall()
        print('📊 Existing tables:')
        for table in tables:
            print(f'  - {table["table_name"]}')

        # Check if users table exists and has id column
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            ORDER BY ordinal_position;
        """)

        user_columns = cursor.fetchall()
        if user_columns:
            print(f'\n👤 Users table structure:')
            for col in user_columns:
                print(f'  - {col["column_name"]}: {col["data_type"]}')
        else:
            print('\n⚠️ Users table not found')

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    check_schema()
