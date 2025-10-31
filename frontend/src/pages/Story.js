import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Story.css';

const Story = () => {
  const navigate = useNavigate();

  return (
    <div className="story-page">
      {/* Logo - Top Left Header */}
      <div className="logo-header">
        <img src="/images/yeschef-logo.png" alt="YesChef" className="logo-header-img" />
        <span className="logo-header-text">YesChef</span>
      </div>

      {/* Back Button - Top Right */}
      <button 
        className="back-btn-top"
        onClick={() => navigate('/')}
      >
        ← Back
      </button>

      {/* Story Content */}
      <section className="story-hero">
        <div className="story-container">
          <h1 className="story-headline">About Me</h1>
          
          <div className="story-content">
            <p>
              Hi, I'm Michael — the creator of YesChef.
            </p>
            
            <p>
              My love for cooking started over twenty years ago, back in college, when I moved into my first 
              apartment with my girlfriend. Cooking shows were everywhere, and I found myself recreating dishes 
              with a Vietnamese twist. It was the first time I realized how creative cooking could be — and it's 
              a passion that's stayed with me ever since.
            </p>
            
            <p>
              At first, cooking was about independence — saving money, making something for myself, figuring 
              things out. But over time, it became about family and self-expression. These days, it's also my 
              focus — I spend hours experimenting with broths and soup-based meals, learning how to build deep 
              flavor with fewer, more intentional ingredients. I've come to believe that good flavor can be 
              simple, and that being purposeful in how we cook leads to better, more meaningful meals.
            </p>
            
            <p>
              YesChef grew out of that mindset. A few years ago, when my wife and I decided to stop eating out 
              and cook all our meals at home to save for our wedding, I realized how chaotic meal planning really 
              was. Recipes were scattered across food blogs, emails, notebooks, and memory. Grocery lists lived in 
              separate apps and got lost in the shuffle. It worked, but barely. I wanted a better way to organize 
              it all — not just for me, but for anyone who loves to cook and share food.
            </p>
            
            <p>
              Most recipe apps out there stop at saving recipes. They're designed for individuals, not for 
              households or communities. I wanted to build something that went further — something that helped 
              people plan, cook, and communicate around food together. Cooking, after all, has never been a solo 
              act. It's a shared experience.
            </p>
            
            <p>
              That belief deepened during a trip to Los Angeles, when I met my wife's aunties for the first time. 
              They told me the stories of how they learned to cook — passing recipes down through generations, by 
              memory and conversation. I realized that if we don't capture that knowledge, it disappears. And I 
              knew I wasn't alone in feeling that loss.
            </p>
            
            <p>
              That's why I built YesChef — to create a space where recipes and traditions can live, grow, and be 
              shared. Where anyone can start small, plan one meal a week, and build from there. It's not just 
              about cooking better, it's about connecting through food — learning, saving, and giving back to the 
              people around you.
            </p>
            
            <p className="story-closing">
              Because at the end of the day, that's what cooking has always been for me: <strong>doing something 
              for others.</strong>
            </p>
            
            <p className="signature">— Michael</p>
          </div>

          {/* CTA to go back */}
          <div className="story-cta">
            <button 
              className="primary-button"
              onClick={() => navigate('/')}
            >
              Back to Home
            </button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Story;
