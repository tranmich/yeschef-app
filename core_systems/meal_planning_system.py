"""
🍽️ MEAL PLANNING SYSTEM - Core Backend Logic
==============================================

Purpose: Main meal planning functionality for Me Hungie
Created: August 11, 2025
Integration: Works with hungie.db and hungie_server.py

Features:
- Create and manage meal plans
- 7-day calendar functionality
- Meal plan persistence and loading
- Integration with recipe database
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

class MealPlanningSystem:
    """Core meal planning functionality for Me Hungie."""
    
    def __init__(self, db_path: str = 'hungie.db'):
        """Initialize meal planning system with database connection."""
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.init_database_tables()
    
    def init_database_tables(self):
        """Initialize required database tables for meal planning."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Meal plans table - stores meal plan metadata and data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS meal_plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plan_name TEXT NOT NULL,
                    week_start_date TEXT NOT NULL,
                    plan_data_json TEXT NOT NULL,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create index for better performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_meal_plans_date 
                ON meal_plans(week_start_date)
            ''')
            
            conn.commit()
            self.logger.info("Meal planning database tables initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing meal planning tables: {e}")
            raise
        finally:
            conn.close()
    
    def create_meal_plan(self, plan_name: str, week_start_date: str, meal_data: Dict) -> int:
        """
        Create a new meal plan.
        
        Args:
            plan_name: Name for the meal plan
            week_start_date: Start date of the week (YYYY-MM-DD format)
            meal_data: Dictionary containing meal assignments
            
        Returns:
            int: ID of the created meal plan
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Validate meal data structure
            if not self._validate_meal_data(meal_data):
                raise ValueError("Invalid meal data structure")
            
            # Insert meal plan
            cursor.execute('''
                INSERT INTO meal_plans (plan_name, week_start_date, plan_data_json)
                VALUES (?, ?, ?)
            ''', (plan_name, week_start_date, json.dumps(meal_data)))
            
            plan_id = cursor.lastrowid
            conn.commit()
            
            self.logger.info(f"Created meal plan '{plan_name}' with ID {plan_id}")
            return plan_id
            
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error creating meal plan: {e}")
            raise
        finally:
            conn.close()
    
    def update_meal_plan(self, plan_id: int, meal_data: Dict) -> bool:
        """
        Update an existing meal plan.
        
        Args:
            plan_id: ID of the meal plan to update
            meal_data: Updated meal data
            
        Returns:
            bool: True if update successful
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Validate meal data structure
            if not self._validate_meal_data(meal_data):
                raise ValueError("Invalid meal data structure")
            
            # Update meal plan
            cursor.execute('''
                UPDATE meal_plans 
                SET plan_data_json = ?, updated_date = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (json.dumps(meal_data), plan_id))
            
            if cursor.rowcount == 0:
                self.logger.warning(f"No meal plan found with ID {plan_id}")
                return False
            
            conn.commit()
            self.logger.info(f"Updated meal plan ID {plan_id}")
            return True
            
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error updating meal plan: {e}")
            raise
        finally:
            conn.close()
    
    def get_meal_plan(self, plan_id: int) -> Optional[Dict]:
        """
        Retrieve a specific meal plan.
        
        Args:
            plan_id: ID of the meal plan to retrieve
            
        Returns:
            Dict or None: Meal plan data if found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, plan_name, week_start_date, plan_data_json, 
                       created_date, updated_date
                FROM meal_plans 
                WHERE id = ?
            ''', (plan_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return {
                'id': row[0],
                'plan_name': row[1],
                'week_start_date': row[2],
                'meal_data': json.loads(row[3]),
                'created_date': row[4],
                'updated_date': row[5]
            }
            
        except Exception as e:
            self.logger.error(f"Error retrieving meal plan: {e}")
            raise
        finally:
            conn.close()
    
    def list_meal_plans(self, limit: int = 50) -> List[Dict]:
        """
        List all meal plans with basic information.
        
        Args:
            limit: Maximum number of plans to return
            
        Returns:
            List[Dict]: List of meal plan summaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, plan_name, week_start_date, created_date, updated_date
                FROM meal_plans 
                ORDER BY updated_date DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            
            return [
                {
                    'id': row[0],
                    'plan_name': row[1],
                    'week_start_date': row[2],
                    'created_date': row[3],
                    'updated_date': row[4]
                }
                for row in rows
            ]
            
        except Exception as e:
            self.logger.error(f"Error listing meal plans: {e}")
            raise
        finally:
            conn.close()
    
    def delete_meal_plan(self, plan_id: int) -> bool:
        """
        Delete a meal plan.
        
        Args:
            plan_id: ID of the meal plan to delete
            
        Returns:
            bool: True if deletion successful
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM meal_plans WHERE id = ?', (plan_id,))
            
            if cursor.rowcount == 0:
                self.logger.warning(f"No meal plan found with ID {plan_id}")
                return False
            
            conn.commit()
            self.logger.info(f"Deleted meal plan ID {plan_id}")
            return True
            
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error deleting meal plan: {e}")
            raise
        finally:
            conn.close()
    
    def get_recipes_from_meal_plan(self, plan_id: int) -> List[int]:
        """
        Extract all recipe IDs from a meal plan.
        
        Args:
            plan_id: ID of the meal plan
            
        Returns:
            List[int]: List of unique recipe IDs
        """
        meal_plan = self.get_meal_plan(plan_id)
        if not meal_plan:
            return []
        
        recipe_ids = set()
        meal_data = meal_plan['meal_data']
        
        # Extract recipe IDs from meal plan structure
        for day_name, day_meals in meal_data.items():
            if isinstance(day_meals, dict):
                for meal_type, recipes in day_meals.items():
                    if isinstance(recipes, list):
                        for recipe_id in recipes:
                            if isinstance(recipe_id, (int, str)):
                                try:
                                    recipe_ids.add(int(recipe_id))
                                except ValueError:
                                    continue
        
        return list(recipe_ids)
    
    def _validate_meal_data(self, meal_data: Dict) -> bool:
        """
        Validate meal data structure.
        
        Args:
            meal_data: Meal data to validate
            
        Returns:
            bool: True if valid structure
        """
        if not isinstance(meal_data, dict):
            return False
        
        # Expected structure: { day: { meal_type: [recipe_ids] } }
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        meal_types = ['breakfast', 'lunch', 'dinner', 'snacks']
        
        for day_name, day_data in meal_data.items():
            if day_name.lower() not in days:
                continue  # Allow flexible day naming
                
            if not isinstance(day_data, dict):
                return False
                
            for meal_type, recipes in day_data.items():
                if meal_type.lower() not in meal_types:
                    continue  # Allow flexible meal type naming
                    
                if not isinstance(recipes, list):
                    return False
        
        return True
    
    def create_template_meal_plan(self) -> Dict:
        """
        Create an empty meal plan template.
        
        Returns:
            Dict: Empty meal plan structure
        """
        return {
            'monday': {'breakfast': [], 'lunch': [], 'dinner': [], 'snacks': []},
            'tuesday': {'breakfast': [], 'lunch': [], 'dinner': [], 'snacks': []},
            'wednesday': {'breakfast': [], 'lunch': [], 'dinner': [], 'snacks': []},
            'thursday': {'breakfast': [], 'lunch': [], 'dinner': [], 'snacks': []},
            'friday': {'breakfast': [], 'lunch': [], 'dinner': [], 'snacks': []},
            'saturday': {'breakfast': [], 'lunch': [], 'dinner': [], 'snacks': []},
            'sunday': {'breakfast': [], 'lunch': [], 'dinner': [], 'snacks': []}
        }


# Convenience function for quick access
def get_meal_planning_system(db_path: str = 'hungie.db') -> MealPlanningSystem:
    """Get initialized meal planning system instance."""
    return MealPlanningSystem(db_path)


if __name__ == "__main__":
    # Test the meal planning system
    import sys
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Initialize system
        meal_planner = MealPlanningSystem()
        
        # Create test meal plan
        template = meal_planner.create_template_meal_plan()
        template['monday']['breakfast'] = [1, 2]  # Add some test recipe IDs
        template['monday']['lunch'] = [3]
        
        plan_id = meal_planner.create_meal_plan(
            "Test Meal Plan",
            "2025-08-11",
            template
        )
        
        print(f"✅ Created test meal plan with ID: {plan_id}")
        
        # Retrieve meal plan
        retrieved_plan = meal_planner.get_meal_plan(plan_id)
        print(f"✅ Retrieved meal plan: {retrieved_plan['plan_name']}")
        
        # List meal plans
        plans = meal_planner.list_meal_plans()
        print(f"✅ Found {len(plans)} meal plans in database")
        
        print("✅ Meal planning system test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing meal planning system: {e}")
        sys.exit(1)
