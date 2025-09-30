#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('hungie.db')
cursor = conn.cursor()

# Check if users table exists and get its structure
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
if cursor.fetchone():
    print("Users table exists")
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    print("Users table columns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
else:
    print("Users table does not exist")

conn.close()