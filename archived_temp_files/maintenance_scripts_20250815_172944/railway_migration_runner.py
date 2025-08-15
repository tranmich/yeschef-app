#!/usr/bin/env python3
"""
Railway Migration Runner
This script will be deployed to Railway and run the migration there
"""

import subprocess
import sys
import os

def run_migration():
    """Run the comprehensive migration script"""
    print("🚀 STARTING MIGRATION ON RAILWAY")
    print("=" * 50)
    
    # Verify we're on Railway
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ Not running on Railway - DATABASE_URL not found")
        return False
    
    print(f"✅ Running on Railway - DATABASE_URL detected")
    
    # Run the comprehensive migration
    try:
        result = subprocess.run([
            sys.executable, 'comprehensive_migration.py'
        ], capture_output=True, text=True, timeout=600)  # 10 minute timeout
        
        print("MIGRATION OUTPUT:")
        print(result.stdout)
        
        if result.stderr:
            print("MIGRATION ERRORS:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
            return True
        else:
            print(f"❌ MIGRATION FAILED - Exit code: {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ MIGRATION TIMED OUT (10 minutes)")
        return False
    except Exception as e:
        print(f"❌ MIGRATION ERROR: {e}")
        return False

if __name__ == "__main__":
    success = run_migration()
    if not success:
        sys.exit(1)
