"""
Check Database for Old Meal Plan Formats

This script checks if any meal plans use the old breakfast/lunch/dinner
format so we can safely clean up the code.
"""

import psycopg2
import json
from datetime import datetime

# Database connection
def get_db_connection():
    """Connect to PostgreSQL database (Railway)"""
    database_url = "postgresql://postgres:udQLpljdqTYmESmntwzmwDcOlBVbqlJG@shuttle.proxy.rlwy.net:31331/railway"
    return psycopg2.connect(database_url)

def check_old_format_plans():
    """Check for plans using old breakfast/lunch/dinner format"""
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    print("=" * 80)
    print("🔍 CHECKING FOR OLD FORMAT MEAL PLANS")
    print("=" * 80)
    print()
    
    # 1. Count total meal plans
    cur.execute("SELECT COUNT(*) FROM meal_plans WHERE user_id = 11")
    total_plans = cur.fetchone()[0]
    print(f"📊 Total meal plans for user 11: {total_plans}")
    print()
    
    # 2. Check for plans with old format (contains breakfast/lunch/dinner)
    query = """
        SELECT 
            id, 
            plan_name, 
            created_date,
            plan_data_json 
        FROM meal_plans 
        WHERE user_id = 11 
        AND (
            plan_data_json::text LIKE '%breakfast%' OR
            plan_data_json::text LIKE '%lunch%' OR
            plan_data_json::text LIKE '%dinner%'
        )
        ORDER BY created_date DESC
    """
    
    cur.execute(query)
    old_format_plans = cur.fetchall()
    
    print(f"🔍 Plans with breakfast/lunch/dinner format: {len(old_format_plans)}")
    print()
    
    if old_format_plans:
        print("⚠️ OLD FORMAT PLANS FOUND:")
        print("-" * 80)
        
        for plan in old_format_plans:
            plan_id, plan_name, created_date, plan_data_json = plan
            
            print(f"Plan ID: {plan_id}")
            print(f"Name: {plan_name}")
            print(f"Created: {created_date}")
            
            # Parse JSON to see structure
            try:
                plan_data = json.loads(plan_data_json) if isinstance(plan_data_json, str) else plan_data_json
                
                # Check if it's old Notion format or new array format
                if isinstance(plan_data, dict):
                    # Old format: {monday: {...}, tuesday: {...}}
                    print(f"Format: OLD v1 (Notion style - object with day names)")
                    print(f"Days: {', '.join(plan_data.keys())}")
                elif isinstance(plan_data, list):
                    # New format: [{id: 1, name: "Day 1", ...}, ...]
                    print(f"Format: NEW v2 (Mobile array - {len(plan_data)} days)")
                    
                    # Check if any day has meals array with breakfast/lunch/dinner
                    has_meals_array = False
                    for day in plan_data:
                        if 'meals' in day and isinstance(day['meals'], list):
                            meal_names = [meal.get('name', '') for meal in day['meals']]
                            if 'Breakfast' in meal_names or 'Lunch' in meal_names or 'Dinner' in meal_names:
                                has_meals_array = True
                                print(f"  Day '{day.get('name')}' has meals: {', '.join(meal_names)}")
                    
                    if has_meals_array:
                        print(f"  ⚠️ Contains unused 'meals' array with B/L/D structure")
                    else:
                        print(f"  ✅ Just mentions breakfast/lunch/dinner in text/recipes")
                
                print()
                
            except Exception as e:
                print(f"Error parsing JSON: {e}")
                print()
        
        print("-" * 80)
    else:
        print("✅ NO OLD FORMAT PLANS FOUND!")
        print("✅ Safe to remove breakfast/lunch/dinner code!")
        print()
    
    # 3. Show sample of new format plans
    query = """
        SELECT 
            id, 
            plan_name, 
            created_date,
            plan_data_json 
        FROM meal_plans 
        WHERE user_id = 11 
        ORDER BY created_date DESC
        LIMIT 5
    """
    
    cur.execute(query)
    recent_plans = cur.fetchall()
    
    print("📋 RECENT PLANS (Last 5):")
    print("-" * 80)
    
    for plan in recent_plans:
        plan_id, plan_name, created_date, plan_data_json = plan
        
        try:
            plan_data = json.loads(plan_data_json) if isinstance(plan_data_json, str) else plan_data_json
            
            if isinstance(plan_data, dict):
                format_type = "OLD v1 (Object)"
                days_info = f"{len(plan_data.keys())} days"
            elif isinstance(plan_data, list):
                format_type = "NEW v2 (Array)"
                days_info = f"{len(plan_data)} days"
                
                # Check for meals array
                has_meals = any('meals' in day for day in plan_data)
                if has_meals:
                    format_type += " (with meals array)"
            else:
                format_type = "UNKNOWN"
                days_info = "?"
            
            print(f"{plan_id:3d} | {plan_name:30s} | {str(created_date)[:10]} | {format_type:25s} | {days_info}")
            
        except Exception as e:
            print(f"{plan_id:3d} | {plan_name:30s} | {str(created_date)[:10]} | ERROR parsing")
    
    print("-" * 80)
    print()
    
    cur.close()
    conn.close()
    
    return len(old_format_plans)

def main():
    try:
        old_count = check_old_format_plans()
        
        print()
        print("=" * 80)
        print("🎯 RECOMMENDATION:")
        print("=" * 80)
        
        if old_count == 0:
            print("✅ NO OLD FORMAT PLANS FOUND!")
            print("✅ SAFE TO REMOVE breakfast/lunch/dinner code!")
            print("✅ All plans use new format or don't have meals array")
            print()
            print("Next steps:")
            print("1. Remove meals array from new plan creation")
            print("2. Remove breakfast/lunch/dinner merge logic")
            print("3. Simplify to just use day.recipes")
        else:
            print(f"⚠️ FOUND {old_count} plans with old format!")
            print("⚠️ Need to decide:")
            print("  Option 1: Migrate these plans to new format")
            print("  Option 2: Keep backward compatibility code")
        
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
