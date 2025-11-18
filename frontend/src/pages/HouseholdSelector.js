/**
 * Household Selector
 * ==================
 * Shows list of households user belongs to
 * Lets user select which household's whiteboards to view
 * 
 * Phase 1 - Week 3
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import * as api from '../utils/api';
import './HouseholdSelector.css';

const HouseholdSelector = ({ onSelectHousehold }) => {
  const { user } = useAuth();

  const [households, setHouseholds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadHouseholds();
  }, []);

  const loadHouseholds = async () => {
    try {
      setLoading(true);
      setError(null);

      // Use existing household API with user ID
      const response = await api.apiCall(`/api/v2/households/user/${user.id}`, {
        method: 'GET'
      });

      if (response && response.success) {
        const userHouseholds = response.data?.households || [];
        setHouseholds(userHouseholds);

        // If only one household, auto-select it
        if (userHouseholds.length === 1) {
          onSelectHousehold(userHouseholds[0].id);
        }
      } else {
        setError('Failed to load households');
      }
    } catch (err) {
      console.error('Error loading households:', err);
      setError('Failed to load households');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectHousehold = (householdId) => {
    onSelectHousehold(householdId);
  };

  if (loading) {
    return (
      <div className="household-selector">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading households...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="household-selector">
        <div className="error-container">
          <h2>Error</h2>
          <p>{error}</p>
          <button onClick={loadHouseholds}>Try Again</button>
        </div>
      </div>
    );
  }

  if (households.length === 0) {
    return (
      <div className="household-selector">
        <div className="empty-state">
          <h2>No Households Found</h2>
          <p>You need to be part of a household to use whiteboards.</p>
          <p>Ask a household owner to invite you!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="household-selector embedded">
      <div className="selector-header embedded">
        <h1>Your Households</h1>
        <p>Select a household to view its whiteboards</p>
      </div>

      <div className="households-grid">
        {households.map((household) => (
          <div
            key={household.id}
            className="household-card"
            onClick={() => handleSelectHousehold(household.id)}
          >
            <h3>{household.name}</h3>
            {household.description && (
              <p className="household-description">{household.description}</p>
            )}
            <div className="household-footer">
              <span className="member-count">
                {household.member_count || 0} members
              </span>
              <button className="select-button">View Whiteboards</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default HouseholdSelector;
