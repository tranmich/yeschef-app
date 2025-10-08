# 🧹 PROJECT CLEANUP PLAN
**Date:** October 8, 2025  
**Goal:** Organize main folder, improve security, and prepare for mobile release

---

## **📋 MAIN FOLDER FILE AUDIT**

### **✅ KEEP (Production Core Files)**
These files are essential and stay in root:

**Server & Core Systems:**
- `hungie_server.py` - Main Flask server (6,560 lines - needs splitting later)
- `ocr_processor.py` - OCR camera import system
- `admin_routes.py` - Admin panel routes
- `admin_system.py` - Admin logic
- `auth_routes.py` - Authentication routes
- `auth_system.py` - Authentication logic
- `template_management.py` - Template system
- `template_recipe_system.py` - Recipe templates

**Configuration:**
- `.env` - Environment variables (LOCAL ONLY - in .gitignore)
- `.env.example` - Example config (safe to commit)
- `.gitignore` - Git ignore rules
- `requirements.txt` - Python dependencies
- `runtime.txt` - Python version
- `Procfile` - Railway deployment
- `railway.json` - Railway config

**Documentation (will move to docs/):**
- `README.md` - Project overview (keep in root)
- `PROJECT_MASTER_GUIDE.md` - Will split into smaller files

---

### **🗑️ DELETE (Confirmed Safe to Remove)**

**Backup Directories:**
- ❌ `backup_before_mobile_ux_simplification_2025-09-23_15-21-32/`
- ❌ `backup_perfect_add_save_load_workflow_2025-09-24_13-21-23/`
- ❌ `backup_perfect_add_save_load_workflow_2025-09-24_13-24-34/`
- **Reason:** Old backups, code is in git history

**Backup Files:**
- ❌ `package-lock.json.backup`
- ❌ `package.json.backup`
- **Reason:** These are frontend files, belong in YesChefMobile/ (and are backed up)

**Root node_modules:**
- ❌ `node_modules/` (if exists in root)
- **Reason:** Should only be in YesChefMobile/, not root

---

### **📂 MOVE TO tests/**

**Test Files:**
- `test_admin_api.py`
- `test_admin_system.py`
- `test_complete_youtube_pipeline.py`
- `test_grocery_list.py`
- `test_ocr.py`
- `test_voice_backend.py`
- `test_youtube_api_integration.py`
- `test_youtube_extractor.py`
- `test_youtube_simple.py`

**Check/Debug Files:**
- `check_database_tables.py`
- `check_database_users.py`
- `check_ingredients.py`
- `check_railway_youtube.py`
- `check_recipe_2608.py`
- `check_recipe_format.py`
- `check_schema.py`
- `check_users_table.py`
- `debug_admin_account.py`
- `debug_grocery_list.py`
- `diagnose_youtube_integration.py`

**Cleanup/Fix Files:**
- `cleanup_duplicates.py`
- `fix_admin_issues.py`
- `fix_recipe_format.py`

---

### **📚 MOVE TO docs/**

**Will organize into subdirectories:**

**docs/features/** (Feature Documentation)
- `OCR_IMPLEMENTATION_COMPLETE.md`
- `VOICE_RECIPE_RECORDING_DESIGN_FINAL.md`
- `YOUTUBE_IMPORT_ARCHITECTURE.md`
- `YOUTUBE_IMPORT_FIXES.md`
- `YOUTUBE_IMPORT_SETUP_GUIDE.md`
- `YOUTUBE_IMPORT_SUCCESS_SUMMARY.md`
- `YOUTUBE_RECIPE_IMPORT_IMPLEMENTATION.md`
- `VIDEO_IMPORT_ROADMAP.md`
- `COLLABORATION_IMPLEMENTATION_PLAN.md`
- `NOTION_STYLE_EDITING_FEATURE.md`
- `REVENUECAT_SETUP_GUIDE.md`

**docs/setup/** (Setup & Configuration)
- `GOOGLE_VISION_SETUP.md`
- `RAILWAY_YOUTUBE_DEPLOYMENT.md`
- `PRODUCTION_STRUCTURE_PLAN.md`
- `INFRASTRUCTURE_REVIEW_OCT6.md`

**docs/fixes/** (Bug Fixes & Improvements)
- `FIXES_APPLIED.md`
- `FORMATTING_FIX.md`
- `STEP_NUMBER_IMPROVEMENT.md`
- `grocery_list_optimizations.md`

**docs/releases/** (Phase Summaries)
- `PHASE1_COMPLETE_SUMMARY.md`
- `PHASE2_COMPLETE_SUMMARY.md`
- `PRODUCTION_READINESS_REPORT.md`

**docs/legal/** (Privacy & Legal)
- `PRIVACY_POLICY.md`
- `PRIVACY_POLICY_HOSTING.md`
- `privacy-policy.html`

**docs/planning/** (TODO & Plans)
- `FAMILY_RECIPE_PRESERVATION_TODO.md`
- `VIDEO_RECIPE_IMPORT_PLAN.js` (evaluate if still needed)

---

### **⚠️ EVALUATE (Need Decision)**

**Utility Scripts:**
- `add_avatar_fields.py` - One-time migration script
- `copy_templates_to_test_user.py` - Development utility
- `create_collaborations_table.py` - SQLite migration
- `create_collaborations_table_postgresql.py` - PostgreSQL migration
- `initialize_templates.py` - Template seeding
- `clean_slate_admin_setup.py` - Admin reset
- `clean_slate_setup.py` - Database reset
- `clean_test_user_templates.py` - Test data cleanup

**Decision:** Keep if still useful, move to `scripts/utilities/` or delete

---

### **🔒 SECURITY CRITICAL**

**Files that MUST be in .gitignore:**
- ❌ `google-vision-credentials.json` - **CRITICAL: Contains API keys!**
- ❌ `hungie.db` - Local database (development only)
- ❌ `extraction_analytics.db` - Local analytics DB
- ❌ `.env` - Environment variables

**Action Required:**
1. Check if these are already in .gitignore
2. If not, add immediately
3. Remove from git history if committed

---

## **📁 PROPOSED DOCS/ STRUCTURE**

```
docs/
├── README.md                        # Navigation guide
├── features/
│   ├── OCR_CAMERA_IMPORT.md        # OCR system
│   ├── VOICE_RECORDING.md          # Voice system  
│   ├── YOUTUBE_IMPORT.md           # YouTube system
│   ├── COLLABORATION.md            # Collaboration features
│   └── MEAL_PLANNING.md            # Meal planning
├── setup/
│   ├── GOOGLE_VISION_SETUP.md      # OCR setup
│   ├── DEPLOYMENT.md               # Railway deployment
│   └── INFRASTRUCTURE.md           # Infrastructure guide
├── fixes/
│   ├── BUG_FIXES.md                # Bug fix log
│   └── OPTIMIZATIONS.md            # Performance improvements
├── releases/
│   ├── PHASE1_SUMMARY.md
│   ├── PHASE2_SUMMARY.md
│   └── PRODUCTION_READINESS.md
├── legal/
│   ├── PRIVACY_POLICY.md
│   └── privacy-policy.html
├── planning/
│   └── ROADMAP.md
├── history/
│   ├── 2025-10-OCTOBER.md          # Monthly achievements
│   └── 2025-09-SEPTEMBER.md
└── archive/
    └── [Old documentation]
```

---

## **📝 README.md USAGE**

**Purpose:** Project entry point and navigation hub

**Should Include:**
1. **Project Overview** (1-2 paragraphs)
2. **Quick Start** (How to run locally)
3. **Key Features** (Bullet list with links to docs/)
4. **Tech Stack** (Python, Flask, React Native, etc.)
5. **Documentation Navigation** (Links to docs/ folders)
6. **Contributing** (How to contribute)
7. **Security** (How to report issues)

**Should NOT Include:**
- Detailed feature documentation (goes in docs/features/)
- Historical logs (goes in docs/history/)
- API keys or credentials (never!)

---

## **🎯 EXECUTION PLAN**

### **Phase 1: Security First (TODAY)**
1. ✅ Check .gitignore for sensitive files
2. ✅ Add missing entries if needed
3. ✅ Verify google-vision-credentials.json is NOT in git
4. ✅ Run security scan

### **Phase 2: Delete Safe Files (TODAY)**
1. ✅ Delete backup directories
2. ✅ Delete .backup files
3. ✅ Delete root node_modules (if exists)
4. ✅ Commit: "chore: Remove backup directories and temp files"

### **Phase 3: Move Test Files (TODAY)**
1. ✅ Move all test_*.py to tests/
2. ✅ Move all check_*.py to tests/utilities/
3. ✅ Move all debug_*.py to tests/debug/
4. ✅ Commit: "chore: Organize test files into tests/ directory"

### **Phase 4: Organize Documentation (TODAY)**
1. ✅ Create docs/ subdirectories
2. ✅ Move .md files to appropriate folders
3. ✅ Update internal links
4. ✅ Commit: "docs: Organize documentation into structured folders"

### **Phase 5: Split PROJECT_MASTER_GUIDE (TODAY/TOMORROW)**
1. ✅ Extract monthly sections into history/
2. ✅ Extract feature docs into features/
3. ✅ Keep current status in PROJECT_MASTER_GUIDE.md
4. ✅ Commit: "docs: Split PROJECT_MASTER_GUIDE into maintainable files"

### **Phase 6: Update README (TODAY/TOMORROW)**
1. ✅ Rewrite README.md for clarity
2. ✅ Add navigation to new docs/ structure
3. ✅ Commit: "docs: Update README with project navigation"

### **Phase 7: Evaluate Scripts (LATER)**
1. Review utility scripts one by one
2. Keep useful ones in scripts/utilities/
3. Delete obsolete ones
4. Document what each does

---

## **✅ SUCCESS CRITERIA**

**Main Folder After Cleanup:**
- ≤ 15 Python files (core systems only)
- ≤ 5 .md files (README + PROJECT_MASTER_GUIDE + maybe 1-2 more)
- 0 backup directories
- 0 test files (all in tests/)
- Clean, professional appearance

**Security:**
- All sensitive files in .gitignore
- No API keys in documentation
- No credentials in git history

**Documentation:**
- Clear folder structure
- Easy to find information
- Each file < 500 lines
- Historical record preserved

---

## **🚨 NOTES FOR SAFETY**

1. **Before deleting anything:** Verify it's in git history
2. **Test files:** Don't delete until we verify they still work
3. **Script files:** Review one by one before removing
4. **Documentation:** Keep ALL information, just reorganize
5. **Credentials:** Triple-check .gitignore before committing

---

**Let's start with Phase 1: Security check! 🔒**
