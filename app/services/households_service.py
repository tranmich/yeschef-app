"""
Households Service
Business logic for households and household members operations
"""

from typing import Dict, Any, List, Optional
import logging

from app.services.base_service import BaseService
from app.database.repositories.households_repository import get_households_repository
from app.database.repositories.friends_repository import get_friends_repository

logger = logging.getLogger(__name__)


class HouseholdsService(BaseService):
    """Service for households business logic"""
    
    def __init__(self):
        super().__init__()
        self.households_repo = get_households_repository()
        self.friends_repo = get_friends_repository()
    
    # ============================================================================
    # HOUSEHOLDS
    # ============================================================================
    
    def get_user_households(self, user_id: int) -> Dict[str, Any]:
        """
        Get all households for user
        
        Args:
            user_id: User ID
        
        Returns:
            Success/error response with households list
        """
        try:
            households = self.households_repo.get_user_households(user_id)
            
            self.log_info(f"Retrieved {len(households)} households for user {user_id}")
            
            return self.success_response(
                data={
                    'households': households,
                    'count': len(households)
                }
            )
            
        except Exception as e:
            self.log_error(f"Error getting user households", exception=e)
            return self.error_response(f"Failed to get households: {str(e)}")
    
    def get_household(
        self,
        household_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Get household by ID with authorization check
        
        Args:
            household_id: Household ID
            user_id: User ID (for authorization)
        
        Returns:
            Success/error response with household data
        """
        try:
            household = self.households_repo.get_household_by_id(household_id)
            
            if not household:
                return self.error_response("Household not found", code="NOT_FOUND")
            
            # Authorization: Check if user is a member
            if not self.households_repo.check_member_exists(household_id, user_id):
                return self.error_response("You are not a member of this household", code="UNAUTHORIZED")
            
            # Get members
            members = self.households_repo.get_household_members(household_id)
            
            return self.success_response(
                data={
                    'household': household,
                    'members': members
                }
            )
            
        except Exception as e:
            self.log_error(f"Error getting household", exception=e)
            return self.error_response(f"Failed to get household: {str(e)}")
    
    def create_household(
        self,
        name: str,
        created_by: int,
        description: str = None
    ) -> Dict[str, Any]:
        """
        Create new household with creator as owner
        
        Args:
            name: Household name
            created_by: User ID of creator
            description: Optional description
        
        Returns:
            Success/error response with created household
        """
        try:
            # Validation
            if not name or not name.strip():
                return self.error_response("Household name is required")
            
            # Create household
            household = self.households_repo.create_household(
                name=name.strip(),
                created_by=created_by,
                description=description.strip() if description else None
            )
            
            if not household:
                return self.error_response("Failed to create household")
            
            # Add creator as owner
            membership = self.households_repo.add_household_member(
                household_id=household['id'],
                user_id=created_by,
                role='owner'
            )
            
            if membership:
                self.log_info(f"Created household: {name} (ID: {household['id']}) for user {created_by}")
                return self.success_response(
                    data={
                        'household': household,
                        'membership': membership
                    },
                    message=f"Household '{name}' created successfully"
                )
            else:
                # Rollback: delete household if membership creation failed
                self.households_repo.delete_household(household['id'])
                return self.error_response("Failed to create household membership")
                
        except Exception as e:
            self.log_error(f"Error creating household", exception=e)
            return self.error_response(f"Failed to create household: {str(e)}")
    
    def update_household(
        self,
        household_id: int,
        user_id: int,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update household with authorization check
        
        Args:
            household_id: Household ID
            user_id: User ID (must be owner or admin)
            updates: Dictionary with fields to update
        
        Returns:
            Success/error response with updated household
        """
        try:
            # Authorization: Check if user is owner or admin
            role = self.households_repo.get_member_role(household_id, user_id)
            
            if not role:
                return self.error_response("You are not a member of this household", code="UNAUTHORIZED")
            
            if role not in ['owner', 'admin']:
                return self.error_response("Only owners and admins can update household details", code="UNAUTHORIZED")
            
            # Update household
            updated = self.households_repo.update_household(household_id, updates)
            
            if updated:
                self.log_info(f"Updated household {household_id}")
                return self.success_response(
                    data=updated,
                    message="Household updated successfully"
                )
            else:
                return self.error_response("Failed to update household")
                
        except Exception as e:
            self.log_error(f"Error updating household", exception=e)
            return self.error_response(f"Failed to update household: {str(e)}")
    
    def delete_household(
        self,
        household_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Delete household (soft delete) - owner only
        
        Args:
            household_id: Household ID
            user_id: User ID (must be owner)
        
        Returns:
            Success/error response
        """
        try:
            # Authorization: Only owner can delete
            if not self.households_repo.is_household_owner(household_id, user_id):
                return self.error_response("Only the household owner can delete it", code="UNAUTHORIZED")
            
            # Delete household
            deleted = self.households_repo.delete_household(household_id)
            
            if deleted:
                self.log_info(f"Deleted household {household_id}")
                return self.success_response(message="Household deleted successfully")
            else:
                return self.error_response("Failed to delete household")
                
        except Exception as e:
            self.log_error(f"Error deleting household", exception=e)
            return self.error_response(f"Failed to delete household: {str(e)}")
    
    # ============================================================================
    # HOUSEHOLD MEMBERS
    # ============================================================================
    
    def get_household_members(
        self,
        household_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Get all members of household with authorization check
        
        Args:
            household_id: Household ID
            user_id: User ID (must be a member)
        
        Returns:
            Success/error response with members list
        """
        try:
            # Authorization: Check if user is a member
            if not self.households_repo.check_member_exists(household_id, user_id):
                return self.error_response("You are not a member of this household", code="UNAUTHORIZED")
            
            # Get members
            members = self.households_repo.get_household_members(household_id)
            
            return self.success_response(
                data={
                    'members': members,
                    'count': len(members)
                }
            )
            
        except Exception as e:
            self.log_error(f"Error getting household members", exception=e)
            return self.error_response(f"Failed to get household members: {str(e)}")
    
    def add_household_member(
        self,
        household_id: int,
        requesting_user_id: int,
        user_id_to_add: int,
        role: str = 'member'
    ) -> Dict[str, Any]:
        """
        Add member to household
        
        Args:
            household_id: Household ID
            requesting_user_id: User making the request (must be owner or admin)
            user_id_to_add: User to add to household
            role: Role for new member ('member', 'admin', 'owner')
        
        Returns:
            Success/error response with membership data
        """
        try:
            # Authorization: Check if requesting user is owner or admin
            requesting_role = self.households_repo.get_member_role(household_id, requesting_user_id)
            
            if not requesting_role:
                return self.error_response("You are not a member of this household", code="UNAUTHORIZED")
            
            if requesting_role not in ['owner', 'admin']:
                return self.error_response("Only owners and admins can add members", code="UNAUTHORIZED")
            
            # Business rule: Only owner can add other owners
            if role == 'owner' and requesting_role != 'owner':
                return self.error_response("Only the household owner can add other owners", code="UNAUTHORIZED")
            
            # Business rule: Can't add yourself (you're already a member)
            if requesting_user_id == user_id_to_add:
                return self.error_response("You are already a member of this household")
            
            # Business rule: Check if user is already a member
            if self.households_repo.check_member_exists(household_id, user_id_to_add):
                return self.error_response("User is already a member of this household")
            
            # Business rule: Can only add friends (optional - remove if not needed)
            if not self.friends_repo.check_friendship_exists(requesting_user_id, user_id_to_add):
                return self.error_response("You can only add friends to your household")
            
            # Add member
            membership = self.households_repo.add_household_member(
                household_id=household_id,
                user_id=user_id_to_add,
                role=role
            )
            
            if membership:
                self.log_info(f"Added user {user_id_to_add} to household {household_id} as {role}")
                return self.success_response(
                    data=membership,
                    message="Member added to household successfully"
                )
            else:
                return self.error_response("Failed to add member to household")
                
        except Exception as e:
            self.log_error(f"Error adding household member", exception=e)
            return self.error_response(f"Failed to add member: {str(e)}")
    
    def remove_household_member(
        self,
        household_id: int,
        requesting_user_id: int,
        user_id_to_remove: int
    ) -> Dict[str, Any]:
        """
        Remove member from household
        
        Args:
            household_id: Household ID
            requesting_user_id: User making the request
            user_id_to_remove: User to remove from household
        
        Returns:
            Success/error response
        """
        try:
            # Get roles
            requesting_role = self.households_repo.get_member_role(household_id, requesting_user_id)
            target_role = self.households_repo.get_member_role(household_id, user_id_to_remove)
            
            if not requesting_role:
                return self.error_response("You are not a member of this household", code="UNAUTHORIZED")
            
            if not target_role:
                return self.error_response("User is not a member of this household", code="NOT_FOUND")
            
            # Authorization rules:
            # 1. Owner can remove anyone
            # 2. Admin can remove members (but not owners or other admins)
            # 3. Members can remove themselves
            
            if requesting_user_id == user_id_to_remove:
                # User removing themselves (leaving household)
                if requesting_role == 'owner':
                    return self.error_response("Household owner cannot leave. Please transfer ownership or delete the household.")
                # Allow member/admin to leave
                pass
            elif requesting_role == 'owner':
                # Owner can remove anyone
                pass
            elif requesting_role == 'admin':
                # Admin can only remove regular members
                if target_role in ['owner', 'admin']:
                    return self.error_response("Admins cannot remove owners or other admins", code="UNAUTHORIZED")
            else:
                # Regular members can't remove others
                return self.error_response("You don't have permission to remove members", code="UNAUTHORIZED")
            
            # Remove member
            removed = self.households_repo.remove_household_member(household_id, user_id_to_remove)
            
            if removed:
                self.log_info(f"Removed user {user_id_to_remove} from household {household_id}")
                return self.success_response(message="Member removed from household successfully")
            else:
                return self.error_response("Failed to remove member from household")
                
        except Exception as e:
            self.log_error(f"Error removing household member", exception=e)
            return self.error_response(f"Failed to remove member: {str(e)}")
    
    def update_member_role(
        self,
        household_id: int,
        requesting_user_id: int,
        user_id_to_update: int,
        new_role: str
    ) -> Dict[str, Any]:
        """
        Update member's role in household
        
        Args:
            household_id: Household ID
            requesting_user_id: User making the request (must be owner)
            user_id_to_update: User whose role to update
            new_role: New role ('member', 'admin', 'owner')
        
        Returns:
            Success/error response with updated membership
        """
        try:
            # Authorization: Only owner can change roles
            if not self.households_repo.is_household_owner(household_id, requesting_user_id):
                return self.error_response("Only the household owner can change member roles", code="UNAUTHORIZED")
            
            # Validation: Check valid role
            if new_role not in ['member', 'admin', 'owner']:
                return self.error_response("Invalid role. Must be 'member', 'admin', or 'owner'")
            
            # Business rule: Can't change your own role
            if requesting_user_id == user_id_to_update:
                return self.error_response("You cannot change your own role")
            
            # Check if user is a member
            if not self.households_repo.check_member_exists(household_id, user_id_to_update):
                return self.error_response("User is not a member of this household", code="NOT_FOUND")
            
            # Update role
            updated = self.households_repo.update_member_role(household_id, user_id_to_update, new_role)
            
            if updated:
                self.log_info(f"Updated user {user_id_to_update} role to {new_role} in household {household_id}")
                return self.success_response(
                    data=updated,
                    message=f"Member role updated to {new_role}"
                )
            else:
                return self.error_response("Failed to update member role")
                
        except Exception as e:
            self.log_error(f"Error updating member role", exception=e)
            return self.error_response(f"Failed to update member role: {str(e)}")


# Singleton instance
_households_service = None

def get_households_service() -> HouseholdsService:
    """Get singleton households service instance"""
    global _households_service
    if _households_service is None:
        _households_service = HouseholdsService()
    return _households_service
