"""
Base Repository Pattern
Provides common database operations for all repositories
"""

from typing import List, Dict, Any, Optional, Tuple
from contextlib import contextmanager
import logging

from app.database.connection import get_db_connection, return_db_connection, transaction

logger = logging.getLogger(__name__)


class BaseRepository:
    """
    Base class for all repositories
    Provides common CRUD operations and query helpers
    """
    
    def __init__(self, table_name: str):
        """
        Initialize repository
        
        Args:
            table_name: Name of the database table
        """
        self.table_name = table_name
    
    @contextmanager
    def _get_connection(self):
        """Get database connection (context manager)"""
        conn = get_db_connection()
        try:
            yield conn
        finally:
            return_db_connection(conn)
    
    @contextmanager
    def _transaction(self):
        """Get database transaction (context manager)"""
        with transaction() as conn:
            yield conn
    
    def _execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        Execute SELECT query and return all results
        
        Args:
            query: SQL query string
            params: Query parameters (tuple)
        
        Returns:
            List of dictionaries (rows)
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            return [dict(row) for row in results]
    
    def _execute_query_one(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """
        Execute SELECT query and return single result
        
        Args:
            query: SQL query string
            params: Query parameters (tuple)
        
        Returns:
            Dictionary (row) or None
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            return dict(result) if result else None
    
    def _execute_insert(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """
        Execute INSERT query and return inserted row
        
        Args:
            query: SQL INSERT query with RETURNING clause
            params: Query parameters (tuple)
        
        Returns:
            Dictionary (inserted row) or None
        """
        try:
            with self._transaction() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params or ())
                result = cursor.fetchone()
                if result:
                    # Convert RealDictRow to regular dict
                    return {key: value for key, value in result.items()}
                return None
        except Exception as e:
            logger.error(f"_execute_insert failed: {e}", exc_info=True)
            raise
    
    def _execute_update(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """
        Execute UPDATE query and return updated row
        
        Args:
            query: SQL UPDATE query with RETURNING clause
            params: Query parameters (tuple)
        
        Returns:
            Dictionary (updated row) or None
        """
        try:
            with self._transaction() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params or ())
                result = cursor.fetchone()
                if result:
                    # Convert RealDictRow to regular dict
                    return {key: value for key, value in result.items()}
                return None
        except Exception as e:
            logger.error(f"_execute_update failed: {e}", exc_info=True)
            raise
    
    def _execute_delete(self, query: str, params: tuple = None) -> int:
        """
        Execute DELETE query and return number of deleted rows
        
        Args:
            query: SQL DELETE query
            params: Query parameters (tuple)
        
        Returns:
            Number of rows deleted
        """
        with self._transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            return cursor.rowcount
    
    def _execute_ddl(self, query: str, params: tuple = None) -> bool:
        """
        Execute DDL query (CREATE TABLE, ALTER TABLE, etc.) that doesn't return rows
        
        Args:
            query: SQL DDL query
            params: Query parameters (tuple)
        
        Returns:
            True if successful
        """
        try:
            with self._transaction() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params or ())
                return True
        except Exception as e:
            logger.error(f"DDL execution failed: {e}")
            return False
    
    # Common CRUD operations (can be overridden)
    
    def find_by_id(self, id: int) -> Optional[Dict[str, Any]]:
        """
        Find record by ID
        
        Args:
            id: Record ID
        
        Returns:
            Dictionary (row) or None
        """
        query = f"SELECT * FROM {self.table_name} WHERE id = %s"
        return self._execute_query_one(query, (id,))
    
    def find_all(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Find all records with pagination
        
        Args:
            limit: Maximum number of records
            offset: Number of records to skip
        
        Returns:
            List of dictionaries (rows)
        """
        query = f"SELECT * FROM {self.table_name} LIMIT %s OFFSET %s"
        return self._execute_query(query, (limit, offset))
    
    def count(self) -> int:
        """
        Count total records in table
        
        Returns:
            Number of records
        """
        query = f"SELECT COUNT(*) as count FROM {self.table_name}"
        result = self._execute_query_one(query)
        return result['count'] if result else 0
    
    def delete_by_id(self, id: int) -> bool:
        """
        Delete record by ID
        
        Args:
            id: Record ID
        
        Returns:
            True if deleted, False if not found
        """
        query = f"DELETE FROM {self.table_name} WHERE id = %s"
        rows_deleted = self._execute_delete(query, (id,))
        return rows_deleted > 0
    
    def exists(self, id: int) -> bool:
        """
        Check if record exists by ID
        
        Args:
            id: Record ID
        
        Returns:
            True if exists, False otherwise
        """
        query = f"SELECT EXISTS(SELECT 1 FROM {self.table_name} WHERE id = %s) as exists"
        result = self._execute_query_one(query, (id,))
        return result['exists'] if result else False
    
    # Helper methods for building dynamic queries
    
    def _build_where_clause(self, conditions: Dict[str, Any]) -> Tuple[str, tuple]:
        """
        Build WHERE clause from conditions dictionary
        
        Args:
            conditions: Dictionary of column: value pairs
        
        Returns:
            Tuple of (where_clause, params)
        
        Example:
            conditions = {'user_id': 123, 'category': 'dinner'}
            Returns: ("WHERE user_id = %s AND category = %s", (123, 'dinner'))
        """
        if not conditions:
            return "", ()
        
        clauses = []
        params = []
        
        for column, value in conditions.items():
            if value is None:
                clauses.append(f"{column} IS NULL")
            else:
                clauses.append(f"{column} = %s")
                params.append(value)
        
        where_clause = "WHERE " + " AND ".join(clauses)
        return where_clause, tuple(params)
    
    def _build_insert_query(self, data: Dict[str, Any]) -> Tuple[str, tuple]:
        """
        Build INSERT query from data dictionary
        
        Args:
            data: Dictionary of column: value pairs
        
        Returns:
            Tuple of (query, params)
        """
        columns = list(data.keys())
        placeholders = ["%s"] * len(columns)
        
        query = f"""
            INSERT INTO {self.table_name} ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            RETURNING *
        """
        
        params = tuple(data.values())
        return query, params
    
    def _build_update_query(self, id: int, data: Dict[str, Any]) -> Tuple[str, tuple]:
        """
        Build UPDATE query from data dictionary
        
        Args:
            id: Record ID to update
            data: Dictionary of column: value pairs
        
        Returns:
            Tuple of (query, params)
        """
        set_clauses = [f"{column} = %s" for column in data.keys()]
        
        query = f"""
            UPDATE {self.table_name}
            SET {', '.join(set_clauses)}
            WHERE id = %s
            RETURNING *
        """
        
        params = tuple(list(data.values()) + [id])
        return query, params
    
    # Logging helpers
    
    def _log_query(self, operation: str, query: str, params: tuple = None):
        """Log query for debugging"""
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"{operation} | {query} | {params}")


if __name__ == '__main__':
    # Test BaseRepository
    print("Testing BaseRepository...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    from app.database.connection import init_database
    init_database()
    
    # Test with users table
    users_repo = BaseRepository('users')
    
    # Test count
    count = users_repo.count()
    print(f"\n✅ Count users: {count}")
    
    # Test find_all
    users = users_repo.find_all(limit=3)
    print(f"✅ Find all users (first 3): {len(users)} users")
    
    # Test find_by_id
    if users:
        user_id = users[0]['id']
        user = users_repo.find_by_id(user_id)
        print(f"✅ Find by ID: {user['name'] if user else 'Not found'}")
    
    # Test exists
    if users:
        exists = users_repo.exists(users[0]['id'])
        print(f"✅ Exists: {exists}")
    
    # Test build_where_clause
    where, params = users_repo._build_where_clause({'name': 'Test', 'email': 'test@example.com'})
    print(f"✅ Build WHERE clause: {where}")
    
    print("\n✅ All BaseRepository tests passed!")
