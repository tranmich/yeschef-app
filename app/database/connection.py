"""
Database connection management
Wraps the existing database connection logic from hungie_server.py
Provides connection pooling and better error handling
"""

import os
import psycopg2
import psycopg2.extras
from psycopg2 import pool
from contextlib import contextmanager
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages database connections with connection pooling
    Wraps the existing get_db_connection() logic
    """
    
    def __init__(self, database_url: str = None, min_connections: int = 1, max_connections: int = 20):
        """
        Initialize database manager with connection pooling
        
        Args:
            database_url: PostgreSQL connection URL
            min_connections: Minimum connections in pool
            max_connections: Maximum connections in pool
        """
        self.database_url = database_url or os.getenv('DATABASE_URL')
        
        if not self.database_url:
            raise ValueError("DATABASE_URL is required")
        
        logger.info("🔄 Initializing database connection pool...")
        logger.info(f"   Min connections: {min_connections}")
        logger.info(f"   Max connections: {max_connections}")
        
        try:
            # Create connection pool
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                min_connections,
                max_connections,
                self.database_url,
                cursor_factory=psycopg2.extras.RealDictCursor
            )
            
            # Test connection
            test_conn = self.connection_pool.getconn()
            test_conn.close()
            self.connection_pool.putconn(test_conn)
            
            logger.info("✅ Database connection pool initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize database pool: {e}")
            raise
    
    def get_connection(self):
        """
        Get a connection from the pool
        Compatible with existing get_db_connection() calls
        
        Returns:
            Database connection with RealDictCursor
        """
        try:
            conn = self.connection_pool.getconn()
            if conn:
                return conn
            else:
                raise Exception("Unable to get connection from pool")
        except Exception as e:
            logger.error(f"❌ Error getting connection: {e}")
            raise
    
    def return_connection(self, conn):
        """
        Return connection to the pool
        
        Args:
            conn: Database connection to return
        """
        if conn:
            self.connection_pool.putconn(conn)
    
    @contextmanager
    def get_connection_context(self):
        """
        Context manager for database connections
        Automatically returns connection to pool
        
        Usage:
            with db_manager.get_connection_context() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users")
                results = cursor.fetchall()
        """
        conn = None
        try:
            conn = self.get_connection()
            yield conn
        finally:
            if conn:
                self.return_connection(conn)
    
    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions
        Automatically commits on success, rolls back on error
        
        Usage:
            with db_manager.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users ...")
                # Automatically commits if no error
        """
        conn = None
        try:
            conn = self.get_connection()
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"❌ Transaction failed, rolled back: {e}")
            raise
        finally:
            if conn:
                self.return_connection(conn)
    
    def close_all_connections(self):
        """Close all connections in the pool"""
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("✅ All database connections closed")


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def init_database(database_url: str = None, min_connections: int = 1, max_connections: int = 20):
    """
    Initialize the global database manager
    Call this once at application startup
    
    Args:
        database_url: PostgreSQL connection URL
        min_connections: Minimum connections in pool
        max_connections: Maximum connections in pool
    """
    global _db_manager
    _db_manager = DatabaseManager(database_url, min_connections, max_connections)
    return _db_manager


def get_db_connection():
    """
    Get database connection - COMPATIBLE WITH EXISTING CODE
    This function matches the signature of get_db_connection() in hungie_server.py
    
    Returns:
        Database connection with RealDictCursor
    """
    if _db_manager is None:
        # Fallback: create connection directly (for backward compatibility)
        logger.warning("⚠️ Database manager not initialized, creating direct connection")
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL is required")
        
        conn = psycopg2.connect(
            database_url,
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        return conn
    
    return _db_manager.get_connection()


def return_db_connection(conn):
    """
    Return database connection to pool
    
    Args:
        conn: Database connection to return
    """
    if _db_manager:
        _db_manager.return_connection(conn)
    else:
        # Fallback: close connection directly
        if conn:
            conn.close()


@contextmanager
def get_db_context():
    """
    Context manager for database connections
    Automatically returns connection to pool
    
    Usage:
        with get_db_context() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()
    """
    if _db_manager:
        with _db_manager.get_connection_context() as conn:
            yield conn
    else:
        # Fallback: create and close connection
        conn = get_db_connection()
        try:
            yield conn
        finally:
            return_db_connection(conn)


@contextmanager
def transaction():
    """
    Context manager for database transactions
    Automatically commits on success, rolls back on error
    
    Usage:
        with transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users ...")
            # Automatically commits if no error
    """
    if _db_manager:
        with _db_manager.transaction() as conn:
            yield conn
    else:
        # Fallback: manual transaction
        conn = get_db_connection()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Transaction failed: {e}")
            raise
        finally:
            return_db_connection(conn)


if __name__ == '__main__':
    # Test database connection
    print("Testing database connection...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    # Initialize database manager
    db_manager = init_database()
    
    # Test 1: Get connection
    print("\nTest 1: Get connection from pool")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 as test")
    result = cursor.fetchone()
    print(f"  Query result: {result}")
    return_db_connection(conn)
    print("  ✅ Connection returned to pool")
    
    # Test 2: Context manager
    print("\nTest 2: Context manager")
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM users")
        result = cursor.fetchone()
        print(f"  User count: {result['count']}")
    print("  ✅ Connection automatically returned")
    
    # Test 3: Transaction
    print("\nTest 3: Transaction (read-only test)")
    with transaction() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        print(f"  Transaction result: {result}")
    print("  ✅ Transaction completed")
    
    # Cleanup
    db_manager.close_all_connections()
    print("\n✅ All tests passed!")
