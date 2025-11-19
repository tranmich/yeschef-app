"""
Event Logger Utility
====================
Centralized system for logging household activity events and broadcasting notifications

Usage:
    from app.utils.event_logger import EventLogger
    
    EventLogger.log_event(
        household_id=11,
        user_id=23,
        event_type='recipe.added',
        resource_type='recipe',
        resource_id=2609,
        event_data={
            'recipe_title': 'Garlic Chicken',
            'recipe_image': 'url...'
        }
    )
"""

import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class EventLogger:
    """Centralized event logging for household activity feed"""
    
    # Event type constants
    EVENT_TYPES = {
        # Recipe events
        'recipe.added': 'added a recipe',
        'recipe.updated': 'updated a recipe',
        'recipe.commented': 'commented on',
        'recipe.favorited': 'favorited',
        
        # Whiteboard events
        'whiteboard.created': 'created a whiteboard',
        'whiteboard.updated': 'updated a whiteboard',
        'whiteboard.recipe_added': 'added a recipe to',
        'whiteboard.recipe_removed': 'removed a recipe from',
        'whiteboard.recipe_tagged': 'tagged a recipe in',
        'whiteboard.note_added': 'added a note to',
        'whiteboard.note_updated': 'updated a note in',
        'whiteboard.note_deleted': 'deleted a note from',
        'whiteboard.mealplan_created': 'created a meal plan in',
        'whiteboard.mealplan_updated': 'updated a meal plan in',
        'whiteboard.mealplan_deleted': 'deleted a meal plan from',
        'whiteboard.recipe_added_to_mealplan': 'added a recipe to a meal plan in',
        'whiteboard.grocery_created': 'created a grocery list in',
        'whiteboard.grocery_updated': 'updated a grocery list in',
        'whiteboard.grocery_deleted': 'deleted a grocery list from',
        'whiteboard.comment_added': 'commented on',
        'whiteboard.comment_replied': 'replied to a comment in',
        'whiteboard.comment_deleted': 'deleted a comment from',
        'whiteboard.member_joined': 'joined',
        'whiteboard.shared': 'shared',
        'whiteboard.deleted': 'deleted a whiteboard',
        
        # Grocery list events
        'grocery.created': 'created a grocery list',
        'grocery.updated': 'updated a grocery list',
        'grocery.item_checked': 'checked off items in',
        'grocery.completed': 'completed',
        
        # Meal plan events
        'mealplan.created': 'created a meal plan',
        'mealplan.updated': 'updated a meal plan',
        'mealplan.recipe_added': 'added a recipe to',
        
        # Comment events
        'comment.added': 'commented on',
        'comment.reaction': 'reacted to',
        
        # Member events
        'member.joined': 'joined the household',
        'member.left': 'left the household',
    }
    
    @staticmethod
    def log_event(
        household_id: int,
        user_id: int,
        event_type: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        event_data: Optional[Dict[str, Any]] = None,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> Optional[int]:
        """
        Log an activity event to the database
        
        Args:
            household_id: ID of the household where event occurred
            user_id: ID of user who performed the action
            event_type: Type of event (e.g., 'recipe.added', 'comment.added')
            resource_type: Type of resource (e.g., 'recipe', 'whiteboard', 'grocery_list')
            resource_id: ID of the resource
            event_data: Additional metadata as JSONB (titles, previews, images, etc.)
            title: Human-readable title (auto-generated if not provided)
            description: Human-readable description (auto-generated if not provided)
        
        Returns:
            Event ID if successful, None otherwise
        """
        try:
            from app.database.connection import get_db_connection
            import psycopg2.extras
            
            conn = get_db_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            # Auto-generate title if not provided
            if not title and event_data:
                title = event_data.get('resource_title') or event_data.get('title')
            
            # Auto-generate description if not provided
            if not description and event_type in EventLogger.EVENT_TYPES:
                action = EventLogger.EVENT_TYPES[event_type]
                resource_name = title or f"{resource_type} #{resource_id}"
                description = f"{action} {resource_name}"
            
            # Insert event
            cur.execute("""
                INSERT INTO activity_feed 
                (household_id, user_id, event_type, resource_type, reference_id, 
                 title, description, event_data, created_at, is_read)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb, NOW(), FALSE)
                RETURNING id, created_at
            """, (
                household_id, 
                user_id, 
                event_type, 
                resource_type, 
                resource_id,
                title,
                description,
                json.dumps(event_data) if event_data else None
            ))
            
            result = cur.fetchone()
            event_id = result['id']
            created_at = result['created_at']
            
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info(
                f"Event logged: {event_type} | household={household_id} | "
                f"user={user_id} | resource={resource_type}:{resource_id} | event_id={event_id}"
            )
            
            # Broadcast real-time notification via Pusher (if available)
            try:
                EventLogger._broadcast_event(
                    household_id=household_id,
                    event_id=event_id,
                    event_type=event_type,
                    user_id=user_id,
                    event_data=event_data,
                    created_at=created_at.isoformat() if created_at else None
                )
            except Exception as e:
                logger.warning(f"Failed to broadcast event via Pusher: {e}")
            
            return event_id
            
        except Exception as e:
            logger.error(f"Failed to log event: {e}", exc_info=True)
            return None
    
    @staticmethod
    def _broadcast_event(
        household_id: int,
        event_id: int,
        event_type: str,
        user_id: int,
        event_data: Optional[Dict],
        created_at: Optional[str]
    ):
        """
        Broadcast event via Pusher for real-time updates
        
        Args:
            household_id: Household ID
            event_id: Event ID
            event_type: Event type
            user_id: User who performed action
            event_data: Event metadata
            created_at: ISO timestamp
        """
        try:
            import os
            import pusher
            
            # Initialize Pusher client
            pusher_app_id = os.getenv('PUSHER_APP_ID')
            pusher_key = os.getenv('PUSHER_KEY')
            pusher_secret = os.getenv('PUSHER_SECRET')
            pusher_cluster = os.getenv('PUSHER_CLUSTER', 'us2')
            
            if not all([pusher_app_id, pusher_key, pusher_secret]):
                logger.debug("Pusher not configured, skipping broadcast")
                return
            
            pusher_client = pusher.Pusher(
                app_id=pusher_app_id,
                key=pusher_key,
                secret=pusher_secret,
                cluster=pusher_cluster,
                ssl=True
            )
            
            # Broadcast to household activity channel
            channel = f'household-{household_id}-activity'
            event = 'new-event'
            data = {
                'id': event_id,
                'event_type': event_type,
                'user_id': user_id,
                'event_data': event_data,
                'created_at': created_at
            }
            
            pusher_client.trigger(channel, event, data)
            logger.debug(f"Event broadcast to {channel}: {event_type}")
            
        except ImportError:
            logger.debug("Pusher library not installed, skipping broadcast")
        except Exception as e:
            logger.warning(f"Pusher broadcast failed: {e}")
    
    @staticmethod
    def mark_events_read(event_ids: list, user_id: int) -> int:
        """
        Mark events as read for a user
        
        Args:
            event_ids: List of event IDs to mark as read
            user_id: User ID (for verification)
        
        Returns:
            Number of events marked as read
        """
        try:
            from app.database.connection import get_db_connection
            
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute("""
                UPDATE activity_feed
                SET is_read = TRUE
                WHERE id = ANY(%s)
                RETURNING id
            """, (event_ids,))
            
            count = cur.rowcount
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info(f"Marked {count} events as read for user {user_id}")
            return count
            
        except Exception as e:
            logger.error(f"Failed to mark events as read: {e}")
            return 0
