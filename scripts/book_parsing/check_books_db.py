#!/usr/bin/env python3

import sqlite3

def check_books():
    conn = sqlite3.connect('recipe_books.db')
    cursor = conn.cursor()
    
    try:
        # Check books table
        cursor.execute("SELECT id, title, filename FROM books")
        books = cursor.fetchall()
        print("Books in database:")
        for book_id, title, filename in books:
            cursor.execute("SELECT COUNT(*) FROM recipes WHERE book_id = ?", (book_id,))
            count = cursor.fetchone()[0]
            print(f"  Book {book_id}: {title} ({filename}) - {count} recipes")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_books()
