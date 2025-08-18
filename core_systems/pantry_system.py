"""
🥫 Pantry System - User Pantry Management & Recipe Matching Intelligence
========================================================================

This system manages user pantries and provides intelligent recipe matching
based on available ingredients. It calculates match percentages, suggests
recipes users can make, and generates "use it up" recommendations.

Part of the Me Hungie Pantry Intelligence System - Day 2 Implementation
"""

import psycopg2
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from enum import Enum
import os
from dotenv import load_dotenv

load_dotenv()

class PantryItemStatus(Enum):
    FRESH = "fresh"
    GOOD = "good" 
    EXPIRING_SOON = "expiring_soon"
    EXPIRED = "expired"

@dataclass
class PantryItem:
    """User pantry item with smart tracking"""
    id: Optional[int]
    user_id: int
    canonical_ingredient_id: int
    canonical_name: str
    amount: Optional[float]
    unit: Optional[str]
    expiration_date: Optional[date]
    status: PantryItemStatus
    location: Optional[str] = None  # "fridge", "pantry", "freezer", etc.
    notes: Optional[str] = None
    added_date: datetime = field(default_factory=datetime.now)
    updated_date: datetime = field(default_factory=datetime.now)

@dataclass
class RecipeMatch:
    """Recipe matched against user's pantry"""
    recipe_id: int
    recipe_title: str
    match_percentage: float
    missing_ingredients: List[Tuple[str, Optional[float], Optional[str]]]  # (name, amount, unit)
    available_ingredients: List[Tuple[str, Optional[float], Optional[str]]]
    priority_score: float  # Based on expiring ingredients
    can_make_with_substitutions: bool = False

@dataclass
class UseItUpSuggestion:
    """Suggestion for using expiring ingredients"""
    ingredient_name: str
    amount: Optional[float]
    unit: Optional[str]
    expiration_date: date
    days_until_expiry: int
    suggested_recipes: List[Tuple[int, str, float]]  # (recipe_id, title, match_percentage)

class PantrySystem:
    """
    🥫 Core pantry management system with intelligent recipe matching
    
    This system provides:
    - User pantry item management (add, update, remove, track expiration)
    - Smart recipe matching based on available ingredients
    - "Use it up" suggestions for expiring ingredients
    - Pantry statistics and insights
    - Shopping list generation based on desired recipes
    """
    
    def __init__(self):
        self.db_connection = None
    
    def _get_db_connection(self):
        """Get database connection using Railway PostgreSQL"""
        if not self.db_connection:
            try:
                db_url = os.getenv('DATABASE_URL')
                if not db_url:
                    raise Exception("DATABASE_URL environment variable required")
                
                self.db_connection = psycopg2.connect(db_url)
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                raise
        return self.db_connection
    
    # ========== PANTRY ITEM MANAGEMENT ==========
    
    def add_pantry_item(self, user_id: int, canonical_ingredient_id: int, 
                       amount: Optional[float] = None, unit: Optional[str] = None,
                       location: Optional[str] = None, notes: Optional[str] = None) -> bool:
        """
        ➕ Add an item to user's pantry
        
        Note: Expiry date functionality is hidden for simplicity.
        If the item already exists, update the amount (add to existing)
        """
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            # Check if item already exists
            cursor.execute("""
                SELECT id, amount, unit FROM user_pantry
                WHERE user_id = %s AND canonical_ingredient_id = %s
            """, (user_id, canonical_ingredient_id))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing item (add to amount if units match)
                existing_id, existing_amount, existing_unit = existing
                
                if existing_unit == unit and existing_amount is not None and amount is not None:
                    # Add to existing amount
                    new_amount = existing_amount + amount
                    cursor.execute("""
                        UPDATE user_pantry 
                        SET amount = %s, updated_date = NOW(),
                            location = COALESCE(%s, location),
                            notes = COALESCE(%s, notes)
                        WHERE id = %s
                    """, (new_amount, location, notes, existing_id))
                    print(f"✅ Updated pantry item: added {amount} {unit} (total: {new_amount} {unit})")
                else:
                    # Different units or no amounts - create separate entry
                    return self._insert_new_pantry_item(cursor, user_id, canonical_ingredient_id, 
                                                      amount, unit, location, notes)
            else:
                # Insert new item
                return self._insert_new_pantry_item(cursor, user_id, canonical_ingredient_id,
                                                  amount, unit, location, notes)
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"❌ Failed to add pantry item: {e}")
            if conn:
                conn.rollback()
            return False
    
    def _insert_new_pantry_item(self, cursor, user_id: int, canonical_ingredient_id: int,
                               amount: Optional[float], unit: Optional[str],
                               location: Optional[str], notes: Optional[str]) -> bool:
        """Insert a new pantry item (without expiry date for now)"""
        
        # Set default status to 'good' since we're not tracking expiry
        status = PantryItemStatus.GOOD
        
        cursor.execute("""
            INSERT INTO user_pantry 
            (user_id, canonical_ingredient_id, amount, unit, 
             status, location, notes, added_at, updated_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """, (user_id, canonical_ingredient_id, amount, unit, 
              status.value, location, notes))
        
        print(f"✅ Added new pantry item: {amount} {unit}")
        return True
    
    def _calculate_item_status(self, expiration_date: Optional[date]) -> PantryItemStatus:
        """Calculate item status based on expiration date"""
        if not expiration_date:
            return PantryItemStatus.GOOD
        
        today = date.today()
        days_until_expiry = (expiration_date - today).days
        
        if days_until_expiry < 0:
            return PantryItemStatus.EXPIRED
        elif days_until_expiry <= 2:
            return PantryItemStatus.EXPIRING_SOON
        elif days_until_expiry <= 7:
            return PantryItemStatus.GOOD
        else:
            return PantryItemStatus.FRESH
    
    def update_pantry_item(self, user_id: int, pantry_item_id: int, 
                          amount: Optional[float] = None, unit: Optional[str] = None,
                          location: Optional[str] = None, notes: Optional[str] = None) -> bool:
        """Update an existing pantry item (expiry functionality hidden for now)"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE user_pantry 
                SET amount = COALESCE(%s, amount),
                    unit = COALESCE(%s, unit),
                    location = COALESCE(%s, location),
                    notes = COALESCE(%s, notes),
                    updated_date = NOW()
                WHERE id = %s AND user_id = %s
            """, (amount, unit, location, notes, pantry_item_id, user_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                print(f"✅ Updated pantry item {pantry_item_id}")
                return True
            else:
                print(f"❌ Pantry item {pantry_item_id} not found or not owned by user")
                return False
                
        except Exception as e:
            print(f"❌ Failed to update pantry item: {e}")
            if conn:
                conn.rollback()
            return False
    
    def remove_pantry_item(self, user_id: int, pantry_item_id: int) -> bool:
        """Remove an item from user's pantry"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM user_pantry 
                WHERE id = %s AND user_id = %s
            """, (pantry_item_id, user_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                print(f"✅ Removed pantry item {pantry_item_id}")
                return True
            else:
                print(f"❌ Pantry item {pantry_item_id} not found or not owned by user")
                return False
                
        except Exception as e:
            print(f"❌ Failed to remove pantry item: {e}")
            if conn:
                conn.rollback()
            return False
    
    def get_user_pantry(self, user_id: int, include_expired: bool = False) -> List[PantryItem]:
        """Get all items in user's pantry (expiry functionality hidden for now)"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            # Since we're hiding expiry functionality, get all items
            cursor.execute(f"""
                SELECT up.id, up.user_id, up.canonical_ingredient_id, ci.canonical_name,
                       up.amount, up.unit, up.expiry_date, up.status, up.location,
                       up.notes, up.added_at, up.updated_date
                FROM user_pantry up
                JOIN canonical_ingredients ci ON up.canonical_ingredient_id = ci.id
                WHERE up.user_id = %s
                ORDER BY ci.canonical_name ASC
            """, (user_id,))
            
            pantry_items = []
            for row in cursor.fetchall():
                (id, user_id, canonical_id, canonical_name, amount, unit, 
                 expiry_date, status, location, notes, added_at, updated_date) = row
                
                # Default to 'good' status since we're not tracking expiry
                item_status = PantryItemStatus(status) if status else PantryItemStatus.GOOD
                
                pantry_items.append(PantryItem(
                    id=id,
                    user_id=user_id,
                    canonical_ingredient_id=canonical_id,
                    canonical_name=canonical_name,
                    amount=amount,
                    unit=unit,
                    expiration_date=None,  # Hide expiry date for now
                    status=item_status,
                    location=location,
                    notes=notes,
                    added_date=added_at,
                    updated_date=updated_date
                ))
            
            return pantry_items
            
        except Exception as e:
            print(f"❌ Failed to get user pantry: {e}")
            return []
    
    # ========== RECIPE MATCHING ==========
    
    def find_matching_recipes(self, user_id: int, min_match_percentage: float = 50.0, 
                             limit: int = 20) -> List[RecipeMatch]:
        """
        🎯 Find recipes that match user's pantry ingredients
        
        Returns recipes sorted by:
        1. Match percentage (how many ingredients user has)
        2. Priority score (using expiring ingredients)
        3. Recipe popularity/rating
        """
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            # Get user's pantry ingredients (non-expired)
            user_ingredients = self._get_user_ingredient_ids(cursor, user_id)
            
            if not user_ingredients:
                print(f"ℹ️  User {user_id} has no pantry items")
                return []
            
            # Find recipes with ingredient matches
            cursor.execute("""
                WITH recipe_ingredient_counts AS (
                    SELECT 
                        ri.recipe_id,
                        COUNT(*) as total_ingredients,
                        COUNT(CASE WHEN ri.canonical_ingredient_id = ANY(%s) THEN 1 END) as matched_ingredients
                    FROM recipe_ingredients ri
                    GROUP BY ri.recipe_id
                    HAVING COUNT(CASE WHEN ri.canonical_ingredient_id = ANY(%s) THEN 1 END) > 0
                ),
                recipe_matches AS (
                    SELECT 
                        ric.recipe_id,
                        ric.total_ingredients,
                        ric.matched_ingredients,
                        (ric.matched_ingredients::float / ric.total_ingredients * 100) as match_percentage
                    FROM recipe_ingredient_counts ric
                    WHERE (ric.matched_ingredients::float / ric.total_ingredients * 100) >= %s
                )
                SELECT 
                    rm.recipe_id,
                    r.title,
                    rm.match_percentage,
                    rm.total_ingredients,
                    rm.matched_ingredients
                FROM recipe_matches rm
                JOIN recipes r ON rm.recipe_id = r.id
                ORDER BY rm.match_percentage DESC, r.id DESC
                LIMIT %s
            """, (user_ingredients, user_ingredients, min_match_percentage, limit))
            
            recipe_matches = []
            for row in cursor.fetchall():
                recipe_id, title, match_percentage, total_ingredients, matched_ingredients = row
                
                # Get detailed ingredient breakdown
                missing_ingredients, available_ingredients = self._get_recipe_ingredient_breakdown(
                    cursor, recipe_id, user_ingredients
                )
                
                # Calculate priority score based on expiring ingredients
                priority_score = self._calculate_priority_score(cursor, user_id, recipe_id)
                
                recipe_matches.append(RecipeMatch(
                    recipe_id=recipe_id,
                    recipe_title=title,
                    match_percentage=match_percentage,
                    missing_ingredients=missing_ingredients,
                    available_ingredients=available_ingredients,
                    priority_score=priority_score
                ))
            
            # Sort by priority score (expiring ingredients) then match percentage
            recipe_matches.sort(key=lambda x: (x.priority_score, x.match_percentage), reverse=True)
            
            return recipe_matches
            
        except Exception as e:
            print(f"❌ Failed to find matching recipes: {e}")
            return []
    
    def _get_user_ingredient_ids(self, cursor, user_id: int) -> List[int]:
        """Get list of canonical ingredient IDs in user's pantry (non-expired)"""
        cursor.execute("""
            SELECT DISTINCT canonical_ingredient_id
            FROM user_pantry
            WHERE user_id = %s AND status != 'expired'
        """, (user_id,))
        
        return [row[0] for row in cursor.fetchall()]
    
    def _get_recipe_ingredient_breakdown(self, cursor, recipe_id: int, 
                                       user_ingredients: List[int]) -> Tuple[List, List]:
        """Get missing and available ingredients for a recipe"""
        
        cursor.execute("""
            SELECT ri.canonical_ingredient_id, ci.canonical_name, ri.amount_numeric, ri.unit
            FROM recipe_ingredients ri
            JOIN canonical_ingredients ci ON ri.canonical_ingredient_id = ci.id
            WHERE ri.recipe_id = %s
        """, (recipe_id,))
        
        missing_ingredients = []
        available_ingredients = []
        
        for row in cursor.fetchall():
            ingredient_id, name, amount, unit = row
            
            if ingredient_id in user_ingredients:
                available_ingredients.append((name, amount, unit))
            else:
                missing_ingredients.append((name, amount, unit))
        
        return missing_ingredients, available_ingredients
    
    def _calculate_priority_score(self, cursor, user_id: int, recipe_id: int) -> float:
        """Calculate priority score based on expiring ingredients in the recipe"""
        
        cursor.execute("""
            SELECT COUNT(*) as expiring_count
            FROM user_pantry up
            JOIN recipe_ingredients ri ON up.canonical_ingredient_id = ri.canonical_ingredient_id
            WHERE up.user_id = %s 
            AND ri.recipe_id = %s
            AND up.status IN ('expiring_soon', 'good')
            AND up.expiry_date <= NOW()::date + INTERVAL '7 days'
        """, (user_id, recipe_id))
        
        result = cursor.fetchone()
        expiring_count = result[0] if result else 0
        
        # Higher score for recipes that use expiring ingredients
        return float(expiring_count * 10)  # 10 points per expiring ingredient
    
    # ========== USE IT UP SUGGESTIONS ==========
    
    def get_use_it_up_suggestions(self, user_id: int, days_ahead: int = 7) -> List[UseItUpSuggestion]:
        """
        ⏰ Get suggestions for using ingredients that are expiring soon
        
        NOTE: This functionality is currently hidden as we're not tracking expiry dates.
        Will be re-enabled when expiry tracking is added back.
        """
        print("ℹ️  Use it up suggestions are currently disabled (expiry tracking hidden)")
        return []
    
    # ========== PANTRY STATISTICS ==========
    
    def get_pantry_statistics(self, user_id: int) -> Dict:
        """Get comprehensive pantry statistics and insights"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            # Basic counts
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_items,
                    COUNT(CASE WHEN status = 'fresh' THEN 1 END) as fresh_items,
                    COUNT(CASE WHEN status = 'good' THEN 1 END) as good_items,
                    COUNT(CASE WHEN status = 'expiring_soon' THEN 1 END) as expiring_items,
                    COUNT(CASE WHEN status = 'expired' THEN 1 END) as expired_items
                FROM user_pantry
                WHERE user_id = %s
            """, (user_id,))
            
            counts = cursor.fetchone()
            
            # Category breakdown
            cursor.execute("""
                SELECT ci.category, COUNT(*) as count
                FROM user_pantry up
                JOIN canonical_ingredients ci ON up.canonical_ingredient_id = ci.id
                WHERE up.user_id = %s AND up.status != 'expired'
                GROUP BY ci.category
                ORDER BY count DESC
            """, (user_id,))
            
            categories = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Matching recipes count
            user_ingredients = self._get_user_ingredient_ids(cursor, user_id)
            
            cursor.execute("""
                SELECT COUNT(DISTINCT recipe_id)
                FROM recipe_ingredients
                WHERE canonical_ingredient_id = ANY(%s)
            """, (user_ingredients,))
            
            possible_recipes = cursor.fetchone()[0] if user_ingredients else 0
            
            return {
                'total_items': counts[0] if counts else 0,
                'fresh_items': counts[1] if counts else 0,
                'good_items': counts[2] if counts else 0,
                'expiring_items': counts[3] if counts else 0,
                'expired_items': counts[4] if counts else 0,
                'categories': categories,
                'possible_recipes': possible_recipes,
                'pantry_completeness': len(user_ingredients) / 50 * 100 if user_ingredients else 0  # Assume 50 as "complete" pantry
            }
            
        except Exception as e:
            print(f"❌ Failed to get pantry statistics: {e}")
            return {}
    
    def update_expiration_statuses(self, user_id: Optional[int] = None):
        """
        🔄 Update item statuses based on current expiration dates
        
        Should be run periodically (daily) to keep statuses current
        """
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            # Update statuses for all users or specific user
            user_filter = "AND user_id = %s" if user_id else ""
            params = [user_id] if user_id else []
            
            cursor.execute(f"""
                UPDATE user_pantry
                SET status = CASE
                    WHEN expiration_date IS NULL THEN 'good'
                    WHEN expiration_date < NOW()::date THEN 'expired'
                    WHEN expiration_date <= NOW()::date + INTERVAL '2 days' THEN 'expiring_soon'
                    WHEN expiration_date <= NOW()::date + INTERVAL '7 days' THEN 'good'
                    ELSE 'fresh'
                END,
                updated_date = NOW()
                WHERE expiration_date IS NOT NULL {user_filter}
            """, params)
            
            updated_count = cursor.rowcount
            conn.commit()
            
            print(f"✅ Updated {updated_count} pantry item statuses")
            return updated_count
            
        except Exception as e:
            print(f"❌ Failed to update expiration statuses: {e}")
            return 0

# Convenience function for testing
def test_pantry_system():
    """Test the pantry system with sample operations"""
    
    pantry = PantrySystem()
    test_user_id = 10  # Use a real user ID from the database
    
    print("🧪 Testing Pantry System:")
    print("=" * 50)
    
    # Test adding items
    print("\n📦 Adding test pantry items...")
    pantry.add_pantry_item(test_user_id, 1, amount=2.0, unit="cups", 
                          expiration_date=date.today() + timedelta(days=5))
    pantry.add_pantry_item(test_user_id, 2, amount=1.0, unit="lb",
                          expiration_date=date.today() + timedelta(days=2))
    
    # Test getting pantry
    print("\n📋 Getting pantry items...")
    items = pantry.get_user_pantry(test_user_id)
    for item in items:
        print(f"  - {item.canonical_name}: {item.amount} {item.unit} (expires: {item.expiration_date})")
    
    # Test recipe matching
    print("\n🎯 Finding matching recipes...")
    matches = pantry.find_matching_recipes(test_user_id, min_match_percentage=25.0, limit=5)
    for match in matches:
        print(f"  - {match.recipe_title}: {match.match_percentage:.1f}% match")
    
    # Test use it up suggestions
    print("\n⏰ Getting use it up suggestions...")
    suggestions = pantry.get_use_it_up_suggestions(test_user_id)
    for suggestion in suggestions:
        print(f"  - {suggestion.ingredient_name} expires in {suggestion.days_until_expiry} days")
    
    # Test statistics
    print("\n📊 Pantry statistics...")
    stats = pantry.get_pantry_statistics(test_user_id)
    print(f"  - Total items: {stats.get('total_items', 0)}")
    print(f"  - Expiring items: {stats.get('expiring_items', 0)}")
    print(f"  - Possible recipes: {stats.get('possible_recipes', 0)}")

if __name__ == "__main__":
    test_pantry_system()
