import React, { useState, useEffect } from 'react';
import FriendsAPI from '../services/FriendsAPI';
import './SharedGroceryList.css';

const SharedGroceryList = ({ household }) => {
  const [groceryList, setGroceryList] = useState([]);
  const [newItem, setNewItem] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (household) {
      loadSharedGroceryList();
    }
  }, [household]);

  const loadSharedGroceryList = async () => {
    setLoading(true);
    setError('');
    
    try {
      // For now, we'll use localStorage to simulate shared grocery lists
      // In a real implementation, this would be an API call to FriendsAPI
      const listKey = `household_grocery_${household.id}`;
      const savedList = localStorage.getItem(listKey);
      
      if (savedList) {
        setGroceryList(JSON.parse(savedList));
      } else {
        setGroceryList([]);
      }
    } catch (error) {
      setError('Failed to load shared grocery list');
      console.error('Error loading shared grocery list:', error);
    } finally {
      setLoading(false);
    }
  };

  const saveGroceryList = (updatedList) => {
    try {
      const listKey = `household_grocery_${household.id}`;
      localStorage.setItem(listKey, JSON.stringify(updatedList));
      setGroceryList(updatedList);
    } catch (error) {
      setError('Failed to save grocery list');
      console.error('Error saving grocery list:', error);
    }
  };

  const handleAddItem = (e) => {
    e.preventDefault();
    
    if (!newItem.trim()) {
      setError('Please enter an item');
      return;
    }
    
    const newGroceryItem = {
      id: Date.now(),
      name: newItem.trim(),
      completed: false,
      addedBy: 'Current User', // In real implementation, get from auth context
      addedAt: new Date().toLocaleDateString(),
      category: categorizeItem(newItem.trim())
    };
    
    const updatedList = [...groceryList, newGroceryItem];
    saveGroceryList(updatedList);
    setNewItem('');
    setSuccess('Item added to shared list!');
    
    // Clear success message after 3 seconds
    setTimeout(() => setSuccess(''), 3000);
  };

  const handleToggleItem = (itemId) => {
    const updatedList = groceryList.map(item =>
      item.id === itemId
        ? { ...item, completed: !item.completed, completedBy: item.completed ? null : 'Current User' }
        : item
    );
    saveGroceryList(updatedList);
  };

  const handleRemoveItem = (itemId) => {
    const updatedList = groceryList.filter(item => item.id !== itemId);
    saveGroceryList(updatedList);
  };

  const categorizeItem = (itemName) => {
    const categories = {
      'Produce': ['apple', 'banana', 'orange', 'lettuce', 'tomato', 'onion', 'carrot', 'potato', 'broccoli', 'spinach'],
      'Dairy': ['milk', 'cheese', 'yogurt', 'butter', 'cream', 'eggs'],
      'Meat': ['chicken', 'beef', 'pork', 'fish', 'turkey', 'salmon', 'shrimp'],
      'Pantry': ['rice', 'pasta', 'bread', 'flour', 'sugar', 'salt', 'pepper', 'oil', 'vinegar'],
      'Frozen': ['frozen', 'ice cream', 'frozen vegetables'],
      'Beverages': ['coffee', 'tea', 'juice', 'soda', 'water', 'wine', 'beer']
    };
    
    const lowerName = itemName.toLowerCase();
    for (const [category, items] of Object.entries(categories)) {
      if (items.some(item => lowerName.includes(item))) {
        return category;
      }
    }
    return 'Other';
  };

  const getCategoryIcon = (category) => {
    const icons = {
      'Produce': '🥬',
      'Dairy': '🥛',
      'Meat': '🥩',
      'Pantry': '🥫',
      'Frozen': '🧊',
      'Beverages': '🥤',
      'Other': '🛒'
    };
    return icons[category] || '🛒';
  };

  const groupedItems = groceryList.reduce((groups, item) => {
    const category = item.category || 'Other';
    if (!groups[category]) {
      groups[category] = [];
    }
    groups[category].push(item);
    return groups;
  }, {});

  const completedCount = groceryList.filter(item => item.completed).length;
  const totalCount = groceryList.length;

  if (loading) {
    return (
      <div className="shared-grocery-loading">
        <div className="loading-spinner"></div>
        <p>Loading shared grocery list...</p>
      </div>
    );
  }

  return (
    <div className="shared-grocery-list">
      <div className="grocery-header">
        <h3>🛒 Shared Grocery List</h3>
        <p className="grocery-subtitle">
          Shopping for <strong>{household.name}</strong>
        </p>
        <div className="grocery-progress">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: totalCount > 0 ? `${(completedCount / totalCount) * 100}%` : '0%' }}
            ></div>
          </div>
          <span className="progress-text">
            {completedCount} of {totalCount} items completed
          </span>
        </div>
      </div>

      {/* Messages */}
      {error && (
        <div className="message error-message">
          ❌ {error}
          <button onClick={() => setError('')} className="close-message">×</button>
        </div>
      )}
      {success && (
        <div className="message success-message">
          ✅ {success}
          <button onClick={() => setSuccess('')} className="close-message">×</button>
        </div>
      )}

      {/* Add Item Form */}
      <form onSubmit={handleAddItem} className="add-item-form">
        <input
          type="text"
          value={newItem}
          onChange={(e) => setNewItem(e.target.value)}
          placeholder="Add item to shared list..."
          className="add-item-input"
        />
        <button type="submit" className="add-item-button">
          ➕ Add Item
        </button>
      </form>

      {/* Grocery List */}
      <div className="grocery-list-content">
        {totalCount === 0 ? (
          <div className="empty-grocery-list">
            <span className="empty-icon">🛒</span>
            <h4>Empty Shopping List</h4>
            <p>Start adding items to your shared grocery list!</p>
          </div>
        ) : (
          Object.entries(groupedItems).map(([category, items]) => (
            <div key={category} className="grocery-category">
              <h4 className="category-header">
                {getCategoryIcon(category)} {category} ({items.length})
              </h4>
              <div className="category-items">
                {items.map(item => (
                  <div 
                    key={item.id} 
                    className={`grocery-item ${item.completed ? 'completed' : ''}`}
                  >
                    <button
                      className="item-checkbox"
                      onClick={() => handleToggleItem(item.id)}
                    >
                      {item.completed ? '✅' : '⬜'}
                    </button>
                    <div className="item-info">
                      <span className="item-name">{item.name}</span>
                      <span className="item-meta">
                        Added by {item.addedBy} on {item.addedAt}
                        {item.completed && item.completedBy && (
                          <> • Completed by {item.completedBy}</>
                        )}
                      </span>
                    </div>
                    <button
                      className="remove-item-button"
                      onClick={() => handleRemoveItem(item.id)}
                      title="Remove item"
                    >
                      🗑️
                    </button>
                  </div>
                ))}
              </div>
            </div>
          ))
        )}
      </div>

      <div className="grocery-footer">
        <p className="collaboration-note">
          💡 <strong>Collaboration:</strong> All household members can add, check off, and remove items from this shared list.
        </p>
      </div>
    </div>
  );
};

export default SharedGroceryList;