# Hungie Scripts Directory

This directory contains organized scripts for data import, recipe enhancement, and verification processes.

## 📁 Directory Structure

### `/data_import/`
Scripts for importing recipe data from various sources into the hungie.db database.

- **`import_bonappetit_recipes.py`** - Imports BonAppetitePersonal Chrome Extension JSON files into hungie.db
  - Handles JSON parsing from BonAppetitePersonal format
  - Maps data to hungie.db schema (name → title, etc.)
  - Prevents duplicates via URL checking
  - Creates proper foreign key relationships

### `/enhancement/`
Scripts for enhancing recipes with analysis data and flavor profiles.

- **`generate_flavor_profiles.py`** - Generates comprehensive flavor profiles for recipes
  - Creates primary/secondary flavor classifications
  - Determines intensity levels (mild/moderate/bold)
  - Assigns cuisine styles and complexity scores
  - Integrates with FlavorProfile System

### `/verification/`
Scripts for testing and verifying database content and API functionality.

- **`check_ba_analysis.py`** - Checks analysis and flavor profile completion for Bon Appétit recipes
- **`final_verification.py`** - Detailed verification of enhanced recipe data across multiple samples
- **`check_analysis_data.py`** - General check for analysis-related tables and data
- **`test_direct_search.py`** - Direct database search testing
- **`quick_verify.py`** - Quick recipe count and sample verification
- **`test_api.py`** - Flask API endpoint testing

### `/web_scraping/`
Scripts for web scraping and Chrome extension automation.

- **`automate_scraping.js`** - Browser automation for recipe collection
- **`click_extension.js`** - Chrome extension interaction scripts
- **`pack_extension.js`** - Extension packaging utilities
- **`scrape_recipes.py`** - Python-based recipe scraping tools

### `/database_management/`
Scripts for database organization and recipe management.

- **`manage_recipes.py`** - General recipe database management
- **`organize_recipes.py`** - Recipe organization and categorization tools

### `/book_parsing/`
Scripts for parsing PDF cookbooks and extracting structured recipe data.

- **`complete_canadian_parser.py`** - Main parser for Canadian Living cookbook format
- **`refined_pdf_parser.py`** - Enhanced parser for The Flavor Bible and reference books
- **`complete_bible_parser.py`** - Full processor for large documents (962+ pages)
- **`pdf_formatting_analyzer.py`** - PDF structure analysis tool
- **`check_books_db.py`** - Database verification for parsed book data
- **`check_books_structure.py`** - Book database schema verification
- **`import_bonappetit_to_recipe_books.py`** - Cross-database import utility

## 🚀 Usage Examples

### Import New Recipe Data
```bash
cd scripts/data_import
python import_bonappetit_recipes.py
```

### Generate Recipe Analysis for Books
```bash
cd scripts/book_parsing  
python complete_canadian_parser.py
```

### Generate Missing Flavor Profiles
```bash
cd scripts/enhancement  
python generate_flavor_profiles.py
```

### Parse New PDF Cookbook
```bash
cd scripts/book_parsing
python pdf_formatting_analyzer.py  # Analyze structure first
python complete_canadian_parser.py # Parse recipes
```

### Verify Database Status
```bash
cd scripts/verification
python final_verification.py
```

## 📋 Prerequisites

All scripts require:
- Python 3.7+
- Access to `hungie.db` database (run from project root)
- Required imports: `sqlite3`, `json`, `datetime`
- For enhancement scripts: `flavor_profile_system.py` and `recipe_analyzer.py`

## 🔗 Related Files

These scripts work with:
- **Main database**: `hungie.db`
- **Recipe analyzer**: `recipe_analyzer.py` 
- **Flavor system**: `flavor_profile_system.py`, `enhanced_flavor_profile_system.py`
- **Main app**: `app.py`
- **Data files**: `data/` directory with JSON recipe collections

---

*Last updated: August 8, 2025*
*Total scripts organized: 21 across 6 categories*
