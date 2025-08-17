#!/usr/bin/env python3
"""Check how many chicken recipes exist in the database"""

import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Get database connection"""
    if os.getenv('DATABASE_URL'):
        return psycopg2.connect(
            os.getenv('DATABASE_URL'),
            cursor_factory=psycopg2.extras.DictCursor
        )
    else:
        return psycopg2.connect(
            host='localhost',
            database='hungie',
            user='postgres',
            password='password',
            cursor_factory=psycopg2.extras.DictCursor
        )

def count_chicken_recipes():
    """Count how many recipes match 'chicken'"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Count total recipes
        cursor.execute("SELECT COUNT(*) FROM recipes")
        total_recipes = cursor.fetchone()[0]

        # Count chicken recipes using the same logic as the search
        search_sql = """
        SELECT COUNT(DISTINCT r.id)
        FROM recipes r
        LEFT JOIN ingredients i ON r.id = i.recipe_id  
        WHERE (LOWER(r.title) LIKE %s OR LOWER(r.description) LIKE %s OR LOWER(i.name) LIKE %s)
        """

        query = "chicken"
        params = [f"%{query}%", f"%{query}%", f"%{query}%"]
        cursor.execute(search_sql, params)
        chicken_count = cursor.fetchone()[0]

        print(f"📊 Total recipes in database: {total_recipes}")
        print(f"🐔 Recipes matching 'chicken': {chicken_count}")

        # Get some sample titles
        cursor.execute("""
        SELECT DISTINCT r.title
        FROM recipes r
        LEFT JOIN ingredients i ON r.id = i.recipe_id  
        WHERE (LOWER(r.title) LIKE %s OR LOWER(r.description) LIKE %s OR LOWER(i.name) LIKE %s)
        ORDER BY r.title
        LIMIT 30
        """, params)

        sample_titles = cursor.fetchall()
        print(f"\n📝 Sample chicken recipe titles:")
        for title in sample_titles:
            print(f"  - {title[0]}")

        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    count_chicken_recipes()
