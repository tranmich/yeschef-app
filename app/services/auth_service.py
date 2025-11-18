"""
Authentication Service (V2)
Business logic for user authentication and authorization
Wraps the existing auth_system.py for V2 compatibility
"""

from typing import Dict, Any, Optional
import logging
import os
import re

from app.services.base_service import BaseService
from auth_system import AuthenticationSystem

logger = logging.getLogger(__name__)


class AuthService(BaseService):
    """Service for authentication business logic"""
    
    # Email validation regex (RFC 5322 simplified)
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    def __init__(self, auth_system: AuthenticationSystem = None):
        super().__init__()
        self.auth_system = auth_system
        
        if not self.auth_system:
            # This should not happen in production, but handle gracefully
            logger.warning("AuthService initialized without auth_system - features may be limited")
    
    # ===== Helper Methods =====
    
    def _is_valid_email(self, email: str) -> bool:
        """
        Validate email format
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not email or not isinstance(email, str):
            return False
        return bool(self.EMAIL_REGEX.match(email.strip()))
    
    # ===== User Registration =====
    
    def register_user(self, name: str, email: str, password: str) -> Dict[str, Any]:
        """
        Register a new user
        
        Args:
            name: User's full name
            email: User's email address
            password: User's password (plain text, will be hashed)
        
        Returns:
            Success response with user data and JWT token or error response
        """
        try:
            # Validate input
            if not name or not name.strip():
                return self.error_response('Name is required', code='VALIDATION_ERROR')
            
            if not email or not email.strip():
                return self.error_response('Email is required', code='VALIDATION_ERROR')
            
            # Validate email format
            if not self._is_valid_email(email):
                return self.error_response(
                    'Invalid email format',
                    code='VALIDATION_ERROR'
                )
            
            if not password or len(password) < 6:
                return self.error_response(
                    'Password must be at least 6 characters',
                    code='VALIDATION_ERROR'
                )
            
            # Sanitize inputs
            name = name.strip()
            email = email.strip().lower()
            
            # Use existing auth system
            result = self.auth_system.register_user(name, email, password)
            
            if result['success']:
                logger.info(f"✅ User registered: {email}")
                # Map access_token from auth_system to token for V2 API
                token = result.get('access_token') or result.get('token')
                return self.success_response(
                    data={
                        'user': result.get('user'),
                        'token': token
                    },
                    message='User registered successfully'
                )
            else:
                # Map error codes
                error_message = result.get('message', 'Registration failed')
                if 'already exists' in error_message.lower():
                    return self.error_response(error_message, code='EMAIL_EXISTS')
                else:
                    return self.error_response(error_message, code='REGISTRATION_FAILED')
        
        except Exception as e:
            logger.error(f"❌ Registration error: {e}")
            return self.error_response('Registration failed', code='SERVER_ERROR')
    
    # ===== User Login =====
    
    def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user with email and password
        
        Args:
            email: User's email address
            password: User's password
        
        Returns:
            Success response with user data and JWT token or error response
        """
        try:
            # Validate input
            if not email or not email.strip():
                return self.error_response('Email is required', code='VALIDATION_ERROR')
            
            # Validate email format
            if not self._is_valid_email(email):
                return self.error_response(
                    'Invalid email format',
                    code='VALIDATION_ERROR'
                )
            
            if not password:
                return self.error_response('Password is required', code='VALIDATION_ERROR')
            
            # Sanitize email
            email = email.strip().lower()
            
            # Use existing auth system
            result = self.auth_system.authenticate_user(email, password)
            
            if result['success']:
                logger.info(f"✅ User logged in: {email}")
                # Map access_token from auth_system to token for V2 API
                token = result.get('access_token') or result.get('token')
                return self.success_response(
                    data={
                        'user': result.get('user'),
                        'token': token
                    },
                    message='Login successful'
                )
            else:
                return self.error_response(
                    'Invalid email or password',
                    code='INVALID_CREDENTIALS'
                )
        
        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            return self.error_response('Login failed', code='SERVER_ERROR')
    
    # ===== Get Current User =====
    
    def get_current_user(self, user_id: int) -> Dict[str, Any]:
        """
        Get current user information by ID (from JWT token)
        
        Args:
            user_id: User ID from JWT token
        
        Returns:
            Success response with user data or error response
        """
        try:
            user = self.auth_system.get_user_by_id(user_id)
            
            if user:
                # Remove sensitive data
                safe_user = {
                    'id': user['id'],
                    'name': user['name'],
                    'email': user['email'],
                    'avatar_emoji': user.get('avatar_emoji'),
                    'avatar_background_color': user.get('avatar_background_color'),
                    'created_at': user.get('created_at'),
                    'is_premium': user.get('is_premium', False)
                }
                
                return self.success_response(
                    data={'user': safe_user},
                    message='User retrieved successfully'
                )
            else:
                return self.error_response('User not found', code='NOT_FOUND')
        
        except Exception as e:
            logger.error(f"❌ Get current user error: {e}")
            return self.error_response('Failed to get user', code='SERVER_ERROR')
    
    # ===== Password Reset =====
    
    def request_password_reset(self, email: str) -> Dict[str, Any]:
        """
        Request password reset (send email with reset link)
        
        Args:
            email: User's email address
        
        Returns:
            Success response
        """
        try:
            if not email or not email.strip():
                return self.error_response('Email is required', code='VALIDATION_ERROR')
            
            email = email.strip().lower()
            
            # Use existing auth system
            result = self.auth_system.request_password_reset(email)
            
            if result['success']:
                return self.success_response(
                    message='If an account exists with this email, a password reset link has been sent'
                )
            else:
                # For security, always return success even if email doesn't exist
                return self.success_response(
                    message='If an account exists with this email, a password reset link has been sent'
                )
        
        except Exception as e:
            logger.error(f"❌ Password reset request error: {e}")
            # For security, return success even on error
            return self.success_response(
                message='If an account exists with this email, a password reset link has been sent'
            )
    
    def reset_password(self, token: str, new_password: str) -> Dict[str, Any]:
        """
        Reset password using reset token
        
        Args:
            token: Password reset token
            new_password: New password
        
        Returns:
            Success response or error response
        """
        try:
            if not token:
                return self.error_response('Reset token is required', code='VALIDATION_ERROR')
            
            if not new_password or len(new_password) < 6:
                return self.error_response(
                    'Password must be at least 6 characters',
                    code='VALIDATION_ERROR'
                )
            
            # Use existing auth system
            result = self.auth_system.reset_password(token, new_password)
            
            if result['success']:
                return self.success_response(
                    message='Password reset successfully'
                )
            else:
                return self.error_response(
                    'Invalid or expired reset token',
                    code='INVALID_TOKEN'
                )
        
        except Exception as e:
            logger.error(f"❌ Password reset error: {e}")
            return self.error_response('Password reset failed', code='SERVER_ERROR')
    
    # ===== Account Deletion =====
    
    def delete_account(self, user_id: int, password: str) -> Dict[str, Any]:
        """
        Delete user account (requires password confirmation)
        
        Args:
            user_id: User ID
            password: User's password for confirmation
        
        Returns:
            Success response or error response
        """
        try:
            # Get user
            user = self.auth_system.get_user_by_id(user_id)
            if not user:
                return self.error_response('User not found', code='NOT_FOUND')
            
            # Verify password
            login_result = self.auth_system.authenticate_user(user['email'], password)
            if not login_result['success']:
                return self.error_response(
                    'Invalid password',
                    code='INVALID_CREDENTIALS'
                )
            
            # Delete account using wipe_user_data
            result = self.auth_system.wipe_user_data(user_id)
            
            if result['success']:
                logger.info(f"✅ Account deleted: {user['email']}")
                return self.success_response(
                    message='Account deleted successfully'
                )
            else:
                return self.error_response(
                    'Failed to delete account',
                    code='DELETE_FAILED'
                )
        
        except Exception as e:
            logger.error(f"❌ Account deletion error: {e}")
            return self.error_response('Failed to delete account', code='SERVER_ERROR')
    
    # ===== OAuth Methods (Future) =====
    
    def google_auth_url(self, redirect_uri: str) -> Dict[str, Any]:
        """Get Google OAuth authorization URL"""
        try:
            # This would use the existing OAuth system
            # For now, return placeholder
            return self.success_response(
                data={
                    'auth_url': 'https://accounts.google.com/o/oauth2/v2/auth',
                    'message': 'Google OAuth integration coming soon'
                },
                message='OAuth URL generated'
            )
        except Exception as e:
            logger.error(f"❌ Google auth URL error: {e}")
            return self.error_response('Failed to generate OAuth URL', code='SERVER_ERROR')
    
    def google_auth_callback(self, code: str) -> Dict[str, Any]:
        """Handle Google OAuth callback"""
        try:
            # This would use the existing OAuth system
            # For now, return placeholder
            return self.error_response('Google OAuth integration coming soon', code='NOT_IMPLEMENTED')
        except Exception as e:
            logger.error(f"❌ Google auth callback error: {e}")
            return self.error_response('OAuth callback failed', code='SERVER_ERROR')


# Singleton instance
_auth_service = None

def get_auth_service(auth_system: AuthenticationSystem = None) -> AuthService:
    """Get or create auth service instance"""
    global _auth_service
    if _auth_service is None or auth_system:
        _auth_service = AuthService(auth_system)
    return _auth_service
