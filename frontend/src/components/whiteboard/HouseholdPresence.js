/**
 * Household Presence Component
 * Shows household members and who's currently online
 */

import React, { useState, useEffect } from 'react';
import { subscribeToHouseholdPresence, unsubscribeFromHouseholdPresence } from '../../utils/pusher';
import { apiCall } from '../../utils/api';
import './HouseholdPresence.css';

const HouseholdPresence = ({ householdId }) => {
  const [onlineMembers, setOnlineMembers] = useState([]);
  const [allMembers, setAllMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isInviting, setIsInviting] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteError, setInviteError] = useState('');
  const [inviteSuccess, setInviteSuccess] = useState('');

  // Fetch all household members
  useEffect(() => {
    const fetchMembers = async () => {
      try {
        console.log('👥 Fetching household members for:', householdId);
        const response = await apiCall(`/api/v2/households/${householdId}/members`);
        console.log('👥 Household members response:', response);
        
        if (response.success) {
          const members = response.data?.members || response.members || [];
          console.log('👥 Setting members:', members);
          setAllMembers(members);
        } else {
          console.error('❌ Failed to fetch members:', response);
        }
      } catch (error) {
        console.error('❌ Error fetching household members:', error);
      } finally {
        setLoading(false);
      }
    };

    if (householdId) {
      fetchMembers();
    }
  }, [householdId]);

  // Subscribe to presence channel
  useEffect(() => {
    if (!householdId) return;

    console.log('🔐 Subscribing to presence channel for household:', householdId);
    
    const channel = subscribeToHouseholdPresence(householdId, {
      onSubscriptionSucceeded: (members) => {
        console.log('✅ Presence subscription succeeded!');
        console.log('👥 Members count:', members.count);
        console.log('👥 Members object:', members);
        
        // Convert Pusher members object to array
        const memberList = [];
        members.each((member) => {
          console.log('👤 Member:', member);
          console.log('👤 Member info:', member.info);
          memberList.push({
            id: member.id,
            name: member.info.name,
            email: member.info.email,
            avatar_url: member.info.avatar_url
          });
        });
        console.log('👥 Online members:', memberList);
        setOnlineMembers(memberList);
      },

      onMemberAdded: (member) => {
        console.log('✅ Member came online:', member);
        setOnlineMembers(prev => {
          // Avoid duplicates
          if (prev.find(m => m.id === member.id)) {
            return prev;
          }
          return [...prev, {
            id: member.id,
            name: member.info.name,
            email: member.info.email,
            avatar_url: member.info.avatar_url
          }];
        });
      },

      onMemberRemoved: (member) => {
        console.log('❌ Member went offline:', member);
        setOnlineMembers(prev => prev.filter(m => m.id !== member.id));
      },
    });
    
    // Log any subscription errors
    channel.bind('pusher:subscription_error', (error) => {
      console.error('❌ Presence subscription error:', error);
    });

    return () => {
      unsubscribeFromHouseholdPresence(householdId);
    };
  }, [householdId]);

  const handleInviteUser = async (e) => {
    e.preventDefault();
    setInviteError('');
    setInviteSuccess('');

    if (!inviteEmail.trim()) {
      setInviteError('Please enter an email address');
      return;
    }

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(inviteEmail)) {
      setInviteError('Please enter a valid email address');
      return;
    }

    try {
      const response = await apiCall(`/api/v2/households/${householdId}/members`, {
        method: 'POST',
        body: JSON.stringify({
          email: inviteEmail.trim()
        })
      });

      if (response.success) {
        setInviteSuccess(`Invitation sent to ${inviteEmail}!`);
        setInviteEmail('');
        setIsInviting(false);
        
        // Refresh members list
        setTimeout(async () => {
          const membersResponse = await apiCall(`/api/v2/households/${householdId}/members`);
          if (membersResponse.success) {
            const members = membersResponse.data?.members || membersResponse.members || [];
            setAllMembers(members);
          }
          setInviteSuccess('');
        }, 2000);
      } else {
        setInviteError(response.error || response.message || 'Failed to send invitation');
      }
    } catch (error) {
      console.error('❌ Error inviting user:', error);
      setInviteError('Failed to send invitation. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="household-presence loading">
        <div className="presence-spinner">⏳</div>
      </div>
    );
  }

  return (
    <div className={`household-presence ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="presence-header" onClick={() => setIsCollapsed(!isCollapsed)}>
        <span className="presence-icon">👥</span>
        {!isCollapsed && <span className="presence-title">Household</span>}
        <span className="presence-count">
          {onlineMembers.length} / {allMembers.length}
        </span>
        <button className="collapse-button" title={isCollapsed ? 'Expand' : 'Collapse'}>
          {isCollapsed ? '▲' : '▼'}
        </button>
      </div>

      {!isCollapsed && (
        <>
          <div className="presence-members">
            {allMembers.map(member => {
              // Compare IDs as numbers (convert string to number if needed)
              const memberId = member.user_id || member.id;
              const isOnline = onlineMembers.some(m => {
                const onlineMemberId = typeof m.id === 'string' ? parseInt(m.id) : m.id;
                return onlineMemberId === memberId;
              });
              const displayName = member.user_name || member.name || 'Member';
              const initial = displayName.charAt(0).toUpperCase();

              return (
                <div
                  key={member.user_id || member.id}
                  className={`presence-member ${isOnline ? 'online' : 'offline'}`}
                  title={`${displayName} (${isOnline ? 'online' : 'offline'})`}
                >
                  <div className="member-avatar">
                    {member.avatar_url ? (
                      <img src={member.avatar_url} alt={displayName} />
                    ) : (
                      <span className="avatar-initial">{initial}</span>
                    )}
                    <span className={`status-dot ${isOnline ? 'online' : 'offline'}`} />
                  </div>
                  <div className="member-info">
                    <span className="member-name">{displayName}</span>
                    {isOnline && <span className="online-indicator">• Online</span>}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Invite Section */}
          <div className="presence-invite-section">
            {!isInviting ? (
              <button 
                className="invite-button"
                onClick={() => setIsInviting(true)}
                title="Invite someone to this household"
              >
                + Invite Member
              </button>
            ) : (
              <form className="invite-form" onSubmit={handleInviteUser}>
                <input
                  type="email"
                  className="invite-input"
                  placeholder="Enter email address..."
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  autoFocus
                />
                <div className="invite-actions">
                  <button type="submit" className="invite-send-btn" title="Send invitation">
                    Send
                  </button>
                  <button 
                    type="button" 
                    className="invite-cancel-btn" 
                    onClick={() => {
                      setIsInviting(false);
                      setInviteEmail('');
                      setInviteError('');
                    }}
                    title="Cancel"
                  >
                    Cancel
                  </button>
                </div>
                {inviteError && <div className="invite-error">{inviteError}</div>}
              </form>
            )}
            {inviteSuccess && <div className="invite-success">{inviteSuccess}</div>}
          </div>
        </>
      )}
    </div>
  );
};

export default HouseholdPresence;
