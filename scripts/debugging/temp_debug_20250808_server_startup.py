#!/usr/bin/env python3
"""
Debugging script for hungie_server startup issues
Following our PROJECT_STRUCTURE_GUIDE.md - this is a temporary debug file
that should be deleted after debugging session.
"""

import sys
import os

def test_server_startup():
    """Test server startup with detailed error reporting"""
    try:
        print("🔍 Testing server startup...")
        
        # Add parent directory to path to find hungie_server.py
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
        
        # Test imports first
        print("📦 Testing imports...")
        import hungie_server
        print("✅ hungie_server imported successfully")
        
        # Test app creation
        print("🚀 Testing app creation...")
        app = hungie_server.app
        print(f"✅ App created: {app}")
        
        # Test database connection
        print("💾 Testing database connection...")
        import sqlite3
        conn = sqlite3.connect('hungie.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM recipes")
        count = cursor.fetchone()[0]
        print(f"✅ Database connected: {count} recipes found")
        conn.close()
        
        # Test routes
        print("🛣️ Testing routes...")
        print(f"✅ App routes: {[rule.rule for rule in app.url_map.iter_rules()]}")
        
        print("🎯 All tests passed! Server should start normally.")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    return True

if __name__ == "__main__":
    test_server_startup()
