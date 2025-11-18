/**
 * Pusher Client Configuration
 * Handles real-time updates for comments and presence
 */

import Pusher from 'pusher-js';
import { apiCall } from './api';

// Get Pusher key from environment
const PUSHER_KEY = process.env.REACT_APP_PUSHER_KEY || '60bca4fc1079dbf0900d';
const PUSHER_CLUSTER = process.env.REACT_APP_PUSHER_CLUSTER || 'us2';
const API_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000';

// Enable logging BEFORE creating instance
Pusher.logToConsole = true;

// Create Pusher instance with auth endpoint
const pusher = new Pusher(PUSHER_KEY, {
  cluster: PUSHER_CLUSTER,
  encrypted: true,
  authorizer: (channel, options) => {
    return {
      authorize: (socketId, callback) => {
        const token = localStorage.getItem('authToken'); // Changed from 'access_token' to 'authToken'
        
        console.log('🔐 Authorizing channel:', channel.name, 'with socket:', socketId);
        console.log('🔐 Token found:', token ? `Yes (${token.substring(0, 20)}...)` : 'No');
        
        fetch(`${API_URL}/api/v2/pusher/auth`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': `Bearer ${token}`
          },
          body: `socket_id=${socketId}&channel_name=${channel.name}`
        })
        .then(res => {
          console.log('🔐 Auth response status:', res.status);
          return res.json();
        })
        .then(data => {
          console.log('✅ Auth successful:', data);
          callback(null, data);
        })
        .catch(err => {
          console.error('❌ Auth error:', err);
          callback(err, null);
        });
      }
    };
  }
});

// Already enabled above - remove duplicate
// Enable logging in development
// if (process.env.NODE_ENV === 'development') {
//   Pusher.logToConsole = true;
// }

/**
 * Subscribe to a whiteboard channel for real-time updates
 * @param {number} whiteboardId - The whiteboard ID
 * @param {object} callbacks - Event callbacks
 * @returns {object} - The subscribed channel
 */
export function subscribeToWhiteboard(whiteboardId, callbacks = {}) {
  const channelName = `whiteboard-${whiteboardId}`;
  const channel = pusher.subscribe(channelName);
  
  console.log(`📡 Subscribed to channel: ${channelName}`);
  
  // Comment events
  if (callbacks.onCommentCreated) {
    channel.bind('comment-created', callbacks.onCommentCreated);
  }
  
  if (callbacks.onCommentUpdated) {
    channel.bind('comment-updated', callbacks.onCommentUpdated);
  }
  
  if (callbacks.onCommentDeleted) {
    channel.bind('comment-deleted', callbacks.onCommentDeleted);
  }
  
  return channel;
}

/**
 * Unsubscribe from a whiteboard channel
 * @param {number} whiteboardId - The whiteboard ID
 */
export function unsubscribeFromWhiteboard(whiteboardId) {
  const channelName = `whiteboard-${whiteboardId}`;
  pusher.unsubscribe(channelName);
  console.log(`📡 Unsubscribed from channel: ${channelName}`);
}

/**
 * Subscribe to a presence channel for a household
 * @param {number} householdId - The household ID
 * @param {object} callbacks - Event callbacks
 * @returns {object} - The subscribed presence channel
 */
export function subscribeToHouseholdPresence(householdId, callbacks = {}) {
  const channelName = `presence-household-${householdId}`;
  const channel = pusher.subscribe(channelName);
  
  console.log(`👥 Subscribed to presence channel: ${channelName}`);
  
  // Member events
  if (callbacks.onMemberAdded) {
    channel.bind('pusher:member_added', callbacks.onMemberAdded);
  }
  
  if (callbacks.onMemberRemoved) {
    channel.bind('pusher:member_removed', callbacks.onMemberRemoved);
  }
  
  if (callbacks.onSubscriptionSucceeded) {
    channel.bind('pusher:subscription_succeeded', callbacks.onSubscriptionSucceeded);
  }
  
  return channel;
}

/**
 * Unsubscribe from a household presence channel
 * @param {number} householdId - The household ID
 */
export function unsubscribeFromHouseholdPresence(householdId) {
  const channelName = `presence-household-${householdId}`;
  pusher.unsubscribe(channelName);
  console.log(`👥 Unsubscribed from presence channel: ${channelName}`);
}

/**
 * Generic subscribe to any channel
 * @param {string} channelName - The channel name
 * @param {object} events - Event name to callback mapping
 * @returns {object} - The subscribed channel
 */
export function subscribeToChannel(channelName, events = {}) {
  const channel = pusher.subscribe(channelName);
  
  console.log(`📡 Subscribed to channel: ${channelName}`);
  
  // Bind all event callbacks
  Object.entries(events).forEach(([eventName, callback]) => {
    if (callback && typeof callback === 'function') {
      channel.bind(eventName, callback);
    }
  });
  
  return channel;
}

/**
 * Generic unsubscribe from any channel
 * @param {string} channelName - The channel name
 */
export function unsubscribeFromChannel(channelName) {
  pusher.unsubscribe(channelName);
  console.log(`📡 Unsubscribed from channel: ${channelName}`);
}

export default pusher;
