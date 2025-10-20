"""
User Service
Business logic for user operations
Coordinates UserRepository and adds validation, authorization
"""

from typing import Dict, Any, Optional
import logging

from app.services.base_service import BaseService
from app.database.repositories.user_repository import get_user_repository

logger = logging.getLogger(__name__)


class UserService(BaseService):
    """Service for user business logic"""
    
    def __init__(self):
        super().__init__()
        self.user_repo = get_user_repository()
    
    # User retrieval
    
    def get_user_by_id(self, user_id: int) -> Dict[str, Any]:
        """
        Get user by ID
        
        Args:
            user_id: User ID
        
        Returns:
            Success response with user data or error response
        """
        try:
            user = self.user_repo.find_by_id(user_id)
            
            if not user:
                return self.error_response('User not found', code='NOT_FOUND')
            
            # Remove sensitive fields before returning
            safe_user = self._sanitize_user(user)
            
            return self.success_response(safe_user)
            
        except Exception as e:
            self.log_error(f"Error getting user {user_id}", exception=e)
            return self.error_response('Failed to get user')
    
    def get_user_by_email(self, email: str) -> Dict[str, Any]:
        """
        Get user by email
        
        Args:
            email: User email
        
        Returns:
            Success response with user data or error response
        """
        try:
            # Validate email format
            if not self.validate_email(email):
                return self.error_response('Invalid email format', code='INVALID_EMAIL')
            
            user = self.user_repo.find_by_email(email)
            
            if not user:
                return self.error_response('User not found', code='NOT_FOUND')
            
            safe_user = self._sanitize_user(user)
            
            return self.success_response(safe_user)
            
        except Exception as e:
            self.log_error(f"Error getting user by email {email}", exception=e)
            return self.error_response('Failed to get user')
    
    # User creation
    
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new user with validation
        
        Args:
            user_data: Dictionary with user fields (email, name, password_hash, etc.)
        
        Returns:
            Success response with created user or error response
        """
        try:
            # Validate required fields
            error = self.validate_required_fields(user_data, ['email', 'name'])
            if error:
                return self.error_response(error, code='VALIDATION_ERROR')
            
            # Validate email format
            if not self.validate_email(user_data['email']):
                return self.error_response('Invalid email format', code='INVALID_EMAIL')
            
            # Check if email already exists
            if self.user_repo.email_exists(user_data['email']):
                return self.error_response(
                    'Email already registered',
                    code='EMAIL_EXISTS'
                )
            
            # Create user
            user = self.user_repo.create(user_data)
            
            if not user:
                return self.error_response('Failed to create user')
            
            self.log_info(f"Created user: {user['email']} (ID: {user['id']})")
            
            safe_user = self._sanitize_user(user)
            
            return self.success_response(
                safe_user,
                message='User created successfully'
            )
            
        except ValueError as e:
            # Repository validation error
            return self.error_response(str(e), code='VALIDATION_ERROR')
        except Exception as e:
            self.log_error("Error creating user", exception=e)
            return self.error_response('Failed to create user')
    
    # User updates
    
    def update_user(self, user_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user information
        
        Args:
            user_id: User ID
            updates: Dictionary with fields to update
        
        Returns:
            Success response with updated user or error response
        """
        try:
            # Check if user exists
            existing = self.user_repo.find_by_id(user_id)
            if not existing:
                return self.error_response('User not found', code='NOT_FOUND')
            
            # Validate email if being updated
            if 'email' in updates and not self.validate_email(updates['email']):
                return self.error_response('Invalid email format', code='INVALID_EMAIL')
            
            # Update user
            user = self.user_repo.update(user_id, updates)
            
            if not user:
                return self.error_response('Failed to update user')
            
            self.log_info(f"Updated user: {user['email']} (ID: {user['id']})")
            
            safe_user = self._sanitize_user(user)
            
            return self.success_response(
                safe_user,
                message='User updated successfully'
            )
            
        except ValueError as e:
            return self.error_response(str(e), code='VALIDATION_ERROR')
        except Exception as e:
            self.log_error(f"Error updating user {user_id}", exception=e)
            return self.error_response('Failed to update user')
    
    def update_profile(self, user_id: int, avatar_emoji: str = None,
                      avatar_background_color: str = None) -> Dict[str, Any]:
        """
        Update user profile (avatar)
        
        Args:
            user_id: User ID
            avatar_emoji: Emoji for avatar
            avatar_background_color: Background color
        
        Returns:
            Success response with updated user or error response
        """
        try:
            user = self.user_repo.update_profile(
                user_id,
                avatar_emoji,
                avatar_background_color
            )
            
            if not user:
                return self.error_response('User not found', code='NOT_FOUND')
            
            safe_user = self._sanitize_user(user)
            
            return self.success_response(
                safe_user,
                message='Profile updated successfully'
            )
            
        except Exception as e:
            self.log_error(f"Error updating profile for user {user_id}", exception=e)
            return self.error_response('Failed to update profile')
    
    # Search
    
    def search_users(self, search_term: str, limit: int = 50) -> Dict[str, Any]:
        """
        Search users by name or email
        
        Args:
            search_term: Search term
            limit: Maximum results
        
        Returns:
            Success response with list of users
        """
        try:
            # Search by name and email
            by_name = self.user_repo.search_by_name(search_term, limit=limit)
            by_email = self.user_repo.search_by_email(search_term, limit=limit)
            
            # Combine and deduplicate by user_id
            users_dict = {}
            for user in by_name + by_email:
                if user['id'] not in users_dict:
                    users_dict[user['id']] = self._sanitize_user(user)
            
            users = list(users_dict.values())
            
            return self.success_response({
                'users': users,
                'count': len(users)
            })
            
        except Exception as e:
            self.log_error(f"Error searching users: {search_term}", exception=e)
            return self.error_response('Failed to search users')
    
    # Statistics
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Get user statistics
        
        Args:
            user_id: User ID
        
        Returns:
            Success response with statistics
        """
        try:
            user = self.user_repo.find_by_id(user_id)
            if not user:
                return self.error_response('User not found', code='NOT_FOUND')
            
            # Get recipe count
            from app.database.repositories.recipe_repository import get_recipe_repository
            recipe_repo = get_recipe_repository()
            recipe_count = recipe_repo.count_by_user(user_id)
            
            stats = {
                'user_id': user_id,
                'name': user['name'],
                'email': user['email'],
                'recipe_count': recipe_count,
                'member_since': user.get('created_at')
            }
            
            return self.success_response(stats)
            
        except Exception as e:
            self.log_error(f"Error getting user stats {user_id}", exception=e)
            return self.error_response('Failed to get user stats')
    
    # Helper methods
    
    def _sanitize_user(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove sensitive fields from user data
        
        Args:
            user: User dictionary
        
        Returns:
            Sanitized user dictionary
        """
        # Remove sensitive fields
        sensitive_fields = ['password_hash', 'password']
        
        safe_user = {k: v for k, v in user.items() if k not in sensitive_fields}
        
        return safe_user


# Global instance
_user_service: Optional[UserService] = None


def get_user_service() -> UserService:
    """Get global UserService instance"""
    global _user_service
    if _user_service is None:
        _user_service = UserService()
    return _user_service
