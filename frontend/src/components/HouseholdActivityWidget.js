import React, { useState, useEffect, useCallback, useRef } from 'react';
import './HouseholdActivityWidget.css';
import { getApiUrl } from '../utils/api';
import { useAuth } from '../contexts/AuthContext';

/**
 * HouseholdActivityWidget
 * Draggable, collapsible activity feed widget for a specific household
 * Shows in household/whiteboard views
 */
const HouseholdActivityWidget = ({ 
    householdId, 
    householdName = 'Household',
    onClose,
    initialPosition = { x: 20, y: 100 }
}) => {
    const { token } = useAuth();
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(false);
    const [isCollapsed, setIsCollapsed] = useState(false);
    const [unreadCount, setUnreadCount] = useState(0);
    
    // Dragging state
    const [isDragging, setIsDragging] = useState(false);
    const [position, setPosition] = useState(() => {
        // Load saved position from localStorage
        const saved = localStorage.getItem(`activity-widget-pos-${householdId}`);
        return saved ? JSON.parse(saved) : initialPosition;
    });
    const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
    const widgetRef = useRef(null);

    // Load household activity
    const loadActivity = useCallback(async () => {
        if (!token || !householdId) return;

        setLoading(true);

        try {
            const response = await fetch(
                `${getApiUrl()}/api/v2/activity/households/${householdId}?limit=10`,
                {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                }
            );

            const data = await response.json();

            if (data.success) {
                setEvents(data.events || []);
                setUnreadCount(data.unread_count || 0);
            }
        } catch (err) {
            console.error('Error loading household activity:', err);
        } finally {
            setLoading(false);
        }
    }, [token, householdId]);

    // Load on mount and every 30 seconds
    useEffect(() => {
        loadActivity();
        const interval = setInterval(loadActivity, 30000);
        return () => clearInterval(interval);
    }, [loadActivity]);

    // Save position to localStorage
    useEffect(() => {
        if (householdId) {
            localStorage.setItem(
                `activity-widget-pos-${householdId}`, 
                JSON.stringify(position)
            );
        }
    }, [position, householdId]);

    // Dragging handlers
    const handleMouseDown = (e) => {
        if (e.target.closest('.widget-controls') || e.target.closest('.widget-content')) {
            return; // Don't drag when clicking controls or content
        }

        setIsDragging(true);
        const rect = widgetRef.current.getBoundingClientRect();
        setDragOffset({
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        });
        e.preventDefault();
    };

    useEffect(() => {
        if (!isDragging) return;

        const handleMouseMove = (e) => {
            setPosition({
                x: e.clientX - dragOffset.x,
                y: e.clientY - dragOffset.y
            });
        };

        const handleMouseUp = () => {
            setIsDragging(false);
        };

        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);

        return () => {
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);
        };
    }, [isDragging, dragOffset]);

    // Event icon helper
    const getEventIcon = (eventType) => {
        const iconMap = {
            'recipe.added': '🍳',
            'recipe.commented': '💬',
            'whiteboard.recipe_added': '➕',
            'whiteboard.note_added': '📝',
            'grocery.created': '🛒',
            'comment.added': '💬',
            'mealplan.created': '📅',
        };
        return iconMap[eventType] || '📌';
    };

    return (
        <div
            ref={widgetRef}
            className={`household-activity-widget ${isCollapsed ? 'collapsed' : ''} ${isDragging ? 'dragging' : ''}`}
            style={{
                position: 'fixed',
                left: `${position.x}px`,
                top: `${position.y}px`,
                zIndex: 1000
            }}
        >
            {/* Header - Draggable */}
            <div 
                className="widget-header"
                onMouseDown={handleMouseDown}
            >
                <div className="widget-title">
                    <span className="drag-handle">⋮⋮</span>
                    <span>📋 Activity</span>
                    {unreadCount > 0 && (
                        <span className="widget-badge">{unreadCount}</span>
                    )}
                </div>
                
                <div className="widget-controls">
                    <button 
                        className="widget-btn"
                        onClick={() => setIsCollapsed(!isCollapsed)}
                        title={isCollapsed ? 'Expand' : 'Collapse'}
                    >
                        {isCollapsed ? '▼' : '▲'}
                    </button>
                    <button 
                        className="widget-btn"
                        onClick={loadActivity}
                        disabled={loading}
                        title="Refresh"
                    >
                        🔄
                    </button>
                    {onClose && (
                        <button 
                            className="widget-btn close-btn"
                            onClick={onClose}
                            title="Close"
                        >
                            ✕
                        </button>
                    )}
                </div>
            </div>

            {/* Content - Only shown when expanded */}
            {!isCollapsed && (
                <div className="widget-content">
                    {loading && events.length === 0 && (
                        <div className="widget-loading">Loading...</div>
                    )}

                    {!loading && events.length === 0 && (
                        <div className="widget-empty">
                            <p>No recent activity</p>
                        </div>
                    )}

                    {events.length > 0 && (
                        <div className="widget-events">
                            {events.map(event => (
                                <div key={event.id} className="widget-event">
                                    <div className="widget-event-icon">
                                        {getEventIcon(event.event_type)}
                                    </div>
                                    <div className="widget-event-content">
                                        <div className="widget-event-text">
                                            <strong>{event.user_name}</strong>
                                            <span className="event-action">
                                                {event.description}
                                            </span>
                                        </div>
                                        <div className="widget-event-time">
                                            {event.time_ago}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {events.length >= 10 && (
                        <div className="widget-footer">
                            <button className="view-all-btn">
                                View all activity
                            </button>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default HouseholdActivityWidget;
