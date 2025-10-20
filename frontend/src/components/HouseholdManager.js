import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import HouseholdCard from './HouseholdCard';
import CreateHouseholdModal from './CreateHouseholdModal';
import HouseholdMembersModal from './HouseholdMembersModal';
import * as householdAPI from '../utils/householdAPI';
import './HouseholdManager.css';

const HouseholdManager = () => {
  const { user } = useAuth();
  const [households, setHouseholds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Modals
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showMembersModal, setShowMembersModal] = useState(false);
  const [selectedHousehold, setSelectedHousehold] = useState(null);
  
  // Success message
  const [successMessage, setSuccessMessage] = useState('');

  // Load households on mount
  useEffect(() => {
    loadHouseholds();
  }, []);

  const loadHouseholds = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await householdAPI.getHouseholds();
      
      if (result.success) {
        setHouseholds(result.households || []);
      } else {
        setError(result.error || 'Failed to load households');
      }
    } catch (err) {
      setError('An error occurred while loading households');
      console.error('Load households error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateHousehold = async (name, description) => {
    const result = await householdAPI.createHousehold(name, description);
    
    if (result.success) {
      showSuccess(`🎉 Household "${name}" created successfully!`);
      loadHouseholds(); // Reload list
    }
    
    return result;
  };

  const handleDeleteHousehold = async (household) => {
    const confirmDelete = window.confirm(
      `Are you sure you want to delete "${household.name}"?\n\nThis will remove all members and cannot be undone.`
    );
    
    if (!confirmDelete) return;

    const result = await householdAPI.deleteHousehold(household.id);
    
    if (result.success) {
      showSuccess(`🗑️ Household "${household.name}" deleted`);
      loadHouseholds(); // Reload list
    } else {
      alert(`Failed to delete household: ${result.error}`);
    }
  };

  const handleManageMembers = (household) => {
    setSelectedHousehold(household);
    setShowMembersModal(true);
  };

  const handleMembersModalClose = () => {
    setShowMembersModal(false);
    setSelectedHousehold(null);
    loadHouseholds(); // Reload to get updated member counts
  };

  const showSuccess = (message) => {
    setSuccessMessage(message);
    setTimeout(() => setSuccessMessage(''), 3000);
  };

  if (loading) {
    return (
      <div className="household-manager">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading households...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="household-manager">
      {/* Header */}
      <div className="household-header">
        <div className="header-title">
          <h1>🏠 My Households</h1>
          <p className="header-subtitle">
            Manage your households and collaborate with family & friends
          </p>
        </div>
        <button 
          className="create-household-btn"
          onClick={() => setShowCreateModal(true)}
        >
          <span className="btn-icon">➕</span>
          <span className="btn-text">Create Household</span>
        </button>
      </div>

      {/* Success Message */}
      {successMessage && (
        <div className="success-banner">
          {successMessage}
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="error-banner">
          ⚠️ {error}
          <button onClick={loadHouseholds} className="retry-btn">
            Try Again
          </button>
        </div>
      )}

      {/* Empty State */}
      {!error && households.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">🏠</div>
          <h2>No Households Yet</h2>
          <p>Create your first household to start collaborating on grocery lists and meal plans with family and friends!</p>
          <button 
            className="create-first-btn"
            onClick={() => setShowCreateModal(true)}
          >
            ✨ Create Your First Household
          </button>
        </div>
      )}

      {/* Households Grid */}
      {!error && households.length > 0 && (
        <div className="households-grid">
          {households.map((household) => (
            <HouseholdCard
              key={household.id}
              household={household}
              onManageMembers={handleManageMembers}
              onDelete={handleDeleteHousehold}
              currentUserId={user?.id}
            />
          ))}
        </div>
      )}

      {/* Modals */}
      <CreateHouseholdModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onCreate={handleCreateHousehold}
      />

      <HouseholdMembersModal
        isOpen={showMembersModal}
        onClose={handleMembersModalClose}
        household={selectedHousehold}
        currentUserId={user?.id}
      />
    </div>
  );
};

export default HouseholdManager;
