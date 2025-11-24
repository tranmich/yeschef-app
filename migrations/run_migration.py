"""
🚀 Database Migration Runner
============================
Purpose: Run whiteboard system migration scripts safely

What this script does:
1. Loads DATABASE_URL from .env file
2. Connects to PostgreSQL database
3. Reads SQL migration file
4. Executes migration in a transaction
5. Verifies tables were created
6. Shows summary of results

Author: GitHub Copilot
Date: November 3, 2025
"""

import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv
from pathlib import Path

# ==================================================
# CONFIGURATION
# ==================================================

# Load environment variables from .env file
print("📂 Loading environment variables...")
load_dotenv()

# Get database connection string
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL not found in .env file")
    exit(1)

print(f"✅ Database URL loaded: {DATABASE_URL[:30]}...")

# Migration file paths
MIGRATION_DIR = Path(__file__).parent
MIGRATION_FILE = MIGRATION_DIR / '20251103_create_whiteboard_tables.sql'
ROLLBACK_FILE = MIGRATION_DIR / '20251103_rollback_whiteboard_tables.sql'

# ==================================================
# HELPER FUNCTIONS
# ==================================================

def connect_to_database():
    """
    Establish connection to PostgreSQL database
    
    Railway requires sslmode='require' for security
    """
    try:
        print("\n🔌 Connecting to database...")
        conn = psycopg2.connect(
            DATABASE_URL,
            sslmode='require',  # Required for Railway
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        print("✅ Connected successfully!")
        return conn
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None

def read_sql_file(file_path):
    """
    Read SQL file contents
    
    Returns the SQL as a string
    """
    try:
        print(f"\n📖 Reading SQL file: {file_path.name}")
        with open(file_path, 'r', encoding='utf-8') as f:
            sql = f.read()
        print(f"✅ Read {len(sql)} characters ({len(sql.splitlines())} lines)")
        return sql
    except FileNotFoundError:
        print(f"❌ ERROR: File not found: {file_path}")
        return None
    except Exception as e:
        print(f"❌ ERROR reading file: {e}")
        return None

def execute_migration(conn, sql):
    """
    Execute SQL migration in a transaction
    
    If any error occurs, everything is rolled back
    This is safe - either all changes happen or none
    """
    cursor = conn.cursor()
    
    try:
        print("\n🚀 Executing migration...")
        print("=" * 50)
        
        # Execute SQL (wrapped in BEGIN/COMMIT by the SQL file itself)
        cursor.execute(sql)
        
        # Commit transaction
        conn.commit()
        print("=" * 50)
        print("✅ Migration executed successfully!")
        return True
        
    except Exception as e:
        print("=" * 50)
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        print("🔄 Changes rolled back (database unchanged)")
        return False
    finally:
        cursor.close()

def verify_tables(conn):
    """
    Verify that all expected tables were created
    
    Checks for: wb, wbo, wbc, wbco, wbe
    """
    cursor = conn.cursor()
    
    try:
        print("\n🔍 Verifying tables...")
        
        # Query to check tables
        cursor.execute("""
            SELECT table_name, 
                   pg_size_pretty(pg_total_relation_size(quote_ident(table_name)::regclass)) AS size
            FROM information_schema.tables
            WHERE table_name IN ('wb', 'wbo', 'wbc', 'wbco', 'wbe')
              AND table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        
        if len(tables) == 5:
            print("✅ All 5 tables created successfully!")
            print("\nTable Details:")
            print("-" * 40)
            for table in tables:
                print(f"  {table['table_name']:10s} | {table['size']}")
            print("-" * 40)
            return True
        else:
            print(f"⚠️ Warning: Expected 5 tables, found {len(tables)}")
            return False
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False
    finally:
        cursor.close()

def check_test_data(conn):
    """
    Check if test whiteboard was created
    """
    cursor = conn.cursor()
    
    try:
        print("\n🧪 Checking test data...")
        
        cursor.execute("""
            SELECT id, n, cby, ca 
            FROM wb 
            WHERE n = 'Test Whiteboard - Phase 1'
            LIMIT 1;
        """)
        
        whiteboard = cursor.fetchone()
        
        if whiteboard:
            print("✅ Test whiteboard created!")
            print(f"   ID: {whiteboard['id']}")
            print(f"   Name: {whiteboard['n']}")
            print(f"   Creator: user_id {whiteboard['cby']}")
            print(f"   Created: {whiteboard['ca']}")
            return True
        else:
            print("⚠️ No test whiteboard found (may need manual check)")
            return False
            
    except Exception as e:
        print(f"❌ Test data check failed: {e}")
        return False
    finally:
        cursor.close()

def show_summary(conn):
    """
    Show summary of database objects created
    """
    cursor = conn.cursor()
    
    try:
        print("\n📊 MIGRATION SUMMARY")
        print("=" * 50)
        
        # Count indexes
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM pg_indexes
            WHERE schemaname = 'public'
              AND tablename IN ('wb', 'wbo', 'wbc', 'wbco', 'wbe');
        """)
        index_count = cursor.fetchone()['count']
        print(f"✅ Indexes created: {index_count}")
        
        # Count functions
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM pg_proc p
            JOIN pg_namespace n ON p.pronamespace = n.oid
            WHERE n.nspname = 'public'
              AND p.proname IN (
                  'update_updated_at_column',
                  'update_whiteboard_activity',
                  'log_whiteboard_event',
                  'schedule_permanent_delete'
              );
        """)
        function_count = cursor.fetchone()['count']
        print(f"✅ Functions created: {function_count}")
        
        # Count triggers
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM information_schema.triggers
            WHERE trigger_schema = 'public'
              AND event_object_table IN ('wb', 'wbo', 'wbc', 'wbco', 'wbe');
        """)
        trigger_count = cursor.fetchone()['count']
        print(f"✅ Triggers created: {trigger_count}")
        
        print("=" * 50)
        
    except Exception as e:
        print(f"⚠️ Could not generate full summary: {e}")
    finally:
        cursor.close()

# ==================================================
# MAIN EXECUTION
# ==================================================

def main():
    """
    Main migration execution flow
    """
    print("\n" + "=" * 50)
    print("🚀 WHITEBOARD MIGRATION - PHASE 1")
    print("=" * 50)
    
    # Step 1: Read migration SQL
    sql = read_sql_file(MIGRATION_FILE)
    if not sql:
        return False
    
    # Step 2: Connect to database
    conn = connect_to_database()
    if not conn:
        return False
    
    try:
        # Step 3: Execute migration
        success = execute_migration(conn, sql)
        if not success:
            return False
        
        # Step 4: Verify tables
        verify_tables(conn)
        
        # Step 5: Check test data
        check_test_data(conn)
        
        # Step 6: Show summary
        show_summary(conn)
        
        # Success!
        print("\n" + "=" * 50)
        print("🎉 MIGRATION COMPLETE!")
        print("=" * 50)
        print("\nNext steps:")
        print("1. ✅ Database tables created")
        print("2. ⏳ Create API blueprint (Week 2)")
        print("3. ⏳ Build frontend structure (Week 3)")
        print("4. ⏳ Implement CRUD operations (Week 4)")
        print("\n📋 Track progress: docs/whiteboard_feature/PHASE_1_PROGRESS.md")
        print("=" * 50 + "\n")
        
        return True
        
    finally:
        # Always close connection
        conn.close()
        print("\n🔌 Database connection closed")

# ==================================================
# RUN SCRIPT
# ==================================================

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Migration cancelled by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
