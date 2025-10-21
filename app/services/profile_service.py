"""
Profile Service
Business logic for user profile management
"""

from typing import Optional, Dict, Any
import logging
import base64
import os
from datetime import datetime

from app.database.repositories.profile_repository import ProfileRepository

logger = logging.getLogger(__name__)


class ProfileService:
    """Service for profile operations"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.repository = ProfileRepository()
        self._initialized = True
        
        logger.info("✅ ProfileService initialized")
    
    # ============================================================================
    # PROFILE OPERATIONS
    # ============================================================================
    
    def get_profile(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Get user profile
        
        Args:
            user_id: User ID
        
        Returns:
            Standardized response with profile
        """
        try:
            profile = self.repository.get_profile(user_id)
            
            if profile:
                return {
                    'success': True,
                    'data': profile
                }
            
            return {
                'success': False,
                'error': 'Profile not found'
            }
            
        except Exception as e:
            logger.error(f"❌ Error in get_profile: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to get profile'
            }
    
    def update_profile(
        self,
        user_id: int,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update user profile
        
        Args:
            user_id: User ID
            updates: Dictionary of fields to update
        
        Returns:
            Standardized response with updated profile
        """
        try:
            # Validate updates
            allowed_fields = ['name', 'bio', 'location', 'dietary_preferences', 'cooking_level']
            
            filtered_updates = {
                k: v for k, v in updates.items() 
                if k in allowed_fields and v is not None
            }
            
            if not filtered_updates:
                return {
                    'success': False,
                    'error': 'No valid fields to update'
                }
            
            profile = self.repository.update_profile(user_id, filtered_updates)
            
            if profile:
                return {
                    'success': True,
                    'data': profile,
                    'message': 'Profile updated successfully'
                }
            
            return {
                'success': False,
                'error': 'Failed to update profile'
            }
            
        except Exception as e:
            logger.error(f"❌ Error in update_profile: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to update profile'
            }
    
    def upload_avatar(
        self,
        user_id: int,
        avatar_data: str,
        filename: str = None
    ) -> Dict[str, Any]:
        """
        Upload user avatar (base64 encoded image)
        
        Args:
            user_id: User ID
            avatar_data: Base64 encoded image data
            filename: Optional filename
        
        Returns:
            Standardized response with avatar URL
        """
        try:
            # For now, we'll store the base64 data URL directly
            # In production, you'd upload to S3/CloudFlare/etc
            
            # Validate it's an image
            if not avatar_data.startswith('data:image/'):
                return {
                    'success': False,
                    'error': 'Invalid image data'
                }
            
            # For MVP, just store the data URL
            # TODO: Upload to cloud storage in production
            avatar_url = avatar_data[:1000]  # Truncate for demo (store first 1000 chars)
            
            profile = self.repository.update_avatar(user_id, avatar_url)
            
            if profile:
                return {
                    'success': True,
                    'data': {
                        'avatar_url': profile.get('avatar_url'),
                        'user_id': user_id
                    },
                    'message': 'Avatar uploaded successfully'
                }
            
            return {
                'success': False,
                'error': 'Failed to upload avatar'
            }
            
        except Exception as e:
            logger.error(f"❌ Error in upload_avatar: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to upload avatar'
            }
    
    def get_avatar(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Get user avatar URL
        
        Args:
            user_id: User ID
        
        Returns:
            Standardized response with avatar URL
        """
        try:
            profile = self.repository.get_profile(user_id)
            
            if profile:
                return {
                    'success': True,
                    'data': {
                        'avatar_url': profile.get('avatar_url'),
                        'user_id': user_id
                    }
                }
            
            return {
                'success': False,
                'error': 'User not found'
            }
            
        except Exception as e:
            logger.error(f"❌ Error in get_avatar: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to get avatar'
            }
    
    def delete_avatar(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Delete user avatar
        
        Args:
            user_id: User ID
        
        Returns:
            Standardized response
        """
        try:
            success = self.repository.delete_avatar(user_id)
            
            if success:
                return {
                    'success': True,
                    'message': 'Avatar deleted successfully'
                }
            
            return {
                'success': False,
                'error': 'Failed to delete avatar'
            }
            
        except Exception as e:
            logger.error(f"❌ Error in delete_avatar: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to delete avatar'
            }
    
    def get_stats(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Get profile statistics
        
        Args:
            user_id: User ID
        
        Returns:
            Standardized response with stats
        """
        try:
            stats = self.repository.get_profile_stats(user_id)
            
            return {
                'success': True,
                'data': stats
            }
            
        except Exception as e:
            logger.error(f"❌ Error in get_stats: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to get profile stats'
            }
