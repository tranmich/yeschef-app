#!/usr/bin/env python3
"""
Debug Admin Authentication
Test if admin email detection is working correctly
"""

import requests
import json

def debug_admin_auth():
    """Debug admin authentication and privileges"""
    base_url = "http://localhost:5000"
    
    print("🔍 DEBUGGING ADMIN AUTHENTICATION")
    print("="*50)
    
    # Test login with admin email
    print("\n1. Testing admin login...")
    
    login_data = {
        "email": "tran.mich@gmail.com",
        "password": "your_password_here"  # You'll need to provide the actual password
    }
    
    print("📝 Please manually test admin login in browser:")
    print("   1. Go to http://localhost:5000")
    print("   2. Login with tran.mich@gmail.com") 
    print("   3. Check browser developer console (F12)")
    print("   4. Look for admin detection logs")
    print("   5. Check Authorization header in network requests")
    
    print("\n2. Check server logs for admin detection:")
    print("   Look for these messages in terminal:")
    print("   🔧 Admin access detected - using unlimited search")
    print("   🔧 Admin requesting all recipes for curation")
    
    print("\n3. Manual debugging steps:")
    print("   • In browser console, check localStorage.getItem('authToken')")
    print("   • Verify email in JWT token payload")
    print("   • Check if admin mode toggle appears")
    
    return True

if __name__ == "__main__":
    debug_admin_auth()
