"""
Check user recipes to diagnose why frontend can't see them
"""

import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection():
    """Get database connection"""
    # Try Railway URL first
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return psycopg2.connect(database_url)
    
    # Fallback to individual params
    return psycopg2.connect(
        host=os.getenv('PGHOST'),
        database=os.getenv('PGDATABASE'),
        user=os.getenv('PGUSER'),
        password=os.getenv('PGPASSWORD'),
        port=os.getenv('PGPORT', 5432)
    )

def check_user_recipes(user_id=11):
    """Check recipes for a specific user"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    print("=" * 80)
    print(f"🔍 CHECKING RECIPES FOR USER {user_id}")
    print("=" * 80)
    
    # 1. Total recipes for user
    cursor.execute("""
        SELECT COUNT(*) as total FROM recipes WHERE user_id = %s
    """, (user_id,))
    total = cursor.fetchone()['total']
    print(f"\n📊 Total recipes for user {user_id}: {total}")
    
    # 2. Breakdown by is_template
    cursor.execute("""
        SELECT 
            is_template,
            COUNT(*) as count
        FROM recipes 
        WHERE user_id = %s
        GROUP BY is_template
        ORDER BY is_template
    """, (user_id,))
    breakdown = cursor.fetchall()
    print(f"\n📋 Breakdown by is_template:")
    for row in breakdown:
        template_status = "TRUE (template)" if row['is_template'] else "FALSE (user recipe)"
        print(f"  - is_template = {template_status}: {row['count']} recipes")
    
    # 3. What V1 would see (is_template = FALSE)
    cursor.execute("""
        SELECT COUNT(*) as v1_count FROM recipes 
        WHERE user_id = %s AND is_template = FALSE
    """, (user_id,))
    v1_count = cursor.fetchone()['v1_count']
    print(f"\n🌐 What V1 frontend sees (is_template = FALSE): {v1_count} recipes")
    
    # 4. What V2 would see (all recipes)
    cursor.execute("""
        SELECT COUNT(*) as v2_count FROM recipes 
        WHERE user_id = %s
    """, (user_id,))
    v2_count = cursor.fetchone()['v2_count']
    print(f"📱 What V2 mobile sees (all recipes): {v2_count} recipes")
    
    # 5. Sample recipes
    print(f"\n📝 Sample of your recipes (first 10):")
    cursor.execute("""
        SELECT 
            id, 
            title, 
            is_template, 
            template_id,
            category,
            created_at::date as created
        FROM recipes 
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT 10
    """, (user_id,))
    
    recipes = cursor.fetchall()
    print("\n" + "-" * 120)
    print(f"{'ID':<8} {'Title':<40} {'is_template':<12} {'template_id':<12} {'Category':<15} {'Created':<12}")
    print("-" * 120)
    for recipe in recipes:
        title = recipe['title'][:37] + "..." if len(recipe['title']) > 40 else recipe['title']
        template_id = str(recipe['template_id']) if recipe['template_id'] else "NULL"
        print(f"{recipe['id']:<8} {title:<40} {str(recipe['is_template']):<12} {template_id:<12} {recipe['category'] or 'NULL':<15} {str(recipe['created']):<12}")
    
    # 6. Check if any templates exist
    cursor.execute("""
        SELECT COUNT(*) as template_count 
        FROM recipes 
        WHERE user_id = %s AND is_template = TRUE
    """, (user_id,))
    template_count = cursor.fetchone()['template_count']
    
    if template_count > 0:
        print(f"\n⚠️  WARNING: You have {template_count} recipes marked as is_template = TRUE!")
        print(f"   These will NOT show in the web frontend (v1)")
        print(f"   But WILL show in mobile app (v2)")
        
        print(f"\n📋 Recipes marked as templates:")
        cursor.execute("""
            SELECT id, title, category, created_at::date as created
            FROM recipes 
            WHERE user_id = %s AND is_template = TRUE
            ORDER BY created_at DESC
            LIMIT 10
        """, (user_id,))
        
        templates = cursor.fetchall()
        print("-" * 80)
        print(f"{'ID':<8} {'Title':<50} {'Category':<15} {'Created':<12}")
        print("-" * 80)
        for recipe in templates:
            title = recipe['title'][:47] + "..." if len(recipe['title']) > 50 else recipe['title']
            print(f"{recipe['id']:<8} {title:<50} {recipe['category'] or 'NULL':<15} {str(recipe['created']):<12}")
    else:
        print(f"\n✅ Good! No recipes marked as templates")
    
    # 7. Recommendation
    print("\n" + "=" * 80)
    print("💡 DIAGNOSIS:")
    print("=" * 80)
    
    if template_count > 0:
        print(f"❌ ISSUE FOUND: {template_count} recipes have is_template = TRUE")
        print(f"   - These are hidden from web frontend (v1 uses: WHERE is_template = FALSE)")
        print(f"   - These are visible in mobile (v2 doesn't filter by is_template)")
        print(f"\n🔧 FIX OPTIONS:")
        print(f"   Option 1: Set is_template = FALSE for these recipes (if they're your personal recipes)")
        print(f"   Option 2: Update frontend to use v2 endpoint (recommended long-term)")
        print(f"\n   To fix now, run: python scripts/database/fix_user_recipes.py")
    elif v1_count == 0:
        print(f"❌ ISSUE: No recipes with is_template = FALSE for user {user_id}")
        print(f"   - V1 frontend can't see ANY recipes")
        print(f"   - Check if user_id is correct")
        print(f"   - Check if recipes exist for this user")
    else:
        print(f"✅ Everything looks normal!")
        print(f"   - {v1_count} recipes visible to web frontend")
        print(f"   - {v2_count} recipes visible to mobile")
        print(f"   - If frontend still doesn't show recipes, check authentication/network")
    
    print("=" * 80)
    
    conn.close()

if __name__ == '__main__':
    import sys
    user_id = int(sys.argv[1]) if len(sys.argv) > 1 else 11
    check_user_recipes(user_id)
