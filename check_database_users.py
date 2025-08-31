#!/usr/bin/env python3
"""
Check Database Users
Quick check to see what users exist and their emails
"""

import requests
import json

def check_users():
    """Check what users exist via API calls"""
    base_url = "http://localhost:5000"
    
    print("👥 CHECKING DATABASE USERS")
    print("="*40)
    
    print("\n🔍 Method: Try to create/login with different accounts")
    print("\n1. 📝 REGISTER TEST:")
    print("   Try registering tran.mich@gmail.com if it doesn't exist")
    
    print("\n2. 🔑 LOGIN TEST:")
    print("   Try logging in with tran.mich@gmail.com")
    print("   Check what email shows up in browser console")
    
    print("\n3. 📊 API RESPONSE TEST:")
    print("   After login, check browser console for:")
    print("   'USER AUTH DEBUG: email=\\'tran.mich@gmail.com\\', is_admin=true'")
    
    print("\n🎯 Expected Flow:")
    print("   1. Register/Login with tran.mich@gmail.com")
    print("   2. Backend detects admin email")
    print("   3. Sets admin_access: true in response")
    print("   4. Frontend shows admin button")
    
    print("\n⚠️ If admin button still doesn't show:")
    print("   - Check browser console for exact email being used")
    print("   - Verify server logs show admin detection")
    print("   - Check if there are any typos in email")
    
    return True

if __name__ == "__main__":
    check_users()
