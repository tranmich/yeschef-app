"""
Pusher Service
Handles real-time broadcasting for comments and other features
"""

import os
import logging
from pusher import Pusher

logger = logging.getLogger(__name__)


class PusherService:
    """Service for broadcasting real-time events via Pusher"""
    
    def __init__(self):
        """Initialize Pusher client with environment variable validation"""
        # Validate required Pusher environment variables
        app_id = os.getenv('PUSHER_APP_ID')
        key = os.getenv('PUSHER_KEY')
        secret = os.getenv('PUSHER_SECRET')
        cluster = os.getenv('PUSHER_CLUSTER', 'us2')
        
        missing_vars = []
        if not app_id:
            missing_vars.append('PUSHER_APP_ID')
        if not key:
            missing_vars.append('PUSHER_KEY')
        if not secret:
            missing_vars.append('PUSHER_SECRET')
        
        if missing_vars:
            error_msg = f"Missing required Pusher environment variables: {', '.join(missing_vars)}"
            logger.error(f"❌ {error_msg}")
            raise ValueError(error_msg)
        
        self.pusher = Pusher(
            app_id=app_id,
            key=key,
            secret=secret,
            cluster=cluster,
            ssl=True
        )
        
        logger.info(f"✅ Pusher initialized - App ID: {app_id[:6]}***, Cluster: {cluster}")
    
    def broadcast_comment_created(self, whiteboard_id, comment_data):
        """
        Broadcast when a new comment is created
        
        Args:
            whiteboard_id: The whiteboard ID
            comment_data: The comment object with user info
        """
        try:
            channel = f'whiteboard-{whiteboard_id}'
            event = 'comment-created'
            
            self.pusher.trigger(channel, event, comment_data)
            logger.info(f"📡 Broadcasted comment-created to {channel}")
            
        except Exception as e:
            logger.error(f"❌ Error broadcasting comment-created: {str(e)}")
    
    def broadcast_comment_updated(self, whiteboard_id, comment_data):
        """Broadcast when a comment is updated"""
        try:
            channel = f'whiteboard-{whiteboard_id}'
            event = 'comment-updated'
            
            self.pusher.trigger(channel, event, comment_data)
            logger.info(f"📡 Broadcasted comment-updated to {channel}")
            
        except Exception as e:
            logger.error(f"❌ Error broadcasting comment-updated: {str(e)}")
    
    def broadcast_comment_deleted(self, whiteboard_id, comment_id):
        """Broadcast when a comment is deleted"""
        try:
            channel = f'whiteboard-{whiteboard_id}'
            event = 'comment-deleted'
            
            self.pusher.trigger(channel, event, {'comment_id': comment_id})
            logger.info(f"📡 Broadcasted comment-deleted to {channel}")
            
        except Exception as e:
            logger.error(f"❌ Error broadcasting comment-deleted: {str(e)}")


# Singleton instance
_pusher_service = None

def get_pusher_service():
    """Get the Pusher service singleton"""
    global _pusher_service
    if _pusher_service is None:
        _pusher_service = PusherService()
    return _pusher_service
