import React, { useState, useEffect } from 'react';
import FriendsAPI from '../services/FriendsAPI';
import SharedGroceryList from './SharedGroceryList';
import SharedMealPlanner from './SharedMealPlanner';
import RecipeSharing from './RecipeSharing';
// import PremiumFeatures from './PremiumFeatures'; // Commented out for now
import './FriendsView.css';

const FriendsView = () => {
  // State management
  const [activeTab, setActiveTab] = useState('friends');
  const [loading, setLoading] = useState(true);
  const [friends, setFriends] = useState([]);
  const [requests, setRequests] = useState([]);
  const [households, setHouseholds] = useState([]);
  
  // Modal states
  const [showAddFriendModal, setShowAddFriendModal] = useState(false);
  const [showCreateHouseholdModal, setShowCreateHouseholdModal] = useState(false);
  const [showHouseholdDetailsModal, setShowHouseholdDetailsModal] = useState(false);
  const [showAddMemberModal, setShowAddMemberModal] = useState(false);
  const [showGroceryListModal, setShowGroceryListModal] = useState(false);
  const [selectedHousehold, setSelectedHousehold] = useState(null);
  const [householdMembers, setHouseholdMembers] = useState([]);
  const [activeHouseholdTab, setActiveHouseholdTab] = useState('members');
  const [newFriendEmail, setNewFriendEmail] = useState('');
  const [newFriendMessage, setNewFriendMessage] = useState('');
  const [newHouseholdName, setNewHouseholdName] = useState('');
  const [newHouseholdDescription, setNewHouseholdDescription] = useState('');
  
  // Action states
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  // Premium features commented out for now
  // const [showPremiumModal, setShowPremiumModal] = useState(false);
  // const [premiumFeature, setPremiumFeature] = useState('unlimited-friends');
  // const [isPremiumUser, setIsPremiumUser] = useState(false);

  // Load data on component mount
  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    setLoading(true);
    setError('');
    
    try {
      await Promise.all([
        loadFriends(),
        loadRequests(),
        loadHouseholds()
      ]);
    } catch (error) {
      setError('Failed to load social data');
      console.error('Error loading social data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadFriends = async () => {
    const result = await FriendsAPI.getFriends();
    if (result.success) {
      setFriends(result.friends);
    } else {
      console.error('Failed to load friends:', result.error);
    }
  };

  const loadRequests = async () => {
    const result = await FriendsAPI.getFriendRequests();
    if (result.success) {
      setRequests(result.requests);
    } else {
      console.error('Failed to load requests:', result.error);
    }
  };

  const loadHouseholds = async () => {
    const result = await FriendsAPI.getHouseholds();
    if (result.success) {
      setHouseholds(result.households);
    } else {
      console.error('Failed to load households:', result.error);
    }
  };

  const handleSendFriendRequest = async (e) => {
    e.preventDefault();
    
    // Premium check commented out for now
    // if (!isPremiumUser && friends.length >= 10) {
    //   setPremiumFeature('unlimited-friends');
    //   setShowPremiumModal(true);
    //   return;
    // }
    
    if (!newFriendEmail.trim()) {
      setError('Please enter a valid email address');
      return;
    }
    
    setError('');
    setActionLoading(true);
    
    try {
      const result = await FriendsAPI.sendFriendRequest(newFriendEmail, newFriendMessage);
      setSuccess(`Friend request sent to ${newFriendEmail}!`);
      setNewFriendEmail('');
      setNewFriendMessage('');
      setShowAddFriendModal(false);
      
      // Refresh data
      await Promise.all([loadFriends(), loadRequests()]);
      
      setTimeout(() => setSuccess(''), 3000);
    } catch (error) {
      setError(error.message || 'Failed to send friend request');
    } finally {
      setActionLoading(false);
    }
  };

  const handleCreateHousehold = async (e) => {
    e.preventDefault();
    
    // Premium check commented out for now
    // if (!isPremiumUser && households.length >= 2) {
    //   setPremiumFeature('unlimited-friends');
    //   setShowPremiumModal(true);
    //   return;
    // }
    
    if (!newHouseholdName.trim()) {
      setError('Please enter a household name');
      return;
    }
    
    setError('');
    setActionLoading(true);
    
    try {
      const householdData = {
        name: newHouseholdName.trim(),
        description: newHouseholdDescription.trim() || null
      };
      
      const result = await FriendsAPI.createHousehold(householdData);
      setSuccess(`Household "${newHouseholdName}" created successfully!`);
      setNewHouseholdName('');
      setNewHouseholdDescription('');
      setShowCreateHouseholdModal(false);
      
      // Refresh households
      await loadHouseholds();
      
      setTimeout(() => setSuccess(''), 3000);
    } catch (error) {
      setError(error.message || 'Failed to create household');
    } finally {
      setActionLoading(false);
    }
  };  const handleAcceptRequest = async (request) => {
    setActionLoading(true);
    setError('');
    
    try {
      const result = await FriendsAPI.acceptFriendRequest(request.id);
      if (result.success) {
        setSuccess(result.message);
        loadFriends();
        loadRequests();
      } else {
        setError(result.error);
      }
    } catch (error) {
      setError('Failed to accept friend request');
    } finally {
      setActionLoading(false);
    }
  };

  const handleDeclineRequest = async (request) => {
    setActionLoading(true);
    setError('');
    
    try {
      const result = await FriendsAPI.declineFriendRequest(request.id);
      if (result.success) {
        setSuccess(result.message);
        loadRequests();
      } else {
        setError(result.error);
      }
    } catch (error) {
      setError('Failed to decline friend request');
    } finally {
      setActionLoading(false);
    }
  };

  const handleRemoveFriend = async (friend) => {
    if (!window.confirm(`Are you sure you want to remove ${friend.name} from your friends?`)) {
      return;
    }
    
    setActionLoading(true);
    setError('');
    
    try {
      const result = await FriendsAPI.removeFriend(friend.id);
      if (result.success) {
        setSuccess(result.message);
        loadFriends();
      } else {
        setError(result.error);
      }
    } catch (error) {
      setError('Failed to remove friend');
    } finally {
      setActionLoading(false);
    }
  };

  const handleViewHouseholdDetails = async (household) => {
    setSelectedHousehold(household);
    setActiveHouseholdTab('members');
    setShowHouseholdDetailsModal(true);
    
    // Load household members
    const result = await FriendsAPI.getHouseholdMembers(household.id);
    if (result.success) {
      setHouseholdMembers(result.members);
    } else {
      console.error('Failed to load household members:', result.error);
      setHouseholdMembers([]);
    }
  };

  const handleAddMemberToHousehold = async (friendId) => {
    setActionLoading(true);
    setError('');
    
    try {
      const result = await FriendsAPI.addHouseholdMember(selectedHousehold.id, friendId);
      if (result.success) {
        setSuccess(result.message);
        setShowAddMemberModal(false);
        // Refresh household data
        await handleViewHouseholdDetails(selectedHousehold);
        loadHouseholds();
      } else {
        setError(result.error);
      }
    } catch (error) {
      setError('Failed to add member to household');
    } finally {
      setActionLoading(false);
    }
  };

  const handleRemoveMemberFromHousehold = async (memberId) => {
    if (!window.confirm('Are you sure you want to remove this member from the household?')) {
      return;
    }
    
    setActionLoading(true);
    setError('');
    
    try {
      const result = await FriendsAPI.removeHouseholdMember(selectedHousehold.id, memberId);
      if (result.success) {
        setSuccess(result.message);
        // Refresh household data
        await handleViewHouseholdDetails(selectedHousehold);
        loadHouseholds();
      } else {
        setError(result.error);
      }
    } catch (error) {
      setError('Failed to remove member from household');
    } finally {
      setActionLoading(false);
    }
  };

  const handleDeleteHousehold = async (household) => {
    if (!window.confirm(`Are you sure you want to delete "${household.name}"? This action cannot be undone.`)) {
      return;
    }
    
    setActionLoading(true);
    setError('');
    
    try {
      const result = await FriendsAPI.deleteHousehold(household.id);
      if (result.success) {
        setSuccess(result.message);
        setShowHouseholdDetailsModal(false);
        loadHouseholds();
      } else {
        setError(result.error);
      }
    } catch (error) {
      setError('Failed to delete household');
    } finally {
      setActionLoading(false);
    }
  };

  const getInitials = (name) => {
    if (!name) return 'U';
    return name.split(' ').map(word => word.charAt(0)).join('').toUpperCase().slice(0, 2);
  };

  const renderTabContent = () => {
    if (loading) {
      return (
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading social features...</p>
        </div>
      );
    }

    switch (activeTab) {
      case 'friends':
        return (
          <div className="friends-list">
            {friends.length === 0 ? (
              <div className="empty-state">
                <span className="empty-icon">👥</span>
                <h3>No Friends Yet</h3>
                <p>Start building your cooking community by adding friends!</p>
                <button
                  className="primary-button"
                  onClick={() => setShowAddFriendModal(true)}
                >
                  Add Your First Friend
                </button>
              </div>
            ) : (
              friends.map(friend => (
                <div key={friend.id} className="friend-card">
                  <div className="friend-avatar">
                    {getInitials(friend.name)}
                  </div>
                  <div className="friend-info">
                    <h3 className="friend-name">{friend.name}</h3>
                    <p className="friend-email">{friend.email}</p>
                    <div className="friend-stats">
                      <div className="stat-item">
                        <span className="stat-value">{friend.sharedLists || 0}</span>
                        <span className="stat-label">Shared Lists</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-value">{friend.lastActive || 'Unknown'}</span>
                        <span className="stat-label">Last Active</span>
                      </div>
                    </div>
                  </div>
                  <div className="friend-actions">
                    <button
                      className="action-button remove-button"
                      onClick={() => handleRemoveFriend(friend)}
                      title="Remove Friend"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        );

      case 'requests':
        return (
          <div className="requests-list">
            {requests.length === 0 ? (
              <div className="empty-state">
                <span className="empty-icon">📮</span>
                <h3>No Friend Requests</h3>
                <p>You're all caught up! No pending friend requests.</p>
              </div>
            ) : (
              requests.map(request => (
                <div key={request.id} className="request-card">
                  <div className="request-avatar">
                    {getInitials(request.name)}
                  </div>
                  <div className="request-info">
                    <h3 className="request-name">{request.name}</h3>
                    <p className="request-email">{request.email}</p>
                    {request.message && (
                      <p className="request-message">"{request.message}"</p>
                    )}
                    <p className="request-time">{request.sentAt}</p>
                  </div>
                  <div className="request-actions">
                    {request.type === 'incoming' ? (
                      <>
                        <button
                          className="action-button accept-button"
                          onClick={() => handleAcceptRequest(request)}
                          disabled={actionLoading}
                        >
                          Accept
                        </button>
                        <button
                          className="action-button decline-button"
                          onClick={() => handleDeclineRequest(request)}
                          disabled={actionLoading}
                        >
                          Decline
                        </button>
                      </>
                    ) : (
                      <span className="outgoing-status">Request Sent</span>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        );

      case 'households':
        return (
          <div className="households-list">
            {households.length === 0 ? (
              <div className="empty-state">
                <span className="empty-icon">🏠</span>
                <h3>No Households Yet</h3>
                <p>Create a household to share recipes and meal plans with family or roommates!</p>
                <button
                  className="primary-button"
                  onClick={() => setShowCreateHouseholdModal(true)}
                >
                  Create Your First Household
                </button>
              </div>
            ) : (
              households.map(household => (
                <div key={household.id} className="household-card">
                  <div className="household-avatar">
                    {getInitials(household.name)}
                  </div>
                  <div className="household-info">
                    <h3 className="household-name">{household.name}</h3>
                    {household.description && (
                      <p className="household-description">{household.description}</p>
                    )}
                    <div className="household-stats">
                      <div className="stat-item">
                        <span className="stat-value">{household.members || 0}</span>
                        <span className="stat-label">Members</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-value">{household.sharedLists || 0}</span>
                        <span className="stat-label">Shared Lists</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-value">{household.sharedPlans || 0}</span>
                        <span className="stat-label">Meal Plans</span>
                      </div>
                    </div>
                  </div>
                  <div className="household-actions">
                    <button 
                      className="action-button"
                      onClick={() => handleViewHouseholdDetails(household)}
                      title="Manage Household"
                    >
                      ⚙️
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        );

      case 'sharing':
        return <RecipeSharing />;

      default:
        return null;
    }
  };

  return (
    <div className="friends-view">
      {/* Header */}
      <div className="friends-header">
        <h2>Friends & Households</h2>
        <p className="header-subtitle">Connect with friends and family to share recipes and meal plans</p>
      </div>

      {/* Tab Navigation */}
      <div className="tab-navigation">
        <button
          className={`tab-button ${activeTab === 'friends' ? 'active' : ''}`}
          onClick={() => setActiveTab('friends')}
        >
          👥 Friends ({friends.length})
        </button>
        <button
          className={`tab-button ${activeTab === 'requests' ? 'active' : ''}`}
          onClick={() => setActiveTab('requests')}
        >
          📮 Requests ({requests.length})
        </button>
        <button
          className={`tab-button ${activeTab === 'households' ? 'active' : ''}`}
          onClick={() => setActiveTab('households')}
        >
          🏠 Households ({households.length})
        </button>
        <button
          className={`tab-button ${activeTab === 'sharing' ? 'active' : ''}`}
          onClick={() => setActiveTab('sharing')}
        >
          📤 Recipe Sharing
        </button>
      </div>

      {/* Action Buttons */}
      <div className="action-buttons">
        <button
          className="primary-button"
          onClick={() => setShowAddFriendModal(true)}
        >
          ➕ Add Friend
        </button>
        <button
          className="secondary-button"
          onClick={() => setShowCreateHouseholdModal(true)}
        >
          🏠 Create Household
        </button>
      </div>

      {/* Messages */}
      {error && (
        <div className="message error-message">
          ❌ {error}
          <button onClick={() => setError('')} className="close-message">×</button>
        </div>
      )}
      {success && (
        <div className="message success-message">
          ✅ {success}
          <button onClick={() => setSuccess('')} className="close-message">×</button>
        </div>
      )}

      {/* Tab Content */}
      <div className="tab-content">
        {renderTabContent()}
      </div>

      {/* Add Friend Modal */}
      {showAddFriendModal && (
        <div className="modal-overlay" onClick={() => setShowAddFriendModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Add Friend</h3>
              <button
                className="close-button"
                onClick={() => setShowAddFriendModal(false)}
              >
                ×
              </button>
            </div>
            <form onSubmit={handleSendFriendRequest} className="modal-body">
              <div className="form-group">
                <label htmlFor="friendEmail">Friend's Email Address</label>
                <input
                  id="friendEmail"
                  type="email"
                  value={newFriendEmail}
                  onChange={(e) => setNewFriendEmail(e.target.value)}
                  placeholder="friend@example.com"
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="friendMessage">Message (Optional)</label>
                <textarea
                  id="friendMessage"
                  value={newFriendMessage}
                  onChange={(e) => setNewFriendMessage(e.target.value)}
                  placeholder="Hi! I'd love to share recipes and meal plans with you on YesChef."
                  rows={3}
                />
              </div>
              <div className="modal-actions">
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() => setShowAddFriendModal(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="primary-button"
                  disabled={actionLoading}
                >
                  {actionLoading ? 'Sending...' : 'Send Friend Request'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Create Household Modal */}
      {showCreateHouseholdModal && (
        <div className="modal-overlay" onClick={() => setShowCreateHouseholdModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Create Household</h3>
              <button
                className="close-button"
                onClick={() => setShowCreateHouseholdModal(false)}
              >
                ×
              </button>
            </div>
            <form onSubmit={handleCreateHousehold} className="modal-body">
              <div className="form-group">
                <label htmlFor="householdName">Household Name</label>
                <input
                  id="householdName"
                  type="text"
                  value={newHouseholdName}
                  onChange={(e) => setNewHouseholdName(e.target.value)}
                  placeholder="My Family"
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="householdDescription">Description (Optional)</label>
                <textarea
                  id="householdDescription"
                  value={newHouseholdDescription}
                  onChange={(e) => setNewHouseholdDescription(e.target.value)}
                  placeholder="Describe your household..."
                  rows={3}
                />
              </div>
              <div className="modal-actions">
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() => setShowCreateHouseholdModal(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="primary-button"
                  disabled={actionLoading}
                >
                  {actionLoading ? 'Creating...' : 'Create Household'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Household Details Modal */}
      {showHouseholdDetailsModal && selectedHousehold && (
        <div className="modal-overlay" onClick={() => setShowHouseholdDetailsModal(false)}>
          <div className="modal-content large-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>🏠 {selectedHousehold.name}</h3>
              <button
                className="close-button"
                onClick={() => setShowHouseholdDetailsModal(false)}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              {selectedHousehold.description && (
                <p className="household-modal-description">{selectedHousehold.description}</p>
              )}
              
              {/* Household Tabs */}
              <div className="household-tabs">
                <button
                  className={`household-tab ${activeHouseholdTab === 'members' ? 'active' : ''}`}
                  onClick={() => setActiveHouseholdTab('members')}
                >
                  👥 Members ({householdMembers.length})
                </button>
                <button
                  className={`household-tab ${activeHouseholdTab === 'grocery' ? 'active' : ''}`}
                  onClick={() => setActiveHouseholdTab('grocery')}
                >
                  🛒 Grocery List
                </button>
                <button
                  className={`household-tab ${activeHouseholdTab === 'meals' ? 'active' : ''}`}
                  onClick={() => setActiveHouseholdTab('meals')}
                >
                  🍽️ Meal Plan
                </button>
              </div>

              {/* Tab Content */}
              {activeHouseholdTab === 'members' && (
                <div className="household-tab-content">
                  <div className="household-actions-section">
                    <button
                      className="primary-button"
                      onClick={() => setShowAddMemberModal(true)}
                    >
                      ➕ Add Member
                    </button>
                    <button
                      className="danger-button"
                      onClick={() => handleDeleteHousehold(selectedHousehold)}
                    >
                      🗑️ Delete Household
                    </button>
                  </div>

                  <div className="members-section">
                    <h4>Members ({householdMembers.length})</h4>
                    {householdMembers.length === 0 ? (
                      <p className="no-members">No members yet. Add some friends to get started!</p>
                    ) : (
                      <div className="members-list">
                        {householdMembers.map(member => (
                          <div key={member.id} className="member-item">
                            <div className="member-avatar">
                              {getInitials(member.name)}
                            </div>
                            <div className="member-info">
                              <h5 className="member-name">{member.name}</h5>
                              <p className="member-role">{member.role} • Joined {member.joined_at}</p>
                            </div>
                            {member.role !== 'owner' && (
                              <button
                                className="action-button remove-button"
                                onClick={() => handleRemoveMemberFromHousehold(member.id)}
                                title="Remove Member"
                              >
                                ➖
                              </button>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {activeHouseholdTab === 'grocery' && (
                <div className="household-tab-content">
                  <SharedGroceryList household={selectedHousehold} />
                </div>
              )}

              {activeHouseholdTab === 'meals' && (
                <div className="household-tab-content">
                  <SharedMealPlanner household={selectedHousehold} />
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Add Member to Household Modal */}
      {showAddMemberModal && selectedHousehold && (
        <div className="modal-overlay" onClick={() => setShowAddMemberModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>👥 Add Member to {selectedHousehold.name}</h3>
              <button
                className="close-button"
                onClick={() => setShowAddMemberModal(false)}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <p className="modal-instruction">Select a friend to add to this household:</p>
              
              {friends.length === 0 ? (
                <div className="empty-state small">
                  <p>No friends available to add. Add some friends first!</p>
                </div>
              ) : (
                <div className="friends-selection-list">
                  {friends
                    .filter(friend => !householdMembers.some(member => member.id === friend.id))
                    .map(friend => (
                      <div key={friend.id} className="friend-selection-item">
                        <div className="friend-avatar small">
                          {getInitials(friend.name)}
                        </div>
                        <div className="friend-info">
                          <h5 className="friend-name">{friend.name}</h5>
                          <p className="friend-email">{friend.email}</p>
                        </div>
                        <button
                          className="action-button accept-button"
                          onClick={() => handleAddMemberToHousehold(friend.id)}
                          disabled={actionLoading}
                        >
                          Add
                        </button>
                      </div>
                    ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Premium Features Modal - Commented out for now */}
      {/* {showPremiumModal && (
        <PremiumFeatures
          feature={premiumFeature}
          onUpgrade={(planId) => {
            console.log('Upgrading to plan:', planId);
            setShowPremiumModal(false);
            setSuccess('Upgrade successful! Premium features unlocked!');
            setIsPremiumUser(true);
            setTimeout(() => setSuccess(''), 3000);
          }}
          onClose={() => setShowPremiumModal(false)}
        />
      )} */}
    </div>
  );
};

export default FriendsView;