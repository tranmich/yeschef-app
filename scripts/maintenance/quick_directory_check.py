#!/usr/bin/env python3
"""
Quick check script - Run this when opening VS Code to detect unwanted files
"""
import os

EXPECTED_ROOT_FILES = {
    'hungie_server.py', 'recipe_database_enhancer.py', 'hungie.db', 'recipe_books.db',
    '.env', '.env.example', 'package-lock.json', 'setup.py', 'Procfile', 
    'nixpacks.toml', 'railway.json', 'runtime.txt', 'README.md',
    'PROJECT_MASTER_GUIDE.md', 'ENHANCED_PARSER_GUIDE.md', 
    'RECIPE_SEARCH_LOGIC_EXPLAINED.md', 'RECIPE_SEARCH_DIAGRAMS.md'
}

EXPECTED_ROOT_DIRS = {
    '.git', '.github', '.vscode', 'core_systems', 'frontend', 'scripts', 
    'docs', 'tests', 'universal_recipe_parser', 'cookbook_processing',
    'archived_temp_files', 'Books', 'flavor_systems', 'web', 'venv', 
    '__pycache__', 'mocks'
}

def check_directory():
    base_dir = r"d:\Mik\Downloads\Me Hungie"
    unwanted_files = []
    
    for item in os.listdir(base_dir):
        if item not in EXPECTED_ROOT_FILES and item not in EXPECTED_ROOT_DIRS:
            if not item.startswith('.'):
                unwanted_files.append(item)
    
    if unwanted_files:
        print(f"⚠️  WARNING: {len(unwanted_files)} unwanted files detected!")
        for file in unwanted_files:
            print(f"   - {file}")
        print(f"\n🧹 Run cleanup script:")
        print(f"   python scripts\\maintenance\\restore_clean_structure_aug11.py")
        return False
    else:
        print("✅ Directory is clean and organized!")
        return True

if __name__ == "__main__":
    check_directory()
