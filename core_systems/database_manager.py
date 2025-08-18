"""
Centralized Database Manager - POSTGRESQL ONLY
==============================================

This module ensures ALL components use PostgreSQL consistently.
NO SQLite connections allowed - eliminates local/production mismatches.

Usage in any component:
    from core_systems.database_manager import get_db_connection
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Your PostgreSQL queries here
"""

import os
import psycopg2
import psycopg2.extras
import logging
from typing import Optional
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Centralized PostgreSQL connection management"""
    
    def __init__(self):
        self.connection_url = None
        self._validate_environment()
    
    def _validate_environment(self):
        """Ensure PostgreSQL environment is properly configured"""
        
        # Primary: Public Railway URL (most reliable)
        public_url = "postgresql://postgres:udQLpljdqTYmESmntwzmwDcOlBVbqlJG@shuttle.proxy.rlwy.net:31331/railway"
        
        # Fallback: Environment DATABASE_URL
        env_url = os.getenv('DATABASE_URL')
        
        if env_url:
            logger.info("✅ DATABASE_URL found in environment")
            self.connection_url = env_url
        else:
            logger.info("⚠️ No DATABASE_URL in environment, using public Railway URL")
            self.connection_url = public_url
        
        # Validate it's PostgreSQL (not SQLite)
        if 'postgresql' not in self.connection_url:
            raise ValueError(f"❌ INVALID DATABASE: Only PostgreSQL allowed. Got: {self.connection_url[:20]}...")
        
        logger.info("🟢 Database Manager initialized - PostgreSQL ONLY")
    
    @contextmanager
    def get_connection(self):
        """Get PostgreSQL connection with proper cleanup"""
        conn = None
        try:
            # Use RealDictCursor for consistent dict-like row access
            conn = psycopg2.connect(
                self.connection_url,
                cursor_factory=psycopg2.extras.RealDictCursor
            )
            logger.debug("🔗 PostgreSQL connection established")
            yield conn
            
        except psycopg2.Error as e:
            logger.error(f"❌ PostgreSQL connection failed: {e}")
            if conn:
                conn.rollback()
            raise
            
        finally:
            if conn:
                conn.close()
                logger.debug("🔌 PostgreSQL connection closed")
    
    def test_connection(self):
        """Test PostgreSQL connection and return status"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT version();")
                result = cursor.fetchone()
                logger.info(f"✅ PostgreSQL connection successful: {result['version'][:50]}...")
                return True
        except Exception as e:
            logger.error(f"❌ PostgreSQL connection test failed: {e}")
            return False

# Global database manager instance
_db_manager = DatabaseManager()

def get_db_connection():
    """Get PostgreSQL connection - USE THIS EVERYWHERE"""
    return _db_manager.get_connection()

def test_database_connection():
    """Test PostgreSQL connection"""
    return _db_manager.test_connection()

def get_database_info():
    """Get database connection information"""
    return {
        'type': 'PostgreSQL',
        'url_prefix': _db_manager.connection_url[:30] + '...',
        'status': 'Ready'
    }

# Prevent SQLite usage
def prevent_sqlite_usage():
    """Raise error if SQLite is attempted"""
    raise RuntimeError(
        "❌ SQLite usage is PROHIBITED in this application.\n"
        "Use: from core_systems.database_manager import get_db_connection\n"
        "All database operations must use PostgreSQL."
    )

# Override sqlite3 module to prevent accidental usage
import sys
class SQLiteBlocker:
    def connect(self, *args, **kwargs):
        prevent_sqlite_usage()
    
    def __getattr__(self, name):
        prevent_sqlite_usage()

# Block SQLite imports (optional - can be enabled for strict enforcement)
# sys.modules['sqlite3'] = SQLiteBlocker()

if __name__ == "__main__":
    # Test the database connection
    print("🧪 Testing Database Manager...")
    
    info = get_database_info()
    print(f"Database Type: {info['type']}")
    print(f"Connection: {info['url_prefix']}")
    
    if test_database_connection():
        print("✅ Database Manager working correctly!")
    else:
        print("❌ Database Manager test failed!")
