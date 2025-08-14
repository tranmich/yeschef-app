import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../utils/api';
import './Categories.css';

const Categories = () => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await api.getCategories();
      setCategories(data.data || []);
    } catch (err) {
      setError('Failed to load categories. Our kitchen might be a bit smoky! 🔥');
      console.error('Categories fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getCategoryEmoji = (categoryName) => {
    const emojis = {
      'appetizers': '🥗',
      'breakfast': '🍳',
      'lunch': '🥪',
      'dinner': '🍽️',
      'desserts': '🍰',
      'snacks': '🥨',
      'beverages': '🥤',
      'salads': '🥙',
      'soups': '🍲',
      'main-dish': '🍖',
      'side-dish': '🥔',
      'bread': '🍞',
      'pasta': '🍝',
      'pizza': '🍕',
      'seafood': '🐟',
      'vegetarian': '🥬',
      'vegan': '🌱',
      'healthy': '💚',
      'comfort-food': '🤗',
      'quick-easy': '⚡'
    };
    
    const normalizedName = categoryName.toLowerCase().replace(/[\s_]/g, '-');
    return emojis[normalizedName] || '🍴';
  };

  const getCategoryDescription = (categoryName) => {
    const descriptions = {
      'appetizers': 'Start your meal right with these crowd-pleasers!',
      'breakfast': 'Rise and shine with morning fuel that actually tastes good!',
      'lunch': 'Midday munchies that hit different!',
      'dinner': 'End your day with a bang - these are the main events!',
      'desserts': 'Life is short, eat dessert! (Maybe first?) 🤫',
      'snacks': 'For when you need a little something but not a whole something!',
      'beverages': 'Liquid happiness in various forms!',
      'salads': 'Who said healthy can\'t be exciting?',
      'soups': 'Warm hugs in a bowl - exactly what you need!',
      'main-dish': 'The stars of the show, ready for their close-up!',
      'side-dish': 'Supporting actors that often steal the scene!',
      'bread': 'Because everything is better with carbs. Fight me! 🥖',
      'pasta': 'Italian comfort in every single bite!',
      'pizza': 'The ultimate crowd-pleaser - no explanations needed!',
      'seafood': 'From the ocean to your plate with love!',
      'vegetarian': 'Plant-powered deliciousness that even meat-lovers adore!',
      'vegan': 'Proof that plants can party too! 🌱',
      'healthy': 'Good-for-you food that doesn\'t taste like punishment!',
      'comfort-food': 'For when you need food that feels like a warm hug!',
      'quick-easy': 'Fast, simple, and still absolutely delicious!'
    };
    
    const normalizedName = categoryName.toLowerCase().replace(/[\s_]/g, '-');
    return descriptions[normalizedName] || 'Delicious recipes waiting to be discovered!';
  };

  if (loading) {
    return (
      <div className="categories-page">
        <div className="loading-container">
          <div className="loading-spinner">🍽️</div>
          <h2>Organizing our kitchen...</h2>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="categories-page">
        <div className="error-container">
          <h2>Oops! 😅</h2>
          <p>{error}</p>
          <button onClick={fetchCategories} className="retry-button">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="categories-page">
      <div className="categories-header">
        <h1>Explore by Category</h1>
        <p className="categories-subtitle">
          What are you in the mood for? We've organized everything so you can find exactly what you're craving! 🎯
        </p>
      </div>

      <div className="categories-grid">
        {categories.map((category, index) => (
          <Link 
            key={index}
            to={`/search?category=${encodeURIComponent(category.name)}`}
            className="category-card"
          >
            <div className="category-emoji">
              {getCategoryEmoji(category.name)}
            </div>
            <h3 className="category-name">
              {category.name.replace(/[-_]/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </h3>
            <p className="category-description">
              {getCategoryDescription(category.name)}
            </p>
            <div className="category-count">
              {category.count} recipe{category.count !== 1 ? 's' : ''}
            </div>
          </Link>
        ))}
      </div>

      {categories.length === 0 && (
        <div className="no-categories">
          <h2>No categories found! 🤔</h2>
          <p>Our kitchen is still getting organized. Check back soon!</p>
        </div>
      )}

      <div className="categories-footer">
        <div className="hungie-tip">
          <h3>🔥 Pro Tip from Hungie:</h3>
          <p>
            Can't decide? Close your eyes, scroll, and point! Sometimes the best meals come from spontaneous choices. 
            Or just make everything - we won't judge! 😄
          </p>
        </div>
      </div>
    </div>
  );
};

export default Categories;
