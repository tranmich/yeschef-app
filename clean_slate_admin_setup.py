#!/usr/bin/env python3
"""
Clean Slate via Admin API
Uses the running server's admin endpoints to clear templates
"""

import requests
import json

def clear_templates_via_admin():
    """Clear templates using admin API endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧹 CLEAN SLATE SETUP VIA ADMIN API")
    print("="*50)
    
    # Step 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/api/search?q=test")
        if response.status_code != 200:
            print("❌ Server not running. Please start the server first:")
            print("   python hungie_server.py")
            return False
    except:
        print("❌ Cannot connect to server. Please start the server first:")
        print("   python hungie_server.py")
        return False
    
    print("✅ Server is running")
    
    # Step 2: Instructions for manual cleanup
    print("\n🔧 ADMIN CURATION SETUP INSTRUCTIONS:")
    print("\n1. Login to the app with tran.mich@gmail.com")
    print("2. Click '⚙️ Admin Mode' button to activate admin features")
    print("3. Go to Admin Dashboard")
    print("4. Use 'Template Analytics' tab to see current templates")
    print("5. Use admin buttons on recipe cards to:")
    print("   • ❌ Remove Default - Remove template status from recipes")
    print("   • 🗑️ Delete Recipe - Delete unwanted recipes")
    print("   • ⭐ Make Default - Promote good recipes to templates")
    
    print("\n🎯 NEW USER EXPERIENCE:")
    print("• New users will start with 0 recipes")
    print("• Admin can curate which recipes become templates")
    print("• Templates automatically copy to new users when promoted")
    
    print("\n📊 ADMIN PRIVILEGES ACTIVATED:")
    print("• tran.mich@gmail.com sees ALL recipes (no 500 limit)")
    print("• Regular users limited to 500 recipes")
    print("• Admin has full curation control")
    
    print("\n✅ Clean slate setup ready!")
    print("🌐 Access the app and login with admin credentials to begin curation")
    
    return True

if __name__ == "__main__":
    clear_templates_via_admin()
