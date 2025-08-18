"""
⭐ FAVORITES MANAGER - Recipe Bookmarking System
===============================================

Purpose: Manage user favorite recipes for quick access
Created: August 11, 2025
Integration: Works with recipe database and meal planning

Features:
- Add/remove recipes from favorites
- List user favorites with metadata
- Integration with meal planning system
- Fast favorite status checking
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import logging

class FavoritesManager:
    """Manage user favorite recipes and bookmarks."""
    
    def __init__(self, db_path: str = 'hungie.db'):
        """Initialize favorites manager with database connection."""
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.init_database_tables()
    
    def init_database_tables(self):
        """Initialize required database tables for favorites."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # User favorites table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_favorites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recipe_id INTEGER NOT NULL,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT,
                    UNIQUE(recipe_id),
                    FOREIGN KEY (recipe_id) REFERENCES recipes(id)
                )
            ''')
            
            # Create index for better performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_favorites_recipe 
                ON user_favorites(recipe_id)
            ''')
            
            conn.commit()
            self.logger.info("Favorites database tables initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing favorites tables: {e}")
            raise
        finally:
            conn.close()
    
    def add_favorite(self, recipe_id: int, notes: str = '') -> bool:
        """
        Add a recipe to favorites.
        
        Args:
            recipe_id: ID of the recipe to add to favorites
            notes: Optional notes about why this recipe is favorited
            
        Returns:
            bool: True if added successfully, False if already exists
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if recipe exists
            cursor.execute('SELECT id FROM recipes WHERE id = ?', (recipe_id,))
            if not cursor.fetchone():
                self.logger.warning(f"Recipe ID {recipe_id} not found in database")
                return False
            
            # Try to add to favorites
            cursor.execute('''
                INSERT INTO user_favorites (recipe_id, notes)
                VALUES (?, ?)
            ''', (recipe_id, notes))
            
            conn.commit()
            self.logger.info(f"Added recipe ID {recipe_id} to favorites")
            return True
            
        except sqlite3.IntegrityError:
            # Already exists in favorites
            self.logger.info(f"Recipe ID {recipe_id} already in favorites")
            return False
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error adding recipe to favorites: {e}")
            raise
        finally:
            conn.close()
    
    def remove_favorite(self, recipe_id: int) -> bool:
        """
        Remove a recipe from favorites.
        
        Args:
            recipe_id: ID of the recipe to remove from favorites
            
        Returns:
            bool: True if removed successfully
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM user_favorites WHERE recipe_id = ?', (recipe_id,))
            
            if cursor.rowcount == 0:
                self.logger.info(f"Recipe ID {recipe_id} was not in favorites")
                return False
            
            conn.commit()
            self.logger.info(f"Removed recipe ID {recipe_id} from favorites")
            return True
            
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error removing recipe from favorites: {e}")
            raise
        finally:
            conn.close()
    
    def toggle_favorite(self, recipe_id: int, notes: str = '') -> Dict[str, Any]:
        """
        Toggle favorite status of a recipe.
        
        Args:
            recipe_id: ID of the recipe to toggle
            notes: Optional notes if adding to favorites
            
        Returns:
            Dict: Status information about the toggle operation
        """
        if self.is_favorite(recipe_id):
            success = self.remove_favorite(recipe_id)
            return {
                'success': success,
                'action': 'removed',
                'is_favorite': False,
                'recipe_id': recipe_id
            }
        else:
            success = self.add_favorite(recipe_id, notes)
            return {
                'success': success,
                'action': 'added',
                'is_favorite': True,
                'recipe_id': recipe_id
            }
    
    def is_favorite(self, recipe_id: int) -> bool:
        """
        Check if a recipe is in favorites.
        
        Args:
            recipe_id: ID of the recipe to check
            
        Returns:
            bool: True if recipe is in favorites
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'SELECT 1 FROM user_favorites WHERE recipe_id = ?', 
                (recipe_id,)
            )
            return cursor.fetchone() is not None
            
        except Exception as e:
            self.logger.error(f"Error checking favorite status: {e}")
            return False
        finally:
            conn.close()
    
    def get_favorites(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        Get list of favorite recipes with details.
        
        Args:
            limit: Maximum number of favorites to return
            offset: Number of favorites to skip (for pagination)
            
        Returns:
            List[Dict]: List of favorite recipes with details
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    f.recipe_id,
                    f.added_date,
                    f.notes,
                    r.title,
                    r.description,
                    r.hands_on_time,
                    r.total_time,
                    r.servings,
                    r.category,
                    r.url
                FROM user_favorites f
                JOIN recipes r ON f.recipe_id = r.id
                ORDER BY f.added_date DESC
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            
            rows = cursor.fetchall()
            
            favorites = []
            for row in rows:
                favorites.append({
                    'recipe_id': row[0],
                    'added_date': row[1],
                    'notes': row[2],
                    'title': row[3],
                    'description': row[4],
                    'hands_on_time': row[5],
                    'total_time': row[6],
                    'servings': row[7],
                    'category': row[8],
                    'url': row[9],
                    'is_favorite': True  # Always true for this list
                })
            
            return favorites
            
        except Exception as e:
            self.logger.error(f"Error getting favorites: {e}")
            return []
        finally:
            conn.close()
    
    def get_favorites_count(self) -> int:
        """
        Get total count of favorite recipes.
        
        Returns:
            int: Total number of favorite recipes
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT COUNT(*) FROM user_favorites')
            count = cursor.fetchone()[0]
            return count
            
        except Exception as e:
            self.logger.error(f"Error getting favorites count: {e}")
            return 0
        finally:
            conn.close()
    
    def get_favorite_recipe_ids(self) -> List[int]:
        """
        Get list of all favorite recipe IDs.
        
        Returns:
            List[int]: List of favorite recipe IDs
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT recipe_id FROM user_favorites ORDER BY added_date DESC')
            rows = cursor.fetchall()
            return [row[0] for row in rows]
            
        except Exception as e:
            self.logger.error(f"Error getting favorite recipe IDs: {e}")
            return []
        finally:
            conn.close()
    
    def update_favorite_notes(self, recipe_id: int, notes: str) -> bool:
        """
        Update notes for a favorite recipe.
        
        Args:
            recipe_id: ID of the recipe
            notes: New notes for the favorite
            
        Returns:
            bool: True if updated successfully
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE user_favorites 
                SET notes = ?
                WHERE recipe_id = ?
            ''', (notes, recipe_id))
            
            if cursor.rowcount == 0:
                self.logger.warning(f"Recipe ID {recipe_id} not found in favorites")
                return False
            
            conn.commit()
            self.logger.info(f"Updated notes for favorite recipe ID {recipe_id}")
            return True
            
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error updating favorite notes: {e}")
            raise
        finally:
            conn.close()
    
    def clear_all_favorites(self) -> int:
        """
        Clear all favorites (use with caution).
        
        Returns:
            int: Number of favorites removed
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM user_favorites')
            removed_count = cursor.rowcount
            
            conn.commit()
            self.logger.info(f"Cleared all favorites ({removed_count} recipes)")
            return removed_count
            
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error clearing favorites: {e}")
            raise
        finally:
            conn.close()
    
    def get_favorites_summary(self) -> Dict[str, Any]:
        """
        Get summary information about favorites.
        
        Returns:
            Dict: Summary of favorites data
        """
        try:
            total_count = self.get_favorites_count()
            
            # Get recent favorites
            recent_favorites = self.get_favorites(limit=5)
            
            # Get favorite recipe types (if category data available)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT c.name, COUNT(*) as count
                FROM user_favorites f
                JOIN recipe_categories rc ON f.recipe_id = rc.recipe_id
                JOIN categories c ON rc.category_id = c.id
                GROUP BY c.name
                ORDER BY count DESC
                LIMIT 5
            ''')
            
            category_counts = [{'category': row[0], 'count': row[1]} for row in cursor.fetchall()]
            conn.close()
            
            return {
                'total_favorites': total_count,
                'recent_favorites': recent_favorites,
                'popular_categories': category_counts,
                'has_favorites': total_count > 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting favorites summary: {e}")
            return {
                'total_favorites': 0,
                'recent_favorites': [],
                'popular_categories': [],
                'has_favorites': False
            }
    
    def bulk_check_favorites(self, recipe_ids: List[int]) -> Dict[int, bool]:
        """
        Check favorite status for multiple recipes efficiently.
        
        Args:
            recipe_ids: List of recipe IDs to check
            
        Returns:
            Dict[int, bool]: Mapping of recipe_id to favorite status
        """
        if not recipe_ids:
            return {}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Create placeholders for IN clause
            placeholders = ','.join(['?' for _ in recipe_ids])
            cursor.execute(
                f'SELECT recipe_id FROM user_favorites WHERE recipe_id IN ({placeholders})',
                recipe_ids
            )
            
            favorite_ids = set(row[0] for row in cursor.fetchall())
            
            # Create result mapping
            return {recipe_id: recipe_id in favorite_ids for recipe_id in recipe_ids}
            
        except Exception as e:
            self.logger.error(f"Error bulk checking favorites: {e}")
            return {recipe_id: False for recipe_id in recipe_ids}
        finally:
            conn.close()


# Convenience function for quick access
def get_favorites_manager(db_path: str = 'hungie.db') -> FavoritesManager:
    """Get initialized favorites manager instance."""
    return FavoritesManager(db_path)


if __name__ == "__main__":
    # Test the favorites manager
    import sys
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Initialize manager
        favorites_manager = FavoritesManager()
        
        # Test adding favorites
        test_recipe_ids = [1, 2, 3]  # Replace with actual recipe IDs
        
        for recipe_id in test_recipe_ids:
            result = favorites_manager.toggle_favorite(recipe_id, f"Test note for recipe {recipe_id}")
            print(f"✅ Recipe {recipe_id}: {result['action']} ({'favorite' if result['is_favorite'] else 'not favorite'})")
        
        # Get favorites count
        count = favorites_manager.get_favorites_count()
        print(f"✅ Total favorites: {count}")
        
        # Get favorites list
        favorites = favorites_manager.get_favorites(limit=5)
        print(f"✅ Retrieved {len(favorites)} favorite recipes")
        
        # Get summary
        summary = favorites_manager.get_favorites_summary()
        print(f"✅ Favorites summary: {summary['total_favorites']} total")
        
        print("✅ Favorites manager test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing favorites manager: {e}")
        sys.exit(1)
