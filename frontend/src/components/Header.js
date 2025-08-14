import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Header.css';

const Header = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  return (
    <header className="header">
      <div className="header-container">
        <div className="logo" onClick={() => navigate('/')}>
          <h1>🍴 Hungie</h1>
          <p className="tagline">Your cravings, satisfied!</p>
        </div>

        <form className="search-form" onSubmit={handleSearch}>
          <input
            type="text"
            className="search-input"
            placeholder="What are you craving? Try 'chicken', 'pasta', or 'dessert'..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <button type="submit" className="search-button">
            🔍 Find Food
          </button>
        </form>

        <nav className="nav-links">
          <button onClick={() => navigate('/categories')} className="nav-link">
            Categories
          </button>
          <button onClick={() => navigate('/chat')} className="nav-link chat-link">
            💬 Chat with Hungie
          </button>
        </nav>
      </div>
    </header>
  );
};

export default Header;
