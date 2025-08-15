#!/usr/bin/env python3
"""
Simple migration executor for Railway
This will run the migration once Railway deployment is complete
"""

import os
import subprocess
import sys

def main():
    print("🚀 EXECUTING MIGRATION ON RAILWAY")
    print("=" * 50)
    
    # Verify we're on Railway
    if not os.getenv('DATABASE_URL'):
        print("❌ Not on Railway - DATABASE_URL not found")
        return False
    
    print("✅ Railway environment detected")
    print("🔄 Running comprehensive migration...")
    
    # Execute the migration
    try:
        # Use os.system for direct execution
        result = os.system('python comprehensive_migration.py')
        
        if result == 0:
            print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
            return True
        else:
            print(f"❌ MIGRATION FAILED - Exit code: {result}")
            return False
            
    except Exception as e:
        print(f"❌ MIGRATION ERROR: {e}")
        return False

if __name__ == "__main__":
    main()
