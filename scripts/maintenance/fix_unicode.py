#!/usr/bin/env python3
"""
Quick fix script to replace Unicode emojis with ASCII alternatives
for Windows PowerShell compatibility
"""

import os
import re

def fix_unicode_in_file(filepath):
    """Replace Unicode emojis with ASCII alternatives"""
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Define emoji replacements
        replacements = {
            '✅': '[OK]',
            '❌': '[ERROR]',
            '🧪': '[TEST]',
            '🔍': '[SEARCH]',
            '🏥': '[DIAGNOSTIC]',
            '📊': '[REPORT]',
            '📋': '[CHECKLIST]',
            '🔧': '[SYSTEM]',
            '⚠️': '[WARNING]',
            '🚀': '[LAUNCH]',
            '💾': '[SAVE]',
            '🔑': '[AUTH]',
            '🛡️': '[SECURITY]',
        }
        
        # Apply replacements
        for emoji, ascii_replacement in replacements.items():
            content = content.replace(emoji, ascii_replacement)
        
        # Only write if changes were made
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed Unicode in: {filepath}")
            return True
        else:
            print(f"No Unicode found in: {filepath}")
            return False
            
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
        return False

def main():
    """Fix Unicode in authentication files"""
    
    files_to_fix = [
        'auth_system.py',
        'auth_routes.py',
        'server_diagnostics.py'
    ]
    
    fixed_count = 0
    
    for filename in files_to_fix:
        if os.path.exists(filename):
            if fix_unicode_in_file(filename):
                fixed_count += 1
        else:
            print(f"File not found: {filename}")
    
    print(f"\nFixed {fixed_count} files")
    print("Unicode emojis replaced with ASCII alternatives for Windows compatibility")

if __name__ == "__main__":
    main()
