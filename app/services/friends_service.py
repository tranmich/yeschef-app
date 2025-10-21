"""
Friends Service
Business logic for friends and friend requests operations
"""

from typing import Dict, Any, List, Optional
import logging

from app.services.base_service import BaseService
from app.database.repositories.friends_repository import get_friends_repository
from app.database.repositories.user_repository import get_user_repository

logger = logging.getLogger(__name__)


class FriendsService(BaseService):
    """Service for friends business logic"""
    
    def __init__(self):
        super().__init__()
        self.friends_repo = get_friends_repository()
        self.user_repo = get_user_repository()
    
    # ============================================================================
    # FRIEND REQUESTS
    # ============================================================================
    
    def get_friend_requests(self, user_id: int) -> Dict[str, Any]:
        """
        Get all friend requests for user (incoming and outgoing)
        
        Args:
            user_id: User ID
        
        Returns:
            Success/error response with requests data
        """
        try:
            requests_data = self.friends_repo.get_friend_requests(user_id)
            
            incoming = requests_data.get('incoming', [])
            outgoing = requests_data.get('outgoing', [])
            
            self.log_info(f"Retrieved friend requests for user {user_id}: {len(incoming)} incoming, {len(outgoing)} outgoing")
            
            return self.success_response(
                data={
                    'requests': incoming + outgoing,  # Combined list
                    'incoming': incoming,
                    'outgoing': outgoing,
                    'incoming_count': len(incoming),
                    'outgoing_count': len(outgoing)
                }
            )
            
        except Exception as e:
            self.log_error(f"Error getting friend requests", exception=e)
            return self.error_response(f"Failed to get friend requests: {str(e)}")
    
    def send_friend_request(
        self,
        requester_id: int,
        recipient_email: str,
        message: str = None
    ) -> Dict[str, Any]:
        """
        Send friend request to user by email
        
        Args:
            requester_id: User sending the request
            recipient_email: Email of user to send request to
            message: Optional message
        
        Returns:
            Success/error response
        """
        try:
            # Validation: Check email format
            if not self.validate_email(recipient_email):
                return self.error_response("Invalid email address")
            
            # Find recipient user
            recipient = self.user_repo.find_by_email(recipient_email)
            if not recipient:
                return self.error_response(f"No user found with email: {recipient_email}", code="NOT_FOUND")
            
            recipient_id = recipient['id']
            
            # Business rule: Can't send friend request to yourself
            if requester_id == recipient_id:
                return self.error_response("You cannot send a friend request to yourself")
            
            # Business rule: Check if already friends
            if self.friends_repo.check_friendship_exists(requester_id, recipient_id):
                return self.error_response("You are already friends with this user")
            
            # Business rule: Check if request already exists
            if self.friends_repo.check_friend_request_exists(requester_id, recipient_id):
                return self.error_response("A friend request already exists between you and this user")
            
            # Send the request
            request = self.friends_repo.send_friend_request(requester_id, recipient_id, message)
            
            if request:
                self.log_info(f"Friend request sent: {requester_id} → {recipient_id}")
                return self.success_response(
                    data=request,
                    message=f"Friend request sent to {recipient['name']}"
                )
            else:
                return self.error_response("Failed to send friend request")
                
        except Exception as e:
            self.log_error(f"Error sending friend request", exception=e)
            return self.error_response(f"Failed to send friend request: {str(e)}")
    
    def accept_friend_request(
        self,
        request_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Accept a friend request
        
        Args:
            request_id: Request ID to accept
            user_id: User accepting the request (must be recipient)
        
        Returns:
            Success/error response
        """
        try:
            # Get the request
            request = self.friends_repo.get_friend_request_by_id(request_id)
            
            if not request:
                return self.error_response("Friend request not found", code="NOT_FOUND")
            
            # Authorization: Only recipient can accept
            if request['recipient_id'] != user_id:
                return self.error_response("You are not authorized to accept this request", code="UNAUTHORIZED")
            
            # Check if already accepted
            if request['status'] != 'pending':
                return self.error_response(f"This request has already been {request['status']}")
            
            # Update request status to accepted
            updated_request = self.friends_repo.update_friend_request_status(request_id, 'accepted')
            
            if not updated_request:
                return self.error_response("Failed to update request status")
            
            # Create bidirectional friendship
            friendship = self.friends_repo.create_friendship(
                request['requester_id'],
                request['recipient_id']
            )
            
            if friendship:
                self.log_info(f"Friend request accepted: {request_id}, friendship created")
                return self.success_response(
                    data={
                        'request': updated_request,
                        'friendship': friendship
                    },
                    message=f"You are now friends with {request['requester_name']}"
                )
            else:
                return self.error_response("Failed to create friendship")
                
        except Exception as e:
            self.log_error(f"Error accepting friend request", exception=e)
            return self.error_response(f"Failed to accept friend request: {str(e)}")
    
    def decline_friend_request(
        self,
        request_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Decline a friend request
        
        Args:
            request_id: Request ID to decline
            user_id: User declining the request (must be recipient)
        
        Returns:
            Success/error response
        """
        try:
            # Get the request
            request = self.friends_repo.get_friend_request_by_id(request_id)
            
            if not request:
                return self.error_response("Friend request not found", code="NOT_FOUND")
            
            # Authorization: Only recipient can decline
            if request['recipient_id'] != user_id:
                return self.error_response("You are not authorized to decline this request", code="UNAUTHORIZED")
            
            # Check if already processed
            if request['status'] != 'pending':
                return self.error_response(f"This request has already been {request['status']}")
            
            # Update request status to declined
            updated_request = self.friends_repo.update_friend_request_status(request_id, 'declined')
            
            if updated_request:
                self.log_info(f"Friend request declined: {request_id}")
                return self.success_response(
                    data=updated_request,
                    message="Friend request declined"
                )
            else:
                return self.error_response("Failed to decline request")
                
        except Exception as e:
            self.log_error(f"Error declining friend request", exception=e)
            return self.error_response(f"Failed to decline friend request: {str(e)}")
    
    # ============================================================================
    # FRIENDSHIPS
    # ============================================================================
    
    def get_friends(self, user_id: int) -> Dict[str, Any]:
        """
        Get all friends for user
        
        Args:
            user_id: User ID
        
        Returns:
            Success/error response with friends list
        """
        try:
            friends = self.friends_repo.get_user_friends(user_id)
            
            self.log_info(f"Retrieved {len(friends)} friends for user {user_id}")
            
            return self.success_response(
                data={
                    'friends': friends,
                    'count': len(friends)
                }
            )
            
        except Exception as e:
            self.log_error(f"Error getting friends", exception=e)
            return self.error_response(f"Failed to get friends: {str(e)}")
    
    def remove_friend(
        self,
        user_id: int,
        friend_id: int
    ) -> Dict[str, Any]:
        """
        Remove a friend (unfriend)
        
        Args:
            user_id: User removing the friend
            friend_id: Friend to remove
        
        Returns:
            Success/error response
        """
        try:
            # Business rule: Can't remove yourself
            if user_id == friend_id:
                return self.error_response("Invalid operation")
            
            # Check if friendship exists
            if not self.friends_repo.check_friendship_exists(user_id, friend_id):
                return self.error_response("You are not friends with this user", code="NOT_FOUND")
            
            # Remove the friendship (bidirectional)
            removed = self.friends_repo.remove_friendship(user_id, friend_id)
            
            if removed:
                self.log_info(f"Friendship removed: {user_id} ↔ {friend_id}")
                return self.success_response(message="Friend removed successfully")
            else:
                return self.error_response("Failed to remove friend")
                
        except Exception as e:
            self.log_error(f"Error removing friend", exception=e)
            return self.error_response(f"Failed to remove friend: {str(e)}")
    
    def get_friendship_status(
        self,
        user_id: int,
        other_user_id: int
    ) -> Dict[str, Any]:
        """
        Get friendship status between two users
        
        Args:
            user_id: First user ID
            other_user_id: Second user ID
        
        Returns:
            Success/error response with status
            Status values: 'friends', 'request_sent', 'request_received', 'none'
        """
        try:
            status = self.friends_repo.get_friendship_status(user_id, other_user_id)
            
            return self.success_response(
                data={
                    'user_id': user_id,
                    'other_user_id': other_user_id,
                    'status': status
                }
            )
            
        except Exception as e:
            self.log_error(f"Error getting friendship status", exception=e)
            return self.error_response(f"Failed to get friendship status: {str(e)}")


# Singleton instance
_friends_service = None

def get_friends_service() -> FriendsService:
    """Get singleton friends service instance"""
    global _friends_service
    if _friends_service is None:
        _friends_service = FriendsService()
    return _friends_service
