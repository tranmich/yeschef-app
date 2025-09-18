#!/usr/bin/env python3
"""
Create Friends Schema Migration
Safely adds Friends, Households, and Collaboration tables to existing PostgreSQL database
"""

import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_db_connection():
    """Get database connection using existing pattern"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise Exception("DATABASE_URL environment variable not found")
    
    try:
        # Try internal Railway URL first
        conn = psycopg2.connect(database_url, cursor_factory=psycopg2.extras.RealDictCursor)
        logger.info("✅ Connected to PostgreSQL database")
        return conn
    except Exception as e:
        logger.error(f"Failed to connect with internal URL: {e}")
        # Fallback to public URL pattern from your existing code
        public_url = database_url.replace("postgres.railway.internal:5432", "shuttle.proxy.rlwy.net:31331")
        try:
            conn = psycopg2.connect(public_url, cursor_factory=psycopg2.extras.RealDictCursor)
            logger.info("✅ Connected to PostgreSQL database (public URL)")
            return conn
        except Exception as e2:
            logger.error(f"Failed to connect with public URL: {e2}")
            raise

def run_friends_migration():
    """Run the friends schema migration"""
    
    # Load environment variables
    load_dotenv()
    
    try:
        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        logger.info("🚀 Starting Friends schema migration...")
        
        # Read and execute the migration SQL
        migration_file = os.path.join(os.path.dirname(__file__), 'create_friends_schema.sql')
        
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        # Execute the migration
        cursor.execute(migration_sql)
        conn.commit()
        
        logger.info("✅ Friends schema migration completed successfully!")
        
        # Verify tables were created
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('friendships', 'friend_requests', 'households', 'household_members', 'shares')
            ORDER BY table_name
        """)
        
        tables = [row['table_name'] for row in cursor.fetchall()]
        
        logger.info(f"📊 Created tables: {', '.join(tables)}")
        
        # Check indexes
        cursor.execute("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename IN ('friendships', 'friend_requests', 'households', 'household_members', 'shares')
            AND indexname LIKE 'idx_%'
            ORDER BY indexname
        """)
        
        indexes = [row['indexname'] for row in cursor.fetchall()]
        logger.info(f"🔍 Created indexes: {len(indexes)} total")
        
        # Check functions
        cursor.execute("""
            SELECT proname 
            FROM pg_proc 
            WHERE proname IN ('create_mutual_friendship', 'generate_household_invite_code')
        """)
        
        functions = [row['proname'] for row in cursor.fetchall()]
        logger.info(f"⚙️ Created functions: {', '.join(functions)}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    success = run_friends_migration()
    if success:
        print("\n🎉 Friends schema migration completed successfully!")
        print("✅ Database is ready for Friends functionality")
    else:
        print("\n❌ Migration failed. Check logs for details.")
        exit(1)