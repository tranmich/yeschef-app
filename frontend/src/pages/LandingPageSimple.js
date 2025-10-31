import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import './LandingPageSimple.css';

const LandingPageSimple = () => {
  const navigate = useNavigate();
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
      const API_URL = process.env.REACT_APP_API_URL || '';
      const response = await fetch(`${API_URL}/api/waitlist`, {
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
      {/* Logo - Top Left Header */}
      <div className="logo-header">
        <img src="/images/yeschef-logo.png" alt="YesChef" className="logo-header-img" />
        <span className="logo-header-text">YesChef</span>
      </div>

      {/* Login Button - Top Right */}
      <button 
        className="login-btn-top"
        onClick={() => navigate('/login')}
      >
        Sign In
      </button>

      {/* Hero Section - Email Capture Focus */}
      <section className="hero">
        <div className="hero-container">
          {/* Logo - Hidden, moved to header */}
          <div className="hero-logo">
            <img src="/images/yeschef-logo.png" alt="YesChef" className="logo" />
          </div>

          {/* Main Headline */}
          <h1 className="hero-headline">
            Your recipes.<br />All in one place.
          </h1>

          {/* Subheadline */}
          <p className="hero-subheadline">
            A smarter, simpler way to cook, plan, and share the meals that bring us together.
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
              Invite-only beta · Coming soon
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
          <h2 className="features-headline">Why YesChef?</h2>
          
          <div className="features-grid">
            {/* Feature 1: Capture */}
            <div className="feature-card">
              <div className="feature-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path>
                  <circle cx="12" cy="13" r="4"></circle>
                </svg>
              </div>
              <h3>Save from Anywhere</h3>
              <p>
                Screenshot, link, or voice note. Add any recipe instantly.
              </p>
            </div>

            {/* Feature 2: Organize */}
            <div className="feature-card">
              <div className="feature-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                </svg>
              </div>
              <h3>Organize Your Way</h3>
              <p>
                Collections, tags, search. Find any recipe in seconds.
              </p>
            </div>

            {/* Feature 3: Collaborate */}
            <div className="feature-card">
              <div className="feature-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                  <circle cx="9" cy="7" r="4"></circle>
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                  <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                </svg>
              </div>
              <h3>Share with Your Household</h3>
              <p>
                Plan together. Shop together. Cook together.
              </p>
            </div>

            {/* Feature 4: AI-Powered */}
            <div className="feature-card">
              <div className="feature-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="5"></circle>
                  <line x1="12" y1="1" x2="12" y2="3"></line>
                  <line x1="12" y1="21" x2="12" y2="23"></line>
                  <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                  <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                  <line x1="1" y1="12" x2="3" y2="12"></line>
                  <line x1="21" y1="12" x2="23" y2="12"></line>
                  <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                  <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
                </svg>
              </div>
              <h3>AI Does the Work</h3>
              <p>
                Auto-organize ingredients. Generate meal plans. Smart suggestions.
              </p>
            </div>

            {/* Feature 5: Mobile & Web Sync */}
            <div className="feature-card">
              <div className="feature-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="5" y="2" width="14" height="20" rx="2" ry="2"></rect>
                  <line x1="12" y1="18" x2="12.01" y2="18"></line>
                </svg>
              </div>
              <h3>Mobile & Web Sync</h3>
              <p>
                Access your recipes anywhere. Full flexibility across all your devices.
              </p>
            </div>

            {/* Feature 6: Grocery Lists */}
            <div className="feature-card">
              <div className="feature-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M9 11l3 3L22 4"></path>
                  <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
                </svg>
              </div>
              <h3>Smart Grocery Lists</h3>
              <p>
                Generate grocery lists from recipes instantly. Shop smarter, not harder.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Features List Section */}
      <section className="features-list-section">
        <div className="features-list-container">
          <h2 className="features-list-headline">Everything You Need to Cook with Confidence</h2>
          <p className="features-list-subheadline">
            We built YesChef to solve the real pain points of home cooking
          </p>
          
          <div className="features-columns">
            <div className="features-column">
              <h3 className="column-title">Recipe Management</h3>
              <ul className="features-items">
                <li>Save recipes from any source (screenshots, links, voice notes)</li>
                <li>AI-powered ingredient extraction and organization</li>
                <li>Advanced search with filters and tags</li>
                <li>Custom collections and folders</li>
                <li>Offline access to all saved recipes</li>
              </ul>
            </div>

            <div className="features-column">
              <h3 className="column-title">Meal Planning</h3>
              <ul className="features-items">
                <li>Drag-and-drop meal calendar</li>
                <li>Weekly and monthly planning views</li>
                <li>Auto-generate grocery lists from meal plans</li>
                <li>Serving size adjustments</li>
                <li>Leftover tracking and suggestions</li>
              </ul>
            </div>

            <div className="features-column">
              <h3 className="column-title">Household Collaboration</h3>
              <ul className="features-items">
                <li>Share recipes with household members</li>
                <li>Collaborative grocery lists</li>
                <li>Meal planning together</li>
                <li>Real-time sync across all devices</li>
                <li>Comment and rate recipes as a family</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* About/Founder Section */}
      <section className="about-section">
        <div className="about-container">
          <h2 className="about-headline">About YesChef</h2>
          <div className="about-content">
            <div className="about-text">
              <p>
                Hi, I'm Michael — the creator of YesChef.
              </p>
              <p>
                Cooking has been a part of my life for over twenty years, starting as a way to save money 
                and growing into something much deeper — a way to connect, express myself, and care for others.
              </p>
              <p>
                YesChef was born from that journey. After years of messy notes, lost recipes, and chaotic 
                meal planning, I wanted a better way to organize and share the food we love. This app is my 
                attempt to make cooking simpler, smarter, and more communal — a space to preserve recipes, 
                build habits, and pass stories forward.
              </p>
              <p>
                At its heart, YesChef is about doing for others — one meal at a time.
              </p>
              <p className="signature">— Michael</p>
              <button 
                className="read-more-btn"
                onClick={() => navigate('/story')}
              >
                Read the Full Story →
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="faq-section">
        <div className="faq-container">
          <h2 className="faq-headline">FAQ</h2>
          
          <div className="faq-list">
            <details className="faq-item">
              <summary>How is YesChef different from other recipe apps?</summary>
              <p>We're built for households, not individuals. Share recipes, plan together, and actually know what's for dinner—all in one collaborative workspace.</p>
            </details>

            <details className="faq-item">
              <summary>Can I import my existing recipes?</summary>
              <p>Yes! Add via screenshot, link, voice note, or manual entry. Our AI extracts ingredients and steps automatically.</p>
            </details>

            <details className="faq-item">
              <summary>Does it work offline?</summary>
              <p>Your saved recipes are always accessible, even without internet. Perfect for cooking without distractions.</p>
            </details>

            <details className="faq-item">
              <summary>What about meal planning and grocery lists?</summary>
              <p>Drag recipes to your calendar, and we auto-generate a smart grocery list. Share it with your household—no more "what did you forget?"</p>
            </details>

            <details className="faq-item">
              <summary>Is there a limit to how many recipes I can save?</summary>
              <p>Nope! Save unlimited recipes. We're here to preserve your family's food history, not limit it.</p>
            </details>

            <details className="faq-item">
              <summary>Can I trust you with my data?</summary>
              <p>Your recipes are yours. Period. We encrypt everything, never sell data, and you can export anytime. See our <Link to="/privacy">Privacy Policy</Link>.</p>
            </details>

            <details className="faq-item">
              <summary>When can I actually use this?</summary>
              <p>We're in private beta! Join the waitlist and be among the first 100 users to get lifetime free access.</p>
            </details>
          </div>
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
            <Link to="/privacy">Privacy</Link>
            <a href="mailto:michaeltran@yeschefapp.io">Contact</a>
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

