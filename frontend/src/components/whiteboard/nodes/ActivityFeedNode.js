/**
 * Activity Feed Node
 * Moveable, resizable widget showing household activity
 */

import React, { useState, useEffect, useCallback } from 'react';
import { apiCall } from '../../../utils/api';
import { subscribeToChannel, unsubscribeFromChannel } from '../../../utils/pusher';
import './ActivityFeedNode.css';

const ActivityFeedNode = ({ data, id }) => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');

  const householdId = data.householdId;

  // Map event types to icons and colors
  const getEventIcon = (eventType) => {
    const iconMap = {
      // Recipe events
      'recipe.added': { icon: '🍳', color: '#10b981' },
      'whiteboard.recipe_added': { icon: '➕', color: '#10b981' },
      'whiteboard.recipe_removed': { icon: '➖', color: '#ef4444' },
      'whiteboard.recipe_tagged': { icon: '🏷️', color: '#8b5cf6' },
      
      // Note events
      'whiteboard.note_added': { icon: '📝', color: '#6366f1' },
      'whiteboard.note_updated': { icon: '✏️', color: '#3b82f6' },
      'whiteboard.note_deleted': { icon: '🗑️', color: '#94a3b8' },
      
      // Meal plan events
      'whiteboard.mealplan_created': { icon: '📅', color: '#f59e0b' },
      'whiteboard.mealplan_updated': { icon: '🔄', color: '#f59e0b' },
      'whiteboard.mealplan_deleted': { icon: '🗑️', color: '#94a3b8' },
      'whiteboard.recipe_added_to_mealplan': { icon: '🍽️', color: '#10b981' },
      
      // Grocery list events
      'whiteboard.grocery_created': { icon: '🛒', color: '#ec4899' },
      'whiteboard.grocery_updated': { icon: '📋', color: '#ec4899' },
      'whiteboard.grocery_deleted': { icon: '🗑️', color: '#94a3b8' },
      
      // Comment events
      'whiteboard.comment_added': { icon: '💬', color: '#3b82f6' },
      'whiteboard.comment_replied': { icon: '💭', color: '#3b82f6' },
      'whiteboard.comment_deleted': { icon: '🗑️', color: '#94a3b8' },
      'comment.added': { icon: '💬', color: '#3b82f6' },
      
      // Collaboration events
      'whiteboard.member_joined': { icon: '👋', color: '#8b5cf6' },
      'whiteboard.shared': { icon: '🔗', color: '#8b5cf6' },
      'whiteboard.created': { icon: '✨', color: '#10b981' },
      
      // Legacy events
      'recipe.commented': { icon: '💬', color: '#3b82f6' },
      'recipe.favorited': { icon: '⭐', color: '#f59e0b' },
      'whiteboard.created': { icon: '📋', color: '#8b5cf6' },
      'grocery.created': { icon: '🛒', color: '#ec4899' },
      'grocery.item_checked': { icon: '✅', color: '#10b981' },
      'mealplan.created': { icon: '📅', color: '#f59e0b' },
      'member.joined': { icon: '👋', color: '#8b5cf6' },
    };
    return iconMap[eventType] || { icon: '📌', color: '#6b7280' };
  };

  // Load household activity
  const loadActivity = useCallback(async () => {
    if (!householdId) return;

    setLoading(true);
    setError(null);

    try {
      const url = `/api/v2/activity/households/${householdId}?limit=20`;
      const response = await apiCall(url);

      if (response.success) {
        setEvents(response.events || response.data?.events || []);
      } else {
        setError(response.error || 'Failed to load activity');
      }
    } catch (err) {
      console.error('Error loading activity:', err);
      setError('Failed to load activity');
    } finally {
      setLoading(false);
    }
  }, [householdId]);

  useEffect(() => {
    loadActivity();
    
    // Subscribe to real-time activity updates via Pusher
    if (householdId) {
      const channelName = `household-${householdId}-activity`;
      console.log(`📡 Subscribing to activity channel: ${channelName}`);
      
      const channel = subscribeToChannel(channelName, {
        'new-event': (data) => {
          console.log('🔔 New activity event received:', data);
          // Reload activity to get the full event data
          loadActivity();
        }
      });

      return () => {
        unsubscribeFromChannel(channelName);
      };
    }
  }, [loadActivity, householdId]);

  // Filter events
  const filteredEvents = filter === 'all' 
    ? events 
    : events.filter(e => e.event_type.startsWith(filter));

  return (
    <div className="activity-feed-node">
      {/* Header */}
      <div className="activity-header">
        <div className="activity-title">
          <span className="activity-icon">🔔</span>
          <span>Recent Activity</span>
        </div>
        <button 
          className="refresh-button" 
          onClick={loadActivity}
          disabled={loading}
          title="Refresh"
        >
          🔄
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="activity-filters">
        {['all', 'recipe', 'comment', 'whiteboard'].map(filterType => (
          <button
            key={filterType}
            className={`filter-tab ${filter === filterType ? 'active' : ''}`}
            onClick={() => setFilter(filterType)}
          >
            {filterType === 'all' ? 'All' : filterType.charAt(0).toUpperCase() + filterType.slice(1)}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="activity-content">
        {loading && (
          <div className="activity-loading">
            <div className="loading-spinner">⏳</div>
            <p>Loading activity...</p>
          </div>
        )}

        {error && (
          <div className="activity-error">
            <p>{error}</p>
            <button onClick={loadActivity} className="retry-button">
              Retry
            </button>
          </div>
        )}

        {!loading && !error && filteredEvents.length === 0 && (
          <div className="activity-empty">
            <p>No activity yet</p>
            <p className="empty-hint">
              Household events will appear here
            </p>
          </div>
        )}

        {!loading && !error && filteredEvents.length > 0 && (
          <div className="activity-events">
            {filteredEvents.map((event, index) => {
              const { icon, color } = getEventIcon(event.event_type);
              
              return (
                <div key={event.id || index} className="activity-event">
                  <div className="event-icon" style={{ backgroundColor: `${color}20`, color: color }}>
                    {icon}
                  </div>
                  
                  <div className="event-details">
                    <div className="event-text">
                      <strong>{event.user_name || 'Someone'}</strong> {event.description || event.action || 'did something'}
                    </div>
                    <div className="event-time">
                      {event.time_ago || event.created_at}
                    </div>
                    {event.event_data?.comment_preview && (
                      <div className="event-preview">
                        "{event.event_data.comment_preview}"
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Footer - show event count */}
      {!loading && !error && filteredEvents.length > 0 && (
        <div className="activity-footer">
          Showing {filteredEvents.length} events
        </div>
      )}
    </div>
  );
};

export default ActivityFeedNode;
