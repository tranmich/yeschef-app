# Bon Appétit Recipe Import & Enhancement Process

This is the complete workflow for importing new BonAppetitePersonal recipe collections and enhancing them with analysis data.

## 📋 Step-by-Step Process

### 1. Import New Recipe Data
```bash
cd "d:\Mik\Downloads\Me Hungie"
python scripts\data_import\import_bonappetit_recipes.py
```
**What it does:**
- Imports JSON files from `data/` folder
- Prevents duplicates via URL checking
- Maps BonAppetitePersonal format to hungie.db schema
- Creates ingredient and instruction relationships

### 2. Generate Recipe Analysis (Automatic)
The recipe analyzer should run automatically when the import detects new recipes. If not:
```bash
cd "d:\Mik\Downloads\Me Hungie"
python recipe_analyzer.py
```
**What it does:**
- Analyzes cuisine type, difficulty, techniques
- Identifies main proteins and cooking methods
- Calculates complexity scores and time estimates
- Integrates with FlavorProfile System

### 3. Generate Flavor Profiles
```bash
cd "d:\Mik\Downloads\Me Hungie"
python scripts\enhancement\generate_flavor_profiles.py
```
**What it does:**
- Creates primary/secondary flavor classifications
- Determines intensity levels and cuisine styles
- Calculates complexity and harmony scores
- Links to comprehensive flavor database

### 4. Verify Complete Enhancement
```bash
cd "d:\Mik\Downloads\Me Hungie"
python scripts\verification\final_verification.py
```
**What it does:**
- Checks that all new recipes have analysis data
- Verifies flavor profile completion
- Shows sample enhanced recipe details
- Confirms API compatibility

## 🎯 Expected Results

After completing all steps:
- ✅ All new recipes imported into hungie.db
- ✅ Complete analysis data (difficulty, cuisine, techniques)
- ✅ Comprehensive flavor profiles (flavors, intensity, style)
- ✅ API endpoints updated with new searchable data
- ✅ Frontend can access enhanced recipe information

## 📁 File Locations

- **Data files**: `data/session_*_recipes_*.json`
- **Import script**: `scripts/data_import/import_bonappetit_recipes.py`
- **Enhancement**: `scripts/enhancement/generate_flavor_profiles.py`
- **Verification**: `scripts/verification/final_verification.py`
- **Database**: `hungie.db`

## 🔧 Prerequisites

- Flask backend stopped (if running)
- BonAppetitePersonal JSON files in `data/` folder
- Python environment with required packages
- Access to `hungie.db` database

---

*Quick Reference Guide - August 8, 2025*
