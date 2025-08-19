import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navigateToMealPlanning = () => {
    navigate('/');
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div className="user-welcome">
          <h1>Welcome back, {user?.name}!</h1>
          <p>Ready to plan some delicious meals?</p>
        </div>
        <button onClick={handleLogout} className="logout-button">
          Sign Out
        </button>
      </div>

      <div className="dashboard-content">
        <div className="dashboard-cards">

          <div className="dashboard-card primary" onClick={navigateToMealPlanning}>
            <div className="card-icon">🍽️</div>
            <h3>Meal Planning</h3>
            <p>Plan your meals with AI-powered recipe suggestions</p>
            <button className="card-button">Start Planning</button>
          </div>

          <div className="dashboard-card">
            <div className="card-icon">💾</div>
            <h3>Saved Recipes</h3>
            <p>Access your personal recipe collection</p>
            <button className="card-button" disabled>Coming Soon</button>
          </div>

          <div className="dashboard-card">
            <div className="card-icon">🥕</div>
            <h3>Pantry Management</h3>
            <p>Track your ingredients and pantry items</p>
            <button className="card-button">Manage Pantry</button>
          </div>

          <div className="dashboard-card">
            <div className="card-icon">🛒</div>
            <h3>Grocery Lists</h3>
            <p>Generate smart shopping lists from meal plans</p>
            <button className="card-button" disabled>Coming Soon</button>
          </div>

          <div className="dashboard-card">
            <div className="card-icon">⚙️</div>
            <h3>Preferences</h3>
            <p>Customize your dietary preferences and restrictions</p>
            <button className="card-button" disabled>Coming Soon</button>
          </div>

          <div className="dashboard-card">
            <div className="card-icon">📊</div>
            <h3>Analytics</h3>
            <p>View your cooking habits and meal planning stats</p>
            <button className="card-button" disabled>Coming Soon</button>
          </div>

        </div>
      </div>

      <div className="dashboard-footer">
        <div className="user-info">
          <h4>Account Information</h4>
          <div className="info-item">
            <label>Name:</label>
            <span>{user?.name}</span>
          </div>
          <div className="info-item">
            <label>Email:</label>
            <span>{user?.email}</span>
          </div>
          <div className="info-item">
            <label>Member since:</label>
            <span>{new Date().toLocaleDateString()}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
