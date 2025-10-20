import React, { useState } from 'react';
import './LandingPageSimple.css';

const LandingPageSimple = () => {
  const [email, setEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    // Track with Google Analytics
    if (window.gtag) {
      window.gtag('event', 'waitlist_signup', {
        event_category: 'engagement',
        event_label: 'hero_email_capture'
      });
    }

    try {
      // TODO: Replace with your actual API endpoint
      const response = await fetch('/api/waitlist', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      if (response.ok) {
        setSubmitSuccess(true);
        setEmail('');
        
        // Reset success message after 5 seconds
        setTimeout(() => {
          setSubmitSuccess(false);
        }, 5000);
      }
    } catch (error) {
      console.error('Waitlist signup error:', error);
      // For now, still show success even on error (development)
      setSubmitSuccess(true);
      setEmail('');
      setTimeout(() => setSubmitSuccess(false), 5000);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="landing-simple">
      {/* Hero Section - Email Capture Focus */}
      <section className="hero">
        <div className="hero-container">
          {/* Logo */}
          <div className="hero-logo">
            <img src="/images/yeschef-logo.png" alt="YesChef" className="logo" />
          </div>

          {/* Main Headline */}
          <h1 className="hero-headline">
            Everything in its place
          </h1>

          {/* Subheadline */}
          <p className="hero-subheadline">
            Preserve family recipes and organize your kitchen life.
            <br />From any source, in seconds.
          </p>

          {/* Email Capture Form */}
          <div className="email-capture">
            {submitSuccess ? (
              <div className="success-message">
                <span className="success-icon">✓</span>
                <p>You're on the list! We'll reach out soon with your beta invite.</p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="email-form">
                <input
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="email-input"
                  disabled={isSubmitting}
                />
                <button 
                  type="submit" 
                  className="submit-button"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? 'Joining...' : 'Join Waitlist'}
                </button>
              </form>
            )}
            <p className="hero-note">
              Invite-only beta · iOS & Android · Launching soon
            </p>
          </div>

          {/* Hero Image */}
          <div className="hero-image-container">
            <img 
              src="/images/hero-kitchen.jpg" 
              alt="Organized kitchen" 
              className="hero-image"
            />
          </div>
        </div>
      </section>

      {/* Features Overview - Simple 3 Cards */}
      <section className="features">
        <div className="features-container">
          <h2 className="features-headline">How YesChef Works</h2>
          
          <div className="features-grid">
            {/* Feature 1: Capture */}
            <div className="feature-card">
              <div className="feature-icon">📸</div>
              <h3>Capture</h3>
              <p>
                Photo, voice, or link—add recipes from anywhere in seconds. 
                Handwritten cards, YouTube videos, food blogs, all in one place.
              </p>
            </div>

            {/* Feature 2: Organize */}
            <div className="feature-card">
              <div className="feature-icon">📚</div>
              <h3>Organize</h3>
              <p>
                Your entire collection, beautifully organized. Search by ingredient, 
                tag by occasion, find what you need when you need it.
              </p>
            </div>

            {/* Feature 3: Plan & Shop */}
            <div className="feature-card">
              <div className="feature-icon">📅</div>
              <h3>Plan & Shop</h3>
              <p>
                Drag recipes to your calendar. Get automatic grocery lists. 
                Share with your household. Dinner sorted.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Social Proof - Quick Stats */}
      <section className="social-proof">
        <div className="social-container">
          <p className="social-quote">
            "I finally have all my mom's recipes in one place."
          </p>
          <p className="social-author">— Sarah M., Boston</p>
        </div>
      </section>

      {/* Final CTA */}
      <section className="final-cta">
        <div className="cta-container">
          <h2 className="cta-headline">Start organizing today</h2>
          <p className="cta-subheadline">
            Join the waitlist for early access
          </p>
          
          {submitSuccess ? (
            <div className="success-message">
              <span className="success-icon">✓</span>
              <p>You're all set! Check your email soon.</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="email-form-bottom">
              <input
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="email-input"
                disabled={isSubmitting}
              />
              <button 
                type="submit" 
                className="submit-button"
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Joining...' : 'Join Waitlist'}
              </button>
            </form>
          )}
        </div>
      </section>

      {/* Footer - Minimal */}
      <footer className="footer">
        <div className="footer-container">
          <div className="footer-logo">
            <img src="/images/yeschef-logo.png" alt="YesChef" className="footer-logo-img" />
          </div>
          <p className="footer-tagline">
            Preserve recipes. Plan meals. Ease the overwhelm.
          </p>
          <div className="footer-links">
            <a href="#privacy">Privacy</a>
            <a href="#terms">Terms</a>
            <a href="mailto:hello@yeschefapp.io">Contact</a>
          </div>
          <p className="footer-copyright">
            © 2025 YesChef. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPageSimple;
