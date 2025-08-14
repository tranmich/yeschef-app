import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Home.css';

const Home = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  const handleQuickSearch = (query) => {
    navigate(`/search?q=${encodeURIComponent(query)}`);
  };

  return (
    <div className="home">
      <div className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">
            Hey there, foodie! 👋
          </h1>
          <h2 className="hero-subtitle">
            What's making your stomach rumble today?
          </h2>
          <p className="hero-description">
            From copycat restaurant favorites to comfort food classics, 
            I've got <strong>132 delicious recipes</strong> ready to satisfy your cravings!
          </p>

          <form className="hero-search" onSubmit={handleSearch}>
            <input
              type="text"
              className="hero-search-input"
              placeholder="Try 'chicken tacos', 'chocolate cake', or 'quick dinner'..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <button type="submit" className="hero-search-button">
              🍴 Let's Cook!
            </button>
          </form>

          <div className="quick-searches">
            <p>Popular cravings:</p>
            <div className="quick-search-buttons">
              <button 
                className="quick-search-btn"
                onClick={() => handleQuickSearch('chicken')}
              >
                🐔 Chicken Dishes
              </button>
              <button 
                className="quick-search-btn"
                onClick={() => handleQuickSearch('burger')}
              >
                🍔 Burgers
              </button>
              <button 
                className="quick-search-btn"
                onClick={() => handleQuickSearch('pasta')}
              >
                🍝 Pasta
              </button>
              <button 
                className="quick-search-btn"
                onClick={() => handleQuickSearch('dessert')}
              >
                🍰 Desserts
              </button>
            </div>
          </div>

          <div className="chat-promo">
            <div className="chat-promo-content">
              <div className="chat-promo-icon">💬</div>
              <div className="chat-promo-text">
                <h4>New! Chat with Hungie</h4>
                <p>Get personalized recipe recommendations and cooking tips from your AI chef companion!</p>
              </div>
              <button 
                className="chat-promo-button"
                onClick={() => navigate('/chat')}
              >
                Start Chatting
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="features-section">
        <div className="features-container">
          <h3>Why you'll love Hungie:</h3>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🏠</div>
              <h4>Restaurant Copycats</h4>
              <p>Make your Olive Garden, Starbucks, and Chick-fil-A favorites at home!</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">⚡</div>
              <h4>Quick & Easy</h4>
              <p>Filter by cooking time - from 15-minute meals to weekend projects.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🔍</div>
              <h4>Smart Search</h4>
              <p>Search by ingredient, dish name, or just tell me what you're craving!</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📝</div>
              <h4>Detailed Recipes</h4>
              <p>Step-by-step instructions, ingredients, and cooking tips included.</p>
            </div>
          </div>
        </div>
      </div>

      <div className="stats-section">
        <div className="stats-container">
          <div className="stat">
            <span className="stat-number">92</span>
            <span className="stat-label">Complete Recipes</span>
          </div>
          <div className="stat">
            <span className="stat-number">12</span>
            <span className="stat-label">Categories</span>
          </div>
          <div className="stat">
            <span className="stat-number">100%</span>
            <span className="stat-label">Quality Guaranteed</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
