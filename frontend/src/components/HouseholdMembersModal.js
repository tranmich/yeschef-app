import React, { useState, useEffect } from 'react';
import * as householdAPI from '../utils/householdAPI';
import './HouseholdMembersModal.css';

const HouseholdMembersModal = ({ isOpen, onClose, household, currentUserId }) => {
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    if (isOpen && household) {
      loadMembers();
    }
  }, [isOpen, household]);

  const loadMembers = async () => {
    setLoading(true);
    setError('');
    
    try {
      const result = await householdAPI.getHouseholdMembers(household.id);
      
      if (result.success) {
        setMembers(result.members || []);
      } else {
        setError(result.error || 'Failed to load members');
      }
    } catch (err) {
      setError('An error occurred');
      console.error('Load members error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveMember = async (member) => {
    const confirmRemove = window.confirm(
      `Remove ${member.name} from "${household.name}"?`
    );
    
    if (!confirmRemove) return;

    const result = await householdAPI.removeHouseholdMember(household.id, member.id);
    
    if (result.success) {
      showSuccess(`${member.name} removed from household`);
      loadMembers(); // Reload list
    } else {
      alert(`Failed to remove member: ${result.error}`);
    }
  };

  const showSuccess = (message) => {
    setSuccessMessage(message);
    setTimeout(() => setSuccessMessage(''), 3000);
  };

  const isOwner = household?.role === 'owner';
  const isAdmin = household?.role === 'admin';
  const canManage = isOwner || isAdmin;

  if (!isOpen || !household) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content members-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <h2>👥 {household.name}</h2>
            <p className="modal-subtitle">Manage household members</p>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            ✕
          </button>
        </div>

        {successMessage && (
          <div className="success-message-small">
            ✅ {successMessage}
          </div>
        )}

        {error && (
          <div className="error-message">
            ⚠️ {error}
          </div>
        )}

        {loading ? (
          <div className="loading-container">
            <div className="loading-spinner-small"></div>
            <p>Loading members...</p>
          </div>
        ) : (
          <>
            <div className="members-list">
              {members.length === 0 ? (
                <div className="no-members">
                  <p>No members yet</p>
                </div>
              ) : (
                members.map((member) => {
                  const isCurrentUser = member.id === currentUserId;
                  const isMemberOwner = member.role === 'owner';
                  const canRemove = canManage && !isMemberOwner && !isCurrentUser;

                  return (
                    <div key={member.id} className="member-item">
                      <div className="member-info">
                        <div className="member-avatar">
                          {member.name?.charAt(0).toUpperCase() || '?'}
                        </div>
                        <div className="member-details">
                          <div className="member-name">
                            {member.name}
                            {isCurrentUser && <span className="you-badge">You</span>}
                          </div>
                          <div className="member-email">{member.email}</div>
                        </div>
                      </div>
                      <div className="member-actions">
                        <span className={`role-badge role-${member.role}`}>
                          {member.role === 'owner' ? '👑 Owner' :
                           member.role === 'admin' ? '⭐ Admin' :
                           '👤 Member'}
                        </span>
                        {canRemove && (
                          <button
                            className="remove-member-btn"
                            onClick={() => handleRemoveMember(member)}
                            title="Remove member"
                          >
                            🗑️
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })
              )}
            </div>

            {canManage && (
              <div className="members-footer">
                <p className="footer-hint">
                  💡 You can add friends to this household from the Community section
                </p>
              </div>
            )}
          </>
        )}

        <div className="modal-actions">
          <button className="close-btn" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default HouseholdMembersModal;
