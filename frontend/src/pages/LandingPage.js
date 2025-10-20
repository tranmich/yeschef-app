import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './LandingPage.css';

const LandingPage = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);

  // Log that landing page loaded successfully
  useEffect(() => {
    console.log('✅ YesChef Landing Page Loaded Successfully!');
    console.log('📍 Current route: /');
    console.log('🎨 Brand colors: Mint (#AAC6AD) + Yellow (#EFFD5F)');
  }, []);

  // Track scroll for sticky header
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Intersection Observer for fade-in animations
  useEffect(() => {
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        }
      });
    }, observerOptions);

    document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));

    return () => observer.disconnect();
  }, []);

  const handleWaitlistSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    // Determine which form was submitted (hero or final CTA)
    const formSource = e.target.closest('.hero-section') ? 'hero' : 'final-cta';

    // Track with Google Analytics
    if (window.gtag) {
      window.gtag('event', 'waitlist_signup', {
        event_category: 'engagement',
        event_label: formSource
      });
    }

    try {
      // Call the actual backend API
      const response = await fetch('http://localhost:5000/api/waitlist', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email,
          source: formSource
        }),
      });

      const data = await response.json();

      if (data.success) {
        console.log('✅ Waitlist signup successful:', data);
        setSubmitSuccess(true);
        setEmail('');
        
        // Hide success message after 5 seconds
        setTimeout(() => {
          setSubmitSuccess(false);
        }, 5000);
      } else {
        console.error('❌ Waitlist signup failed:', data.error);
        alert(data.error || 'Failed to join waitlist. Please try again.');
      }
    } catch (error) {
      console.error('❌ Waitlist signup error:', error);
      alert('Network error. Please check your connection and try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCTAClick = (location) => {
    // Track CTA clicks
    if (window.gtag) {
      window.gtag('event', 'cta_click', {
        event_category: 'engagement',
        event_label: location
      });
    }
    setShowWaitlistModal(true);
  };

  return (
    <div className="landing-page">
      {/* Navigation Bar */}
      <nav className={`landing-nav ${isScrolled ? 'scrolled' : ''}`}>
        <div className="nav-container">
          <div className="nav-logo">
            <div className="logo-icon">
              <img src="/images/yeschef-logo.png" alt="YesChef Logo" className="logo-img" />
            </div>
            <span className="logo-text">YesChef</span>
          </div>
          <div className="nav-links">
            <a href="#how-it-works">How It Works</a>
            <a href="#features">Features</a>
            <a href="#community">Join Waitlist</a>
            <button 
              className="nav-signin-btn"
              onClick={() => navigate('/login')}
            >
              Sign In
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section - Simplified with Email Capture */}
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-headline">Everything in its place</h1>
          <p className="hero-subheadline">
            Preserve family recipes and organize your kitchen life.
            <br />From any source, in seconds.
          </p>
          
          {/* Email Capture Form - Front and Center */}
          <form onSubmit={handleWaitlistSubmit} className="hero-email-form">
            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="hero-email-input"
            />
            <button 
              type="submit" 
              className="hero-cta-btn"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Joining...' : 'Join Waitlist'}
            </button>
          </form>
          
          {submitSuccess && (
            <div className="hero-success-message">
              ✓ You're on the list! We'll reach out soon with your invite.
            </div>
          )}
          
          <p className="hero-subtext">
            Invite-only beta · iOS & Android coming soon
          </p>
        </div>
      </section>

      {/* Simple Value Proposition */}
      <section id="how-it-works" className="problem-section fade-in">
        <div className="section-container">
          <h2 className="section-headline">Your recipes are everywhere</h2>
          <p className="section-description">
            Screenshots. Bookmarks. Handwritten cards. That email from mom.
            <br /><strong>It's time to bring them all together.</strong>
          </p>
        </div>
      </section>

      {/* Quick Feature Overview - Simplified */}
      <section id="features" className="features-section fade-in">
        <div className="section-container">
          <h2 className="section-headline">How YesChef works</h2>
          
          <div className="feature-grid">
            <div className="feature-item fade-in">
              <div className="feature-icon-large">📸</div>
              <h3>Capture</h3>
              <p>Photo, voice, or link—add recipes from anywhere in seconds</p>
            </div>

            <div className="feature-item fade-in">
              <div className="feature-icon-large">📁</div>
              <h3>Organize</h3>
              <p>All recipes in one searchable, beautifully organized collection</p>
            </div>

            <div className="feature-item fade-in">
              <div className="feature-icon-large">📅</div>
              <h3>Plan</h3>
              <p>Weekly meal planning with automatic grocery lists</p>
            </div>

            <div className="feature-item fade-in">
              <div className="feature-icon-large">🍳</div>
              <h3>Cook</h3>
              <p>Easy step-by-step cooking mode, ready when you are</p>
            </div>
          </div>
        </div>
      </section>

      {/* Section 3: Organize */}
      <section className="organize-section fade-in">
        <div className="section-container">
          <span className="section-label">Organize</span>
          <h2 className="section-headline">Your collection, beautifully organized</h2>
          
          <div className="app-screenshot-large">
            <div className="screenshot-placeholder large">
              <span>Screenshot: Recipe collection grid view</span>
              <div className="screenshot-caption">Browse your entire collection in one clean interface</div>
            </div>
          </div>

          <div className="feature-highlights">
            <div className="highlight-item fade-in">
              <div className="highlight-icon">�</div>
              <h4>Smart Search</h4>
              <p>Find recipes by ingredient, meal type, or time to cook</p>
            </div>
            
            <div className="highlight-item fade-in">
              <div className="highlight-icon">🏷️</div>
              <h4>Custom Categories</h4>
              <p>Organize your way with tags and collections</p>
            </div>
            
            <div className="highlight-item fade-in">
              <div className="highlight-icon">⭐</div>
              <h4>Quick Favorites</h4>
              <p>Mark and find your go-to recipes instantly</p>
            </div>
          </div>
        </div>
      </section>

      {/* Section 4: Plan */}
      <section className="plan-section fade-in">
        <div className="section-container">
          <span className="section-label">Plan</span>
          <h2 className="section-headline">Your week, organized and ready</h2>
          
          <div className="app-screenshot-large">
            <div className="screenshot-placeholder large">
              <span>Screenshot: Weekly meal planning calendar</span>
              <div className="screenshot-caption">Drag recipes into your week. Share with household. Done.</div>
            </div>
          </div>

          <div className="feature-highlights">
            <div className="highlight-item fade-in">
              <div className="highlight-icon">📅</div>
              <h4>Weekly Calendar</h4>
              <p>See breakfast, lunch, dinner, and snacks for the entire week</p>
            </div>
            
            <div className="highlight-item fade-in">
              <div className="highlight-icon">👥</div>
              <h4>Share with Household</h4>
              <p>Everyone knows what's for dinner—no more asking</p>
            </div>
            
            <div className="highlight-item fade-in">
              <div className="highlight-icon">🔄</div>
              <h4>Flexible Planning</h4>
              <p>Life happens. Rearrange meals in seconds</p>
            </div>
          </div>
        </div>
      </section>

      {/* Section 5: Shop */}
      <section className="shop-section fade-in">
        <div className="section-container">
          <span className="section-label">Shop</span>
          <h2 className="section-headline">Automatic grocery lists from your plan</h2>
          
          <div className="app-screenshot-large">
            <div className="screenshot-placeholder large">
              <span>Screenshot: Organized grocery list by categories</span>
              <div className="screenshot-caption">Ingredients organized by store section. Check off as you shop.</div>
            </div>
          </div>

          <div className="feature-highlights">
            <div className="highlight-item fade-in">
              <div className="highlight-icon">🛒</div>
              <h4>Auto-Generated</h4>
              <p>Your meal plan becomes a shopping list automatically</p>
            </div>
            
            <div className="highlight-item fade-in">
              <div className="highlight-icon">📋</div>
              <h4>Smart Categories</h4>
              <p>Organized by store section for efficient shopping</p>
            </div>
            
            <div className="highlight-item fade-in">
              <div className="highlight-icon">✓</div>
              <h4>Check Off Items</h4>
              <p>Track what you've grabbed as you shop</p>
            </div>
          </div>
        </div>
      </section>

      {/* Section 6: The Result - Simple Message */}
      <section className="result-section fade-in">
        <div className="result-content">
          <h2 className="result-headline">Everything in its place</h2>
          <p className="result-subtext">
            When your recipes are organized, meal planning becomes manageable.
            <br />When your week is planned, shopping becomes simple.
            <br />When shopping is simple, cooking becomes calm.
          </p>
          <button 
            className="result-cta-btn"
            onClick={() => handleCTAClick('result')}
          >
            Join the Waitlist
          </button>
        </div>
      </section>

      {/* Section 7: Community & Legacy */}
      <section id="community" className="legacy-section fade-in">
        <div className="legacy-container">
          <div className="legacy-content">
            <h2 className="legacy-headline">You're not just organizing recipes</h2>
            <h3 className="legacy-subheadline">You're building a family cookbook</h3>
            <p className="legacy-body">
              Every recipe you save becomes part of your household's story. 
              The dishes your kids will request when they visit. The favorites 
              they'll recreate in their own kitchens.
            </p>
            <p className="legacy-body">
              YesChef helps you preserve what matters while making today's 
              meal planning manageable.
            </p>
            <button 
              className="legacy-cta-btn"
              onClick={() => handleCTAClick('legacy')}
            >
              Start Your Collection
            </button>
          </div>
          <div className="legacy-visual">
            <div className="legacy-image-placeholder">
              <span>Multi-generational cooking or recipe card preservation</span>
            </div>
          </div>
        </div>
      </section>

      {/* Section 8: Social Proof */}
            {/* Simple Social Proof */}
      <section className="testimonials-section fade-in">
        <div className="section-container">
          <h2 className="testimonials-headline">Join families organizing their recipes</h2>
          <div className="testimonials-grid">
            <div className="testimonial-card fade-in">
              <p className="testimonial-text">"Finally have all my mom's recipes in one place."</p>
              <p className="testimonial-author">— Sarah M.</p>
            </div>

            <div className="testimonial-card fade-in">
              <p className="testimonial-text">"Voice recording changed everything for preserving grandma's recipes."</p>
              <p className="testimonial-author">— Michael T.</p>
            </div>

            <div className="testimonial-card fade-in">
              <p className="testimonial-text">"Meal planning doesn't feel like a chore anymore."</p>
              <p className="testimonial-author">— Jennifer K.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA - Email Capture */}
      <section id="community" className="final-cta-section fade-in">
        <h2 className="final-cta-headline">Start organizing your recipes today</h2>
        <p className="final-cta-subheadline">
          Join families preserving their recipes with YesChef
        </p>
        
        {/* Email Capture Form */}
        <form onSubmit={handleWaitlistSubmit} className="hero-email-form">
          <input
            type="email"
            placeholder="Enter your email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="hero-email-input"
          />
          <button 
            type="submit" 
            className="final-cta-btn"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Joining...' : 'Join Waitlist'}
          </button>
        </form>
        
        {submitSuccess && (
          <div className="hero-success-message">
            ✓ You're on the list! We'll reach out soon.
          </div>
        )}
        
        <p className="final-cta-subtext">
          Invite-only beta · iOS & Android coming soon
        </p>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <div className="footer-container">
          <div className="footer-section">
            <div className="footer-logo">
              <div className="logo-icon">
                <img src="/images/yeschef-logo.png" alt="YesChef Logo" className="logo-img" />
              </div>
              <span className="logo-text">YesChef</span>
            </div>
            <p className="footer-tagline">
              Preserve recipes. Plan meals. Ease the overwhelm.
            </p>
          </div>

          <div className="footer-section">
            <h4>Product</h4>
            <a href="#how-it-works">How It Works</a>
            <a href="#features">Features</a>
            <a href="#community">Community</a>
          </div>

          <div className="footer-section">
            <h4>Company</h4>
            <a href="#about">About</a>
            <a href="#privacy">Privacy Policy</a>
            <a href="#terms">Terms of Service</a>
            <a href="#contact">Contact</a>
          </div>
        </div>
        <div className="footer-bottom">
          <p>© 2025 YesChef. All rights reserved.</p>
        </div>
      </footer>


    </div>
  );
};

export default LandingPage;
