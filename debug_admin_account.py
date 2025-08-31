#!/usr/bin/env python3
"""
Check Admin Account Status
Verify if tran.mich@gmail.com exists and debug admin detection
"""

def debug_admin_account():
    """Check admin account and debug admin detection"""
    
    print("🔍 DEBUGGING ADMIN ACCOUNT STATUS")
    print("="*50)
    
    print("\n📋 QUICK DEBUG STEPS:")
    
    print("\n1. 🔍 CHECK IF ADMIN ACCOUNT EXISTS:")
    print("   • Go to the app login page")
    print("   • Try to login with: tran.mich@gmail.com")
    print("   • Does the account exist? Can you login?")
    
    print("\n2. 🔧 CHECK BROWSER CONSOLE LOGS:")
    print("   After logging in, open Developer Tools (F12) and look for:")
    print("   ✅ Expected: '🔧 ADMIN ACCESS DETECTED - User has admin privileges'")
    print("   ❌ Problem: 'admin_access: false' or no admin logs")
    
    print("\n3. 📊 CHECK API RESPONSE:")
    print("   In browser console, look for:")
    print("   📊 User recipes response: {admin_access: true, ...}")
    print("   If admin_access is false, admin button won't show")
    
    print("\n4. 🎯 POSSIBLE ISSUES:")
    print("   Issue A: Account doesn't exist → Need to create tran.mich@gmail.com")
    print("   Issue B: Account exists but admin detection fails → Backend issue")
    print("   Issue C: Admin detection works but button logic broken → Frontend issue")
    
    print("\n5. 💡 QUICK FIXES:")
    print("   Fix A: Register new account with tran.mich@gmail.com")
    print("   Fix B: Check server logs for admin detection")
    print("   Fix C: Add debug logging to frontend admin button logic")
    
    print("\n🎯 ACTION PLAN:")
    print("1. First, confirm you can login with tran.mich@gmail.com")
    print("2. Check browser console for admin detection logs")
    print("3. Report what you see in the console")
    print("4. I'll fix the specific issue based on your findings")
    
    return True

if __name__ == "__main__":
    debug_admin_account()
