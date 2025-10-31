import React, { useState } from 'react';
import './Home.css';

const Home = () => {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState('');

  const handleSignup = async (e) => {
    e.preventDefault();
    
    try {
      const response = await fetch('/api/waitlist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });
      
      if (response.ok) {
        setStatus('success');
        setEmail('');
      } else {
        setStatus('error');
      }
    } catch (error) {
      console.error('Signup error:', error);
      setStatus('error');
    }
  };

  return (
    <div className="home-simple">
      {/* Hero Section with Centered Signup */}
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">
            🍳 Welcome to <span className="brand-text">YesChef</span>
          </h1>
          <p className="hero-subtitle">
            Your personal AI cooking assistant for meal planning, recipes, and grocery lists
          </p>

          {/* Centered Signup Form */}
          <form onSubmit={handleSignup} className="signup-form">
            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="email-input"
            />
            <button type="submit" className="signup-btn">
              Get Early Access
            </button>
          </form>

          {status === 'success' && (
            <p className="success-message">✅ Thanks! You're on the list!</p>
          )}
          {status === 'error' && (
            <p className="error-message">❌ Something went wrong. Please try again.</p>
          )}
        </div>
      </section>

      {/* Single Benefits Section */}
      <section className="benefits-section">
        <h2 className="benefits-title">Why YesChef?</h2>
        <div className="benefits-grid">
          <div className="benefit-card">
            <span className="benefit-icon">🤖</span>
            <h3>AI-Powered</h3>
            <p>Smart recipe suggestions based on what you have</p>
          </div>

          <div className="benefit-card">
            <span className="benefit-icon">�</span>
            <h3>Meal Planning</h3>
            <p>Plan your week with automatic grocery lists</p>
          </div>

          <div className="benefit-card">
            <span className="benefit-icon">�</span>
            <h3>Smart Shopping</h3>
            <p>Never forget an ingredient again</p>
          </div>

          <div className="benefit-card">
            <span className="benefit-icon">🥕</span>
            <h3>Pantry Tracking</h3>
            <p>Know what's in your kitchen at all times</p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
