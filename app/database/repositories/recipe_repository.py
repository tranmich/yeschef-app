"""
Recipe Repository
Handles all database operations for recipes table
"""

from typing import Optional, Dict, Any, List
import json
import logging

from app.database.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class RecipeRepository(BaseRepository):
    """Repository for recipes table"""
    
    def __init__(self):
        super().__init__('recipes')
    
    # Find methods
    
    def find_by_user(self, user_id: int, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Find all recipes for a user
        
        Args:
            user_id: User ID
            limit: Maximum results
            offset: Offset for pagination
        
        Returns:
            List of recipe dictionaries
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        return self._execute_query(query, (user_id, limit, offset))
    
    def find_by_category(self, user_id: int, category: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Find recipes by category for a user
        
        Args:
            user_id: User ID
            category: Recipe category
            limit: Maximum results
        
        Returns:
            List of recipe dictionaries
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE user_id = %s AND category = %s
            ORDER BY created_at DESC
            LIMIT %s
        """
        return self._execute_query(query, (user_id, category, limit))
    
    def find_by_flavor_profile(self, user_id: int, flavor_profile: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Find recipes by flavor profile for a user
        
        Args:
            user_id: User ID
            flavor_profile: Flavor profile
            limit: Maximum results
        
        Returns:
            List of recipe dictionaries
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE user_id = %s AND flavor_profile = %s
            ORDER BY created_at DESC
            LIMIT %s
        """
        return self._execute_query(query, (user_id, flavor_profile, limit))
    
    def find_community_recipes(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Find community-shared recipes
        
        Args:
            limit: Maximum results
            offset: Offset for pagination
        
        Returns:
            List of recipe dictionaries
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE is_community_shared = TRUE
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        return self._execute_query(query, (limit, offset))
    
    def find_template_recipes(self) -> List[Dict[str, Any]]:
        """
        Find template recipes
        
        Returns:
            List of template recipe dictionaries
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE is_template = TRUE
            ORDER BY title
        """
        return self._execute_query(query)
    
    # Search methods
    
    def search(self, user_id: int, search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search recipes by title (case-insensitive)
        
        Args:
            user_id: User ID
            search_term: Search term
            limit: Maximum results
        
        Returns:
            List of recipe dictionaries
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE user_id = %s AND title ILIKE %s
            ORDER BY created_at DESC
            LIMIT %s
        """
        return self._execute_query(query, (user_id, f'%{search_term}%', limit))
    
    def search_all_fields(self, user_id: int, search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search recipes by title, category, or description (case-insensitive)
        
        Args:
            user_id: User ID
            search_term: Search term
            limit: Maximum results
        
        Returns:
            List of recipe dictionaries
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE user_id = %s 
              AND (
                  title ILIKE %s 
                  OR category ILIKE %s 
                  OR description ILIKE %s
              )
            ORDER BY created_at DESC
            LIMIT %s
        """
        search_pattern = f'%{search_term}%'
        return self._execute_query(query, (user_id, search_pattern, search_pattern, search_pattern, limit))
    
    # Create/Update methods
    
    def create(self, recipe_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create new recipe
        
        Args:
            recipe_data: Dictionary with recipe fields
        
        Returns:
            Created recipe dictionary or None
        """
        # Ensure required fields
        if 'user_id' not in recipe_data:
            raise ValueError("user_id is required")
        if 'title' not in recipe_data:
            raise ValueError("title is required")
        
        # Convert lists/dicts to JSON strings if needed
        if 'ingredients' in recipe_data and isinstance(recipe_data['ingredients'], list):
            recipe_data['ingredients'] = json.dumps(recipe_data['ingredients'])
        if 'instructions' in recipe_data and isinstance(recipe_data['instructions'], list):
            recipe_data['instructions'] = json.dumps(recipe_data['instructions'])
        
        query, params = self._build_insert_query(recipe_data)
        recipe = self._execute_insert(query, params)
        
        if recipe:
            logger.info(f"✅ Created recipe: {recipe['title']} (ID: {recipe['id']}) for user {recipe['user_id']}")
        
        return recipe
    
    def update(self, recipe_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update recipe
        
        Args:
            recipe_id: Recipe ID
            updates: Dictionary with fields to update
        
        Returns:
            Updated recipe dictionary or None
        """
        # Convert lists/dicts to JSON strings if needed
        if 'ingredients' in updates and isinstance(updates['ingredients'], list):
            updates['ingredients'] = json.dumps(updates['ingredients'])
        if 'instructions' in updates and isinstance(updates['instructions'], list):
            updates['instructions'] = json.dumps(updates['instructions'])
        
        query, params = self._build_update_query(recipe_id, updates)
        recipe = self._execute_update(query, params)
        
        if recipe:
            logger.info(f"✅ Updated recipe: {recipe['title']} (ID: {recipe['id']})")
        
        return recipe
    
    def share_to_community(self, recipe_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Share recipe to community
        
        Args:
            recipe_id: Recipe ID
            user_id: User ID (for authorization)
        
        Returns:
            Updated recipe dictionary or None
        """
        # Verify ownership
        recipe = self.find_by_id(recipe_id)
        if not recipe or recipe['user_id'] != user_id:
            raise ValueError("Recipe not found or unauthorized")
        
        return self.update(recipe_id, {'is_community_shared': True})
    
    def unshare_from_community(self, recipe_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Unshare recipe from community
        
        Args:
            recipe_id: Recipe ID
            user_id: User ID (for authorization)
        
        Returns:
            Updated recipe dictionary or None
        """
        # Verify ownership
        recipe = self.find_by_id(recipe_id)
        if not recipe or recipe['user_id'] != user_id:
            raise ValueError("Recipe not found or unauthorized")
        
        return self.update(recipe_id, {'is_community_shared': False})
    
    # Delete with authorization
    
    def delete(self, recipe_id: int, user_id: int) -> bool:
        """
        Delete recipe (with authorization check)
        
        Args:
            recipe_id: Recipe ID
            user_id: User ID (for authorization)
        
        Returns:
            True if deleted, False if not found or unauthorized
        """
        # Check if user is admin (user_id 11 is admin)
        is_admin = (user_id == 11)
        
        # Verify ownership (or admin bypass)
        recipe = self.find_by_id(recipe_id)
        if not recipe:
            raise ValueError("Recipe not found")
        
        # Non-admins can only delete their own recipes
        if not is_admin and recipe['user_id'] != user_id:
            raise ValueError("Unauthorized to delete this recipe")
        
        success = self.delete_by_id(recipe_id)
        
        if success:
            logger.info(f"✅ Deleted recipe ID: {recipe_id} by user {user_id}{' (admin)' if is_admin else ''}")
        
        return success
    
    # Statistics
    
    def count_by_user(self, user_id: int) -> int:
        """
        Count recipes for a user
        
        Args:
            user_id: User ID
        
        Returns:
            Number of recipes
        """
        query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE user_id = %s"
        result = self._execute_query_one(query, (user_id,))
        return result['count'] if result else 0
    
    def count_by_category(self, user_id: int, category: str) -> int:
        """
        Count recipes by category for a user
        
        Args:
            user_id: User ID
            category: Recipe category
        
        Returns:
            Number of recipes
        """
        query = f"""
            SELECT COUNT(*) as count FROM {self.table_name}
            WHERE user_id = %s AND category = %s
        """
        result = self._execute_query_one(query, (user_id, category))
        return result['count'] if result else 0
    
    def get_categories(self, user_id: int) -> List[str]:
        """
        Get all unique categories for a user
        
        Args:
            user_id: User ID
        
        Returns:
            List of category names
        """
        query = f"""
            SELECT DISTINCT category FROM {self.table_name}
            WHERE user_id = %s AND category IS NOT NULL
            ORDER BY category
        """
        results = self._execute_query(query, (user_id,))
        return [row['category'] for row in results]
    
    def get_flavor_profiles(self, user_id: int) -> List[str]:
        """
        Get all unique flavor profiles for a user
        
        Args:
            user_id: User ID
        
        Returns:
            List of flavor profiles
        """
        query = f"""
            SELECT DISTINCT flavor_profile FROM {self.table_name}
            WHERE user_id = %s AND flavor_profile IS NOT NULL
            ORDER BY flavor_profile
        """
        results = self._execute_query(query, (user_id,))
        return [row['flavor_profile'] for row in results]
    
    # Duplicate detection (for Phase 6 performance optimization)
    
    def find_recent_similar(self, user_id: int, title: str, within_minutes: int = 5) -> Optional[Dict[str, Any]]:
        """
        Find similar recipe created recently (for duplicate detection)
        
        Args:
            user_id: User ID
            title: Recipe title
            within_minutes: Time window in minutes
        
        Returns:
            Recipe dictionary if found, None otherwise
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE user_id = %s 
              AND LOWER(title) = LOWER(%s)
              AND created_at > NOW() - INTERVAL '%s minutes'
            ORDER BY created_at DESC
            LIMIT 1
        """
        return self._execute_query_one(query, (user_id, title.strip(), within_minutes))


# Global instance
_recipe_repository: Optional[RecipeRepository] = None


def get_recipe_repository() -> RecipeRepository:
    """Get global RecipeRepository instance"""
    global _recipe_repository
    if _recipe_repository is None:
        _recipe_repository = RecipeRepository()
    return _recipe_repository
