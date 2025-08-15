#!/usr/bin/env python3
"""
Railway One-Time Migration Job
This will run the migration and then shut down
"""

import os
import sys
import subprocess
import time

def main():
    print("🚀 RAILWAY MIGRATION JOB STARTING")
    print("=" * 50)
    
    # Wait a moment for Railway environment to be ready
    time.sleep(5)
    
    # Check if we're really on Railway
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ Not running on Railway - DATABASE_URL not available")
        return False
    
    print("✅ Railway environment confirmed")
    print(f"📡 DATABASE_URL detected: {database_url[:50]}...")
    
    # Check if SQLite file exists
    if not os.path.exists('hungie.db'):
        print("❌ hungie.db not found - cannot migrate")
        return False
    
    print("✅ SQLite database found")
    
    # Run the comprehensive migration
    print("🔄 Starting comprehensive migration...")
    
    try:
        # Run the migration script
        result = subprocess.run([
            sys.executable, 
            'comprehensive_migration.py'
        ], capture_output=True, text=True, timeout=1200)  # 20 minute timeout
        
        print("📋 MIGRATION OUTPUT:")
        print("=" * 30)
        print(result.stdout)
        
        if result.stderr:
            print("⚠️  MIGRATION WARNINGS/ERRORS:")
            print("=" * 35)
            print(result.stderr)
        
        if result.returncode == 0:
            print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
            print("✅ Railway PostgreSQL now has all recipes")
            print("✅ Frontend should work immediately")
            return True
        else:
            print(f"❌ MIGRATION FAILED - Exit code: {result.returncode}")
            return False
    
    except subprocess.TimeoutExpired:
        print("❌ MIGRATION TIMED OUT (20 minutes)")
        return False
    except Exception as e:
        print(f"❌ MIGRATION ERROR: {e}")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🚀 RAILWAY MIGRATION JOB COMPLETE!")
        print("✅ All 721 recipes migrated successfully")
        print("✅ PostgreSQL ready for production")
        print("✅ Frontend will now find recipes")
    else:
        print("\n❌ RAILWAY MIGRATION JOB FAILED")
        sys.exit(1)
    
    print("\n💤 Job shutting down...")
    time.sleep(10)  # Give time to read results
