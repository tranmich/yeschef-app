#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('hungie.db')
cursor = conn.cursor()

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables in database:")
for table in tables:
    print(f"- {table[0]}")

# Check if we have data
for table_name in [t[0] for t in tables]:
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"{table_name}: {count} records")

conn.close()
