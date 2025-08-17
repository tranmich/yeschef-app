#!/usr/bin/env python3
"""
Check local SQLite database content to ensure no conflicts
"""
import sqlite3
import os

def check_local_sqlite():
    print("🔍 CHECKING LOCAL SQLITE DATABASES")
    print("=" * 40)
    
    sqlite_files = ['hungie.db', 'scripts/book_parsing/recipe_books.db']
    
    for db_file in sqlite_files:
        if os.path.exists(db_file):
            print(f"\n📁 Checking {db_file}:")
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # Check for recipes table
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='recipes'")
                has_recipes = cursor.fetchone()
                
                if has_recipes:
                    cursor.execute("SELECT COUNT(*) FROM recipes")
                    count = cursor.fetchone()[0]
                    print(f"   ⚠️  Contains {count} recipes in SQLite!")
                    
                    if count > 0:
                        cursor.execute("SELECT id, title FROM recipes LIMIT 5")
                        samples = cursor.fetchall()
                        print(f"   📝 Sample recipes:")
                        for recipe in samples:
                            print(f"      ID {recipe[0]}: {recipe[1][:50]}...")
                else:
                    print(f"   ✅ No recipes table found")
                
                conn.close()
                
            except Exception as e:
                print(f"   ❌ Error reading {db_file}: {e}")
        else:
            print(f"\n📁 {db_file}: File not found")

def check_app_database_usage():
    print(f"\n🔍 CHECKING APPLICATION DATABASE USAGE")
    print("=" * 40)
    
    # Look for any sqlite usage in the main server
    with open('hungie_server.py', 'r') as f:
        content = f.read()
        
    if 'sqlite' in content.lower():
        print("⚠️  Found SQLite references in hungie_server.py!")
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'sqlite' in line.lower():
                print(f"   Line {i+1}: {line.strip()}")
    else:
        print("✅ No SQLite references found in hungie_server.py")
    
    if 'hungie.db' in content:
        print("⚠️  Found hungie.db references in hungie_server.py!")
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'hungie.db' in line:
                print(f"   Line {i+1}: {line.strip()}")
    else:
        print("✅ No hungie.db references found in hungie_server.py")

if __name__ == "__main__":
    check_local_sqlite()
    check_app_database_usage()
