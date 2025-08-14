#!/usr/bin/env python3
"""
Server Testing Debug Script
Created: 2025-08-08
Purpose: Test server startup with detailed error handling
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

try:
    print("🔍 Testing server startup with detailed error handling...")
    
    # Import the app
    from hungie_server import app, logger
    
    print("✅ App imported successfully")
    
    # Try to start server with error handling
    print("🚀 Starting server with detailed error handling...")
    
    try:
        app.run(
            host="0.0.0.0",     # Listen on all interfaces
            port=8000,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except Exception as server_error:
        print(f"❌ Server startup failed: {server_error}")
        print(f"Error type: {type(server_error)}")
        
        # Try alternative port
        print("🔄 Trying alternative port 8001...")
        try:
            app.run(
                host="0.0.0.0",
                port=8001,
                debug=False,
                use_reloader=False,
                threaded=True
            )
        except Exception as alt_error:
            print(f"❌ Alternative port also failed: {alt_error}")
    
except Exception as e:
    print(f"❌ Import or initialization failed: {e}")
    import traceback
    traceback.print_exc()
