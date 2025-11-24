"""
Whiteboard Schema Migration Script
===================================
Executes the whiteboard_schema_v1.sql migration

Usage:
    python run_whiteboard_migration.py

Author: GitHub Copilot
Date: November 3, 2025
"""

import psycopg2
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_file = Path(__file__).parent.parent / '.env'
if env_file.exists():
    load_dotenv(env_file)
    print(f"✅ Loaded environment from {env_file}")
else:
    print(f"⚠️  No .env file found at {env_file}")

def run_migration():
    """Execute whiteboard schema migration"""
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ ERROR: DATABASE_URL not found in environment")
        return False
    
    # Read SQL file
    sql_file = Path(__file__).parent / 'migrations' / 'whiteboard_schema_v1.sql'
    
    if not sql_file.exists():
        print(f"❌ ERROR: Migration file not found: {sql_file}")
        return False
    
    print(f"📄 Reading migration file: {sql_file}")
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    # Connect to database
    print(f"🔄 Connecting to PostgreSQL...")
    try:
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("✅ Connected to database")
        print("🚀 Executing migration...")
        
        # Execute the migration script
        cursor.execute(sql_script)
        
        print("\n" + "="*60)
        print("✅ MIGRATION SUCCESSFUL!")
        print("="*60)
        
        # Verify tables created
        print("\n📊 Verifying tables...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
              AND table_name LIKE 'whiteboard%'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print(f"\n✅ Created {len(tables)} tables:")
        for table in tables:
            print(f"   - {table[0]}")
        
        # Verify indexes
        print("\n🔍 Verifying indexes...")
        cursor.execute("""
            SELECT COUNT(DISTINCT indexname)
            FROM pg_indexes 
            WHERE schemaname = 'public' 
              AND tablename LIKE 'whiteboard%'
        """)
        index_count = cursor.fetchone()[0]
        print(f"✅ Created {index_count} indexes")
        
        # Verify triggers
        print("\n⚡ Verifying triggers...")
        cursor.execute("""
            SELECT COUNT(DISTINCT trigger_name)
            FROM information_schema.triggers
            WHERE trigger_schema = 'public'
              AND event_object_table LIKE 'whiteboard%'
        """)
        trigger_count = cursor.fetchone()[0]
        print(f"✅ Created {trigger_count} triggers")
        
        # Verify functions
        print("\n🔧 Verifying functions...")
        cursor.execute("""
            SELECT COUNT(*)
            FROM pg_proc p
            JOIN pg_namespace n ON p.pronamespace = n.oid
            WHERE n.nspname = 'public'
              AND p.proname LIKE '%whiteboard%'
        """)
        function_count = cursor.fetchone()[0]
        print(f"✅ Created {function_count} helper functions")
        
        print("\n" + "="*60)
        print("🎉 WHITEBOARD DATABASE SCHEMA READY!")
        print("="*60)
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR during migration: {str(e)}")
        return False

if __name__ == '__main__':
    print("="*60)
    print("WHITEBOARD SCHEMA MIGRATION")
    print("="*60)
    print()
    
    success = run_migration()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("   You can now use the whiteboard feature.")
    else:
        print("\n❌ Migration failed!")
        print("   Please check the error messages above.")
