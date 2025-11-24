"""
Grocery List API Endpoint Audit
================================
Purpose: Map all endpoints, their column usage, and callers
Date: November 12, 2025
"""

import re
import os

def audit_endpoints():
    print("=" * 80)
    print("GROCERY LIST API ENDPOINT AUDIT")
    print("=" * 80)
    print()
    
    # Search for all grocery list related endpoints
    files_to_check = [
        ('hungie_server.py', 'Legacy V1 API'),
        ('app/api/v2/grocery_lists.py', 'V2 API'),
        ('app/api/v2/whiteboards.py', 'Whiteboard API'),
        ('app/database/repositories/grocery_list_repository.py', 'Repository Layer')
    ]
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    for filepath, description in files_to_check:
        full_path = os.path.join(base_path, filepath)
        if not os.path.exists(full_path):
            print(f"❌ {description}: {filepath} NOT FOUND")
            continue
            
        print(f"\n{'=' * 80}")
        print(f"📁 {description}: {filepath}")
        print('=' * 80)
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Find route definitions
        routes = re.findall(r"@\w+\.route\(['\"](.*?)['\"].*?methods=\[(.*?)\]", content, re.DOTALL)
        if not routes:
            routes = re.findall(r"@app\.route\(['\"](.*?)['\"].*?methods=\[(.*?)\]", content, re.DOTALL)
        
        if routes:
            print(f"\n🔗 ENDPOINTS FOUND: {len(routes)}")
            for route, methods in routes:
                if 'grocery' in route.lower():
                    print(f"  • {methods.strip():20} {route}")
        
        # Find column usage
        print(f"\n📊 COLUMN USAGE:")
        
        columns_to_check = {
            'name': 0,
            'list_name': 0,
            'items_json': 0,
            'list_data': 0,
            'updated_at': 0,
            'updated_date': 0,
            'created_at': 0,
            'created_date': 0
        }
        
        for col in columns_to_check.keys():
            # Count occurrences in SELECT/UPDATE/INSERT statements
            pattern = rf'\b{col}\b'
            matches = re.findall(pattern, content, re.IGNORECASE)
            columns_to_check[col] = len(matches)
        
        # Group by duplicate sets
        print("\n  Legacy Columns (V1):")
        print(f"    list_name:    {columns_to_check['list_name']:3d} occurrences")
        print(f"    list_data:    {columns_to_check['list_data']:3d} occurrences")
        print(f"    updated_at:   {columns_to_check['updated_at']:3d} occurrences")
        print(f"    created_at:   {columns_to_check['created_at']:3d} occurrences")
        
        print("\n  Whiteboard Columns (New):")
        print(f"    name:         {columns_to_check['name']:3d} occurrences")
        print(f"    items_json:   {columns_to_check['items_json']:3d} occurrences")
        print(f"    updated_date: {columns_to_check['updated_date']:3d} occurrences")
        print(f"    created_date: {columns_to_check['created_date']:3d} occurrences")
        
        # Find function definitions
        functions = re.findall(r'def (.*?grocery.*?)\(', content, re.IGNORECASE)
        if functions:
            print(f"\n🔧 FUNCTIONS: {len(functions)}")
            for func in functions[:10]:  # Show first 10
                print(f"  • {func}")
            if len(functions) > 10:
                print(f"  ... and {len(functions) - 10} more")

def check_frontend_usage():
    print("\n\n" + "=" * 80)
    print("FRONTEND API CALLS AUDIT")
    print("=" * 80)
    
    frontend_files = [
        'frontend/src/components/GroceryManagerWorkspace.js',
        'frontend/src/components/LoadGroceryListPanel.js',
        'frontend/src/pages/WhiteboardApp.js',
        'frontend/src/components/whiteboard/nodes/GroceryListNode.js'
    ]
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    for filepath in frontend_files:
        full_path = os.path.join(base_path, filepath)
        if not os.path.exists(full_path):
            continue
            
        print(f"\n📱 {os.path.basename(filepath)}")
        print("-" * 80)
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find API calls
        api_calls = re.findall(r'(?:fetch|apiCall|api\.|whiteboardAPI\.)\([\'"`]([^\'"`]*grocery[^\'"`]*)', content, re.IGNORECASE)
        
        if api_calls:
            print(f"  API Calls: {len(api_calls)}")
            for call in set(api_calls):
                print(f"    • {call}")
        else:
            print("  No direct API calls found")
        
        # Check which fields are accessed
        field_access = re.findall(r'\.(list_name|name|list_data|items_json|items|updated_at|updated_date)', content)
        if field_access:
            from collections import Counter
            counts = Counter(field_access)
            print(f"\n  Field Access:")
            for field, count in counts.most_common():
                print(f"    {field:15} {count:3d}x")

if __name__ == '__main__':
    audit_endpoints()
    check_frontend_usage()
    
    print("\n\n" + "=" * 80)
    print("SUMMARY & RECOMMENDATIONS")
    print("=" * 80)
    print("""
Based on this audit, we can see:

1. WHICH endpoints use which columns
2. WHERE the inconsistencies are
3. WHAT needs to be unified
4. HOW to safely migrate

Next steps:
1. Create unified update method (writes to ALL columns)
2. Create unified read method (uses COALESCE for newest data)
3. Migrate existing data to ensure consistency
4. Test thoroughly
5. Deprecate old columns (future)
""")
