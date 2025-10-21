"""
Friends Repository
Handles all database operations for friend requests and friendships
"""

from typing import Optional, Dict, Any, List
import logging

from app.database.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class FriendsRepository(BaseRepository):
    """Repository for friend_requests and friendships tables"""
    
    def __init__(self):
        # Note: We'll work with two tables (friend_requests and friendships)
        super().__init__('friendships')
    
    # ============================================================================
    # FRIEND REQUESTS OPERATIONS
    # ============================================================================
    
    def get_friend_requests(self, user_id: int) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all friend requests for a user (incoming and outgoing)
        
        Args:
            user_id: User ID
        
        Returns:
            Dictionary with 'incoming' and 'outgoing' request lists
        """
        try:
            # Get incoming requests (requests sent to this user)
            incoming_query = """
                SELECT 
                    fr.id,
                    fr.requester_id,
                    fr.recipient_id,
                    fr.message,
                    fr.status,
                    fr.created_at,
                    u.name as requester_name,
                    u.email as requester_email
                FROM friend_requests fr
                JOIN users u ON fr.requester_id = u.id
                WHERE fr.recipient_id = %s AND fr.status = 'pending'
                ORDER BY fr.created_at DESC
            """
            incoming = self._execute_query(incoming_query, (user_id,))
            
            # Get outgoing requests (requests sent by this user)
            outgoing_query = """
                SELECT 
                    fr.id,
                    fr.requester_id,
                    fr.recipient_id,
                    fr.message,
                    fr.status,
                    fr.created_at,
                    u.name as recipient_name,
                    u.email as recipient_email
                FROM friend_requests fr
                JOIN users u ON fr.recipient_id = u.id
                WHERE fr.requester_id = %s AND fr.status = 'pending'
                ORDER BY fr.created_at DESC
            """
            outgoing = self._execute_query(outgoing_query, (user_id,))
            
            logger.info(f"✅ Got friend requests for user {user_id}: {len(incoming)} incoming, {len(outgoing)} outgoing")
            
            return {
                'incoming': incoming,
                'outgoing': outgoing
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting friend requests: {e}", exc_info=True)
            return {'incoming': [], 'outgoing': []}
    
    def send_friend_request(
        self,
        requester_id: int,
        recipient_id: int,
        message: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Send a friend request
        
        Args:
            requester_id: User sending the request
            recipient_id: User receiving the request
            message: Optional message
        
        Returns:
            Created friend request or None
        """
        try:
            query = """
                INSERT INTO friend_requests 
                (requester_id, recipient_id, message, status, created_at, updated_at)
                VALUES (%s, %s, %s, 'pending', NOW(), NOW())
                RETURNING *
            """
            params = (requester_id, recipient_id, message)
            
            result = self._execute_insert(query, params)
            
            if result:
                logger.info(f"✅ Friend request sent: {requester_id} → {recipient_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error sending friend request: {e}", exc_info=True)
            return None
    
    def get_friend_request_by_id(self, request_id: int) -> Optional[Dict[str, Any]]:
        """
        Get friend request by ID
        
        Args:
            request_id: Request ID
        
        Returns:
            Friend request dictionary or None
        """
        query = """
            SELECT 
                fr.*,
                u1.name as requester_name,
                u1.email as requester_email,
                u2.name as recipient_name,
                u2.email as recipient_email
            FROM friend_requests fr
            JOIN users u1 ON fr.requester_id = u1.id
            JOIN users u2 ON fr.recipient_id = u2.id
            WHERE fr.id = %s
        """
        return self._execute_query_one(query, (request_id,))
    
    def update_friend_request_status(
        self,
        request_id: int,
        status: str
    ) -> Optional[Dict[str, Any]]:
        """
        Update friend request status (accept/decline)
        
        Args:
            request_id: Request ID
            status: New status ('accepted' or 'declined')
        
        Returns:
            Updated friend request or None
        """
        try:
            query = """
                UPDATE friend_requests
                SET status = %s, updated_at = NOW()
                WHERE id = %s
                RETURNING *
            """
            params = (status, request_id)
            
            result = self._execute_update(query, params)
            
            if result:
                logger.info(f"✅ Friend request {request_id} status updated to: {status}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error updating friend request: {e}", exc_info=True)
            return None
    
    def check_friend_request_exists(
        self,
        requester_id: int,
        recipient_id: int
    ) -> bool:
        """
        Check if a friend request already exists between two users
        
        Args:
            requester_id: Requester user ID
            recipient_id: Recipient user ID
        
        Returns:
            True if request exists (either direction), False otherwise
        """
        query = """
            SELECT EXISTS(
                SELECT 1 FROM friend_requests
                WHERE (
                    (requester_id = %s AND recipient_id = %s) OR
                    (requester_id = %s AND recipient_id = %s)
                ) AND status = 'pending'
            ) as exists
        """
        result = self._execute_query_one(query, (requester_id, recipient_id, recipient_id, requester_id))
        return result['exists'] if result else False
    
    # ============================================================================
    # FRIENDSHIPS OPERATIONS
    # ============================================================================
    
    def get_user_friends(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all accepted friends for a user
        
        Args:
            user_id: User ID
        
        Returns:
            List of friend dictionaries with user details
        """
        try:
            query = """
                SELECT 
                    f.id as friendship_id,
                    f.friend_id,
                    f.status,
                    f.created_at as friend_since,
                    u.name as friend_name,
                    u.email as friend_email
                FROM friendships f
                JOIN users u ON f.friend_id = u.id
                WHERE f.user_id = %s AND f.status = 'accepted'
                ORDER BY u.name
            """
            
            friends = self._execute_query(query, (user_id,))
            
            logger.info(f"✅ Got {len(friends)} friends for user {user_id}")
            
            return friends
            
        except Exception as e:
            logger.error(f"❌ Error getting user friends: {e}", exc_info=True)
            return []
    
    def create_friendship(
        self,
        user_id: int,
        friend_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Create a friendship (called after accepting friend request)
        Creates bidirectional friendship (two rows)
        
        Args:
            user_id: First user ID
            friend_id: Second user ID
        
        Returns:
            Created friendship or None
        """
        try:
            # Create bidirectional friendship using transaction
            with self._transaction() as conn:
                cursor = conn.cursor()
                
                # Insert friendship: user → friend
                query1 = """
                    INSERT INTO friendships 
                    (user_id, friend_id, status, created_at, updated_at)
                    VALUES (%s, %s, 'accepted', NOW(), NOW())
                    RETURNING *
                """
                cursor.execute(query1, (user_id, friend_id))
                result1 = cursor.fetchone()
                
                # Insert friendship: friend → user (bidirectional)
                query2 = """
                    INSERT INTO friendships 
                    (user_id, friend_id, status, created_at, updated_at)
                    VALUES (%s, %s, 'accepted', NOW(), NOW())
                """
                cursor.execute(query2, (friend_id, user_id))
                
                logger.info(f"✅ Created bidirectional friendship: {user_id} ↔ {friend_id}")
                
                # Return the first friendship record
                return dict(result1) if result1 else None
                
        except Exception as e:
            logger.error(f"❌ Error creating friendship: {e}", exc_info=True)
            return None
    
    def remove_friendship(self, user_id: int, friend_id: int) -> bool:
        """
        Remove a friendship (bidirectional)
        
        Args:
            user_id: First user ID
            friend_id: Second user ID
        
        Returns:
            True if removed successfully, False otherwise
        """
        try:
            with self._transaction() as conn:
                cursor = conn.cursor()
                
                # Delete both directions
                query = """
                    DELETE FROM friendships
                    WHERE (user_id = %s AND friend_id = %s) 
                       OR (user_id = %s AND friend_id = %s)
                """
                cursor.execute(query, (user_id, friend_id, friend_id, user_id))
                
                deleted_count = cursor.rowcount
                
                if deleted_count > 0:
                    logger.info(f"✅ Removed friendship: {user_id} ↔ {friend_id}")
                    return True
                else:
                    logger.warning(f"⚠️ No friendship found between {user_id} and {friend_id}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error removing friendship: {e}", exc_info=True)
            return False
    
    def check_friendship_exists(self, user_id: int, friend_id: int) -> bool:
        """
        Check if a friendship exists between two users
        
        Args:
            user_id: First user ID
            friend_id: Second user ID
        
        Returns:
            True if friendship exists, False otherwise
        """
        query = """
            SELECT EXISTS(
                SELECT 1 FROM friendships
                WHERE (user_id = %s AND friend_id = %s)
                  AND status = 'accepted'
            ) as exists
        """
        result = self._execute_query_one(query, (user_id, friend_id))
        return result['exists'] if result else False
    
    def get_friendship_status(self, user_id: int, other_user_id: int) -> str:
        """
        Get friendship status between two users
        
        Args:
            user_id: First user ID
            other_user_id: Second user ID
        
        Returns:
            'friends', 'request_sent', 'request_received', 'none'
        """
        try:
            # Check if they're already friends
            if self.check_friendship_exists(user_id, other_user_id):
                return 'friends'
            
            # Check for pending friend request
            query = """
                SELECT 
                    CASE
                        WHEN requester_id = %s THEN 'request_sent'
                        WHEN recipient_id = %s THEN 'request_received'
                        ELSE 'none'
                    END as status
                FROM friend_requests
                WHERE (
                    (requester_id = %s AND recipient_id = %s) OR
                    (requester_id = %s AND recipient_id = %s)
                ) AND status = 'pending'
                LIMIT 1
            """
            result = self._execute_query_one(
                query,
                (user_id, user_id, user_id, other_user_id, other_user_id, user_id)
            )
            
            return result['status'] if result else 'none'
            
        except Exception as e:
            logger.error(f"❌ Error getting friendship status: {e}", exc_info=True)
            return 'none'


# Singleton instance
_friends_repository = None

def get_friends_repository() -> FriendsRepository:
    """Get singleton friends repository instance"""
    global _friends_repository
    if _friends_repository is None:
        _friends_repository = FriendsRepository()
    return _friends_repository
