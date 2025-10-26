# ✅ PHASE 0: PRE-FLIGHT CHECKLIST
## Your Starting Point - Complete This Before Any Code Changes

**Estimated Time:** 1-2 hours  
**Risk Level:** ZERO (just preparation)  
**Goal:** Create safety nets and documentation

---

## 📋 CHECKLIST

Copy this checklist and check off items as you complete them:

```
BACKUPS
[ ] Database backup created
[ ] Code backup created
[ ] Git commit with all current changes
[ ] Git tag created: "pre-refactoring-backup"

BRANCH SETUP
[ ] Created branch: refactor/shadow-implementation
[ ] Pushed branch to remote
[ ] Confirmed can switch back to master if needed

BASELINE DOCUMENTATION
[ ] API response baseline recorded (optional but helpful)
[ ] List of mobile endpoints documented
[ ] Current API behavior captured

TOOLS INSTALLED
[ ] SQLAlchemy installed
[ ] Alembic installed
[ ] pytest installed
[ ] Redis client installed
[ ] Other dependencies installed
[ ] requirements.txt updated

COMMUNICATION
[ ] 6 test users notified (optional)
[ ] Expectations set

VERIFICATION
[ ] Current app still works
[ ] Can access database
[ ] All services running normally
```

---

## 🔧 DETAILED STEPS

### Step 1: Backup Your Database (15 minutes)

**Why:** If anything goes wrong, you can restore everything

```powershell
# Open PowerShell in your project directory
cd "d:\Mik\Downloads\Me Hungie"

# Create backups directory
New-Item -ItemType Directory -Force -Path "backups"

# Get your database URL
# From .env file or Railway dashboard
$env:DATABASE_URL = "your-database-url-here"

# Create backup (you'll need pg_dump installed)
# If you don't have PostgreSQL tools installed locally, that's okay!
# We can use Railway's built-in backup instead

# Alternative: Note your Railway backup settings
# Railway automatically backs up your database
# Go to: Railway Dashboard → Your Project → PostgreSQL → Backups
# Verify automatic backups are enabled
```

**✅ Backup Verified When:**
- You have a .sql backup file, OR
- Railway automatic backups are enabled

---

### Step 2: Backup Your Code (5 minutes)

```powershell
cd "d:\Mik\Downloads\Me Hungie"

# Copy hungie_server.py
Copy-Item "hungie_server.py" "backups\hungie_server_backup_$(Get-Date -Format 'yyyyMMdd').py"

# Verify backup exists
Get-Item "backups\hungie_server_backup_*.py"
```

**✅ Backup Verified When:**
- You see the backup file in `backups/` folder

---

### Step 3: Git Safety Net (10 minutes)

```powershell
cd "d:\Mik\Downloads\Me Hungie"

# Check current status
git status

# Add all current changes
git add .

# Commit current state
git commit -m "Pre-refactoring backup - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"

# Create safety tag
git tag -a "pre-refactoring-backup" -m "State before shadow implementation refactoring"

# Push everything
git push origin master
git push origin --tags

# Verify tag exists
git tag -l "pre-*"
```

**✅ Git Safety Net Complete When:**
- You see "pre-refactoring-backup" tag in list
- Code is pushed to remote repository

**Rollback Command (if you ever need it):**
```powershell
git checkout pre-refactoring-backup
```

---

### Step 4: Create Refactoring Branch (5 minutes)

```powershell
cd "d:\Mik\Downloads\Me Hungie"

# Create and switch to new branch
git checkout -b refactor/shadow-implementation

# Verify you're on the new branch
git branch

# Push to remote
git push -u origin refactor/shadow-implementation
```

**✅ Branch Setup Complete When:**
- `git branch` shows `* refactor/shadow-implementation`
- Branch exists on GitHub/remote

**Why This Helps:**
- Master branch stays untouched
- Can switch back anytime: `git checkout master`
- Easy to compare changes: `git diff master refactor/shadow-implementation`

---

### Step 5: Document Current Endpoints (15 minutes)

Create a simple list of what your mobile app uses:

```powershell
cd "d:\Mik\Downloads\Me Hungie"
New-Item -ItemType Directory -Force -Path "docs\refactoring"
New-Item -ItemType File -Path "docs\refactoring\mobile_endpoints.md"
```

Copy this into `docs\refactoring\mobile_endpoints.md`:

```markdown
# Mobile App API Endpoints

## Authentication
- POST /api/auth/login
- POST /api/auth/google
- POST /api/auth/signup
- POST /api/auth/verify-token
- GET  /api/health

## Recipes
- GET    /api/recipes
- POST   /api/recipes
- GET    /api/recipes/:id
- PUT    /api/recipes/:id/edit
- DELETE /api/recipes/:id
- GET    /api/user/recipes
- POST   /api/search/recipes

## Profile
- GET  /api/profile
- PUT  /api/profile
- PUT  /api/profile/avatar
- GET  /api/profile/stats

## Meal Plans
- POST   /api/meal-plans
- GET    /api/meal-plans
- GET    /api/meal-plans/:id
- PUT    /api/meal-plans/:id
- DELETE /api/meal-plans/:id

## Grocery Lists
- POST   /api/grocery-lists
- GET    /api/grocery-lists
- GET    /api/grocery-lists/:id
- PUT    /api/grocery-lists/:id
- DELETE /api/grocery-lists/:id

## Friends & Social
- GET  /api/friends/list
- GET  /api/friends/requests
- POST /api/friends/request
- POST /api/friends/accept
- POST /api/friends/reject
- POST /api/friends/remove

## Households
- GET    /api/households
- POST   /api/households
- GET    /api/households/:id
- PUT    /api/households/:id
- DELETE /api/households/:id
- POST   /api/households/:id/invite
- POST   /api/households/:id/leave

## Recipe Sharing
- POST /api/recipes/:id/share
- GET  /api/shared-recipes

## Stats
- GET /api/database/stats
```

**✅ Documentation Complete When:**
- File exists with endpoint list
- You understand which endpoints are most important

---

### Step 6: Install Required Dependencies (20 minutes)

```powershell
cd "d:\Mik\Downloads\Me Hungie"

# Activate your virtual environment if you have one
# .\venv\Scripts\Activate.ps1

# Install new dependencies
pip install sqlalchemy==2.0.23
pip install alembic==1.13.0
pip install pytest==7.4.3
pip install pytest-cov==4.1.0
pip install flask-caching==2.1.0
pip install redis==5.0.1
pip install deepdiff==6.7.1

# Update requirements file
pip freeze > requirements-new.txt

# Compare with old requirements
Write-Host "New dependencies added!"
```

**✅ Dependencies Installed When:**
- All `pip install` commands succeed
- `requirements-new.txt` created

**Note:** Keep `requirements.txt` (old) and `requirements-new.txt` (new) separate for now. We'll merge them later.

---

### Step 7: Verify Current App Still Works (10 minutes)

```powershell
cd "d:\Mik\Downloads\Me Hungie"

# Start your server
python hungie_server.py
```

In another PowerShell window:

```powershell
# Test health endpoint
curl http://localhost:5000/api/health

# Expected response:
# {"status": "healthy", ...}
```

**In Your Mobile App:**
- Open YesChef app
- Try to log in
- Load recipes
- Create a test recipe
- Everything should work normally

**✅ Verification Complete When:**
- Server starts without errors
- Health endpoint responds
- Mobile app can connect and use features

---

### Step 8: Create Project Structure (5 minutes)

We'll just create the folders, not add any code yet:

```powershell
cd "d:\Mik\Downloads\Me Hungie"

# Create new folder structure
New-Item -ItemType Directory -Force -Path "app"
New-Item -ItemType Directory -Force -Path "app\models"
New-Item -ItemType Directory -Force -Path "app\services"
New-Item -ItemType Directory -Force -Path "app\api"
New-Item -ItemType Directory -Force -Path "app\api\v2"
New-Item -ItemType Directory -Force -Path "app\database"
New-Item -ItemType Directory -Force -Path "app\database\repositories"
New-Item -ItemType Directory -Force -Path "app\cache"
New-Item -ItemType Directory -Force -Path "app\middleware"
New-Item -ItemType Directory -Force -Path "app\utils"
New-Item -ItemType Directory -Force -Path "tests"
New-Item -ItemType Directory -Force -Path "tests\unit"
New-Item -ItemType Directory -Force -Path "tests\integration"
New-Item -ItemType Directory -Force -Path "tests\baseline"

# Create __init__.py files (so Python recognizes them as packages)
"" | Out-File -FilePath "app\__init__.py" -Encoding utf8
"" | Out-File -FilePath "app\models\__init__.py" -Encoding utf8
"" | Out-File -FilePath "app\services\__init__.py" -Encoding utf8
"" | Out-File -FilePath "app\api\__init__.py" -Encoding utf8
"" | Out-File -FilePath "app\api\v2\__init__.py" -Encoding utf8
"" | Out-File -FilePath "app\database\__init__.py" -Encoding utf8
"" | Out-File -FilePath "app\database\repositories\__init__.py" -Encoding utf8
"" | Out-File -FilePath "app\cache\__init__.py" -Encoding utf8
"" | Out-File -FilePath "app\middleware\__init__.py" -Encoding utf8
"" | Out-File -FilePath "app\utils\__init__.py" -Encoding utf8
"" | Out-File -FilePath "tests\__init__.py" -Encoding utf8
"" | Out-File -FilePath "tests\unit\__init__.py" -Encoding utf8
"" | Out-File -FilePath "tests\integration\__init__.py" -Encoding utf8

Write-Host "✅ Folder structure created!"
```

**Verify it worked:**

```powershell
# You should see all the folders
Get-ChildItem -Path "app" -Recurse -Directory | Select-Object FullName
```

**✅ Structure Created When:**
- All folders exist
- All `__init__.py` files created

---

### Step 9: Optional - Record API Baseline (20 minutes)

This is optional but recommended. It helps you verify v2 matches v1 exactly.

```powershell
cd "d:\Mik\Downloads\Me Hungie"
New-Item -ItemType File -Path "tests\baseline\record_responses.py"
```

Copy this code into `tests\baseline\record_responses.py`:

```python
"""
Record current API responses as baseline
Run this to capture how your API behaves NOW
We'll compare v2 responses against this
"""

import requests
import json
from datetime import datetime
import os

# Configuration
BASE_URL = "https://yeschefapp-production.up.railway.app"
# Or for local testing:
# BASE_URL = "http://localhost:5000"

# You'll need to get a real token by logging in
# We'll show you how to get this
TEST_TOKEN = os.getenv("TEST_TOKEN", "")

if not TEST_TOKEN:
    print("⚠️  No TEST_TOKEN found!")
    print("To get a token:")
    print("1. Open your mobile app")
    print("2. Log in")
    print("3. The token is stored in SecureStore")
    print("4. Or check Network tab in browser dev tools")
    print("")
    print("For now, we'll skip token-required endpoints")
    input("Press Enter to continue with non-auth endpoints...")

HEADERS = {
    "Content-Type": "application/json"
}

if TEST_TOKEN:
    HEADERS["Authorization"] = f"Bearer {TEST_TOKEN}"

def record_endpoint(method, endpoint, data=None, requires_auth=False):
    """Record an endpoint's response"""
    if requires_auth and not TEST_TOKEN:
        print(f"⏭️  Skipping {endpoint} (requires auth)")
        return
    
    print(f"📡 Recording: {method} {endpoint}")
    
    try:
        url = f"{BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, headers=HEADERS, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=HEADERS, json=data, timeout=10)
        
        result = {
            "endpoint": endpoint,
            "method": method,
            "status_code": response.status_code,
            "response": response.json() if response.ok else {"error": response.text},
            "timestamp": datetime.now().isoformat(),
            "success": response.ok
        }
        
        # Save to file
        safe_filename = endpoint.replace("/", "_").replace(":", "_")
        filename = f"{method}_{safe_filename}.json"
        filepath = os.path.join("tests", "baseline", filename)
        
        with open(filepath, "w") as f:
            json.dump(result, f, indent=2)
        
        status = "✅" if response.ok else "❌"
        print(f"  {status} Saved to {filename}")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    print("=" * 70)
    print("📝 RECORDING BASELINE API RESPONSES")
    print("=" * 70)
    print(f"Target: {BASE_URL}")
    print(f"Auth: {'✅ Token found' if TEST_TOKEN else '❌ No token (skipping auth endpoints)'}")
    print("")
    
    # Non-auth endpoints (anyone can call these)
    print("🌐 Testing public endpoints...")
    record_endpoint("GET", "/api/health", requires_auth=False)
    record_endpoint("GET", "/api/database/stats", requires_auth=False)
    
    # Auth-required endpoints
    if TEST_TOKEN:
        print("\n🔐 Testing authenticated endpoints...")
        record_endpoint("GET", "/api/profile", requires_auth=True)
        record_endpoint("GET", "/api/user/recipes", requires_auth=True)
        record_endpoint("GET", "/api/meal-plans", requires_auth=True)
        record_endpoint("GET", "/api/grocery-lists", requires_auth=True)
        record_endpoint("GET", "/api/friends/list", requires_auth=True)
    
    print("\n" + "=" * 70)
    print("✅ Baseline recording complete!")
    print(f"📁 Files saved to: tests/baseline/")
    print("")
    print("These will be used to verify v2 matches v1 exactly")
    print("=" * 70)
```

**Run it:**

```powershell
cd "d:\Mik\Downloads\Me Hungie"
python tests\baseline\record_responses.py
```

**✅ Baseline Recorded When:**
- Script runs without errors
- JSON files created in `tests\baseline\`
- You see "Baseline recording complete!"

---

### Step 10: Commit Your Pre-Flight Work (5 minutes)

```powershell
cd "d:\Mik\Downloads\Me Hungie"

# See what changed
git status

# Add all changes
git add .

# Commit
git commit -m "Phase 0 complete: Pre-flight checklist done

- Created backups
- Set up folder structure
- Installed dependencies
- Documented mobile endpoints
- Recorded API baseline (optional)

Ready for Phase 1!"

# Push to your refactoring branch
git push origin refactor/shadow-implementation
```

**✅ Pre-Flight Complete When:**
- All changes committed
- Branch pushed to remote
- You feel prepared!

---

## 🎉 CONGRATULATIONS!

You've completed Phase 0! Here's what you've accomplished:

✅ **Safety Nets in Place**
- Database backed up (or Railway auto-backup verified)
- Code backed up
- Git tag created for rollback
- Separate branch for refactoring

✅ **Documentation Created**
- Mobile endpoints documented
- Baseline responses recorded (optional)
- Project structure created

✅ **Tools Installed**
- All dependencies ready
- Testing framework available

✅ **Verification Done**
- Current app still works
- Nothing broke
- Mobile app still connects

---

## 🚀 YOU'RE READY FOR PHASE 1!

**Next Step:** Phase 1 - Foundation Setup (2-4 hours)

Phase 1 will create:
- App factory pattern (`app/__init__.py`)
- Configuration management (`app/config.py`)
- Database connection wrapper (`app/database/connection.py`)
- Basic tests (`tests/conftest.py`, `tests/test_basic.py`)

**Want to continue?** Let me know and I'll guide you through Phase 1 step by step!

---

## 🆘 TROUBLESHOOTING

### "pip install failed"
```powershell
# Try upgrading pip first
python -m pip install --upgrade pip

# Then retry
pip install sqlalchemy==2.0.23
```

### "Can't access database"
```powershell
# Check if DATABASE_URL is set
$env:DATABASE_URL

# If empty, check your .env file or Railway dashboard
```

### "Git commands not working"
```powershell
# Make sure you're in the right directory
cd "d:\Mik\Downloads\Me Hungie"

# Verify Git is installed
git --version
```

### "hungie_server.py won't start"
```powershell
# Check for Python errors in console
# Make sure all dependencies from requirements.txt are installed
pip install -r requirements.txt
```

---

## 📞 NEED HELP?

If you get stuck on any step:
1. Don't panic! Nothing is broken yet (we haven't changed code)
2. Note which step failed
3. Save any error messages
4. We can troubleshoot together

**You can rollback anytime:**
```powershell
git checkout master  # Back to original state
```

---

## ✅ FINAL CHECKLIST

Before moving to Phase 1, verify:

- [ ] I have backups of everything
- [ ] I'm on the refactoring branch
- [ ] All dependencies installed
- [ ] Current app still works
- [ ] Folder structure created
- [ ] I understand what we're doing
- [ ] I'm ready for Phase 1!

**Ready?** Let me know and we'll start Phase 1! 🚀

---

**Questions?** Ask anything! This is a learning journey, not a race. 💪
