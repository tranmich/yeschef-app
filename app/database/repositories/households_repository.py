"""
Households Repository
Handles all database operations for households and household members
"""

from typing import Optional, Dict, Any, List
import logging

from app.database.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class HouseholdsRepository(BaseRepository):
    """Repository for households and household_members tables"""
    
    def __init__(self):
        super().__init__('households')
    
    # ============================================================================
    # HOUSEHOLDS OPERATIONS
    # ============================================================================
    
    def get_user_households(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all households for a user
        
        Args:
            user_id: User ID
        
        Returns:
            List of household dictionaries with member counts
        """
        try:
            query = """
                SELECT 
                    h.id,
                    h.name,
                    h.description,
                    h.owner_user_id,
                    h.is_active,
                    h.created_at,
                    h.updated_at,
                    u.name as creator_name,
                    hm.role as user_role,
                    COUNT(hm2.id) as member_count
                FROM households h
                JOIN users u ON h.owner_user_id = u.id
                JOIN household_members hm ON h.id = hm.household_id
                LEFT JOIN household_members hm2 ON h.id = hm2.household_id
                WHERE hm.user_id = %s AND h.is_active = TRUE
                GROUP BY h.id, h.name, h.description, h.owner_user_id, h.is_active, 
                         h.created_at, h.updated_at, u.name, hm.role
                ORDER BY h.created_at DESC
            """
            
            households = self._execute_query(query, (user_id,))
            
            logger.info(f"✅ Got {len(households)} households for user {user_id}")
            
            return households
            
        except Exception as e:
            logger.error(f"❌ Error getting user households: {e}", exc_info=True)
            return []
    
    def get_household_by_id(self, household_id: int) -> Optional[Dict[str, Any]]:
        """
        Get household by ID with creator details
        
        Args:
            household_id: Household ID
        
        Returns:
            Household dictionary or None
        """
        try:
            query = """
                SELECT 
                    h.*,
                    u.name as creator_name,
                    u.email as creator_email,
                    COUNT(hm.id) as member_count
                FROM households h
                JOIN users u ON h.owner_user_id = u.id
                LEFT JOIN household_members hm ON h.id = hm.household_id
                WHERE h.id = %s
                GROUP BY h.id, h.name, h.description, h.owner_user_id, h.is_active,
                         h.created_at, h.updated_at, u.name, u.email
            """
            
            return self._execute_query_one(query, (household_id,))
            
        except Exception as e:
            logger.error(f"❌ Error getting household: {e}", exc_info=True)
            return None
    
    def create_household(
        self,
        name: str,
        created_by: int,
        description: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create new household
        
        Args:
            name: Household name
            created_by: User ID of creator
            description: Optional description
        
        Returns:
            Created household or None
        """
        try:
            query = """
                INSERT INTO households 
                (name, description, owner_user_id, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, TRUE, NOW(), NOW())
                RETURNING *
            """
            params = (name, description, created_by)
            
            result = self._execute_insert(query, params)
            
            if result:
                logger.info(f"✅ Created household: {name} (ID: {result['id']})")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error creating household: {e}", exc_info=True)
            return None
    
    def update_household(
        self,
        household_id: int,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update household
        
        Args:
            household_id: Household ID
            updates: Dictionary with fields to update (name, description, is_active)
        
        Returns:
            Updated household or None
        """
        try:
            # Build dynamic UPDATE query
            set_clauses = []
            params = []
            
            allowed_fields = ['name', 'description', 'is_active']
            for key, value in updates.items():
                if key in allowed_fields:
                    set_clauses.append(f"{key} = %s")
                    params.append(value)
            
            if not set_clauses:
                return None
            
            # Add updated_at
            set_clauses.append("updated_at = NOW()")
            
            # Add household_id to params
            params.append(household_id)
            
            query = f"""
                UPDATE households
                SET {', '.join(set_clauses)}
                WHERE id = %s
                RETURNING *
            """
            
            result = self._execute_update(query, tuple(params))
            
            if result:
                logger.info(f"✅ Updated household {household_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error updating household: {e}", exc_info=True)
            return None
    
    def delete_household(self, household_id: int) -> bool:
        """
        Delete household (soft delete by setting is_active = FALSE)
        
        Args:
            household_id: Household ID
        
        Returns:
            True if deleted, False otherwise
        """
        try:
            query = """
                UPDATE households
                SET is_active = FALSE, updated_at = NOW()
                WHERE id = %s
            """
            
            with self._transaction() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (household_id,))
                
                if cursor.rowcount > 0:
                    logger.info(f"✅ Deleted household {household_id}")
                    return True
                else:
                    logger.warning(f"⚠️ No household found with ID {household_id}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error deleting household: {e}", exc_info=True)
            return False
    
    # ============================================================================
    # HOUSEHOLD MEMBERS OPERATIONS
    # ============================================================================
    
    def get_household_members(self, household_id: int) -> List[Dict[str, Any]]:
        """
        Get all members of a household
        
        Args:
            household_id: Household ID
        
        Returns:
            List of member dictionaries with user details
        """
        try:
            query = """
                SELECT 
                    hm.id as membership_id,
                    hm.household_id,
                    hm.user_id,
                    hm.role,
                    hm.joined_at,
                    u.name as user_name,
                    u.email as user_email
                FROM household_members hm
                JOIN users u ON hm.user_id = u.id
                WHERE hm.household_id = %s
                ORDER BY 
                    CASE hm.role
                        WHEN 'owner' THEN 1
                        WHEN 'admin' THEN 2
                        WHEN 'member' THEN 3
                    END,
                    u.name
            """
            
            members = self._execute_query(query, (household_id,))
            
            logger.info(f"✅ Got {len(members)} members for household {household_id}")
            
            return members
            
        except Exception as e:
            logger.error(f"❌ Error getting household members: {e}", exc_info=True)
            return []
    
    def add_household_member(
        self,
        household_id: int,
        user_id: int,
        role: str = 'member'
    ) -> Optional[Dict[str, Any]]:
        """
        Add member to household
        
        Args:
            household_id: Household ID
            user_id: User ID to add
            role: Member role ('owner', 'admin', 'member')
        
        Returns:
            Created membership or None
        """
        try:
            query = """
                INSERT INTO household_members 
                (household_id, user_id, role, joined_at)
                VALUES (%s, %s, %s, NOW())
                RETURNING *
            """
            params = (household_id, user_id, role)
            
            result = self._execute_insert(query, params)
            
            if result:
                logger.info(f"✅ Added user {user_id} to household {household_id} as {role}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error adding household member: {e}", exc_info=True)
            return None
    
    def remove_household_member(self, household_id: int, user_id: int) -> bool:
        """
        Remove member from household
        
        Args:
            household_id: Household ID
            user_id: User ID to remove
        
        Returns:
            True if removed, False otherwise
        """
        try:
            query = """
                DELETE FROM household_members
                WHERE household_id = %s AND user_id = %s
            """
            
            deleted_count = self._execute_delete(query, (household_id, user_id))
            
            if deleted_count > 0:
                logger.info(f"✅ Removed user {user_id} from household {household_id}")
                return True
            else:
                logger.warning(f"⚠️ Member not found in household")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error removing household member: {e}", exc_info=True)
            return False
    
    def update_member_role(
        self,
        household_id: int,
        user_id: int,
        role: str
    ) -> Optional[Dict[str, Any]]:
        """
        Update member's role in household
        
        Args:
            household_id: Household ID
            user_id: User ID
            role: New role ('owner', 'admin', 'member')
        
        Returns:
            Updated membership or None
        """
        try:
            query = """
                UPDATE household_members
                SET role = %s
                WHERE household_id = %s AND user_id = %s
                RETURNING *
            """
            params = (role, household_id, user_id)
            
            result = self._execute_update(query, params)
            
            if result:
                logger.info(f"✅ Updated user {user_id} role to {role} in household {household_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error updating member role: {e}", exc_info=True)
            return None
    
    def check_member_exists(self, household_id: int, user_id: int) -> bool:
        """
        Check if user is a member of household
        
        Args:
            household_id: Household ID
            user_id: User ID
        
        Returns:
            True if member exists, False otherwise
        """
        query = """
            SELECT EXISTS(
                SELECT 1 FROM household_members
                WHERE household_id = %s AND user_id = %s
            ) as exists
        """
        result = self._execute_query_one(query, (household_id, user_id))
        return result['exists'] if result else False
    
    def get_member_role(self, household_id: int, user_id: int) -> Optional[str]:
        """
        Get member's role in household
        
        Args:
            household_id: Household ID
            user_id: User ID
        
        Returns:
            Role string or None
        """
        query = """
            SELECT role FROM household_members
            WHERE household_id = %s AND user_id = %s
        """
        result = self._execute_query_one(query, (household_id, user_id))
        return result['role'] if result else None
    
    def is_household_owner(self, household_id: int, user_id: int) -> bool:
        """
        Check if user is the owner of household
        
        Args:
            household_id: Household ID
            user_id: User ID
        
        Returns:
            True if user is owner, False otherwise
        """
        query = """
            SELECT EXISTS(
                SELECT 1 FROM households
                WHERE id = %s AND created_by = %s
            ) as exists
        """
        result = self._execute_query_one(query, (household_id, user_id))
        return result['exists'] if result else False


# Singleton instance
_households_repository = None

def get_households_repository() -> HouseholdsRepository:
    """Get singleton households repository instance"""
    global _households_repository
    if _households_repository is None:
        _households_repository = HouseholdsRepository()
    return _households_repository
