#!/usr/bin/env python3
"""
Simple server launcher for debugging
"""
from hungie_server import app
import logging

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    print("🚀 Starting Hungie Server with Authentication...")
    
    try:
        # Test the app first
        print("🧪 Testing authentication endpoint...")
        with app.test_client() as client:
            response = client.get('/api/auth/status')
            print(f"✅ Auth status: {response.status_code}")
        
        print("🚀 Starting server on http://localhost:5000")
        app.run(
            host="127.0.0.1",
            port=5000,
            debug=True  # Enable debug for better error messages
        )
    except Exception as e:
        print(f"❌ Server error: {e}")
        import traceback
        traceback.print_exc()
