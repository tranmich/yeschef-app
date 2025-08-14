#!/usr/bin/env python3

import sqlite3

def check_books_structure():
    conn = sqlite3.connect('recipe_books.db')
    cursor = conn.cursor()
    
    try:
        # Check books table structure
        cursor.execute("PRAGMA table_info(books)")
        columns = cursor.fetchall()
        print("Books table columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Check books content
        cursor.execute("SELECT * FROM books")
        books = cursor.fetchall()
        print(f"\nBooks in database ({len(books)} total):")
        for book in books:
            print(f"  {book}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_books_structure()
