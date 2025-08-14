# Me Hungie Folder Cleanup Plan
Generated: August 8, 2025

## 🎯 Goal: Keep only essential production files

## ✅ KEEP - Core Production Files:
- `hungie_server.py` - Main backend server
- `enhanced_search.py` - Search functionality  
- `production_flavor_system.py` - Flavor system
- `recipe_database_enhancer.py` - Database enhancement
- `hungie.db` - Main database
- `frontend/` - React frontend
- `.env` - Environment variables
- `requirements.txt` - Python dependencies
- `package.json` - Node dependencies
- `PROJECT_STRUCTURE_GUIDE.md` - Updated documentation
- `.git/` - Version control
- `.gitignore` - Git ignore rules

## ✅ KEEP - Important Data:
- `data/` - Recipe collections and archives
- `flavor_bible_data/` - Flavor pairing data
- `bonappetit-collection-2025-08-04.json` - Recipe collection
- `The-Flavor-Bible (1).pdf` - Reference material

## ✅ KEEP - Organized Scripts (move to scripts/):
- `import_bonappetit_recipes.py` - Data import utility
- `categorize_recipes.py` - Category management
- `enhance_database.py` - Database enhancement

## 🗑️ REMOVE - Temporary/Debug Files:
### App Backups (already backed up):
- `app_backup.py`
- `app_backup_20250808_120229.py` 
- `app_backup_20250808_120232.py`
- `app_clean.py`
- `app_problematic_backup.py`
- `backend_server.py`

### Debug/Test Files:
- `debug_*.py` (16 files)
- `check_*.py` (25+ files) 
- `test_*.py` (except test_api.py)
- `quick_*.py` (5 files)
- `simple_*.py` (8 files)
- `manual_*.py` (2 files)
- `final_*.py` (7 files)

### Parser Development Files:
- `*_parser.py` (30+ parser variations)
- `analyze_*.py` (10+ analysis files)
- `working_*.py` (3 files)
- `fixed_*.py` (4 files)
- `complete_*.py` (3 files)

### Temporary/Experimental:
- `adaptive_recipe_parser.py`
- `comprehensive_parser.py`
- `pattern_recognition_parser.py`
- `human_like_parser.py`
- `ingredient_extractor.py`
- All `*_test.py` files
- `cleanup_*.py` files
- `migrate_*.py` files
- `repair_*.py` files

### Old/Deprecated:
- `main.py` (old server)
- `server.py` (old server)
- `minimal_server.py`
- `clean_server.py`
- `prod_server.py`
- Node modules (will reinstall)
- `__pycache__/`
- `me_hungie.egg-info/`
- `venv/` (if present, will recreate)

### Archive Files:
- `bonappetit_archive_*.json`
- `hungie_backup_*.db`
- Log files: `*.log`
- Error reports: `*_error_report.json`

## 📁 ORGANIZE - Move to Proper Directories:
### scripts/data_import/:
- `import_bonappetit_recipes.py`
- `import_session_recipes.py`
- `integrate_recipes.py`

### scripts/maintenance/:
- `categorize_recipes.py`
- `enhance_database.py`
- `database_analyzer.py`

### docs/:
- All `.md` files except PROJECT_STRUCTURE_GUIDE.md
- `USAGE_GUIDE.md`
- `SUCCESS_GUIDE.md`
- etc.

### archive/:
- `hungie_backup_*.db`
- `bonappetit_archive_*.json`
- All backup files

## 🎯 Expected Result:
Clean folder with ~20 essential files instead of 200+ files
