#!/usr/bin/env python3
"""
Inspect Current Database Schema
Quick utility to examine SQLite database structure before PostgreSQL migration
"""

import sqlite3
import sys
import os

def inspect_database():
    """Examine the current SQLite database structure"""
    db_path = 'hungie.db'

    if not os.path.exists(db_path):
        print(f"❌ Database file '{db_path}' not found!")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        print("📊 DATABASE SCHEMA ANALYSIS")
        print("=" * 50)
        print(f"Database: {db_path}")
        print(f"Total Tables: {len(tables)}")
        print()

        for table in tables:
            table_name = table[0]
            print(f"🔍 Table: {table_name}")

            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()

            print("   Columns:")
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, primary_key = col
                pk_indicator = " (PRIMARY KEY)" if primary_key else ""
                null_indicator = " NOT NULL" if not_null else ""
                default_indicator = f" DEFAULT {default_val}" if default_val else ""
                print(f"     - {col_name}: {col_type}{pk_indicator}{null_indicator}{default_indicator}")

            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            row_count = cursor.fetchone()[0]
            print(f"   Rows: {row_count}")
            print()

        conn.close()
        print("✅ Database inspection complete!")

    except Exception as e:
        print(f"❌ Error inspecting database: {e}")

if __name__ == "__main__":
    inspect_database()
