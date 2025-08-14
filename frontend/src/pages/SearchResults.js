import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import RecipeCard from '../components/RecipeCard';
import { api } from '../utils/api';
import './SearchResults.css';

const SearchResults = () => {
  const [searchParams] = useSearchParams();
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const query = searchParams.get('q') || '';

  useEffect(() => {
    if (query) {
      searchRecipes(query);
    }
  }, [query]);

  const searchRecipes = async (searchQuery) => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await api.searchRecipes(searchQuery);
      setResults(data.data || []);
    } catch (err) {
      setError('Oops! Something went wrong with your search. Try again?');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getHungieResponse = (query, resultCount) => {
    const responses = {
      chicken: [
        `Cluck yeah! 🐔 Found ${resultCount} chicken recipes that'll make you wing it in the kitchen!`,
        `Chicken dinner winner! 🏆 I've got ${resultCount} poultry-perfect recipes for you!`
      ],
      burger: [
        `Burger time! 🍔 ${resultCount} patty-perfect recipes coming right up!`,
        `Let's beef up your meal game! 💪 Found ${resultCount} burger recipes that are well done!`
      ],
      pasta: [
        `Pasta la vista, boring dinners! 🍝 ${resultCount} noodle-icious recipes ready!`,
        `You're not going anywhere without these ${resultCount} pasta-bilities! 🇮🇹`
      ],
      dessert: [
        `Sweet dreams are made of these! 🍰 ${resultCount} dessert recipes to satisfy your sweet tooth!`,
        `Life's short, eat dessert first! 🧁 Found ${resultCount} sweet treats for you!`
      ]
    };

    // Find matching category or use default
    const category = Object.keys(responses).find(cat => 
      query.toLowerCase().includes(cat)
    );
    
    if (category) {
      const categoryResponses = responses[category];
      return categoryResponses[Math.floor(Math.random() * categoryResponses.length)];
    }
    
    // Default responses
    const defaultResponses = [
      `Nom nom! 😋 Found ${resultCount} delicious recipes that match your craving!`,
      `Your taste buds are in for a treat! 🎉 ${resultCount} amazing recipes coming your way!`,
      `Cooking magic activated! ✨ ${resultCount} recipes ready to satisfy your hunger!`
    ];
    
    return defaultResponses[Math.floor(Math.random() * defaultResponses.length)];
  };

  if (loading) {
    return (
      <div className="search-results">
        <div className="loading-container">
          <div className="loading-spinner">🍳</div>
          <h2>Cooking up some delicious results...</h2>
          <p>Hold tight while I search through my recipe collection!</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="search-results">
        <div className="error-container">
          <h2>Oops! 😅</h2>
          <p>{error}</p>
          <button 
            onClick={() => searchRecipes(query)}
            className="retry-button"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="search-results">
      <div className="search-header">
        <h1>Search Results for "{query}"</h1>
        <div className="hungie-response">
          <p>{getHungieResponse(query, results.length)}</p>
        </div>
      </div>

      {results.length === 0 ? (
        <div className="no-results">
          <h2>Hmm, I couldn't find any recipes for that! 🤔</h2>
          <p>But don't worry, here are some suggestions:</p>
          <div className="suggestions">
            <p>Try searching for:</p>
            <ul>
              <li>🐔 "chicken" for chicken dishes</li>
              <li>🍔 "burger" for burger recipes</li>
              <li>🍝 "pasta" for pasta dishes</li>
              <li>🍰 "dessert" for sweet treats</li>
              <li>🥗 "salad" for fresh options</li>
            </ul>
          </div>
        </div>
      ) : (
        <div className="results-container">
          <div className="results-count">
            Found {results.length} recipe{results.length !== 1 ? 's' : ''}
          </div>
          
          <div className="results-grid">
            {results.map(recipe => (
              <RecipeCard key={recipe.id} recipe={recipe} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchResults;
