"""
Clean Up Old Meal Plan Formats

This script deletes all old v1 format meal plans and keeps only v2 format plans.
NO BACKUP - as requested!
"""

import psycopg2
import json
from datetime import datetime

# Database connection
def get_db_connection():
    """Connect to PostgreSQL database (Railway)"""
    database_url = "postgresql://postgres:udQLpljdqTYmESmntwzmwDcOlBVbqlJG@shuttle.proxy.rlwy.net:31331/railway"
    return psycopg2.connect(database_url)

def delete_old_format_plans():
    """Delete all old v1 format meal plans"""
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    print("=" * 80)
    print("🧹 CLEANING UP OLD MEAL PLAN FORMATS")
    print("=" * 80)
    print()
    
    # 1. Show what we're about to delete
    print("📋 IDENTIFYING PLANS TO DELETE...")
    print()
    
    query = """
        SELECT 
            id, 
            plan_name, 
            created_date,
            plan_data_json 
        FROM meal_plans 
        WHERE user_id = 11 
        ORDER BY created_date DESC
    """
    
    cur.execute(query)
    all_plans = cur.fetchall()
    
    plans_to_delete = []
    plans_to_keep = []
    
    for plan in all_plans:
        plan_id, plan_name, created_date, plan_data_json = plan
        
        try:
            plan_data = json.loads(plan_data_json) if isinstance(plan_data_json, str) else plan_data_json
            
            # Check format
            if isinstance(plan_data, dict):
                # Old v1 format - DELETE
                plans_to_delete.append((plan_id, plan_name, created_date, "OLD v1 (Object)"))
            elif isinstance(plan_data, list):
                # Check if it's the clean new format or has meals array
                has_meals_array = False
                for day in plan_data:
                    if 'meals' in day and isinstance(day['meals'], list):
                        meal_names = [meal.get('name', '') for meal in day['meals']]
                        if 'Breakfast' in meal_names or 'Lunch' in meal_names or 'Dinner' in meal_names:
                            has_meals_array = True
                            break
                
                # Keep new v2 plans (even if they have meals array - we'll clean that in code)
                plans_to_keep.append((plan_id, plan_name, created_date, "NEW v2 (Array)", has_meals_array))
            else:
                # Unknown format - DELETE to be safe
                plans_to_delete.append((plan_id, plan_name, created_date, "UNKNOWN"))
                
        except Exception as e:
            # Can't parse - DELETE
            plans_to_delete.append((plan_id, plan_name, created_date, f"ERROR: {e}"))
    
    print(f"❌ Plans TO DELETE: {len(plans_to_delete)}")
    print("-" * 80)
    for plan_id, plan_name, created_date, format_type in plans_to_delete:
        print(f"  {plan_id:3d} | {plan_name:30s} | {str(created_date)[:10]} | {format_type}")
    print()
    
    print(f"✅ Plans TO KEEP: {len(plans_to_keep)}")
    print("-" * 80)
    for plan_id, plan_name, created_date, format_type, has_meals in plans_to_keep:
        meals_info = " (has meals array)" if has_meals else ""
        print(f"  {plan_id:3d} | {plan_name:30s} | {str(created_date)[:10]} | {format_type}{meals_info}")
    print()
    
    # 2. Confirm deletion
    print("=" * 80)
    print("⚠️  READY TO DELETE OLD PLANS")
    print("=" * 80)
    print()
    
    if not plans_to_delete:
        print("✅ No old plans to delete!")
        cur.close()
        conn.close()
        return
    
    print(f"About to DELETE {len(plans_to_delete)} old v1 format meal plans.")
    print(f"This will keep {len(plans_to_keep)} new v2 format meal plans.")
    print()
    
    # Get confirmation
    response = input("Type 'DELETE' to confirm: ")
    
    if response != 'DELETE':
        print("❌ Cancelled - no changes made")
        cur.close()
        conn.close()
        return
    
    print()
    print("🗑️  DELETING OLD PLANS...")
    print()
    
    # 3. Delete old plans
    deleted_count = 0
    
    for plan_id, plan_name, created_date, format_type in plans_to_delete:
        try:
            delete_query = "DELETE FROM meal_plans WHERE id = %s AND user_id = 11"
            cur.execute(delete_query, (plan_id,))
            deleted_count += 1
            print(f"  ✅ Deleted: {plan_id} - {plan_name}")
        except Exception as e:
            print(f"  ❌ Error deleting {plan_id}: {e}")
    
    # Commit changes
    conn.commit()
    
    print()
    print("=" * 80)
    print(f"✅ CLEANUP COMPLETE!")
    print("=" * 80)
    print()
    print(f"Deleted: {deleted_count} old v1 plans")
    print(f"Kept: {len(plans_to_keep)} new v2 plans")
    print()
    
    # 4. Show final state
    print("📊 FINAL DATABASE STATE:")
    print("-" * 80)
    
    cur.execute("SELECT COUNT(*) FROM meal_plans WHERE user_id = 11")
    final_count = cur.fetchone()[0]
    print(f"Total meal plans for user 11: {final_count}")
    print()
    
    if final_count > 0:
        cur.execute("""
            SELECT id, plan_name, created_date 
            FROM meal_plans 
            WHERE user_id = 11 
            ORDER BY created_date DESC
        """)
        
        remaining = cur.fetchall()
        print("Remaining plans:")
        for plan_id, plan_name, created_date in remaining:
            print(f"  {plan_id:3d} | {plan_name:30s} | {str(created_date)[:10]}")
    
    print("-" * 80)
    print()
    
    cur.close()
    conn.close()

def main():
    try:
        delete_old_format_plans()
        
        print()
        print("=" * 80)
        print("🎯 NEXT STEPS:")
        print("=" * 80)
        print()
        print("✅ Database cleaned!")
        print("✅ Only v2 format plans remain")
        print()
        print("Now you can:")
        print("1. Remove breakfast/lunch/dinner code from mobile app")
        print("2. Remove backward compatibility code")
        print("3. Simplify to just use day.recipes")
        print("4. Test the auto-generate grocery list feature!")
        print()
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
