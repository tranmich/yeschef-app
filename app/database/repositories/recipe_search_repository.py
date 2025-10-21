"""
Recipe Import & Search Repository
Handles database operations for recipe importing, searching, and recommendations
"""

from typing import Optional, Dict, Any, List
import logging

from app.database.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class RecipeSearchRepository(BaseRepository):
    """Repository for advanced recipe search and import operations"""
    
    def __init__(self):
        super().__init__('recipes')
    
    # ============================================================================
    # ADVANCED SEARCH
    # ============================================================================
    
    def search_recipes(
        self,
        user_id: int,
        query: str = None,
        category: str = None,
        prep_time_max: int = None,
        cook_time_max: int = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Advanced recipe search with filters
        
        Args:
            user_id: User ID (for personalization)
            query: Search term
            category: Recipe category filter
            prep_time_max: Max prep time in minutes
            cook_time_max: Max cook time in minutes
            limit: Maximum results
            offset: Pagination offset
        
        Returns:
            List of matching recipes
        """
        try:
            conditions = ["user_id = %s"]
            params = [user_id]
            
            if query:
                conditions.append("(title ILIKE %s OR description ILIKE %s)")
                params.extend([f'%{query}%', f'%{query}%'])
            
            if category:
                conditions.append("category = %s")
                params.append(category)
            
            if prep_time_max:
                conditions.append("CAST(NULLIF(regexp_replace(prep_time, '[^0-9]', '', 'g'), '') AS INTEGER) <= %s")
                params.append(prep_time_max)
            
            if cook_time_max:
                conditions.append("CAST(NULLIF(regexp_replace(cook_time, '[^0-9]', '', 'g'), '') AS INTEGER) <= %s")
                params.append(cook_time_max)
            
            where_clause = " AND ".join(conditions)
            params.extend([limit, offset])
            
            query_sql = f"""
                SELECT *
                FROM recipes
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            
            recipes = self._execute_query(query_sql, tuple(params))
            
            logger.info(f"✅ Found {len(recipes)} recipes matching search")
            
            return recipes
            
        except Exception as e:
            logger.error(f"❌ Error searching recipes: {e}", exc_info=True)
            return []
    
    def get_recipe_recommendations(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recipe recommendations based on user's favorites and history
        
        Args:
            user_id: User ID
            limit: Maximum results
        
        Returns:
            List of recommended recipes
        """
        try:
            # Get recipes from community that match user's favorite categories
            query = """
                SELECT DISTINCT r.*
                FROM recipes r
                JOIN recipe_shares rs ON r.id = rs.recipe_id
                WHERE rs.is_shared = TRUE
                AND r.user_id != %s
                AND r.category IN (
                    SELECT DISTINCT r2.category
                    FROM favorites f
                    JOIN recipes r2 ON f.recipe_id = r2.id
                    WHERE f.user_id = %s
                    LIMIT 3
                )
                ORDER BY RANDOM()
                LIMIT %s
            """
            
            recipes = self._execute_query(query, (user_id, user_id, limit))
            
            logger.info(f"✅ Got {len(recipes)} recommendations for user {user_id}")
            
            return recipes
            
        except Exception as e:
            logger.error(f"❌ Error getting recommendations: {e}", exc_info=True)
            return []
    
    def search_by_ingredients(
        self,
        user_id: int,
        ingredients: List[str],
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search recipes by available ingredients
        
        Args:
            user_id: User ID
            ingredients: List of ingredient names
            limit: Maximum results
        
        Returns:
            List of recipes that use these ingredients
        """
        try:
            # Build a search pattern for each ingredient
            ingredient_conditions = []
            params = []
            
            for ingredient in ingredients:
                ingredient_conditions.append("ingredients::text ILIKE %s")
                params.append(f'%{ingredient}%')
            
            params.extend([user_id, limit])
            
            where_clause = " OR ".join(ingredient_conditions) if ingredient_conditions else "TRUE"
            
            query = f"""
                SELECT *
                FROM recipes
                WHERE ({where_clause})
                AND user_id = %s
                ORDER BY created_at DESC
                LIMIT %s
            """
            
            recipes = self._execute_query(query, tuple(params))
            
            logger.info(f"✅ Found {len(recipes)} recipes with matching ingredients")
            
            return recipes
            
        except Exception as e:
            logger.error(f"❌ Error searching by ingredients: {e}", exc_info=True)
            return []
    
    def get_popular_recipes(
        self,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get most popular community recipes (by likes and claims)
        
        Args:
            limit: Maximum results
        
        Returns:
            List of popular recipes
        """
        try:
            query = """
                SELECT 
                    r.*,
                    COUNT(DISTINCT cl.id) as like_count,
                    COUNT(DISTINCT rs.id) as share_count
                FROM recipes r
                LEFT JOIN community_likes cl ON r.id = cl.recipe_id
                LEFT JOIN recipe_shares rs ON r.id = rs.recipe_id AND rs.is_shared = TRUE
                WHERE rs.is_shared = TRUE
                GROUP BY r.id
                ORDER BY like_count DESC, share_count DESC
                LIMIT %s
            """
            
            recipes = self._execute_query(query, (limit,))
            
            logger.info(f"✅ Got {len(recipes)} popular recipes")
            
            return recipes
            
        except Exception as e:
            logger.error(f"❌ Error getting popular recipes: {e}", exc_info=True)
            return []
    
    def get_recent_recipes(
        self,
        user_id: int,
        days: int = 7,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get user's recent recipes
        
        Args:
            user_id: User ID
            days: Number of days to look back
            limit: Maximum results
        
        Returns:
            List of recent recipes
        """
        try:
            query = """
                SELECT *
                FROM recipes
                WHERE user_id = %s
                AND created_at >= NOW() - INTERVAL '%s days'
                ORDER BY created_at DESC
                LIMIT %s
            """
            
            recipes = self._execute_query(query, (user_id, days, limit))
            
            logger.info(f"✅ Got {len(recipes)} recent recipes")
            
            return recipes
            
        except Exception as e:
            logger.error(f"❌ Error getting recent recipes: {e}", exc_info=True)
            return []
    
    # ============================================================================
    # IMPORT TRACKING
    # ============================================================================
    
    def log_import(
        self,
        user_id: int,
        source_url: str,
        recipe_id: int = None,
        status: str = 'success',
        error_message: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Log a recipe import attempt
        
        Args:
            user_id: User ID
            source_url: URL of imported recipe
            recipe_id: Created recipe ID (if successful)
            status: Import status (success/failed)
            error_message: Error message if failed
        
        Returns:
            Import log record
        """
        try:
            query = """
                INSERT INTO recipe_imports 
                (user_id, source_url, recipe_id, status, error_message, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
                RETURNING *
            """
            
            params = (user_id, source_url, recipe_id, status, error_message)
            
            log = self._execute_insert(query, params)
            
            if log:
                logger.info(f"✅ Logged import from {source_url}")
            
            return log
            
        except Exception as e:
            logger.error(f"❌ Error logging import: {e}", exc_info=True)
            return None
    
    def get_import_history(
        self,
        user_id: int,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get user's import history
        
        Args:
            user_id: User ID
            limit: Maximum results
        
        Returns:
            List of import records
        """
        try:
            query = """
                SELECT *
                FROM recipe_imports
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s
            """
            
            imports = self._execute_query(query, (user_id, limit))
            
            logger.info(f"✅ Got {len(imports)} import records")
            
            return imports
            
        except Exception as e:
            logger.error(f"❌ Error getting import history: {e}", exc_info=True)
            return []
