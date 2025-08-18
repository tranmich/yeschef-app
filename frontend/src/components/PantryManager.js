import React, { useState, useEffect } from 'react';
import './PantryManager.css';

const PantryManager = () => {
  const [pantryItems, setPantryItems] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pantryStatus, setPantryStatus] = useState(null);
  const [pantryEnabled, setPantryEnabled] = useState(true);
  const [availableIngredients, setAvailableIngredients] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchPantryData();
    checkPantryStatus();
    loadAvailableIngredients();
  }, []);

  const fetchPantryData = async () => {
    try {
      setIsLoading(true);
      // For now, use mock data since backend pantry endpoints might not be fully implemented
      // TODO: Replace with actual API call to backend pantry system
      setTimeout(() => {
        setPantryItems([
          { id: 1, name: 'Chicken Breast', amount: 'some', category: 'protein' },
          { id: 3, name: 'Onion', amount: 'plenty', category: 'produce' },
          { id: 5, name: 'Olive Oil', amount: 'some', category: 'cooking' }
        ]);
        setIsLoading(false);
      }, 500);
    } catch (err) {
      setError('Failed to load pantry items');
      setIsLoading(false);
    }
  };

  const loadAvailableIngredients = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/ingredients`);
      if (response.ok) {
        const data = await response.json();
        setAvailableIngredients(data.ingredients || []);
      } else {
        console.log('Failed to load ingredients, using fallback');
        setAvailableIngredients([
          { name: 'Chicken Breast', category: 'protein' },
          { name: 'Rice', category: 'grain' },
          { name: 'Onion', category: 'produce' },
          { name: 'Garlic', category: 'produce' }
        ]);
      }
    } catch (err) {
      console.log('Ingredients loading error:', err);
      setAvailableIngredients([]);
    }
  };

  const checkPantryStatus = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/pantry/status`);
      if (response.ok) {
        const data = await response.json();
        setPantryStatus(data.status);
        setPantryEnabled(data.enabled);
      }
    } catch (err) {
      console.log('Pantry status check failed:', err);
      setPantryStatus('🟢 PANTRY: ENABLED (Test Mode)');
    }
  };

  const togglePantrySystem = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/config/pantry/toggle`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setPantryEnabled(data.pantry_enabled);
        setPantryStatus(data.config.pantry.status);
        
        // Reload pantry items if enabled
        if (data.pantry_enabled) {
          await loadPantryItems();
        }
      } else {
        console.error('Failed to toggle pantry system');
      }
    } catch (err) {
      console.error('Pantry toggle error:', err);
    }
  };

  const addPantryItem = (ingredient) => {
    const newItem = {
      id: Date.now(), // Generate temporary ID
      name: ingredient.name,
      category: ingredient.category,
      amount: 'some'
    };
    setPantryItems(prev => [...prev, newItem]);
    setSearchTerm(''); // Clear search after adding
  };

  const removePantryItem = (ingredientId) => {
    setPantryItems(prev => prev.filter(item => item.id !== ingredientId));
  };

  const updateAmount = (ingredientId, newAmount) => {
    setPantryItems(prev => 
      prev.map(item => 
        item.id === ingredientId ? { ...item, amount: newAmount } : item
      )
    );
  };

  const getAmountColor = (amount) => {
    switch (amount) {
      case 'plenty': return '#4CAF50';
      case 'some': return '#FF9800';
      case 'low': return '#F44336';
      default: return '#666';
    }
  };

  if (isLoading) {
    return (
      <div className="pantry-manager">
        <div className="loading">Loading pantry...</div>
      </div>
    );
  }

  return (
    <div className="pantry-manager">
      <div className="pantry-header">
        <div className="pantry-title-section">
          <h2>🥕 Pantry Management</h2>
          <button 
            onClick={togglePantrySystem}
            className={`pantry-toggle-btn ${pantryEnabled ? 'enabled' : 'disabled'}`}
            title={`${pantryEnabled ? 'Disable' : 'Enable'} Pantry System`}
          >
            {pantryEnabled ? '🟢 ON' : '🔴 OFF'}
          </button>
        </div>
        {pantryStatus && (
          <div className="pantry-status">{pantryStatus}</div>
        )}
        <p>Track your ingredients and discover recipes you can make!</p>
      </div>

      {error && (
        <div className="error-message">{error}</div>
      )}

      <div className="pantry-sections">
        
        {/* Current Pantry Items */}
        <div className="pantry-section">
          <h3>Your Pantry ({pantryItems.length} items)</h3>
          {pantryItems.length === 0 ? (
            <div className="empty-pantry">
              <p>Your pantry is empty. Add some ingredients below!</p>
            </div>
          ) : (
            <div className="pantry-items">
              {pantryItems.map(item => (
                <div key={item.id} className="pantry-item">
                  <div className="item-info">
                    <span className="item-name">{item.name}</span>
                    <span className="item-category">{item.category}</span>
                  </div>
                  <div className="item-controls">
                    <select 
                      value={item.amount} 
                      onChange={(e) => updateAmount(item.id, e.target.value)}
                      className="amount-selector"
                      style={{ borderColor: getAmountColor(item.amount) }}
                    >
                      <option value="plenty">Plenty</option>
                      <option value="some">Some</option>
                      <option value="low">Low</option>
                    </select>
                    <button 
                      onClick={() => removePantryItem(item.id)}
                      className="remove-button"
                    >
                      ❌
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Add New Items */}
        <div className="pantry-section">
          <h3>Add Ingredients</h3>
          <div className="ingredient-search">
            <input
              type="text"
              placeholder="Search ingredients..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="ingredient-search-input"
            />
          </div>
          <div className="available-ingredients">
            {availableIngredients
              .filter(ingredient => {
                const alreadyAdded = pantryItems.find(item => item.name === ingredient.name);
                const matchesSearch = ingredient.name.toLowerCase().includes(searchTerm.toLowerCase());
                return !alreadyAdded && matchesSearch;
              })
              .slice(0, 20) // Limit to 20 results
              .map((ingredient, index) => (
                <button
                  key={`${ingredient.name}-${index}`}
                  onClick={() => addPantryItem(ingredient)}
                  className="add-ingredient-button"
                >
                  <span className="ingredient-name">{ingredient.name}</span>
                  <span className="ingredient-category">{ingredient.category}</span>
                  <span className="add-icon">➕</span>
                </button>
              ))}
          </div>
          {searchTerm && availableIngredients.filter(ingredient => 
            ingredient.name.toLowerCase().includes(searchTerm.toLowerCase())
          ).length === 0 && (
            <div className="no-results">No ingredients found matching "{searchTerm}"</div>
          )}
        </div>

      </div>

      <div className="pantry-footer">
        <div className="pantry-stats">
          <div className="stat">
            <span className="stat-number">{pantryItems.length}</span>
            <span className="stat-label">Total Items</span>
          </div>
          <div className="stat">
            <span className="stat-number">{pantryItems.filter(item => item.amount === 'low').length}</span>
            <span className="stat-label">Running Low</span>
          </div>
          <div className="stat">
            <span className="stat-number">{new Set(pantryItems.map(item => item.category)).size}</span>
            <span className="stat-label">Categories</span>
          </div>
        </div>
        
        <div className="feature-note">
          <p>💡 <strong>Next:</strong> Recipe matching will show which recipes you can make with your pantry items!</p>
        </div>
      </div>
    </div>
  );
};

export default PantryManager;
