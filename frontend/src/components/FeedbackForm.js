import React, { useState } from 'react';
import './FeedbackForm.css';

const FeedbackForm = ({ onClose, onSubmit }) => {
  const [feedback, setFeedback] = useState('');
  const [rating, setRating] = useState(5);
  const [email, setEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      // For MVP, we'll just log feedback to console
      // In production, you'd send this to your analytics service
      const feedbackData = {
        feedback,
        rating,
        email: email || 'anonymous',
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent
      };

      console.log('User Feedback:', feedbackData);
      
      // Track feedback submission
      if (window.gtag) {
        window.gtag('event', 'feedback_submitted', {
          rating: rating,
          has_email: !!email
        });
      }

      onSubmit(feedbackData);
      onClose();
    } catch (error) {
      console.error('Feedback submission error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="feedback-overlay">
      <div className="feedback-modal">
        <div className="feedback-header">
          <h3>Help Make Hungie Better! 🍴</h3>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        <form onSubmit={handleSubmit} className="feedback-form">
          <div className="rating-section">
            <label>How would you rate your experience?</label>
            <div className="star-rating">
              {[1, 2, 3, 4, 5].map(star => (
                <button
                  key={star}
                  type="button"
                  className={`star ${rating >= star ? 'filled' : ''}`}
                  onClick={() => setRating(star)}
                >
                  ⭐
                </button>
              ))}
            </div>
          </div>

          <div className="feedback-section">
            <label htmlFor="feedback">What did you think? Any suggestions?</label>
            <textarea
              id="feedback"
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder="I love the substitution feature! It would be cool if..."
              rows={4}
              required
            />
          </div>

          <div className="email-section">
            <label htmlFor="email">Email (optional - for updates):</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="chef@example.com"
            />
          </div>

          <div className="form-actions">
            <button type="button" onClick={onClose} className="cancel-btn">
              Maybe Later
            </button>
            <button type="submit" disabled={isSubmitting} className="submit-btn">
              {isSubmitting ? 'Sending...' : 'Send Feedback'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default FeedbackForm;
