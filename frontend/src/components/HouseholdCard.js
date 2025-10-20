import React from 'react';
import './HouseholdCard.css';

const HouseholdCard = ({ household, onManageMembers, onDelete, currentUserId }) => {
  const isOwner = household.role === 'owner';
  
  return (
    <div className="household-card">
      <div className="household-card-header">
        <div className="household-icon">🏠</div>
        <div className="household-info">
          <h3 className="household-name">{household.name}</h3>
          <div className="household-meta">
            <span className="household-role-badge" data-role={household.role}>
              {household.role === 'owner' ? '👑 Owner' : 
               household.role === 'admin' ? '⭐ Admin' : 
               '👤 Member'}
            </span>
            <span className="household-date">Created {household.createdAt}</span>
          </div>
        </div>
      </div>

      <div className="household-stats">
        <div className="stat-item">
          <span className="stat-icon">👥</span>
          <span className="stat-label">{household.members} {household.members === 1 ? 'Member' : 'Members'}</span>
        </div>
        <div className="stat-item">
          <span className="stat-icon">🛒</span>
          <span className="stat-label">{household.sharedLists || 0} Lists</span>
        </div>
        <div className="stat-item">
          <span className="stat-icon">📅</span>
          <span className="stat-label">{household.sharedPlans || 0} Plans</span>
        </div>
      </div>

      <div className="household-actions">
        <button 
          className="household-btn view-members-btn"
          onClick={() => onManageMembers(household)}
          title="View and manage members"
        >
          <span className="btn-icon">👥</span>
          <span className="btn-text">Members</span>
        </button>
        
        {isOwner && (
          <button 
            className="household-btn delete-btn"
            onClick={() => onDelete(household)}
            title="Delete household"
          >
            <span className="btn-icon">🗑️</span>
            <span className="btn-text">Delete</span>
          </button>
        )}
      </div>
    </div>
  );
};

export default HouseholdCard;
