#!/usr/bin/env python3
"""
Emergency cleanup script - VS Code restored archived files
Restore the clean main directory structure from yesterday's work
"""
import os
import shutil
from datetime import datetime

# Files that should STAY in root directory (core production files)
CORE_PRODUCTION_FILES = {
    'hungie_server.py',
    'recipe_database_enhancer.py', 
    'hungie.db',
    'recipe_books.db',
    '.env',
    '.env.example',
    'package-lock.json',
    'setup.py',
    'Procfile',
    'nixpacks.toml',
    'railway.json',
    'runtime.txt',
    'README.md',
    'PROJECT_MASTER_GUIDE.md',
    'ENHANCED_PARSER_GUIDE.md',
    'RECIPE_SEARCH_LOGIC_EXPLAINED.md',
    'RECIPE_SEARCH_DIAGRAMS.md'
}

# Directories that should STAY in root
CORE_DIRECTORIES = {
    '.git',
    '.github', 
    'core_systems',
    'frontend',
    'scripts',
    'docs',
    'tests',
    'universal_recipe_parser',
    'cookbook_processing',
    'archived_temp_files',
    'Books',
    'flavor_systems',
    'web',
    'venv',
    '__pycache__',
    'mocks'
}

def main():
    base_dir = r"d:\Mik\Downloads\Me Hungie"
    archive_dir = os.path.join(base_dir, "archived_temp_files", "vs_code_restore_cleanup_aug11")
    
    # Create archive directory
    os.makedirs(archive_dir, exist_ok=True)
    
    print("🧹 Emergency cleanup - Restoring clean main directory structure")
    print(f"📦 Moving unwanted files to: {archive_dir}")
    
    moved_files = []
    
    # Check each item in main directory
    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)
        
        # Skip if it's a core file or directory
        if item in CORE_PRODUCTION_FILES or item in CORE_DIRECTORIES:
            continue
            
        # Skip special files
        if item.startswith('.') and item not in CORE_PRODUCTION_FILES:
            continue
            
        try:
            # Move unwanted files to archive
            dest_path = os.path.join(archive_dir, item)
            if os.path.isfile(item_path):
                shutil.move(item_path, dest_path)
                moved_files.append(f"📄 {item}")
                print(f"Moved file: {item}")
            elif os.path.isdir(item_path):
                shutil.move(item_path, dest_path) 
                moved_files.append(f"📁 {item}")
                print(f"Moved directory: {item}")
        except Exception as e:
            print(f"⚠️  Error moving {item}: {e}")
    
    # Create summary report
    report_path = os.path.join(archive_dir, "CLEANUP_REPORT.md")
    with open(report_path, 'w') as f:
        f.write(f"# VS Code Restore Cleanup Report\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Reason:** VS Code restored archived files to main directory\n\n")
        f.write(f"## Files Moved to Archive ({len(moved_files)} total):\n")
        for file in moved_files:
            f.write(f"- {file}\n")
        f.write(f"\n## Core Files Preserved in Root:\n")
        for file in sorted(CORE_PRODUCTION_FILES):
            f.write(f"- 📄 {file}\n")
        f.write(f"\n## Core Directories Preserved:\n")
        for dir in sorted(CORE_DIRECTORIES):
            f.write(f"- 📁 {dir}/\n")
    
    print(f"\n✅ Cleanup complete!")
    print(f"📊 Moved {len(moved_files)} items to archive")
    print(f"📋 Report saved to: {report_path}")
    print(f"\n🎯 Main directory is now clean and organized!")

if __name__ == "__main__":
    main()
