import { useState, useEffect } from 'react';

/**
 * Custom hook for managing pantry data across components
 * Provides pantry items and synchronization with backend
 */
export const usePantry = () => {
  const [pantryItems, setPantryItems] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load pantry from localStorage on component mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem('pantryItems');
      if (stored) {
        const parsed = JSON.parse(stored);
        setPantryItems(parsed);
        console.log('🥫 Pantry loaded from localStorage:', parsed.map(item => item.name));
      }
    } catch (err) {
      console.error('❌ Error loading pantry from localStorage:', err);
    }
  }, []);

  // Save pantry to localStorage whenever it changes
  useEffect(() => {
    try {
      localStorage.setItem('pantryItems', JSON.stringify(pantryItems));
      console.log('💾 Pantry saved to localStorage:', pantryItems.map(item => item.name));
    } catch (err) {
      console.error('❌ Error saving pantry to localStorage:', err);
    }
  }, [pantryItems]);

  // Add item to pantry
  const addPantryItem = (ingredient) => {
    console.log('➕ Adding to pantry via hook:', ingredient);
    const newItem = {
      id: Date.now(),
      name: ingredient.name,
      category: ingredient.category || 'other',
      amount: 'some',
      addedAt: new Date().toISOString()
    };

    setPantryItems(prev => {
      const exists = prev.find(item => item.name.toLowerCase() === ingredient.name.toLowerCase());
      if (exists) {
        console.log('⚠️ Item already in pantry:', ingredient.name);
        return prev;
      }
      const updated = [...prev, newItem];
      console.log('✅ Pantry updated via hook:', updated.map(item => item.name));
      return updated;
    });
  };

  // Remove item from pantry
  const removePantryItem = (itemId) => {
    setPantryItems(prev => {
      const updated = prev.filter(item => item.id !== itemId);
      console.log('🗑️ Item removed from pantry:', updated.map(item => item.name));
      return updated;
    });
  };

  // Update item amount
  const updatePantryAmount = (itemId, newAmount) => {
    setPantryItems(prev =>
      prev.map(item =>
        item.id === itemId ? { ...item, amount: newAmount } : item
      )
    );
  };

  // Get pantry items formatted for API
  const getPantryForAPI = () => {
    return pantryItems.map(item => ({
      name: item.name,
      category: item.category,
      amount: item.amount
    }));
  };

  // Clear all pantry items
  const clearPantry = () => {
    setPantryItems([]);
    console.log('🧹 Pantry cleared');
  };

  return {
    pantryItems,
    isLoading,
    error,
    addPantryItem,
    removePantryItem,
    updatePantryAmount,
    getPantryForAPI,
    clearPantry,
    pantryCount: pantryItems.length,
    hasItems: pantryItems.length > 0
  };
};
