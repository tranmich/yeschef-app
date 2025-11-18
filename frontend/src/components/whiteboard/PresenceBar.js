/**
 * Presence Bar Component
 * 
 * Shows connected users at the bottom of the whiteboard canvas
 * - Colored circles with user initials
 * - Shows current activity status
 * - "You" label for current user
 * - Fades idle users after 2 minutes
 */

import React from 'react';
import { useMyPresence, useOthers } from '../../liveblocks.config';
import './PresenceBar.css';

const PresenceBar = () => {
  const [myPresence] = useMyPresence();
  const others = useOthers();

  // Combine current user with others for display
  const allUsers = [
    { connectionId: 'me', presence: myPresence, isMe: true },
    ...others.map(other => ({
      connectionId: other.connectionId,
      presence: other.presence,
      isMe: false,
    })),
  ];

  // Filter out users without user info
  const validUsers = allUsers.filter(u => u.presence?.user);

  if (validUsers.length === 0) {
    return null; // Don't show bar if no users
  }

  return (
    <div className="presence-bar">
      <div className="presence-bar-content">
        <div className="presence-label">
          👥 {validUsers.length} {validUsers.length === 1 ? 'person' : 'people'} viewing
        </div>
        
        <div className="presence-avatars">
          {validUsers.map((user, index) => {
            const userInfo = user.presence.user;
            const activityStatus = user.presence.activityStatus || 'viewing';
            
            return (
              <div
                key={user.connectionId}
                className={`presence-avatar ${activityStatus === 'viewing' ? 'idle' : 'active'}`}
                style={{
                  backgroundColor: userInfo.color,
                  zIndex: validUsers.length - index, // Stack in order
                }}
                title={`${userInfo.name} - ${activityStatus}`}
              >
                <span className="presence-initials">{userInfo.initials}</span>
                {user.isMe && <span className="presence-you-label">You</span>}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default PresenceBar;
