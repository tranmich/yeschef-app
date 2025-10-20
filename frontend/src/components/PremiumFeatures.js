import React, { useState } from 'react';
import './PremiumFeatures.css';

const PremiumFeatures = ({ feature, onUpgrade, onClose }) => {
  const [showPlans, setShowPlans] = useState(false);

  const premiumFeatures = {
    'unlimited-friends': {
      title: '👥 Unlimited Friends',
      description: 'Connect with unlimited friends and family members',
      current: 'Limited to 10 friends',
      premium: 'Unlimited friends & households',
      icon: '👥',
      color: '#AAC6AD'
    },
    'advanced-sharing': {
      title: '📤 Advanced Recipe Sharing',
      description: 'Share recipes with custom permissions and private groups',
      current: 'Basic recipe sharing',
      premium: 'Private groups, custom permissions, bulk sharing',
      icon: '📤',
      color: '#f59e0b'
    },
    'meal-planning-pro': {
      title: '🍽️ Pro Meal Planning',
      description: 'Advanced meal planning with shopping lists and nutritional info',
      current: 'Basic weekly planning',
      premium: 'Monthly planning, nutrition tracking, automated shopping lists',
      icon: '🍽️',
      color: '#8b5cf6'
    },
    'community-analytics': {
      title: '📊 Community Analytics',
      description: 'See detailed analytics for your shared recipes',
      current: 'Basic likes and saves',
      premium: 'Detailed analytics, trending recipes, engagement insights',
      icon: '📊',
      color: '#06b6d4'
    },
    'premium-support': {
      title: '💬 Priority Support',
      description: 'Get premium customer support and early access to features',
      current: 'Community support',
      premium: '24/7 priority support, early access to new features',
      icon: '💬',
      color: '#ef4444'
    }
  };

  const plans = [
    {
      id: 'monthly',
      name: 'Monthly Plan',
      price: '$4.99',
      period: '/month',
      description: 'Perfect for getting started',
      popular: false,
      features: [
        'Unlimited friends & households',
        'Advanced recipe sharing',
        'Pro meal planning',
        'Community analytics',
        'Priority support',
        'Early access to features'
      ]
    },
    {
      id: 'yearly',
      name: 'Yearly Plan',
      price: '$39.99',
      period: '/year',
      description: 'Best value - Save 33%!',
      popular: true,
      savings: 'Save $20/year',
      features: [
        'Everything in Monthly Plan',
        'Additional storage (10GB)',
        'Custom recipe categories',
        'Advanced export options',
        'Family sharing (up to 6 members)',
        'Exclusive premium recipes'
      ]
    }
  ];

  const currentFeature = premiumFeatures[feature] || premiumFeatures['unlimited-friends'];

  const handleUpgrade = (planId) => {
    console.log('Upgrading to plan:', planId);
    if (onUpgrade) {
      onUpgrade(planId);
    }
    
    // In real implementation, this would initiate payment flow
    alert(`Redirecting to payment for ${plans.find(p => p.id === planId)?.name}...`);
  };

  if (showPlans) {
    return (
      <div className="premium-overlay">
        <div className="premium-modal large-premium-modal">
          <div className="premium-header">
            <div className="header-content">
              <h2>🌟 Upgrade to Premium</h2>
              <p>Unlock all social features and take your cooking experience to the next level!</p>
            </div>
            <button className="close-button" onClick={onClose}>×</button>
          </div>

          <div className="plans-section">
            <div className="plans-grid">
              {plans.map(plan => (
                <div key={plan.id} className={`plan-card ${plan.popular ? 'popular' : ''}`}>
                  {plan.popular && <div className="popular-badge">Most Popular</div>}
                  
                  <div className="plan-header">
                    <h3 className="plan-name">{plan.name}</h3>
                    <div className="plan-pricing">
                      <span className="plan-price">{plan.price}</span>
                      <span className="plan-period">{plan.period}</span>
                    </div>
                    <p className="plan-description">{plan.description}</p>
                    {plan.savings && (
                      <div className="savings-badge">{plan.savings}</div>
                    )}
                  </div>

                  <div className="plan-features">
                    <ul>
                      {plan.features.map((feature, index) => (
                        <li key={index}>
                          <span className="feature-check">✅</span>
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <button
                    className={`upgrade-button ${plan.popular ? 'popular' : ''}`}
                    onClick={() => handleUpgrade(plan.id)}
                  >
                    Choose {plan.name}
                  </button>
                </div>
              ))}
            </div>
          </div>

          <div className="premium-footer">
            <div className="guarantee-section">
              <h4>💯 30-Day Money-Back Guarantee</h4>
              <p>Try Premium risk-free! Cancel anytime within 30 days for a full refund.</p>
            </div>
            
            <div className="testimonials">
              <h4>❤️ What Our Premium Users Say</h4>
              <div className="testimonials-grid">
                <div className="testimonial">
                  <p>"Premium has completely transformed how I plan meals with my family!"</p>
                  <span>- Sarah M.</span>
                </div>
                <div className="testimonial">
                  <p>"The community features are amazing. I've discovered so many great recipes!"</p>
                  <span>- Mike R.</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="premium-overlay">
      <div className="premium-modal">
        <div className="premium-header">
          <div className="feature-icon" style={{ backgroundColor: currentFeature.color }}>
            {currentFeature.icon}
          </div>
          <div className="header-content">
            <h2>{currentFeature.title}</h2>
            <p>{currentFeature.description}</p>
          </div>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="feature-comparison">
          <div className="comparison-item current">
            <div className="comparison-header">
              <h3>🆓 Free Plan</h3>
              <span className="plan-badge free">Current</span>
            </div>
            <p className="comparison-description">{currentFeature.current}</p>
          </div>

          <div className="comparison-item premium">
            <div className="comparison-header">
              <h3>🌟 Premium Plan</h3>
              <span className="plan-badge premium">Upgrade</span>
            </div>
            <p className="comparison-description">{currentFeature.premium}</p>
          </div>
        </div>

        <div className="premium-benefits">
          <h3>🎯 What You'll Get with Premium</h3>
          <div className="benefits-grid">
            {Object.entries(premiumFeatures).map(([key, featureInfo]) => (
              <div key={key} className={`benefit-item ${key === feature ? 'highlighted' : ''}`}>
                <div className="benefit-icon">{featureInfo.icon}</div>
                <div className="benefit-content">
                  <h4>{featureInfo.title.replace(/^[^\s]+\s/, '')}</h4>
                  <p>{featureInfo.premium}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="premium-actions">
          <button
            className="view-plans-button"
            onClick={() => setShowPlans(true)}
          >
            🌟 View Premium Plans
          </button>
          <button
            className="maybe-later-button"
            onClick={onClose}
          >
            Maybe Later
          </button>
        </div>

        <div className="premium-note">
          <p>
            💡 <strong>Limited Time:</strong> Get 30% off your first year when you upgrade today!
          </p>
        </div>
      </div>
    </div>
  );
};

export default PremiumFeatures;