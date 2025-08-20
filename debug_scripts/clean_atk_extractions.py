#!/usr/bin/env python3
"""
Clean previous ATK extractions before running enhanced extraction
"""

import sys
import os

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_systems.database_manager import DatabaseManager

def clean_previous_extractions():
    """Clean up any previous ATK 25th extractions"""
    
    db = DatabaseManager()
    
    # Clean up any ATK 25th extractions to start fresh
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM recipes WHERE source LIKE %s", ('%ATK 25th%',))
        deleted = cursor.rowcount
        conn.commit()
        print(f'Cleaned {deleted} previous ATK 25th extractions')
        
        # Show current recipe count
        cursor.execute('SELECT COUNT(*) FROM recipes')
        total = cursor.fetchone()[0]
        print(f'Total recipes remaining: {total}')

if __name__ == "__main__":
    clean_previous_extractions()
