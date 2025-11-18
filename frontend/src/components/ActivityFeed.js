import React, { useState, useEffect, useCallback } from 'react';
import './ActivityFeed.css';
import { getApiUrl } from '../utils/api';
import { useAuth } from '../contexts/AuthContext';

/**
 * ActivityEvent Component
 * Displays a single activity event with icon, user info, and time
 */
const ActivityEvent = ({ event, onClick }) => {
    // Map event types to icons and colors
    const getEventIcon = (eventType) => {
        const iconMap = {
            'recipe.added': { icon: '🍳', color: '#10b981' },
            'recipe.commented': { icon: '💬', color: '#3b82f6' },
            'recipe.favorited': { icon: '⭐', color: '#f59e0b' },
            'whiteboard.created': { icon: '📋', color: '#8b5cf6' },
            'whiteboard.recipe_added': { icon: '➕', color: '#10b981' },
            'whiteboard.note_added': { icon: '📝', color: '#6366f1' },
            'grocery.created': { icon: '🛒', color: '#ec4899' },
            'grocery.item_checked': { icon: '✅', color: '#10b981' },
            'mealplan.created': { icon: '📅', color: '#f59e0b' },
            'comment.added': { icon: '💬', color: '#3b82f6' },
            'member.joined': { icon: '👋', color: '#8b5cf6' },
        };
        return iconMap[eventType] || { icon: '📌', color: '#6b7280' };
    };

    const { icon, color } = getEventIcon(event.event_type);

    return (
        <div 
            className={`activity-event ${onClick ? 'clickable' : ''} ${!event.is_read ? 'unread' : ''}`}
            onClick={onClick}
        >
            <div className="event-icon" style={{ backgroundColor: `${color}20`, color: color }}>
                {icon}
            </div>
            
            <div className="event-content">
                <div className="event-text">
                    <strong>{event.user_name}</strong> {event.description}
                </div>
                
                <div className="event-meta">
                    <span className="time-ago">{event.time_ago}</span>
                    {event.event_data?.whiteboard_id && (
                        <span className="whiteboard-link">
                            • Whiteboard #{event.event_data.whiteboard_id}
                        </span>
                    )}
                </div>
                
                {event.event_data?.comment_preview && (
                    <div className="event-preview">
                        "{event.event_data.comment_preview}"
                    </div>
                )}
            </div>
            
            {!event.is_read && (
                <div className="unread-indicator" />
            )}
        </div>
    );
};

/**
 * HouseholdGroup Component
 * Collapsible group of events for a single household
 */
const HouseholdGroup = ({ householdName, householdId, events, onEventClick }) => {
    const [isExpanded, setIsExpanded] = useState(true);
    const unreadCount = events.filter(e => !e.is_read).length;

    return (
        <div className="household-group">
            <div 
                className="household-header"
                onClick={() => setIsExpanded(!isExpanded)}
            >
                <div className="household-info">
                    <span className="household-icon">🏠</span>
                    <span className="household-name">{householdName}</span>
                    <span className="event-count">{events.length} updates</span>
                    {unreadCount > 0 && (
                        <span className="unread-badge">{unreadCount} new</span>
                    )}
                </div>
                <span className="expand-icon">{isExpanded ? '▼' : '▶'}</span>
            </div>
            
            {isExpanded && (
                <div className="household-events">
                    {events.map(event => (
                        <ActivityEvent 
                            key={event.id} 
                            event={event}
                            onClick={() => onEventClick && onEventClick(event)}
                        />
                    ))}
                </div>
            )}
        </div>
    );
};

/**
 * ActivityFeed Component
 * Global activity feed showing events from all user's households
 */
const ActivityFeed = ({ className = '', maxHeight = '600px' }) => {
    const { token } = useAuth();
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [unreadCount, setUnreadCount] = useState(0);
    const [filter, setFilter] = useState('all'); // 'all', 'recipe', 'comment', 'whiteboard', etc.

    // Load activity feed
    const loadActivityFeed = useCallback(async () => {
        if (!token) return;

        setLoading(true);
        setError(null);

        try {
            const url = new URL(`${getApiUrl()}/api/v2/activity/feed`);
            url.searchParams.append('limit', '50');
            
            if (filter !== 'all') {
                url.searchParams.append('event_types', filter);
            }

            const response = await fetch(url, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (data.success) {
                setEvents(data.events || []);
                setUnreadCount(data.unread_count || 0);
            } else {
                setError(data.error || 'Failed to load activity feed');
            }
        } catch (err) {
            console.error('Error loading activity feed:', err);
            setError('Network error loading activity');
        } finally {
            setLoading(false);
        }
    }, [token, filter]);

    // Load on mount and when filter changes
    useEffect(() => {
        loadActivityFeed();
    }, [loadActivityFeed]);

    // Mark event as read when clicked
    const handleEventClick = async (event) => {
        if (event.is_read) return;

        try {
            const response = await fetch(`${getApiUrl()}/api/v2/activity/mark-read`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    event_ids: [event.id]
                })
            });

            if (response.ok) {
                // Update local state
                setEvents(prev => prev.map(e => 
                    e.id === event.id ? { ...e, is_read: true } : e
                ));
                setUnreadCount(prev => Math.max(0, prev - 1));
            }
        } catch (err) {
            console.error('Error marking event as read:', err);
        }

        // Navigate to the resource if applicable
        if (event.resource_type === 'recipe' && event.reference_id) {
            // Could navigate to recipe detail page
            console.log('Navigate to recipe:', event.reference_id);
        }
    };

    // Mark all as read
    const markAllRead = async () => {
        const unreadEventIds = events.filter(e => !e.is_read).map(e => e.id);
        
        if (unreadEventIds.length === 0) return;

        try {
            const response = await fetch(`${getApiUrl()}/api/v2/activity/mark-read`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    event_ids: unreadEventIds
                })
            });

            if (response.ok) {
                setEvents(prev => prev.map(e => ({ ...e, is_read: true })));
                setUnreadCount(0);
            }
        } catch (err) {
            console.error('Error marking all as read:', err);
        }
    };

    // Group events by household
    const eventsByHousehold = events.reduce((acc, event) => {
        const key = event.household_id;
        if (!acc[key]) {
            acc[key] = {
                householdId: event.household_id,
                householdName: event.household_name,
                events: []
            };
        }
        acc[key].events.push(event);
        return acc;
    }, {});

    const householdGroups = Object.values(eventsByHousehold);

    return (
        <div className={`activity-feed ${className}`}>
            {/* Header */}
            <div className="feed-header">
                <div className="feed-title">
                    <h3>🔔 Recent Activity</h3>
                    {unreadCount > 0 && (
                        <span className="unread-badge-header">{unreadCount} new</span>
                    )}
                </div>
                
                <div className="feed-actions">
                    {unreadCount > 0 && (
                        <button 
                            className="mark-all-read-btn"
                            onClick={markAllRead}
                        >
                            Mark all read
                        </button>
                    )}
                    <button 
                        className="refresh-btn"
                        onClick={loadActivityFeed}
                        disabled={loading}
                    >
                        🔄
                    </button>
                </div>
            </div>

            {/* Filter Tabs */}
            <div className="feed-filters">
                {['all', 'recipe', 'comment', 'whiteboard', 'grocery'].map(filterType => (
                    <button
                        key={filterType}
                        className={`filter-btn ${filter === filterType ? 'active' : ''}`}
                        onClick={() => setFilter(filterType)}
                    >
                        {filterType.charAt(0).toUpperCase() + filterType.slice(1)}
                    </button>
                ))}
            </div>

            {/* Content */}
            <div className="feed-content" style={{ maxHeight }}>
                {loading && (
                    <div className="feed-loading">
                        <p>Loading activity...</p>
                    </div>
                )}

                {error && (
                    <div className="feed-error">
                        <p>{error}</p>
                        <button onClick={loadActivityFeed} className="retry-btn">
                            Retry
                        </button>
                    </div>
                )}

                {!loading && !error && events.length === 0 && (
                    <div className="feed-empty">
                        <p>No activity yet</p>
                        <p className="empty-hint">
                            Events from your households will appear here
                        </p>
                    </div>
                )}

                {!loading && !error && householdGroups.length > 0 && (
                    <div className="household-groups">
                        {householdGroups.map(group => (
                            <HouseholdGroup
                                key={group.householdId}
                                householdName={group.householdName}
                                householdId={group.householdId}
                                events={group.events}
                                onEventClick={handleEventClick}
                            />
                        ))}
                    </div>
                )}
            </div>

            {/* Footer */}
            {events.length > 0 && (
                <div className="feed-footer">
                    <p className="event-count-footer">
                        Showing {events.length} recent events
                    </p>
                </div>
            )}
        </div>
    );
};

export default ActivityFeed;
