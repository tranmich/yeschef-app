import React, { useState, useEffect, useMemo } from 'react';
import { usePantry } from '../hooks/usePantry';
import './PantryManager.css';

const PantryManager = () => {
  // Use shared pantry hook
  const {
    pantryItems,
    addPantryItem: addToPantry,
    removePantryItem,
    updatePantryAmount
  } = usePantry();

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pantryStatus, setPantryStatus] = useState(null);
  const [pantryEnabled, setPantryEnabled] = useState(true);
  const [availableIngredients, setAvailableIngredients] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchSuggestions, setSearchSuggestions] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  
  // Section visibility state
  const [expandedSections, setExpandedSections] = useState({
    spices: true,      // Spices open by default (highest value)
    dryGoods: false,   // Dry goods collapsed by default
    freshWeek: false   // Fresh this week collapsed by default
  });

  useEffect(() => {
    checkPantryStatus();
    loadAvailableIngredients();
    setIsLoading(false); // Since pantry data comes from hook
  }, []);

  // Debug: Monitor pantryItems changes
  useEffect(() => {
    console.log('🔄 PantryManager - pantryItems state updated:', pantryItems.length, 'items');
    console.log('🔄 PantryManager - Items:', pantryItems.map(item => `${item.name} (${item.category})`));
  }, [pantryItems]);

  // Search for ingredients as user types
  useEffect(() => {
    if (searchTerm.length >= 2) {
      searchIngredients(searchTerm);
    } else {
      setSearchSuggestions([]);
      setShowSuggestions(false);
    }
  }, [searchTerm]);

  const loadAvailableIngredients = async () => {
    try {
      console.log('🔍 Loading ingredients from API...');
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/ingredients`);
      if (response.ok) {
        const data = await response.json();
        console.log('✅ Ingredients loaded from API:', {
          count: data.ingredients?.length || 0,
          sample: data.ingredients?.slice(0, 5) || []
        });
        setAvailableIngredients(data.ingredients || []);
      } else {
        console.log('⚠️ Failed to load ingredients, using smart fallback');
        // Enhanced fallback with proper categorization
        setAvailableIngredients([
          // Spices - High value, low maintenance
          { name: 'Garlic Powder', category: 'spices' },
          { name: 'Black Pepper', category: 'spices' },
          { name: 'Salt', category: 'spices' },
          { name: 'Paprika', category: 'spices' },
          { name: 'Cumin', category: 'spices' },
          { name: 'Oregano', category: 'spices' },
          { name: 'Basil', category: 'spices' },
          { name: 'Thyme', category: 'spices' },
          { name: 'Red Pepper Flakes', category: 'spices' },
          { name: 'Onion Powder', category: 'spices' },
          
          // Dry goods - Medium value, medium maintenance
          { name: 'Pasta', category: 'dryGoods' },
          { name: 'Rice', category: 'dryGoods' },
          { name: 'Flour', category: 'dryGoods' },
          { name: 'Olive Oil', category: 'dryGoods' },
          { name: 'Canned Beans', category: 'dryGoods' },
          { name: 'Canned Tomatoes', category: 'dryGoods' },
          { name: 'Quinoa', category: 'dryGoods' },
          { name: 'Oats', category: 'dryGoods' },
          { name: 'Coconut Oil', category: 'dryGoods' },
          { name: 'Honey', category: 'dryGoods' },
          
          // Fresh items - For "this week" only
          { name: 'Chicken Breast', category: 'fresh' },
          { name: 'Ground Beef', category: 'fresh' },
          { name: 'Onion', category: 'fresh' },
          { name: 'Bell Pepper', category: 'fresh' },
          { name: 'Spinach', category: 'fresh' },
          { name: 'Broccoli', category: 'fresh' },
          { name: 'Tomato', category: 'fresh' },
          { name: 'Lemon', category: 'fresh' }
        ]);
      }
    } catch (err) {
      console.log('❌ Ingredients loading error:', err);
      setAvailableIngredients([]);
    }
  };

  // Smart category mapping for existing items
  const getCategoryFromName = (name) => {
    const spices = ['salt', 'pepper', 'garlic', 'onion powder', 'paprika', 'cumin', 'oregano', 'basil', 'thyme', 'cinnamon', 'chili', 'red pepper', 'turmeric', 'ginger', 'bay leaves', 'rosemary', 'sage', 'parsley', 'cilantro', 'dill'];
    const dryGoods = ['pasta', 'rice', 'flour', 'oil', 'vinegar', 'beans', 'lentils', 'quinoa', 'oats', 'sugar', 'honey', 'syrup', 'sauce', 'stock', 'broth', 'canned', 'dried'];
    
    const lowerName = name.toLowerCase();
    
    if (spices.some(spice => lowerName.includes(spice))) return 'spices';
    if (dryGoods.some(dry => lowerName.includes(dry))) return 'dryGoods';
    return 'fresh'; // Default to fresh for everything else
  };

  // Handle selecting a suggestion
  const selectSuggestion = (suggestion, category) => {
    console.log('✅ Selected suggestion:', suggestion.name, 'for category:', category);
    addPantryItem({ 
      name: suggestion.name, 
      category: category || suggestion.category || getCategoryFromName(suggestion.name)
    });
    setSearchTerm('');
    setSearchSuggestions([]);
    setShowSuggestions(false);
  };

  // Toggle section visibility
  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  // Categorize pantry items with memo for performance
  const categorizeItems = useMemo(() => {
    const categorized = {
      spices: [],
      dryGoods: [],
      fresh: []
    };

    console.log('🔄 Categorizing pantry items:', pantryItems);

    pantryItems.forEach(item => {
      const category = item.category === 'spices' || item.category === 'dryGoods' || item.category === 'fresh' 
        ? item.category 
        : getCategoryFromName(item.name);
      
      console.log(`📋 Item "${item.name}" categorized as "${category}"`);
      
      if (categorized[category]) {
        categorized[category].push(item);
      } else {
        console.log(`⚠️ Unknown category "${category}" for item "${item.name}", defaulting to fresh`);
        categorized.fresh.push(item); // Default fallback
      }
    });

    console.log('📊 Final categorization:', categorized);
    return categorized;
  }, [pantryItems]);

  // Search for ingredients with API
  const searchIngredients = async (query) => {
    if (!query || query.length < 2) {
      setSearchSuggestions([]);
      setShowSuggestions(false);
      return;
    }

    try {
      setIsSearching(true);
      const apiUrl = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000';
      const response = await fetch(`${apiUrl}/api/ingredients?query=${encodeURIComponent(query)}`);
      
      console.log('🔍 Search API response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('🔍 Search results:', data.ingredients?.length || 0, 'ingredients');
        console.log('🔍 Raw search response:', data);
        
        // Filter out ingredients already in pantry
        const filteredSuggestions = (data.ingredients || []).filter(ingredient => 
          !pantryItems.find(item => item.name.toLowerCase() === ingredient.name.toLowerCase())
        );
        
        setSearchSuggestions(filteredSuggestions.slice(0, 8)); // Limit to 8 suggestions
        setShowSuggestions(true);
      } else {
        const errorText = await response.text();
        console.log('⚠️ Search failed:', response.status, errorText);
        setSearchSuggestions([]);
        setShowSuggestions(false);
      }
    } catch (err) {
      console.error('❌ Search error:', err);
      setSearchSuggestions([]);
      setShowSuggestions(false);
    } finally {
      setIsSearching(false);
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
          await loadAvailableIngredients();
        }
      } else {
        console.error('Failed to toggle pantry system');
      }
    } catch (err) {
      console.error('Pantry toggle error:', err);
    }
  };

  const addPantryItem = (ingredient) => {
    console.log('➕ Adding ingredient to pantry:', ingredient);
    
    // Ensure proper categorization
    const categoryMapped = {
      ...ingredient,
      category: ingredient.category || getCategoryFromName(ingredient.name)
    };
    
    console.log('🏷️ Category mapped ingredient:', categoryMapped);
    
    addToPantry(categoryMapped);
    setSearchTerm(''); // Clear search after adding
  };

  const updateAmount = (ingredientId, newAmount) => {
    updatePantryAmount(ingredientId, newAmount);
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
          <h2>Pantry Management</h2>
          <button
            onClick={togglePantrySystem}
            className={`pantry-toggle-btn ${pantryEnabled ? 'enabled' : 'disabled'}`}
            title={`${pantryEnabled ? 'Disable' : 'Enable'} Pantry System`}
          >
            {pantryEnabled ? 'ON' : 'OFF'}
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

        {/* Smart 3-Section Pantry Organization */}
        {(() => {
          const categorizedItems = categorizeItems;
          
          return (
            <>
              {/* 1. SPICE RACK - High value, low maintenance */}
              <div className="pantry-section smart-section spice-section">
                <div 
                  className="section-header" 
                  onClick={() => toggleSection('spices')}
                >
                  <div className="header-content">
                    <h3>Spice Rack ({categorizedItems.spices.length})</h3>
                    <span className="value-badge high-value">High Value</span>
                  </div>
                  <span className={`expand-icon ${expandedSections.spices ? 'expanded' : ''}`}>▼</span>
                </div>
                <div className="section-description">
                  Set once, use forever. Greatest cooking impact for least effort.
                </div>
                
                {expandedSections.spices && (
                  <div className="section-content">
                    {/* Current Spice Items */}
                    {categorizedItems.spices.length > 0 ? (
                      <div className="current-items">
                        <h4>Your Spices</h4>
                        {categorizedItems.spices.map(item => (
                          <div key={item.id} className="pantry-item spice-item">
                            <div className="item-info">
                              <span className="item-name">{item.name}</span>
                            </div>
                            <div className="item-controls">
                              <button
                                onClick={() => removePantryItem(item.id)}
                                className="remove-button"
                                title="Remove from spice rack"
                              >
                                ✕
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="empty-section">
                        <p>No spices added yet. Start building your spice collection!</p>
                      </div>
                    )}
                    
                    {/* Add Spices - Smart Autocomplete */}
                    <div className="add-section">
                      <h4>Add Spices</h4>
                      <div className="autocomplete-container">
                        <div className="search-add-container">
                          <input
                            type="text"
                            placeholder="Type spice name (e.g., paprika, cumin)..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="section-search-input spice-search"
                            onKeyPress={(e) => {
                              if (e.key === 'Enter' && searchTerm.trim()) {
                                if (searchSuggestions.length > 0) {
                                  selectSuggestion(searchSuggestions[0], 'spices');
                                } else {
                                  addPantryItem({ name: searchTerm.trim(), category: 'spices' });
                                }
                              }
                            }}
                            onFocus={() => {
                              if (searchSuggestions.length > 0) {
                                setShowSuggestions(true);
                              }
                            }}
                            onBlur={() => {
                              // Delay hiding suggestions to allow click
                              setTimeout(() => setShowSuggestions(false), 200);
                            }}
                          />
                          {isSearching && (
                            <div className="search-loading">🔍</div>
                          )}
                        </div>
                        
                        {/* Smart Suggestions Dropdown */}
                        {showSuggestions && searchSuggestions.length > 0 && (
                          <div className="suggestions-dropdown spice-suggestions">
                            {searchSuggestions.map((suggestion, index) => (
                              <button
                                key={`suggestion-${index}-${suggestion.name}`}
                                onClick={() => selectSuggestion(suggestion, 'spices')}
                                className="suggestion-item"
                              >
                                <span className="suggestion-name">{suggestion.name}</span>
                                <span className="suggestion-category">{suggestion.category}</span>
                              </button>
                            ))}
                          </div>
                        )}
                        
                        {/* Manual Add Button */}
                        {searchTerm.trim() && !isSearching && (
                          <button
                            onClick={() => addPantryItem({ name: searchTerm.trim(), category: 'spices' })}
                            className="add-search-button spice-add"
                          >
                            Add "{searchTerm.trim()}" as spice
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* 2. DRY GOODS - Medium value, medium maintenance */}
              <div className="pantry-section smart-section dry-goods-section">
                <div 
                  className="section-header" 
                  onClick={() => toggleSection('dryGoods')}
                >
                  <div className="header-content">
                    <h3>Pantry Staples ({categorizedItems.dryGoods.length})</h3>
                    <span className="value-badge medium-value">Optional</span>
                  </div>
                  <span className={`expand-icon ${expandedSections.dryGoods ? 'expanded' : ''}`}>▼</span>
                </div>
                <div className="section-description">
                  Long-lasting staples. Update when you shop, ignore the rest.
                </div>
                
                {expandedSections.dryGoods && (
                  <div className="section-content">
                    {/* Current Dry Goods */}
                    {categorizedItems.dryGoods.length > 0 ? (
                      <div className="current-items">
                        <h4>Your Pantry Staples</h4>
                        {categorizedItems.dryGoods.map(item => (
                          <div key={item.id} className="pantry-item dry-goods-item">
                            <div className="item-info">
                              <span className="item-name">{item.name}</span>
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
                                title="Remove from pantry staples"
                              >
                                ✕
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="empty-section">
                        <p>No pantry staples added yet. Add your go-to cooking essentials!</p>
                      </div>
                    )}
                    
                    {/* Add Dry Goods - Smart Autocomplete */}
                    <div className="add-section">
                      <h4>Add Staples</h4>
                      <div className="autocomplete-container">
                        <div className="search-add-container">
                          <input
                            type="text"
                            placeholder="Type staple name (e.g., pasta, rice, olive oil)..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="section-search-input dry-goods-search"
                            onKeyPress={(e) => {
                              if (e.key === 'Enter' && searchTerm.trim()) {
                                if (searchSuggestions.length > 0) {
                                  selectSuggestion(searchSuggestions[0], 'dryGoods');
                                } else {
                                  addPantryItem({ name: searchTerm.trim(), category: 'dryGoods' });
                                }
                              }
                            }}
                            onFocus={() => {
                              if (searchSuggestions.length > 0) {
                                setShowSuggestions(true);
                              }
                            }}
                            onBlur={() => {
                              setTimeout(() => setShowSuggestions(false), 200);
                            }}
                          />
                          {isSearching && (
                            <div className="search-loading">🔍</div>
                          )}
                        </div>
                        
                        {/* Smart Suggestions Dropdown */}
                        {showSuggestions && searchSuggestions.length > 0 && (
                          <div className="suggestions-dropdown dry-goods-suggestions">
                            {searchSuggestions.map((suggestion, index) => (
                              <button
                                key={`suggestion-${index}-${suggestion.name}`}
                                onClick={() => selectSuggestion(suggestion, 'dryGoods')}
                                className="suggestion-item"
                              >
                                <span className="suggestion-name">{suggestion.name}</span>
                                <span className="suggestion-category">{suggestion.category}</span>
                              </button>
                            ))}
                          </div>
                        )}
                        
                        {/* Manual Add Button */}
                        {searchTerm.trim() && !isSearching && (
                          <button
                            onClick={() => addPantryItem({ name: searchTerm.trim(), category: 'dryGoods' })}
                            className="add-search-button dry-goods-add"
                          >
                            Add "{searchTerm.trim()}" as staple
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* 3. FRESH THIS WEEK - Ephemeral, no pressure */}
              <div className="pantry-section smart-section fresh-section">
                <div 
                  className="section-header" 
                  onClick={() => toggleSection('freshWeek')}
                >
                  <div className="header-content">
                    <h3>Fresh This Week ({categorizedItems.fresh.length})</h3>
                    <span className="value-badge low-pressure">No Pressure</span>
                  </div>
                  <span className={`expand-icon ${expandedSections.freshWeek ? 'expanded' : ''}`}>▼</span>
                </div>
                <div className="section-description">
                  What's fresh right now? Perfect for "cook tonight" suggestions.
                </div>
                
                {expandedSections.freshWeek && (
                  <div className="section-content">
                    {/* Current Fresh Items */}
                    {categorizedItems.fresh.length > 0 ? (
                      <div className="current-items">
                        <h4>Fresh This Week</h4>
                        {categorizedItems.fresh.map(item => (
                          <div key={item.id} className="pantry-item fresh-item">
                            <div className="item-info">
                              <span className="item-name">{item.name}</span>
                            </div>
                            <div className="item-controls">
                              <button
                                onClick={() => removePantryItem(item.id)}
                                className="remove-button"
                                title="Remove from fresh items"
                              >
                                ✕
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="empty-section">
                        <p>No fresh items tracked this week. Add what's in your fridge!</p>
                      </div>
                    )}
                    
                    {/* Add Fresh Items - Smart Autocomplete */}
                    <div className="add-section">
                      <h4>Add Fresh Items</h4>
                      <div className="autocomplete-container">
                        <div className="search-add-container">
                          <input
                            type="text"
                            placeholder="Type fresh item (e.g., chicken, spinach, tomato)..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="section-search-input fresh-search"
                            onKeyPress={(e) => {
                              if (e.key === 'Enter' && searchTerm.trim()) {
                                if (searchSuggestions.length > 0) {
                                  selectSuggestion(searchSuggestions[0], 'fresh');
                                } else {
                                  addPantryItem({ name: searchTerm.trim(), category: 'fresh' });
                                }
                              }
                            }}
                            onFocus={() => {
                              if (searchSuggestions.length > 0) {
                                setShowSuggestions(true);
                              }
                            }}
                            onBlur={() => {
                              setTimeout(() => setShowSuggestions(false), 200);
                            }}
                          />
                          {isSearching && (
                            <div className="search-loading">🔍</div>
                          )}
                        </div>
                        
                        {/* Smart Suggestions Dropdown */}
                        {showSuggestions && searchSuggestions.length > 0 && (
                          <div className="suggestions-dropdown fresh-suggestions">
                            {searchSuggestions.map((suggestion, index) => (
                              <button
                                key={`suggestion-${index}-${suggestion.name}`}
                                onClick={() => selectSuggestion(suggestion, 'fresh')}
                                className="suggestion-item"
                              >
                                <span className="suggestion-name">{suggestion.name}</span>
                                <span className="suggestion-category">{suggestion.category}</span>
                              </button>
                            ))}
                          </div>
                        )}
                        
                        {/* Manual Add Button */}
                        {searchTerm.trim() && !isSearching && (
                          <button
                            onClick={() => addPantryItem({ name: searchTerm.trim(), category: 'fresh' })}
                            className="add-search-button fresh-add"
                          >
                            Add "{searchTerm.trim()}" as fresh
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </>
          );
        })()}

      </div>

      <div className="pantry-footer">
        <div className="pantry-stats smart-stats">
          <div className="stat">
            <span className="stat-number">{categorizeItems.spices.length}</span>
            <span className="stat-label">Spices</span>
          </div>
          <div className="stat">
            <span className="stat-number">{categorizeItems.dryGoods.length}</span>
            <span className="stat-label">Staples</span>
          </div>
          <div className="stat">
            <span className="stat-number">{categorizeItems.fresh.length}</span>
            <span className="stat-label">Fresh</span>
          </div>
          <div className="stat">
            <span className="stat-number">{pantryItems.filter(item => item.amount === 'low').length}</span>
            <span className="stat-label">Running Low</span>
          </div>
        </div>

        <div className="feature-note smart-note">
          <p><strong>Smart Strategy:</strong> Start with spices (high value, low effort), add staples when you shop, track fresh when convenient!</p>
        </div>
      </div>
    </div>
  );
};

export default PantryManager;
