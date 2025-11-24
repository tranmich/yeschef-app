"""
Phase 2: Audit Legacy Column Usage
===================================
Find all references to legacy columns that need to be updated
"""

import os
import re
from pathlib import Path

def search_file(filepath, patterns):
    """Search a file for patterns"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        results = []
        for pattern_name, pattern in patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                line = content.split('\n')[line_num - 1].strip()
                results.append({
                    'pattern': pattern_name,
                    'line': line_num,
                    'text': line
                })
        
        return results
    except Exception as e:
        return []

def audit_codebase():
    base_path = Path(__file__).parent
    
    # Patterns to search for
    legacy_patterns = {
        'list_name': r'\blist_name\b',
        'items_json': r'\bitems_json\b',
        'updated_date': r'\bupdated_date\b',
        'created_date': r'\bcreated_date\b'
    }
    
    # Files to check
    files_to_check = [
        'app/database/repositories/grocery_list_repository.py',
        'hungie_server.py',
        'app/api/v2/grocery_lists.py',
        'app/api/v2/whiteboards.py'
    ]
    
    print("=" * 80)
    print("PHASE 2: LEGACY COLUMN USAGE AUDIT")
    print("=" * 80)
    print()
    
    total_references = 0
    
    for filepath in files_to_check:
        full_path = base_path / filepath
        if not full_path.exists():
            print(f"⚠️  {filepath}: NOT FOUND")
            continue
        
        results = search_file(full_path, legacy_patterns)
        
        if results:
            print(f"\n📁 {filepath}")
            print("-" * 80)
            
            pattern_counts = {}
            for result in results:
                pattern = result['pattern']
                pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
            
            for pattern, count in pattern_counts.items():
                print(f"   {pattern}: {count} references")
                total_references += count
            
            # Show first few examples
            print(f"\n   Examples:")
            for result in results[:5]:
                print(f"      Line {result['line']:4d}: {result['text'][:80]}")
            
            if len(results) > 5:
                print(f"      ... and {len(results) - 5} more")
    
    print("\n" + "=" * 80)
    print(f"TOTAL LEGACY REFERENCES: {total_references}")
    print("=" * 80)
    print()
    
    if total_references > 0:
        print("⚠️  These need to be updated to use:")
        print("   • list_name → name")
        print("   • items_json → list_data")
        print("   • updated_date → updated_at")
        print("   • created_date → created_at")
    else:
        print("✅ No legacy column references found!")
    
    return total_references

if __name__ == '__main__':
    audit_codebase()
