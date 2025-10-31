import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Privacy.css';

const Privacy = () => {
  const navigate = useNavigate();

  return (
    <div className="privacy-page">
      <button className="back-btn" onClick={() => navigate('/')}>
        ← Back to Home
      </button>

      <div className="privacy-container">
        <h1>Privacy Policy for YesChef</h1>
        
        <p className="effective-date">
          <strong>Effective Date:</strong> September 29, 2025<br />
          <strong>Last Updated:</strong> September 29, 2025
        </p>

        <section>
          <h2>1. Introduction</h2>
          <p>
            Welcome to YesChef ("we," "our," or "us"). This Privacy Policy explains how we collect, use, disclose, 
            and safeguard your information when you use our mobile application and related services (collectively, the "Service").
          </p>
        </section>

        <section>
          <h2>2. Information We Collect</h2>
          
          <h3>2.1 Personal Information You Provide</h3>
          <ul>
            <li><strong>Account Information:</strong> Email address, username, and password when you create an account</li>
            <li><strong>Profile Information:</strong> Custom avatar selections (background and icon preferences)</li>
            <li><strong>Recipe Data:</strong> Recipes you save, create, or share with the community</li>
            <li><strong>Meal Plans:</strong> Your meal planning preferences and schedules</li>
            <li><strong>Grocery Lists:</strong> Shopping lists you create and manage</li>
            <li><strong>Community Content:</strong> Posts, comments, and shared recipes you contribute</li>
          </ul>

          <h3>2.2 Automatically Collected Information</h3>
          <ul>
            <li><strong>Usage Data:</strong> How you interact with our app (features used, time spent)</li>
            <li><strong>Device Information:</strong> Device type, operating system, app version</li>
            <li><strong>Performance Data:</strong> Crash reports and app performance metrics</li>
          </ul>
        </section>

        <section>
          <h2>3. How We Use Your Information</h2>
          <p>We use your information to:</p>
          <ul>
            <li><strong>Provide Services:</strong> Enable core app functionality (recipes, meal planning, grocery lists)</li>
            <li><strong>Personalization:</strong> Customize your experience with saved preferences and recommendations</li>
            <li><strong>Community Features:</strong> Enable recipe sharing and social interactions with friends</li>
            <li><strong>Account Management:</strong> Authenticate your account and provide customer support</li>
            <li><strong>Improve Our Service:</strong> Analyze usage patterns to enhance app performance and features</li>
            <li><strong>Communication:</strong> Send important updates about your account or the service</li>
          </ul>
        </section>

        <section>
          <h2>4. Information Sharing and Disclosure</h2>
          
          <h3>4.1 We Do NOT Sell Your Personal Information</h3>
          
          <h3>4.2 We May Share Information:</h3>
          <ul>
            <li><strong>With Your Consent:</strong> When you explicitly choose to share content publicly</li>
            <li><strong>Service Providers:</strong> Railway (cloud hosting), Expo (mobile platform)</li>
            <li><strong>Legal Requirements:</strong> When required by law or to protect our rights</li>
          </ul>
        </section>

        <section>
          <h2>5. Data Storage and Security</h2>
          
          <h3>5.1 Security Measures</h3>
          <ul>
            <li><strong>Encryption:</strong> Data transmission is encrypted using industry-standard protocols</li>
            <li><strong>Authentication:</strong> Secure login with hashed passwords</li>
            <li><strong>Access Controls:</strong> Limited access to personal data by authorized personnel only</li>
          </ul>
        </section>

        <section>
          <h2>6. Your Rights and Choices</h2>
          
          <h3>6.1 Account Control</h3>
          <ul>
            <li><strong>Access:</strong> View and update your profile information anytime</li>
            <li><strong>Data Portability:</strong> Request a copy of your data in a portable format</li>
            <li><strong>Deletion:</strong> Delete your account and associated data through the app settings</li>
          </ul>

          <h3>6.2 Children's Privacy</h3>
          <ul>
            <li>Our service is not intended for children under 13</li>
            <li>We do not knowingly collect personal information from children under 13</li>
            <li>If we learn we have collected such information, we will delete it promptly</li>
          </ul>
        </section>

        <section>
          <h2>7. International Users</h2>
          <p>
            Your data may be stored and processed in the United States or other countries where our service providers operate.
          </p>
        </section>

        <section>
          <h2>8. Changes to This Policy</h2>
          <p>
            We may update this Privacy Policy from time to time. We will notify you of any changes by posting the new 
            Privacy Policy on this page and updating the "Last Updated" date.
          </p>
        </section>

        <section>
          <h2>9. Contact Us</h2>
          <p>
            If you have questions about this Privacy Policy, please contact us at:
          </p>
          <p>
            <strong>Email:</strong> <a href="mailto:hello@yeschefapp.io">hello@yeschefapp.io</a>
          </p>
        </section>

        <div className="footer-note">
          <p>© 2025 YesChef. All rights reserved.</p>
        </div>
      </div>
    </div>
  );
};

export default Privacy;
